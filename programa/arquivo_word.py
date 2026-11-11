"""Abre o documento do Word (`.docx`) que a pessoa escolheu no Anonimizar.

Por dentro, o `.docx` é um pacote compactado (um `.zip` com outro nome) de
arquivos de texto com marcações - o XML. O corpo do documento mora no
`word/document.xml`; o cabeçalho, o rodapé e as notas, em peças ao lado dele.
O programa abre esse pacote com o que já vem no próprio Python, sem biblioteca
nova (décima emenda da spec 003, decisão de 23/10/2026): a de PDF que o
programa usa só abre Word na versão paga, e a python-docx não lê caixa de
texto, nota nem alteração controlada.

O que sai daqui é o texto do documento impresso já no formato do `.md` - títulos
com `#`, listas com `-`, tabelas com barras, notas com `[^1]` -, pronto para a
revisão. Nenhuma macro é executada e nada sai da máquina: o programa só lê
texto (RN-20 e RN-23).
"""
import re
import zipfile
import zlib
from pathlib import Path
from typing import NamedTuple
from xml.etree import ElementTree

from arquivo_texto import ArquivoNaoServe

# O endereço que o Word põe na frente de cada marcação do documento. O
# ElementTree escreve as marcações com ele por extenso, entre chaves.
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
LIGACAO = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"

# Nomes que o Word grava em inglês mesmo no Word em português: "heading 1" é o
# "Título 1" da tela, e "title" é o "Título" (RN-28).
TITULO = "title"
PREFIXO_DE_TITULO = "heading "

# Até que nível de título o `.md` tem marcação: de `#` a `######`.
NIVEL_MAXIMO = 6

# A ordem em que os cabeçalhos (e os rodapés) de uma mesma parte do documento
# aparecem: o da primeira página vem antes do das outras.
TIPOS_DE_CABECALHO = ("first", "default", "even")

# As peças do pacote que o documento impresso usa. É nelas que uma alteração
# controlada muda o texto; nos estilos e nos ajustes, ela não muda nada que se
# leia.
PECAS_DE_TEXTO = ("word/document", "word/header", "word/footer",
                  "word/footnotes", "word/endnotes")

# As marcas da alteração controlada no texto: o trecho inserido, o apagado, e
# o que foi movido de um lugar (de onde sai) para outro (aonde chega).
ALTERACOES = ("ins", "del", "moveFrom", "moveTo")

# As frases de cada Word que não abre (RN-30), com o texto aprovado no
# rascunho 10. Todas voltam à escolha do arquivo, sem travar.
ESTRAGADO = (
    "O {nome} não pôde ser lido como documento do Word: ele pode estar "
    "estragado ou ser outro tipo de arquivo com o nome trocado."
)
PROTEGIDO = (
    "O {nome} está protegido por senha. Abra no Word, tire a senha e salve de "
    "novo, e escolha o arquivo outra vez."
)
DOC_ANTIGO = (
    "O {nome} é um documento do Word antigo (.doc) com o nome de .docx. Abra no "
    "Word e salve como .docx."
)
VAZIO = "O {nome} está vazio: não há texto nele."
SO_IMAGENS = (
    "O {nome} não tem texto, só imagens. Salve-o como PDF pelo Word e escolha o "
    "PDF: o programa lê as imagens e você confere."
)
GRANDE_DEMAIS = "O {nome} é grande demais para o programa abrir com segurança."

# O limite do texto do pacote, descompactado (RN-30). O texto de um documento
# comum, mesmo de centenas de páginas, fica muito abaixo disso. É conferido
# antes de descompactar: um pacote pequeno pode esconder um conteúdo enorme,
# feito para travar quem o abre. As imagens não contam, porque não são
# descompactadas.
LIMITE_DO_TEXTO = 50 * 1024 * 1024

# Os primeiros bytes de um arquivo do Office antigo, o mesmo formato por fora
# do .doc e do .docx protegido por senha: o Word cifra o .docx guardando-o
# dentro de um pacote desse tipo, com uma parte chamada "EncryptionInfo".
CABECALHO_DO_OFFICE_ANTIGO = bytes.fromhex("D0CF11E0A1B11AE1")
MARCA_DE_CIFRADO = "EncryptionInfo".encode("utf-16-le")

# O que dentro de um desenho é imagem para a faixa: a foto colada, a imagem do
# jeito antigo, o gráfico e o diagrama (RN-26).
MARCAS_DE_IMAGEM = ("blip", "imagedata", "chart", "relIds")


class DocumentoDoWord(NamedTuple):
    """O texto que vai para a revisão, e o que ficou de fora dele (RN-29).

    O que ficou de fora só vira a faixa da revisão: nunca vai para o arquivo.
    """
    texto: str
    comentarios: int = 0
    imagens: int = 0
    texto_oculto: bool = False
    alteracoes: bool = False


def ler(caminho):
    """O documento do Word: o texto no formato do `.md`, e o que ficou de fora.

    A ordem é a do documento impresso (RN-24): o cabeçalho, o corpo, o rodapé
    e, no fim, as notas. Arquivo que não é um pacote do Word, ou que não tem a
    parte do corpo, dá a frase de "estragado" (RN-30) e não chega à revisão.
    """
    caminho = Path(caminho)
    _recusar_o_que_nao_e_pacote(caminho)
    try:
        with zipfile.ZipFile(caminho) as pacote:
            _recusar_o_grande_demais(pacote, caminho.name)
            leitura = _Leitura(pacote, caminho.name)
            documento = leitura.documento()
    # O pacote pode abrir e o conteúdo de dentro estar estragado: um byte
    # trocado no meio dá erro de descompactação (zlib.error), e um Word
    # compactado num formato que o Python não lê dá NotImplementedError. Os dois
    # escapavam e deixavam a tela parada, sem frase nenhuma (lente crítica da
    # etapa 1).
    except (zipfile.BadZipFile, KeyError, ElementTree.ParseError, zlib.error,
            EOFError, NotImplementedError, _SemCorpo):
        raise ArquivoNaoServe(ESTRAGADO.format(nome=caminho.name))
    # Sem texto, a revisão não abre: ela diria "nenhum CPF encontrado", e isso
    # se leria como "este documento não tem CPF" (RN-30). O "só imagens" olha o
    # corpo: páginas escaneadas coladas num Word com timbre no cabeçalho e
    # número de página no rodapé têm texto só nas bordas, e abriam uma revisão
    # quase vazia (lente crítica da etapa 5).
    if not leitura.texto_do_corpo.strip() and leitura.imagens_no_corpo:
        raise ArquivoNaoServe(SO_IMAGENS.format(nome=caminho.name))
    if not documento.texto.strip():
        raise ArquivoNaoServe(VAZIO.format(nome=caminho.name))
    return documento


def _recusar_o_que_nao_e_pacote(caminho):
    """O .docx protegido por senha e o .doc antigo com o nome trocado.

    Nenhum dos dois é um pacote do Word: os dois são o formato antigo do
    Office por fora, e cada um tem a frase dele, com o que fazer (RN-30). O
    que não é nem um nem outro segue, e cai na frase de "estragado" se não for
    pacote.
    """
    with open(caminho, "rb") as arquivo:
        if arquivo.read(len(CABECALHO_DO_OFFICE_ANTIGO)) != CABECALHO_DO_OFFICE_ANTIGO:
            return
        dados = arquivo.read()
    frase = PROTEGIDO if MARCA_DE_CIFRADO in dados else DOC_ANTIGO
    raise ArquivoNaoServe(frase.format(nome=caminho.name))


def _recusar_o_grande_demais(pacote, nome):
    """Recusa o pacote cujo texto, descompactado, passaria do limite (RN-30).

    A conta usa o tamanho que cada peça declara, sem descompactar nada.
    """
    texto = sum(peca.file_size for peca in pacote.infolist()
                if peca.filename.endswith((".xml", ".rels")))
    if texto > LIMITE_DO_TEXTO:
        raise ArquivoNaoServe(GRANDE_DEMAIS.format(nome=nome))


class _SemCorpo(Exception):
    """O pacote abriu, mas o documento não tem a parte do corpo."""


class _Leitura:
    """Uma passada pelo documento, guardando o que precisa ser lembrado.

    As notas ganham número na ordem em que são chamadas no texto, e a caixa de
    texto sai depois do parágrafo em que está presa: as duas coisas só se sabem
    andando pelo documento na ordem, e é isto que esta leitura guarda.
    """

    def __init__(self, pacote, nome):
        self.pacote = pacote
        self.nome = nome
        # Quanto já foi descompactado, para o limite da RN-30 (veja `_peca`).
        self.descompactado = 0
        self.estilos = _estilos(self._peca("word/styles.xml"))
        self.ligacoes = self._ligacoes()
        self.numeracao = _Numeracao(self._peca("word/numbering.xml"))
        ajustes = self._peca("word/settings.xml")
        # "Páginas pares e ímpares diferentes" é uma opção do documento
        # inteiro; sem ela, o cabeçalho das páginas pares nunca é impresso.
        self.pares_diferentes = _ligado(
            ajustes.find(f"{W}evenAndOddHeaders") if ajustes is not None else None)
        # As notas chamadas no texto, na ordem: (tipo, código da nota no Word).
        self.notas_chamadas = []
        # O número de cada nota, depois que a ordem delas é conhecida.
        self.numeros = None
        # O que fica de fora do arquivo e a faixa da revisão conta (RN-29).
        self.texto_oculto = False
        self.imagens = 0
        self.pecas_lidas = []
        # Se o estilo do parágrafo que está sendo lido esconde o texto.
        self._paragrafo_oculto = None

    def documento(self):
        texto = self.texto()
        comentarios = self._peca("word/comments.xml")
        return DocumentoDoWord(
            texto=texto,
            comentarios=(len(comentarios.findall(f"{W}comment"))
                         if comentarios is not None else 0),
            imagens=self.imagens,
            texto_oculto=self.texto_oculto,
            alteracoes=any(next(raiz.iter(f"{W}{marca}"), None) is not None
                           for raiz in self.pecas_lidas for marca in ALTERACOES),
        )

    def texto(self):
        raiz = self._peca("word/document.xml")
        corpo = raiz.find(f"{W}body") if raiz is not None else None
        if corpo is None:
            raise _SemCorpo()
        # Duas passadas pelo corpo. A primeira só descobre a ordem em que as
        # notas são chamadas: as de fim continuam a numeração das de rodapé, e
        # o número de uma nota de fim só se sabe depois de contar todas as de
        # rodapé. A segunda escreve o texto já com os números certos - um
        # número posto depois entortaria a coluna da tabela em que a nota é
        # chamada.
        list(self._blocos(corpo))
        ordem = ([n for n in self.notas_chamadas if n[0] == "footnote"]
                 + [n for n in self.notas_chamadas if n[0] == "endnote"])
        self.numeros = {nota: numero for numero, nota in enumerate(ordem, start=1)}
        # A primeira passada também contou os itens das listas: a contagem
        # recomeça, senão a segunda passada continuaria do número em que a
        # primeira parou.
        self.numeracao.recomecar()
        blocos_do_corpo = list(self._blocos(corpo))
        # O corpo sozinho decide o "só imagens" (veja `ler`). As imagens dele
        # são as contadas até aqui: as do cabeçalho e as das notas vêm depois.
        self.texto_do_corpo = _juntar_blocos(blocos_do_corpo)
        self.imagens_no_corpo = self.imagens
        blocos = (self._partes_de_borda(corpo, "headerReference")
                  + blocos_do_corpo
                  + self._partes_de_borda(corpo, "footerReference"))
        texto = _juntar_blocos(blocos)
        notas = self._notas()
        return texto + "\n\n" + notas if notas and texto else texto or notas

    # -------------------------------------------------------- peças do pacote

    def _peca(self, nome):
        """Uma peça do pacote já lida, ou None quando o documento não a tem.

        Cada peça soma no limite da RN-30 antes de ser descompactada, tenha o
        nome que tiver: a ligação do cabeçalho pode levar a uma peça que não
        termina em .xml, e a conta de antes da leitura não a via (lente crítica
        da etapa 5).
        """
        try:
            self.descompactado += self.pacote.getinfo(nome).file_size
        except KeyError:
            return None
        if self.descompactado > LIMITE_DO_TEXTO:
            raise ArquivoNaoServe(GRANDE_DEMAIS.format(nome=self.nome))
        raiz = ElementTree.fromstring(self.pacote.read(nome))
        if nome.startswith(PECAS_DE_TEXTO):
            self.pecas_lidas.append(raiz)
        return raiz

    def _ligacoes(self):
        """De cada código de ligação do corpo, a peça do pacote a que ele leva.

        O corpo não diz "header1.xml": ele diz "rId7", e a lista do que cada
        código quer dizer mora numa peça à parte.
        """
        raiz = self._peca("word/_rels/document.xml.rels")
        ligacoes = {}
        for ligacao in (raiz.iter(LIGACAO) if raiz is not None else ()):
            alvo = ligacao.get("Target") or ""
            if ligacao.get("TargetMode") == "External":
                continue  # endereço de internet de um link: nunca é aberto
            ligacoes[ligacao.get("Id")] = (alvo.lstrip("/") if alvo.startswith("/")
                                           else "word/" + alvo)
        return ligacoes

    # ------------------------------------------------ cabeçalho e rodapé

    def _partes_de_borda(self, corpo, marcacao):
        """Os cabeçalhos (ou os rodapés) do documento, cada diferente uma vez.

        Cada parte do documento (cada "seção" do Word) diz qual cabeçalho usa.
        Quase sempre é o mesmo em todas, e ele aparece uma vez só; havendo um
        diferente, ele aparece também, na ordem em que surge (RN-24).
        """
        # A marca de seção guardada dentro de uma alteração controlada é a de
        # antes da alteração: o cabeçalho que ela cita foi trocado, e o
        # documento com tudo aceito não o tem mais (RN-25, lente crítica da
        # etapa 3).
        antigas = {id(secao) for mudanca in corpo.iter(f"{W}sectPrChange")
                   for secao in mudanca.iter(f"{W}sectPr")}
        vistos, assinaturas, pecas_vistas, blocos = set(), set(), set(), []
        for secao in corpo.iter(f"{W}sectPr"):
            if id(secao) in antigas:
                continue
            referencias = {ref.get(f"{W}type", "default"): ref.get(f"{R}id")
                           for ref in secao.findall(f"{W}{marcacao}")}
            # O Word guarda o cabeçalho da primeira página (e o das pares)
            # mesmo depois de a opção ser desligada. Só entra o que é impresso:
            # o da primeira página com "Primeira página diferente" ligada, e o
            # das pares com "Pares e ímpares diferentes" (lente crítica da
            # etapa 3).
            if not _ligado(secao.find(f"{W}titlePg")):
                referencias.pop("first", None)
            if not self.pares_diferentes:
                referencias.pop("even", None)
            for tipo in TIPOS_DE_CABECALHO:
                peca = self.ligacoes.get(referencias.get(tipo))
                # Cada peça é lida uma vez só, mesmo citada por várias partes
                # do documento: lida de novo, a imagem dela (um logotipo) seria
                # contada de novo na faixa.
                if not peca or peca in pecas_vistas:
                    continue
                pecas_vistas.add(peca)
                raiz = self._peca(peca)
                if raiz is None:
                    continue
                antes = self.imagens
                dela = list(self._blocos(raiz))
                chave = _juntar_blocos(dela)
                # Ao desligar "Vincular ao anterior", o Word copia o cabeçalho
                # para uma peça nova, igual: o mesmo texto e o mesmo logotipo
                # não contam de novo (lente crítica da etapa 5).
                assinatura = (chave, self.imagens - antes)
                if assinatura in assinaturas:
                    self.imagens = antes
                    continue
                assinaturas.add(assinatura)
                if chave and chave not in vistos:
                    vistos.add(chave)
                    blocos += dela
        return blocos

    # -------------------------------------------------------------- notas

    def _notas(self):
        """As notas, numeradas na ordem em que foram chamadas no texto.

        As de rodapé vêm primeiro, de 1 em diante, e as de fim continuam a
        numeração (premissa da décima emenda). Cada uma sai no formato de nota
        do `.md`, `[^1]: texto`, que o assistente de IA reconhece.
        """
        pecas = {"footnote": self._peca("word/footnotes.xml"),
                 "endnote": self._peca("word/endnotes.xml")}
        linhas = []
        for (tipo, codigo), numero in self.numeros.items():
            texto = ""
            raiz = pecas[tipo]
            for nota in (raiz.findall(f"{W}{tipo}") if raiz is not None else ()):
                if nota.get(f"{W}id") == codigo:
                    partes = []
                    self._partes_da_celula(nota, partes, na_tabela=False)
                    texto = SEPARADOR_NA_CELULA.join(partes)
            linhas.append(f"[^{numero}]: {texto}".rstrip())
        return "\n".join(linhas)

    def _marca_da_nota(self, tipo, codigo):
        """A marca `[^n]` no ponto do texto em que a nota é chamada.

        Na primeira passada pelo corpo a nota só é anotada, e a marca fica
        vazia; na segunda, ela já tem número (veja `texto`).
        """
        if self.numeros is None:
            if (tipo, codigo) not in self.notas_chamadas:
                self.notas_chamadas.append((tipo, codigo))
            return ""
        numero = self.numeros.get((tipo, codigo))
        # Uma nota chamada fora do corpo (de dentro de um cabeçalho, que o Word
        # não grava, mas outro programa pode) fica sem número e sem marca, e o
        # resto do documento abre. Antes, ela fazia o documento inteiro ser
        # recusado como "estragado" (lente crítica da etapa 3).
        return f"[^{numero}]" if numero else ""

    # ------------------------------------------------------------- blocos

    def _blocos(self, no):
        """Os parágrafos e tabelas, na ordem, cada um com o seu jeito de sair.

        Cada bloco é (texto, é item de lista).
        """
        for filho in no:
            nome = _nome(filho)
            if nome == "p":
                caixas = []
                bloco = self._paragrafo(filho, caixas)
                if bloco:
                    yield bloco
                # A caixa de texto sai logo depois do parágrafo em que está
                # presa, uma vez só (RN-24).
                for conteudo in caixas:
                    yield from self._blocos(conteudo)
            elif nome == "tbl":
                tabela = self._tabela(filho)
                if tabela:
                    yield tabela, False
            elif nome in EMBRULHOS_DE_BLOCO:
                yield from self._blocos(filho)

    def _paragrafo(self, paragrafo, caixas):
        texto = self._texto_do_paragrafo(paragrafo, caixas).strip()
        # O item numerado é contado antes de ver se tem texto: o Word mostra e
        # conta o número do item vazio (ou só com uma imagem), e sem contá-lo
        # todo número dali em diante sairia um a menos (lente crítica da
        # etapa 6).
        item = _item_de_lista(paragrafo, self.estilos)
        formato, rotulo = (self.numeracao.rotulo(*item) if item
                           else ("marcador", ""))
        if not texto:
            return None
        # No título e no item de lista, a quebra de linha (Shift+Enter no
        # Word) vira espaço: no .md, a linha de baixo deixaria de ser parte do
        # título, ou do item (anotado na revisão 37).
        nivel = _nivel_do_titulo(paragrafo, self.estilos)
        if nivel:
            # O título numerado ("1 OBJETO") leva o número, e entra na conta:
            # as cláusulas "1.1", "2.1" de baixo dependem dele (lente crítica
            # da etapa 6).
            if item and formato == "numero" and rotulo:
                texto = rotulo + " " + texto
            return "#" * nivel + " " + texto.replace("\n", " "), False
        if item is None:
            return texto, False
        profundidade = item[1]
        if formato == "nenhum":
            # A lista sem marca nenhuma (formato "nenhum" no Word): o texto
            # sai como parágrafo comum, porque não há o que mostrar na frente.
            return texto.replace("\n", " "), False
        # Quatro espaços por nível: o subitem de um item numerado ("1. ", e até
        # "10. ") só é visto pelo .md como subitem com o recuo da largura do
        # número de cima; com dois, ele virava uma lista solta (lente crítica
        # da etapa 6).
        recuo = "    " * profundidade
        texto = texto.replace("\n", " ")
        if formato == "marcador" or not rotulo:
            return recuo + "- " + texto, True
        # "1." e "1)" são lista numerada do próprio .md; "a)", "I." e "1.1"
        # não são, e vão depois de um marcador - assim o .md continua vendo
        # uma lista, e o número que o Word mostra aparece como está (RN-28).
        if ROTULO_DO_MD.fullmatch(rotulo):
            return recuo + rotulo + " " + texto, True
        return recuo + "- " + rotulo + " " + texto, True

    # ------------------------------------------------------------- tabelas

    def _tabela(self, tabela):
        """A tabela do Word como tabela do `.md`, com barras e colunas alinhadas.

        A primeira linha vira o cabeçalho, que é como o `.md` monta toda tabela.
        Tabela sem nenhum texto não sai: seria só um desenho de barras vazio.
        """
        # A linha apagada com o controle de alterações ligado não sai: o Word a
        # mostra riscada, e o documento com tudo aceito não a tem (RN-25).
        linhas = [self._celulas_da_linha(linha) for linha in _filhos(tabela, "tr")
                  if not _tem(linha.find(f"{W}trPr"), "del")]
        if not any(any(celula for celula in linha) for linha in linhas):
            return None
        colunas = max(len(linha) for linha in linhas)
        linhas = [linha + [""] * (colunas - len(linha)) for linha in linhas]
        larguras = [max(LARGURA_MINIMA, *(len(linha[i]) for linha in linhas))
                    for i in range(colunas)]

        def montar(celulas):
            return "| " + " | ".join(
                texto.ljust(largura) for texto, largura in zip(celulas, larguras)) + " |"

        saida = [montar(linhas[0]), montar(["-" * largura for largura in larguras])]
        saida += [montar(linha) for linha in linhas[1:]]
        return "\n".join(saida)

    def _celulas_da_linha(self, linha):
        """O texto de cada posição da linha, com as posições vazias no lugar.

        A célula mesclada na horizontal ocupa várias posições: o texto fica na
        primeira, e as outras ficam vazias (RN-27). A mesclada na vertical o
        Word já grava vazia nas linhas de baixo. Cada texto aparece uma vez só,
        como no Word - repetido, um CPF seria contado e liberado mais de uma
        vez na revisão.
        """
        celulas = []
        propriedades = linha.find(f"{W}trPr")
        # As posições que a linha pula no começo, quando ela começa mais para
        # a direita que as outras.
        celulas += [""] * _numero(_valor(propriedades, "gridBefore"))
        for celula in _filhos(linha, "tc"):
            partes = []
            self._partes_da_celula(celula, partes)
            celulas.append(SEPARADOR_NA_CELULA.join(partes))
            ocupa = _numero(_valor(celula.find(f"{W}tcPr"), "gridSpan"), 1)
            celulas += [""] * (ocupa - 1)
        return celulas

    def _partes_da_celula(self, no, partes, na_tabela=True):
        """Os parágrafos da célula, um por parte, para irem numa linha só.

        Na célula, os parágrafos ficam separados por ` / ` (RN-27); a tabela
        dentro de outra entra do mesmo jeito, como texto corrido; e a caixa de
        texto presa num parágrafo da célula entra logo depois dele. A nota de
        rodapé usa o mesmo arranjo, por isso `na_tabela` diz se a barra
        vertical do texto precisa ser protegida.
        """
        for filho in no:
            nome = _nome(filho)
            if nome == "p":
                caixas = []
                texto = self._texto_do_paragrafo(filho, caixas)
                # O item numerado na célula leva o número na frente e entra na
                # conta: a lista continua depois da tabela com o número certo
                # (lente crítica da etapa 6).
                item = _item_de_lista(filho, self.estilos)
                if item:
                    formato, rotulo = self.numeracao.rotulo(*item)
                    if formato == "numero" and rotulo and texto.strip():
                        texto = rotulo + " " + texto.strip()
                # Uma quebra de linha dentro do parágrafo é outra linha da
                # célula; a tabulação vira espaço. Na tabela, a barra vertical
                # do texto sai como `\|`, senão ela partiria a coluna em duas.
                texto = texto.replace("\n", SEPARADOR_NA_CELULA).replace("\t", " ")
                if na_tabela:
                    texto = texto.replace("|", "\\|")
                if texto.strip():
                    partes.append(texto.strip())
                # A caixa de texto presa na célula é lida como o resto da
                # célula: a barra protegida e a tabela de dentro dela como
                # texto corrido. Lida como bloco solto, ela partia a tabela de
                # fora em colunas a mais (lente crítica da etapa 3).
                for conteudo in caixas:
                    self._partes_da_celula(conteudo, partes, na_tabela)
            elif nome == "tbl":
                for linha in _filhos(filho, "tr"):
                    for celula in _filhos(linha, "tc"):
                        self._partes_da_celula(celula, partes, na_tabela)
            elif nome in EMBRULHOS_DE_BLOCO:
                self._partes_da_celula(filho, partes, na_tabela)

    # ------------------------------------------------- o texto do parágrafo

    def _texto_do_paragrafo(self, paragrafo, caixas):
        partes = []
        # O estilo do parágrafo também pode esconder o texto dele. Guardado
        # aqui porque é de cada trecho que se decide o que é oculto.
        anterior = self._paragrafo_oculto
        self._paragrafo_oculto = _estilo_oculto(
            _valor(paragrafo.find(f"{W}pPr"), "pStyle"), self.estilos)
        self._ler_pedacos(paragrafo, partes, caixas)
        self._paragrafo_oculto = anterior
        return "".join(partes)

    def _ler_pedacos(self, no, partes, caixas):
        """Junta o texto do parágrafo, pedaço por pedaço, na ordem.

        O Word corta o texto em pedaços onde quiser - uma mudança de fonte, a
        correção ortográfica - e um número pode vir partido entre dois. Juntar
        na ordem devolve o número inteiro, e é ele que a busca do CPF vai ver.

        O trecho apagado com o controle de alterações (`del`) não entra: o
        documento sai como ficaria com tudo aceito (RN-25).
        """
        for filho in no:
            nome = _nome(filho)
            if nome == "r":
                self._ler_trecho(filho, partes, caixas)
            elif nome in EMBRULHOS:
                self._ler_pedacos(filho, partes, caixas)

    def _ler_trecho(self, trecho, partes, caixas):
        # O texto oculto não é impresso nem aparece na tela do Word: fica de
        # fora, e a faixa da revisão avisa que ele existia (RN-25 e RN-29). O
        # oculto pode estar marcado no trecho, no estilo do trecho ou no do
        # parágrafo - o que estiver mais perto do texto vale.
        propriedades = trecho.find(f"{W}rPr")
        oculto = _oculto_escrito(propriedades)
        if oculto is None:
            oculto = _estilo_oculto(_valor(propriedades, "rStyle"), self.estilos)
        if oculto is None:
            oculto = self._paragrafo_oculto
        if oculto:
            # Só conta para a faixa o trecho com letra de verdade: o Word marca
            # como ocultos pedaços sem texto (a marca de um campo), e a faixa
            # avisaria de um texto que não existe (lente crítica da etapa 4).
            if any((t.text or "").strip() for t in trecho.iter(f"{W}t")):
                self.texto_oculto = True
            return
        for filho in trecho:
            nome = _nome(filho)
            if nome == "t":
                partes.append(filho.text or "")
            elif nome == "tab":
                partes.append("\t")
            elif nome in ("br", "cr"):
                partes.append("\n")
            elif nome == "noBreakHyphen":
                partes.append("-")
            elif nome == "footnoteReference":
                partes.append(self._marca_da_nota("footnote", filho.get(f"{W}id")))
            elif nome == "endnoteReference":
                partes.append(self._marca_da_nota("endnote", filho.get(f"{W}id")))
            elif nome in ("AlternateContent", "drawing", "pict", "object"):
                caixas += _conteudos_de_caixa(filho)
                # A imagem é contada só na passada que escreve o texto: a
                # primeira passada pelo corpo, a das notas, a contaria de novo.
                if self.numeros is not None and _e_imagem(filho):
                    self.imagens += 1


def _e_imagem(desenho):
    """Se o desenho é imagem para a faixa (RN-26): foto, gráfico, diagrama,
    objeto colado (uma planilha) ou forma. Só a caixa de texto pura não é: o
    texto dela vai para o arquivo."""
    if _nome(desenho) == "AlternateContent":
        escolhas = [filho for filho in desenho if _nome(filho) in ("Choice", "Fallback")]
        if not escolhas:
            return False
        desenho = escolhas[0]
    nomes = set(_nomes_fora_da_caixa(desenho))
    return any(marca in nomes for marca in MARCAS_DE_IMAGEM) or "txbxContent" not in nomes


def _nomes_fora_da_caixa(no):
    """As marcações do desenho, sem entrar no miolo de uma caixa de texto.

    A imagem colada dentro da caixa é contada quando o miolo da caixa é lido;
    olhando lá dentro também aqui, ela era contada duas vezes (lente crítica
    da etapa 5).
    """
    yield _nome(no)
    if _nome(no) != "txbxContent":
        for filho in no:
            yield from _nomes_fora_da_caixa(filho)


def _conteudos_de_caixa(no):
    """O miolo de cada caixa de texto de um desenho, uma vez cada.

    O Word grava a caixa de texto duas vezes: no jeito de hoje e num jeito
    antigo, para versões velhas do Word, lado a lado. Só o primeiro jeito é
    lido; os dois juntos fariam o texto da caixa - e um CPF dentro dela -
    aparecer duas vezes.

    E a busca não entra no miolo de uma caixa já achada: a caixa dentro dela é
    achada de novo quando o miolo for lido. Entrando, ela saía duas ou três
    vezes (lente crítica da etapa 3).
    """
    nome = _nome(no)
    if nome == "txbxContent":
        return [no]
    if nome == "AlternateContent":
        escolhas = [filho for filho in no if _nome(filho) in ("Choice", "Fallback")]
        return _conteudos_de_caixa(escolhas[0]) if escolhas else []
    achados = []
    for filho in no:
        achados += _conteudos_de_caixa(filho)
    return achados


# ----------------------------------------------------------------- estilos

def _estilos(raiz):
    """Os estilos do documento, pelo código que o parágrafo usa para citá-los.

    O parágrafo não diz "Título 1": ele diz o código do estilo, que muda de
    documento para documento (e com o idioma do Word). O nome de verdade e o
    estilo de que ele herda moram no `word/styles.xml`.
    """
    estilos = {}
    for estilo in (raiz.iter(f"{W}style") if raiz is not None else ()):
        nome = estilo.find(f"{W}name")
        base = estilo.find(f"{W}basedOn")
        estilos[estilo.get(f"{W}styleId")] = (
            (nome.get(f"{W}val") or "").lower() if nome is not None else "",
            base.get(f"{W}val") if base is not None else None,
            _nivel_de_topico(estilo.find(f"{W}pPr")),
            _oculto_escrito(estilo.find(f"{W}rPr")),
            _marca_de_lista(estilo.find(f"{W}pPr")),
        )
    return estilos


def _marca_de_lista(propriedades):
    """(número da lista, nível) que as propriedades marcam, cada um ou None."""
    marca = _marcacao(propriedades, "numPr")
    if marca is None:
        return None
    return _valor(marca, "numId"), _valor(marca, "ilvl")


def _oculto_escrito(propriedades):
    """O que as propriedades dizem do "oculto": True, False, ou None quando
    não dizem nada - e aí vale o que vem de cima (o estilo de que herda)."""
    marca = _marcacao(propriedades, "vanish")
    return None if marca is None else _ligado(marca)


def _estilo_oculto(codigo, estilos):
    """Se o estilo esconde o texto, por ele mesmo ou pelo estilo de que herda.

    Esconder pelo estilo é o mesmo que esconder no trecho: o Word não mostra
    nem imprime (lente crítica da etapa 4). Um estilo que diz "não oculto"
    vale sobre o de cima.
    """
    for _ in range(10):
        if codigo not in estilos:
            return None
        _, base, _, oculto, _ = estilos[codigo]
        if oculto is not None:
            return oculto
        codigo = base
    return None


def _nivel_do_titulo(paragrafo, estilos):
    """De 1 a 6 se o parágrafo é título (RN-28), ou 0 se não é.

    Vale o que o Word marca como título: o estilo "Título" e os "Título 1" a
    "Título 6", também quando outro estilo herda deles, ou o nível de tópico
    posto direto no parágrafo. Texto só em negrito e maior não é título
    (premissa da décima emenda): a formatação some, e o título continua título.
    """
    propriedades = paragrafo.find(f"{W}pPr")
    nivel = _nivel_de_topico(propriedades)
    if nivel:
        return nivel
    codigo = _valor(propriedades, "pStyle")
    # O limite de voltas protege de um estilo que herda de si mesmo, que o
    # Word não grava, mas um arquivo montado por outro programa pode trazer.
    for _ in range(10):
        if codigo not in estilos:
            return 0
        nome, base, nivel, _, _ = estilos[codigo]
        if nome == TITULO:
            return 1
        if nome.startswith(PREFIXO_DE_TITULO):
            numero = nome[len(PREFIXO_DE_TITULO):]
            if numero.isdigit() and 1 <= int(numero) <= NIVEL_MAXIMO:
                return int(numero)
        if nivel:
            return nivel
        codigo = base
    return 0


def _nivel_de_topico(propriedades):
    """O "nível de tópico" que o Word dá ao parágrafo, de 1 a 6.

    O Word grava de 0 a 8, e 9 quer dizer "corpo do texto". Acima do 6 não há
    marcação de título no `.md`, e o parágrafo fica como texto comum.
    """
    valor = _valor(propriedades, "outlineLvl")
    if valor is not None and valor.isdigit() and int(valor) < NIVEL_MAXIMO:
        return int(valor) + 1
    return 0


# ---------------------------------------------------------------- numeração

# Os rótulos que o próprio .md entende como item de lista numerada.
ROTULO_DO_MD = re.compile(r"\d+[.)]")

# Até que nível o Word numera uma lista: de 0 a 8.
NIVEIS_DA_LISTA = 9

ROMANOS = ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
           (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"),
           (4, "IV"), (1, "I"))


class _Numeracao:
    """O número (ou a letra) que o Word mostra na frente de cada item (RN-28).

    O Word não grava o número de cada item: grava a regra da lista (começa em
    1, letra minúscula, "%1.%2") e conta na hora de mostrar. Esta conta é
    refeita aqui, na ordem do documento. Listas que usam a mesma regra
    continuam a contagem uma da outra, como no Word, a não ser que uma delas
    mande recomeçar.
    """

    def __init__(self, raiz):
        # Por regra de lista: o começo, o formato e o rótulo de cada nível.
        self.regras = {}
        # Por lista: a regra que ela usa, e de onde ela manda recomeçar.
        self.listas = {}
        for regra in (raiz.findall(f"{W}abstractNum") if raiz is not None else ()):
            niveis = {}
            for nivel in regra.findall(f"{W}lvl"):
                niveis[_numero(nivel.get(f"{W}ilvl"))] = (
                    _numero(_valor(nivel, "start"), 1),
                    _valor(nivel, "numFmt") or "decimal",
                    _valor(nivel, "lvlText") or "")
            self.regras[regra.get(f"{W}abstractNumId")] = niveis
        for lista in (raiz.findall(f"{W}num") if raiz is not None else ()):
            recomecos = {}
            for troca in lista.findall(f"{W}lvlOverride"):
                inicio = _valor(troca, "startOverride")
                if inicio is not None:
                    recomecos[_numero(troca.get(f"{W}ilvl"))] = _numero(inicio, 1)
            self.listas[lista.get(f"{W}numId")] = (
                _valor(lista, "abstractNumId"), recomecos)
        self.recomecar()

    def recomecar(self):
        self.contagens = {}
        self.ja_usadas = set()

    def rotulo(self, lista, nivel):
        """("marcador", ""), ("nenhum", "") ou ("numero", "1.2") para o item."""
        if lista not in self.listas:
            return "marcador", ""
        regra, recomecos = self.listas[lista]
        niveis = self.regras.get(regra, {})
        inicio, formato, modelo = niveis.get(nivel, (1, "decimal", f"%{nivel + 1}."))
        if formato == "bullet":
            return "marcador", ""
        contagem = self.contagens.setdefault(regra, [None] * NIVEIS_DA_LISTA)
        if lista not in self.ja_usadas:
            self.ja_usadas.add(lista)
            for nivel_que_recomeca, valor in recomecos.items():
                if nivel_que_recomeca < NIVEIS_DA_LISTA:
                    contagem[nivel_que_recomeca] = valor - 1
        if nivel >= NIVEIS_DA_LISTA:
            return "marcador", ""
        atual = contagem[nivel]
        contagem[nivel] = inicio if atual is None else atual + 1
        # O item de um nível faz os níveis de baixo recomeçarem: depois do
        # "2.", o primeiro subitem volta a ser "2.1".
        for de_baixo in range(nivel + 1, NIVEIS_DA_LISTA):
            contagem[de_baixo] = None
        if formato == "none":
            return "nenhum", ""
        for k in range(NIVEIS_DA_LISTA):
            marca = f"%{k + 1}"
            if marca in modelo:
                inicio_k, formato_k, _ = niveis.get(k, (1, "decimal", ""))
                valor = contagem[k] if contagem[k] is not None else inicio_k
                modelo = modelo.replace(marca, _escrever_numero(valor, formato_k))
        return "numero", modelo


def _escrever_numero(valor, formato):
    """O número no formato da lista: 3, 03, c, C, iii ou III."""
    if formato in ("lowerLetter", "upperLetter"):
        # O Word repete a letra depois do "z": aa, bb, cc.
        letra = chr(ord("a") + (valor - 1) % 26) * ((valor - 1) // 26 + 1)
        return letra.upper() if formato == "upperLetter" else letra
    if formato in ("lowerRoman", "upperRoman"):
        romano, resto = "", valor
        for valor_romano, letras in ROMANOS:
            while resto >= valor_romano:
                romano, resto = romano + letras, resto - valor_romano
        return romano.lower() if formato == "lowerRoman" else romano
    if formato == "decimalZero":
        return f"{valor:02d}"
    # Os outros formatos ("primeiro", "um", número por extenso) saem em número:
    # o que importa ao assistente é a ordem, e não a grafia.
    return str(valor)


# ------------------------------------------------------------------ blocos

# O controle de conteúdo do Word (um campo de formulário, um bloco de citação)
# só embrulha parágrafos, linhas ou células: entra-se nele e segue-se a ordem de
# dentro.
EMBRULHOS_DE_BLOCO = ("sdt", "sdtContent", "customXml")

# O que embrulha um pedaço do parágrafo sem mudar o texto dele: o link, o
# trecho inserido com o controle de alterações ligado, o campo simples, as
# marcas de idioma. Entra-se e lê-se o que está dentro.
EMBRULHOS = EMBRULHOS_DE_BLOCO + ("hyperlink", "ins", "smartTag", "fldSimple",
                                  "moveTo", "dir", "bdo")

# Entre dois parágrafos da mesma célula. O `.md` não aceita quebra de linha
# dentro da célula da tabela, e os espaços dos dois lados impedem que a barra
# grude num número - grudada, ela faria um CPF parecer ligado a outro (RN-3).
SEPARADOR_NA_CELULA = " / "

# A linha de separação de baixo do cabeçalho precisa de pelo menos três traços
# para o `.md` reconhecer a tabela.
LARGURA_MINIMA = 3


def _item_de_lista(paragrafo, estilos):
    """(número da lista, nível) do item, ou None quando não é item de lista.

    O Word marca o item no próprio parágrafo ou no estilo dele - o estilo
    "Lista numerada" põe a lista em todo parágrafo que o usa -, e o que está
    no parágrafo vale sobre o do estilo. O número 0 quer dizer "tirado da
    lista", e o parágrafo volta a ser texto comum.
    """
    propriedades = paragrafo.find(f"{W}pPr")
    lista, nivel = _marca_de_lista(propriedades) or (None, None)
    codigo = _valor(propriedades, "pStyle")
    for _ in range(10):
        if (lista is not None and nivel is not None) or codigo not in estilos:
            break
        _, base, _, _, do_estilo = estilos[codigo]
        if do_estilo:
            lista = lista if lista is not None else do_estilo[0]
            nivel = nivel if nivel is not None else do_estilo[1]
        codigo = base
    if lista in (None, "0"):
        return None
    return lista, _numero(nivel)


def _juntar_blocos(blocos):
    """Os blocos viram o texto do `.md`, com uma linha em branco entre eles.

    Itens seguidos da mesma lista ficam colados, sem linha em branco no meio:
    é assim que o `.md` sabe que eles são uma lista só.
    """
    partes = []
    anterior_era_item = False
    for texto, e_item in blocos:
        if partes:
            partes.append("\n" if e_item and anterior_era_item else "\n\n")
        partes.append(texto)
        anterior_era_item = e_item
    return "".join(partes)


def _filhos(no, procurado):
    """As linhas da tabela, ou as células da linha, na ordem.

    Um controle de conteúdo pode embrulhar uma linha ou uma célula: entra-se
    nele, senão o que está dentro sumiria da tabela.
    """
    for filho in no:
        nome = _nome(filho)
        if nome == procurado:
            yield filho
        elif nome in EMBRULHOS_DE_BLOCO:
            yield from _filhos(filho, procurado)


# ------------------------------------------------------------------- miúdos

def _nome(no):
    """O nome da marcação sem o endereço na frente: `p`, `r`, `t`."""
    return no.tag.rsplit("}", 1)[-1]


def _marcacao(no, nome):
    """A marcação de dentro com aquele nome, ou None."""
    return no.find(f"{W}{nome}") if no is not None else None


def _tem(no, nome):
    """Se a marcação existe dentro do nó, valha o que valer."""
    return _marcacao(no, nome) is not None


def _ligado(marcacao):
    """Uma opção do Word como `<w:titlePg/>`: ligada quando existe, a não ser
    que ela diga com todas as letras que está desligada."""
    if marcacao is None:
        return False
    return marcacao.get(f"{W}val") not in ("0", "false", "off")


def _numero(valor, padrao=0):
    """O número escrito numa marcação, ou o padrão quando ela não existe."""
    return int(valor) if valor and valor.isdigit() else padrao


def _valor(no, marcacao):
    """O valor de uma marcação de dentro, como `<w:pStyle w:val="..."/>`."""
    if no is None:
        return None
    achado = no.find(f"{W}{marcacao}")
    return achado.get(f"{W}val") if achado is not None else None

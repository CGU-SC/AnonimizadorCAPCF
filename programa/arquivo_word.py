"""Abre o documento do Word (`.docx`) que a pessoa escolheu no Anonimizar.

Por dentro, o `.docx` é um pacote compactado (um `.zip` com outro nome) de
arquivos de texto com marcações - o XML. O corpo do documento mora no
`word/document.xml`. O programa abre esse pacote com o que já vem no próprio
Python, sem biblioteca nova (décima emenda da spec 003, decisão de 23/10/2026):
a de PDF que o programa usa só abre Word na versão paga, e a python-docx não lê
caixa de texto, nota nem alteração controlada.

O que sai daqui é o texto do documento já no formato do `.md` - títulos com
`#`, listas com `-` -, pronto para a revisão. Nenhuma macro é executada e nada
sai da máquina: o programa só lê texto (RN-20 e RN-23).
"""
import zipfile
import zlib
from pathlib import Path
from xml.etree import ElementTree

from arquivo_texto import ArquivoNaoServe

# O endereço que o Word põe na frente de cada marcação do documento. O
# ElementTree escreve as marcações com ele por extenso, entre chaves.
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Nomes que o Word grava em inglês mesmo no Word em português: "heading 1" é o
# "Título 1" da tela, e "title" é o "Título" (RN-28).
TITULO = "title"
PREFIXO_DE_TITULO = "heading "

# Até que nível de título o `.md` tem marcação: de `#` a `######`.
NIVEL_MAXIMO = 6

ESTRAGADO = (
    "O {nome} não pôde ser lido como documento do Word: ele pode estar "
    "estragado ou ser outro tipo de arquivo com o nome trocado."
)


def ler(caminho):
    """O texto do documento do Word, no formato do `.md`.

    Arquivo que não é um pacote do Word, ou que não tem a parte do corpo, dá
    a frase de "estragado" (RN-30) e não chega à revisão.
    """
    caminho = Path(caminho)
    try:
        with zipfile.ZipFile(caminho) as pacote:
            corpo = ElementTree.fromstring(pacote.read("word/document.xml"))
            estilos = _estilos(pacote)
    # O pacote pode abrir e o conteúdo de dentro estar estragado: um byte
    # trocado no meio dá erro de descompactação (zlib.error), e um Word
    # compactado num formato que o Python não lê dá NotImplementedError. Os dois
    # escapavam e deixavam a tela parada, sem frase nenhuma (lente crítica da
    # etapa 1).
    except (zipfile.BadZipFile, KeyError, ElementTree.ParseError, zlib.error,
            EOFError, NotImplementedError):
        raise ArquivoNaoServe(ESTRAGADO.format(nome=caminho.name))

    documento = corpo.find(f"{W}body")
    if documento is None:
        raise ArquivoNaoServe(ESTRAGADO.format(nome=caminho.name))
    return _juntar_blocos(_blocos(documento, estilos))


# ------------------------------------------------------------------ estilos

def _estilos(pacote):
    """Os estilos do documento, pelo código que o parágrafo usa para citá-los.

    O parágrafo não diz "Título 1": ele diz o código do estilo, que muda de
    documento para documento (e com o idioma do Word). O nome de verdade e o
    estilo de que ele herda moram no `word/styles.xml`.
    """
    try:
        raiz = ElementTree.fromstring(pacote.read("word/styles.xml"))
    except KeyError:
        return {}
    estilos = {}
    for estilo in raiz.iter(f"{W}style"):
        nome = estilo.find(f"{W}name")
        base = estilo.find(f"{W}basedOn")
        estilos[estilo.get(f"{W}styleId")] = (
            (nome.get(f"{W}val") or "").lower() if nome is not None else "",
            base.get(f"{W}val") if base is not None else None,
            _nivel_de_topico(estilo.find(f"{W}pPr")),
        )
    return estilos


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
        nome, base, nivel = estilos[codigo]
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


# ------------------------------------------------------------------- blocos

# O controle de conteúdo do Word (um campo de formulário, um bloco de citação)
# só embrulha parágrafos, linhas ou células: entra-se nele e segue-se a ordem de
# dentro.
EMBRULHOS_DE_BLOCO = ("sdt", "sdtContent", "customXml")

def _blocos(no, estilos):
    """Os parágrafos do documento, na ordem, cada um com o seu jeito de sair.

    Cada bloco é (texto, é item de lista).
    """
    for filho in no:
        nome = _nome(filho)
        if nome == "p":
            bloco = _paragrafo(filho, estilos)
            if bloco:
                yield bloco
        elif nome == "tbl":
            tabela = _tabela(filho)
            if tabela:
                yield tabela, False
        elif nome in EMBRULHOS_DE_BLOCO:
            yield from _blocos(filho, estilos)


def _paragrafo(paragrafo, estilos):
    texto = _texto_do_paragrafo(paragrafo).strip()
    if not texto:
        return None
    nivel = _nivel_do_titulo(paragrafo, estilos)
    if nivel:
        return "#" * nivel + " " + texto, False
    profundidade = _profundidade_na_lista(paragrafo)
    if profundidade is not None:
        # Dois espaços por nível é o recuo que o `.md` entende como subitem
        # de uma lista com marcador.
        return "  " * profundidade + "- " + texto, True
    return texto, False


def _profundidade_na_lista(paragrafo):
    """O nível do item (0 é o primeiro), ou None quando não é item de lista.

    O Word marca o item com o número da lista a que ele pertence; o número 0
    quer dizer "tirado da lista", e o parágrafo volta a ser texto comum.
    """
    propriedades = paragrafo.find(f"{W}pPr")
    marca = propriedades.find(f"{W}numPr") if propriedades is not None else None
    if marca is None or _valor(marca, "numId") in (None, "0"):
        return None
    nivel = _valor(marca, "ilvl")
    return int(nivel) if nivel and nivel.isdigit() else 0


# ------------------------------------------------------------------- tabelas

# Entre dois parágrafos da mesma célula. O `.md` não aceita quebra de linha
# dentro da célula da tabela, e os espaços dos dois lados impedem que a barra
# grude num número - grudada, ela faria um CPF parecer ligado a outro (RN-3).
SEPARADOR_NA_CELULA = " / "

# A linha de separação de baixo do cabeçalho precisa de pelo menos três traços
# para o `.md` reconhecer a tabela.
LARGURA_MINIMA = 3


def _tabela(tabela):
    """A tabela do Word como tabela do `.md`, com barras e colunas alinhadas.

    A primeira linha vira o cabeçalho, que é como o `.md` monta toda tabela.
    Tabela sem nenhum texto não sai: seria só um desenho de barras vazio.
    """
    linhas = [_celulas_da_linha(linha) for linha in _filhos(tabela, "tr")]
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


def _celulas_da_linha(linha):
    """O texto de cada posição da linha, com as posições vazias no lugar.

    A célula mesclada na horizontal ocupa várias posições: o texto fica na
    primeira, e as outras ficam vazias (RN-27). A mesclada na vertical o Word
    já grava vazia nas linhas de baixo. Cada texto aparece uma vez só, como no
    Word - repetido, um CPF seria contado e liberado mais de uma vez na revisão.
    """
    celulas = []
    propriedades = linha.find(f"{W}trPr")
    # As posições que a linha pula no começo, quando ela começa mais para a
    # direita que as outras.
    celulas += [""] * _numero(_valor(propriedades, "gridBefore"))
    for celula in _filhos(linha, "tc"):
        celulas.append(_texto_da_celula(celula))
        ocupa = _numero(_valor(celula.find(f"{W}tcPr"), "gridSpan"), 1)
        celulas += [""] * (ocupa - 1)
    return celulas


def _texto_da_celula(celula):
    """Os parágrafos da célula numa linha só, separados por ` / ` (RN-27).

    A tabela dentro de outra entra do mesmo jeito: o texto de cada célula dela,
    na ordem, como texto corrido na célula de fora.
    """
    partes = []
    _partes_da_celula(celula, partes)
    return SEPARADOR_NA_CELULA.join(partes)


def _partes_da_celula(no, partes):
    for filho in no:
        nome = _nome(filho)
        if nome == "p":
            texto = _texto_do_paragrafo(filho)
            # Uma quebra de linha dentro do parágrafo é outra linha da célula;
            # a tabulação vira espaço. A barra vertical do texto sai como `\|`,
            # senão ela partiria a coluna em duas.
            texto = (texto.replace("\n", SEPARADOR_NA_CELULA).replace("\t", " ")
                     .replace("|", "\\|").strip())
            if texto:
                partes.append(texto)
        elif nome == "tbl":
            for linha in _filhos(filho, "tr"):
                for celula in _filhos(linha, "tc"):
                    _partes_da_celula(celula, partes)
        elif nome in EMBRULHOS_DE_BLOCO:
            _partes_da_celula(filho, partes)


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


# ----------------------------------------------------------- o texto do parágrafo

# O que embrulha um pedaço do parágrafo sem mudar o texto dele: o link, o
# trecho inserido com o controle de alterações ligado, o campo simples, as
# marcas de idioma. Entra-se e lê-se o que está dentro.
EMBRULHOS = ("hyperlink", "ins", "smartTag", "customXml", "fldSimple", "sdt",
             "sdtContent", "moveTo", "dir", "bdo")


def _texto_do_paragrafo(paragrafo):
    partes = []
    _ler_pedacos(paragrafo, partes)
    return "".join(partes)


def _ler_pedacos(no, partes):
    """Junta o texto do parágrafo, pedaço por pedaço, na ordem.

    O Word corta o texto em pedaços onde quiser - uma mudança de fonte, a
    correção ortográfica - e um número pode vir partido entre dois. Juntar na
    ordem devolve o número inteiro, e é ele que a busca do CPF vai ver.

    O trecho apagado com o controle de alterações (`del`) não entra: o
    documento sai como ficaria com tudo aceito (RN-25).
    """
    for filho in no:
        nome = _nome(filho)
        if nome == "r":
            _ler_trecho(filho, partes)
        elif nome in EMBRULHOS:
            _ler_pedacos(filho, partes)


def _ler_trecho(trecho, partes):
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


# ------------------------------------------------------------------- miúdos

def _nome(no):
    """O nome da marcação sem o endereço na frente: `p`, `r`, `t`."""
    return no.tag.rsplit("}", 1)[-1]


def _numero(valor, padrao=0):
    """O número escrito numa marcação, ou o padrão quando ela não existe."""
    return int(valor) if valor and valor.isdigit() else padrao


def _valor(no, marcacao):
    """O valor de uma marcação de dentro, como `<w:pStyle w:val="..."/>`."""
    if no is None:
        return None
    achado = no.find(f"{W}{marcacao}")
    return achado.get(f"{W}val") if achado is not None else None

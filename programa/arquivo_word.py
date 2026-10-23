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

def _blocos(no, estilos):
    """Os parágrafos do documento, na ordem, cada um com o seu jeito de sair.

    Cada bloco é (texto, é item de lista). O controle de conteúdo do Word (um
    campo de formulário, um bloco de citação) só embrulha parágrafos: entra-se
    nele e segue-se a ordem de dentro.
    """
    for filho in no:
        nome = _nome(filho)
        if nome == "p":
            bloco = _paragrafo(filho, estilos)
            if bloco:
                yield bloco
        elif nome in ("sdt", "sdtContent", "customXml"):
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


def _valor(no, marcacao):
    """O valor de uma marcação de dentro, como `<w:pStyle w:val="..."/>`."""
    if no is None:
        return None
    achado = no.find(f"{W}{marcacao}")
    return achado.get(f"{W}val") if achado is not None else None

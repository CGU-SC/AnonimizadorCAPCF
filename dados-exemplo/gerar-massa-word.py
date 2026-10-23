"""Gera os documentos do Word inventados da massa do Anonimizar (décima emenda).

Para refazer, da raiz do projeto:

    .\\.venv\\Scripts\\python.exe dados-exemplo\\gerar-massa-word.py

O `.docx` é montado à mão, peça por peça, com o que já vem no Python - o mesmo
jeito com que o programa o lê. Nenhum documento de verdade entra aqui, nem como
modelo: tudo o que está escrito nele foi inventado. Os CPFs que passam na conta
são só de dígitos repetidos (RN-22 da spec 003).

O arquivo sai idêntico toda vez: a data de cada peça dentro do pacote é fixa,
para o git não acusar mudança num documento que não mudou.
"""
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

PASTA = Path(__file__).parent

# Uma data fixa para as peças do pacote. Com a data do dia, o arquivo mudaria a
# cada vez que o script rodasse, mesmo com o mesmo conteúdo.
DATA_FIXA = (2026, 1, 1, 0, 0, 0)

ESPACOS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
           'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')

TIPOS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
</Types>"""

LIGACOES_DO_PACOTE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

LIGACOES_DO_DOCUMENTO = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>"""

# Os códigos dos estilos imitam os do Word em português ("Ttulo1"), que não
# dizem o nível: o programa tem que achar o nível pelo nome do estilo.
ESTILOS = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {ESPACOS}>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Ttulo"><w:name w:val="Title"/><w:basedOn w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Ttulo1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Ttulo2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Destaque"><w:name w:val="Destaque da fundacao"/><w:basedOn w:val="Ttulo2"/></w:style>
<w:style w:type="paragraph" w:styleId="PargrafodaLista"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/></w:style>
</w:styles>"""

# Uma lista com marcador, de dois níveis.
NUMERACAO = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering {ESPACOS}>
<w:abstractNum w:abstractNumId="0">
<w:lvl w:ilvl="0"><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/></w:lvl>
<w:lvl w:ilvl="1"><w:numFmt w:val="bullet"/><w:lvlText w:val="o"/></w:lvl>
</w:abstractNum>
<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>"""


# --------------------------------------------------------------- peças do texto

def trecho(texto, negrito=False):
    """Um pedaço de texto, como o Word grava: `<w:r><w:t>...</w:t></w:r>`."""
    formato = "<w:rPr><w:b/></w:rPr>" if negrito else ""
    return f'<w:r>{formato}<w:t xml:space="preserve">{escape(texto)}</w:t></w:r>'


def paragrafo(*trechos, estilo=None, lista=None, nivel=0):
    propriedades = ""
    if estilo:
        propriedades += f'<w:pStyle w:val="{estilo}"/>'
    if lista:
        propriedades += f'<w:numPr><w:ilvl w:val="{nivel}"/><w:numId w:val="{lista}"/></w:numPr>'
    if propriedades:
        propriedades = f"<w:pPr>{propriedades}</w:pPr>"
    conteudo = "".join(t if t.startswith("<") else trecho(t) for t in trechos)
    return f"<w:p>{propriedades}{conteudo}</w:p>"


# ------------------------------------------------------------- o documento 18

def corpo_do_documento():
    """O relatório inventado, com um caso de cada coisa que o programa lê.

    Cada caso tem uma razão de estar aqui, escrita ao lado.
    """
    return "".join([
        paragrafo("Relatório de execução", estilo="Ttulo"),
        paragrafo("Projeto Exemplo de Extensão — termo de outorga nº 4521/2026."),
        paragrafo("Identificação", estilo="Ttulo1"),
        # O CPF inteiro num pedaço só: o caso simples.
        paragrafo("Coordenadora: Ana Suposta Lima, CPF 111.111.111-11."),
        # O mesmo CPF partido em três pedaços, como o Word faz quando a
        # correção ortográfica ou uma mudança de fonte passa no meio dele. Só
        # juntando os pedaços na ordem a busca vê o número inteiro.
        paragrafo("Vice-coordenador: Davi Hipotético, CPF ",
                  trecho("222.222", negrito=True), trecho(".222"), trecho("-22"),
                  "."),
        paragrafo("Bolsistas", estilo="Ttulo2"),
        paragrafo("Ivo Fictício, CPF 333.333.333-33", lista=1),
        paragrafo("bolsa de extensão, 12 parcelas", lista=1, nivel=1),
        paragrafo("Otávio Suposto, CPF 444.444.444-44", lista=1),
        # Um estilo próprio da fundação, que herda do "Título 2": continua
        # sendo título, de nível 2.
        paragrafo("Prestação de contas", estilo="Destaque"),
        # Texto em negrito não é título (premissa da décima emenda).
        paragrafo(trecho("Saldo devolvido à conta do projeto.", negrito=True)),
        # Parágrafo vazio: o Word grava, e o .md não precisa de três linhas em
        # branco por causa dele.
        paragrafo(),
        paragrafo("Florianópolis, 30 de setembro de 2026."),
    ])


def documento(corpo):
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f"<w:document {ESPACOS}><w:body>{corpo}<w:sectPr/></w:body></w:document>")


def gravar_pacote(caminho, pecas):
    with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as pacote:
        for nome, conteudo in pecas.items():
            info = zipfile.ZipInfo(nome, date_time=DATA_FIXA)
            info.compress_type = zipfile.ZIP_DEFLATED
            pacote.writestr(info, conteudo)


def main():
    gravar_pacote(PASTA / "18-documento-do-word.docx", {
        "[Content_Types].xml": TIPOS,
        "_rels/.rels": LIGACOES_DO_PACOTE,
        "word/_rels/document.xml.rels": LIGACOES_DO_DOCUMENTO,
        "word/document.xml": documento(corpo_do_documento()),
        "word/styles.xml": ESTILOS,
        "word/numbering.xml": NUMERACAO,
    })
    # Um arquivo de texto qualquer com o nome trocado para .docx: não é pacote
    # do Word, e tem de dar a frase de "estragado" em vez de travar (RN-30).
    (PASTA / "19-nao-e-word.docx").write_bytes(
        "Este arquivo é texto comum, com o nome trocado para .docx.\n".encode("utf-8"))
    print("Gerados 18-documento-do-word.docx e 19-nao-e-word.docx")


if __name__ == "__main__":
    main()

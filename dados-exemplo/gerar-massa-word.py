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
           'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
           'xmlns:v="urn:schemas-microsoft-com:vml"')

TIPOS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
<Override PartName="/word/header2.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
<Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>
<Override PartName="/word/endnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.endnotes+xml"/>
<Override PartName="/word/comments.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>
</Types>"""

LIGACOES_DO_PACOTE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

LIGACOES_DO_DOCUMENTO = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header2.xml"/>
<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
<Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>
<Relationship Id="rId7" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/endnotes" Target="endnotes.xml"/>
<Relationship Id="rId8" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="https://bolsas.exemplo.invalid/ficha?cpf=11111111111" TargetMode="External"/>
<Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" Target="comments.xml"/>
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


def celula(*conteudo, ocupa=1, mescla_vertical=None):
    """Uma célula da tabela. `ocupa` mescla na horizontal; `mescla_vertical` é
    "restart" na primeira linha da mescla e "continue" nas de baixo, que o Word
    grava vazias."""
    propriedades = ""
    if ocupa > 1:
        propriedades += f'<w:gridSpan w:val="{ocupa}"/>'
    if mescla_vertical:
        propriedades += f'<w:vMerge w:val="{mescla_vertical}"/>'
    if propriedades:
        propriedades = f"<w:tcPr>{propriedades}</w:tcPr>"
    # A célula do Word tem sempre pelo menos um parágrafo, mesmo vazia.
    miolo = "".join(c if c.startswith("<w:") else paragrafo(c) for c in conteudo)
    return f"<w:tc>{propriedades}{miolo or paragrafo()}</w:tc>"


def tabela(*linhas):
    return "<w:tbl>" + "".join(f"<w:tr>{''.join(l)}</w:tr>" for l in linhas) + "</w:tbl>"


MARCA_DE_ALTERACAO = 'w:author="Revisora Exemplo" w:date="2026-09-30T00:00:00Z"'


def oculto(texto):
    """Um trecho formatado como "oculto": não aparece no Word nem é impresso."""
    return (f'<w:r><w:rPr><w:vanish/></w:rPr>'
            f'<w:t xml:space="preserve">{escape(texto)}</w:t></w:r>')


def inserido(texto, codigo):
    """Um trecho incluído com o "controlar alterações" ligado."""
    return f'<w:ins w:id="{codigo}" {MARCA_DE_ALTERACAO}>{trecho(texto)}</w:ins>'


def apagado(texto, codigo):
    """Um trecho apagado com o "controlar alterações" ligado: o Word o mostra
    riscado, e ele continua dentro do arquivo."""
    return (f'<w:del w:id="{codigo}" {MARCA_DE_ALTERACAO}><w:r>'
            f'<w:delText xml:space="preserve">{escape(texto)}</w:delText></w:r></w:del>')


def link(texto, ligacao):
    return f'<w:hyperlink r:id="{ligacao}">{trecho(texto)}</w:hyperlink>'


def comentario_chamado(codigo):
    """O ponto do texto em que um comentário (o balão na margem) está preso."""
    return f'<w:r><w:commentReference w:id="{codigo}"/></w:r>'


def campo(instrucao, resultado):
    """Um campo automático, como o número da página: a fórmula fica guardada
    (instrText) e o Word mostra o resultado, que é o que vai para o .md."""
    return ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> {instrucao} </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            f"{trecho(resultado)}"
            '<w:r><w:fldChar w:fldCharType="end"/></w:r>')


def chamada_de_nota(tipo, codigo):
    """O número pequeno, no meio do texto, que chama a nota de rodapé ou de fim."""
    return f'<w:r><w:{tipo}Reference w:id="{codigo}"/></w:r>'


def caixa_de_texto(*paragrafos):
    """Uma caixa de texto, no jeito que todo Word abre (o desenho antigo).

    O jeito de hoje grava a caixa duas vezes, lado a lado; esse caso é
    conferido nos testes do programa, com o Word montado ali mesmo.
    """
    return ('<w:r><w:pict><v:shape style="width:260pt;height:40pt" type="#_x0000_t202">'
            '<v:textbox><w:txbxContent>' + "".join(paragrafos)
            + '</w:txbxContent></v:textbox></v:shape></w:pict></w:r>')


def secao(cabecalho, rodape):
    """A marca de fim de uma parte do documento, com o cabeçalho e o rodapé dela."""
    return (f'<w:sectPr><w:headerReference w:type="default" r:id="{cabecalho}"/>'
            f'<w:footerReference w:type="default" r:id="{rodape}"/></w:sectPr>')


def peca(raiz, conteudo):
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f"<w:{raiz} {ESPACOS}>{conteudo}</w:{raiz}>")


# O cabeçalho da primeira parte do documento, e um diferente para o anexo: os
# dois aparecem no começo do .md, uma vez cada. O rodapé é o mesmo nas duas
# partes, e aparece uma vez só.
CABECALHO_1 = peca("hdr", paragrafo("FUNDAÇÃO EXEMPLO DE APOIO — Processo 23000.000000/2026-00"))
CABECALHO_2 = peca("hdr", paragrafo("ANEXO — Comprovantes de pagamento"))
RODAPE = peca("ftr", paragrafo("Relatório de execução — documento de exemplo, inventado — Página ",
                               campo("PAGE", "1"), " de 3"))

# Os comentários (os balões na margem): nunca vão para o .md, e a faixa conta
# quantos eram. O segundo tem um CPF, que não pode aparecer em lugar nenhum.
COMENTARIOS = peca("comments", (
    '<w:comment w:id="0" w:author="Revisora Exemplo">'
    + paragrafo("Conferir o termo de outorga.") + "</w:comment>"
    '<w:comment w:id="1" w:author="Revisora Exemplo">'
    + paragrafo("Ver a ficha do CPF 888.888.888-88.") + "</w:comment>"))

# As duas primeiras notas são as separadoras que o Word grava sozinho em todo
# documento com nota; elas não são chamadas no texto e não saem no .md.
SEPARADORAS = ('<w:{t} w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:{t}>'
               '<w:{t} w:type="continuationSeparator" w:id="0"><w:p><w:r>'
               '<w:continuationSeparator/></w:r></w:p></w:{t}>')
NOTAS_DE_RODAPE = peca("footnotes", SEPARADORAS.format(t="footnote") + (
    '<w:footnote w:id="1"><w:p><w:r><w:footnoteRef/></w:r>'
    + trecho(" Conforme o plano de trabalho aprovado; bolsista substituto, CPF 666.666.666-66.")
    + "</w:p></w:footnote>"))
NOTAS_DE_FIM = peca("endnotes", SEPARADORAS.format(t="endnote") + (
    '<w:endnote w:id="1"><w:p><w:r><w:endnoteRef/></w:r>'
    + trecho(" Valores conferidos pela coordenação do projeto.") + "</w:p></w:endnote>"))


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
        # A nota de rodapé é chamada aqui, e o texto dela (com um CPF) vai para
        # o fim do .md.
        paragrafo("Coordenadora: Ana Suposta Lima, CPF 111.111.111-11.",
                  chamada_de_nota("footnote", 1)),
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
        # A tabela de pagamentos, com um caso difícil em cada linha.
        tabela(
            [celula("Bolsista"), celula("CPF"), celula("Valor")],
            [celula("Ana Suposta Lima"), celula("111.111.111-11"), celula("R$ 1.500,00")],
            # O CPF que perdeu o zero da frente, numa coluna: a máscara cresce
            # e a coluna tem de continuar reta (nona emenda).
            [celula("Ivo Fictício"), celula("0000000000"), celula("R$ 900,00")],
            # Dois parágrafos na mesma célula: saem na mesma linha, com " / ".
            [celula("Otávio Suposto", "(bolsa encerrada em agosto)"),
             celula("444.444.444-44"), celula("R$ 0,00")],
            # Mesclada em duas colunas: o texto fica na primeira posição.
            [celula("Total pago", ocupa=2), celula("R$ 2.400,00")],
            # Uma linha apagada com o "controlar alterações" ligado: não sai.
            ['<w:trPr><w:del w:id="20" ' + MARCA_DE_ALTERACAO + "/></w:trPr>",
             celula(paragrafo(apagado("Caio Removido", 21))),
             celula(paragrafo(apagado("555.555.555-55", 22))),
             celula(paragrafo(apagado("R$ 300,00", 23)))],
        ),
        # O que o Word guarda e não imprime (etapa 4): nada disso vai para o
        # .md, e a faixa da revisão avisa.
        paragrafo("Análise", estilo="Ttulo2"),
        paragrafo("Parecer: aprovado.", comentario_chamado(0)),
        paragrafo("Pagamentos conferidos.", comentario_chamado(1),
                  oculto(" Conferidos contra a ficha do CPF 999.999.999-99.")),
        paragrafo("Bolsista incluída na revisão: ",
                  inserido("Beatriz Inventada, CPF 111.111.111-11", 10),
                  apagado("Caio Removido, CPF 555.555.555-55", 11), "."),
        # Do link vai só o texto que aparece; o endereço por trás dele, que
        # aqui termina num número de 11 dígitos, não vai.
        paragrafo("Ficha completa no ", link("sistema de bolsas", "rId8"), "."),
        paragrafo("Plano de trabalho", estilo="Ttulo2"),
        tabela(
            [celula("Projeto"), celula("Atividade"), celula("Responsáveis")],
            # Mesclada na vertical; uma barra escrita no texto, que não pode
            # partir a coluna; e uma tabela dentro da célula.
            [celula("Projeto Exemplo", mescla_vertical="restart"),
             celula("Oficinas | rodas de conversa"),
             celula(tabela([celula("Ana Suposta Lima"),
                            celula("Davi Hipotético, CPF 222.222.222-22")]))],
            [celula(mescla_vertical="continue"), celula("Relatório final"),
             celula("Ana Suposta Lima")],
        ),
        # A caixa de texto presa neste parágrafo sai logo depois dele.
        paragrafo("Observação da coordenação:",
                  caixa_de_texto(paragrafo("Pagamento ao bolsista Ivo Fictício confirmado; "
                                           "conta do CPF 777.777.777-77."))),
        # O fim da primeira parte do documento: daqui para baixo vale o
        # cabeçalho do anexo, diferente, e o mesmo rodapé.
        f"<w:p><w:pPr>{secao('rId3', 'rId5')}</w:pPr></w:p>",
        # Um estilo próprio da fundação, que herda do "Título 2": continua
        # sendo título, de nível 2.
        paragrafo("Prestação de contas", estilo="Destaque"),
        # Texto em negrito não é título (premissa da décima emenda). E a nota
        # de fim chamada aqui continua a numeração da de rodapé.
        paragrafo(trecho("Saldo devolvido à conta do projeto.", negrito=True),
                  chamada_de_nota("endnote", 1)),
        # Parágrafo vazio: o Word grava, e o .md não precisa de três linhas em
        # branco por causa dele.
        paragrafo(),
        paragrafo("Florianópolis, 30 de setembro de 2026."),
    ])


def documento(corpo):
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f"<w:document {ESPACOS}><w:body>{corpo}{secao('rId4', 'rId5')}</w:body></w:document>")


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
        "word/header1.xml": CABECALHO_1,
        "word/header2.xml": CABECALHO_2,
        "word/footer1.xml": RODAPE,
        "word/footnotes.xml": NOTAS_DE_RODAPE,
        "word/endnotes.xml": NOTAS_DE_FIM,
        "word/comments.xml": COMENTARIOS,
    })
    # Um arquivo de texto qualquer com o nome trocado para .docx: não é pacote
    # do Word, e tem de dar a frase de "estragado" em vez de travar (RN-30).
    (PASTA / "19-nao-e-word.docx").write_bytes(
        "Este arquivo é texto comum, com o nome trocado para .docx.\n".encode("utf-8"))
    print("Gerados 18-documento-do-word.docx e 19-nao-e-word.docx")


if __name__ == "__main__":
    main()

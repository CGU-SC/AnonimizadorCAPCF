"""Testes da leitura do documento do Word (décima emenda da spec 003).

Os documentos são montados aqui mesmo, peça por peça, com o mínimo que o caso
pede: assim cada teste mostra o pedaço do Word que ele confere, sem depender de
um arquivo pronto.
"""
import zipfile
from pathlib import Path

import pytest

import arquivo_word
from arquivo_texto import ArquivoNaoServe

MASSA = Path(__file__).parent.parent / "dados-exemplo"

ESPACOS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def _word(tmp_path, corpo, estilos=None, nome="teste.docx"):
    caminho = tmp_path / nome
    with zipfile.ZipFile(caminho, "w") as pacote:
        pacote.writestr(
            "word/document.xml",
            f"<w:document {ESPACOS}><w:body>{corpo}</w:body></w:document>")
        if estilos:
            pacote.writestr("word/styles.xml",
                            f"<w:styles {ESPACOS}>{estilos}</w:styles>")
    return caminho


def _p(texto, propriedades=""):
    return f"<w:p><w:pPr>{propriedades}</w:pPr><w:r><w:t>{texto}</w:t></w:r></w:p>"


def test_paragrafos_separados_por_linha_em_branco(tmp_path):
    caminho = _word(tmp_path, _p("Primeiro.") + _p("Segundo."))
    assert arquivo_word.ler(caminho) == "Primeiro.\n\nSegundo."


def test_o_numero_partido_em_pedacos_volta_inteiro(tmp_path):
    corpo = ("<w:p><w:r><w:t>CPF 111.111</w:t></w:r><w:r><w:t>.111</w:t></w:r>"
             "<w:r><w:t>-11</w:t></w:r></w:p>")
    assert arquivo_word.ler(_word(tmp_path, corpo)) == "CPF 111.111.111-11"


def test_titulo_pelo_nome_do_estilo_e_pela_heranca(tmp_path):
    estilos = (
        '<w:style w:styleId="Ttulo"><w:name w:val="Title"/></w:style>'
        '<w:style w:styleId="Ttulo2"><w:name w:val="heading 2"/></w:style>'
        '<w:style w:styleId="Meu"><w:name w:val="Meu titulo"/>'
        '<w:basedOn w:val="Ttulo2"/></w:style>')
    corpo = (_p("Capa", '<w:pStyle w:val="Ttulo"/>')
             + _p("Seção", '<w:pStyle w:val="Ttulo2"/>')
             + _p("Herdado", '<w:pStyle w:val="Meu"/>')
             + _p("Tópico", '<w:outlineLvl w:val="2"/>'))
    assert arquivo_word.ler(_word(tmp_path, corpo, estilos)) == (
        "# Capa\n\n## Seção\n\n## Herdado\n\n### Tópico")


def test_negrito_nao_vira_titulo_nem_asterisco(tmp_path):
    corpo = "<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Saldo</w:t></w:r></w:p>"
    assert arquivo_word.ler(_word(tmp_path, corpo)) == "Saldo"


def test_lista_com_subitem_fica_colada_e_recuada(tmp_path):
    item = '<w:numPr><w:ilvl w:val="{}"/><w:numId w:val="1"/></w:numPr>'
    corpo = (_p("Antes.") + _p("um", item.format(0)) + _p("sub", item.format(1))
             + _p("dois", item.format(0)) + _p("Depois."))
    assert arquivo_word.ler(_word(tmp_path, corpo)) == (
        "Antes.\n\n- um\n  - sub\n- dois\n\nDepois.")


def test_paragrafo_vazio_nao_deixa_buraco(tmp_path):
    corpo = _p("A") + "<w:p/>" + "<w:p><w:r><w:t> </w:t></w:r></w:p>" + _p("B")
    assert arquivo_word.ler(_word(tmp_path, corpo)) == "A\n\nB"


def test_o_trecho_apagado_nao_entra_e_o_inserido_entra(tmp_path):
    """RN-25: o documento como ficaria com tudo aceito."""
    corpo = ("<w:p><w:r><w:t>CPF </w:t></w:r>"
             "<w:del><w:r><w:delText>222.222.222-22</w:delText></w:r></w:del>"
             "<w:ins><w:r><w:t>111.111.111-11</w:t></w:r></w:ins></w:p>")
    assert arquivo_word.ler(_word(tmp_path, corpo)) == "CPF 111.111.111-11"


def test_controle_de_conteudo_e_lido_por_dentro(tmp_path):
    corpo = f"<w:sdt><w:sdtContent>{_p('Dentro do campo.')}</w:sdtContent></w:sdt>"
    assert arquivo_word.ler(_word(tmp_path, corpo)) == "Dentro do campo."


def test_quebra_de_linha_e_tabulacao(tmp_path):
    corpo = "<w:p><w:r><w:t>a</w:t><w:tab/><w:t>b</w:t><w:br/><w:t>c</w:t></w:r></w:p>"
    assert arquivo_word.ler(_word(tmp_path, corpo)) == "a\tb\nc"


@pytest.mark.parametrize("conteudo", [b"texto comum", b"PK\x03\x04quebrado"])
def test_o_que_nao_e_pacote_do_word_da_a_frase_de_estragado(tmp_path, conteudo):
    caminho = tmp_path / "relatorio.docx"
    caminho.write_bytes(conteudo)
    with pytest.raises(ArquivoNaoServe) as erro:
        arquivo_word.ler(caminho)
    assert "relatorio.docx" in str(erro.value)
    assert "estragado" in str(erro.value)


def test_conteudo_estragado_por_dentro_da_a_frase_e_nao_escapa(tmp_path):
    """Regressão da lente crítica da etapa 1: o pacote abre, mas o conteúdo
    compactado de dentro está corrompido - ou compactado num formato que o
    Python não lê. Antes, o erro escapava e a tela ficava parada, sem frase."""
    original = (MASSA / "18-documento-do-word.docx").read_bytes()
    corrompido = bytearray(original)
    meio = original.find(b"word/document.xml") + 60
    corrompido[meio] ^= 0xFF
    corrompido[meio + 1] ^= 0xFF
    caminho = tmp_path / "corrompido.docx"
    caminho.write_bytes(bytes(corrompido))
    with pytest.raises(ArquivoNaoServe):
        arquivo_word.ler(caminho)

    with zipfile.ZipFile(tmp_path / "base.zip", "w", zipfile.ZIP_STORED) as pacote:
        pacote.writestr("word/document.xml", "<a/>")
    formato_raro = bytearray((tmp_path / "base.zip").read_bytes())
    # 9 é o "deflate64", um jeito de compactar que o Python não sabe abrir: a
    # marca vai no cabeçalho de cada peça e no índice do fim do pacote.
    for posicao in (8, formato_raro.find(b"PK\x01\x02") + 10):
        formato_raro[posicao:posicao + 2] = (9).to_bytes(2, "little")
    caminho = tmp_path / "formato-raro.docx"
    caminho.write_bytes(bytes(formato_raro))
    with pytest.raises(ArquivoNaoServe):
        arquivo_word.ler(caminho)


def test_pacote_sem_a_parte_do_corpo_da_a_frase_de_estragado(tmp_path):
    caminho = tmp_path / "sem-corpo.docx"
    with zipfile.ZipFile(caminho, "w") as pacote:
        pacote.writestr("outra-coisa.xml", "<a/>")
    with pytest.raises(ArquivoNaoServe):
        arquivo_word.ler(caminho)


def test_o_word_da_massa():
    """O documento 18, inteiro: é ele que a conferência 04 mostra."""
    assert arquivo_word.ler(MASSA / "18-documento-do-word.docx") == (
        "# Relatório de execução\n\n"
        "Projeto Exemplo de Extensão — termo de outorga nº 4521/2026.\n\n"
        "# Identificação\n\n"
        "Coordenadora: Ana Suposta Lima, CPF 111.111.111-11.\n\n"
        "Vice-coordenador: Davi Hipotético, CPF 222.222.222-22.\n\n"
        "## Bolsistas\n\n"
        "- Ivo Fictício, CPF 333.333.333-33\n"
        "  - bolsa de extensão, 12 parcelas\n"
        "- Otávio Suposto, CPF 444.444.444-44\n\n"
        "## Prestação de contas\n\n"
        "Saldo devolvido à conta do projeto.\n\n"
        "Florianópolis, 30 de setembro de 2026.")

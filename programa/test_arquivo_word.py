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


def _texto(caminho):
    """Só o texto que vai para a revisão; o que ficou de fora tem testes à parte."""
    return arquivo_word.ler(caminho).texto


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
    assert _texto(caminho) == "Primeiro.\n\nSegundo."


def test_o_numero_partido_em_pedacos_volta_inteiro(tmp_path):
    corpo = ("<w:p><w:r><w:t>CPF 111.111</w:t></w:r><w:r><w:t>.111</w:t></w:r>"
             "<w:r><w:t>-11</w:t></w:r></w:p>")
    assert _texto(_word(tmp_path, corpo)) == "CPF 111.111.111-11"


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
    assert _texto(_word(tmp_path, corpo, estilos)) == (
        "# Capa\n\n## Seção\n\n## Herdado\n\n### Tópico")


def test_negrito_nao_vira_titulo_nem_asterisco(tmp_path):
    corpo = "<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Saldo</w:t></w:r></w:p>"
    assert _texto(_word(tmp_path, corpo)) == "Saldo"


def test_lista_com_subitem_fica_colada_e_recuada(tmp_path):
    item = '<w:numPr><w:ilvl w:val="{}"/><w:numId w:val="1"/></w:numPr>'
    corpo = (_p("Antes.") + _p("um", item.format(0)) + _p("sub", item.format(1))
             + _p("dois", item.format(0)) + _p("Depois."))
    assert _texto(_word(tmp_path, corpo)) == (
        "Antes.\n\n- um\n  - sub\n- dois\n\nDepois.")


def test_paragrafo_vazio_nao_deixa_buraco(tmp_path):
    corpo = _p("A") + "<w:p/>" + "<w:p><w:r><w:t> </w:t></w:r></w:p>" + _p("B")
    assert _texto(_word(tmp_path, corpo)) == "A\n\nB"


def test_o_trecho_apagado_nao_entra_e_o_inserido_entra(tmp_path):
    """RN-25: o documento como ficaria com tudo aceito."""
    corpo = ("<w:p><w:r><w:t>CPF </w:t></w:r>"
             "<w:del><w:r><w:delText>222.222.222-22</w:delText></w:r></w:del>"
             "<w:ins><w:r><w:t>111.111.111-11</w:t></w:r></w:ins></w:p>")
    assert _texto(_word(tmp_path, corpo)) == "CPF 111.111.111-11"


def test_controle_de_conteudo_e_lido_por_dentro(tmp_path):
    corpo = f"<w:sdt><w:sdtContent>{_p('Dentro do campo.')}</w:sdtContent></w:sdt>"
    assert _texto(_word(tmp_path, corpo)) == "Dentro do campo."


def test_quebra_de_linha_e_tabulacao(tmp_path):
    corpo = "<w:p><w:r><w:t>a</w:t><w:tab/><w:t>b</w:t><w:br/><w:t>c</w:t></w:r></w:p>"
    assert _texto(_word(tmp_path, corpo)) == "a\tb\nc"


# ------------------------------------------------------------------ tabelas

def _tc(*conteudo, propriedades=""):
    miolo = "".join(c if c.startswith("<w:") else _p(c) for c in conteudo) or "<w:p/>"
    return f"<w:tc><w:tcPr>{propriedades}</w:tcPr>{miolo}</w:tc>"


def _tbl(*linhas, propriedades_da_linha=""):
    return "<w:tbl>" + "".join(
        f"<w:tr><w:trPr>{propriedades_da_linha}</w:trPr>{''.join(l)}</w:tr>"
        for l in linhas) + "</w:tbl>"


def test_tabela_com_barras_e_colunas_alinhadas(tmp_path):
    corpo = _tbl([_tc("Nome"), _tc("CPF")],
                 [_tc("Ana Suposta Lima"), _tc("111.111.111-11")])
    assert _texto(_word(tmp_path, corpo)) == (
        "| Nome             | CPF            |\n"
        "| ---------------- | -------------- |\n"
        "| Ana Suposta Lima | 111.111.111-11 |")


def test_a_celula_mesclada_aparece_uma_vez_na_primeira_posicao(tmp_path):
    """RN-27: o texto não se repete - repetido, um CPF seria contado duas vezes."""
    corpo = _tbl([_tc("a"), _tc("b"), _tc("c")],
                 [_tc("111.111.111-11", propriedades='<w:gridSpan w:val="2"/>'), _tc("d")])
    texto = _texto(_word(tmp_path, corpo))
    assert texto.count("111.111.111-11") == 1
    assert texto.splitlines()[2] == "| 111.111.111-11 |     | d   |"


def test_mesclada_na_vertical_fica_vazia_embaixo(tmp_path):
    corpo = _tbl([_tc("Projeto", propriedades='<w:vMerge w:val="restart"/>'), _tc("x")],
                 [_tc(propriedades="<w:vMerge/>"), _tc("y")])
    assert _texto(_word(tmp_path, corpo)).splitlines()[2] == "|         | y   |"


def test_dois_paragrafos_e_quebra_de_linha_na_celula(tmp_path):
    quebra = "<w:p><w:r><w:t>linha 1</w:t><w:br/><w:t>linha 2</w:t></w:r></w:p>"
    corpo = _tbl([_tc("um", "dois"), _tc(quebra)])
    assert _texto(_word(tmp_path, corpo)).splitlines()[0] == (
        "| um / dois | linha 1 / linha 2 |")


def test_tabela_dentro_de_outra_vira_texto_corrido(tmp_path):
    de_dentro = _tbl([_tc("Ana"), _tc("CPF 222.222.222-22")])
    corpo = _tbl([_tc("Responsáveis"), _tc(de_dentro)])
    assert _texto(_word(tmp_path, corpo)).splitlines()[0] == (
        "| Responsáveis | Ana / CPF 222.222.222-22 |")


def test_a_barra_vertical_do_texto_nao_parte_a_coluna(tmp_path):
    corpo = _tbl([_tc("a | b"), _tc("c")])
    linha = _texto(_word(tmp_path, corpo)).splitlines()[0]
    assert linha == "| a \\| b | c   |"


def test_linha_que_comeca_mais_a_direita(tmp_path):
    corpo = (_tbl([_tc("a"), _tc("b")])[:-len("</w:tbl>")]
             + '<w:tr><w:trPr><w:gridBefore w:val="1"/></w:trPr>'
             + _tc("só b") + "</w:tr></w:tbl>")
    assert _texto(_word(tmp_path, corpo)).splitlines()[2] == "|     | só b |"


def test_tabela_vazia_nao_sai_e_texto_em_volta_continua(tmp_path):
    corpo = _p("Antes.") + _tbl([_tc(), _tc()]) + _p("Depois.")
    assert _texto(_word(tmp_path, corpo)) == "Antes.\n\nDepois."


def test_o_cpf_curto_na_coluna_continua_com_a_coluna_reta(tmp_path):
    """A máscara do CPF sem o zero cresce, e a compensação da nona emenda tira
    os espaços de depois dele: a tabela do Word continua alinhada."""
    from cpf import aplicar, procurar
    corpo = _tbl([_tc("Bolsista"), _tc("CPF"), _tc("Valor")],
                 [_tc("Ana Suposta Lima"), _tc("111.111.111-11"), _tc("R$ 1,00")],
                 [_tc("Ivo"), _tc("0000000000"), _tc("R$ 2,00")])
    texto = _texto(_word(tmp_path, corpo))
    saida = aplicar(texto, procurar(texto))
    assert "XXX000000XX" in saida
    assert len({len(linha) for linha in saida.splitlines()}) == 1


@pytest.mark.parametrize("conteudo", [b"texto comum", b"PK\x03\x04quebrado"])
def test_o_que_nao_e_pacote_do_word_da_a_frase_de_estragado(tmp_path, conteudo):
    caminho = tmp_path / "relatorio.docx"
    caminho.write_bytes(conteudo)
    with pytest.raises(ArquivoNaoServe) as erro:
        _texto(caminho)
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
        _texto(caminho)

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
        _texto(caminho)


def test_pacote_sem_a_parte_do_corpo_da_a_frase_de_estragado(tmp_path):
    caminho = tmp_path / "sem-corpo.docx"
    with zipfile.ZipFile(caminho, "w") as pacote:
        pacote.writestr("outra-coisa.xml", "<a/>")
    with pytest.raises(ArquivoNaoServe):
        _texto(caminho)


def test_o_word_da_massa():
    """O documento 18, inteiro: é ele que a conferência 04 mostra."""
    assert _texto(MASSA / "18-documento-do-word.docx") == (
        "FUNDAÇÃO EXEMPLO DE APOIO — Processo 23000.000000/2026-00\n\n"
        "ANEXO — Comprovantes de pagamento\n\n"
        "# Relatório de execução\n\n"
        "Projeto Exemplo de Extensão — termo de outorga nº 4521/2026.\n\n"
        "# Identificação\n\n"
        "Coordenadora: Ana Suposta Lima, CPF 111.111.111-11.[^1]\n\n"
        "Vice-coordenador: Davi Hipotético, CPF 222.222.222-22.\n\n"
        "## Bolsistas\n\n"
        "- Ivo Fictício, CPF 333.333.333-33\n"
        "  - bolsa de extensão, 12 parcelas\n"
        "- Otávio Suposto, CPF 444.444.444-44\n\n"
        "| Bolsista                                     | CPF            | Valor       |\n"
        "| -------------------------------------------- | -------------- | ----------- |\n"
        "| Ana Suposta Lima                             | 111.111.111-11 | R$ 1.500,00 |\n"
        "| Ivo Fictício                                 | 0000000000     | R$ 900,00   |\n"
        "| Otávio Suposto / (bolsa encerrada em agosto) | 444.444.444-44 | R$ 0,00     |\n"
        "| Total pago                                   |                | R$ 2.400,00 |\n\n"
        "## Análise\n\n"
        "Parecer: aprovado.\n\n"
        "Pagamentos conferidos.\n\n"
        "Bolsista incluída na revisão: Beatriz Inventada, CPF 111.111.111-11.\n\n"
        "Ficha completa no sistema de bolsas.\n\n"
        "## Plano de trabalho\n\n"
        "| Projeto         | Atividade                     | Responsáveis                                           |\n"
        "| --------------- | ----------------------------- | ------------------------------------------------------ |\n"
        "| Projeto Exemplo | Oficinas \\| rodas de conversa | Ana Suposta Lima / Davi Hipotético, CPF 222.222.222-22 |\n"
        "|                 | Relatório final               | Ana Suposta Lima                                       |\n\n"
        "Observação da coordenação:\n\n"
        "Pagamento ao bolsista Ivo Fictício confirmado; conta do CPF 777.777.777-77.\n\n"
        "## Prestação de contas\n\n"
        "Saldo devolvido à conta do projeto.[^2]\n\n"
        "Florianópolis, 30 de setembro de 2026.\n\n"
        "Relatório de execução — documento de exemplo, inventado — Página 1 de 3\n\n"
        "[^1]: Conforme o plano de trabalho aprovado; bolsista substituto, CPF 666.666.666-66.\n"
        "[^2]: Valores conferidos pela coordenação do projeto.")


# ------------------------------------- cabeçalho, rodapé, notas e caixas (etapa 3)

LIGACOES = "http://schemas.openxmlformats.org/package/2006/relationships"
TIPO = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
ESPACOS_R = ESPACOS + (' xmlns:r="http://schemas.openxmlformats.org/officeDocument/'
                       '2006/relationships"')


def _word_com_pecas(tmp_path, corpo, pecas, ligacoes=()):
    """Um Word com peças a mais (cabeçalho, notas) e as ligações do corpo."""
    caminho = tmp_path / "teste.docx"
    with zipfile.ZipFile(caminho, "w") as pacote:
        pacote.writestr(
            "word/document.xml",
            f"<w:document {ESPACOS_R}><w:body>{corpo}</w:body></w:document>")
        for nome, conteudo in pecas.items():
            pacote.writestr(nome, conteudo)
        pacote.writestr("word/_rels/document.xml.rels", (
            f'<Relationships xmlns="{LIGACOES}">'
            + "".join(f'<Relationship Id="{i}" Type="{TIPO}{t}" Target="{alvo}"{extra}/>'
                      for i, t, alvo, extra in ligacoes)
            + "</Relationships>"))
    return caminho


def _secao(*referencias):
    return "<w:sectPr>" + "".join(
        f'<w:{m}Reference w:type="{tipo}" r:id="{i}"/>' for m, tipo, i in referencias
    ) + "</w:sectPr>"


def _borda(raiz, texto):
    return f"<w:{raiz} {ESPACOS}>{_p(texto)}</w:{raiz}>"


def test_cabecalho_abre_e_rodape_fecha_cada_diferente_uma_vez(tmp_path):
    """RN-24: o mesmo cabeçalho em três partes aparece uma vez; o diferente,
    também, na ordem em que surge."""
    quebra = "<w:p><w:pPr>{}</w:pPr></w:p>"
    corpo = (_p("Parte 1") + quebra.format(_secao(("header", "default", "c1"),
                                                  ("footer", "default", "r1")))
             + _p("Parte 2") + quebra.format(_secao(("header", "default", "c1")))
             + _p("Parte 3") + _secao(("header", "default", "c2"),
                                      ("footer", "default", "r1")))
    caminho = _word_com_pecas(
        tmp_path, corpo,
        {"word/header1.xml": _borda("hdr", "Cabeçalho A"),
         "word/header2.xml": _borda("hdr", "Cabeçalho B"),
         "word/footer1.xml": _borda("ftr", "Rodapé")},
        [("c1", "header", "header1.xml", ""), ("c2", "header", "header2.xml", ""),
         ("r1", "footer", "footer1.xml", "")])
    assert _texto(caminho) == (
        "Cabeçalho A\n\nCabeçalho B\n\nParte 1\n\nParte 2\n\nParte 3\n\nRodapé")


def test_cabecalho_da_primeira_pagina_vem_antes(tmp_path):
    corpo = _p("Corpo") + _secao(("header", "default", "c1"),
                                 ("header", "first", "c2")).replace(
        "</w:sectPr>", "<w:titlePg/></w:sectPr>")
    caminho = _word_com_pecas(
        tmp_path, corpo,
        {"word/header1.xml": _borda("hdr", "Das outras"),
         "word/header2.xml": _borda("hdr", "Da primeira")},
        [("c1", "header", "header1.xml", ""), ("c2", "header", "header2.xml", "")])
    assert _texto(caminho) == "Da primeira\n\nDas outras\n\nCorpo"


def test_cabecalho_de_opcao_desligada_nao_entra(tmp_path):
    """Regressão da lente crítica da etapa 3: o Word guarda o cabeçalho da
    primeira página (e o das pares) depois de a opção ser desligada, e ele
    aparecia no .md sem nunca ser impresso."""
    corpo = _p("Corpo") + _secao(("header", "default", "c1"), ("header", "first", "c2"),
                                 ("header", "even", "c3"))
    pecas = {"word/header1.xml": _borda("hdr", "Impresso"),
             "word/header2.xml": _borda("hdr", "Primeira, desligada"),
             "word/header3.xml": _borda("hdr", "Pares")}
    ligacoes = [("c1", "header", "header1.xml", ""), ("c2", "header", "header2.xml", ""),
                ("c3", "header", "header3.xml", "")]
    assert _texto(_word_com_pecas(tmp_path, corpo, pecas, ligacoes)) == (
        "Impresso\n\nCorpo")
    # Com "pares e ímpares diferentes" ligada, o das pares entra.
    pecas["word/settings.xml"] = f"<w:settings {ESPACOS}><w:evenAndOddHeaders/></w:settings>"
    assert _texto(_word_com_pecas(tmp_path, corpo, pecas, ligacoes)) == (
        "Impresso\n\nPares\n\nCorpo")


def test_cabecalho_de_antes_de_uma_alteracao_controlada_nao_entra(tmp_path):
    """Regressão da lente crítica da etapa 3 (RN-25): a marca de seção guardada
    na alteração cita o cabeçalho de antes, que o documento aceito não tem."""
    antiga = f"<w:sectPrChange>{_secao(('header', 'default', 'velho'))}</w:sectPrChange>"
    corpo = _p("Corpo") + _secao(("header", "default", "novo")).replace(
        "</w:sectPr>", antiga + "</w:sectPr>")
    caminho = _word_com_pecas(
        tmp_path, corpo,
        {"word/header1.xml": _borda("hdr", "Cabeçalho novo"),
         "word/header2.xml": _borda("hdr", "Velho, CPF 111.111.111-11")},
        [("novo", "header", "header1.xml", ""), ("velho", "header", "header2.xml", "")])
    assert _texto(caminho) == "Cabeçalho novo\n\nCorpo"


def test_cabecalho_que_falta_no_pacote_nao_trava(tmp_path):
    corpo = _p("Corpo") + _secao(("header", "default", "c1"))
    caminho = _word_com_pecas(tmp_path, corpo, {},
                              [("c1", "header", "header1.xml", "")])
    assert _texto(caminho) == "Corpo"


def _notas(raiz, *notas):
    separadoras = (f'<w:{raiz} w:type="separator" w:id="-1"><w:p><w:r><w:separator/>'
                   f"</w:r></w:p></w:{raiz}>")
    return (f"<w:{raiz}s {ESPACOS}>{separadoras}" + "".join(
        f'<w:{raiz} w:id="{i}"><w:p><w:r><w:{raiz}Ref/></w:r><w:r><w:t xml:space="preserve"> '
        f"{texto}</w:t></w:r></w:p></w:{raiz}>" for i, texto in notas) + f"</w:{raiz}s>")


def _chama(tipo, i):
    return f'<w:r><w:{tipo}Reference w:id="{i}"/></w:r>'


def test_notas_numeradas_na_ordem_e_as_de_fim_continuam(tmp_path):
    """Premissa da décima emenda: as de rodapé primeiro, as de fim depois."""
    corpo = (f"<w:p><w:r><w:t>Fim antes</w:t></w:r>{_chama('endnote', 5)}</w:p>"
             f"<w:p><w:r><w:t>Rodapé A</w:t></w:r>{_chama('footnote', 9)}</w:p>"
             f"<w:p><w:r><w:t>Rodapé B</w:t></w:r>{_chama('footnote', 2)}</w:p>")
    caminho = _word_com_pecas(tmp_path, corpo, {
        "word/footnotes.xml": _notas("footnote", (2, "Nota B, CPF 111.111.111-11."),
                                     (9, "Nota A.")),
        "word/endnotes.xml": _notas("endnote", (5, "Nota de fim."))})
    assert _texto(caminho) == (
        "Fim antes[^3]\n\nRodapé A[^1]\n\nRodapé B[^2]\n\n"
        "[^1]: Nota A.\n[^2]: Nota B, CPF 111.111.111-11.\n[^3]: Nota de fim.")


def test_nota_chamada_numa_celula_nao_entorta_a_coluna(tmp_path):
    corpo = _tbl([_tc("Nome"), _tc("Valor")],
                 [_tc(f"<w:p><w:r><w:t>Ana</w:t></w:r>{_chama('footnote', 1)}</w:p>"),
                  _tc("R$ 1,00")])
    caminho = _word_com_pecas(tmp_path, corpo, {
        "word/footnotes.xml": _notas("footnote", (1, "Bolsista."))})
    linhas = _texto(caminho).splitlines()
    assert linhas[2] == "| Ana[^1] | R$ 1,00 |"
    assert len({len(linha) for linha in linhas[:3]}) == 1


VML = 'xmlns:v="urn:schemas-microsoft-com:vml"'
MC = 'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"'


def _caixa(texto):
    """A caixa de texto como o Word de hoje grava: duas vezes, lado a lado."""
    return (f"<mc:AlternateContent {MC}><mc:Choice Requires=\"wps\"><w:drawing>"
            f"<w:txbxContent>{_p(texto)}</w:txbxContent></w:drawing></mc:Choice>"
            f"<mc:Fallback><w:pict><v:shape {VML}><v:textbox><w:txbxContent>"
            f"{_p(texto)}</w:txbxContent></v:textbox></v:shape></w:pict></mc:Fallback>"
            f"</mc:AlternateContent>")


def test_caixa_de_texto_sai_uma_vez_depois_do_paragrafo(tmp_path):
    corpo = (f"<w:p><w:r><w:t>Presa aqui.</w:t></w:r>"
             f"<w:r>{_caixa('Na caixa, CPF 111.111.111-11.')}</w:r></w:p>" + _p("Depois."))
    assert _texto(_word(tmp_path, corpo)) == (
        "Presa aqui.\n\nNa caixa, CPF 111.111.111-11.\n\nDepois.")


def test_caixa_de_texto_num_paragrafo_sem_texto(tmp_path):
    corpo = f"<w:p><w:r>{_caixa('Só a caixa.')}</w:r></w:p>"
    assert _texto(_word(tmp_path, corpo)) == "Só a caixa."


def test_caixa_de_texto_dentro_da_celula(tmp_path):
    celula = f"<w:p><w:r><w:t>Nome</w:t></w:r><w:r>{_caixa('da caixa')}</w:r></w:p>"
    corpo = _tbl([_tc(celula), _tc("x")])
    assert _texto(_word(tmp_path, corpo)).splitlines()[0] == (
        "| Nome / da caixa | x   |")


def test_caixa_na_celula_com_barra_e_tabela_nao_parte_a_tabela(tmp_path):
    """Regressão da lente crítica da etapa 3: o texto da caixa entrava na
    célula sem a barra protegida, e a tabela de dentro dela como tabela."""
    miolo = _p("Banco | Conta") + _tbl([_tc("Ag"), _tc("123")])
    caixa = (f"<w:pict><v:shape {VML}><v:textbox><w:txbxContent>{miolo}"
             f"</w:txbxContent></v:textbox></v:shape></w:pict>")
    celula = f"<w:p><w:r><w:t>Dados</w:t></w:r><w:r>{caixa}</w:r></w:p>"
    corpo = _tbl([_tc("A"), _tc("B")], [_tc(celula), _tc("x")])
    linhas = _texto(_word(tmp_path, corpo)).splitlines()
    assert linhas[2].startswith("| Dados / Banco \\| Conta / Ag / 123 |")
    assert len({len(linha) for linha in linhas}) == 1
    assert all(linha.count("|") - linha.count("\\|") == 3 for linha in linhas)


def test_caixa_dentro_de_caixa_sai_uma_vez(tmp_path):
    """Regressão da lente crítica da etapa 3: a caixa de dentro saía duas ou
    três vezes, e o CPF dela era contado repetido na revisão."""
    de_dentro = f"<w:p><w:r>{_caixa('Dentro, CPF 111.111.111-11.')}</w:r></w:p>"
    de_fora = (f"<mc:AlternateContent {MC}><mc:Choice Requires=\"wps\"><w:drawing>"
               f"<w:txbxContent>{_p('Fora.')}{de_dentro}</w:txbxContent></w:drawing>"
               f"</mc:Choice><mc:Fallback><w:pict><v:shape {VML}><v:textbox><w:txbxContent>"
               f"{_p('Fora.')}{de_dentro}</w:txbxContent></v:textbox></v:shape></w:pict>"
               f"</mc:Fallback></mc:AlternateContent>")
    corpo = f"<w:p><w:r>{de_fora}</w:r></w:p>"
    texto = _texto(_word(tmp_path, corpo))
    assert texto.count("111.111.111-11") == 1
    assert texto.count("Fora.") == 1


def test_nota_chamada_fora_do_corpo_nao_derruba_o_documento(tmp_path):
    """Regressão da lente crítica da etapa 3: uma nota chamada de dentro do
    cabeçalho fazia o documento inteiro ser recusado como "estragado"."""
    cabecalho = (f"<w:hdr {ESPACOS}><w:p><w:r><w:t>Topo</w:t></w:r>"
                 f"{_chama('footnote', 1)}</w:p></w:hdr>")
    corpo = _p("Corpo") + _secao(("header", "default", "c1"))
    caminho = _word_com_pecas(
        tmp_path, corpo,
        {"word/header1.xml": cabecalho,
         "word/footnotes.xml": _notas("footnote", (1, "Nota."))},
        [("c1", "header", "header1.xml", "")])
    assert _texto(caminho) == "Topo\n\nCorpo"


# ----------------------------------- o que o Word guarda e não imprime (etapa 4)

def test_o_word_da_massa_conta_o_que_ficou_de_fora():
    word = arquivo_word.ler(MASSA / "18-documento-do-word.docx")
    assert (word.comentarios, word.texto_oculto, word.alteracoes) == (2, True, True)
    # Nenhum dos CPFs que o Word guarda e não imprime chega ao texto: o do
    # comentário, o do texto oculto e o da pessoa excluída na revisão.
    for numero in ("888.888.888-88", "999.999.999-99", "555.555.555-55"):
        assert numero not in word.texto, numero


def test_texto_oculto_fica_de_fora_e_e_contado(tmp_path):
    corpo = ("<w:p><w:r><w:t>Visível.</w:t></w:r><w:r><w:rPr><w:vanish/></w:rPr>"
             "<w:t> CPF 111.111.111-11</w:t></w:r></w:p>")
    word = arquivo_word.ler(_word(tmp_path, corpo))
    assert (word.texto, word.texto_oculto) == ("Visível.", True)


def test_texto_oculto_pelo_estilo_tambem_fica_de_fora(tmp_path):
    """Regressão da lente crítica da etapa 4: o oculto vindo do estilo do
    trecho (ou do parágrafo, ou herdado) entrava no .md, e a faixa não avisava."""
    estilos = (
        '<w:style w:styleId="Oculto"><w:name w:val="Oculto"/>'
        "<w:rPr><w:vanish/></w:rPr></w:style>"
        '<w:style w:styleId="Herda"><w:name w:val="Herda"/>'
        '<w:basedOn w:val="Oculto"/></w:style>'
        '<w:style w:styleId="Volta"><w:name w:val="Volta"/><w:basedOn w:val="Oculto"/>'
        '<w:rPr><w:vanish w:val="0"/></w:rPr></w:style>')
    corpo = ('<w:p><w:r><w:t>Visível.</w:t></w:r><w:r><w:rPr><w:rStyle w:val="Oculto"/>'
             "</w:rPr><w:t> CPF 111.111.111-11</w:t></w:r></w:p>"
             + _p("Do parágrafo, CPF 222.222.222-22", '<w:pStyle w:val="Herda"/>')
             + _p("Desfeito no estilo.", '<w:pStyle w:val="Volta"/>'))
    word = arquivo_word.ler(_word(tmp_path, corpo, estilos))
    assert word.texto == "Visível.\n\nDesfeito no estilo."
    assert word.texto_oculto


def test_oculto_sem_letra_nao_acende_a_faixa(tmp_path):
    """Regressão da lente crítica da etapa 4: o Word marca como ocultos pedaços
    sem texto (a marca de um campo), e a faixa dizia "texto oculto" à toa."""
    corpo = ('<w:p><w:r><w:t>Texto.</w:t></w:r><w:r><w:rPr><w:vanish/></w:rPr>'
             '<w:fldChar w:fldCharType="begin"/></w:r><w:r><w:rPr><w:vanish/></w:rPr>'
             "<w:t> </w:t></w:r></w:p>")
    word = arquivo_word.ler(_word(tmp_path, corpo))
    assert (word.texto, word.texto_oculto) == ("Texto.", False)


def test_trecho_marcado_como_nao_oculto_continua(tmp_path):
    corpo = ('<w:p><w:r><w:rPr><w:vanish w:val="false"/></w:rPr>'
             "<w:t>Aparece.</w:t></w:r></w:p>")
    word = arquivo_word.ler(_word(tmp_path, corpo))
    assert (word.texto, word.texto_oculto) == ("Aparece.", False)


def test_comentarios_contados_e_fora_do_texto(tmp_path):
    caminho = _word_com_pecas(
        tmp_path, _p("Texto.") + '<w:p><w:r><w:commentReference w:id="0"/></w:r></w:p>',
        {"word/comments.xml": (f"<w:comments {ESPACOS}>"
                               f'<w:comment w:id="0">{_p("CPF 111.111.111-11")}</w:comment>'
                               f'<w:comment w:id="1">{_p("Outro.")}</w:comment></w:comments>')})
    word = arquivo_word.ler(caminho)
    assert (word.texto, word.comentarios) == ("Texto.", 2)


def test_alteracao_controlada_e_avisada_e_sai_aceita(tmp_path):
    corpo = ("<w:p><w:r><w:t>Antes </w:t></w:r>"
             "<w:moveFrom><w:r><w:t>saiu daqui </w:t></w:r></w:moveFrom>"
             "<w:moveTo><w:r><w:t>chegou aqui</w:t></w:r></w:moveTo></w:p>")
    word = arquivo_word.ler(_word(tmp_path, corpo))
    assert (word.texto, word.alteracoes) == ("Antes chegou aqui", True)


def test_documento_sem_nada_de_fora(tmp_path):
    word = arquivo_word.ler(_word(tmp_path, _p("Só texto.")))
    assert word == arquivo_word.DocumentoDoWord("Só texto.")


def test_linha_de_tabela_apagada_nao_sai(tmp_path):
    apagada = ('<w:tr><w:trPr><w:del w:id="1"/></w:trPr>'
               + _tc("<w:p><w:del><w:r><w:delText>Caio</w:delText></w:r></w:del></w:p>")
               + _tc("x") + "</w:tr>")
    corpo = _tbl([_tc("Nome"), _tc("Valor")], [_tc("Ana"), _tc("1")])
    corpo = corpo.replace("</w:tbl>", apagada + "</w:tbl>")
    linhas = _texto(_word(tmp_path, corpo)).splitlines()
    assert len(linhas) == 3
    assert "x" not in linhas[-1]


def test_campo_entra_com_o_que_mostra_e_nao_a_formula(tmp_path):
    corpo = ('<w:p><w:r><w:t xml:space="preserve">Página </w:t></w:r>'
             '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
             "<w:r><w:instrText> PAGE </w:instrText></w:r>"
             '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
             "<w:r><w:t>4</w:t></w:r>"
             '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'
             '<w:p><w:fldSimple w:instr=" DATE "><w:r><w:t>30/09/2026</w:t></w:r>'
             "</w:fldSimple></w:p>")
    assert _texto(_word(tmp_path, corpo)) == "Página 4\n\n30/09/2026"


def test_do_link_vai_so_o_texto(tmp_path):
    corpo = ('<w:p><w:hyperlink r:id="x"><w:r><w:t>sistema</w:t></w:r>'
             "</w:hyperlink></w:p>")
    caminho = _word_com_pecas(tmp_path, corpo, {}, [
        ("x", "hyperlink", "https://exemplo.invalid/ficha?cpf=11111111111",
         ' TargetMode="External"')])
    assert _texto(caminho) == "sistema"


# ------------------------------- as imagens e os Words que não abrem (etapa 5)

A = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'


def _foto(descricao="foto"):
    return (f'<w:r><w:drawing><wp:docPr descr="{descricao}"/><a:blip {A} r:embed="x"/>'
            "</w:drawing></w:r>")


def test_imagens_contadas_e_a_descricao_escondida_nao_vai(tmp_path):
    corpo = (f"<w:p><w:r><w:t>Com foto.</w:t></w:r>{_foto('Assinatura, CPF 111.111.111-11')}</w:p>"
             # a imagem do jeito antigo, um objeto colado (planilha) e um gráfico
             f'<w:p><w:r><w:pict><v:shape {VML}><v:imagedata/></v:shape></w:pict></w:r></w:p>'
             "<w:p><w:r><w:object/></w:r></w:p>"
             f'<w:p><w:r><w:drawing><c:chart xmlns:c="urn:grafico"/></w:drawing></w:r></w:p>')
    corpo = corpo.replace("<wp:docPr", '<wp:docPr xmlns:wp="urn:wp"').replace(
        'r:embed="x"', 'xmlns:r="urn:r" r:embed="x"')
    word = arquivo_word.ler(_word(tmp_path, corpo))
    assert (word.texto, word.imagens) == ("Com foto.", 4)


def test_caixa_de_texto_nao_e_imagem_e_a_dupla_conta_uma_vez(tmp_path):
    corpo = (f"<w:p><w:r><w:t>Texto.</w:t></w:r><w:r>{_caixa('Na caixa.')}</w:r></w:p>"
             f"<w:p><w:r><w:t>Foto:</w:t></w:r><w:r><mc:AlternateContent {MC}>"
             f"<mc:Choice><w:drawing><a:blip {A}/></w:drawing></mc:Choice>"
             f"<mc:Fallback><w:pict><v:shape {VML}><v:imagedata/></v:shape></w:pict>"
             "</mc:Fallback></mc:AlternateContent></w:r></w:p>")
    word = arquivo_word.ler(_word(tmp_path, corpo))
    assert word.imagens == 1


def test_o_logotipo_do_cabecalho_repetido_conta_uma_vez(tmp_path):
    cabecalho = (f"<w:hdr {ESPACOS}><w:p><w:r><w:t>Topo</w:t></w:r>"
                 f"<w:r><w:drawing><a:blip {A}/></w:drawing></w:r></w:p></w:hdr>")
    quebra = "<w:p><w:pPr>{}</w:pPr></w:p>"
    corpo = (_p("Parte 1") + quebra.format(_secao(("header", "default", "c1")))
             + _p("Parte 2") + _secao(("header", "default", "c1")))
    caminho = _word_com_pecas(tmp_path, corpo, {"word/header1.xml": cabecalho},
                              [("c1", "header", "header1.xml", "")])
    assert arquivo_word.ler(caminho).imagens == 1


def test_imagem_dentro_de_nota_conta_uma_vez(tmp_path):
    """O corpo é lido duas vezes por causa das notas; a imagem, contada uma."""
    corpo = (f"<w:p><w:r><w:t>Texto</w:t></w:r>{_chama('footnote', 1)}</w:p>"
             f"<w:p><w:r><w:drawing><a:blip {A}/></w:drawing></w:r></w:p>")
    caminho = _word_com_pecas(tmp_path, corpo, {
        "word/footnotes.xml": _notas("footnote", (1, "Nota."))})
    assert arquivo_word.ler(caminho).imagens == 1


@pytest.mark.parametrize("nome, trecho_da_frase", [
    ("19-nao-e-word.docx", "estragado"),
    ("21-word-so-com-imagens.docx", "não tem texto, só imagens. Salve-o como PDF"),
    ("22-word-protegido.docx", "está protegido por senha"),
    ("23-doc-antigo-renomeado.docx", "documento do Word antigo (.doc)"),
    ("24-word-vazio.docx", "está vazio: não há texto nele"),
    ("25-word-grande-demais.docx", "grande demais para o programa abrir com segurança"),
])
def test_cada_word_que_nao_abre_tem_a_sua_frase(nome, trecho_da_frase):
    """RN-30: cada um volta à escolha com a frase dele, e o nome no começo."""
    with pytest.raises(ArquivoNaoServe) as erro:
        arquivo_word.ler(MASSA / nome)
    assert str(erro.value).startswith(f"O {nome} ")
    assert trecho_da_frase in str(erro.value)


def test_o_grande_demais_e_recusado_sem_descompactar(tmp_path, monkeypatch):
    """O limite é conferido pelo tamanho que cada peça declara: nenhuma peça é
    aberta antes disso."""
    import zipfile as zf
    abertas = []
    original = zf.ZipFile.read
    monkeypatch.setattr(zf.ZipFile, "read",
                        lambda self, nome, *a: abertas.append(nome) or original(self, nome, *a))
    with pytest.raises(ArquivoNaoServe):
        arquivo_word.ler(MASSA / "25-word-grande-demais.docx")
    assert abertas == []


def test_escaneado_com_timbre_e_numero_de_pagina_e_so_imagens(tmp_path):
    """Regressão da lente crítica da etapa 5: com texto só no cabeçalho e no
    rodapé, a revisão abria quase vazia em vez de mandar pelo caminho do PDF."""
    corpo = (f"<w:p><w:r><w:drawing><a:blip {A}/></w:drawing></w:r></w:p>"
             + _secao(("header", "default", "c1"), ("footer", "default", "r1")))
    caminho = _word_com_pecas(
        tmp_path, corpo,
        {"word/header1.xml": _borda("hdr", "Fundação Exemplo"),
         "word/footer1.xml": _borda("ftr", "Página 1 de 3")},
        [("c1", "header", "header1.xml", ""), ("r1", "footer", "footer1.xml", "")])
    with pytest.raises(ArquivoNaoServe) as erro:
        arquivo_word.ler(caminho)
    assert "só imagens" in str(erro.value)


def test_corpo_sem_texto_e_sem_imagem_com_logotipo_no_cabecalho_e_vazio(tmp_path):
    cabecalho = f"<w:hdr {ESPACOS}><w:p><w:r><w:drawing><a:blip {A}/></w:drawing></w:r></w:p></w:hdr>"
    caminho = _word_com_pecas(
        tmp_path, "<w:p/>" + _secao(("header", "default", "c1")),
        {"word/header1.xml": cabecalho}, [("c1", "header", "header1.xml", "")])
    with pytest.raises(ArquivoNaoServe) as erro:
        arquivo_word.ler(caminho)
    assert "está vazio" in str(erro.value)


def test_imagem_dentro_de_caixa_de_texto_conta_uma_vez(tmp_path):
    """Regressão da lente crítica da etapa 5: a foto dentro da caixa era
    contada pela caixa e de novo pelo miolo dela."""
    miolo = f"<w:p><w:r><w:drawing><a:blip {A}/></w:drawing></w:r></w:p>"
    caixa = (f"<w:pict><v:shape {VML}><v:textbox><w:txbxContent>{_p('Legenda.')}{miolo}"
             "</w:txbxContent></v:textbox></v:shape></w:pict>")
    corpo = f"<w:p><w:r><w:t>Texto.</w:t></w:r><w:r>{caixa}</w:r></w:p>"
    word = arquivo_word.ler(_word(tmp_path, corpo))
    assert (word.imagens, word.texto) == (1, "Texto.\n\nLegenda.")


def test_peca_de_nome_estranho_tambem_soma_no_limite(tmp_path, monkeypatch):
    """Regressão da lente crítica da etapa 5: a ligação do cabeçalho podia
    levar a uma peça que não termina em .xml, e o limite não a contava."""
    monkeypatch.setattr(arquivo_word, "LIMITE_DO_TEXTO", 5_000)
    corpo = _p("Corpo") + _secao(("header", "default", "c1"))
    caminho = _word_com_pecas(
        tmp_path, corpo,
        {"word/cabecalho.bin": f"<w:hdr {ESPACOS}>{_p('x' * 10_000)}</w:hdr>"},
        [("c1", "header", "cabecalho.bin", "")])
    with pytest.raises(ArquivoNaoServe) as erro:
        arquivo_word.ler(caminho)
    assert "grande demais" in str(erro.value)


def test_cabecalho_copiado_com_o_logotipo_conta_uma_vez(tmp_path):
    """Regressão da lente crítica da etapa 5: ao desligar "Vincular ao
    anterior", o Word copia o cabeçalho para outra peça, igual."""
    cabecalho = (f"<w:hdr {ESPACOS}><w:p><w:r><w:t>Topo</w:t></w:r>"
                 f"<w:r><w:drawing><a:blip {A}/></w:drawing></w:r></w:p></w:hdr>")
    quebra = "<w:p><w:pPr>{}</w:pPr></w:p>"
    corpo = (_p("Parte 1") + quebra.format(_secao(("header", "default", "c1")))
             + _p("Parte 2") + _secao(("header", "default", "c2")))
    caminho = _word_com_pecas(
        tmp_path, corpo,
        {"word/header1.xml": cabecalho, "word/header2.xml": cabecalho},
        [("c1", "header", "header1.xml", ""), ("c2", "header", "header2.xml", "")])
    word = arquivo_word.ler(caminho)
    assert (word.imagens, word.texto) == (1, "Topo\n\nParte 1\n\nParte 2")


def test_o_limite_vale_para_o_texto_e_nao_para_as_imagens(tmp_path):
    caminho = tmp_path / "foto-grande.docx"
    with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as pacote:
        pacote.writestr("word/document.xml",
                        f"<w:document {ESPACOS}><w:body>{_p('Texto.')}</w:body></w:document>")
        pacote.writestr("word/media/foto.png", bytes(arquivo_word.LIMITE_DO_TEXTO + 1))
    assert _texto(caminho) == "Texto."


def test_o_endereco_de_um_link_nunca_vira_peca_lida(tmp_path):
    """Ligação para fora (um link) não é peça do pacote: nem é procurada."""
    corpo = _p("Corpo") + _secao(("header", "default", "x"))
    caminho = _word_com_pecas(tmp_path, corpo, {}, [
        ("x", "hyperlink", "http://exemplo.invalid/cpf", ' TargetMode="External"')])
    assert _texto(caminho) == "Corpo"

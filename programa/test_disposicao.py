"""Testes da remontagem do texto pela posição das palavras na página.

O que estes testes guardam é a regra RN-10: o que era tabela no documento sai
como tabela de texto, com as colunas separadas — nos dois caminhos, o do PDF e
o do OCR.
"""
from pathlib import Path

import disposicao
import documento
import leitura

MASSA = Path(__file__).parent.parent / "dados-exemplo"


def _coluna_de(linha, pedaco):
    """Em que coluna do texto aquele pedaço começa."""
    return linha.index(pedaco)


def _linhas_da_tabela(texto):
    return {
        linha.split()[0]: linha
        for linha in texto.splitlines()
        if linha.strip() and linha.split()[0] in {"Item", "1", "2", "3", "4"}
    }


def test_a_tabela_do_pdf_sai_com_as_colunas_alinhadas():
    """Critério de aceite da spec 002, pelo caminho da camada de texto."""
    paginas = documento.texto_da_camada(MASSA / "01-com-texto-e-tabela.pdf")

    linhas = _linhas_da_tabela(paginas[2])
    assert set(linhas) == {"Item", "1", "2", "3", "4"}, "não achei a tabela inteira"

    # A coluna dos valores tem que ser a mesma em todas as linhas.
    colunas = {
        _coluna_de(linhas["Item"], "Valor"),
        _coluna_de(linhas["1"], "3.480,00"),
        _coluna_de(linhas["2"], "6.120,50"),
        _coluna_de(linhas["3"], "9.240,00"),
        _coluna_de(linhas["4"], "15.000,00"),
    }
    assert len(colunas) == 1, (
        f"a coluna dos valores mudou de lugar entre as linhas: {sorted(colunas)}"
    )


def test_a_tabela_do_ocr_sai_com_as_colunas_alinhadas():
    """O mesmo critério, agora pelo caminho que lê a imagem.

    Este é o caso que importa de verdade: documento escaneado é a razão de o
    módulo existir, e é nele que a tabela costuma virar uma coisa por linha.
    """
    # Só a página da tabela, e não o documento inteiro: ler as doze levaria
    # dezoito segundos para olhar uma, e lista de testes lenta é lista que as
    # pessoas param de rodar.
    import pymupdf

    leitura.preparar_motor()
    doc = pymupdf.open(MASSA / "02-imprimir-para-pdf.pdf")
    try:
        pagina_da_tabela = leitura._ler_pagina(doc[11])
    finally:
        doc.close()

    linhas = _linhas_da_tabela(pagina_da_tabela)
    assert set(linhas) == {"Item", "1", "2", "3", "4"}, "não achei a tabela inteira"

    colunas = {
        _coluna_de(linhas["Item"], "Quantidade"),
        _coluna_de(linhas["1"], "12"),
        _coluna_de(linhas["2"], "4"),
        _coluna_de(linhas["3"], "18"),
    }
    assert len(colunas) == 1, (
        f"a coluna da quantidade mudou de lugar entre as linhas: {sorted(colunas)}"
    )


def test_o_texto_corrido_nao_ganha_espacos_a_mais():
    """Teste de regressão de um defeito que apareceu construindo esta etapa.

    A primeira tentativa punha cada palavra na coluna exata em que ela estava, e
    o título em maiúsculas saía esparramado — "UNIVERSIDADE   FEDERAL   DE" —,
    porque maiúscula é mais larga que a média das letras.
    """
    paginas = documento.texto_da_camada(MASSA / "01-com-texto-e-tabela.pdf")
    primeira = paginas[0].splitlines()[0]

    assert primeira == "UNIVERSIDADE FEDERAL DE SANTA CATARINA"


def test_vao_pequeno_vira_um_espaco_e_vao_grande_vira_coluna():
    """A regra que separa uma frase de uma tabela, conferida sozinha.

    As posições aqui são inventadas, em qualquer unidade: o que o teste mede é a
    decisão, e não o documento.
    """
    # "ab cd" colados como frase, e "ef" lá longe, noutra coluna.
    linha = [(0, 20, "ab"), (24, 44, "cd"), (200, 220, "ef")]

    montada = disposicao.montar([linha])[0]

    assert montada.startswith("ab cd"), "as duas primeiras deviam ler como frase"
    assert "   " in montada, "a terceira devia ter pulado para outra coluna"
    assert montada.endswith("ef")


def test_palavras_na_mesma_altura_viram_uma_linha_so():
    """A célula de uma tabela costuma ser gravada como um texto separado.

    Confiar no que o PDF chama de "linha" devolveria uma célula por linha, que é
    exatamente o problema que esta etapa resolve. Quem diz que elas são a mesma
    linha é a altura.
    """
    # (x inicial, y do topo, x final, y da base, texto)
    palavras = [
        (10, 100, 30, 110, "Item"),
        (80, 100, 160, 110, "Descricao"),
        (300, 100, 330, 110, "Valor"),
        (10, 115, 20, 125, "1"),
        (80, 115, 200, 125, "Material"),
    ]

    linhas = disposicao.agrupar_por_altura(palavras)

    assert len(linhas) == 2, f"deviam ser duas linhas, vieram {len(linhas)}"
    assert [p[2] for p in linhas[0]] == ["Item", "Descricao", "Valor"]
    assert [p[2] for p in linhas[1]] == ["1", "Material"]


def test_pagina_sem_palavra_nenhuma_nao_estoura():
    assert disposicao.montar([]) == []
    assert disposicao.agrupar_por_altura([]) == []


def test_carimbo_lateral_nao_embaralha_o_corpo():
    """Teste de regressão do defeito mais grave achado na etapa 5.

    Um documento com o número do processo carimbado de lado na margem — o
    formato que sai de sistema de processos — fazia o programa fundir e
    intercalar as linhas do corpo: "Primeira Segunda linha linha do do corpo
    corpo". A causa era medir a entrelinha pelos vãos entre as alturas da
    página, e o carimbo espalha alturas.
    """
    paginas = documento.texto_da_camada(MASSA / "07-carimbo-lateral.pdf")
    linhas = [l.strip() for l in paginas[0].splitlines() if l.strip()]

    assert "UNIVERSIDADE FEDERAL DE SANTA CATARINA" in linhas
    assert "Pagina 1 de 2" in linhas
    assert any(l.startswith("Trata-se de prestacao de contas") for l in linhas), (
        "o corpo do documento saiu embaralhado"
    )


def test_o_carimbo_nao_se_perde():
    """O conteúdo da margem não pode sumir, mesmo saindo fora de ordem.

    Limitação conhecida em 11/09/2026: o carimbo de lado é preservado, mas as
    palavras dele saem na ordem trocada. Perder o número do processo seria pior
    que mostrá-lo fora de ordem, e a conferência na tela deixa a pessoa arrumar.
    """
    texto = documento.texto_da_camada(MASSA / "07-carimbo-lateral.pdf")[0]

    assert "PROCESSO" in texto
    assert "23080.012345/2026-77" in texto


def test_a_linha_em_branco_entre_blocos_sobrevive_no_pdf():
    """Teste de regressão do segundo defeito achado na etapa 5.

    O arquivo que sai é `.md`, e nesse formato linhas seguidas sem uma linha
    vazia entre elas viram um parágrafo só. Sem a separação, o cabeçalho chegava
    colado ao corpo dentro da conversa com o assistente.
    """
    pagina = documento.texto_da_camada(MASSA / "01-com-texto-e-tabela.pdf")[0]

    assert "\n\n" in pagina, "os blocos do documento saíram todos colados"


def test_a_linha_em_branco_entre_blocos_sobrevive_no_ocr():
    """O mesmo, pelo caminho que lê a imagem."""
    import pymupdf

    leitura.preparar_motor()
    doc = pymupdf.open(MASSA / "02-imprimir-para-pdf.pdf")
    try:
        pagina = leitura._ler_pagina(doc[0])
    finally:
        doc.close()

    assert "\n\n" in pagina, "os blocos do documento saíram todos colados"

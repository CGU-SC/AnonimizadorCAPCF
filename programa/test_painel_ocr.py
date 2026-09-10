"""Testes do painel do "Gerar OCR".

Estes testes não substituem olhar a tela - eles pegam a classe de defeito que
olhar a tela pega tarde demais: a frase que não coube e saiu cortada. Foi
exatamente o que aconteceu na conferência da etapa 1, em 10/09/2026.
"""
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

import painel_ocr


@pytest.fixture(scope="module")
def aplicacao():
    """O Qt precisa estar de pé para qualquer tela existir, mesmo sem aparecer."""
    return QApplication.instance() or QApplication([])


def test_a_caixa_de_erro_cabe_a_frase_inteira(aplicacao):
    """Teste de regressão do defeito achado na conferência da etapa 1.

    A caixa vinha com altura de uma linha só, e o fim da explicação sumia para
    fora da borda. Quem lia via meia frase sem nenhum sinal de que faltava
    pedaço.
    """
    tela = painel_ocr._TelaErro(ao_escolher_outro=lambda: None)

    # A frase mais longa que o programa consegue mostrar hoje.
    motivo = (
        "O arquivo não pôde ser aberto. Ele pode estar danificado ou não ser "
        "um PDF, apesar do nome."
    )
    tela.mostrar(Path("05-corrompido.pdf"), motivo)

    altura_reservada = tela.explicacao.minimumHeight()
    altura_necessaria = tela.explicacao.heightForWidth(tela.LARGURA_DO_TEXTO)

    assert altura_reservada >= altura_necessaria, (
        "a caixa de erro reservou menos altura do que a frase precisa - "
        "o texto vai sair cortado na tela"
    )
    # Uma linha só seria o defeito de volta: esta frase ocupa várias.
    assert altura_reservada > 20


def test_o_numero_de_letras_sai_escrito_em_portugues(aplicacao):
    """Teste de regressão do defeito achado pela lente crítica.

    A linha saía como "sim. 1720 letras": o ponto tinha comido a vírgula da
    frase, e o separador de milhar nunca aparecia. É a linha que a pessoa lê
    para decidir se aproveita o texto do documento.
    """
    import documento

    tela = painel_ocr._TelaFicha(ao_escolher_outro=lambda: None)
    massa = Path(__file__).parent.parent / "dados-exemplo"
    ficha = documento.conferir(massa / "01-com-texto-e-tabela.pdf")

    tela.mostrar(ficha)

    # 1.472 é o que este documento inventado tem de letras, sem contar espaço
    # nem quebra de linha. O número está fixo aqui de propósito: se um dia ele
    # mudar sem ninguém ter mexido na massa, alguma coisa mudou na contagem.
    assert tela.linha_texto.valor.text() == "sim, 1.472 letras"


def test_separador_de_milhar_nao_depende_da_maquina():
    """O mesmo número, escrito do mesmo jeito em qualquer Windows."""
    assert painel_ocr._com_separador_de_milhar(7) == "7"
    assert painel_ocr._com_separador_de_milhar(999) == "999"
    assert painel_ocr._com_separador_de_milhar(1720) == "1.720"
    assert painel_ocr._com_separador_de_milhar(1234567) == "1.234.567"


def test_falha_inesperada_nao_deixa_o_painel_preso(aplicacao, monkeypatch):
    """Teste de regressão do defeito mais grave achado pela lente crítica.

    A tela de espera não tem botão nenhum. Se a leitura estourasse por um
    motivo não previsto, o painel ficava preso nela para sempre - e nem sair
    pelo menu resolvia. Toda tela do programa precisa ter saída.
    """
    painel = painel_ocr.PainelOcr()

    def estourar(_caminho):
        raise ValueError("defeito que ninguém previu")

    monkeypatch.setattr(painel_ocr, "conferir", estourar)
    painel._conferir(Path("qualquer-documento.pdf"))

    assert painel.telas.currentWidget() is painel.tela_erro, (
        "o painel ficou preso na tela de espera, que não tem como sair"
    )


def test_toda_mensagem_de_erro_do_programa_cabe_na_caixa(aplicacao):
    """Vale para as quatro frases que o programa sabe mostrar, não só uma."""
    import documento

    tela = painel_ocr._TelaErro(ao_escolher_outro=lambda: None)
    massa = Path(__file__).parent.parent / "dados-exemplo"

    for nome in ["05-corrompido.pdf", "06-protegido-por-senha.pdf",
                 "nao-existe.pdf"]:
        try:
            documento.conferir(massa / nome)
        except documento.DocumentoNaoAbre as problema:
            tela.mostrar(Path(nome), str(problema))
            assert tela.explicacao.minimumHeight() >= tela.explicacao.heightForWidth(
                tela.LARGURA_DO_TEXTO
            ), f"a frase de erro de {nome} não cabe na caixa"
        else:
            pytest.fail(f"{nome} deveria ter dado erro e não deu")

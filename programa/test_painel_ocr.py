"""Testes do painel do "Gerar OCR".

Estes testes não substituem olhar a tela - eles pegam a classe de defeito que
olhar a tela pega tarde demais: a frase que não coube e saiu cortada. Foi
exatamente o que aconteceu na conferência da etapa 1, em 10/09/2026.
"""
from pathlib import Path

import pytest
import painel_ocr


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

    tela = painel_ocr._TelaFicha(
        ao_escolher_outro=lambda: None, ao_ler=lambda _ficha: None
    )
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


def test_a_barra_anda_mesmo_num_documento_de_uma_pagina_so(aplicacao):
    """Teste de regressão do defeito achado pela lente crítica na etapa 2.

    A barra contava só as páginas terminadas. Num documento de uma página só
    ela ficava em zero do começo ao fim da leitura, e barra parada é lida como
    programa travado.
    """
    import documento

    tela = painel_ocr._TelaLendo(ao_cancelar=lambda: None)
    massa = Path(__file__).parent.parent / "dados-exemplo"

    tela.comecar(documento.conferir(massa / "03-conteudo-girado.pdf"))
    tela.avancar(1, 1)
    assert tela.barra.value() == tela.barra.maximum(), (
        "num documento de uma página a barra não saiu do lugar"
    )

    tela.comecar(documento.conferir(massa / "02-imprimir-para-pdf.pdf"))
    tela.avancar(7, 12)
    # 7 de 12 é o que o rascunho aprovado mostra nessa página.
    assert tela.barra.value() == 7
    assert tela.barra.maximum() == 12


def test_sem_motor_de_leitura_nao_aparece_tentar_de_novo(aplicacao):
    """Teste de regressão: botão que nunca pode dar certo não deve existir.

    Falhar numa página pode ser passageiro. Faltar o motor de leitura não é -
    só instalando resolve -, e oferecer "tentar de novo" ali gasta o tempo de
    quem usa e ainda esconde a causa real.
    """
    painel = painel_ocr.PainelOcr()
    # O aviso carrega quem o mandou, para leitura abandonada não sequestrar a
    # tela; aqui a leitura de mentira faz esse papel.
    leitura = painel_ocr.LeituraEmSegundoPlano(Path("qualquer.pdf"))
    painel.leitura = leitura

    painel._leitura_falhou(leitura, 7, "Alguma coisa deu errado ao ler esta página.")
    assert not painel.tela_erro.botao_tentar.isHidden(), (
        "falha numa página pode ser tentada de novo, e o botão sumiu"
    )

    painel.leitura = leitura
    painel._leitura_falhou(leitura, 0, "O motor de leitura não foi encontrado.")
    assert painel.tela_erro.botao_tentar.isHidden(), (
        "sem motor instalado, tentar de novo vai falhar igual - o botão não "
        "pode aparecer"
    )


def test_fechar_no_meio_da_leitura_para_a_leitura_antes(aplicacao):
    """Teste de regressão do defeito mais grave achado na etapa 2.

    Fechar a janela durante uma leitura fazia o programa estourar em vez de
    fechar limpo. Reproduzido em 10/09/2026: o programa terminava com código de
    erro. Agora ele pede para a leitura parar e espera a página em curso.
    """
    import documento

    painel = painel_ocr.PainelOcr()
    massa = Path(__file__).parent.parent / "dados-exemplo"
    painel.comecar_a_ler(documento.conferir(massa / "02-imprimir-para-pdf.pdf"))

    leitura = painel.leitura
    assert leitura.isRunning(), "a leitura nem chegou a começar"

    painel.encerrar()

    assert not leitura.isRunning(), (
        "a leitura continuou rodando depois de o programa mandar encerrar - "
        "é isso que faz o programa estourar ao fechar"
    )


def test_escolher_outro_documento_para_a_leitura_em_andamento(aplicacao):
    """Teste de regressão do defeito mais grave achado na etapa 3.

    Escolher outro documento no meio de uma leitura deixava três coisas
    erradas: a máquina seguia trabalhando num documento abandonado; o aviso de
    leitura terminada chegava depois e levava a tela para a conferência do
    documento antigo; e começar outra leitura por cima derrubava o programa.
    """
    import documento

    painel = painel_ocr.PainelOcr()
    massa = Path(__file__).parent.parent / "dados-exemplo"
    painel.comecar_a_ler(documento.conferir(massa / "02-imprimir-para-pdf.pdf"))
    abandonada = painel.leitura
    assert abandonada.isRunning()

    painel.receber_documento(massa / "01-com-texto-e-tabela.pdf")

    assert not abandonada.isRunning(), (
        "a leitura antiga continuou rodando num documento que ninguém quer mais"
    )
    assert painel.leitura is None


def test_aviso_de_leitura_abandonada_nao_sequestra_a_tela(aplicacao):
    """O aviso que chega atrasado não pode trocar a tela por conta própria.

    Uma leitura abandonada termina o que estava fazendo e avisa depois. Se esse
    aviso valesse, a pessoa estaria olhando um documento e o programa a levaria
    para outro, sem ela ter pedido nada.
    """
    import documento

    painel = painel_ocr.PainelOcr()
    massa = Path(__file__).parent.parent / "dados-exemplo"
    ficha_antiga = documento.conferir(massa / "02-imprimir-para-pdf.pdf")
    abandonada = painel_ocr.LeituraEmSegundoPlano(ficha_antiga.caminho)

    # O programa já está em outro documento: esta leitura não é mais a de agora.
    painel.leitura = None
    tela_antes = painel.telas.currentWidget()

    painel._leitura_terminou(abandonada, ficha_antiga, ["texto velho"])

    assert painel.telas.currentWidget() is tela_antes, (
        "o aviso de uma leitura abandonada trocou a tela"
    )

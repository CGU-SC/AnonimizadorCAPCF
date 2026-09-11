"""Testes da tela que decide o que fazer com o texto já gravado no PDF.

O que estes testes guardam é a regra RN-4: o programa não julga se o texto
presta. Ele mostra as primeiras linhas e a escolha é da pessoa — porque palpite
errado aqui produz um arquivo de lixo que ninguém percebe.
"""
from pathlib import Path

import documento
import painel_ocr
import tela_conferencia
import tela_decisao

MASSA = Path(__file__).parent.parent / "dados-exemplo"


def _tela(escolhas):
    return tela_decisao.TelaDecisao(
        ao_aproveitar=lambda ficha, paginas: escolhas.append(("aproveitar", paginas)),
        ao_ignorar=lambda ficha: escolhas.append(("ignorar", None)),
        ao_escolher_outro=lambda: escolhas.append(("outro", None)),
    )


def test_mostra_as_primeiras_linhas_do_texto_que_ja_existe(aplicacao):
    escolhas = []
    tela = _tela(escolhas)
    ficha = documento.conferir(MASSA / "01-com-texto-e-tabela.pdf")

    tela.mostrar(ficha, documento.texto_da_camada(ficha.caminho))

    amostra = tela.amostra.toPlainText()
    assert amostra.startswith("UNIVERSIDADE FEDERAL DE SANTA CATARINA")
    assert "3 páginas, 1.472 letras" in tela.legenda.text()


def test_mostra_o_lixo_quando_o_texto_e_lixo(aplicacao):
    """O caso que dá sentido a esta tela inteira.

    Este documento já passou por um OCR ruim antes: tem texto por dentro, e esse
    texto não quer dizer nada. O programa precisa mostrá-lo como está, para a
    pessoa ver num olhar e mandar reler.
    """
    escolhas = []
    tela = _tela(escolhas)
    ficha = documento.conferir(MASSA / "04-texto-embaralhado.pdf")

    tela.mostrar(ficha, documento.texto_da_camada(ficha.caminho))

    amostra = tela.amostra.toPlainText()
    assert amostra.strip(), "a amostra veio vazia - não dá para decidir sobre nada"
    assert "UNIVERSIDADE" not in amostra, "isto deveria ser lixo, e veio texto"


def test_a_amostra_nao_traz_linhas_vazias(aplicacao):
    """PDF devolve páginas cheias de linha em branco; amostra em branco não decide nada."""
    escolhas = []
    tela = _tela(escolhas)
    ficha = documento.conferir(MASSA / "01-com-texto-e-tabela.pdf")

    tela.mostrar(ficha, ["", "   ", "\n\n", "a primeira linha de verdade", ""])

    assert tela.amostra.toPlainText() == "a primeira linha de verdade"


def test_o_botao_de_ignorar_diz_quanto_tempo_vai_levar(aplicacao):
    """A escolha não pode ser feita no escuro.

    Ignorar um documento de cem páginas custa dois minutos e meio, e é justo
    saber disso antes de clicar.
    """
    escolhas = []
    tela = _tela(escolhas)

    ficha = documento.conferir(MASSA / "01-com-texto-e-tabela.pdf")
    tela.mostrar(ficha, documento.texto_da_camada(ficha.caminho))
    assert "segundos" in tela.porque_ignorar.text()

    from leitura import tempo_estimado
    assert tempo_estimado(1) == "uns 2 segundos"
    assert tempo_estimado(12) == "uns 18 segundos"
    assert tempo_estimado(40) == "cerca de 1 minuto"
    # 100 páginas dão 2 minutos e meio, e a metade arredonda para cima: quem
    # decide esperar prefere descobrir que terminou antes do previsto.
    assert tempo_estimado(100) == "cerca de 3 minutos"


def test_as_duas_escolhas_levam_a_caminhos_diferentes(aplicacao):
    escolhas = []
    tela = _tela(escolhas)
    ficha = documento.conferir(MASSA / "01-com-texto-e-tabela.pdf")
    paginas = documento.texto_da_camada(ficha.caminho)
    tela.mostrar(ficha, paginas)

    tela.botao_aproveitar.click()
    assert escolhas[-1][0] == "aproveitar"
    assert escolhas[-1][1] == paginas, "aproveitar tem que levar o texto que estava lá"

    tela.botao_ignorar.click()
    assert escolhas[-1][0] == "ignorar"


def test_documento_com_texto_vai_para_a_decisao_e_nao_direto_para_a_leitura(aplicacao):
    painel = painel_ocr.PainelOcr()

    painel.seguir_a_partir_da_ficha(
        documento.conferir(MASSA / "01-com-texto-e-tabela.pdf")
    )

    assert painel.telas.currentWidget() is painel.tela_decisao
    assert painel.leitura is None, "não pode ter começado a ler nada"


def test_aproveitar_leva_direto_para_a_conferencia_com_o_selo_certo(aplicacao):
    """Regra RN-12: a conferência acontece nos dois caminhos, e não tem como ser
    pulada. O que muda é o selo, que diz de onde o texto veio."""
    painel = painel_ocr.PainelOcr()
    ficha = documento.conferir(MASSA / "01-com-texto-e-tabela.pdf")
    paginas = documento.texto_da_camada(ficha.caminho)

    painel.aproveitar_o_texto_existente(ficha, paginas)

    assert painel.telas.currentWidget() is painel.tela_conferencia
    assert painel.tela_conferencia.selo.text() == "VEIO DO PRÓPRIO PDF"
    assert painel.tela_conferencia.texto_conferido() == paginas


def test_ignorar_manda_ler_as_imagens_e_o_texto_e_o_do_ocr(aplicacao):
    """Critério de aceite da spec 002.

    "Dado que a pessoa escolheu ignorar e ler as imagens, quando a leitura
    termina, então o texto exibido na conferência é o do OCR, e não o da camada
    original."
    """
    painel = painel_ocr.PainelOcr()
    ficha = documento.conferir(MASSA / "04-texto-embaralhado.pdf")
    lixo = documento.texto_da_camada(ficha.caminho)

    painel.comecar_a_ler(ficha)
    leitura = painel.leitura
    leitura.wait(60_000)
    aplicacao.processEvents()

    assert painel.telas.currentWidget() is painel.tela_conferencia
    assert painel.tela_conferencia.selo.text() == "VEIO DO OCR"
    assert painel.tela_conferencia.texto_conferido() != lixo, (
        "a conferência ficou com o texto embaralhado do PDF, e não com o do OCR"
    )


def test_sem_o_motor_instalado_o_pdf_com_texto_continua_funcionando(
    aplicacao, monkeypatch
):
    """Critério de aceite da spec 002, e a razão de o aviso do motor não bloquear.

    "Dado que o Tesseract não está instalado, quando a pessoa escolhe um PDF que
    tem camada de texto, então o caminho segue normalmente até a conferência."

    Numa máquina do núcleo onde o motor não foi instalado, metade do módulo
    ainda serve — e é só esta metade que não depende dele.
    """
    import leitura

    monkeypatch.setattr(leitura, "localizar_tesseract", lambda: None)

    painel = painel_ocr.PainelOcr()
    ficha = documento.conferir(MASSA / "01-com-texto-e-tabela.pdf")

    painel.seguir_a_partir_da_ficha(ficha)
    assert painel.telas.currentWidget() is painel.tela_decisao

    painel.aproveitar_o_texto_existente(
        ficha, documento.texto_da_camada(ficha.caminho)
    )
    assert painel.telas.currentWidget() is painel.tela_conferencia
    assert painel.tela_conferencia.selo.text() == "VEIO DO PRÓPRIO PDF"


def test_sem_o_motor_instalado_o_caminho_do_ocr_reclama(aplicacao, monkeypatch):
    """O outro lado da mesma moeda: o que precisa do motor não pode ficar mudo."""
    import leitura
    import pytest

    monkeypatch.setattr(leitura, "localizar_tesseract", lambda: None)

    with pytest.raises(leitura.MotorNaoEncontrado):
        leitura.preparar_motor()

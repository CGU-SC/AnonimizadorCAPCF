"""As perguntas antes de reabrir (emenda de 05/11/2026 da spec 001, RN-25, RN-27 e
RN-28, com o acréscimo de 06/11/2026; etapa 6 da funcionalidade 10).

Uma leitura em andamento ou um texto lido e ainda não salvo, em qualquer dos dois
módulos, fazem o "Reabrir agora" perguntar antes, na própria tela do Tema.
"""
import shutil
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

import documento
import estilo
import main
from main import TAMANHO_MINIMO, JanelaPrincipal
from tela_do_tema import (
    CONTINUAR_A_LEITURA,
    LEITURA,
    NAO_DEU_PARA_REABRIR,
    NAO_REABRIR,
    REABRIR_MESMO_ASSIM,
    TEMA,
    TEXTO_NAO_SALVO,
    VALE_AO_REABRIR,
    pergunta_antes_de_reabrir,
)

MASSA = Path(__file__).parent.parent / "dados-exemplo"
PDF_COM_TEXTO = MASSA / "01-com-texto-e-tabela.pdf"


class _LeituraRodando:
    """Uma leitura que só para quando mandam parar, sem rodar motor nenhum."""

    def __init__(self):
        self.parou = False

    def isRunning(self):
        return not self.parou

    def cancelar(self):
        self.parou = True

    def wait(self, _ms):
        pass


@pytest.fixture
def pedidos(monkeypatch):
    """Troca o abrir de novo por um que só anota o tema pedido."""
    anotados = []
    monkeypatch.setattr(main, "abrir_de_novo", lambda tema: anotados.append(tema) or True)
    return anotados


@pytest.fixture
def janela(aplicacao, preferencias_isoladas):
    janela = JanelaPrincipal()
    janela.show()
    return janela


def _pedir_para_reabrir(janela):
    """Vai ao Tema, marca o claro e clica em "Reabrir agora", como a pessoa faz."""
    janela.menu.botao_config_ia.click()
    tela = janela.painel_ia.tela_tema
    tela.opcoes[estilo.CLARO].click()
    tela.aviso.botao.click()
    return tela


def _leitura_no_gerar_ocr(janela):
    leitura = _LeituraRodando()
    janela.painel_ocr.leitura = leitura
    return leitura


def _leitura_no_anonimizar(janela):
    leitura = _LeituraRodando()
    janela.painel_anonimizar.pdf.leitura = leitura
    return leitura


def _texto_no_gerar_ocr(janela, tmp_path):
    """O Gerar OCR na conferência de um PDF, com o texto ainda não salvo."""
    pdf = tmp_path / "do-ocr.pdf"
    shutil.copy(PDF_COM_TEXTO, pdf)
    ocr = janela.painel_ocr
    ficha = documento.conferir(pdf)
    ocr.ficha_atual = ficha
    ocr.aproveitar_o_texto_existente(ficha, documento.texto_da_camada(pdf))
    assert ocr.telas.currentWidget() is ocr.tela_conferencia


def _texto_no_anonimizar(janela, tmp_path):
    """Um PDF na conferência do Anonimizar, antes da revisão."""
    pdf = tmp_path / "do-anonimizar.pdf"
    shutil.copy(PDF_COM_TEXTO, pdf)
    painel = janela.painel_anonimizar
    painel.receber_arquivo(pdf)
    painel.pdf.conferir_documento(pdf)
    painel.pdf.tela_decisao.botao_aproveitar.click()
    assert painel.telas.currentWidget() is painel.pdf.tela_conferencia


def _o_que_a_pergunta_diz(tela):
    return tela.pergunta.cima.text(), tela.pergunta.baixo.text(), tela.pergunta.botao_forte.text()


# ------------------------------------------------------------ as frases da spec


def test_sem_nada_a_perder_nao_ha_pergunta():
    assert pergunta_antes_de_reabrir(None, None) is None


@pytest.mark.parametrize("no_ocr, no_anonimizar, cima, baixo, forte", [
    (LEITURA, None,
     "Há uma leitura em andamento no Gerar OCR.",
     "Reabrir agora a interrompe, e o documento precisa ser lido de novo depois.",
     CONTINUAR_A_LEITURA),
    (None, LEITURA,
     "Há uma leitura em andamento no Anonimizar.",
     "Reabrir agora a interrompe, e o documento precisa ser lido de novo depois.",
     CONTINUAR_A_LEITURA),
    (TEXTO_NAO_SALVO, None,
     "Há um texto lido e ainda não salvo no Gerar OCR.",
     "Reabrir agora o descarta, e o documento precisa ser lido de novo depois.",
     NAO_REABRIR),
    (None, TEXTO_NAO_SALVO,
     "Há um texto lido e ainda não salvo no Anonimizar.",
     "Reabrir agora o descarta, e o documento precisa ser lido de novo depois.",
     NAO_REABRIR),
    (LEITURA, LEITURA,
     "Há uma leitura em andamento no Gerar OCR e outra no Anonimizar.",
     "Reabrir agora interrompe as duas, e os documentos precisam ser lidos de novo depois.",
     CONTINUAR_A_LEITURA),
    (LEITURA, TEXTO_NAO_SALVO,
     "Há uma leitura em andamento no Gerar OCR e um texto lido e ainda não salvo no "
     "Anonimizar.",
     "Reabrir agora interrompe a leitura e descarta o texto, e os dois documentos precisam "
     "ser lidos de novo depois.",
     CONTINUAR_A_LEITURA),
    (TEXTO_NAO_SALVO, LEITURA,
     "Há um texto lido e ainda não salvo no Gerar OCR e uma leitura em andamento no "
     "Anonimizar.",
     "Reabrir agora descarta o texto e interrompe a leitura, e os dois documentos precisam "
     "ser lidos de novo depois.",
     CONTINUAR_A_LEITURA),
    (TEXTO_NAO_SALVO, TEXTO_NAO_SALVO,
     "Há um texto lido e ainda não salvo no Gerar OCR e outro no Anonimizar.",
     "Reabrir agora descarta os dois, e os documentos precisam ser lidos de novo depois.",
     NAO_REABRIR),
])
def test_cada_caso_tem_as_frases_e_o_botao_da_spec(no_ocr, no_anonimizar, cima, baixo, forte):
    assert pergunta_antes_de_reabrir(no_ocr, no_anonimizar) == (cima, baixo, forte)


# ----------------------------------------------------- uma leitura em andamento


def test_leitura_no_gerar_ocr_pergunta_na_tela_do_tema(janela, pedidos):
    _leitura_no_gerar_ocr(janela)
    tela = _pedir_para_reabrir(janela)
    assert pedidos == []
    assert janela.isVisible()
    assert not tela.pergunta.isHidden()
    assert tela.aviso.isHidden()
    assert _o_que_a_pergunta_diz(tela) == (
        "Há uma leitura em andamento no Gerar OCR.",
        "Reabrir agora a interrompe, e o documento precisa ser lido de novo depois.",
        CONTINUAR_A_LEITURA)
    assert tela.pergunta.botao_mesmo_assim.text() == REABRIR_MESMO_ASSIM
    # Na própria tela, sem caixa por cima da janela.
    assert janela.painel.currentWidget() is janela.painel_ia
    assert QApplication.activeModalWidget() is None


def test_continuar_a_leitura_devolve_a_frase_e_nao_mexe_na_leitura(janela, pedidos):
    leitura = _leitura_no_gerar_ocr(janela)
    tela = _pedir_para_reabrir(janela)
    tela.pergunta.botao_forte.click()
    assert tela.pergunta.isHidden()
    assert not tela.aviso.isHidden()
    assert tela.aviso.frase.text() == VALE_AO_REABRIR
    assert not tela.aviso.botao.isHidden()
    assert not leitura.parou
    assert janela.painel_ocr.leitura is leitura
    assert pedidos == []


def test_reabrir_mesmo_assim_para_a_leitura_e_reabre(janela, pedidos):
    leitura = _leitura_no_gerar_ocr(janela)
    tela = _pedir_para_reabrir(janela)
    tela.pergunta.botao_mesmo_assim.click()
    assert pedidos == [estilo.CLARO]
    assert not janela.isVisible()
    assert leitura.parou, "a leitura sobreviveu ao reabrir"


def test_leitura_no_anonimizar_diz_no_anonimizar(janela, pedidos):
    leitura = _leitura_no_anonimizar(janela)
    tela = _pedir_para_reabrir(janela)
    assert tela.pergunta.cima.text() == "Há uma leitura em andamento no Anonimizar."
    tela.pergunta.botao_mesmo_assim.click()
    assert pedidos == [estilo.CLARO]
    assert leitura.parou


def test_reabrir_mesmo_assim_que_falha_diz_por_que(janela, monkeypatch):
    monkeypatch.setattr(main, "abrir_de_novo", lambda tema: False)
    _leitura_no_gerar_ocr(janela)
    tela = _pedir_para_reabrir(janela)
    tela.pergunta.botao_mesmo_assim.click()
    assert janela.isVisible()
    assert tela.pergunta.isHidden()
    assert not tela.aviso.isHidden()
    assert tela.aviso.frase.text() == NAO_DEU_PARA_REABRIR
    assert tela.aviso.botao.isHidden()


# ---------------------------------------------------- um texto lido e não salvo


def test_texto_nao_salvo_no_gerar_ocr_pergunta_com_nao_reabrir(janela, pedidos, tmp_path):
    _texto_no_gerar_ocr(janela, tmp_path)
    texto_antes = janela.painel_ocr.tela_conferencia.texto_conferido()
    tela = _pedir_para_reabrir(janela)
    assert _o_que_a_pergunta_diz(tela) == (
        "Há um texto lido e ainda não salvo no Gerar OCR.",
        "Reabrir agora o descarta, e o documento precisa ser lido de novo depois.",
        NAO_REABRIR)
    tela.pergunta.botao_forte.click()
    ocr = janela.painel_ocr
    assert pedidos == []
    assert ocr.tela_conferencia.texto_conferido() == texto_antes
    assert ocr.telas.currentWidget() is ocr.tela_conferencia


def test_texto_salvo_no_gerar_ocr_reabre_sem_perguntar(janela, pedidos, tmp_path):
    _texto_no_gerar_ocr(janela, tmp_path)
    ocr = janela.painel_ocr
    ocr.tela_conferencia.botao_conferido.click()
    ocr.tentar_salvar(tmp_path / "salvo.md")
    _pedir_para_reabrir(janela)
    assert pedidos == [estilo.CLARO]


def test_pdf_na_conferencia_do_anonimizar_pergunta(janela, pedidos, tmp_path):
    _texto_no_anonimizar(janela, tmp_path)
    tela = _pedir_para_reabrir(janela)
    assert tela.pergunta.cima.text() == "Há um texto lido e ainda não salvo no Anonimizar."
    assert tela.pergunta.botao_forte.text() == NAO_REABRIR
    tela.pergunta.botao_forte.click()
    painel = janela.painel_anonimizar
    assert pedidos == []
    assert any(painel.pdf.texto_conferido())
    assert painel.telas.currentWidget() is painel.pdf.tela_conferencia


# ------------------------------------------------- mais de uma coisa a perder


def test_leitura_no_gerar_ocr_e_texto_no_anonimizar_numa_pergunta_so(janela, pedidos,
                                                                     tmp_path):
    leitura = _leitura_no_gerar_ocr(janela)
    _texto_no_anonimizar(janela, tmp_path)
    tela = _pedir_para_reabrir(janela)
    assert tela.pergunta.cima.text() == (
        "Há uma leitura em andamento no Gerar OCR e um texto lido e ainda não salvo no "
        "Anonimizar.")
    assert tela.pergunta.botao_forte.text() == CONTINUAR_A_LEITURA
    tela.pergunta.botao_forte.click()
    assert not leitura.parou
    assert any(janela.painel_anonimizar.pdf.texto_conferido())
    assert pedidos == []


def test_o_que_mudou_com_a_pergunta_na_tela_e_perguntado_de_novo(janela, pedidos, tmp_path):
    # Quem aceitou interromper uma leitura não aceitou jogar fora o texto que ela virou.
    _leitura_no_gerar_ocr(janela)
    tela = _pedir_para_reabrir(janela)
    janela.painel_ocr.leitura = None
    _texto_no_gerar_ocr(janela, tmp_path)
    tela.pergunta.botao_mesmo_assim.click()
    assert pedidos == []
    assert not tela.pergunta.isHidden()
    assert tela.pergunta.cima.text() == "Há um texto lido e ainda não salvo no Gerar OCR."
    tela.pergunta.botao_mesmo_assim.click()
    assert pedidos == [estilo.CLARO]


def test_o_que_acabou_com_a_pergunta_na_tela_nao_e_perguntado(janela, pedidos):
    _leitura_no_gerar_ocr(janela)
    tela = _pedir_para_reabrir(janela)
    janela.painel_ocr.leitura = None
    tela.pergunta.botao_mesmo_assim.click()
    assert pedidos == [estilo.CLARO]


def test_marcar_o_tema_da_tela_tira_a_pergunta(janela, pedidos):
    _leitura_no_gerar_ocr(janela)
    tela = _pedir_para_reabrir(janela)
    tela.opcoes[estilo.ESCURO].click()
    assert tela.pergunta.isHidden()
    assert tela.aviso.isHidden()
    tela.opcoes[estilo.CLARO].click()
    assert tela.pergunta.isHidden()
    assert tela.aviso.frase.text() == VALE_AO_REABRIR


def test_sair_da_tela_tira_a_pergunta_e_a_volta_pergunta_o_que_vale_agora(janela, pedidos,
                                                                          tmp_path):
    # Revisão da etapa 6: a pergunta velha ficava na tela, e o "Reabrir mesmo assim"
    # jogava fora, sem perguntar, as correções de outro documento lido no meio-tempo.
    _texto_no_anonimizar(janela, tmp_path)
    tela = _pedir_para_reabrir(janela)
    assert not tela.pergunta.isHidden()

    janela.menu.botao_voltar_ia.click()
    janela.menu.botao_anonimizar.click()
    janela.menu.botao_config_ia.click()
    assert janela.painel_ia.tela_atual() == TEMA
    assert tela.pergunta.isHidden()
    assert tela.aviso.frase.text() == VALE_AO_REABRIR
    assert not tela.aviso.botao.isHidden()

    tela.aviso.botao.click()
    assert pedidos == []
    assert tela.pergunta.cima.text() == "Há um texto lido e ainda não salvo no Anonimizar."


def test_trocar_de_opcao_nas_configuracoes_tambem_tira_a_pergunta(janela, pedidos):
    _leitura_no_gerar_ocr(janela)
    tela = _pedir_para_reabrir(janela)
    janela.menu.itens_do_submenu[1].click()
    janela.menu.botao_tema.click()
    assert tela.pergunta.isHidden()
    assert not tela.aviso.botao.isHidden()
    assert pedidos == []


# ------------------------------------------------- a revisão não salva vem antes


def test_revisao_nao_salva_vem_antes_e_a_leitura_e_perguntada_depois(janela, pedidos,
                                                                     tmp_path):
    copia = tmp_path / "10-prestacao-com-cpf.md"
    shutil.copy(MASSA / copia.name, copia)
    janela.menu.botao_anonimizar.click()
    janela.painel_anonimizar.receber_arquivo(copia)
    janela.menu.botao_config_ia.click()
    # Sair do Anonimizar já pergunta: descartada, a revisão sai antes da tela do Tema.
    # Para chegar ao caso da RN-28, o reabrir é pedido com a revisão aberta, como um
    # caminho novo faria.
    janela.painel_anonimizar._voltar_de_onde_estava()
    _leitura_no_gerar_ocr(janela)
    tela = janela.painel_ia.tela_tema
    tela.opcoes[estilo.CLARO].click()
    janela.reabrir(estilo.CLARO)
    anonimizar = janela.painel_anonimizar
    assert anonimizar.telas.currentWidget() is anonimizar.tela_descartar
    assert pedidos == []

    anonimizar.tela_descartar.botao_descartar.click()
    assert pedidos == []
    assert janela.painel.currentWidget() is janela.painel_ia
    assert janela.painel_ia.tela_atual() == TEMA
    assert not tela.pergunta.isHidden()
    assert tela.pergunta.cima.text() == "Há uma leitura em andamento no Gerar OCR."


# ------------------------------------------------------------ a janela mínima


def test_na_janela_minima_a_pergunta_mais_longa_sai_inteira(janela, tmp_path):
    janela.showNormal()
    janela.resize(TAMANHO_MINIMO)
    _leitura_no_gerar_ocr(janela)
    _texto_no_anonimizar(janela, tmp_path)
    tela = _pedir_para_reabrir(janela)
    QApplication.processEvents()
    pergunta = tela.pergunta
    for frase in (pergunta.cima, pergunta.baixo):
        assert frase.height() >= frase.heightForWidth(frase.width()), frase.text()
        assert frase.geometry().right() < pergunta.width(), frase.text()
    for botao in (pergunta.botao_forte, pergunta.botao_mesmo_assim):
        assert botao.width() >= botao.sizeHint().width(), botao.text()
    assert pergunta.geometry().right() < tela.width()

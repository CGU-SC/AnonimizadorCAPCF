"""Cada motor faltando, nos dois módulos (RN-29 e RN-30 da emenda de 18/10/2026
da spec 002).

Nenhum motor desta máquina é tocado: o controle do motor recebe respostas de
mentira para "o PaddleOCR está completo?" e "achei o Tesseract?". O caso de
nenhum dos dois funcionando é o de antes da emenda, e está em
test_painel_sem_motor.py.
"""
from pathlib import Path

import pytest

import caminho_do_pdf
import motor_na_tela
import motor_paddleocr
from painel_anonimizar import PainelAnonimizar
from painel_ocr import PainelOcr

MASSA = Path(__file__).parent.parent / "dados-exemplo"
ESCANEADO = MASSA / "02-imprimir-para-pdf.pdf"


class _Maquina:
    def __init__(self):
        self.paddleocr = True
        self.tesseract = True
        # O Tesseract está lá, só que sem o pacote de português.
        self.sem_portugues = False


@pytest.fixture
def maquina(monkeypatch):
    estado = _Maquina()
    monkeypatch.setattr(motor_paddleocr, "presente", lambda: estado.paddleocr)
    monkeypatch.setattr(
        motor_na_tela, "localizar_tesseract",
        lambda: Path(r"C:\Qualquer\tesseract.exe") if estado.tesseract else None)
    monkeypatch.setattr(motor_na_tela, "ha_algum_tesseract", lambda: estado.sem_portugues)
    monkeypatch.setattr(motor_na_tela, "localizar_instalador", lambda: None)
    return estado


def _escolhas(painel_ocr, painel_anonimizar):
    return (painel_ocr.escolha_do_motor,
            painel_anonimizar.pdf.tela_de_ler.escolha_do_motor)


# ------------------------------------------------- falta só o Tesseract


def test_sem_o_tesseract_a_falta_e_dita_na_linha_dele_e_nao_no_alto(maquina):
    """RN-30: o PaddleOCR lê, então não há aviso no alto nem tela cheia."""
    maquina.tesseract = False
    painel_ocr, painel_anonimizar = PainelOcr(), PainelAnonimizar()

    for painel in (painel_ocr, painel_anonimizar):
        assert painel.motor.aviso.isHidden()
    for escolha in _escolhas(painel_ocr, painel_anonimizar):
        assert not escolha.tesseract.isEnabled()
        assert not escolha.falta_tesseract.isHidden()
        assert escolha.falta_tesseract.text() == caminho_do_pdf.FALTA_TESSERACT
        assert escolha.resumo_tesseract.isHidden()
        # As três saídas ficam ali, coladas na linha do Tesseract.
        assert not escolha.saidas_do_tesseract.isHidden()
        assert escolha.paddleocr.isChecked()


def test_sem_o_tesseract_o_pdf_escaneado_segue_para_a_leitura(maquina):
    """Antes da emenda, o PDF escaneado ia para a tela cheia de motor faltando."""
    maquina.tesseract = False

    painel_ocr = PainelOcr()
    painel_ocr.pdf.conferir_documento(ESCANEADO)
    assert painel_ocr.telas.currentWidget() is painel_ocr.pdf.tela_ficha

    painel_anonimizar = PainelAnonimizar()
    painel_anonimizar.receber_arquivo(ESCANEADO)
    painel_anonimizar.pdf.conferir_documento(ESCANEADO)
    assert painel_anonimizar.telas.currentWidget() is painel_anonimizar.pdf.tela_de_ler


def test_tesseract_instalado_com_o_programa_aberto_volta_a_linha(maquina):
    maquina.tesseract = False
    painel = PainelOcr()
    maquina.tesseract = True

    painel.motor.conferir_de_novo()

    escolha = painel.escolha_do_motor
    assert escolha.tesseract.isEnabled()
    assert escolha.falta_tesseract.isHidden()
    assert escolha.saidas_do_tesseract.isHidden()
    # Voltar o Tesseract não tira a marca do PaddleOCR.
    assert escolha.paddleocr.isChecked()


def test_tesseract_marcado_que_some_passa_a_marca_ao_paddleocr(maquina):
    painel = PainelOcr()
    painel.escolha_do_motor.tesseract.setChecked(True)
    maquina.tesseract = False

    painel.motor.conferir()

    assert painel.escolha_do_motor.paddleocr.isChecked()


# ------------------------------------------------- falta só o PaddleOCR


def test_sem_o_paddleocr_a_linha_pede_reinstalar_e_o_tesseract_vem_marcado(maquina):
    """RN-29: instalação estragada. Nada troca de motor por baixo do pano: a
    marca vai para o Tesseract, e a linha apagada diz por quê."""
    maquina.paddleocr = False
    painel_ocr, painel_anonimizar = PainelOcr(), PainelAnonimizar()

    for painel in (painel_ocr, painel_anonimizar):
        assert painel.motor.aviso.isHidden()
    for escolha in _escolhas(painel_ocr, painel_anonimizar):
        assert not escolha.paddleocr.isEnabled()
        assert escolha.falta_paddleocr.text() == caminho_do_pdf.FALTA_PADDLEOCR
        assert not escolha.falta_paddleocr.isHidden()
        assert escolha.resumo_paddleocr.isHidden()
        assert escolha.tesseract.isChecked()
        assert escolha.saidas_do_tesseract.isHidden()


# ------------------------------------------------- falta os dois


def test_sem_nenhum_o_aviso_e_o_de_hoje_e_as_saidas_nao_se_repetem(maquina):
    """Rascunho 11, estado 4: o aviso do alto traz as saídas; a linha do
    Tesseract só diz que falta."""
    maquina.paddleocr = False
    maquina.tesseract = False
    painel = PainelOcr()

    assert not painel.motor.aviso.isHidden()
    escolha = painel.escolha_do_motor
    assert not escolha.paddleocr.isEnabled()
    assert not escolha.tesseract.isEnabled()
    assert escolha.falta_tesseract.text() == caminho_do_pdf.FALTA_TESSERACT_SEM_NENHUM
    assert escolha.saidas_do_tesseract.isHidden()

    painel.pdf.conferir_documento(ESCANEADO)
    assert painel.telas.currentWidget() is painel.tela_sem_motor


def test_as_frases_de_falta_cabem_numa_linha_na_janela_minima():
    """Como os resumos, as frases não quebram linha (test_escolha_do_motor)."""
    from test_escolha_do_motor import LARGURA_QUE_SOBRA

    escolha = caminho_do_pdf.EscolhaDoMotor("MOTOR DE LEITURA")
    for frase in (caminho_do_pdf.FALTA_PADDLEOCR, caminho_do_pdf.FALTA_TESSERACT,
                  caminho_do_pdf.FALTA_PORTUGUES):
        escolha.falta_tesseract.setText(frase)
        escolha.falta_tesseract.ensurePolished()
        assert escolha.falta_tesseract.sizeHint().width() <= LARGURA_QUE_SOBRA, frase


def test_sem_o_portugues_a_linha_nao_diz_que_o_tesseract_falta(maquina):
    """Lente crítica da etapa 4: "não encontrado" mandaria a TI conferir, ver o
    Tesseract instalado, e não mexer em nada."""
    maquina.tesseract = False
    maquina.sem_portugues = True
    painel = PainelOcr()

    assert painel.escolha_do_motor.falta_tesseract.text() == caminho_do_pdf.FALTA_PORTUGUES


def test_conferir_de_novo_sem_sucesso_fala_do_tesseract_e_nao_do_motor(maquina):
    """Lente crítica da etapa 4: com o PaddleOCR lendo ao lado, "o motor
    continua sem ser encontrado" faria pensar que o programa parou de ler."""
    maquina.tesseract = False
    painel = PainelOcr()

    painel.motor.conferir_de_novo()

    recado = painel.motor._saidas_na_escolha.recado.text()
    assert recado.startswith("O Tesseract continua sem ser encontrado.")

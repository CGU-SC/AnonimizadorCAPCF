"""A lembrança do motor separada da tela (etapa 1 da funcionalidade 4)."""
from pathlib import Path

import preferencias
from caminho_do_pdf import EscolhaDoMotor
from lembranca_do_motor import LembrancaDoMotor
from painel_anonimizar import PainelAnonimizar
from painel_ocr import PainelOcr

PROGRAMA = Path(__file__).parent


def test_a_tela_nao_sabe_mais_onde_a_escolha_fica_guardada():
    """É o que a separação promete: motor novo não repete a ligação na tela."""
    codigo = (PROGRAMA / "caminho_do_pdf.py").read_text(encoding="utf-8")
    assert "preferencias" not in codigo


def test_a_lembranca_guarda_por_modulo():
    LembrancaDoMotor("gerar_ocr").lembrar("tesseract")
    assert LembrancaDoMotor("gerar_ocr").motor() == "tesseract"
    assert LembrancaDoMotor("anonimizar").motor() is None


def test_sem_lembranca_a_escolha_nao_grava_nada():
    escolha = EscolhaDoMotor("LER COM")
    escolha.tesseract.setChecked(True)
    assert preferencias.ler_bloco("gerar_ocr") == {}
    assert preferencias.ler_bloco("anonimizar") == {}


def test_cada_modulo_continua_com_a_sua_escolha():
    PainelOcr().escolha_do_motor.tesseract.setChecked(True)
    assert preferencias.ler("gerar_ocr", "motor") == "tesseract"
    assert preferencias.ler("anonimizar", "motor") is None
    assert PainelOcr().escolha_do_motor.tesseract.isChecked()
    assert PainelAnonimizar().pdf.tela_de_ler.escolha_do_motor.paddleocr.isChecked()

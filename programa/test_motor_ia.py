"""A IA como motor de leitura, e o instalador (etapa 8, RN-38 a RN-42 da spec 004)."""
import shutil
import sys
from pathlib import Path

import pytest
from PIL import Image

import avisos_da_ia
import caminho_do_pdf
import config_ia
import leitura
import motor_ia
import preferencias
import rede_da_ia
from caminho_do_pdf import FRASE_DA_IA_ACESA, EscolhaDoMotor
from lembranca_do_motor import LembrancaDoMotor
from leitura import MOTOR_IA, MOTOR_PADDLEOCR
from painel_anonimizar import PainelAnonimizar
from painel_ocr import PainelOcr
from test_escolha_do_motor import leitura_de_mentira  # noqa: F401

RAIZ = Path(__file__).parent.parent
sys.path.insert(0, str(RAIZ / "abrir"))
from servidor_de_ia_de_mentira import ServidorDeMentira  # noqa: E402

MASSA = RAIZ / "dados-exemplo"
ESCANEADO = next(MASSA.glob("*escanead*.pdf"), None)
MODELO = "modelo-exemplo-visao-13b"


@pytest.fixture
def servidor():
    servidor = ServidorDeMentira()
    yield servidor
    servidor.parar()


def _motor_ativo(servidor=None, porta=None):
    config_ia.guardar_do_destino(
        config_ia.LM_STUDIO, porta=servidor.porta if servidor else (porta or 1234),
        modelo_revisora="modelo-exemplo-texto-8b", modelo_motor=MODELO)
    config_ia.marcar_testado(config_ia.LM_STUDIO, True)
    config_ia.marcar_motor_testado(config_ia.LM_STUDIO, True)
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    config_ia.ligar_geral()
    config_ia.marcar_motor(True)


_paineis = []


def _escolhas():
    # Guardados: painel recolhido pelo Python leva junto as telas de dentro.
    _paineis[:] = [PainelOcr(), PainelAnonimizar()]
    return (_paineis[0].escolha_do_motor, _paineis[1].pdf.tela_de_ler.escolha_do_motor)


def test_com_a_chave_desligada_fica_apagada_e_diz_onde_ligar():
    for escolha in _escolhas():
        assert not escolha.ia_local.isEnabled()
        assert escolha.ia_local.text() == "IA local"
        assert escolha.frase_da_ia.text() == 'Ligue em Configurações de IA, em "Habilitar IA".'


def test_com_a_chave_sem_modelo_pede_o_modelo():
    _motor_ativo()
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, modelo_motor="")
    for escolha in _escolhas():
        assert not escolha.ia_local.isEnabled()
        assert "Escolha o modelo do motor" in escolha.frase_da_ia.text()


def test_modelo_sem_passar_no_teste_nao_acende():
    _motor_ativo()
    config_ia.marcar_motor_testado(config_ia.LM_STUDIO, False)
    assert not EscolhaDoMotor("LER COM").ia_local.isEnabled()


def test_com_a_chave_e_o_modelo_acende_nos_dois_modulos_sem_ficar_marcada():
    _motor_ativo()
    for escolha in _escolhas():
        assert escolha.ia_local.isEnabled()
        assert escolha.ia_local.text() == "IA local (LM Studio)"
        assert escolha.frase_da_ia.text() == FRASE_DA_IA_ACESA
        assert escolha.marcado() == MOTOR_PADDLEOCR


def test_marcada_ela_e_o_motor_e_e_lembrada_por_modulo():
    _motor_ativo()
    PainelOcr().escolha_do_motor.ia_local.setChecked(True)
    assert preferencias.ler("gerar_ocr", "motor") == MOTOR_IA
    assert PainelOcr().escolha_do_motor.marcado() == MOTOR_IA
    assert PainelAnonimizar().pdf.tela_de_ler.escolha_do_motor.marcado() == MOTOR_PADDLEOCR


def test_lembrada_com_a_chave_desligada_passa_a_outro_e_diz_o_motivo():
    _motor_ativo()
    PainelOcr().escolha_do_motor.ia_local.setChecked(True)
    config_ia.marcar_motor(False)
    escolha = PainelOcr().escolha_do_motor
    assert escolha.marcado() != MOTOR_IA
    assert "porque a IA foi desligada" in escolha.frase_da_ia.text()
    # A troca vale como escolha nova, e é lembrada (RN-37 da spec 002).
    assert LembrancaDoMotor("gerar_ocr").motor() == MOTOR_PADDLEOCR


def test_desligando_com_a_tela_aberta_a_marca_passa_na_proxima_conferida():
    _motor_ativo()
    painel = PainelOcr()
    painel.escolha_do_motor.ia_local.setChecked(True)
    config_ia.desligar_destino()
    painel.motor.conferir()
    assert painel.escolha_do_motor.marcado() != MOTOR_IA
    assert "porque a IA foi desligada" in painel.escolha_do_motor.frase_da_ia.text()


def test_sem_paddleocr_a_marca_da_ia_passa_ao_tesseract():
    _motor_ativo()
    escolha = EscolhaDoMotor("LER COM")
    escolha.ia_local.setChecked(True)
    config_ia.marcar_motor(False)
    escolha.mostrar_o_que_ha(False, True)
    assert escolha.marcado() == leitura.MOTOR_TESSERACT


def test_a_frase_da_ia_nao_corta_na_janela_minima():
    from test_escolha_do_motor import LARGURA_QUE_SOBRA
    _motor_ativo()
    escolha = EscolhaDoMotor("LER COM")
    assert escolha.frase_da_ia.width() <= LARGURA_QUE_SOBRA
    assert escolha.frase_da_ia.minimumHeight() >= escolha.frase_da_ia.heightForWidth(
        escolha.frase_da_ia.width())


def test_o_tempo_nao_inventa_numero():
    assert leitura.tempo_estimado(10, MOTOR_IA) == "um tempo que depende do modelo"


def test_a_imagem_vai_reduzida_e_o_texto_volta(servidor):
    _motor_ativo(servidor)
    motor_ia.preparar()
    grande = Image.new("RGB", (2480, 3508), "white")
    texto = motor_ia.ler(grande)
    assert "Texto lido pela IA" in texto
    corpo = servidor.comportamento.corpo_cru[0]
    assert '"model": "modelo-exemplo-visao-13b"' in corpo
    assert "data:image/png;base64," in corpo
    from base64 import b64decode
    from io import BytesIO
    dados = corpo.split("base64,")[1].split('"')[0]
    assert max(Image.open(BytesIO(b64decode(dados))).size) == motor_ia.MAIOR_LADO_EM_PIXELS


def test_sem_a_chave_nao_le(servidor):
    with pytest.raises(motor_ia.IaIndisponivel):
        motor_ia.preparar()


@pytest.fixture
def pdf(tmp_path):
    import pymupdf
    caminho = tmp_path / "documento.pdf"
    documento = pymupdf.open()
    documento.new_page().insert_text((72, 72), "Pagina um")
    documento.new_page().insert_text((72, 72), "Pagina dois")
    documento.save(caminho)
    documento.close()
    return caminho


def test_o_documento_inteiro_e_lido_pela_ia(servidor, pdf):
    _motor_ativo(servidor)
    paginas = leitura.ler_documento(pdf, motor=MOTOR_IA)
    assert len(paginas) == 2 and "Texto lido" in paginas[0]


def test_falha_numa_pagina_vira_a_falha_de_leitura_de_sempre(servidor, pdf):
    _motor_ativo(servidor)
    servidor.comportamento.cair_no_pedido = 2
    with pytest.raises(leitura.LeituraFalhou) as falha:
        leitura.ler_documento(pdf, motor=MOTOR_IA)
    assert falha.value.pagina == 2
    assert "erro" not in str(falha.value)


def test_sem_a_chave_a_leitura_vira_motor_nao_encontrado(pdf):
    with pytest.raises(leitura.MotorNaoEncontrado):
        leitura.ler_documento(pdf, motor=MOTOR_IA)


def test_cancelar_de_verdade_corta_a_pagina(servidor, pdf):
    import threading
    import time
    _motor_ativo(servidor)
    servidor.comportamento.demora = 6
    resultado = []

    def ler():
        try:
            leitura.ler_documento(pdf, motor=MOTOR_IA)
        except leitura.LeituraCancelada as parada:
            resultado.append(parada.pagina)

    linha = threading.Thread(target=ler)
    comeco = time.monotonic()
    linha.start()
    time.sleep(1)
    motor_ia.cancelar()
    linha.join(3)
    assert resultado == [1]
    assert time.monotonic() - comeco < 4


def test_marcada_e_ela_que_le_e_a_conferencia_e_a_de_sempre(leitura_de_mentira, tmp_path, servidor):  # noqa: F811
    _motor_ativo(servidor)
    painel = PainelOcr()
    painel.escolha_do_motor.ia_local.setChecked(True)
    ficha = type("Ficha", (), {"caminho": tmp_path / "x.pdf", "paginas": 1,
                               "tem_camada_de_texto": False})()
    painel.pdf.comecar_a_ler(ficha)
    assert leitura_de_mentira.motores == [MOTOR_IA]


def test_endereco_nao_confirmado_nao_le_e_fica_onde_estava(leitura_de_mentira, tmp_path, monkeypatch):  # noqa: F811
    avisos_da_ia.esquecer_confirmado()
    _motor_ativo()
    config_ia.guardar_do_destino(config_ia.SERVIDOR, endereco="http://ia.instituicao.exemplo",
                                 modelo_revisora="m", modelo_motor=MODELO)
    config_ia.marcar_testado(config_ia.SERVIDOR, True)
    config_ia.marcar_motor_testado(config_ia.SERVIDOR, True)
    config_ia.ligar_destino(config_ia.SERVIDOR)
    monkeypatch.setattr(rede_da_ia, "_numeros_do_nome", lambda host: [])
    monkeypatch.setattr(avisos_da_ia, "exibir", lambda *a, **k: False)
    painel = PainelOcr()
    painel.escolha_do_motor.ia_local.setChecked(True)
    tela_antes = painel.telas.currentWidget()
    ficha = type("Ficha", (), {"caminho": tmp_path / "x.pdf", "paginas": 1,
                               "tem_camada_de_texto": False})()
    painel.pdf.comecar_a_ler(ficha)
    assert leitura_de_mentira.motores == []
    assert painel.telas.currentWidget() is tela_antes


def test_a_conferencia_diz_quem_leu():
    assert leitura.NOME_NA_TELA[MOTOR_IA] == "IA local"


def test_caminho_do_pdf_nao_tem_nenhum_sinal_de_rede():
    codigo = Path(caminho_do_pdf.__file__).read_text(encoding="utf-8").lower()
    assert "http" not in codigo


# ------------------------------------------------------------------ o instalador


def test_o_modelo_do_env_traz_as_duas_linhas_em_branco():
    texto = (RAIZ / "empacotar" / "modelo.env").read_text(encoding="utf-8")
    assert "\nIA_SERVIDOR_TOKEN=\n" in texto
    assert "\nIA_ENDERECOS_LOCAIS=\n" in texto
    assert "LLM_REMOTA" not in texto


def test_o_exemplo_nao_tem_mais_as_variaveis_que_ninguem_lia():
    texto = (RAIZ / ".env.example").read_text(encoding="utf-8")
    assert "LLM_REMOTA" not in texto
    assert "IA_SERVIDOR_TOKEN=\n" in texto.replace("\r\n", "\n")


def test_desinstalar_leva_o_token_e_atualizar_nao():
    iss = (RAIZ / "empacotar" / "instalador.iss").read_text(encoding="utf-8")
    apagar = iss.split("[UninstallDelete]")[1].split("[Icons]")[0]
    assert 'Name: "{app}\\.env"' in apagar
    assert 'Name: "{app}\\.env.*.gravando"' in apagar
    # Numa atualização, o .env que existe fica como está.
    assert 'DestName: ".env"; Flags: onlyifdoesntexist' in iss


def test_o_instalador_nao_leva_o_servidor_de_mentira():
    spec = (RAIZ / "empacotar" / "anonimizador.spec").read_text(encoding="utf-8")
    assert "mentira" not in spec
    assert shutil.which is not None

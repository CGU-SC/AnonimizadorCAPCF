"""As escolhas lembradas de um uso para o outro (emenda de 28/10/2026 da spec 002).

Cada teste lembra num arquivo só dele, numa pasta provisória (o
`preferencias_isoladas` do conftest.py): nenhum teste toca o `preferencias.ini`
da raiz do projeto, que é o desta máquina.

"Fechar e abrir o programa de novo" é, aqui, montar o painel de novo: tudo o que
o programa tinha na memória vai embora, e só o que foi gravado volta.
"""
import configparser
import os
from pathlib import Path

import pytest

import configuracao
import leitura
import motor_na_tela
import motor_paddleocr
import preferencias
from painel_anonimizar import PainelAnonimizar
from painel_ocr import PainelOcr


@pytest.fixture
def maquina(monkeypatch):
    """Os dois motores presentes, sem depender do que esta máquina tem."""
    monkeypatch.setattr(motor_paddleocr, "presente", lambda: True)
    monkeypatch.setattr(motor_na_tela, "localizar_tesseract",
                        lambda: Path(r"C:\Qualquer\tesseract.exe"))
    monkeypatch.setattr(motor_na_tela, "localizar_instalador", lambda: None)


def _lido(arquivo):
    conteudo = configparser.ConfigParser(interpolation=None)
    conteudo.read_string(arquivo.read_text(encoding="utf-8"))
    return {secao: dict(conteudo[secao]) for secao in conteudo.sections()}


# ------------------------------------------------------- o arquivo em si

def test_os_testes_nunca_tocam_o_arquivo_da_raiz(preferencias_isoladas):
    """Premissa da emenda: teste não se mistura com o uso desta máquina."""
    da_raiz = configuracao.pasta_do_programa() / preferencias.NOME_DO_ARQUIVO
    assert preferencias.caminho() == preferencias_isoladas
    assert preferencias.caminho() != da_raiz


def test_sem_arquivo_nada_e_lembrado():
    assert preferencias.ler("gerar_ocr", "motor") is None


def test_gravado_volta_e_cada_secao_fica_com_o_seu(preferencias_isoladas):
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    preferencias.gravar("anonimizar", "motor", "paddleocr")
    preferencias.gravar("gerar_ocr", "motor", "paddleocr")
    assert preferencias.ler("gerar_ocr", "motor") == "paddleocr"
    assert preferencias.ler("anonimizar", "motor") == "paddleocr"
    assert _lido(preferencias_isoladas) == {
        "gerar_ocr": {"motor": "paddleocr"}, "anonimizar": {"motor": "paddleocr"}}


def test_o_arquivo_diz_o_que_e_para_quem_o_abrir(preferencias_isoladas):
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    assert preferencias_isoladas.read_text(encoding="utf-8").startswith(
        "# Escolhas de quem usa o Anonimizador CAPCF")


@pytest.mark.parametrize("estragado", [
    b"isto nao e um arquivo de preferencias\n[sem fim",
    b"\xff\xfe\x00 lixo binario \x00\x9d",
    b"motor = tesseract\n",            # sem bloco nenhum
])
def test_arquivo_estragado_vale_como_nada_lembrado_e_e_refeito(
        preferencias_isoladas, estragado):
    """RN-39: abre no padrão, sem erro; a próxima gravação refaz o arquivo."""
    preferencias_isoladas.write_bytes(estragado)
    assert preferencias.ler("gerar_ocr", "motor") is None
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    assert _lido(preferencias_isoladas) == {"gerar_ocr": {"motor": "tesseract"}}


def test_pasta_que_nao_aceita_gravar_segue_calada(tmp_path, monkeypatch):
    """RN-39: perder a lembrança não trava nada nem avisa."""
    sem_pasta = tmp_path / "pasta-que-nao-existe" / "preferencias.ini"
    monkeypatch.setattr(preferencias, "caminho", lambda: sem_pasta)
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    assert not sem_pasta.exists()
    assert preferencias.ler("gerar_ocr", "motor") is None


def test_gravacao_cortada_no_meio_deixa_o_que_estava_inteiro(
        preferencias_isoladas, monkeypatch):
    """RN-39: o arquivo novo só toma o lugar do velho no fim; cortado antes,
    o que já estava lembrado continua, e o provisório não fica para trás."""
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    antes = preferencias_isoladas.read_bytes()

    def falha(*_):
        raise OSError("a máquina desligou")
    monkeypatch.setattr(os, "replace", falha)
    preferencias.gravar("gerar_ocr", "motor", "paddleocr")

    assert preferencias_isoladas.read_bytes() == antes
    assert not list(preferencias_isoladas.parent.glob("*.gravando"))


def test_leitura_presa_por_outro_programa_nao_apaga_as_outras_escolhas(
        preferencias_isoladas, monkeypatch):
    """Regressão da lente crítica da etapa 1: com o arquivo preso por um
    instante, a próxima gravação reescrevia só a escolha nova e perdia as
    outras. Agora ela desiste, e as outras continuam."""
    preferencias.gravar("anonimizar", "motor", "tesseract")
    antes = preferencias_isoladas.read_bytes()
    ler_de_verdade = Path.read_bytes
    preso = [True]

    def lendo(caminho, *a, **k):
        if preso[0] and caminho == preferencias_isoladas:
            raise PermissionError("preso pelo antivírus")
        return ler_de_verdade(caminho, *a, **k)
    monkeypatch.setattr(Path, "read_bytes", lendo)
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    preso[0] = False

    assert preferencias_isoladas.read_bytes() == antes


def test_arquivo_salvo_com_bom_e_editado_a_mao_e_entendido(preferencias_isoladas):
    """Regressão da lente crítica da etapa 1: o "UTF-8 com BOM" do Bloco de
    Notas contava como estragado, e "Tesseract" com maiúscula era ignorado."""
    preferencias_isoladas.write_bytes(
        "\ufeff[gerar_ocr]\nmotor =  Tesseract \n".encode("utf-8"))
    assert preferencias.ler("gerar_ocr", "motor") == "tesseract"


@pytest.mark.parametrize("formato", ["utf-8", "utf-8-sig", "utf-16", "cp1252"])
def test_arquivo_salvo_no_bloco_de_notas_em_qualquer_formato_e_entendido(
        preferencias_isoladas, formato):
    """Regressão da lente crítica da etapa 4: salvo em "ANSI" ou "Unicode", o
    "não" da janela fazia o arquivo inteiro valer como estragado."""
    preferencias_isoladas.write_bytes(
        "[gerar_ocr]\nmotor = tesseract\n[janela]\nmaximizada = não\n".encode(formato))
    assert preferencias.ler("gerar_ocr", "motor") == "tesseract"
    assert preferencias.ler("janela", "maximizada") == "não"
    preferencias.gravar("anonimizar", "motor", "tesseract")
    assert preferencias.ler("gerar_ocr", "motor") == "tesseract"


def test_bloco_default_escrito_a_mao_nao_vaza_para_os_outros(preferencias_isoladas):
    """Regressão da lente crítica da etapa 4."""
    preferencias_isoladas.write_text("[DEFAULT]\nmotor = tesseract\n", encoding="utf-8")
    assert preferencias.ler("gerar_ocr", "motor") is None
    assert preferencias.ler_bloco("janela") == {}


def test_troca_recusada_por_um_instante_insiste_e_grava(preferencias_isoladas, monkeypatch):
    """Regressão da lente crítica da etapa 4: o antivírus segura o arquivo por
    um instante, e a troca é recusada; a escolha não se perde por isso."""
    recusas = [PermissionError("antivírus"), PermissionError("antivírus")]
    trocar_de_verdade = os.replace

    def troca(*a):
        if recusas:
            raise recusas.pop()
        return trocar_de_verdade(*a)
    monkeypatch.setattr(os, "replace", troca)
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    assert preferencias.ler("gerar_ocr", "motor") == "tesseract"
    assert not list(preferencias_isoladas.parent.glob("*.gravando"))


def test_duas_janelas_nao_dividem_o_arquivo_provisorio(preferencias_isoladas, monkeypatch):
    """Regressão da lente crítica da etapa 1: o nome do provisório é de cada
    programa aberto."""
    nomes = []
    abrir = open

    def guarda(caminho, *a, **k):
        nomes.append(Path(caminho).name)
        return abrir(caminho, *a, **k)
    monkeypatch.setattr("builtins.open", guarda)
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    assert nomes == [f"preferencias-do-teste.ini.{os.getpid()}.gravando"]


# ------------------------------------------------- o Gerar OCR (etapa 1)

def test_o_gerar_ocr_lembra_o_motor_marcado(maquina, preferencias_isoladas):
    """RN-36: marcou o Tesseract, fechou, abriu - ele vem marcado."""
    PainelOcr().escolha_do_motor.tesseract.setChecked(True)
    assert _lido(preferencias_isoladas) == {"gerar_ocr": {"motor": "tesseract"}}

    reaberto = PainelOcr()
    assert reaberto.escolha_do_motor.marcado() == leitura.MOTOR_TESSERACT


def test_voltar_ao_padrao_e_marcar_o_paddleocr(maquina):
    """Fora de escopo da emenda: não há botão de voltar ao padrão."""
    painel = PainelOcr()
    painel.escolha_do_motor.tesseract.setChecked(True)
    painel.escolha_do_motor.paddleocr.setChecked(True)
    assert PainelOcr().escolha_do_motor.marcado() == leitura.MOTOR_PADDLEOCR


def test_quem_nunca_escolheu_abre_com_o_paddleocr(maquina, preferencias_isoladas):
    assert PainelOcr().escolha_do_motor.marcado() == leitura.MOTOR_PADDLEOCR
    # Só abrir não grava nada: a lembrança nasce da escolha da pessoa.
    assert not preferencias_isoladas.exists()


def test_motor_lembrado_que_nao_existe_vale_como_nada(maquina, preferencias_isoladas):
    preferencias_isoladas.write_text("[gerar_ocr]\nmotor = outro\n", encoding="utf-8")
    assert PainelOcr().escolha_do_motor.marcado() == leitura.MOTOR_PADDLEOCR


def test_marcar_no_gerar_ocr_nao_muda_o_anonimizar(maquina):
    """RN-36: uma escolha por módulo."""
    PainelOcr().escolha_do_motor.tesseract.setChecked(True)
    assert _do_anonimizar(PainelAnonimizar()).marcado() == leitura.MOTOR_PADDLEOCR


# ------------------------------------------------- o Anonimizar (etapa 2)

def _do_anonimizar(painel):
    return painel.pdf.tela_de_ler.escolha_do_motor


def test_o_anonimizar_lembra_o_motor_sem_ler_documento(maquina, preferencias_isoladas):
    """Critério de aceite: marcou o Tesseract no Anonimizar, sem ler nada,
    fechou e abriu - ele vem marcado, e o Gerar OCR fica como estava."""
    PainelOcr().escolha_do_motor.tesseract.setChecked(True)
    _do_anonimizar(PainelAnonimizar()).tesseract.setChecked(True)
    _do_anonimizar(PainelAnonimizar()).paddleocr.setChecked(True)
    assert _lido(preferencias_isoladas) == {
        "gerar_ocr": {"motor": "tesseract"}, "anonimizar": {"motor": "paddleocr"}}

    _do_anonimizar(PainelAnonimizar()).tesseract.setChecked(True)
    assert _do_anonimizar(PainelAnonimizar()).marcado() == leitura.MOTOR_TESSERACT
    # O Gerar OCR ficou com o que estava: se o Anonimizar gravasse no bloco
    # dele, ali estaria o último motor marcado no Anonimizar.
    preferencias.gravar("gerar_ocr", "motor", "paddleocr")
    _do_anonimizar(PainelAnonimizar()).paddleocr.setChecked(True)
    _do_anonimizar(PainelAnonimizar()).tesseract.setChecked(True)
    assert PainelOcr().escolha_do_motor.marcado() == leitura.MOTOR_PADDLEOCR


def test_marcar_no_anonimizar_nao_muda_o_gerar_ocr(maquina, preferencias_isoladas):
    _do_anonimizar(PainelAnonimizar()).tesseract.setChecked(True)
    assert PainelOcr().escolha_do_motor.marcado() == leitura.MOTOR_PADDLEOCR
    assert _lido(preferencias_isoladas) == {"anonimizar": {"motor": "tesseract"}}


def test_o_gerar_ocr_nao_lembra_pela_tela_de_ler_que_nao_mostra(
        maquina, preferencias_isoladas):
    """O Gerar OCR monta a tela de ler do caminho do PDF sem usá-la: a escolha
    escondida dela não pode gravar nada, nem ler o que é do Anonimizar."""
    preferencias_isoladas.write_text("[anonimizar]\nmotor = tesseract\n", encoding="utf-8")
    escondida = PainelOcr().pdf.tela_de_ler.escolha_do_motor
    assert escondida.marcado() == leitura.MOTOR_PADDLEOCR
    escondida.tesseract.setChecked(True)
    escondida.paddleocr.setChecked(True)
    assert _lido(preferencias_isoladas) == {"anonimizar": {"motor": "tesseract"}}


def test_nenhum_dos_dois_grava_ao_abrir(maquina, preferencias_isoladas):
    PainelOcr()
    PainelAnonimizar()
    assert not preferencias_isoladas.exists()


# ------------------------------------- o motor lembrado que falta (RN-37)

@pytest.fixture
def sem_tesseract(monkeypatch):
    """O PaddleOCR presente e o Tesseract sumido; liga e desliga no meio."""
    class Estado:
        tesseract = False
    monkeypatch.setattr(motor_paddleocr, "presente", lambda: True)
    monkeypatch.setattr(
        motor_na_tela, "localizar_tesseract",
        lambda: Path(r"C:\Qualquer\tesseract.exe") if Estado.tesseract else None)
    monkeypatch.setattr(motor_na_tela, "ha_algum_tesseract", lambda: False)
    monkeypatch.setattr(motor_na_tela, "localizar_instalador", lambda: None)
    return Estado


@pytest.mark.parametrize("modulo", ["gerar_ocr", "anonimizar"])
def test_tesseract_lembrado_que_sumiu_passa_a_ser_o_paddleocr(
        sem_tesseract, preferencias_isoladas, modulo):
    """Critério de aceite da RN-37: abre com o PaddleOCR marcado e a linha do
    Tesseract apagada, e o arquivo passa a dizer paddleocr para o módulo; o
    outro módulo fica como estava."""
    outro = "anonimizar" if modulo == "gerar_ocr" else "gerar_ocr"
    preferencias_isoladas.write_text(
        f"[{modulo}]\nmotor = tesseract\n[{outro}]\nmotor = tesseract\n",
        encoding="utf-8")

    painel = PainelOcr() if modulo == "gerar_ocr" else PainelAnonimizar()
    escolha = (painel.escolha_do_motor if modulo == "gerar_ocr"
               else _do_anonimizar(painel))
    assert escolha.marcado() == leitura.MOTOR_PADDLEOCR
    assert not escolha.tesseract.isEnabled()
    assert _lido(preferencias_isoladas) == {
        modulo: {"motor": "paddleocr"}, outro: {"motor": "tesseract"}}


@pytest.mark.parametrize("modulo", ["gerar_ocr", "anonimizar"])
def test_o_tesseract_que_volta_nao_e_remarcado_sozinho(
        sem_tesseract, preferencias_isoladas, modulo):
    """Critério de aceite da RN-37: quando o Tesseract volta, o módulo continua
    com o PaddleOCR - com o programa aberto e na próxima vez que abrir."""
    def escolha_de(painel):
        return (painel.escolha_do_motor if modulo == "gerar_ocr"
                else _do_anonimizar(painel))
    novo = PainelOcr if modulo == "gerar_ocr" else PainelAnonimizar

    preferencias_isoladas.write_text(f"[{modulo}]\nmotor = tesseract\n", encoding="utf-8")
    painel = novo()
    sem_tesseract.tesseract = True
    painel.motor.conferir_de_novo()
    assert escolha_de(painel).tesseract.isEnabled()
    assert escolha_de(painel).marcado() == leitura.MOTOR_PADDLEOCR
    assert escolha_de(novo()).marcado() == leitura.MOTOR_PADDLEOCR
    assert _lido(preferencias_isoladas) == {modulo: {"motor": "paddleocr"}}


def test_faltando_os_dois_nada_muda_no_que_esta_lembrado(monkeypatch, preferencias_isoladas):
    """RN-37: sem motor nenhum, não há para onde a marca passar."""
    monkeypatch.setattr(motor_paddleocr, "presente", lambda: False)
    monkeypatch.setattr(motor_na_tela, "localizar_tesseract", lambda: None)
    monkeypatch.setattr(motor_na_tela, "ha_algum_tesseract", lambda: False)
    monkeypatch.setattr(motor_na_tela, "localizar_instalador", lambda: None)
    preferencias_isoladas.write_text(
        "[gerar_ocr]\nmotor = tesseract\n[anonimizar]\nmotor = tesseract\n",
        encoding="utf-8")
    antes = preferencias_isoladas.read_bytes()
    PainelOcr()
    PainelAnonimizar()
    assert preferencias_isoladas.read_bytes() == antes


def test_paddleocr_lembrado_que_sumiu_passa_a_ser_o_tesseract(monkeypatch, preferencias_isoladas):
    """RN-37, o outro lado: lembrado o padrão e faltando os modelos, a marca
    vai para o Tesseract e ele passa a ser o lembrado."""
    monkeypatch.setattr(motor_paddleocr, "presente", lambda: False)
    monkeypatch.setattr(motor_na_tela, "localizar_tesseract",
                        lambda: Path(r"C:\Qualquer\tesseract.exe"))
    monkeypatch.setattr(motor_na_tela, "localizar_instalador", lambda: None)
    preferencias_isoladas.write_text("[anonimizar]\nmotor = paddleocr\n", encoding="utf-8")
    assert _do_anonimizar(PainelAnonimizar()).marcado() == leitura.MOTOR_TESSERACT
    assert _lido(preferencias_isoladas) == {"anonimizar": {"motor": "tesseract"}}


def test_pasta_sem_gravacao_le_com_o_tesseract_ate_fechar(maquina, tmp_path, monkeypatch):
    """Critério de aceite: a pasta não aceita gravar, a pessoa marca o
    Tesseract, e é ele que lê até fechar - sem aviso."""
    sem_pasta = tmp_path / "pasta-que-nao-existe" / "preferencias.ini"
    monkeypatch.setattr(preferencias, "caminho", lambda: sem_pasta)
    for painel, escolha in ((p := PainelOcr(), p.escolha_do_motor),
                            (a := PainelAnonimizar(), _do_anonimizar(a))):
        escolha.tesseract.setChecked(True)
        assert escolha.marcado() == leitura.MOTOR_TESSERACT
        assert painel.motor.aviso.isHidden()
    assert not sem_pasta.exists()

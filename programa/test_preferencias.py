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
    texto_de_verdade = Path.read_text

    def preso(caminho, *a, **k):
        if caminho == preferencias_isoladas:
            raise PermissionError("preso pelo antivírus")
        return texto_de_verdade(caminho, *a, **k)
    monkeypatch.setattr(Path, "read_text", preso)
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    monkeypatch.undo()

    assert preferencias_isoladas.read_bytes() == antes


def test_arquivo_salvo_com_bom_e_editado_a_mao_e_entendido(preferencias_isoladas):
    """Regressão da lente crítica da etapa 1: o "UTF-8 com BOM" do Bloco de
    Notas contava como estragado, e "Tesseract" com maiúscula era ignorado."""
    preferencias_isoladas.write_bytes(
        "\ufeff[gerar_ocr]\nmotor =  Tesseract \n".encode("utf-8"))
    assert preferencias.ler("gerar_ocr", "motor") == "tesseract"


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
    anonimizar = PainelAnonimizar()
    assert anonimizar.pdf.tela_de_ler.escolha_do_motor.marcado() == leitura.MOTOR_PADDLEOCR

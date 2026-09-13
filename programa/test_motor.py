"""Testes de onde o programa procura o motor de leitura, e do que faz sem ele.

Nenhum destes testes esconde o Tesseract desta máquina de verdade: eles montam
pastas de mentira numa pasta temporária, com um arquivo vazio chamado
tesseract.exe. Para o programa, basta o arquivo estar lá - quem confere se ele
funciona é a leitura, testada em test_leitura.py.
"""
from pathlib import Path

import pytest

import configuracao
import motor


@pytest.fixture(autouse=True)
def sem_pasta_apontada():
    """A pasta apontada vive na memória do programa: cada teste começa sem ela."""
    motor.esquecer_pasta_apontada()
    yield
    motor.esquecer_pasta_apontada()


@pytest.fixture
def maquina_sem_tesseract(monkeypatch):
    """Uma máquina onde o programa não acha o Tesseract em lugar nenhum."""
    monkeypatch.setattr(motor, "valor_do_env", lambda _nome: None)
    monkeypatch.setattr(motor.shutil, "which", lambda _nome: None)
    monkeypatch.setattr(motor, "PASTAS_DE_COSTUME", [])
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.delenv("TESSDATA_PREFIX", raising=False)


def _tesseract_de_mentira(pasta, com_portugues=True):
    pasta.mkdir(parents=True, exist_ok=True)
    executavel = pasta / "tesseract.exe"
    executavel.write_bytes(b"")
    if com_portugues:
        (pasta / "tessdata").mkdir(exist_ok=True)
        (pasta / "tessdata" / "por.traineddata").write_bytes(b"")
    return executavel


# ------------------------------------------------------------------- o .env


def test_o_valor_do_env_e_lido(tmp_path, monkeypatch):
    monkeypatch.setattr(configuracao, "pasta_do_programa", lambda: tmp_path)
    (tmp_path / ".env").write_text(
        "# comentário que não conta\n"
        "LLM_REMOTA_URL=\n"
        'TESSERACT_CAMINHO="D:\\Programas TI\\Tesseract-OCR"\n',
        encoding="utf-8",
    )

    # As aspas são o jeito comum de escrever caminho com espaço, e não fazem
    # parte do caminho.
    assert configuracao.valor_do_env("TESSERACT_CAMINHO") == r"D:\Programas TI\Tesseract-OCR"


def test_valor_em_branco_conta_como_nao_preenchido(tmp_path, monkeypatch):
    """É assim que a variável vem no .env.example - e o programa procura sozinho."""
    monkeypatch.setattr(configuracao, "pasta_do_programa", lambda: tmp_path)
    (tmp_path / ".env").write_text("TESSERACT_CAMINHO=\n", encoding="utf-8")

    assert configuracao.valor_do_env("TESSERACT_CAMINHO") is None


@pytest.mark.parametrize("formato", ["utf-8", "utf-8-sig", "utf-16", "cp1252"])
def test_o_env_e_lido_nos_formatos_que_o_bloco_de_notas_grava(tmp_path, monkeypatch,
                                                              formato):
    """Teste de regressão do achado 1 da revisão da etapa 7.

    O .env.example tem acento nos comentários. Salvo em "Unicode" ou "ANSI" no
    Bloco de Notas, o .env derrubava o programa ao abrir, sem janela e sem
    mensagem - mesmo com o Tesseract no lugar de sempre.
    """
    monkeypatch.setattr(configuracao, "pasta_do_programa", lambda: tmp_path)
    (tmp_path / ".env").write_text(
        "# Preenchido, o aviso deixa de aparecer nesta máquina.\n"
        "TESSERACT_CAMINHO=D:\\Programas\\Tesseract-OCR\n",
        encoding=formato,
    )

    assert configuracao.valor_do_env("TESSERACT_CAMINHO") == r"D:\Programas\Tesseract-OCR"


def test_env_ilegivel_segue_como_se_nao_houvesse(tmp_path, monkeypatch):
    monkeypatch.setattr(configuracao, "pasta_do_programa", lambda: tmp_path)
    # Bytes que não formam texto em nenhum dos formatos aceitos.
    (tmp_path / ".env").write_bytes(b"TESSERACT_CAMINHO=\x81\x8d\x8f\x90\x9d\n")

    assert configuracao.valor_do_env("TESSERACT_CAMINHO") is None


def test_env_em_unicode_nao_impede_o_programa_de_abrir(tmp_path, monkeypatch):
    """O cenário do achado 1 inteiro: era aqui, montando o painel, que estourava."""
    import painel_ocr

    monkeypatch.setattr(configuracao, "pasta_do_programa", lambda: tmp_path)
    (tmp_path / ".env").write_text(
        "# máquina\nTESSERACT_CAMINHO=\n", encoding="utf-16"
    )

    painel_ocr.PainelOcr()


def test_sem_env_nenhum_nao_da_erro(tmp_path, monkeypatch):
    """Máquina sem .env é o caso comum, e não pode derrubar o programa."""
    monkeypatch.setattr(configuracao, "pasta_do_programa", lambda: tmp_path)

    assert configuracao.valor_do_env("TESSERACT_CAMINHO") is None


# ------------------------------------------------------- procurar o motor


def test_sem_tesseract_em_lugar_nenhum_a_resposta_e_nenhum(maquina_sem_tesseract):
    assert motor.localizar_tesseract() is None


def test_a_pasta_escrita_no_env_pela_ti_e_usada(tmp_path, monkeypatch,
                                                 maquina_sem_tesseract):
    """RN-19: a TI grava o caminho uma vez, e o aviso some naquela máquina."""
    executavel = _tesseract_de_mentira(tmp_path / "Tesseract da TI")
    monkeypatch.setattr(motor, "valor_do_env", lambda _nome: str(executavel.parent))

    assert motor.localizar_tesseract() == executavel


def test_o_env_pode_trazer_o_proprio_executavel(tmp_path, monkeypatch,
                                                maquina_sem_tesseract):
    executavel = _tesseract_de_mentira(tmp_path / "OCR")
    monkeypatch.setattr(motor, "valor_do_env", lambda _nome: str(executavel))

    assert motor.localizar_tesseract() == executavel


def test_as_pastas_de_costume_sao_procuradas(tmp_path, monkeypatch,
                                             maquina_sem_tesseract):
    executavel = _tesseract_de_mentira(tmp_path / "Tesseract-OCR")
    monkeypatch.setattr(motor, "PASTAS_DE_COSTUME", [executavel.parent])

    assert motor.localizar_tesseract() == executavel


def test_tesseract_sem_portugues_nao_conta_como_encontrado(tmp_path, monkeypatch,
                                                           maquina_sem_tesseract):
    """Teste de regressão do achado 2 da revisão da etapa 7 (RN-19).

    Instalado sem o português, o aviso sumia e toda leitura de documento
    escaneado falhava na primeira página, com um "tentar de novo" que nunca ia
    dar certo.
    """
    executavel = _tesseract_de_mentira(tmp_path / "OCR", com_portugues=False)
    monkeypatch.setattr(motor, "PASTAS_DE_COSTUME", [executavel.parent])

    assert motor.localizar_tesseract() is None
    assert motor.ha_tesseract_sem_portugues() is True


def test_sem_tesseract_nenhum_nao_e_caso_de_pacote_faltando(maquina_sem_tesseract):
    assert motor.ha_tesseract_sem_portugues() is False


def test_um_tesseract_sem_portugues_nao_esconde_um_bom(tmp_path, monkeypatch,
                                                       maquina_sem_tesseract):
    incompleto = _tesseract_de_mentira(tmp_path / "velho", com_portugues=False)
    completo = _tesseract_de_mentira(tmp_path / "novo")
    monkeypatch.setattr(motor, "PASTAS_DE_COSTUME",
                        [incompleto.parent, completo.parent])

    assert motor.localizar_tesseract() == completo


def test_a_pasta_de_idiomas_escolhida_pela_ti_e_respeitada(tmp_path, monkeypatch,
                                                           maquina_sem_tesseract):
    """Com TESSDATA_PREFIX, é lá - e só lá - que o Tesseract procura os idiomas."""
    executavel = _tesseract_de_mentira(tmp_path / "OCR", com_portugues=False)
    idiomas = tmp_path / "idiomas da TI"
    idiomas.mkdir()
    (idiomas / "por.traineddata").write_bytes(b"")
    monkeypatch.setattr(motor, "PASTAS_DE_COSTUME", [executavel.parent])
    monkeypatch.setenv("TESSDATA_PREFIX", str(idiomas))

    assert motor.localizar_tesseract() == executavel


# --------------------------------------------------------- apontar a pasta


def test_apontar_uma_pasta_sem_tesseract_nao_e_guardado(tmp_path,
                                                         maquina_sem_tesseract):
    """Guardar a pasta errada faria o programa procurar no lugar errado calado."""
    assert motor.apontar_pasta(tmp_path) is False
    assert motor.localizar_tesseract() is None


def test_apontar_a_pasta_certa_faz_o_motor_aparecer(tmp_path,
                                                    maquina_sem_tesseract):
    executavel = _tesseract_de_mentira(tmp_path / "OCR")

    assert motor.apontar_pasta(executavel.parent) is True
    assert motor.localizar_tesseract() == executavel


def test_a_pasta_apontada_nao_e_gravada_em_lugar_nenhum(tmp_path, monkeypatch,
                                                        maquina_sem_tesseract):
    """RN-22: nada é guardado entre um uso e outro. Apontar vale só na memória."""
    monkeypatch.setattr(configuracao, "pasta_do_programa", lambda: tmp_path)
    executavel = _tesseract_de_mentira(tmp_path / "OCR")
    antes = sorted(p.name for p in tmp_path.rglob("*"))

    motor.apontar_pasta(executavel.parent)

    assert sorted(p.name for p in tmp_path.rglob("*")) == antes


# ---------------------------------------------------------- o instalador


def test_o_instalador_e_achado_na_pasta_instaladores(tmp_path, monkeypatch):
    monkeypatch.setattr(motor, "pasta_do_programa", lambda: tmp_path)
    pasta = tmp_path / "instaladores"
    pasta.mkdir()
    (pasta / "leia-me.txt").write_text("outra coisa", encoding="utf-8")
    (pasta / "outro-programa.exe").write_bytes(b"")
    instalador = pasta / "tesseract-ocr-w64-setup-5.4.0.exe"
    instalador.write_bytes(b"")

    assert motor.localizar_instalador() == instalador


def test_sem_a_pasta_instaladores_nao_ha_instalador(tmp_path, monkeypatch):
    monkeypatch.setattr(motor, "pasta_do_programa", lambda: tmp_path)

    assert motor.localizar_instalador() is None


def test_pasta_instaladores_sem_o_do_tesseract_nao_serve(tmp_path, monkeypatch):
    monkeypatch.setattr(motor, "pasta_do_programa", lambda: tmp_path)
    (tmp_path / "instaladores").mkdir()
    (tmp_path / "instaladores" / "outro-programa.exe").write_bytes(b"")

    assert motor.localizar_instalador() is None


# ------------------------------------------------------- nada sai daqui


@pytest.mark.parametrize("modulo", ["motor.py", "configuracao.py", "telas_do_motor.py"])
def test_os_arquivos_do_motor_nao_falam_com_a_internet(modulo):
    """Critério de aceite 22, sobre os arquivos novos da etapa 7.

    O instalador é aberto da própria máquina, nunca baixado (RN-20). Se alguém
    um dia acrescentar um endereço ou uma chamada de rede aqui, este teste cai.
    """
    codigo = (Path(__file__).parent / modulo).read_text(encoding="utf-8").lower()

    for proibido in ["http", "www.", "requests", "urllib", "socket", "download"]:
        assert proibido not in codigo, (
            f"apareceu '{proibido}' em {modulo} - o programa não baixa nada e "
            "não fala com a internet"
        )

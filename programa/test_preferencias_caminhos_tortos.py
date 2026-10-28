"""Os caminhos tortos da lembrança, com o programa inteiro (etapa 4 da
funcionalidade 8): o `.env` da TI intacto, o arquivo morando ao lado dele, nada
do trabalho guardado, e o arquivo estragado ou a pasta sem gravação sem
atrapalhar nada (emendas de 28/10/2026 das specs 002 e 001, RN-38 a RN-40).

Aqui a "instalação" é uma pasta provisória com um `.env` de mentira: o
`preferencias.ini` volta a ser procurado onde o programa de verdade o procura,
ao lado do `.env`, e não no arquivo isolado de cada teste.
"""
import re
import shutil
from pathlib import Path

import pytest

import configuracao
import documento
import leitura
import motor_na_tela
import motor_paddleocr
import preferencias
from main import JanelaPrincipal

# Guardado antes de qualquer teste rodar: o conftest troca o lugar do arquivo
# em cada teste, e aqui é o lugar de verdade que está em teste.
CAMINHO_DE_VERDADE = preferencias.caminho

RAIZ = Path(__file__).parent.parent
MASSA = RAIZ / "dados-exemplo"

# Um .env como a TI deixa: comentários com acento, linha em branco, valor com
# aspas, e a quebra de linha do Windows - tudo o que uma regravação mudaria.
ENV_DA_TI = (
    "# Configuração desta máquina — preenchida pela TI em 28/10/2026.\r\n"
    "# Não apague: o caminho do Tesseract instalado fora do lugar de sempre.\r\n"
    "\r\n"
    'TESSERACT_CAMINHO="C:\\Programas da TI\\Tesseract-OCR"\r\n'
).encode("utf-8")


@pytest.fixture
def instalacao(tmp_path, monkeypatch):
    """Uma pasta de instalação com o .env da TI, e os dois motores presentes."""
    pasta = tmp_path / "Anonimizador CAPCF"
    pasta.mkdir()
    (pasta / ".env").write_bytes(ENV_DA_TI)
    monkeypatch.setattr(configuracao, "pasta_do_programa", lambda: pasta)
    monkeypatch.setattr(preferencias, "caminho", CAMINHO_DE_VERDADE)
    monkeypatch.setattr(motor_paddleocr, "presente", lambda: True)
    monkeypatch.setattr(motor_na_tela, "localizar_tesseract",
                        lambda: Path(r"C:\Programas da TI\Tesseract-OCR\tesseract.exe"))
    monkeypatch.setattr(motor_na_tela, "localizar_instalador", lambda: None)
    # A trava: se a pasta de mentira não pegasse, os testes daqui gravariam no
    # preferencias.ini da raiz do projeto.
    assert preferencias.caminho().parent == pasta
    return pasta


def _marcar_e_fechar(janela):
    janela.painel_ocr.escolha_do_motor.tesseract.setChecked(True)
    do_anonimizar = janela.painel_anonimizar.pdf.tela_de_ler.escolha_do_motor
    do_anonimizar.tesseract.setChecked(True)
    do_anonimizar.paddleocr.setChecked(True)
    janela.close()


def test_o_arquivo_mora_ao_lado_do_env_e_nunca_na_raiz_do_projeto(instalacao):
    """RN-38, e a premissa dos testes isolados: nesta instalação de mentira o
    arquivo é o dela, e não o desta máquina."""
    assert preferencias.caminho() == instalacao / "preferencias.ini"
    _marcar_e_fechar(JanelaPrincipal())
    assert sorted(p.name for p in instalacao.iterdir()) == [".env", "preferencias.ini"]


def test_o_env_da_ti_fica_identico_byte_a_byte(instalacao):
    """Critério de aceite da spec 002: o programa só lê o .env."""
    _marcar_e_fechar(JanelaPrincipal())
    _marcar_e_fechar(JanelaPrincipal())
    assert (instalacao / ".env").read_bytes() == ENV_DA_TI


def test_depois_de_um_uso_com_documentos_o_arquivo_so_tem_as_escolhas(
        instalacao, tmp_path):
    """RN-40 e critério de aceite: um uso inteiro - um PDF conferido no Gerar
    OCR, seguido para o Anonimizar e salvo -, e o arquivo tem só os motores e
    a janela. Nenhum nome de documento, pasta, texto ou data."""
    pdf = tmp_path / "prestacao-de-contas-da-fundacao.pdf"
    shutil.copy(MASSA / "01-com-texto-e-tabela.pdf", pdf)

    janela = JanelaPrincipal()
    janela.menu.botao_ocr.click()
    ocr = janela.painel_ocr
    ficha = documento.conferir(pdf)
    ocr.ficha_atual = ficha
    ocr.aproveitar_o_texto_existente(ficha, documento.texto_da_camada(pdf))
    ocr.tela_conferencia.botao_conferido.click()
    ocr.tela_saida.botao_anonimizar.click()
    anonimizar = janela.painel_anonimizar
    anonimizar.abrir_o_salvar()
    salvo = Path(anonimizar.tela_salvar.campo.text())
    anonimizar.gravar(salvo)
    assert salvo.exists()
    _marcar_e_fechar(janela)

    lembrado = preferencias._conteudo()
    assert {secao: set(lembrado[secao]) for secao in lembrado.sections()} == {
        "gerar_ocr": {"motor"},
        "anonimizar": {"motor"},
        "janela": {"largura", "altura", "maximizada"},
    }
    texto = (instalacao / "preferencias.ini").read_text(encoding="utf-8")
    sem_o_cabecalho = "\n".join(
        linha for linha in texto.splitlines() if not linha.startswith("#"))
    for o_que_nao_pode in ("prestacao", "fundacao", ".pdf", ".md", "\\", "/",
                           str(tmp_path), "2026"):
        assert o_que_nao_pode not in sem_o_cabecalho
    assert not re.search(r"\d{3}\.\d{3}", sem_o_cabecalho)


def test_arquivo_estragado_abre_no_padrao_e_e_refeito(instalacao):
    """Critério de aceite: lixo no arquivo, o programa abre como no primeiro
    uso - os dois módulos no PaddleOCR, a janela maximizada -, sem erro; e a
    próxima escolha grava um arquivo certo."""
    arquivo = instalacao / "preferencias.ini"
    arquivo.write_bytes(b"\x00\xff lixo [janela\nlargura = \x9d\n")
    janela = JanelaPrincipal()
    assert janela.abre_maximizada
    assert janela.painel_ocr.escolha_do_motor.marcado() == leitura.MOTOR_PADDLEOCR
    assert (janela.painel_anonimizar.pdf.tela_de_ler.escolha_do_motor.marcado()
            == leitura.MOTOR_PADDLEOCR)
    janela.painel_ocr.escolha_do_motor.tesseract.setChecked(True)
    assert preferencias._conteudo().sections() == ["gerar_ocr"]


def test_arquivo_apagado_volta_ao_primeiro_uso(instalacao):
    _marcar_e_fechar(JanelaPrincipal())
    (instalacao / "preferencias.ini").unlink()
    janela = JanelaPrincipal()
    assert janela.abre_maximizada
    assert janela.painel_ocr.escolha_do_motor.marcado() == leitura.MOTOR_PADDLEOCR


def test_pasta_sem_gravacao_nao_atrapalha_marcar_nem_fechar(instalacao, monkeypatch):
    """RN-39: a pasta ficou protegida. Marcar e fechar seguem sem erro e sem
    aviso, e o .env continua intacto."""
    def recusa(*a, **k):
        raise PermissionError("pasta protegida")
    monkeypatch.setattr(preferencias, "open", recusa, raising=False)
    janela = JanelaPrincipal()
    janela.painel_ocr.escolha_do_motor.tesseract.setChecked(True)
    assert janela.painel_ocr.escolha_do_motor.marcado() == leitura.MOTOR_TESSERACT
    janela.close()
    assert sorted(p.name for p in instalacao.iterdir()) == [".env"]
    assert (instalacao / ".env").read_bytes() == ENV_DA_TI


def test_o_gitignore_cobre_o_arquivo_e_o_provisorio():
    """Critério de aceite: a escolha desta máquina fica fora do histórico."""
    linhas = (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "preferencias.ini" in linhas
    assert "preferencias.ini.*.gravando" in linhas


# ------------------------------------------------- o instalador (etapa 5)


def _secoes_do_instalador():
    """As seções da receita do instalador, cada uma com as linhas que não são
    comentário."""
    receita = (RAIZ / "empacotar" / "instalador.iss").read_text(encoding="utf-8-sig")
    secoes, atual = {}, None
    for linha in receita.splitlines():
        linha = linha.strip()
        if not linha or linha.startswith(";"):
            continue
        if linha.startswith("[") and linha.endswith("]"):
            atual = secoes.setdefault(linha[1:-1], [])
        elif atual is not None:
            atual.append(linha)
    return secoes


def test_desinstalar_apaga_o_arquivo_e_o_provisorio():
    """RN-41: o desinstalador só apaga o que o instalador pôs, e o arquivo é o
    programa quem cria - por isso ele precisa estar na lista de apagar."""
    apagar = _secoes_do_instalador().get("UninstallDelete", [])
    assert r'Type: files; Name: "{app}\preferencias.ini"' in apagar
    assert r'Type: files; Name: "{app}\preferencias.ini.*.gravando"' in apagar


def test_atualizar_mantem_o_arquivo():
    """RN-41: instalar uma versão nova por cima não traz nem apaga o arquivo.

    "Não traz" inclui a pasta do programa montada, que entra inteira: um
    preferencias.ini deixado nela (o programa montado aberto ali mesmo, para
    testar) iria dentro do instalador e passaria por cima da escolha de quem
    atualiza (lente crítica da etapa 5)."""
    secoes = _secoes_do_instalador()
    assert not any("preferencias" in linha for linha in secoes.get("InstallDelete", []))
    for linha in secoes["Files"]:
        if "preferencias" in linha:
            assert 'Excludes: "preferencias.ini,preferencias.ini.*.gravando"' in linha
    pasta_inteira = [linha for linha in secoes["Files"] if "{#Nome}\\*" in linha]
    assert pasta_inteira
    for linha in pasta_inteira:
        assert 'Excludes: "preferencias.ini,preferencias.ini.*.gravando"' in linha

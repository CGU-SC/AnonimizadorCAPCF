"""O único arquivo que fala com a rede, contra um servidor de mentira nesta máquina.

Nenhum destes testes depende de um LM Studio ou de um servidor de verdade (RN-45).
"""
import ast
import subprocess
import sys
from pathlib import Path

import pytest

import rede_da_ia

PROGRAMA = Path(__file__).parent

SINAIS_DE_REDE = ("http", "socket", "urllib", "requests", "ftplib")


def test_so_um_arquivo_do_programa_tem_sinal_de_rede():
    """RN-44: varre todo arquivo do programa, e não só os que o Anonimizar importa."""
    for arquivo in PROGRAMA.glob("*.py"):
        if arquivo.name.startswith(("test_", "conftest")) or arquivo.name == "rede_da_ia.py":
            continue
        codigo = arquivo.read_text(encoding="utf-8").lower()
        # O caminho dos arquivos do Word que o programa nunca visita (test_cpf.py).
        codigo = codigo.replace("http://schemas.openxmlformats.org/", "")
        for sinal in SINAIS_DE_REDE:
            assert sinal not in codigo, f"{arquivo.name}: {sinal}"


def test_o_arquivo_da_rede_nao_baixa_nada_nem_conhece_endereco_de_fora():
    import re
    codigo = (PROGRAMA / "rede_da_ia.py").read_text(encoding="utf-8")
    assert "www." not in codigo
    # Com ponto no nome ou número: é o jeito de um endereço de verdade estar escrito.
    enderecos = re.findall(r"https?://[0-9a-z-]+[.][0-9a-z.-]+", codigo)
    assert set(enderecos) == {"http://127.0.0.1"}, enderecos
    arvore = ast.parse(codigo)
    nomes = {no.name for no in ast.walk(arvore)
             if isinstance(no, (ast.FunctionDef, ast.ClassDef))}
    assert not any("baixar" in n or "download" in n for n in nomes)


def test_com_a_ia_desligada_o_arquivo_da_rede_nem_e_carregado():
    """RN-43: abre o programa inteiro em outro processo e olha o que foi carregado."""
    roteiro = (
        "import sys;"
        "from PySide6.QtWidgets import QApplication;"
        "app = QApplication([]);"
        "import main;"
        "janela = main.JanelaPrincipal();"
        "print('rede_da_ia' in sys.modules, 'http.client' in sys.modules)"
    )
    resultado = subprocess.run([sys.executable, "-c", roteiro], cwd=PROGRAMA,
                               capture_output=True, text=True, timeout=120)
    assert "False" in resultado.stdout.split()[0], resultado.stdout + resultado.stderr


_ROTEIRO_DO_CAMINHO_INTEIRO = """
import socket, sys, tempfile
from pathlib import Path
import configuracao
pasta = Path(tempfile.mkdtemp())
configuracao.pasta_do_programa = lambda: pasta
conexoes = []
socket.socket.connect = lambda self, *a: conexoes.append(a)
socket.getaddrinfo = lambda *a, **k: conexoes.append(a) or []
from PySide6.QtWidgets import QApplication
app = QApplication([])
import main
janela = main.JanelaPrincipal()
janela.show()
janela.menu.botao_anonimizar.click()
painel = janela.painel_anonimizar
painel.receber_arquivo(Path(sys.argv[1]))
painel.abrir_o_salvar()
painel.gravar(pasta / "saida.md")
assert (pasta / "saida.md").exists()
janela.menu.botao_ocr.click()
janela.close()
print("CARREGOU" if "rede_da_ia" in sys.modules else "NAO_CARREGOU", len(conexoes))
"""


def test_com_a_ia_desligada_o_caminho_inteiro_nao_abre_conexao():
    """RN-43: do arquivo ao .md gravado, e não só ao abrir o programa."""
    documento = PROGRAMA.parent / "dados-exemplo" / "30-revisao-por-ia.md"
    resultado = subprocess.run(
        [sys.executable, "-c", _ROTEIRO_DO_CAMINHO_INTEIRO, str(documento)],
        cwd=PROGRAMA, capture_output=True, text=True, timeout=120)
    assert resultado.stdout.split()[-2:] == ["NAO_CARREGOU", "0"], (
        resultado.stdout + resultado.stderr)


def test_com_a_ia_ligada_abrir_o_programa_nao_abre_conexao(monkeypatch):
    """RN-8: a primeira conexão só vem quando a pessoa pede."""
    import config_ia
    from main import JanelaPrincipal
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, modelo_revisora="m", modelo_motor="m")
    config_ia.marcar_testado(config_ia.LM_STUDIO, True)
    config_ia.marcar_motor_testado(config_ia.LM_STUDIO, True)
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    config_ia.ligar_geral()
    conexoes = []
    monkeypatch.setattr(rede_da_ia.socket.socket, "connect",
                        lambda self, *a: conexoes.append(a))
    janela = JanelaPrincipal()
    janela.show()
    janela.close()
    assert conexoes == []


def test_lista_os_modelos_e_diz_quais_leem_imagem(servidor):
    modelos = rede_da_ia.listar_modelos(servidor.base)
    assert [m.nome for m in modelos] == ["modelo-exemplo-texto-8b", "modelo-exemplo-visao-13b"]
    assert modelos[0].le_imagem is False and modelos[1].le_imagem is True
    assert modelos[0].carregado is True and modelos[1].carregado is False
    assert "carregado" in modelos[0].descricao() and "5,1 GB" in modelos[0].descricao()


def test_lista_antiga_traz_so_os_nomes(servidor):
    servidor.comportamento.so_lista_comum = True
    modelos = rede_da_ia.listar_modelos(servidor.base)
    # O de embedding sai também aqui: ele não conversa.
    assert [m.nome for m in modelos] == ["modelo-exemplo-texto-8b",
                                         "modelo-exemplo-visao-13b", "modelo-exemplo-busca"]
    assert modelos[0].le_imagem is None


def test_destino_que_nao_lista_devolve_none(servidor):
    servidor.comportamento.sem_lista = True
    assert rede_da_ia.listar_modelos(servidor.base) is None


def test_destino_fora_do_ar_da_falha_com_frase_pronta(servidor):
    base = servidor.base
    servidor.parar()
    with pytest.raises(rede_da_ia.FalhaDaIa) as falha:
        rede_da_ia.listar_modelos(base)
    assert str(falha.value) == rede_da_ia.NAO_RESPONDEU


def test_redirecionamento_nao_e_seguido(servidor):
    """RN-23: o destino final é sempre o que a pessoa viu."""
    servidor.comportamento.redirecionar = True
    with pytest.raises(rede_da_ia.FalhaDaIa) as falha:
        rede_da_ia.listar_modelos(servidor.base)
    assert str(falha.value) == rede_da_ia.REDIRECIONOU
    assert len(servidor.comportamento.pedidos) == 1


def test_o_teste_nao_leva_numero_nenhum(servidor):
    """RN-7: a frase do teste é inventada, sem nada do documento."""
    rede_da_ia.testar_modelo(servidor.base, None, "modelo")
    import json
    corpo = json.loads(servidor.comportamento.corpo_cru[0])
    assert not any(c.isdigit() for c in str(corpo["messages"]))


def test_a_imagem_do_teste_e_inventada_e_vale_como_imagem(servidor):
    from base64 import b64decode
    assert b64decode(rede_da_ia.imagem_de_teste()).startswith(b"\x89PNG")
    rede_da_ia.testar_modelo(servidor.base, None, "modelo", rede_da_ia.imagem_de_teste())
    assert "image_url" in servidor.comportamento.corpo_cru[0]


def test_token_vai_no_cabecalho_e_a_recusa_nao_o_repete(servidor):
    servidor.comportamento.token = "token-inventado-123"
    rede_da_ia.listar_modelos(servidor.base, "token-inventado-123")
    with pytest.raises(rede_da_ia.FalhaDaIa) as falha:
        rede_da_ia.listar_modelos(servidor.base, "errado-456")
    assert str(falha.value) == rede_da_ia.TOKEN_RECUSADO
    assert "errado-456" not in str(falha.value)


def test_erro_do_destino_nao_traz_o_que_ele_respondeu(servidor):
    servidor.comportamento.cair_no_pedido = 1
    with pytest.raises(rede_da_ia.FalhaDaIa) as falha:
        rede_da_ia.conversar(servidor.base, None, "m", [{"role": "user", "content": "x"}], 5)
    assert "caiu" not in str(falha.value)


def test_cancelar_corta_o_pedido_na_hora(servidor):
    import threading
    import time
    servidor.comportamento.demora = 5
    cancelador = rede_da_ia.Cancelador()
    resultado = []

    def pedir():
        try:
            rede_da_ia.conversar(servidor.base, None, "m",
                                 [{"role": "user", "content": "texto"}], 30, cancelador)
        except rede_da_ia.PedidoCancelado:
            resultado.append("cancelado")

    linha = threading.Thread(target=pedir)
    comeco = time.monotonic()
    linha.start()
    time.sleep(0.3)
    cancelador.cancelar()
    linha.join(4)
    assert resultado == ["cancelado"]
    assert time.monotonic() - comeco < 4


@pytest.mark.parametrize("endereco,espera", [
    ("http://localhost:1234", "É esta máquina."),
    ("127.0.0.1:1234", "É esta máquina."),
    ("http://[::1]:8000", "É esta máquina."),
    ("https://ia.ufsc.br", "É um nome da UFSC."),
    ("http://ufsc.br/ia", "É um nome da UFSC."),
    ("http://10.20.30.40:8000", "rede interna"),
    ("192.168.0.9", "rede interna"),
    ("http://172.16.5.5", "rede interna"),
])
def test_enderecos_reconhecidos(endereco, espera):
    avaliacao = rede_da_ia.avaliar_endereco(endereco)
    assert avaliacao.valido and avaliacao.reconhecido
    assert espera in avaliacao.por_que


@pytest.mark.parametrize("endereco", [
    "http://8.8.8.8",
    "http://172.32.0.1",
    "http://[::ffff:8.8.8.8]",
    # Parecidos com a UFSC, e de outro dono.
    "https://xufsc.br",
    "https://ufsc.br.exemplo.invalid",
    "http://0.0.0.0",
])
def test_enderecos_nao_reconhecidos(endereco):
    avaliacao = rede_da_ia.avaliar_endereco(endereco)
    assert avaliacao.valido and not avaliacao.reconhecido


def test_nome_que_da_em_numero_interno_e_reconhecido_e_externo_nao(monkeypatch):
    numeros = {"interno.instituicao.exemplo": "10.0.0.5",
               "misturado.instituicao.exemplo": "10.0.0.5",
               "externo.instituicao.exemplo": "8.8.8.8"}

    def resposta(host, _porta):
        saida = [(0, 0, 0, "", (numeros[host], 0))]
        if host.startswith("misturado"):
            saida.append((0, 0, 0, "", ("8.8.8.8", 0)))
        return saida

    monkeypatch.setattr(rede_da_ia.socket, "getaddrinfo", resposta)
    assert rede_da_ia.avaliar_endereco("http://interno.instituicao.exemplo").reconhecido
    assert not rede_da_ia.avaliar_endereco("http://externo.instituicao.exemplo").reconhecido
    # Um número só de fora já não é "rede interna".
    assert not rede_da_ia.avaliar_endereco("http://misturado.instituicao.exemplo").reconhecido


def test_nome_que_a_rede_nao_conhece_nao_e_reconhecido(monkeypatch):
    def nao_conhece(*_):
        raise OSError
    monkeypatch.setattr(rede_da_ia.socket, "getaddrinfo", nao_conhece)
    avaliacao = rede_da_ia.avaliar_endereco("http://sumido.instituicao.exemplo")
    assert avaliacao.valido and not avaliacao.reconhecido


def test_a_lista_do_env_vale_exato_e_por_terminacao(monkeypatch):
    def nao_conhece(*_):
        raise OSError
    monkeypatch.setattr(rede_da_ia.socket, "getaddrinfo", nao_conhece)
    locais = ["ia.instituicao.exemplo", ".outra.exemplo", "maquina.exemplo:8998"]
    for endereco in ("http://ia.instituicao.exemplo:80", "https://qualquer.outra.exemplo",
                     "http://maquina.exemplo:8998"):
        assert rede_da_ia.avaliar_endereco(endereco, locais).reconhecido, endereco
    for endereco in ("http://xia.instituicao.exemplo", "http://outra.exemplo",
                     "http://maquina.exemplo:9000"):
        assert not rede_da_ia.avaliar_endereco(endereco, locais).reconhecido, endereco


@pytest.mark.parametrize("endereco", ["", "ftp://ia.exemplo", "http://fulano:senha@ia.ufsc.br",
                                      "http://ufsc.br@ia.exemplo", "http://ia.exemplo:porta"])
def test_endereco_mal_escrito_nao_vale(endereco):
    assert not rede_da_ia.avaliar_endereco(endereco).valido


def test_http_e_marcado_como_sem_cifra():
    assert rede_da_ia.avaliar_endereco("http://10.0.0.1").sem_cifra
    assert not rede_da_ia.avaliar_endereco("https://10.0.0.1").sem_cifra


def test_a_base_tira_o_v1_e_a_barra():
    assert rede_da_ia.base_do_endereco(" 10.0.0.1:80/v1/ ") == "http://10.0.0.1:80"
    assert rede_da_ia.base_do_endereco("https://ia.ufsc.br/caminho") == "https://ia.ufsc.br/caminho"

"""Preparo comum a todos os testes, lido pelo pytest sozinho.

Existe por um motivo só, e é um motivo chato: rodando a lista inteira, todos os
testes passavam e mesmo assim o comando devolvia erro na saída. Quem olha só o
resultado do comando - uma pessoa com pressa, ou uma verificação automática -
concluiria que a lista falhou.

A causa é tela criada dentro de um teste e deixada para trás. Ela continua viva
até o Python fechar, e aí é desmontada depois de o Qt já ter sido desligado.
Desmontar cada uma no fim do teste que a criou resolve.
"""
import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

# O servidor de mentira mora em abrir/, e não em programa/: ele não faz parte do
# programa, e o instalador não o leva.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "abrir"))
from servidor_de_ia_de_mentira import ServidorDeMentira  # noqa: E402

# Guardada aqui fora de propósito: o Qt precisa continuar de pé até o fim da
# lista de testes, e uma variável dentro de função seria recolhida antes disso.
_aplicacao = None


@pytest.fixture(scope="session", autouse=True)
def aplicacao():
    """Sobe o Qt uma vez só, antes de tudo, e o mantém de pé até o fim.

    Nenhuma janela aparece: o Qt precisa existir para uma tela poder ser criada,
    mas ninguém manda mostrá-la.
    """
    global _aplicacao
    _aplicacao = QApplication.instance() or QApplication([])
    return _aplicacao


@pytest.fixture(autouse=True)
def preferencias_isoladas(tmp_path, monkeypatch):
    """Cada teste lembra as escolhas num arquivo só dele, numa pasta provisória.

    Sem isto, um teste que marca o Tesseract deixaria o seguinte começando com
    o Tesseract - e gravaria no `preferencias.ini` da raiz do projeto, o desta
    máquina, misturando teste com uso de verdade (emenda de 28/10/2026 da spec
    002, premissa dos testes isolados).
    """
    import preferencias
    arquivo = tmp_path / "preferencias-do-teste.ini"
    monkeypatch.setattr(preferencias, "caminho", lambda: arquivo)
    return arquivo


@pytest.fixture(autouse=True)
def env_isolado(tmp_path, monkeypatch):
    """O `.env` da raiz do projeto é o desta máquina, e o token vai para ele: teste
    nenhum pode lê-lo nem gravá-lo (RN-45 da spec 004). Quem aponta outra pasta,
    como os testes do motor, continua valendo."""
    import configuracao
    da_raiz = Path(__file__).resolve().parent.parent / ".env"
    caminho_de_verdade = configuracao.caminho_do_env

    def caminho():
        caminho_pedido = caminho_de_verdade()
        return tmp_path / ".env" if caminho_pedido == da_raiz else caminho_pedido

    monkeypatch.setattr(configuracao, "caminho_do_env", caminho)


@pytest.fixture(autouse=True)
def tema_escuro_depois():
    """O teste que monta telas no claro devolve o escuro ao terminar.

    O tema vale para o programa inteiro, e não para uma tela: esquecido no claro,
    ele passaria para os testes seguintes, que conferem as cores do escuro, e
    eles falhariam longe de quem causou (funcionalidade 10).
    """
    yield
    import estilo
    estilo.usar_tema(estilo.ESCURO)


@pytest.fixture(autouse=True)
def caixa_sem_resposta_falha(monkeypatch):
    """Uma caixa de aviso esperando resposta travaria a lista inteira, sem nada dizer.
    Assim, o teste que esqueceu de responder falha na hora, e diz qual caixa foi."""
    import avisos_da_ia

    def sem_resposta(titulo, *_, **__):
        raise AssertionError(f"caixa aberta sem resposta no teste: {titulo}")

    monkeypatch.setattr(avisos_da_ia, "exibir", sem_resposta)


@pytest.fixture
def servidor():
    """Um servidor de IA de mentira, numa porta livre desta máquina (RN-45 da spec 004)."""
    servidor = ServidorDeMentira()
    yield servidor
    servidor.parar()


@pytest.fixture
def outro_servidor():
    """Um segundo, para os testes de troca de destino."""
    servidor = ServidorDeMentira()
    yield servidor
    servidor.parar()


@pytest.fixture(autouse=True)
def limpar_as_telas(aplicacao):
    """Desmonta as telas criadas por cada teste, antes do teste seguinte."""
    yield
    for tela in aplicacao.topLevelWidgets():
        tela.deleteLater()
    aplicacao.processEvents()

"""Preparo comum a todos os testes, lido pelo pytest sozinho.

Existe por um motivo só, e é um motivo chato: rodando a lista inteira, todos os
testes passavam e mesmo assim o comando devolvia erro na saída. Quem olha só o
resultado do comando - uma pessoa com pressa, ou uma verificação automática -
concluiria que a lista falhou.

A causa é tela criada dentro de um teste e deixada para trás. Ela continua viva
até o Python fechar, e aí é desmontada depois de o Qt já ter sido desligado.
Desmontar cada uma no fim do teste que a criou resolve.
"""
import pytest
from PySide6.QtWidgets import QApplication

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
def limpar_as_telas(aplicacao):
    """Desmonta as telas criadas por cada teste, antes do teste seguinte."""
    yield
    for tela in aplicacao.topLevelWidgets():
        tela.deleteLater()
    aplicacao.processEvents()

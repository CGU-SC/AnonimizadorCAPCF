"""O "Reabrir agora" sem nada a perder (emenda de 05/11/2026 da spec 001, RN-24;
etapa 4 da funcionalidade 10). As perguntas antes de reabrir com uma leitura ou um
texto a perder são da etapa 6."""
import os
import sys

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

import estilo
import main
import preferencias
from main import LEMBRAR_COMO, TAMANHO_MINIMO, JanelaPrincipal
from tela_do_tema import NAO_DEU_PARA_REABRIR, REABRIR_AGORA, VALE_AO_REABRIR


@pytest.fixture
def pedidos(monkeypatch):
    """Troca o abrir de novo por um que só anota o tema pedido: o de verdade abriria
    outra cópia do programa no meio da lista de testes."""
    anotados = []

    def anotar(tema):
        anotados.append(tema)
        return True

    monkeypatch.setattr(main, "abrir_de_novo", anotar)
    return anotados


@pytest.fixture
def nao_abre(monkeypatch):
    """Finge que o Windows não deixou abrir a cópia nova."""
    monkeypatch.setattr(main, "abrir_de_novo", lambda tema: False)


@pytest.fixture
def janela():
    janela = JanelaPrincipal()
    janela.show()
    janela.menu.botao_config_ia.click()
    return janela


def _marcar_claro(janela):
    tela = janela.painel_ia.tela_tema
    tela.opcoes[estilo.CLARO].click()
    return tela


def test_o_botao_aparece_ao_lado_da_frase(janela, preferencias_isoladas):
    tela = _marcar_claro(janela)
    assert tela.aviso.frase.text() == VALE_AO_REABRIR
    assert tela.aviso.botao.text() == REABRIR_AGORA
    assert not tela.aviso.botao.isHidden()


def test_reabrir_pede_o_tema_marcado_e_fecha_a_janela(janela, preferencias_isoladas, pedidos):
    tela = _marcar_claro(janela)
    tela.aviso.botao.click()
    assert pedidos == [estilo.CLARO]
    assert not janela.isVisible()


def test_reabrir_grava_o_tamanho_antes_de_a_nova_abrir(janela, preferencias_isoladas,
                                                       monkeypatch):
    # A nova lê o tamanho assim que começa: ele já precisa estar gravado nessa hora.
    janela.showNormal()
    janela.resize(1100, 700)
    QApplication.processEvents()
    lido_pela_nova = []
    monkeypatch.setattr(main, "abrir_de_novo",
                        lambda tema: lido_pela_nova.append(preferencias.ler_bloco(LEMBRAR_COMO))
                        or True)
    _marcar_claro(janela).aviso.botao.click()
    assert lido_pela_nova[0]["largura"] == "1100"
    assert lido_pela_nova[0]["altura"] == "700"
    assert lido_pela_nova[0]["maximizada"] == main.NAO_MAXIMIZADA


def test_sem_gravacao_o_tema_vai_junto_com_o_pedido(janela, preferencias_isoladas, pedidos):
    preferencias_isoladas.mkdir()
    _marcar_claro(janela).aviso.botao.click()
    assert pedidos == [estilo.CLARO]


def test_nao_abrindo_a_janela_fica_e_diz_por_que(janela, preferencias_isoladas, nao_abre):
    tela = _marcar_claro(janela)
    tela.aviso.botao.click()
    assert janela.isVisible()
    assert tela.aviso.frase.text() == NAO_DEU_PARA_REABRIR
    assert tela.aviso.botao.isHidden()


def test_depois_da_falha_mudar_de_ideia_devolve_a_frase_e_o_botao(janela, preferencias_isoladas,
                                                                  nao_abre):
    tela = _marcar_claro(janela)
    tela.aviso.botao.click()
    tela.opcoes[estilo.ESCURO].click()
    tela.opcoes[estilo.CLARO].click()
    assert tela.aviso.frase.text() == VALE_AO_REABRIR
    assert not tela.aviso.botao.isHidden()


def test_na_janela_minima_o_botao_e_a_frase_da_falha_cabem(janela, preferencias_isoladas,
                                                           nao_abre):
    janela.showNormal()
    janela.resize(TAMANHO_MINIMO)
    tela = _marcar_claro(janela)
    QApplication.processEvents()
    for peca in (tela.aviso.frase, tela.aviso.botao):
        assert peca.width() >= peca.sizeHint().width(), peca.text()
    tela.aviso.botao.click()
    QApplication.processEvents()
    assert tela.aviso.frase.width() >= tela.aviso.frase.sizeHint().width()


def test_em_desenvolvimento_reabre_o_python_com_este_arquivo():
    programa, argumentos = main.comando_para_reabrir(estilo.CLARO)
    assert programa == sys.executable
    assert argumentos == [os.path.abspath(main.__file__), "--tema", "claro"]


def test_instalado_reabre_o_proprio_executavel(monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    programa, argumentos = main.comando_para_reabrir(estilo.ESCURO)
    assert programa == sys.executable
    assert argumentos == ["--tema", "escuro"]


def test_abrir_de_novo_solta_a_copia_nova(monkeypatch):
    chamados = []

    class _Processo:
        @staticmethod
        def startDetached(programa, argumentos, pasta):
            chamados.append((programa, argumentos, pasta))
            return True, 4242

    monkeypatch.setattr(main, "QProcess", _Processo)
    assert main.abrir_de_novo(estilo.CLARO) is True
    assert chamados == [(*main.comando_para_reabrir(estilo.CLARO), os.getcwd())]


@pytest.mark.parametrize("argumentos, tema", [
    (["main.py", "--tema", "claro"], "claro"),
    (["main.py", "--tema", "escuro"], "escuro"),
    (["main.py", "--tema", "azul"], None),
    (["main.py", "--tema"], None),
    (["main.py"], None),
])
def test_o_tema_pedido_so_vale_se_for_escuro_ou_claro(argumentos, tema):
    assert main.tema_pedido(argumentos) == tema


@pytest.fixture
def modo_do_windows(aplicacao):
    yield aplicacao.styleHints()
    aplicacao.styleHints().setColorScheme(Qt.ColorScheme.Unknown)


def test_o_tema_pedido_vale_mais_que_o_guardado(aplicacao, preferencias_isoladas,
                                                modo_do_windows):
    preferencias.gravar("aparencia", "tema", "escuro")
    assert main.usar_o_tema_lembrado(aplicacao, estilo.CLARO) == estilo.CLARO
    assert modo_do_windows.colorScheme() == Qt.ColorScheme.Light

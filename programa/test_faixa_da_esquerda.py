"""A faixa da esquerda redesenhada (emenda de 03/11/2026 da spec 001, RN-9 a RN-13)."""
import pytest
from PySide6.QtWidgets import QApplication, QLabel

from desenhos_da_faixa import SimboloDoPrograma
from main import TAMANHO_MINIMO, JanelaPrincipal
from versao import VERSAO


@pytest.fixture
def janela():
    return JanelaPrincipal()


def _cabecalho(janela):
    return janela.menu.nome.parentWidget()


def test_o_cabecalho_tem_o_simbolo_o_nome_e_a_versao(janela):
    cabecalho = _cabecalho(janela)
    assert cabecalho.findChildren(SimboloDoPrograma)
    assert janela.menu.nome.text() == "Anonimizador"
    assert janela.menu.versao.text() == f"CAPCF · versão {VERSAO}"


def test_a_versao_aparece_so_no_cabecalho(janela):
    """RN-10: no pé ela não volta, nem num texto solto em outro canto da faixa."""
    cabecalho = _cabecalho(janela)
    com_versao = [r for r in janela.menu.findChildren(QLabel) if VERSAO in r.text()]
    assert com_versao == [janela.menu.versao]
    assert janela.menu.versao.parentWidget() is cabecalho


def test_o_cabecalho_fica_parado_quando_o_submenu_entra(janela):
    """O submenu toma o lugar do menu (RN-2 da spec 004), e o cabeçalho fica fora
    da troca."""
    cabecalho = _cabecalho(janela)
    assert not janela.menu.paginas.isAncestorOf(cabecalho)
    janela.menu.botao_config_ia.click()
    assert janela.menu.paginas.currentWidget() is janela.menu.pagina_ia
    assert janela.menu.versao.text() == f"CAPCF · versão {VERSAO}"


def test_nada_do_cabecalho_sai_cortado_na_janela_minima(janela):
    """A faixa tem largura fixa, e o Qt espreme o texto em vez de avisar: cada
    texto precisa ter pelo menos a largura que pede ("O que já nos mordeu")."""
    janela.showNormal()
    janela.resize(TAMANHO_MINIMO)
    QApplication.processEvents()
    for rotulo in (janela.menu.nome, janela.menu.versao):
        assert rotulo.width() >= rotulo.sizeHint().width(), rotulo.text()

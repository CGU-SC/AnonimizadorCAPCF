"""A faixa da esquerda redesenhada (emenda de 03/11/2026 da spec 001, RN-9 a RN-13)."""
import pytest
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QLabel

from desenhos_da_faixa import TAMANHO_DO_ICONE, SimboloDoPrograma, icone_do_item
from estilo import COR_TEXTO, COR_TEXTO_SECUNDARIO
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


def test_nenhum_item_sai_cortado_na_janela_minima(janela):
    """Com o ícone, cada item pede mais largura; o do menu e o do submenu
    precisam caber nos 220 px da faixa, sem o Qt espremer o texto."""
    janela.showNormal()
    janela.resize(TAMANHO_MINIMO)
    QApplication.processEvents()
    menu = janela.menu
    for item in (menu.botao_ocr, menu.botao_anonimizar, menu.botao_config_ia):
        assert item.width() >= item.sizeHint().width(), item.text()
    menu.botao_config_ia.click()
    QApplication.processEvents()
    for item in (menu.botao_voltar_ia, *menu.itens_do_submenu):
        assert item.width() >= item.sizeHint().width(), item.text()


def test_cada_item_do_menu_principal_tem_o_seu_icone(janela):
    """RN-11: lupa, cadeado e engrenagem; o emoji de engrenagem saiu do texto."""
    menu = janela.menu
    for item in (menu.botao_ocr, menu.botao_anonimizar, menu.botao_config_ia):
        assert not item.icon().isNull(), item.text()
    assert menu.botao_config_ia.text() == "Configurações de IA"


def test_os_itens_do_submenu_continuam_so_texto(janela):
    for item in (janela.menu.botao_voltar_ia, *janela.menu.itens_do_submenu):
        assert item.icon().isNull(), item.text()


def _cor_do_traco(icone, estado):
    """A cor dos pontos totalmente opacos do desenho: a borda do traço é
    suavizada e mistura cor com transparência, o miolo não."""
    imagem = icone.pixmap(TAMANHO_DO_ICONE, QIcon.Normal, estado).toImage()
    cores = {
        imagem.pixelColor(x, y).name()
        for x in range(imagem.width()) for y in range(imagem.height())
        if imagem.pixelColor(x, y).alpha() == 255
    }
    assert len(cores) == 1, cores
    return cores.pop()


@pytest.mark.parametrize("desenho", ["lupa", "cadeado", "engrenagem"])
def test_o_icone_e_cinza_no_item_normal_e_claro_no_marcado(aplicacao, desenho):
    """RN-12: o ícone acompanha a cor do texto do item."""
    icone = icone_do_item(desenho)
    assert _cor_do_traco(icone, QIcon.Off) == COR_TEXTO_SECUNDARIO
    assert _cor_do_traco(icone, QIcon.On) == COR_TEXTO

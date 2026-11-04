"""A faixa da esquerda redesenhada (emenda de 03/11/2026 da spec 001, RN-9 a RN-13)."""
import pytest
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon
from PySide6.QtWidgets import QApplication, QLabel

from desenhos_da_faixa import TAMANHO_DO_ICONE, SimboloDoPrograma, icone_do_item
from estilo import (COR_DESTAQUE, COR_DESTAQUE_HOVER, COR_FUNDO_ELEVADO, COR_TEXTO,
                    COR_TEXTO_SECUNDARIO)
from main import LARGURA_DO_FILETE, TAMANHO_MINIMO, JanelaPrincipal
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


def _foto_da_faixa(janela):
    janela.showNormal()
    QApplication.processEvents()
    return janela.menu.grab().toImage()


def _cores_na_linha_do_item(foto, menu, item):
    """A cor do filete (logo depois da margem de 8 px) e a do fundo (perto da
    ponta direita, longe do texto), no meio da altura do item."""
    canto = item.mapTo(menu, item.rect().topLeft())
    y = canto.y() + item.height() // 2
    filete = foto.pixelColor(canto.x() + 8 + LARGURA_DO_FILETE // 2, y)
    fundo = foto.pixelColor(canto.x() + item.width() - 20, y)
    return filete, fundo


def _fundo_do_marcado_esperado():
    """O azul de destaque a 24% por cima do fundo da faixa."""
    azul, faixa = QColor(COR_DESTAQUE), QColor(COR_FUNDO_ELEVADO)
    return [round(0.24 * a + 0.76 * f) for a, f in
            ((azul.red(), faixa.red()), (azul.green(), faixa.green()),
             (azul.blue(), faixa.blue()))]


def _perto(cor, rgb):
    return all(abs(c - e) <= 2 for c, e in zip((cor.red(), cor.green(), cor.blue()), rgb))


def test_o_item_marcado_tem_fundo_fraco_e_filete_e_os_outros_nada(janela):
    """RN-13: o marcado não é mais o bloco azul cheio."""
    menu = janela.menu
    menu.botao_anonimizar.click()
    foto = _foto_da_faixa(janela)

    filete, fundo = _cores_na_linha_do_item(foto, menu, menu.botao_anonimizar)
    assert filete.name() == COR_DESTAQUE_HOVER
    assert _perto(fundo, _fundo_do_marcado_esperado()), fundo.name()

    for item in (menu.botao_ocr, menu.botao_config_ia):
        filete, fundo = _cores_na_linha_do_item(foto, menu, item)
        assert filete.name() == fundo.name() == COR_FUNDO_ELEVADO, item.text()


def test_no_submenu_o_marcado_e_igual(janela):
    menu = janela.menu
    menu.botao_config_ia.click()
    foto = _foto_da_faixa(janela)

    filete, fundo = _cores_na_linha_do_item(foto, menu, menu.botao_lm_studio)
    assert filete.name() == COR_DESTAQUE_HOVER
    assert _perto(fundo, _fundo_do_marcado_esperado()), fundo.name()
    filete, fundo = _cores_na_linha_do_item(foto, menu, menu.botao_servidor_ia)
    assert filete.name() == fundo.name() == COR_FUNDO_ELEVADO


def test_o_texto_nao_pula_para_o_lado_ao_marcar(janela):
    """O filete transparente já ocupa o lugar no item normal: marcar só o pinta."""
    menu = janela.menu
    item = menu.botao_anonimizar

    def onde_comeca_o_icone():
        foto = _foto_da_faixa(janela)
        canto = item.mapTo(menu, item.rect().topLeft())
        y = canto.y() + item.height() // 2
        fundo = foto.pixelColor(canto.x() + item.width() - 20, y)
        for x in range(canto.x() + 8 + LARGURA_DO_FILETE, canto.x() + item.width()):
            if foto.pixelColor(x, y) != fundo:
                return x - canto.x()

    antes = onde_comeca_o_icone()
    item.click()
    assert onde_comeca_o_icone() == antes


def test_nenhum_item_marcado_sai_cortado(janela):
    """Marcado, o texto fica em negrito e mais largo. O Qt não refaz a largura
    pedida pelo botão quando o estilo muda com o estado, então a conta é feita
    aqui: a frase em negrito precisa caber no que sobra do botão depois da
    margem (8 + 8), do filete, do respiro (12 de cada lado, menos o filete) e
    do ícone, quando há."""
    janela.showNormal()
    janela.resize(TAMANHO_MINIMO)
    QApplication.processEvents()
    menu = janela.menu
    for item in (menu.botao_ocr, menu.botao_anonimizar, *menu.itens_do_submenu):
        fonte = QFont(item.font())
        fonte.setPixelSize(15)
        fonte.setWeight(QFont.DemiBold)
        frase = QFontMetrics(fonte).horizontalAdvance(item.text())
        icone = 0 if item.icon().isNull() else TAMANHO_DO_ICONE.width() + 4
        sobra = menu.width() - 16 - LARGURA_DO_FILETE - (12 - LARGURA_DO_FILETE) - 12 - icone
        assert frase <= sobra, (item.text(), frase, sobra)

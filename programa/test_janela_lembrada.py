"""A janela maximizada no primeiro uso e o tamanho lembrado (emenda de
28/10/2026 da spec 001, RN-4 a RN-8).

A conta de onde a janela abre é feita sem tela nenhuma, com telas de mentira de
vários tamanhos: é ela que garante que a janela cabe e fica no meio, em
qualquer monitor. Os testes do fim abrem a janela de verdade, por um instante,
para conferir o que só o Windows responde - o tamanho de antes de maximizar.
"""
import ctypes
import time

import pytest
from PySide6.QtCore import QMargins, QRect
from PySide6.QtWidgets import QApplication

import main
import preferencias
from main import JanelaPrincipal, como_abrir

# Uma tela Full HD com a barra de tarefas embaixo, e a moldura medida no
# Windows 11 desta máquina: 31 px de barra de título, sem borda visível.
TELA = QRect(0, 0, 1920, 1032)
MOLDURA = QMargins(0, 31, 0, 0)


def _lembrado(largura=None, altura=None, maximizada=None):
    return {"largura": largura, "altura": altura, "maximizada": maximizada}


def _por_fora(retangulo, moldura=MOLDURA):
    """A janela inteira, com a barra de título: é ela que precisa caber."""
    return retangulo.adjusted(-moldura.left(), -moldura.top(),
                              moldura.right(), moldura.bottom())


def _no_meio(retangulo, area, moldura=MOLDURA):
    centro, meio = _por_fora(retangulo, moldura).center(), area.center()
    return abs(centro.x() - meio.x()) <= 1 and abs(centro.y() - meio.y()) <= 1


# ------------------------------------------------- a conta, sem tela


def test_primeiro_uso_abre_maximizada_e_volta_ao_tamanho_de_antes():
    """RN-4 e RN-8: sem nada lembrado, maximizada; saindo do maximizado,
    1000 x 640 no meio da tela."""
    retangulo, maximizada = como_abrir(_lembrado(), TELA, MOLDURA)
    assert maximizada
    assert retangulo.size() == main.TAMANHO_NORMAL
    assert _no_meio(retangulo, TELA)


def test_sem_bloco_nenhum_tambem_e_primeiro_uso():
    assert como_abrir(None, TELA, MOLDURA)[1]


def test_o_tamanho_lembrado_volta_no_meio_da_tela():
    """Critério de aceite: fechou com 1200 x 800, abre com 1200 x 800, no meio."""
    retangulo, maximizada = como_abrir(_lembrado("1200", "800", "não"), TELA, MOLDURA)
    assert not maximizada
    assert (retangulo.width(), retangulo.height()) == (1200, 800)
    assert _no_meio(retangulo, TELA)


def test_fechou_maximizada_abre_maximizada_com_o_tamanho_de_antes():
    """RN-5: o tamanho lembrado é o de quando ela sai do maximizado."""
    retangulo, maximizada = como_abrir(_lembrado("1300", "700", "sim"), TELA, MOLDURA)
    assert maximizada
    assert (retangulo.width(), retangulo.height()) == (1300, 700)


def test_tamanho_maior_que_a_tela_encolhe_e_cabe_com_a_barra_de_titulo():
    """RN-7: o monitor mudou. A janela inteira, com a barra de título, cabe."""
    notebook = QRect(0, 0, 1366, 728)
    retangulo, _ = como_abrir(_lembrado("1900", "1000", "não"), notebook, MOLDURA)
    assert notebook.contains(_por_fora(retangulo))
    assert _por_fora(retangulo).height() == notebook.height()
    assert retangulo.width() == notebook.width()


def test_tamanho_menor_que_o_minimo_vira_o_minimo():
    retangulo, _ = como_abrir(_lembrado("400", "300", "não"), TELA, MOLDURA)
    assert retangulo.size() == main.TAMANHO_MINIMO
    assert _no_meio(retangulo, TELA)


@pytest.mark.parametrize("lembrado", [
    _lembrado("muito", "800", "não"),
    _lembrado("1200", None, "não"),
    _lembrado("1200.5", "800", "não"),
    _lembrado("0", "800", "não"),
    _lembrado("-1200", "800", "sim"),
])
def test_tamanho_que_nao_da_para_ler_vale_como_primeiro_uso(lembrado):
    """RN-4: "primeiro uso" é não haver tamanho lembrado que dê para ler."""
    retangulo, maximizada = como_abrir(lembrado, TELA, MOLDURA)
    assert maximizada
    assert retangulo.size() == main.TAMANHO_NORMAL


def test_maximizada_que_nao_da_para_ler_vale_como_nao_maximizada():
    """Com o tamanho lembrado, o que não for "sim" abre fora do maximizado."""
    assert not como_abrir(_lembrado("1200", "800", "talvez"), TELA, MOLDURA)[1]
    assert not como_abrir(_lembrado("1200", "800", None), TELA, MOLDURA)[1]


@pytest.mark.parametrize("area", [
    QRect(0, 0, 1920, 1032),          # Full HD, barra de tarefas embaixo
    QRect(0, 48, 1920, 1032),         # barra de tarefas em cima
    QRect(1920, 0, 2560, 1400),       # segundo monitor, à direita
    QRect(-1280, 200, 1280, 984),     # segundo monitor, à esquerda e mais baixo
    QRect(0, 0, 1366, 728),           # notebook
])
@pytest.mark.parametrize("largura, altura", [
    ("1000", "640"), ("1200", "800"), ("3000", "2000"), ("100", "100")])
def test_a_janela_abre_no_meio_e_nunca_fora_da_tela(area, largura, altura):
    """RN-6 e RN-7, em várias telas: no meio daquela tela, e inteira dentro dela."""
    retangulo, _ = como_abrir(_lembrado(largura, altura, "não"), area, MOLDURA)
    assert area.contains(_por_fora(retangulo))
    assert _no_meio(retangulo, area)


def test_tamanho_absurdo_escrito_a_mao_encolhe_em_vez_de_derrubar_o_programa():
    """Regressão da lente crítica da etapa 3: um número grande demais para o
    Qt derrubava o programa ao abrir (RN-39)."""
    retangulo, _ = como_abrir(_lembrado("99999999999", "800", "não"), TELA, MOLDURA)
    assert TELA.contains(_por_fora(retangulo))


def test_tela_menor_que_o_minimo_deixa_a_barra_de_titulo_a_vista():
    """A janela não encolhe abaixo do mínimo, e numa tela menor ela não cabe.
    Passa então pela direita e por baixo - nunca por cima, onde fica a barra de
    título por onde ela é arrastada."""
    pequena = QRect(100, 50, 800, 500)
    retangulo, _ = como_abrir(_lembrado("1200", "800", "não"), pequena, MOLDURA)
    assert retangulo.size() == main.TAMANHO_MINIMO
    assert _por_fora(retangulo).topLeft() == pequena.topLeft()


# ------------------------------------------------- a janela de verdade
# Aqui a janela aparece por um instante: só o Windows diz o tamanho a que ela
# volta ao sair do maximizado. O que se espera é calculado para a tela desta
# máquina, e por isso os testes servem em qualquer monitor.


def _esperado(janela, largura, altura):
    retangulo, _ = como_abrir(_lembrado(str(largura), str(altura), "não"),
                              janela.screen().availableGeometry(),
                              janela.windowHandle().frameMargins())
    return retangulo.width(), retangulo.height()


def _janela_lembrada(arquivo):
    return dict(preferencias._conteudo()["janela"]) if arquivo.exists() else None


def test_abrir_a_janela_nao_grava_nada(preferencias_isoladas):
    JanelaPrincipal()
    assert not preferencias_isoladas.exists()


def test_sem_nada_lembrado_a_janela_vai_abrir_maximizada():
    janela = JanelaPrincipal()
    assert janela.abre_maximizada
    assert (janela.width(), janela.height()) == _esperado(janela, 1000, 640)


def test_fechou_maximizada_lembra_maximizada_e_o_tamanho_de_antes(preferencias_isoladas):
    """RN-5, com o Windows: maximizada no primeiro uso e fechada assim, ela
    lembra o "sim" e o 1000 x 640 a que volta ao sair do maximizado."""
    janela = JanelaPrincipal()
    largura, altura = _esperado(janela, 1000, 640)
    janela.abrir()
    QApplication.processEvents()
    assert janela.isMaximized()
    janela.close()
    assert _janela_lembrada(preferencias_isoladas) == {
        "largura": str(largura), "altura": str(altura), "maximizada": "sim"}

    reaberta = JanelaPrincipal()
    assert reaberta.abre_maximizada
    assert (reaberta.width(), reaberta.height()) == (largura, altura)
    reaberta.close()


def test_fechou_com_1200_por_800_abre_com_1200_por_800_no_meio(preferencias_isoladas):
    """Critério de aceite, com o Windows: o tamanho volta, no meio da tela, e a
    janela inteira cabe nela."""
    janela = JanelaPrincipal()
    largura, altura = _esperado(janela, 1200, 800)
    janela.show()
    janela.resize(largura, altura)
    QApplication.processEvents()
    janela.close()
    assert _janela_lembrada(preferencias_isoladas) == {
        "largura": str(largura), "altura": str(altura), "maximizada": "não"}

    reaberta = JanelaPrincipal()
    reaberta.abrir()
    QApplication.processEvents()
    assert not reaberta.isMaximized()
    assert (reaberta.width(), reaberta.height()) == (largura, altura)
    area = reaberta.screen().availableGeometry()
    assert area.contains(reaberta.frameGeometry())
    centro = reaberta.frameGeometry().center()
    assert abs(centro.x() - area.center().x()) <= 1
    assert abs(centro.y() - area.center().y()) <= 1
    reaberta.close()


def test_maximizada_e_fechada_depois_de_mexer_no_tamanho_lembra_o_de_antes(
        preferencias_isoladas):
    """RN-5: deixou 1100 x 700, maximizou, fechou - ao sair do maximizado na
    próxima vez, ela volta a 1100 x 700, e não ao tamanho da tela."""
    janela = JanelaPrincipal()
    largura, altura = _esperado(janela, 1100, 700)
    janela.show()
    janela.resize(largura, altura)
    QApplication.processEvents()
    janela.showMaximized()
    QApplication.processEvents()
    janela.close()
    assert _janela_lembrada(preferencias_isoladas) == {
        "largura": str(largura), "altura": str(altura), "maximizada": "sim"}

    reaberta = JanelaPrincipal()
    reaberta.abrir()
    QApplication.processEvents()
    assert reaberta.isMaximized()
    reaberta.showNormal()
    QApplication.processEvents()
    assert (reaberta.width(), reaberta.height()) == (largura, altura)
    reaberta.close()


def test_maximizada_minimizada_pela_barra_de_tarefas_e_fechada_continua_maximizada(
        preferencias_isoladas):
    """Suspeita da lente crítica da etapa 3, derrubada: fechada pela barra de
    tarefas enquanto minimizada, a janela que estava maximizada continua
    lembrada como maximizada. A minimização é a do próprio Windows, e não a do
    Qt, que é o caminho de quem clica no tracinho da janela."""
    janela = JanelaPrincipal()
    largura, altura = _esperado(janela, 1100, 700)
    janela.show()
    janela.resize(largura, altura)
    QApplication.processEvents()
    janela.showMaximized()
    QApplication.processEvents()
    MINIMIZAR = 6   # SW_MINIMIZE, o pedido do Windows de minimizar
    ctypes.windll.user32.ShowWindow(int(janela.winId()), MINIMIZAR)
    for _ in range(20):
        QApplication.processEvents()
        time.sleep(0.02)
    assert janela.isMinimized()
    janela.close()
    assert _janela_lembrada(preferencias_isoladas) == {
        "largura": str(largura), "altura": str(altura), "maximizada": "sim"}


def test_minimizada_do_tamanho_normal_e_fechada_lembra_o_tamanho(preferencias_isoladas):
    """Suspeita da lente crítica da etapa 4, derrubada: minimizada pelo
    Windows a partir do tamanho normal, ela lembra esse tamanho, e não o do
    ícone na barra de tarefas."""
    janela = JanelaPrincipal()
    largura, altura = _esperado(janela, 1200, 800)
    janela.show()
    janela.resize(largura, altura)
    QApplication.processEvents()
    MINIMIZAR = 6   # SW_MINIMIZE, o pedido do Windows de minimizar
    ctypes.windll.user32.ShowWindow(int(janela.winId()), MINIMIZAR)
    for _ in range(20):
        QApplication.processEvents()
        time.sleep(0.02)
    assert janela.isMinimized()
    janela.close()
    assert _janela_lembrada(preferencias_isoladas) == {
        "largura": str(largura), "altura": str(altura), "maximizada": "não"}


def test_fechar_que_para_na_pergunta_de_descartar_nao_grava(
        preferencias_isoladas, monkeypatch):
    """A janela que ficou de pé porque a pessoa voltou para salvar não fechou:
    não há o que lembrar ainda."""
    janela = JanelaPrincipal()
    monkeypatch.setattr(janela.painel_anonimizar, "perguntar_antes_de_descartar",
                        lambda *a, **k: True)
    janela.close()
    assert not preferencias_isoladas.exists()


def test_a_janela_grava_no_bloco_dela_sem_mexer_nos_motores(preferencias_isoladas):
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    preferencias.gravar("anonimizar", "motor", "tesseract")
    JanelaPrincipal().close()
    conteudo = preferencias._conteudo()
    assert conteudo.sections() == ["gerar_ocr", "anonimizar", "janela"]
    assert conteudo["gerar_ocr"]["motor"] == "tesseract"
    assert conteudo["anonimizar"]["motor"] == "tesseract"


def test_largura_e_altura_sao_gravadas_juntas(preferencias_isoladas, monkeypatch):
    """Uma gravação só para as três: cortada no meio, nada muda, em vez de
    ficar a largura nova com a altura velha."""
    gravacoes = []
    gravar_de_verdade = preferencias.gravar_juntos
    monkeypatch.setattr(preferencias, "gravar_juntos",
                        lambda *a: (gravacoes.append(a), gravar_de_verdade(*a)))
    JanelaPrincipal().close()
    assert len(gravacoes) == 1

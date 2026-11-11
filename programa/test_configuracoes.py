"""O menu "Configurações", as duas seções, os ícones e a tela do Tema (emenda de
05/11/2026 da spec 001, RN-20 a RN-23; RN-42 da spec 002; emenda de mesma data da
spec 004). O "Reabrir agora" e as perguntas antes dele são de etapas seguintes."""
import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QAbstractButton, QApplication, QLabel, QPushButton, QRadioButton

import estilo
import main
import preferencias
import tela_do_tema
from main import TAMANHO_MINIMO, JanelaPrincipal
from tela_do_tema import TEMA, VALE_AO_REABRIR


@pytest.fixture
def janela():
    return JanelaPrincipal()


def _textos_do_submenu(janela):
    """O que aparece no submenu, de cima para baixo."""
    submenu = janela.menu.pagina_ia.layout()
    textos = []
    for i in range(submenu.count()):
        peca = submenu.itemAt(i).widget()
        if peca is None:
            continue
        textos.append(peca.text() if isinstance(peca, QAbstractButton) else peca.rotulo.text())
    return textos


def test_o_submenu_tem_as_duas_secoes_na_ordem_combinada(janela):
    janela.menu.botao_config_ia.click()
    assert _textos_do_submenu(janela) == [
        "‹ Voltar", "Configurações Gerais", "Tema", "Configurações de IA",
        "LM Studio", "Servidor de IA Interno", "Habilitar IA"]


def test_entrar_abre_o_tema_com_o_desenho_do_tema_no_titulo(janela):
    janela.menu.botao_config_ia.click()
    assert janela.menu.botao_tema.isChecked()
    assert janela.painel_ia.tela_atual() == TEMA
    cabecalho = janela.painel_ia.tela_tema.cabecalho
    # RN-31: o desenho do item "Tema"; a engrenagem fica no item da faixa.
    assert cabecalho.icone.desenho == "tema"
    assert cabecalho.titulo.text() == "Tema"
    assert cabecalho.legenda.text() == "As cores do programa. O desenho das telas é o mesmo nos dois."


def test_o_titulo_de_secao_nao_se_clica_e_nunca_fica_marcado(janela):
    janela.menu.botao_config_ia.click()
    janela.menu.botao_lm_studio.click()
    marcados_antes = [i.isChecked() for i in janela.menu.itens_do_submenu]
    for titulo in janela.menu.titulos_de_secao:
        assert not isinstance(titulo, QAbstractButton)
        QTest.mouseClick(titulo, Qt.LeftButton, Qt.NoModifier, QPoint(10, 10))
    assert [i.isChecked() for i in janela.menu.itens_do_submenu] == marcados_antes
    assert janela.painel_ia.tela_atual() != TEMA


def test_o_titulo_de_secao_e_letra_pequena_no_cinza_com_o_filete(janela):
    for titulo in janela.menu.titulos_de_secao:
        folha = titulo.rotulo.styleSheet()
        assert f"font-size: {estilo.TEXTO_PEQUENO}px" in folha
        assert estilo.COR_TEXTO_SECUNDARIO in folha
        filete = titulo.findChild(type(titulo), "filete")
        assert filete is not None and filete.height() == 1
        assert estilo.COR_BORDA in filete.styleSheet()


def test_so_o_titulo_de_secao_diz_configuracoes_de_ia(janela):
    # Emenda de 05/11/2026 da spec 004: o único texto visível com "Configurações de
    # IA" é o título de seção do submenu.
    textos = [peca.text() for peca in janela.findChildren(QLabel) + janela.findChildren(QPushButton)
              if "Configurações de IA" in peca.text()]
    assert textos == ["Configurações de IA"]
    assert janela.menu.titulos_de_secao[1].rotulo.text() == "Configurações de IA"


def test_a_tela_do_tema_comeca_no_tema_da_tela_e_sem_a_frase(janela):
    tela = janela.painel_ia.tela_tema
    assert tela.opcoes[estilo.ESCURO].isChecked()
    assert not tela.opcoes[estilo.CLARO].isChecked()
    assert tela.aviso.isHidden()


def test_as_opcoes_e_as_explicacoes_tem_os_textos_da_spec(janela):
    tela = janela.painel_ia.tela_tema
    assert [b.text() for b in tela.findChildren(QRadioButton)] == ["Escuro", "Claro"]
    explicacoes = [r.text() for r in tela.findChildren(QLabel) if "Fundo" in r.text()]
    assert explicacoes[0].startswith("Fundo grafite e letra clara · ")
    assert "o tema de quem nunca escolheu" in explicacoes[0]
    assert explicacoes[1] == "Fundo claro e letra escura"
    assert tela.aviso.frase.text() == VALE_AO_REABRIR == "O tema novo vale quando o programa abrir de novo."


def _lembrado(arquivo):
    return preferencias.ler(tela_do_tema.LEMBRAR_TEMA, tela_do_tema.CHAVE_DO_TEMA)


def test_marcar_claro_guarda_na_hora_e_mostra_a_frase(janela, preferencias_isoladas):
    tela = janela.painel_ia.tela_tema
    tela.opcoes[estilo.CLARO].click()
    assert _lembrado(preferencias_isoladas) == "claro"
    assert not tela.aviso.isHidden()
    # Marcar de volta o tema da tela faz a frase sumir, e o arquivo volta a dizer escuro.
    tela.opcoes[estilo.ESCURO].click()
    assert _lembrado(preferencias_isoladas) == "escuro"
    assert tela.aviso.isHidden()


def test_guardar_o_tema_nao_mexe_no_motor_nem_na_janela(janela, preferencias_isoladas):
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    preferencias.gravar_juntos("janela", {"largura": 1100, "altura": 700, "maximizada": "não"})
    janela.painel_ia.tela_tema.opcoes[estilo.CLARO].click()
    assert preferencias.ler("gerar_ocr", "motor") == "tesseract"
    assert preferencias.ler_bloco("janela") == {"largura": "1100", "altura": "700",
                                                "maximizada": "não"}
    assert _lembrado(preferencias_isoladas) == "claro"


def test_sem_gravacao_a_escolha_vale_ate_fechar(janela, preferencias_isoladas):
    # Uma pasta no lugar do arquivo: a gravação falha, calada (RN-39 da spec 002).
    preferencias_isoladas.mkdir()
    tela = janela.painel_ia.tela_tema
    tela.opcoes[estilo.CLARO].click()
    assert tela.escolhido == estilo.CLARO
    assert not tela.aviso.isHidden()
    assert tela_do_tema.lembrado() is None


@pytest.mark.parametrize("escrito, vale", [("claro", "claro"), ("Claro", "claro"),
                                           ("escuro", "escuro"), ("azul", None), ("", None)])
def test_o_tema_lembrado_so_vale_se_for_escuro_ou_claro(escrito, vale):
    preferencias.gravar(tela_do_tema.LEMBRAR_TEMA, tela_do_tema.CHAVE_DO_TEMA, escrito)
    assert tela_do_tema.lembrado() == vale


@pytest.fixture
def modo_do_windows(aplicacao):
    """Devolve o modo de cores ao do Windows depois do teste: ele vale para o
    programa inteiro, e forçado no claro passaria para os testes seguintes."""
    yield aplicacao.styleHints()
    aplicacao.styleHints().setColorScheme(Qt.ColorScheme.Unknown)


@pytest.mark.parametrize("guardado, abre", [(None, "escuro"), ("escuro", "escuro"),
                                            ("claro", "claro"), ("azul", "escuro")])
def test_o_programa_abre_no_tema_guardado(aplicacao, modo_do_windows, guardado, abre):
    if guardado is not None:
        preferencias.gravar(tela_do_tema.LEMBRAR_TEMA, tela_do_tema.CHAVE_DO_TEMA, guardado)
    assert main.usar_o_tema_lembrado(aplicacao) == abre
    assert estilo.TEMA == abre
    assert estilo.COR_FUNDO == estilo.TEMAS[abre]["COR_FUNDO"]


def test_guardado_que_nao_da_para_ler_abre_no_escuro(aplicacao, modo_do_windows,
                                                      preferencias_isoladas):
    # Uma pasta no lugar do arquivo: nada se lê, e o programa abre no escuro, sem erro.
    preferencias_isoladas.mkdir()
    assert main.usar_o_tema_lembrado(aplicacao) == estilo.ESCURO


def test_no_claro_as_pecas_do_windows_seguem_o_claro(aplicacao, modo_do_windows):
    preferencias.gravar(tela_do_tema.LEMBRAR_TEMA, tela_do_tema.CHAVE_DO_TEMA, "claro")
    main.usar_o_tema_lembrado(aplicacao)
    assert modo_do_windows.colorScheme() == Qt.ColorScheme.Light


def test_no_escuro_o_modo_do_windows_fica_como_estava(aplicacao, modo_do_windows):
    antes = modo_do_windows.colorScheme()
    main.usar_o_tema_lembrado(aplicacao)
    assert modo_do_windows.colorScheme() == antes


def test_aberto_no_claro_a_tela_do_tema_mostra_claro_e_nada_embaixo(aplicacao, modo_do_windows):
    preferencias.gravar(tela_do_tema.LEMBRAR_TEMA, tela_do_tema.CHAVE_DO_TEMA, "claro")
    main.usar_o_tema_lembrado(aplicacao)
    janela = JanelaPrincipal()
    janela.menu.botao_config_ia.click()
    tela = janela.painel_ia.tela_tema
    assert tela.opcoes[estilo.CLARO].isChecked()
    assert tela.aviso.isHidden()
    # E a janela inteira nasceu no claro: o fundo do painel já é o do claro.
    assert estilo.TEMAS[estilo.CLARO]["COR_FUNDO"] in janela.painel.styleSheet()


def test_na_janela_minima_nada_sai_cortado_no_submenu_nem_no_tema(janela):
    janela.showNormal()
    janela.resize(TAMANHO_MINIMO)
    janela.menu.botao_config_ia.click()
    tela = janela.painel_ia.tela_tema
    tela.opcoes[estilo.CLARO].click()
    QApplication.processEvents()
    for item in (janela.menu.botao_voltar_ia, *janela.menu.itens_do_submenu):
        assert item.width() >= item.sizeHint().width(), item.text()
    for titulo in janela.menu.titulos_de_secao:
        assert titulo.rotulo.width() >= titulo.rotulo.sizeHint().width(), titulo.rotulo.text()
    pecas = [*tela.findChildren(QRadioButton), *tela.findChildren(QLabel)]
    for peca in pecas:
        if peca.isVisible() and peca.text():
            assert peca.width() >= peca.sizeHint().width(), peca.text()
    assert tela.aviso.frase.width() >= tela.aviso.frase.sizeHint().width()

"""O item "Configurações" e o submenu (etapa 2, RN-1 a RN-3 da spec 004; nome e
Tema desde a emenda de 05/11/2026 da spec 001, RN-20 a RN-22)."""
import pytest

from main import JanelaPrincipal
from painel_ia import HABILITAR, LM_STUDIO, SERVIDOR
from tela_do_tema import TEMA
from test_antes_de_descartar import _copia


@pytest.fixture
def janela():
    return JanelaPrincipal()


def test_o_item_fica_no_fim_da_faixa_longe_dos_modulos(janela):
    principal = janela.menu.pagina_principal.layout()
    ordem = [principal.indexOf(i) for i in (janela.menu.botao_ocr,
                                            janela.menu.botao_anonimizar,
                                            janela.menu.botao_config_ia)]
    assert ordem == sorted(ordem)
    # O espaço vazio é o que o empurra para baixo.
    assert principal.itemAt(ordem[1] + 1).spacerItem() is not None
    assert ordem[2] == principal.count() - 1
    # Nada vem abaixo das páginas do menu: desde a emenda de 03/11/2026 da spec
    # 001 a versão mora no cabeçalho, e o item é o último da faixa.
    faixa = janela.menu.layout()
    assert faixa.indexOf(janela.menu.paginas) == faixa.count() - 1


def test_o_clique_troca_o_menu_inteiro_pelo_submenu(janela):
    janela.menu.botao_config_ia.click()
    assert janela.menu.paginas.currentWidget() is janela.menu.pagina_ia
    assert janela.painel.currentWidget() is janela.painel_ia
    assert [i.text() for i in janela.menu.itens_do_submenu] == [
        "Tema", "LM Studio", "Servidor de IA Interno", "Habilitar IA"]
    # Entra pela primeira opção, o Tema, e não mais pelo LM Studio (RN-22).
    assert janela.menu.botao_tema.isChecked()
    assert janela.painel_ia.tela_atual() == TEMA


def test_cada_item_traz_a_sua_tela_e_so_um_fica_marcado(janela):
    janela.menu.botao_config_ia.click()
    janela.menu.botao_servidor_ia.click()
    assert janela.painel_ia.tela_atual() == SERVIDOR
    janela.menu.botao_habilitar_ia.click()
    assert janela.painel_ia.tela_atual() == HABILITAR
    assert [i.isChecked() for i in janela.menu.itens_do_submenu] == [
        False, False, False, True]
    # Clicar no já marcado não desmarca: aqui não há tela de boas-vindas.
    janela.menu.botao_habilitar_ia.click()
    assert janela.menu.botao_habilitar_ia.isChecked()
    assert janela.painel_ia.tela_atual() == HABILITAR


def test_voltar_devolve_o_menu_de_sempre(janela):
    janela.menu.botao_config_ia.click()
    janela.menu.botao_voltar_ia.click()
    assert janela.menu.paginas.currentWidget() is janela.menu.pagina_principal
    assert janela.painel.currentWidget() is janela.painel_vazio


def test_com_revisao_nao_salva_vem_a_pergunta_de_descartar(janela, tmp_path):
    arquivo = _copia(tmp_path)
    janela.menu.botao_anonimizar.click()
    janela.painel_anonimizar.receber_arquivo(arquivo)

    janela.menu.botao_config_ia.click()

    painel = janela.painel_anonimizar
    assert painel.telas.currentWidget() is painel.tela_descartar
    assert janela.menu.paginas.currentWidget() is janela.menu.pagina_principal
    assert janela.menu.botao_anonimizar.isChecked()

    painel.tela_descartar.botao_descartar.click()
    assert janela.painel.currentWidget() is janela.painel_ia
    assert janela.menu.paginas.currentWidget() is janela.menu.pagina_ia


def test_com_o_submenu_aberto_fechar_com_revisao_volta_ao_menu_de_sempre(janela, tmp_path):
    arquivo = _copia(tmp_path)
    janela.menu.botao_anonimizar.click()
    painel = janela.painel_anonimizar
    painel.receber_arquivo(arquivo)
    painel._salvo = True
    janela.menu.botao_config_ia.click()
    painel._salvo = False

    janela.close()

    assert janela.menu.paginas.currentWidget() is janela.menu.pagina_principal
    assert janela.painel.currentWidget() is painel

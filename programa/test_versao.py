"""Teste do número da versão na janela."""
import re

from main import JanelaPrincipal
from versao import VERSAO


def test_a_janela_mostra_o_numero_da_versao(aplicacao):
    """Sem o número na tela, "qual versão você está usando?" não tem resposta."""
    janela = JanelaPrincipal()

    assert janela.menu.versao.text() == f"versão {VERSAO}"


def test_o_numero_tem_tres_partes():
    """É esse formato que o instalador do Windows entende como versão."""
    assert re.fullmatch(r"\d+\.\d+\.\d+", VERSAO)

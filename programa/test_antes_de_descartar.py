"""Testes da pergunta antes de descartar a revisão (etapa 6 do Anonimizar).

São quatro as saídas que jogariam fora o trabalho de revisão: o botão do rodapé,
arrastar outro arquivo, trocar de item no menu e fechar a janela. As quatro
passam pela mesma pergunta, e nenhuma delas descarta nada antes da resposta.

Os cliques são dados nos botões de verdade, e não chamando as funções por
dentro: foi assim que dois defeitos passaram pelos testes na etapa 5.
"""
import shutil
from pathlib import Path

import cpf
from main import JanelaPrincipal
from painel_anonimizar import PainelAnonimizar

MASSA = Path(__file__).parent.parent / "dados-exemplo"
COM_CPF = "10-prestacao-com-cpf.md"


def _copia(pasta, nome=COM_CPF):
    origem = pasta / nome
    shutil.copy(MASSA / nome, origem)
    return origem


def _painel_na_revisao(tmp_path):
    painel = PainelAnonimizar()
    painel.receber_arquivo(_copia(tmp_path))
    return painel


def _salvar(painel):
    painel.abrir_o_salvar()
    painel.gravar(Path(painel.tela_salvar.campo.text()))


# ------------------------------------------------- sair pela própria revisão


def test_sair_pela_revisao_pergunta_antes(tmp_path, aplicacao):
    painel = _painel_na_revisao(tmp_path)
    painel.voltar_para_escolher()

    assert painel.telas.currentWidget() is painel.tela_descartar
    # Nada foi descartado enquanto a pergunta está na tela.
    assert painel.tela_revisao.texto_mascarado() != ""
    assert "ainda não foi salva" in painel.tela_descartar.titulo.text()


def test_voltar_e_salvar_devolve_a_revisao_como_estava(tmp_path, aplicacao):
    painel = _painel_na_revisao(tmp_path)
    antes = painel.tela_revisao.texto_mascarado()
    painel.voltar_para_escolher()

    from PySide6.QtWidgets import QPushButton
    voltar = next(b for b in painel.tela_descartar.findChildren(QPushButton)
                  if b.text() == "Voltar e salvar")
    voltar.click()

    assert painel.telas.currentWidget() is painel.tela_revisao
    assert painel.tela_revisao.texto_mascarado() == antes


def test_descartar_e_seguir_leva_para_a_escolha_do_arquivo(tmp_path, aplicacao):
    painel = _painel_na_revisao(tmp_path)
    painel.voltar_para_escolher()
    painel.tela_descartar.botao_descartar.click()

    assert painel.telas.currentWidget() is painel.tela_escolher
    assert painel.tela_revisao.texto_mascarado() == ""


def test_o_que_se_perde_aparece_com_numero(tmp_path, aplicacao):
    """A contagem é o que deixa decidir num olhar (rascunho 08, estado 11)."""
    painel = _painel_na_revisao(tmp_path)
    liberado = next(o for o in painel.tela_revisao._ocorrencias if o.passa_na_conta)
    liberado.situacao = cpf.LIBERADO
    painel.tela_revisao._desenhar()
    painel.voltar_para_escolher()

    frase = painel.tela_descartar.explicacao.text()
    assert COM_CPF in frase
    assert "11 números mascarados, 1 liberado por você" in frase


# -------------------------------------------------- abrir outro arquivo


def test_outro_arquivo_pergunta_antes_e_so_abre_depois(tmp_path, aplicacao):
    painel = _painel_na_revisao(tmp_path)
    outro = _copia(tmp_path, "11-sem-cpf.md")

    painel.receber_arquivo(outro)
    assert painel.telas.currentWidget() is painel.tela_descartar
    # O arquivo novo ainda não entrou: o texto na tela é o do primeiro.
    assert painel.tela_revisao.texto_mascarado().count("XXX") == 12

    painel.tela_descartar.botao_descartar.click()
    assert painel.telas.currentWidget() is painel.tela_revisao
    assert painel.tela_revisao.texto_mascarado().count("XXX") == 0


def test_outro_arquivo_solto_por_cima_da_pergunta_nao_perde_a_volta(tmp_path,
                                                                    aplicacao):
    """Lição herdada do Gerar OCR: a pergunta não vira o lugar de voltar.

    Guardando a própria pergunta como "de onde eu vim", o "Voltar e salvar"
    ficava sem sair do lugar, e a única saída que funcionava era a que joga o
    trabalho fora - a perda que esta pergunta existe para evitar.
    """
    painel = _painel_na_revisao(tmp_path)
    outro = _copia(tmp_path, "11-sem-cpf.md")

    painel.receber_arquivo(outro)
    assert painel.telas.currentWidget() is painel.tela_descartar
    # O segundo arquivo solto por cima da pergunta pergunta de novo, em vez de
    # abrir direto: com a pergunta na tela, a revisão continua lá para perder.
    painel.receber_arquivo(outro)
    assert painel.telas.currentWidget() is painel.tela_descartar

    painel._voltar_de_onde_estava()
    assert painel.telas.currentWidget() is painel.tela_revisao
    assert painel.tela_revisao.texto_mascarado().count("XXX") == 12


# ------------------------------------------------------- quando não pergunta


def test_depois_de_salvar_nao_pergunta_mais(tmp_path, aplicacao):
    painel = _painel_na_revisao(tmp_path)
    _salvar(painel)

    assert not painel.tem_revisao_nao_salva()
    painel.voltar_para_escolher()
    assert painel.telas.currentWidget() is painel.tela_escolher


def test_sem_revisao_aberta_nao_pergunta(tmp_path, aplicacao):
    """Pergunta que aparece sem motivo ensina a clicar em "sim" sem ler."""
    painel = PainelAnonimizar()
    assert not painel.tem_revisao_nao_salva()
    painel.voltar_para_escolher()
    assert painel.telas.currentWidget() is painel.tela_escolher


def test_arquivo_que_nao_serve_nao_deixa_pergunta_para_tras(tmp_path, aplicacao):
    """Da tela de erro não há revisão para perder."""
    painel = PainelAnonimizar()
    ruim = tmp_path / "vazio.md"
    ruim.write_text("", encoding="utf-8")
    painel.receber_arquivo(ruim)

    assert painel.telas.currentWidget() is painel.tela_erro
    assert not painel.tem_revisao_nao_salva()


# ------------------------------------------------ o menu e o fechar da janela


def test_trocar_de_item_no_menu_pergunta_antes(tmp_path, aplicacao):
    janela = JanelaPrincipal()
    janela.menu.botao_anonimizar.click()
    janela.painel_anonimizar.receber_arquivo(_copia(tmp_path))

    janela.menu.botao_ocr.click()

    painel = janela.painel_anonimizar
    assert janela.painel.currentWidget() is painel
    assert painel.telas.currentWidget() is painel.tela_descartar
    # O menu continua marcando o Anonimizar enquanto a pergunta está na tela.
    assert janela.menu.botao_anonimizar.isChecked()
    assert not janela.menu.botao_ocr.isChecked()

    painel.tela_descartar.botao_descartar.click()
    assert janela.painel.currentWidget() is janela.painel_ocr
    assert janela.menu.botao_ocr.isChecked()


def test_desmarcar_o_anonimizar_no_menu_tambem_pergunta(tmp_path, aplicacao):
    janela = JanelaPrincipal()
    janela.menu.botao_anonimizar.click()
    janela.painel_anonimizar.receber_arquivo(_copia(tmp_path))

    janela.menu.botao_anonimizar.click()

    painel = janela.painel_anonimizar
    assert painel.telas.currentWidget() is painel.tela_descartar
    assert janela.menu.botao_anonimizar.isChecked()


def test_fechar_a_janela_pergunta_e_a_janela_fica_de_pe(tmp_path, aplicacao):
    from PySide6.QtGui import QCloseEvent

    janela = JanelaPrincipal()
    janela.menu.botao_anonimizar.click()
    janela.painel_anonimizar.receber_arquivo(_copia(tmp_path))

    evento = QCloseEvent()
    janela.closeEvent(evento)

    painel = janela.painel_anonimizar
    assert not evento.isAccepted(), "a janela não pode fechar com a pergunta na tela"
    assert painel.telas.currentWidget() is painel.tela_descartar
    # O botão diz o que a pessoa pediu, e não "descartar e seguir".
    assert painel.tela_descartar.botao_descartar.text() == "Fechar sem salvar"

    # E clicando nele, a janela fecha de verdade: a segunda tentativa não
    # esbarra na mesma pergunta.
    painel.tela_descartar.botao_descartar.click()
    assert not painel.tem_revisao_nao_salva()
    segundo = QCloseEvent()
    janela.closeEvent(segundo)
    assert segundo.isAccepted()


def test_fechar_a_janela_depois_de_salvar_nao_pergunta(tmp_path, aplicacao):
    from PySide6.QtGui import QCloseEvent

    janela = JanelaPrincipal()
    janela.menu.botao_anonimizar.click()
    janela.painel_anonimizar.receber_arquivo(_copia(tmp_path))
    _salvar(janela.painel_anonimizar)

    evento = QCloseEvent()
    janela.closeEvent(evento)

    assert evento.isAccepted()


def test_com_a_pergunta_na_tela_nada_e_descartado_em_silencio(tmp_path, aplicacao):
    """A proteção nao pode sumir justamente enquanto esta sendo usada.

    Com a pergunta na tela, fechar a janela fechava o programa e soltar outro
    arquivo o abria por cima - nos dois casos, a revisão inteira se perdia sem
    uma palavra (revisão da etapa 6).
    """
    from PySide6.QtGui import QCloseEvent

    janela = JanelaPrincipal()
    janela.menu.botao_anonimizar.click()
    painel = janela.painel_anonimizar
    painel.receber_arquivo(_copia(tmp_path))
    painel.voltar_para_escolher()
    assert painel.telas.currentWidget() is painel.tela_descartar

    evento = QCloseEvent()
    janela.closeEvent(evento)
    assert not evento.isAccepted(), "a janela fechou com a pergunta na tela"
    assert painel.tela_revisao.texto_mascarado() != "", "a revisão se perdeu"


def test_quem_troca_de_modulo_e_volta_encontra_a_escolha_do_arquivo(tmp_path,
                                                                    aplicacao):
    """A pergunta velha nao pode ficar esperando no painel.

    Descartando pelo menu, o painel ficava parado na pergunta ja respondida:
    voltando ao Anonimizar, a pessoa reencontrava uma tela em que nenhum dos
    dois botoes levava a lugar nenhum (revisao da etapa 6).
    """
    janela = JanelaPrincipal()
    janela.menu.botao_anonimizar.click()
    painel = janela.painel_anonimizar
    painel.receber_arquivo(_copia(tmp_path))

    janela.menu.botao_ocr.click()
    painel.tela_descartar.botao_descartar.click()
    janela.menu.botao_anonimizar.click()

    assert painel.telas.currentWidget() is painel.tela_escolher


def test_documento_sem_nenhum_numero_nao_pergunta(tmp_path, aplicacao):
    """Pergunta sem motivo ensina a clicar em "descartar" sem ler.

    Nada encontrado e nada mascarado a mao: abrir o documento de novo e
    imediato, e nao ha o que perder (revisao da etapa 6).
    """
    painel = PainelAnonimizar()
    painel.receber_arquivo(_copia(tmp_path, "11-sem-cpf.md"))
    assert painel.telas.currentWidget() is painel.tela_revisao

    painel.voltar_para_escolher()
    assert painel.telas.currentWidget() is painel.tela_escolher


def test_um_trecho_mascarado_a_mao_ja_faz_a_pergunta_aparecer(tmp_path, aplicacao):
    """Mesmo sem o programa achar nada, o que a pessoa fez conta."""
    painel = PainelAnonimizar()
    painel.receber_arquivo(_copia(tmp_path, "11-sem-cpf.md"))
    texto = painel.tela_revisao._texto
    comeco = texto.index("2026")
    painel.tela_revisao._ocorrencias.append(
        cpf.mascarar_a_mao(texto, comeco, comeco + 4))
    painel.tela_revisao._desenhar()

    painel.voltar_para_escolher()
    assert painel.telas.currentWidget() is painel.tela_descartar
    assert "1 mascarado à mão por você" in painel.tela_descartar.explicacao.text()

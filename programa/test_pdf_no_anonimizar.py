"""Testes dos caminhos tortos do PDF pelo Anonimizar (etapa 7, fatia 7c).

Cancelar a leitura, o motor de leitura faltando, e a pergunta antes de
descartar durante a conferência. O caminho normal - o PDF indo da decisão à
revisão - está nos testes do painel.
"""
from pathlib import Path

import pytest

import motor_na_tela
from main import JanelaPrincipal
from painel_anonimizar import PainelAnonimizar

MASSA = Path(__file__).parent.parent / "dados-exemplo"
COM_TEXTO = MASSA / "01-com-texto-e-tabela.pdf"
SEM_TEXTO = MASSA / "02-imprimir-para-pdf.pdf"


class _LeituraDeMentira:
    """Faz o papel da leitura em andamento, sem rodar o Tesseract."""

    def isRunning(self):
        return False

    def cancelar(self):
        pass


@pytest.fixture
def sem_motor(monkeypatch):
    """Uma máquina sem o Tesseract, que ganha o motor quando pedirem."""
    estado = {"tem_motor": False}
    monkeypatch.setattr(motor_na_tela, "localizar_tesseract",
                        lambda: Path("tesseract.exe") if estado["tem_motor"] else None)
    monkeypatch.setattr(motor_na_tela, "ha_algum_tesseract", lambda: False)
    monkeypatch.setattr(motor_na_tela, "localizar_instalador", lambda: None)
    return estado


def _na_conferencia(painel):
    """Leva o PDF com texto até a conferência, pelo caminho que a pessoa faz."""
    painel.receber_arquivo(COM_TEXTO)
    painel.pdf.conferir_documento(COM_TEXTO)
    painel.pdf.tela_decisao.botao_aproveitar.click()
    assert painel.telas.currentWidget() is painel.pdf.tela_conferencia


# ------------------------------------------------------ cancelar a leitura


def test_cancelar_a_leitura_volta_a_escolha_e_diz_o_que_houve(aplicacao):
    painel = PainelAnonimizar()
    painel.receber_arquivo(SEM_TEXTO)
    painel.pdf.conferir_documento(SEM_TEXTO)
    leitura = _LeituraDeMentira()
    painel.pdf.leitura = leitura

    painel.pdf._leitura_cancelada(leitura, 3)

    assert painel.telas.currentWidget() is painel.tela_escolher
    assert painel.faixa_do_topo.isVisibleTo(painel)
    assert "página 3" in painel.faixa_do_topo.text()
    assert "Nada foi gravado" in painel.faixa_do_topo.text()


def test_documento_novo_apaga_a_faixa_do_cancelamento(aplicacao):
    painel = PainelAnonimizar()
    painel.faixa_do_topo.mostrar("Leitura cancelada na página 3.")
    painel.receber_arquivo(MASSA / "11-sem-cpf.md")
    assert not painel.faixa_do_topo.isVisibleTo(painel)


# --------------------------------------------------- o motor de leitura faltando


def test_sem_motor_o_aviso_e_a_lista_do_que_da_aparecem(aplicacao, sem_motor):
    """Rascunho 08, estado 2: a escolha do arquivo continua funcionando."""
    painel = PainelAnonimizar()

    assert painel.motor.aviso.isVisibleTo(painel)
    assert painel.lista_sem_motor.isVisibleTo(painel)
    assert not painel.tipos.isVisibleTo(painel)
    assert "PDF escaneado" in painel.lista_sem_motor.text()


def test_sem_motor_um_md_abre_a_revisao_normalmente(aplicacao, sem_motor):
    painel = PainelAnonimizar()
    painel.receber_arquivo(MASSA / "10-prestacao-com-cpf.md")
    assert painel.telas.currentWidget() is painel.tela_revisao


def test_sem_motor_o_pdf_com_texto_funciona(aplicacao, sem_motor):
    """O PDF com texto por dentro não precisa do motor."""
    painel = PainelAnonimizar()
    painel.receber_arquivo(COM_TEXTO)
    painel.pdf.conferir_documento(COM_TEXTO)
    assert painel.telas.currentWidget() is painel.pdf.tela_decisao


def test_sem_motor_o_pdf_escaneado_leva_a_tela_cheia(aplicacao, sem_motor):
    """Rascunho 08, estado 2b, com a frase a mais do Anonimizar."""
    painel = PainelAnonimizar()
    painel.receber_arquivo(SEM_TEXTO)
    painel.pdf.conferir_documento(SEM_TEXTO)

    tela = painel.motor.tela_sem_motor
    assert painel.telas.currentWidget() is tela
    assert "não tem texto por dentro" in tela.explicacao.text()
    assert "podem ser anonimizados normalmente" in tela.explicacao.text()


def test_sem_motor_ignorar_o_texto_leva_a_tela_cheia(aplicacao, sem_motor):
    """Rascunho 08, estado 2c: o documento tem texto, e a frase não nega isso."""
    painel = PainelAnonimizar()
    painel.receber_arquivo(COM_TEXTO)
    painel.pdf.conferir_documento(COM_TEXTO)
    painel.pdf.tela_decisao.botao_ignorar.click()

    tela = painel.motor.tela_sem_motor
    assert painel.telas.currentWidget() is tela
    assert "como imagem" in tela.explicacao.text()
    assert "não tem texto por dentro" not in tela.explicacao.text()


def test_motor_resolvido_na_tela_cheia_segue_para_a_tela_de_ler(aplicacao, sem_motor):
    """Segue para a tela de ler, e não direto para a leitura."""
    painel = PainelAnonimizar()
    painel.receber_arquivo(SEM_TEXTO)
    painel.pdf.conferir_documento(SEM_TEXTO)

    sem_motor["tem_motor"] = True
    painel.motor.conferir_de_novo()

    assert painel.telas.currentWidget() is painel.pdf.tela_de_ler
    assert painel.pdf.tela_de_ler.titulo.text() == "Este documento precisa ser lido"
    # E a tela de escolher volta a mostrar a linha dos tipos, no lugar da lista
    # do que dá sem o motor. A tela de escolher não está à vista agora, então a
    # pergunta é se cada linha está marcada para aparecer quando ela voltar.
    assert not painel.tipos.isHidden()
    assert painel.lista_sem_motor.isHidden()


# ------------------------------------ a pergunta durante a conferência do PDF


def test_na_conferencia_escolher_outro_pergunta_com_as_palavras_do_gerar_ocr(aplicacao):
    """Rascunho 08, tabela do estado 11: vale a pergunta do Gerar OCR."""
    painel = PainelAnonimizar()
    _na_conferencia(painel)

    painel.voltar_para_escolher()

    assert painel.telas.currentWidget() is painel.tela_descartar
    assert painel.tela_descartar.titulo.text() == (
        "O texto deste documento ainda não foi salvo")
    assert COM_TEXTO.name in painel.tela_descartar.explicacao.text()


def test_na_conferencia_arrastar_outro_arquivo_pergunta(aplicacao):
    painel = PainelAnonimizar()
    _na_conferencia(painel)

    painel.receber_arquivo(MASSA / "11-sem-cpf.md")
    assert painel.telas.currentWidget() is painel.tela_descartar

    # "Voltar" devolve a conferência como estava.
    painel._voltar_de_onde_estava()
    assert painel.telas.currentWidget() is painel.pdf.tela_conferencia


def test_na_conferencia_descartar_solta_o_texto_conferido(aplicacao):
    painel = PainelAnonimizar()
    _na_conferencia(painel)

    painel.voltar_para_escolher()
    painel.tela_descartar.botao_descartar.click()

    assert painel.telas.currentWidget() is painel.tela_escolher
    assert not any(painel.pdf.texto_conferido())


def test_na_conferencia_trocar_de_modulo_nao_pergunta_e_nada_se_perde(aplicacao):
    """Trocando de item no menu, a conferência fica esperando como estava."""
    janela = JanelaPrincipal()
    janela.menu.botao_anonimizar.click()
    painel = janela.painel_anonimizar
    _na_conferencia(painel)

    janela.menu.botao_ocr.click()
    assert janela.painel.currentWidget() is janela.painel_ocr

    janela.menu.botao_anonimizar.click()
    assert painel.telas.currentWidget() is painel.pdf.tela_conferencia
    assert any(painel.pdf.texto_conferido())


def test_conferido_a_pergunta_passa_a_ser_a_da_revisao(aplicacao):
    """Depois do "Conferido", quem pergunta é a revisão, com as palavras dela."""
    painel = PainelAnonimizar()
    _na_conferencia(painel)
    painel.pdf.tela_conferencia.botao_conferido.click()

    painel.voltar_para_escolher()
    assert painel.tela_descartar.titulo.text() == (
        "A revisão deste documento ainda não foi salva")


# ------------------------------------------------------- fechar a janela


class _LeituraRodando:
    """Uma leitura em andamento, que registra se alguém mandou parar."""

    def __init__(self):
        self.parou = False

    def isRunning(self):
        return not self.parou

    def cancelar(self):
        self.parou = True

    def wait(self, _ms):
        pass


def test_fechar_a_janela_para_a_leitura_do_anonimizar(aplicacao):
    """Revisão da etapa 7: só a leitura do Gerar OCR parava ao fechar.

    A do Anonimizar sobrevivia à janela, e o Windows mostrava a caixa de "o
    programa parou de funcionar" - o defeito que o CLAUDE.md registra como
    resolvido em 10/09/2026, de volta pela porta nova.
    """
    from PySide6.QtGui import QCloseEvent

    janela = JanelaPrincipal()
    leitura = _LeituraRodando()
    janela.painel_anonimizar.pdf.leitura = leitura

    evento = QCloseEvent()
    janela.closeEvent(evento)

    assert evento.isAccepted()
    assert leitura.parou, "a leitura do Anonimizar sobreviveu ao fechar da janela"


def test_abrir_um_md_no_meio_da_leitura_para_a_leitura_do_pdf(aplicacao):
    """Revisão da etapa 7: a leitura velha tomava a tela por cima da revisão.

    Quando ela terminava, a tela ia para a conferência do PDF, e o texto dele
    podia sair com o nome e a quebra de linha do .md aberto depois.
    """
    painel = PainelAnonimizar()
    painel.receber_arquivo(SEM_TEXTO)
    painel.pdf.conferir_documento(SEM_TEXTO)
    leitura = _LeituraRodando()
    painel.pdf.leitura = leitura

    painel.receber_arquivo(MASSA / "10-prestacao-com-cpf.md")
    assert leitura.parou, "a leitura do PDF continuou rodando"
    assert painel.telas.currentWidget() is painel.tela_revisao

    # Um aviso atrasado da leitura antiga não pode mais tomar a tela.
    painel.pdf._leitura_terminou(leitura, painel.pdf.ficha_atual, ["texto do pdf"])
    assert painel.telas.currentWidget() is painel.tela_revisao
    assert painel._origem.name == "10-prestacao-com-cpf.md"


def test_depois_de_salvar_um_pdf_novo_nao_pergunta_sobre_o_anterior(tmp_path, aplicacao):
    """Revisão da etapa 7: a pergunta falava de uma revisão já gravada.

    Salvo o A.md, abrir um PDF deixava a revisão dele por baixo, e fechar a
    janela perguntava se ela podia ser descartada - e não fechava.
    """
    import shutil

    from PySide6.QtGui import QCloseEvent

    origem = tmp_path / "A.md"
    shutil.copy(MASSA / "10-prestacao-com-cpf.md", origem)
    janela = JanelaPrincipal()
    janela.menu.botao_anonimizar.click()
    painel = janela.painel_anonimizar
    painel.receber_arquivo(origem)
    painel.abrir_o_salvar()
    painel.gravar(Path(painel.tela_salvar.campo.text()))

    painel.receber_arquivo(COM_TEXTO)
    painel.pdf.conferir_documento(COM_TEXTO)

    evento = QCloseEvent()
    janela.closeEvent(evento)
    assert evento.isAccepted(), "a janela recusou fechar por causa do A.md já salvo"

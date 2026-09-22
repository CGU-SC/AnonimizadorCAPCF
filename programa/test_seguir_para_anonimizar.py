"""Testes do "Seguir para Anonimizar" no fim do Gerar OCR (etapa 8).

O texto conferido vai para a revisão por dentro do programa, sem arquivo no
meio, e o menu passa a marcar "Anonimizar" (RN-16). O Gerar OCR fica como
estava (oitava emenda da spec 003). E o aviso da tela de salvar de lá deixa de
dizer que o Anonimizar "ainda vai ser construído" (RN-17).
"""
import shutil
from pathlib import Path

import pytest

import cpf
import documento
from main import JanelaPrincipal

MASSA = Path(__file__).parent.parent / "dados-exemplo"


@pytest.fixture
def pdf(tmp_path):
    """Uma cópia do PDF de teste numa pasta descartável, para dizer se algum
    arquivo foi gravado ao lado dele."""
    copia = tmp_path / "prestacao.pdf"
    shutil.copy(MASSA / "01-com-texto-e-tabela.pdf", copia)
    return copia


def _janela_na_saida_do_ocr(pdf):
    """A janela inteira, com o Gerar OCR na escolha da saída."""
    janela = JanelaPrincipal()
    janela.menu.botao_ocr.click()
    ocr = janela.painel_ocr
    ficha = documento.conferir(pdf)
    ocr.ficha_atual = ficha
    ocr.aproveitar_o_texto_existente(ficha, documento.texto_da_camada(pdf))
    ocr.tela_conferencia.botao_conferido.click()
    assert ocr.telas.currentWidget() is ocr.tela_saida
    return janela


def test_na_janela_o_botao_do_anonimizar_esta_aceso(aplicacao, pdf):
    janela = _janela_na_saida_do_ocr(pdf)
    assert janela.painel_ocr.tela_saida.botao_anonimizar.isEnabled()
    assert janela.painel_ocr.tela_saida.botao_salvar.isEnabled()


def test_seguir_leva_o_texto_para_a_revisao_e_marca_o_menu(aplicacao, pdf):
    """Critério de aceite da spec 003 (RN-16)."""
    janela = _janela_na_saida_do_ocr(pdf)
    antes = set(pdf.parent.iterdir())

    janela.painel_ocr.tela_saida.botao_anonimizar.click()

    anonimizar = janela.painel_anonimizar
    assert janela.painel.currentWidget() is anonimizar
    assert janela.menu.botao_anonimizar.isChecked()
    assert not janela.menu.botao_ocr.isChecked()
    assert anonimizar.telas.currentWidget() is anonimizar.tela_revisao
    # O texto chega mascarado, como em qualquer outro caminho.
    na_tela = anonimizar.tela_revisao.texto_mascarado()
    assert "XXX" in na_tela
    assert cpf.procurar(na_tela) == []
    # E nada foi gravado no meio do caminho.
    assert set(pdf.parent.iterdir()) == antes


def test_o_caminho_sugerido_sai_do_pdf_que_foi_lido(aplicacao, pdf):
    """Fluxo vindo do Gerar OCR, passo 1c."""
    janela = _janela_na_saida_do_ocr(pdf)
    janela.painel_ocr.tela_saida.botao_anonimizar.click()

    anonimizar = janela.painel_anonimizar
    anonimizar.abrir_o_salvar()
    assert anonimizar.tela_salvar.campo.text() == str(
        pdf.with_name("prestacao - sem CPF.md"))


def test_voltando_ao_gerar_ocr_o_texto_continua_la(aplicacao, pdf):
    """Oitava emenda (b): o Gerar OCR fica exatamente como estava.

    Para voltar, a pessoa passa pela pergunta antes de descartar, porque a
    revisão aberta no Anonimizar ainda não foi salva (etapa 6). Descartada a
    revisão, o Gerar OCR está do jeito que ela deixou, com o texto conferido.
    """
    janela = _janela_na_saida_do_ocr(pdf)
    ocr = janela.painel_ocr
    conferido = ocr.tela_conferencia.texto_conferido()
    ocr.tela_saida.botao_anonimizar.click()

    janela.menu.botao_ocr.click()
    anonimizar = janela.painel_anonimizar
    assert anonimizar.telas.currentWidget() is anonimizar.tela_descartar
    anonimizar.tela_descartar.botao_descartar.click()

    assert janela.painel.currentWidget() is ocr
    assert ocr.telas.currentWidget() is ocr.tela_saida
    assert ocr.tela_conferencia.texto_conferido() == conferido
    # Dá para salvar o texto como está, ou seguir de novo.
    assert ocr.tela_saida.botao_salvar.isEnabled()
    assert ocr.tela_saida.botao_anonimizar.isEnabled()


def test_seguir_de_novo_depois_de_salvar_abre_sem_perguntar(aplicacao, pdf):
    """Revisão salva não tem o que perder: o segundo "Seguir" abre direto."""
    janela = _janela_na_saida_do_ocr(pdf)
    ocr = janela.painel_ocr
    anonimizar = janela.painel_anonimizar
    ocr.tela_saida.botao_anonimizar.click()
    anonimizar.abrir_o_salvar()
    anonimizar.gravar(Path(anonimizar.tela_salvar.campo.text()))

    janela.menu.botao_ocr.click()
    assert janela.painel.currentWidget() is ocr
    ocr.tela_saida.botao_anonimizar.click()

    assert anonimizar.telas.currentWidget() is anonimizar.tela_revisao


def test_a_guarda_do_segundo_seguir_segura_uma_revisao_nao_salva(aplicacao, pdf):
    """A defesa do código, mesmo sem caminho de tela que chegue até ela.

    Pela tela, todo caminho de volta ao Gerar OCR já passa pela pergunta do
    menu. A guarda existe para o dia em que surgir outro caminho - e um texto
    chegando por cima de uma revisão não salva nunca pode descartá-la calado.
    """
    janela = _janela_na_saida_do_ocr(pdf)
    anonimizar = janela.painel_anonimizar
    anonimizar.receber_arquivo(MASSA / "10-prestacao-com-cpf.md")

    janela._seguir_para_anonimizar(pdf, ["texto de outro documento"])

    assert anonimizar.telas.currentWidget() is anonimizar.tela_descartar
    assert anonimizar.tela_descartar.titulo.text() == (
        "A revisão deste documento ainda não foi salva")


def test_o_aviso_da_tela_de_salvar_do_ocr_aponta_para_o_anonimizar(aplicacao, pdf):
    """Critério de aceite da spec 003 (RN-17)."""
    from PySide6.QtWidgets import QLabel

    janela = _janela_na_saida_do_ocr(pdf)
    ocr = janela.painel_ocr
    ocr.escolher_onde_salvar()

    frases = " ".join(rotulo.text() for rotulo in ocr.tela_salvar.findChildren(QLabel))
    assert "CPFs inteiros" in frases
    assert "ainda vai ser construído" not in frases
    assert "Seguir para Anonimizar" in frases


def test_com_conferencia_aberta_a_pergunta_diz_onde_ficou_o_texto(aplicacao, pdf,
                                                                  tmp_path):
    """Revisão da etapa 8: a pessoa pedia uma coisa e ouvia falar de outra.

    Com um PDF na conferência do Anonimizar, o "Seguir" troca de módulo e
    pergunta sobre aquele documento - não sobre o que ela acabou de conferir.
    Nada se perde, mas sem uma linha dizendo isso não há como entender.
    """
    outro = tmp_path / "do-anonimizar.pdf"
    shutil.copy(MASSA / "01-com-texto-e-tabela.pdf", outro)

    janela = _janela_na_saida_do_ocr(pdf)
    anonimizar = janela.painel_anonimizar
    anonimizar.receber_arquivo(outro)
    anonimizar.pdf.conferir_documento(outro)
    anonimizar.pdf.tela_decisao.botao_aproveitar.click()

    janela.painel_ocr.tela_saida.botao_anonimizar.click()

    frase = anonimizar.tela_descartar.explicacao.text()
    assert outro.name in frase
    assert "continua no Gerar OCR" in frase

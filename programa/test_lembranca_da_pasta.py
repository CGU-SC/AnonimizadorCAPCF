"""A pasta do último arquivo aberto, lembrada de um uso para o outro (RN-43 da
spec 002, emenda de 14/11/2026 - funcionalidade 11).

O `preferencias.ini` de cada teste é o arquivo isolado do `conftest.py`, e as
pastas "de documentos" são provisórias: nada daqui toca no desta máquina.
"""
from PySide6.QtWidgets import QFileDialog

import lembranca_da_pasta
import preferencias
from main import JanelaPrincipal


def _documento(pasta, nome="prestacao-de-contas.md"):
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / nome
    arquivo.write_text("Relatório sem CPF.\n", encoding="utf-8")
    return arquivo


def _pasta_em_que_a_janela_abre(monkeypatch, painel):
    """Clica em "Escolher arquivo…" sem abrir a janela do Windows, e devolve a
    pasta em que ela abriria."""
    pedidas = []

    def janela_de_mentira(_pai, _titulo, pasta, _filtro):
        pedidas.append(pasta)
        return "", ""

    monkeypatch.setattr(QFileDialog, "getOpenFileName", janela_de_mentira)
    painel._abrir_seletor_de_arquivo()
    return pedidas[0]


def test_sem_nada_lembrado_a_janela_abre_como_sempre():
    assert lembranca_da_pasta.pasta_inicial() == ""


def test_guarda_a_pasta_e_nunca_o_nome_do_arquivo(tmp_path):
    """Premissa da emenda: a pasta diz onde os documentos moram, o nome diria
    o que eles têm."""
    pasta = tmp_path / "Prestações 2026"
    lembranca_da_pasta.lembrar(_documento(pasta, "bolsistas-da-fundacao.md"))
    assert lembranca_da_pasta.pasta_inicial() == str(pasta.resolve())
    texto = preferencias.caminho().read_text(encoding="utf-8")
    assert "bolsistas" not in texto
    assert ".md" not in texto


def test_a_pasta_volta_com_as_maiusculas_e_os_acentos(tmp_path):
    """Lida sem passar para minúsculas, como o resto do preferencias.ini."""
    pasta = tmp_path / "Prestações FAPEU"
    lembranca_da_pasta.lembrar(_documento(pasta))
    assert lembranca_da_pasta.pasta_inicial().endswith("Prestações FAPEU")


def test_a_pasta_que_sumiu_vale_como_nada_lembrado(tmp_path):
    """Premissa da emenda: o pendrive tirado abre a janela como antes, sem aviso."""
    arquivo = _documento(tmp_path / "pendrive")
    lembranca_da_pasta.lembrar(arquivo)
    arquivo.unlink()
    arquivo.parent.rmdir()
    assert lembranca_da_pasta.pasta_inicial() == ""


def test_a_pasta_de_rede_fora_do_ar_nao_congela_a_janela(tmp_path, monkeypatch):
    """Lente crítica da funcionalidade 11: com a rede fora, o Windows demora a
    dizer que a pasta não existe. Passado o prazo, vale como nada lembrado, sem
    esperar o servidor."""
    import threading
    import time

    rede = tmp_path / "rede"
    lembranca_da_pasta.lembrar(_documento(rede))
    servidor_que_nao_responde = threading.Event()
    isdir_de_verdade = lembranca_da_pasta.os.path.isdir

    # Só a pasta "da rede" demora: o resto do Python continua respondendo.
    def isdir_com_a_rede_fora(pasta):
        if str(pasta) == str(rede.resolve()):
            return servidor_que_nao_responde.wait(30)
        return isdir_de_verdade(pasta)

    monkeypatch.setattr(lembranca_da_pasta.os.path, "isdir", isdir_com_a_rede_fora)
    monkeypatch.setattr(lembranca_da_pasta, "SEGUNDOS_PARA_CONFERIR", 0.2)
    inicio = time.monotonic()
    try:
        assert lembranca_da_pasta.pasta_inicial() == ""
        assert time.monotonic() - inicio < 2
    finally:
        servidor_que_nao_responde.set()


def test_lembrar_nao_mexe_no_motor_nem_no_tema(tmp_path):
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    preferencias.gravar("tema", "tema", "claro")
    lembranca_da_pasta.lembrar(_documento(tmp_path / "docs"))
    assert preferencias.ler("gerar_ocr", "motor") == "tesseract"
    assert preferencias.ler("tema", "tema") == "claro"


def test_a_mesma_pasta_nao_reescreve_o_arquivo(tmp_path, monkeypatch):
    pasta = tmp_path / "docs"
    lembranca_da_pasta.lembrar(_documento(pasta, "um.md"))
    gravacoes = []
    monkeypatch.setattr(preferencias, "gravar", lambda *a: gravacoes.append(a))
    lembranca_da_pasta.lembrar(_documento(pasta, "outro.md"))
    assert gravacoes == []


def test_arrastar_no_anonimizar_conta_e_vale_para_o_gerar_ocr(tmp_path, monkeypatch):
    """Respostas do levantamento: arrastar conta, e a pasta é uma só para os
    dois módulos."""
    janela = JanelaPrincipal()
    pasta = tmp_path / "Prestações"
    janela.painel_anonimizar.receber_arquivo(_documento(pasta))
    assert (_pasta_em_que_a_janela_abre(monkeypatch, janela.painel_ocr)
            == str(pasta.resolve()))


def test_o_gerar_ocr_lembra_e_o_anonimizar_abre_la(tmp_path, monkeypatch):
    janela = JanelaPrincipal()
    ocr = janela.painel_ocr
    # Só a lembrança está em teste: a leitura do PDF tem os testes dela.
    monkeypatch.setattr(ocr, "_receber_documento", lambda caminho: None)
    pasta = tmp_path / "Escaneados"
    ocr.receber_documento(_documento(pasta, "oficio.pdf"))
    assert (_pasta_em_que_a_janela_abre(monkeypatch, janela.painel_anonimizar)
            == str(pasta.resolve()))


def test_um_programa_novo_abre_na_pasta_lembrada(tmp_path, monkeypatch):
    """De um uso para o outro: fechar e abrir de novo mantém a pasta."""
    janela = JanelaPrincipal()
    pasta = tmp_path / "Prestações"
    janela.painel_anonimizar.receber_arquivo(_documento(pasta))
    janela.close()
    outra = JanelaPrincipal()
    assert (_pasta_em_que_a_janela_abre(monkeypatch, outra.painel_anonimizar)
            == str(pasta.resolve()))

"""Testes do arquivo `.md` e das telas que levam até ele.

Quase tudo o que estes testes guardam é invisível na tela: que o arquivo não
leva nenhum recado do programa dentro, que nada é gravado pela metade, que o
PDF de origem continua intacto. São as promessas que só se descobrem quebradas
depois que o arquivo já foi parar na conversa com o assistente de IA.
"""
from pathlib import Path

import pytest

import arquivo_md
import documento
import painel_ocr

MASSA = Path(__file__).parent.parent / "dados-exemplo"


# ------------------------------------------------------------ o arquivo

def test_o_caminho_sugerido_e_ao_lado_do_documento():
    """Regra RN-15: a mesma pasta, o mesmo nome, terminação .md."""
    pdf = Path("C:/processos/2026/prestacao-042.pdf")

    assert arquivo_md.caminho_sugerido(pdf) == Path("C:/processos/2026/prestacao-042.md")


def test_o_arquivo_tem_o_texto_e_mais_nada():
    """Regra RN-11 e critério de aceite da spec 002.

    "Dado que o arquivo foi gravado, quando ele é aberto, então ele contém o
    texto do documento e nenhuma linha de aviso escrita pelo programa." Recado
    no meio do texto ninguém lê, e ele ainda viaja para dentro da conversa com o
    assistente, onde parece fazer parte do documento.
    """
    paginas = ["texto da primeira pagina", "texto da segunda pagina"]

    conteudo = arquivo_md.montar_conteudo(paginas)

    assert conteudo == "texto da primeira pagina\n\ntexto da segunda pagina\n"
    for recado in ["OCR", "página", "pagina 1", "conferid", "gerado", "---",
                   "Anomizador", "CPF"]:
        if recado in paginas[0] or recado in paginas[1]:
            continue
        assert recado not in conteudo, f"o programa escreveu '{recado}' dentro do arquivo"


def test_grava_e_o_arquivo_fica_exatamente_como_o_texto(tmp_path):
    destino = tmp_path / "saida.md"
    conteudo = arquivo_md.montar_conteudo(["linha com acentuação: ção, é, ã"])

    arquivo_md.gravar(destino, conteudo)

    assert destino.read_text(encoding="utf-8") == conteudo


def test_gravacao_interrompida_nao_deixa_arquivo_pela_metade(tmp_path, monkeypatch):
    """Um .md pela metade seria arrastado para a conversa como se estivesse inteiro.

    A gravação passa por um arquivo provisório, e só no fim troca de nome.
    Interrompendo no meio, não sobra nem o definitivo, nem o provisório.
    """
    destino = tmp_path / "saida.md"

    def estourar(*_):
        raise OSError("disco cheio no meio da gravação")

    monkeypatch.setattr(arquivo_md.os, "replace", estourar)

    with pytest.raises(OSError):
        arquivo_md.gravar(destino, "conteudo qualquer")

    assert not destino.exists(), "ficou um arquivo pela metade"
    assert list(tmp_path.iterdir()) == [], "ficou o provisório para trás"


def test_nome_livre_nao_apaga_nada(tmp_path):
    ocupado = tmp_path / "saida.md"
    ocupado.write_text("isto ja existia", encoding="utf-8")
    (tmp_path / "saida (2).md").write_text("este tambem", encoding="utf-8")

    livre = arquivo_md.caminho_livre(ocupado)

    assert livre == tmp_path / "saida (3).md"
    assert not livre.exists()


# ------------------------------------------------------------ o caminho nas telas

def _painel_na_conferencia(copia_do_pdf):
    """Um painel já com o texto aproveitado e aberto na conferência."""
    painel = painel_ocr.PainelOcr()
    ficha = documento.conferir(copia_do_pdf)
    painel.ficha_atual = ficha
    painel.aproveitar_o_texto_existente(ficha, documento.texto_da_camada(ficha.caminho))
    return painel


@pytest.fixture
def copia_do_pdf(tmp_path):
    """Uma cópia do documento de teste numa pasta descartável.

    O arquivo .md vai para a pasta do PDF, e a massa de teste do projeto não
    pode ganhar arquivos a cada rodada de testes.
    """
    import shutil
    copia = tmp_path / "prestacao.pdf"
    shutil.copy(MASSA / "01-com-texto-e-tabela.pdf", copia)
    return copia


def test_painel_sozinho_nao_oferece_um_anonimizar_que_nao_leva_a_lugar_nenhum(
        aplicacao, copia_do_pdf):
    """Montado fora da janela, o painel não tem para onde mandar o texto.

    Até a etapa 8 do Anonimizar este teste guardava o critério da spec 002 de
    o botão ficar apagado porque "o módulo 3 ainda não foi construído" - que a
    RN-16 da spec 003 substituiu. Agora ele fica apagado só quando ninguém vai
    receber o texto: botão que parece pronto e não faz nada é lido como defeito.
    O botão aceso, na janela de verdade, está em test_seguir_para_anonimizar.
    """
    painel = _painel_na_conferencia(copia_do_pdf)

    painel.tela_conferencia.botao_conferido.click()

    assert painel.telas.currentWidget() is painel.tela_saida
    assert painel.tela_saida.botao_salvar.isEnabled()
    assert not painel.tela_saida.botao_anonimizar.isEnabled()


def test_a_tela_de_salvar_vem_com_o_caminho_preenchido(aplicacao, copia_do_pdf):
    """Critério de aceite da spec 002, sobre a tela de salvar."""
    painel = _painel_na_conferencia(copia_do_pdf)

    painel.seguir_para_a_saida()
    painel.escolher_onde_salvar()

    assert painel.telas.currentWidget() is painel.tela_salvar
    assert painel.tela_salvar.campo.text() == str(copia_do_pdf.with_suffix(".md"))
    assert not painel.tela_salvar.campo.isReadOnly(), "o caminho tem que ser editável"


def test_salvar_grava_o_texto_corrigido_e_mostra_onde(aplicacao, copia_do_pdf):
    """Critério de aceite: o que vai para o arquivo é o texto já corrigido."""
    painel = _painel_na_conferencia(copia_do_pdf)
    painel.tela_conferencia.editor.setPlainText("PAGINA UM CORRIGIDA A MAO")
    destino = copia_do_pdf.with_suffix(".md")

    painel.seguir_para_a_saida()
    painel.escolher_onde_salvar()
    painel.tentar_salvar(destino)

    assert painel.telas.currentWidget() is painel.tela_gravado
    assert painel.tela_gravado.caminho.text() == str(destino)
    conteudo = destino.read_text(encoding="utf-8")
    assert conteudo.startswith("PAGINA UM CORRIGIDA A MAO")


def test_arquivo_que_ja_existe_faz_perguntar_antes(aplicacao, copia_do_pdf):
    """Regra RN-16 e critério de aceite: nunca sobrescrever calado."""
    painel = _painel_na_conferencia(copia_do_pdf)
    destino = copia_do_pdf.with_suffix(".md")
    destino.write_text("trabalho anterior que nao pode sumir", encoding="utf-8")

    painel.seguir_para_a_saida()
    painel.escolher_onde_salvar()
    painel.tentar_salvar(destino)

    assert painel.telas.currentWidget() is painel.tela_sobrescrever
    assert destino.read_text(encoding="utf-8") == "trabalho anterior que nao pode sumir", (
        "o programa escreveu por cima antes de perguntar"
    )


def test_salvar_com_outro_nome_nao_toca_no_que_ja_existe(aplicacao, copia_do_pdf):
    painel = _painel_na_conferencia(copia_do_pdf)
    destino = copia_do_pdf.with_suffix(".md")
    destino.write_text("trabalho anterior", encoding="utf-8")

    painel.seguir_para_a_saida()
    painel.escolher_onde_salvar()
    painel.tentar_salvar(destino)
    painel.salvar_com_outro_nome()

    assert painel.telas.currentWidget() is painel.tela_salvar
    assert painel.tela_salvar.campo.text() == str(copia_do_pdf.with_name("prestacao (2).md"))
    assert destino.read_text(encoding="utf-8") == "trabalho anterior"


def test_escrever_por_cima_so_depois_de_confirmar(aplicacao, copia_do_pdf):
    painel = _painel_na_conferencia(copia_do_pdf)
    destino = copia_do_pdf.with_suffix(".md")
    destino.write_text("trabalho anterior", encoding="utf-8")

    painel.seguir_para_a_saida()
    painel.escolher_onde_salvar()
    painel.tentar_salvar(destino)
    painel.escrever_por_cima()

    assert painel.telas.currentWidget() is painel.tela_gravado
    assert "trabalho anterior" not in destino.read_text(encoding="utf-8")


def test_pasta_sem_permissao_nao_perde_o_trabalho(aplicacao, copia_do_pdf, monkeypatch):
    """Falhar a gravação deixa a pessoa na tela de salvar, com tudo intacto."""
    painel = _painel_na_conferencia(copia_do_pdf)
    painel.tela_conferencia.editor.setPlainText("correcao que nao pode sumir")

    def recusar(*_):
        raise PermissionError("acesso negado")

    monkeypatch.setattr(painel_ocr, "gravar", recusar)

    painel.seguir_para_a_saida()
    painel.escolher_onde_salvar()
    painel.tentar_salvar(copia_do_pdf.with_suffix(".md"))

    assert painel.telas.currentWidget() is painel.tela_salvar
    assert not painel.tela_salvar.problema.isHidden(), "não avisou que não gravou"
    assert painel.tela_conferencia.texto_conferido()[0] == "correcao que nao pode sumir"


def test_o_pdf_de_origem_continua_identico_depois_de_salvar(aplicacao, copia_do_pdf):
    """Critério de aceite da spec 002, agora sobre o processo inteiro.

    "Dado que o PDF de origem é comparado antes e depois de todo o processo,
    então ele está idêntico." O .md é gravado ao lado dele, na mesma pasta - o
    lugar exato em que uma troca de terminação mal feita escreveria por cima.
    """
    antes = copia_do_pdf.read_bytes()
    painel = _painel_na_conferencia(copia_do_pdf)

    painel.seguir_para_a_saida()
    painel.escolher_onde_salvar()
    painel.tentar_salvar(copia_do_pdf.with_suffix(".md"))

    assert copia_do_pdf.read_bytes() == antes


# ------------------------------------------------------------ antes de descartar (RN-1)

def test_sair_com_texto_nao_salvo_pergunta_antes(aplicacao, copia_do_pdf):
    """Regra RN-1 da spec 002.

    Sem a pergunta, meia hora de correção sumia com um clique em "Processar
    outro documento", sem aviso e sem volta.
    """
    painel = _painel_na_conferencia(copia_do_pdf)
    painel.tela_conferencia.editor.setPlainText("correcao de meia hora")

    painel.voltar_para_escolher()

    assert painel.telas.currentWidget() is painel.tela_descartar
    assert painel.tela_conferencia.texto_conferido()[0] == "correcao de meia hora", (
        "o texto foi jogado fora antes de a pessoa responder"
    )


def test_voltar_e_salvar_devolve_tudo_como_estava(aplicacao, copia_do_pdf):
    painel = _painel_na_conferencia(copia_do_pdf)
    painel.tela_conferencia.editor.setPlainText("correcao de meia hora")

    painel.voltar_para_escolher()
    painel._voltar_de_onde_estava()

    assert painel.telas.currentWidget() is painel.tela_conferencia
    assert painel.tela_conferencia.texto_conferido()[0] == "correcao de meia hora"


def test_descartar_e_seguir_joga_fora_e_segue(aplicacao, copia_do_pdf):
    painel = _painel_na_conferencia(copia_do_pdf)
    painel.tela_conferencia.editor.setPlainText("correcao que a pessoa desistiu")

    painel.voltar_para_escolher()
    painel._descartar_e_seguir()

    assert painel.telas.currentWidget() is painel.tela_escolher
    assert painel.tela_conferencia.texto_conferido() == []


def test_depois_de_salvar_nao_pergunta_mais(aplicacao, copia_do_pdf):
    """Pergunta que aparece sem motivo ensina a clicar em 'sim' sem ler."""
    painel = _painel_na_conferencia(copia_do_pdf)
    painel.seguir_para_a_saida()
    painel.escolher_onde_salvar()
    painel.tentar_salvar(copia_do_pdf.with_suffix(".md"))

    painel.voltar_para_escolher()

    assert painel.telas.currentWidget() is painel.tela_escolher


def test_arrastar_outro_pdf_com_texto_nao_salvo_pergunta_antes(aplicacao, copia_do_pdf):
    """O caminho mais fácil de perder trabalho sem querer: soltar outro arquivo."""
    painel = _painel_na_conferencia(copia_do_pdf)

    painel.receber_documento(MASSA / "02-imprimir-para-pdf.pdf")

    assert painel.telas.currentWidget() is painel.tela_descartar
    assert painel.ficha_atual.caminho == copia_do_pdf, (
        "o documento novo tomou o lugar do antigo antes de a pessoa responder"
    )


def test_antes_da_conferencia_nao_ha_o_que_perguntar(aplicacao):
    """Escolhendo ou lendo, ainda não existe texto da pessoa para perder."""
    painel = painel_ocr.PainelOcr()

    painel.voltar_para_escolher()

    assert painel.telas.currentWidget() is painel.tela_escolher


def test_a_pergunta_diz_quantas_paginas_foram_corrigidas(aplicacao, copia_do_pdf):
    """Nenhuma correção perde pouco; trinta correções perdem uma tarde."""
    painel = _painel_na_conferencia(copia_do_pdf)
    painel.tela_conferencia.editor.setPlainText("mexi")

    painel.voltar_para_escolher()

    assert "1 com correção sua" in painel.tela_descartar.explicacao.text()


def test_pergunta_por_cima_da_pergunta_nao_prende_ninguem(aplicacao, copia_do_pdf):
    """Teste de regressão do defeito mais grave achado na revisão da etapa 6.

    Com a pergunta de descartar já na tela, soltar outro documento por cima
    fazia o programa guardar a própria pergunta como "o lugar para onde voltar".
    "Voltar e salvar" não saía do lugar, e a única saída que funcionava era a
    que jogava o texto fora - a perda que a pergunta existe para evitar.
    """
    painel = _painel_na_conferencia(copia_do_pdf)
    painel.tela_conferencia.editor.setPlainText("correcao de meia hora")

    painel.receber_documento(MASSA / "02-imprimir-para-pdf.pdf")
    painel.receber_documento(MASSA / "03-conteudo-girado.pdf")
    painel._voltar_de_onde_estava()

    assert painel.telas.currentWidget() is painel.tela_conferencia, (
        "'Voltar e salvar' não saiu da pergunta"
    )
    assert painel.tela_conferencia.texto_conferido()[0] == "correcao de meia hora"


def test_nome_sem_pasta_vai_para_a_pasta_do_documento(aplicacao, copia_do_pdf):
    """Teste de regressão do segundo defeito achado na revisão da etapa 6.

    Digitar só "saida.md" gravava o arquivo na pasta de onde o programa foi
    aberto - aqui, a raiz do projeto, dentro do repositório. Um arquivo com os
    CPFs inteiros, perdido onde ninguém ia procurar.
    """
    from PySide6.QtWidgets import QPushButton

    painel = _painel_na_conferencia(copia_do_pdf)
    painel.seguir_para_a_saida()
    painel.escolher_onde_salvar()
    painel.tela_salvar.campo.setText("saida.md")

    salvar = [b for b in painel.tela_salvar.findChildren(QPushButton)
              if b.text() == "Salvar"][0]
    salvar.click()

    esperado = copia_do_pdf.parent / "saida.md"
    assert esperado.exists(), "o arquivo não foi para a pasta do documento"
    assert painel.tela_gravado.caminho.text() == str(esperado), (
        "a tela de sucesso tem que mostrar o caminho completo"
    )
    assert not (Path.cwd() / "saida.md").exists(), (
        "o arquivo caiu na pasta de onde o programa foi aberto"
    )


def test_o_md_nunca_cai_por_cima_do_pdf_de_origem():
    """Regra RN-17: o PDF de origem nunca é alterado, e o .md mora ao lado dele.

    Conferido nesta revisão: nem digitando o próprio nome do PDF no campo o
    arquivo cai por cima dele.
    """
    for nome in ["doc.pdf", "doc.PDF", "relatorio.final.pdf"]:
        pdf = Path("C:/processos") / nome
        assert arquivo_md.caminho_sugerido(pdf) != pdf


def test_a_janela_do_windows_nao_pergunta_sobre_substituir(aplicacao, copia_do_pdf,
                                                           monkeypatch):
    """Quem pergunta sobre apagar o arquivo é a tela do programa, e mais ninguém.

    A janela do Windows perguntava "deseja substituir?" e, respondido que sim,
    só devolvia o caminho - nada era gravado. Quem respondeu achava ter mandado
    salvar, e o programa parecia não fazer nada (achado na conferência da etapa
    5 do Anonimizar, em 18/09/2026, e igual aqui).
    """
    from PySide6.QtWidgets import QFileDialog

    pedidos = {}

    def falsa_janela(*args, **kwargs):
        pedidos.update(kwargs)
        return "", ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", falsa_janela)
    painel = _painel_na_conferencia(copia_do_pdf)
    painel.seguir_para_a_saida()
    painel.escolher_onde_salvar()
    painel.tela_salvar._escolher_pasta()

    assert pedidos["options"] == QFileDialog.Option.DontConfirmOverwrite

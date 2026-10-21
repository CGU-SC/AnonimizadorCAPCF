"""Testes do painel do "Anonimizar" e da tela de revisão.

Eles não substituem olhar a tela: pegam a classe de defeito que olhar pega
tarde demais - a frase que sai cortada, a contagem que não bate com o texto, e
o pior de todos, um CPF que aparece inteiro na tela de revisão.
"""
from pathlib import Path

from PySide6.QtGui import QTextCharFormat, QTextCursor

import cpf
import estilo
from painel_anonimizar import PainelAnonimizar
from tela_revisao import AVISO_SEM_CPF, TelaRevisao, _posicao_no_qt

MASSA = Path(__file__).parent.parent / "dados-exemplo"


def _painel_com(nome, aplicacao):
    painel = PainelAnonimizar()
    painel.receber_arquivo(MASSA / nome)
    return painel


def test_o_md_da_massa_abre_na_revisao_sem_nenhum_cpf_inteiro(aplicacao):
    painel = _painel_com("10-prestacao-com-cpf.md", aplicacao)
    assert painel.telas.currentWidget() is painel.tela_revisao

    na_tela = painel.tela_revisao.texto_mascarado()
    # Passando o texto da tela pelo motor de novo, não pode sobrar nada: todo
    # número que ele acha no arquivo saiu mascarado.
    assert cpf.procurar(na_tela) == []
    # E o que não é CPF continua inteiro, inclusive o número colado a outro
    # dígito, que a massa tem de propósito (regra RN-3).
    for inteiro in ("12.345.678/0001-90", "23080.012345/2026-11",
                    "9111.111.111-11", "1234 5678 910"):
        assert inteiro in na_tela, inteiro


def test_a_contagem_bate_com_o_que_esta_mascarado_no_texto(aplicacao):
    painel = _painel_com("10-prestacao-com-cpf.md", aplicacao)
    revisao = painel.tela_revisao

    # O mesmo número por dois caminhos: o selo da tela, e a contagem de trechos
    # mascarados no próprio texto que está na tela.
    assert revisao.selo_encontrados.text() == "12 números encontrados"
    assert revisao.selo_suspeitos.text() == "9 suspeitos"
    assert revisao.texto_mascarado().count("XXX") == 12


def test_o_selo_dos_validos_conta_o_que_o_texto_marca_de_vermelho(aplicacao):
    """A contagem do alto e as marcas do texto contam a mesma coisa.

    O selo vermelho ("CPF válido") conta os números do tipo "passa na conta"; no texto, são os
    de traço reto e vermelho. Os suspeitos - inclusive o "quase CPF" que passa
    na conta - ficam no amarelo, com traço ondulado.
    """
    painel = _painel_com("10-prestacao-com-cpf.md", aplicacao)
    revisao = painel.tela_revisao
    assert revisao.selo_validos.text() == "3 CPFs válidos"
    assert estilo.COR_ERRO_TEXTO in revisao.selo_validos.styleSheet()
    assert estilo.COR_ALERTA in revisao.selo_suspeitos.styleSheet()

    vermelhos = 0
    cursor = revisao.texto.textCursor()
    for ocorrencia in cpf.procurar(
            (MASSA / "10-prestacao-com-cpf.md").read_text(encoding="utf-8")):
        cursor.setPosition(ocorrencia.inicio + 1)
        formato = cursor.charFormat()
        e_vermelho = formato.foreground().color().name() == estilo.COR_ERRO_TEXTO
        reto = formato.underlineStyle() == QTextCharFormat.SingleUnderline
        assert e_vermelho == reto == (not ocorrencia.suspeito), ocorrencia.original
        vermelhos += e_vermelho
    assert vermelhos == 3


def test_o_aviso_de_nenhum_cpf_aparece_e_o_texto_fica_como_veio(aplicacao):
    painel = _painel_com("11-sem-cpf.md", aplicacao)
    revisao = painel.tela_revisao

    assert revisao.aviso_sem_cpf.isVisible() or revisao.aviso_sem_cpf.isVisibleTo(painel)
    assert not revisao.selo_encontrados.isVisibleTo(painel)
    assert revisao.texto_mascarado() == (MASSA / "11-sem-cpf.md").read_text(
        encoding="utf-8")


def test_os_avisos_da_revisao_cabem_inteiros(aplicacao):
    """Regressão da revisão da etapa 3: o aviso reservava 32 e precisava de 34.

    É a classe de defeito que o CLAUDE.md registra: a última linha some para
    fora da borda sem nada acusar. Este teste percorre as frases de largura fixa
    da revisão e falha se alguma reservar menos do que precisa.
    """
    from lista_de_achados import LARGURA, _nada_para_olhar
    import estilo as _estilo

    revisao = TelaRevisao(ao_anonimizar_outro=lambda: None)
    revisao.mostrar("sem.md", "Ata sem número nenhum.", [])

    avisos = [
        (revisao.explicacao_sem_cpf, revisao.LARGURA_DO_TEXTO_DO_AVISO),
        (_nada_para_olhar(), LARGURA - _estilo.ESPACO_4),
    ]
    for rotulo, largura in avisos:
        assert rotulo.minimumHeight() >= rotulo.heightForWidth(largura), (
            f"a frase '{rotulo.text()[:30]}…' vai sair cortada")


def test_arquivo_ja_anonimizado_nao_acha_nada(aplicacao):
    painel = _painel_com("10-prestacao-com-cpf - sem CPF.md", aplicacao)
    assert painel.tela_revisao.aviso_sem_cpf.isVisibleTo(painel)


def test_o_texto_da_revisao_nao_aceita_digitacao(aplicacao):
    """Regra RN-8: aqui só se mascara e se desfaz máscara."""
    painel = _painel_com("10-prestacao-com-cpf.md", aplicacao)
    assert painel.tela_revisao.texto.isReadOnly()


def test_a_tabela_do_documento_continua_alinhada_na_tela(aplicacao):
    painel = _painel_com("10-prestacao-com-cpf.md", aplicacao)
    linhas = [
        linha for linha in painel.tela_revisao.texto_mascarado().splitlines()
        if linha.startswith("| Beltrana") or linha.startswith("| Ciclano")
    ]
    assert len(linhas) == 2
    assert len(linhas[0]) == len(linhas[1])
    assert linhas[0].count("|") == 5


def test_arquivo_vazio_mostra_o_erro_e_volta_para_a_escolha(aplicacao):
    painel = _painel_com("15-vazio.md", aplicacao)
    assert painel.telas.currentWidget() is painel.tela_erro
    assert "está vazio" in painel.tela_erro.explicacao.text()

    painel.voltar_para_escolher()
    assert painel.telas.currentWidget() is painel.tela_escolher


def test_arquivo_que_nao_e_texto_mostra_o_erro(aplicacao):
    painel = _painel_com("16-planilha-renomeada.md", aplicacao)
    assert painel.telas.currentWidget() is painel.tela_erro
    assert "não parece ser texto" in painel.tela_erro.explicacao.text()


def test_a_caixa_de_erro_cabe_a_frase_inteira(aplicacao):
    """A frase longa não pode sair cortada, como já aconteceu no Gerar OCR."""
    painel = _painel_com("16-planilha-renomeada.md", aplicacao)
    explicacao = painel.tela_erro.explicacao
    assert explicacao.minimumHeight() >= explicacao.heightForWidth(
        painel.tela_erro.LARGURA_DO_TEXTO)
    assert explicacao.minimumHeight() > 20


def test_o_pdf_entra_pelo_caminho_do_pdf(aplicacao):
    """Desde a etapa 7, o PDF anda por aqui: conferência do documento primeiro.

    Até a etapa 6 ele recebia um aviso dizendo que o caminho dele viria depois.
    """
    painel = PainelAnonimizar()
    painel.receber_arquivo(MASSA / "01-com-texto-e-tabela.pdf")

    assert painel.telas.currentWidget() is painel.pdf.tela_verificando
    # A conferência do documento acontece logo depois de a tela de espera
    # aparecer. Com texto por dentro, a tela seguinte é a de decidir, sem o
    # cartão do Gerar OCR no meio (rascunho 08, estado 3b; oitava emenda).
    painel.pdf.conferir_documento(MASSA / "01-com-texto-e-tabela.pdf")
    assert painel.telas.currentWidget() is painel.pdf.tela_decisao


def test_o_pdf_sem_texto_abre_a_tela_de_ler_com_o_motor(aplicacao):
    """Rascunho 08, estado 3a: nome, páginas e a escolha do motor antes de ler."""
    pdf = MASSA / "02-imprimir-para-pdf.pdf"
    painel = PainelAnonimizar()
    painel.receber_arquivo(pdf)
    painel.pdf.conferir_documento(pdf)

    tela = painel.pdf.tela_de_ler
    assert painel.telas.currentWidget() is tela
    assert tela.titulo.text() == "Este documento precisa ser lido"
    assert pdf.name in tela.legenda.text()
    # Emenda de 18/10/2026 da spec 002: o PaddleOCR vem marcado (RN-25).
    assert tela.escolha_do_motor.paddleocr.isChecked()
    assert not tela.escolha_do_motor.ia_local.isEnabled()
    assert tela.botao_ler.text().startswith("Ler as ")


def test_ignorar_o_texto_leva_a_tela_de_ler_e_ela_volta_a_decisao(aplicacao):
    """Rascunho 08, estado 3c: quem mudar de ideia volta a decidir."""
    pdf = MASSA / "01-com-texto-e-tabela.pdf"
    painel = PainelAnonimizar()
    painel.receber_arquivo(pdf)
    painel.pdf.conferir_documento(pdf)

    painel.pdf.tela_decisao.botao_ignorar.click()
    tela = painel.pdf.tela_de_ler
    assert painel.telas.currentWidget() is tela
    assert tela.titulo.text() == "Ler as imagens deste documento"
    assert "será ignorado" in tela.legenda.text()

    tela.botao_outro.click()
    assert painel.telas.currentWidget() is painel.pdf.tela_decisao


def test_arquivo_de_outro_tipo_nao_promete_etapa_seguinte(aplicacao, tmp_path):
    """Regressão da revisão da etapa 2: o .docx recebia a frase do PDF.

    Word e planilha estão fora do escopo da spec: não entram nesta versão nem
    nas seguintes, e a tela não pode sugerir que entram.
    """
    arquivo = tmp_path / "relatorio.docx"
    arquivo.write_bytes(b"PK")
    painel = PainelAnonimizar()
    painel.receber_arquivo(arquivo)
    frase = painel.tela_erro.explicacao.text()
    assert "de outro tipo" in frase
    assert "etapa seguinte" not in frase


def test_sair_da_revisao_solta_o_texto(aplicacao):
    """Sem isto, o texto do documento anterior ficaria guardado na tela.

    Desde a etapa 6, sair pergunta antes: o texto só é solto depois de a pessoa
    dizer que pode descartar.
    """
    painel = _painel_com("10-prestacao-com-cpf.md", aplicacao)
    painel.voltar_para_escolher()
    painel.tela_descartar.botao_descartar.click()
    assert painel.tela_revisao.texto_mascarado() == ""


def test_o_destaque_cai_certo_com_emoji_antes_do_numero(aplicacao):
    """Regressão da revisão da etapa 2: o destaque escorregava uma casa.

    O Qt conta símbolo fora do comum como duas casas, e o Python como uma.
    """
    revisao = TelaRevisao(ao_anonimizar_outro=lambda: None)
    texto = "📄 nota do CPF 111.111.111-11 fim"
    ocorrencia = cpf.procurar(texto)[0]
    revisao.mostrar("t.md", texto, [ocorrencia])

    cursor = revisao.texto.textCursor()
    cursor.setPosition(_posicao_no_qt(texto, ocorrencia.inicio))
    cursor.setPosition(
        _posicao_no_qt(texto, ocorrencia.fim), QTextCursor.KeepAnchor)
    assert cursor.selectedText() == ocorrencia.mascara
    assert cursor.charFormat().underlineStyle() != QTextCharFormat.NoUnderline


def test_o_destaque_cai_em_cima_do_numero_mascarado(aplicacao):
    """O traço precisa marcar o número, e não um pedaço de texto ao lado."""
    revisao = TelaRevisao(ao_anonimizar_outro=lambda: None)
    texto = "O CPF 111.111.111-11 e nada mais."
    revisao.mostrar("teste.md", texto, cpf.procurar(texto))

    sem_traco = QTextCharFormat.NoUnderline
    cursor = revisao.texto.textCursor()
    cursor.setPosition(texto.index("111") + 1)
    assert cursor.charFormat().underlineStyle() != sem_traco
    cursor.setPosition(1)
    assert cursor.charFormat().underlineStyle() == sem_traco


def test_o_pdf_com_texto_vai_da_conferencia_direto_para_a_revisao(aplicacao):
    """Critério da spec 003: conferido, o texto do PDF vai direto para a revisão.

    A escolha entre "salvar o texto como está" e "seguir para o Anonimizar" não
    aparece neste caminho: quem entrou por aqui ja disse o que quer, e oferecer
    o arquivo com os CPFs inteiros seria oferecer o contrario (RN-15).
    """
    pdf = MASSA / "01-com-texto-e-tabela.pdf"
    painel = PainelAnonimizar()
    painel.receber_arquivo(pdf)
    painel.pdf.conferir_documento(pdf)

    # O PDF da massa tem texto por dentro: a decisao e da pessoa, e ela vem
    # logo depois da conferencia do documento.
    assert painel.telas.currentWidget() is painel.pdf.tela_decisao

    painel.pdf.aproveitar_o_texto_existente(
        painel.pdf.ficha_atual, painel.pdf.tela_decisao._paginas)
    assert painel.telas.currentWidget() is painel.pdf.tela_conferencia

    painel.pdf.tela_conferencia.botao_conferido.click()
    assert painel.telas.currentWidget() is painel.tela_revisao

    # E a revisao chega mascarada, como em qualquer outro caminho.
    na_tela = painel.tela_revisao.texto_mascarado()
    assert cpf.procurar(na_tela) == []
    assert "XXX" in na_tela
    # O caminho sugerido para salvar sai do PDF que foi lido.
    painel.abrir_o_salvar()
    assert painel.tela_salvar.campo.text().endswith("01-com-texto-e-tabela - sem CPF.md")


def _que_cresce(texto, original, mascara, espacos_tirados=0):
    """Uma ocorrência com a máscara maior que o número, montada à mão.

    É o desenho do CPF sem o zero da frente (nona emenda): na etapa 1 a busca
    ainda não o acha, e o teste confere só o que a tela faz com ele.
    """
    inicio = texto.index(original)
    return cpf.Ocorrencia(inicio=inicio, fim=inicio + len(original),
                          original=original, mascara=mascara,
                          tipo=cpf.PASSA_NA_CONTA, passa_na_conta=True,
                          espacos_tirados=espacos_tirados)


def test_o_destaque_cai_em_cima_da_mascara_que_cresce(aplicacao):
    """O destaque segue o texto como ele sai, e não o tamanho do original.

    Contando pelo documento, o traço terminava uma casa antes do fim da
    máscara, e o número seguinte ganhava o traço deslocado - e um CPF ficava
    na tela sem marca nenhuma.
    """
    texto = "A 0000000000 e o CPF 111.111.111-11 fim"
    curto = _que_cresce(texto, "0000000000", "XXX000000XX")
    comum = next(o for o in cpf.procurar(texto) if not o.sem_zero)
    revisao = TelaRevisao(ao_anonimizar_outro=lambda: None)
    revisao.mostrar("t.md", texto, [curto, comum])

    na_tela = revisao.texto_mascarado()
    assert na_tela == "A XXX000000XX e o CPF XXX.111.111-XX fim"
    cursor = revisao.texto.textCursor()
    for mascara in ("XXX000000XX", "XXX.111.111-XX"):
        inicio = na_tela.index(mascara)
        for dentro in (inicio + 1, inicio + len(mascara)):
            cursor.setPosition(dentro)
            assert cursor.charFormat().underlineStyle() != QTextCharFormat.NoUnderline
        cursor.setPosition(inicio + len(mascara) + 1)
        assert cursor.charFormat().underlineStyle() == QTextCharFormat.NoUnderline

    # Ir até o número marca exatamente a máscara inteira na tela.
    revisao.ir_para(comum)
    assert revisao.texto.textCursor().selectedText() == "XXX.111.111-XX"


def test_o_trecho_marcado_depois_da_mascara_que_cresce_cai_no_lugar(aplicacao):
    texto = "| 0000000000     | Ana |\nCódigo 1234 5678 910 da ficha"
    curto = _que_cresce(texto, "0000000000", "XXX000000XX", espacos_tirados=1)
    revisao = TelaRevisao(ao_anonimizar_outro=lambda: None)
    revisao.mostrar("t.md", texto, [curto])

    na_tela = revisao.texto_mascarado()
    inicio = na_tela.index("1234 5678 910")
    cursor = revisao.texto.textCursor()
    cursor.setPosition(_posicao_no_qt(na_tela, inicio))
    cursor.setPosition(_posicao_no_qt(na_tela, inicio + len("1234 5678 910")),
                       QTextCursor.KeepAnchor)
    revisao.texto.setTextCursor(cursor)
    revisao.botao_mascarar.click()

    assert "XXX4 5678 9XX" in revisao.texto_mascarado()
    assert "| XXX000000XX    | Ana |" in revisao.texto_mascarado()


def test_o_cpf_sem_o_zero_aparece_destacado_entre_os_validos(aplicacao):
    """Nona emenda, etapa 2: achado pela busca, destacado e contado como válido."""
    texto = ("| Bolsista         | CPF            | Valor       |\n"
             "| Ana Suposta Lima | 111.111.111-11 | R$ 1.500,00 |\n"
             "| Davi Hipotético  | 0000000000     | R$ 1.500,00 |\n")
    revisao = TelaRevisao(ao_anonimizar_outro=lambda: None)
    revisao.mostrar("t.md", texto, cpf.procurar(texto))

    assert revisao.selo_validos.text() == "2 CPFs válidos"
    na_tela = revisao.texto_mascarado()
    assert "| Davi Hipotético  | XXX000000XX    | R$ 1.500,00 |" in na_tela
    # O arquivo sai igual à tela.
    assert revisao.texto_para_o_arquivo() == na_tela

    inicio = na_tela.index("XXX000000XX")
    cursor = revisao.texto.textCursor()
    cursor.setPosition(inicio + len("XXX000000XX"))
    formato = cursor.charFormat()
    assert formato.underlineStyle() == QTextCharFormat.SingleUnderline
    assert formato.foreground().color().name() == estilo.COR_ERRO_TEXTO

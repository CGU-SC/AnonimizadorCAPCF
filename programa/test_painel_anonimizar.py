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


def test_o_pdf_avisa_que_ainda_nao_anda_por_aqui(aplicacao):
    """Enquanto o caminho do PDF não existe, ele diz isso em vez de não fazer nada."""
    painel = PainelAnonimizar()
    painel.receber_arquivo(MASSA / "01-com-texto-e-tabela.pdf")
    assert painel.telas.currentWidget() is painel.tela_erro
    assert "etapa seguinte" in painel.tela_erro.explicacao.text()


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

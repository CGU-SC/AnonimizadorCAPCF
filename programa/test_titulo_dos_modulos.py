"""O título das telas dos módulos com o ícone do módulo, e a explicação da IA
local alinhada (acréscimo de 04/11/2026 à emenda de 03/11/2026 da spec 001,
RN-14 e RN-15)."""
from pathlib import Path
from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QApplication

import config_ia
from cabecalho_da_tela import CabecalhoDaTela
from caminho_do_pdf import FRASE_DA_IA_ACESA, EscolhaDoMotor
from estilo import COR_TEXTO
from main import TAMANHO_MINIMO, JanelaPrincipal
from painel_ia import LM_STUDIO_EM_OUTRA_MAQUINA


@pytest.fixture
def janela():
    return JanelaPrincipal()


def _desenho(tela):
    return tela.cabecalho.icone.desenho


def test_cada_tela_do_gerar_ocr_leva_a_lupa(janela):
    ocr = janela.painel_ocr
    for tela in (ocr, ocr.tela_ficha, ocr.tela_decisao, ocr.tela_saida, ocr.tela_salvar):
        assert _desenho(tela) == "lupa", type(tela).__name__


def test_cada_tela_do_anonimizar_leva_o_cadeado(janela):
    """Inclusive as do caminho do PDF, que é a mesma peça do Gerar OCR: o ícone
    é o do módulo por onde a pessoa entrou."""
    anon = janela.painel_anonimizar
    for tela in (anon, anon.pdf.tela_decisao, anon.pdf.tela_de_ler, anon.tela_salvar):
        assert _desenho(tela) == "cadeado", type(tela).__name__


def test_cada_tela_das_configuracoes_leva_o_desenho_da_sua_opcao(janela):
    """RN-31: o mesmo desenho do item do submenu, e não a engrenagem."""
    ia = janela.painel_ia
    for tela, desenho in ((ia.tela_tema, "tema"), (ia.tela_lm_studio, "lm_studio"),
                          (ia.tela_servidor, "servidor"), (ia.tela_habilitar, "habilitar")):
        assert _desenho(tela) == desenho, type(tela).__name__


def test_o_desenho_das_configuracoes_aparece_pintado_no_titulo(janela):
    """Os quatro desenhos nasceram para o tamanho do submenu: pintados no quadrado
    do título, eles precisam sair, e não um quadrado vazio sem nenhum erro."""
    from PySide6.QtGui import QColor
    import estilo

    ia = janela.painel_ia
    letra = QColor(estilo.COR_TEXTO)
    for tela in (ia.tela_tema, ia.tela_lm_studio, ia.tela_servidor, ia.tela_habilitar):
        foto = tela.cabecalho.icone.grab().toImage()
        tracos = sum(
            1 for x in range(foto.width()) for y in range(foto.height())
            if abs(foto.pixelColor(x, y).lightness() - letra.lightness()) < 40)
        assert tracos > 20, type(tela).__name__


def test_os_textos_dos_titulos_nao_mudaram(janela):
    assert janela.painel_ocr.cabecalho.titulo.text() == "Gerar OCR"
    assert janela.painel_ocr.cabecalho.legenda.text() == (
        "Converte documento digitalizado em texto para conferência.")
    assert janela.painel_anonimizar.cabecalho.titulo.text() == "Anonimizar"
    assert janela.painel_ocr.tela_saida.cabecalho.titulo.text() == "Texto conferido. E agora?"
    assert janela.painel_ocr.tela_salvar.cabecalho.titulo.text() == "Onde salvar o arquivo"
    assert janela.painel_anonimizar.tela_salvar.cabecalho.titulo.text() == (
        "Onde salvar o texto mascarado")
    assert janela.painel_ia.tela_lm_studio.cabecalho.titulo.text() == "LM Studio"


def test_as_telas_de_fora_continuam_sem_o_titulo_novo(janela):
    """As de espera, as de erro, as de título no meio e as que têm cabeçalho
    próprio ficam como estavam."""
    ocr, anon = janela.painel_ocr, janela.painel_anonimizar
    de_fora = (ocr.tela_verificando, ocr.tela_lendo, ocr.tela_erro, ocr.tela_conferencia,
               ocr.tela_sobrescrever, ocr.tela_gravado, ocr.tela_descartar,
               anon.tela_erro, anon.tela_revisao, anon.tela_gravado, anon.tela_descartar)
    for tela in de_fora:
        assert not tela.findChildren(CabecalhoDaTela), type(tela).__name__


def _base_da_linha(janela, peca):
    """A altura, na janela, da linha de baixo de um cabeçalho."""
    return peca.mapTo(janela, peca.rect().bottomLeft()).y()


def test_a_linha_do_titulo_fica_na_altura_da_linha_da_faixa(janela):
    janela.showNormal()
    QApplication.processEvents()
    faixa = _base_da_linha(janela, janela.menu.nome.parentWidget())

    janela.menu.botao_ocr.click()
    QApplication.processEvents()
    assert _base_da_linha(janela, janela.painel_ocr.cabecalho) == faixa

    janela.menu.botao_config_ia.click()
    QApplication.processEvents()
    assert _base_da_linha(janela, janela.painel_ia.tela_lm_studio.cabecalho) == faixa


def test_nada_do_titulo_sai_cortado_na_janela_minima(janela):
    """A legenda do Anonimizar é a mais longa das telas de entrada: na janela
    mínima ela desce para a segunda linha, e a linha de baixo desce junto."""
    janela.showNormal()
    janela.resize(TAMANHO_MINIMO)
    for botao, cabecalho in ((janela.menu.botao_ocr, janela.painel_ocr.cabecalho),
                             (janela.menu.botao_anonimizar, janela.painel_anonimizar.cabecalho)):
        botao.click()
        QApplication.processEvents()
        titulo, legenda = cabecalho.titulo, cabecalho.legenda
        assert titulo.width() >= titulo.sizeHint().width(), titulo.text()
        assert legenda.height() >= legenda.heightForWidth(legenda.width()), legenda.text()
        assert cabecalho.height() >= legenda.geometry().bottom()


def _nada_cortado(cabecalho):
    """A legenda inteira à vista, e a linha de baixo do título abaixo dela."""
    legenda = cabecalho.legenda
    assert legenda.height() >= legenda.heightForWidth(legenda.width()), legenda.text()
    assert cabecalho.height() > legenda.geometry().bottom(), legenda.text()


def test_o_aviso_dos_cpfs_inteiros_nao_sai_cortado(janela, monkeypatch):
    """A legenda da IA em outra máquina é trocada depois de a tela estar
    montada, e na janela mínima desce para a segunda linha: é nela que fica o
    "com os CPFs inteiros". O título precisa crescer junto."""
    monkeypatch.setattr(config_ia, "lm_studio_nesta_maquina", lambda: False)
    janela.showNormal()
    janela.resize(TAMANHO_MINIMO)
    janela.menu.botao_config_ia.click()
    # Configurações abre no Tema desde a funcionalidade 10 (RN-22): o LM Studio
    # é a segunda opção.
    janela.menu.botao_lm_studio.click()
    QApplication.processEvents()
    cabecalho = janela.painel_ia.tela_lm_studio.cabecalho
    assert cabecalho.legenda.text() == LM_STUDIO_EM_OUTRA_MAQUINA
    assert cabecalho.legenda.heightForWidth(cabecalho.legenda.width()) > (
        cabecalho.titulo.sizeHint().height()), "a frase devia quebrar na janela mínima"
    _nada_cortado(cabecalho)


def test_a_janela_que_encolhe_faz_o_titulo_crescer(janela, monkeypatch):
    """O aviso cabe numa linha com a janela larga; encolhida até o mínimo, a
    legenda desce para a segunda linha, e o título precisa crescer junto."""
    monkeypatch.setattr(config_ia, "lm_studio_nesta_maquina", lambda: False)
    janela.showNormal()
    janela.resize(1400, 800)
    janela.menu.botao_config_ia.click()
    janela.menu.botao_lm_studio.click()
    QApplication.processEvents()
    janela.resize(TAMANHO_MINIMO)
    QApplication.processEvents()
    _nada_cortado(janela.painel_ia.tela_lm_studio.cabecalho)


def test_o_nome_de_arquivo_comprido_nao_sai_cortado(janela):
    """A legenda da tela de ler leva o nome do arquivo, que pode ser longo."""
    janela.showNormal()
    janela.resize(TAMANHO_MINIMO)
    janela.menu.botao_anonimizar.click()
    pdf = janela.painel_anonimizar.pdf
    ficha = SimpleNamespace(caminho=Path("prestacao-de-contas-do-convenio-de-pesquisa-2026.pdf"),
                            paginas=12)
    pdf.tela_de_ler.mostrar(ficha, ignorando=False)
    pdf._mostrar(pdf.tela_de_ler)
    QApplication.processEvents()
    _nada_cortado(pdf.tela_de_ler.cabecalho)


def test_a_legenda_que_encolhe_devolve_o_titulo_a_altura_da_faixa(janela):
    """Voltando à frase curta, a linha volta para a altura da linha da faixa."""
    janela.showNormal()
    janela.resize(TAMANHO_MINIMO)
    janela.menu.botao_config_ia.click()
    # Configurações abre no Tema desde a funcionalidade 10 (RN-22): o LM Studio
    # é a segunda opção.
    janela.menu.botao_lm_studio.click()
    QApplication.processEvents()
    cabecalho = janela.painel_ia.tela_lm_studio.cabecalho
    curta = cabecalho.legenda.text()
    cabecalho.legenda.setText(LM_STUDIO_EM_OUTRA_MAQUINA)
    QApplication.processEvents()
    cabecalho.legenda.setText(curta)
    QApplication.processEvents()
    faixa = _base_da_linha(janela, janela.menu.nome.parentWidget())
    assert _base_da_linha(janela, cabecalho) == faixa


def _primeiro_ponto_da_frase(foto, escolha, rotulo):
    """Onde, da esquerda para a direita, aparece a primeira letra da linha."""
    canto = rotulo.mapTo(escolha, rotulo.rect().topLeft())
    y_do_meio = canto.y() + rotulo.height() // 2
    fundo = foto.pixelColor(foto.width() - 1, y_do_meio)
    for x in range(foto.width()):
        for y in range(canto.y(), canto.y() + rotulo.height()):
            if foto.pixelColor(x, y) != fundo:
                return x
    return None


def test_a_explicacao_da_ia_comeca_no_recuo_das_outras(aplicacao):
    """RN-15: encostada na margem, ela parecia de outro assunto. Sem a IA
    ligada a frase é a de "Ligue em Configurações", e o recuo é o mesmo
    para qualquer frase."""
    escolha = EscolhaDoMotor("LER COM")
    escolha.resize(640, escolha.sizeHint().height())
    escolha.show()
    QApplication.processEvents()
    foto = escolha.grab().toImage()

    do_paddleocr = _primeiro_ponto_da_frase(foto, escolha, escolha.resumo_paddleocr)
    da_ia = _primeiro_ponto_da_frase(foto, escolha, escolha.frase_da_ia)
    assert do_paddleocr is not None and da_ia is not None
    assert abs(da_ia - do_paddleocr) <= 2, (da_ia, do_paddleocr)


def test_o_tempo_da_ia_tem_o_destaque_dos_outros(aplicacao, monkeypatch):
    monkeypatch.setattr(config_ia, "motor_ativo", lambda: True)
    monkeypatch.setattr(config_ia, "destino_ligado", lambda: config_ia.LM_STUDIO)
    escolha = EscolhaDoMotor("LER COM")
    frase, tempo = FRASE_DA_IA_ACESA
    assert f"<span style='color: {COR_TEXTO};'>{tempo}</span>" in escolha.frase_da_ia.text()
    assert escolha.frase_da_ia.text().startswith(frase)

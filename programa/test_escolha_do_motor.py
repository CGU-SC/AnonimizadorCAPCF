"""A escolha com três motores, nos dois módulos (emenda de 18/10/2026 da spec 002).

O que estes testes protegem é o que a medição da conferência 02 mostrou que
importa: o PaddleOCR vir marcado, e o motor marcado ser de fato o que lê. Até
esta emenda, a escolha da tela não decidia nada - o programa chamava sempre o
Tesseract, qualquer que fosse o botão marcado.
"""
import json
import re
from pathlib import Path

import pytest

import caminho_do_pdf
import estilo
import leitura
from caminho_do_pdf import EscolhaDoMotor
from painel_anonimizar import PainelAnonimizar
from painel_ocr import PainelOcr

MASSA = Path(__file__).parent.parent / "dados-exemplo"
PAGINAS_DIFICEIS = MASSA / "20-paginas-dificeis.pdf"

# O espaço que sobra para o resumo na janela mínima: 900 px menos o menu da
# esquerda, as margens do painel e a barra de rolagem da tela de escolher.
LARGURA_QUE_SOBRA = 900 - estilo.LARGURA_MENU - estilo.ESPACO_4 - estilo.ESPACO_5 - 10


class _LeituraDeMentira:
    """Guarda o motor que recebeu, sem ler nada e sem abrir trabalho ao lado."""

    motores = []

    def __init__(self, caminho, motor):
        _LeituraDeMentira.motores.append(motor)
        for aviso in ("avancou", "terminou", "cancelou", "falhou"):
            setattr(self, aviso, _AvisoDeMentira())

    def start(self):
        pass

    def isRunning(self):
        return False


class _AvisoDeMentira:
    def connect(self, _funcao):
        pass


@pytest.fixture
def leitura_de_mentira(monkeypatch):
    _LeituraDeMentira.motores = []
    monkeypatch.setattr(caminho_do_pdf, "LeituraEmSegundoPlano", _LeituraDeMentira)
    return _LeituraDeMentira


def _escolhas_dos_dois_modulos():
    painel_ocr = PainelOcr()
    painel_anonimizar = PainelAnonimizar()
    return (painel_ocr.escolha_do_motor,
            painel_anonimizar.pdf.tela_de_ler.escolha_do_motor)


def test_os_dois_modulos_mostram_os_tres_motores_com_o_paddleocr_marcado():
    """RN-25: nesta ordem, o PaddleOCR marcado, e a IA local apagada."""
    for escolha in _escolhas_dos_dois_modulos():
        assert escolha.paddleocr.text() == "PaddleOCR (nesta máquina)"
        assert escolha.tesseract.text() == "Tesseract (nesta máquina)"
        assert escolha.ia_local.text() == "IA local"
        assert escolha.paddleocr.isChecked()
        assert not escolha.ia_local.isEnabled()
        assert escolha.marcado() == leitura.MOTOR_PADDLEOCR

        # A ordem em que aparecem na tela é a ordem em que entram no bloco.
        ordem = [escolha.layout().indexOf(peca) for peca in
                 (escolha.paddleocr, escolha.tesseract, escolha.ia_local)]
        assert ordem == sorted(ordem)


def test_o_resumo_de_cada_motor_e_o_combinado():
    """RN-31: o que cada um faz melhor, e quanto leva por página."""
    escolha = EscolhaDoMotor("MOTOR DE LEITURA")
    assert ("Melhor resultado, inclusive em tabela e página escaneada ruim"
            in escolha.resumo_paddleocr.text())
    assert "cerca de 2 segundos por página" in escolha.resumo_paddleocr.text()
    assert "Pode pular tabela com grade" in escolha.resumo_tesseract.text()
    assert "cerca de 3 segundos por página" in escolha.resumo_tesseract.text()


def test_o_resumo_cabe_numa_linha_na_janela_minima():
    """O resumo não quebra linha, e por isso precisa caber na largura que sobra.

    Mais largo que isso, ele empurraria a tela para os lados - e a primeira
    letra de tudo ficaria cortada, sem nada acusar (O que já nos mordeu,
    17/09/2026).
    """
    escolha = EscolhaDoMotor("MOTOR DE LEITURA")
    for resumo in (escolha.resumo_paddleocr, escolha.resumo_tesseract):
        # Sem isto o Qt mede com a fonte padrão, e não com a do estilo.
        resumo.ensurePolished()
        assert resumo.sizeHint().width() <= LARGURA_QUE_SOBRA, resumo.text()


def test_marcando_o_tesseract_ele_passa_a_ser_o_escolhido():
    escolha = EscolhaDoMotor("LER COM")
    escolha.tesseract.setChecked(True)
    assert escolha.marcado() == leitura.MOTOR_TESSERACT
    assert not escolha.paddleocr.isChecked()


def test_no_gerar_ocr_o_motor_marcado_e_o_que_le(leitura_de_mentira):
    """RN-26: até a emenda, a leitura nunca perguntava qual estava marcado."""
    painel = PainelOcr()
    ficha = caminho_do_pdf.conferir(MASSA / "02-imprimir-para-pdf.pdf")

    painel.pdf.comecar_a_ler(ficha)
    painel.escolha_do_motor.tesseract.setChecked(True)
    painel.pdf.comecar_a_ler(ficha)

    assert leitura_de_mentira.motores == [leitura.MOTOR_PADDLEOCR,
                                          leitura.MOTOR_TESSERACT]


def test_no_anonimizar_o_motor_marcado_e_o_que_le(leitura_de_mentira):
    painel = PainelAnonimizar()
    ficha = caminho_do_pdf.conferir(MASSA / "02-imprimir-para-pdf.pdf")

    painel.pdf.comecar_a_ler(ficha)
    painel.pdf.tela_de_ler.escolha_do_motor.tesseract.setChecked(True)
    painel.pdf.comecar_a_ler(ficha)

    assert leitura_de_mentira.motores == [leitura.MOTOR_PADDLEOCR,
                                          leitura.MOTOR_TESSERACT]


def test_cada_modulo_tem_a_sua_escolha():
    """RN-26: marcar o Tesseract num módulo não muda o outro."""
    do_ocr, do_anonimizar = _escolhas_dos_dois_modulos()
    do_ocr.tesseract.setChecked(True)
    assert do_anonimizar.marcado() == leitura.MOTOR_PADDLEOCR


def test_a_pagina_vai_ao_paddleocr_como_imagem_pronta(monkeypatch):
    """Regressão da lente crítica da etapa 1 (18/10/2026).

    Entregue como tabela de números, a página chegava ao modelo com o vermelho
    e o azul trocados: o RapidOCR supõe outra ordem de cores para tabela, e só
    acerta sozinho quando recebe a imagem pronta.
    """
    from PIL import Image

    import motor_paddleocr

    recebido = []

    def motor_de_mentira(imagem):
        recebido.append(imagem)
        return type("Resultado", (), {"txts": None, "boxes": None})()

    monkeypatch.setattr(motor_paddleocr, "preparar", lambda: motor_de_mentira)
    motor_paddleocr.ler(Image.new("RGB", (10, 10), "white"))

    assert isinstance(recebido[0], Image.Image)


@pytest.mark.parametrize("indice", [0, 1, 2, 3])
def test_o_paddleocr_le_inteiros_os_cpfs_das_paginas_limpas_com_poeira_e_torta(indice):
    """Critério da emenda: inclusive os 12 da tabela com grade, que o
    Tesseract pula inteira mesmo com a página limpa (conferência 02)."""
    import pymupdf

    gabarito = json.loads(
        (MASSA / "20-paginas-dificeis.gabarito.json").read_text(encoding="utf-8"))
    pagina = gabarito[indice]
    esperados = re.findall(r"\d{3}\.?\d{3}\.?\d{3}[-/]?\d{2}", pagina["texto"])
    assert esperados, "a página do gabarito deveria ter CPF"

    documento = pymupdf.open(PAGINAS_DIFICEIS)
    try:
        texto = leitura._ler_pagina_com_paddleocr(documento[indice])
    finally:
        documento.close()

    faltando = [cpf for cpf in esperados if cpf not in texto]
    assert not faltando, f"{pagina['pagina']}: não leu {faltando}"

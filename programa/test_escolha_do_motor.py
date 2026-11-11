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

# O CPF escrito no gabarito, solto: nem colado a outro dígito, nem dentro de
# outro número. Sem as duas pontas, um pedaço do número do processo
# (23080.012345/2026-11) passava por CPF - é a mesma regra do programa (RN-3
# da spec 003).
CPF_NO_GABARITO = r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}[-/]?\d{2}(?!\d)"

# O espaço que sobra para o resumo na janela mínima: 900 px menos o menu da
# esquerda, as margens do painel e a barra de rolagem da tela de escolher.
LARGURA_QUE_SOBRA = 900 - estilo.LARGURA_MENU - estilo.ESPACO_4 - estilo.ESPACO_5 - 10


class _LeituraDeMentira:
    """Guarda o motor que recebeu, sem ler nada e sem abrir trabalho ao lado."""

    motores = []

    def __init__(self, caminho, motor):
        _LeituraDeMentira.motores.append(motor)
        _LeituraDeMentira.ultima = self
        for aviso in ("avancou", "terminou", "cancelou", "falhou"):
            setattr(self, aviso, _AvisoDeMentira())

    def start(self):
        pass

    def isRunning(self):
        return False


class _AvisoDeMentira:
    """Guarda quem se ligou, para o teste poder dar o aviso como se a leitura
    tivesse terminado."""

    def __init__(self):
        self.ligados = []

    def connect(self, funcao):
        self.ligados.append(funcao)

    def emit(self, *valores):
        for funcao in self.ligados:
            funcao(*valores)


@pytest.fixture
def leitura_de_mentira(monkeypatch):
    _LeituraDeMentira.motores = []
    # Sem apagar, a leitura do teste anterior ficava guardada: um teste em que
    # a leitura nem começa daria o aviso de fim nela, ligada a outra tela, e
    # passaria conferindo a coisa errada (lente crítica da etapa 3).
    _LeituraDeMentira.ultima = None
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

    monkeypatch.setattr(motor_paddleocr, "preparar", lambda virar_linhas: motor_de_mentira)
    motor_paddleocr.ler(Image.new("RGB", (10, 10), "white"), virar_linhas=False)

    assert isinstance(recebido[0], Image.Image)


@pytest.mark.parametrize("indice", [0, 1, 2, 3])
def test_o_paddleocr_le_inteiros_os_cpfs_das_paginas_limpas_com_poeira_e_torta(indice):
    """Critério da emenda: inclusive os 12 da tabela com grade, que o
    Tesseract pula inteira mesmo com a página limpa (conferência 02)."""
    import pymupdf

    gabarito = json.loads(
        (MASSA / "20-paginas-dificeis.gabarito.json").read_text(encoding="utf-8"))
    pagina = gabarito[indice]
    esperados = re.findall(CPF_NO_GABARITO, pagina["texto"])
    assert esperados, "a página do gabarito deveria ter CPF"

    documento = pymupdf.open(PAGINAS_DIFICEIS)
    try:
        texto = leitura._ler_pagina_com_paddleocr(documento[indice])
    finally:
        documento.close()

    faltando = [cpf for cpf in esperados if cpf not in texto]
    assert not faltando, f"{pagina['pagina']}: não leu {faltando}"


# ------------------------------------------------- etapa 3: deitada, selo, tempo


def _ler_com_o_paddleocr(caminho, indice):
    import pymupdf
    documento = pymupdf.open(caminho)
    try:
        leitura.preparar_motor()
        return leitura._ler_pagina_endireitada_com_paddleocr(documento[indice])
    finally:
        documento.close()


def test_a_pagina_deitada_sai_endireitada_com_o_paddleocr():
    """RN-28: o detector do Tesseract endireita a página para o PaddleOCR.

    Sem ele, a página deitada da massa 20 saía com um terço das palavras e dois
    CPFs escapando (conferência 02).
    """
    texto = _ler_com_o_paddleocr(MASSA / "03-conteudo-girado.pdf", 0)
    assert "UNIVERSIDADE FEDERAL DE SANTA CATARINA" in texto

    gabarito = json.loads(
        (MASSA / "20-paginas-dificeis.gabarito.json").read_text(encoding="utf-8"))
    deitada = next(i for i, p in enumerate(gabarito) if p["pagina"] == "oficio-deitado")
    esperados = re.findall(CPF_NO_GABARITO, gabarito[deitada]["texto"])
    texto = _ler_com_o_paddleocr(PAGINAS_DIFICEIS, deitada)
    assert [cpf for cpf in esperados if cpf not in texto] == []


def test_sem_o_tesseract_a_orientacao_do_paddleocr_nao_e_conferida(monkeypatch):
    monkeypatch.setattr(leitura, "localizar_tesseract", lambda: None)
    assert not leitura.orientacao_conferida(leitura.MOTOR_PADDLEOCR)
    # Com o Tesseract marcado, quem não está é o próprio motor: o aviso
    # disso é outro, o de motor faltando.
    assert leitura.orientacao_conferida(leitura.MOTOR_TESSERACT)


def test_a_conferencia_diz_quem_leu_e_avisa_da_orientacao(leitura_de_mentira, monkeypatch):
    """RN-32 e RN-28, pelo caminho inteiro: da escolha à conferência."""
    monkeypatch.setattr(caminho_do_pdf, "orientacao_conferida", lambda motor: False)
    painel = PainelOcr()
    ficha = caminho_do_pdf.conferir(MASSA / "02-imprimir-para-pdf.pdf")

    painel.pdf.comecar_a_ler(ficha)
    leitura_de_mentira.ultima.terminou.emit(["texto lido"] * ficha.paginas)

    conferencia = painel.pdf.tela_conferencia
    assert conferencia.selo.text() == "LIDO PELO PADDLEOCR"
    assert not conferencia.faixa_da_orientacao.isHidden()
    # O aviso é da tela: o texto que segue para o arquivo não o leva (RN-11).
    assert "orientação" not in " ".join(conferencia.texto_conferido())


def test_com_o_tesseract_o_selo_diz_tesseract_e_nao_ha_aviso(leitura_de_mentira):
    painel = PainelOcr()
    painel.escolha_do_motor.tesseract.setChecked(True)
    ficha = caminho_do_pdf.conferir(MASSA / "02-imprimir-para-pdf.pdf")

    painel.pdf.comecar_a_ler(ficha)
    leitura_de_mentira.ultima.terminou.emit(["texto lido"] * ficha.paginas)

    conferencia = painel.pdf.tela_conferencia
    assert conferencia.selo.text() == "LIDO PELO TESSERACT"
    assert conferencia.faixa_da_orientacao.isHidden()


def test_a_estimativa_antes_de_ler_usa_o_motor_marcado():
    """RN-31: no PDF com texto por dentro, ignorar e ler as imagens leva o
    tempo do motor marcado - 3 páginas: 6 segundos com o PaddleOCR, 9 com o
    Tesseract."""
    painel = PainelOcr()
    ficha = caminho_do_pdf.conferir(MASSA / "01-com-texto-e-tabela.pdf")

    painel.pdf.decidir_sobre_o_texto_existente(ficha)
    assert "uns 6 segundos" in painel.pdf.tela_decisao.porque_ignorar.text()

    painel.escolha_do_motor.tesseract.setChecked(True)
    painel.pdf.decidir_sobre_o_texto_existente(ficha)
    assert "uns 9 segundos" in painel.pdf.tela_decisao.porque_ignorar.text()


def test_palpite_do_detector_nao_vira_a_pagina(monkeypatch):
    """Regressão da conferência da etapa 3 (19/10/2026).

    Na página desbotada, o detector do Tesseract mandou virar de cabeça para
    baixo com confiança 1,2, e o PaddleOCR deixou de ler os 4 CPFs que lia.
    Resposta com pouca confiança conta como "não decidiu"; com confiança, gira.
    """
    from PIL import Image

    pagina = Image.new("RGB", (40, 20), "white")

    monkeypatch.setattr(leitura.pytesseract, "image_to_osd",
                        lambda *a, **k: {"rotate": 180, "orientation_conf": 1.2})
    assert leitura._endireitar(pagina) is pagina

    monkeypatch.setattr(leitura.pytesseract, "image_to_osd",
                        lambda *a, **k: {"rotate": 90, "orientation_conf": 14.76})
    assert leitura._endireitar(pagina).size == (20, 40)


def test_a_pagina_desbotada_nao_e_virada_a_toa():
    """A mesma página que mostrou o defeito, lida de verdade pelo detector."""
    import pymupdf

    leitura.preparar_motor()
    documento = pymupdf.open(PAGINAS_DIFICEIS)
    try:
        imagem = leitura._desenhar(documento[4])
    finally:
        documento.close()
    assert leitura._endireitar(imagem) is imagem


def test_a_pagina_deitada_sai_com_todas_as_linhas():
    """Regressão da conferência da etapa 3 (19/10/2026).

    O RapidOCR virava linha por linha o que achava estar de cabeça para baixo, e
    virava linhas certas: no ofício deitado, a do processo e a das parcelas
    saíam como lixo. Desligado isso, as duas voltam.
    """
    gabarito = json.loads(
        (MASSA / "20-paginas-dificeis.gabarito.json").read_text(encoding="utf-8"))
    deitada = next(i for i, p in enumerate(gabarito) if p["pagina"] == "oficio-deitado")
    texto = _ler_com_o_paddleocr(PAGINAS_DIFICEIS, deitada)
    assert "23080.012345/2026-11" in texto
    assert "parcelas de março a junho" in texto


def _tesseract_de_mentira(pasta, *arquivos_de_idioma):
    (pasta / "tessdata").mkdir()
    for nome in arquivos_de_idioma:
        (pasta / "tessdata" / nome).write_text("")
    executavel = pasta / "tesseract.exe"
    executavel.write_text("")
    return executavel


def test_sem_o_arquivo_do_detector_a_orientacao_nao_e_conferida(tmp_path, monkeypatch):
    """Lente crítica da etapa 3: quem endireita é o detector, e ele usa um
    arquivo próprio. Só com o português, a página seguia sem endireitar e a
    conferência não avisava."""
    monkeypatch.delenv("TESSDATA_PREFIX", raising=False)
    so_portugues = _tesseract_de_mentira(tmp_path, "por.traineddata")
    monkeypatch.setattr(leitura, "localizar_tesseract", lambda: so_portugues)
    assert not leitura.orientacao_conferida(leitura.MOTOR_PADDLEOCR)

    (tmp_path / "tessdata" / "osd.traineddata").write_text("")
    assert leitura.orientacao_conferida(leitura.MOTOR_PADDLEOCR)


@pytest.mark.parametrize("conferida, deve_virar_linhas", [(True, False), (False, True)])
def test_o_paddleocr_vira_linhas_so_sem_o_detector(monkeypatch, conferida, deve_virar_linhas):
    """Lente crítica da etapa 3: com o detector, virar linha por linha só
    atrapalhava; sem ele, é a única defesa contra a folha de cabeça para baixo."""
    import motor_paddleocr

    pedidos = []
    monkeypatch.setattr(leitura, "orientacao_conferida", lambda motor: conferida)
    monkeypatch.setattr(motor_paddleocr, "preparar", lambda virar_linhas: None)
    monkeypatch.setattr(motor_paddleocr, "ler",
                        lambda imagem, virar_linhas: pedidos.append(virar_linhas) or "")

    leitura.ler_documento(MASSA / "03-conteudo-girado.pdf", motor=leitura.MOTOR_PADDLEOCR)
    assert pedidos == [deve_virar_linhas]

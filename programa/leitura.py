"""Lê o texto de um PDF virando cada página em imagem e passando para o OCR.

Este arquivo não sabe que existe uma janela: ele avisa o andamento e pergunta
se foi cancelado através de duas funções que quem chama entrega. É isso que
permite testar a leitura sem abrir o programa.

Nada aqui sai da máquina. Os dois motores leem na própria máquina - o
Tesseract, instalado no Windows; o PaddleOCR, dentro do programa -, e o
documento não viaja para lugar nenhum.
"""
import io

import pymupdf
import pytesseract
from PIL import Image

import motor_paddleocr
from disposicao import montar
from motor import localizar_tesseract, tem_o_detector

# Os motores que a escolha da tela oferece (emenda de 18/10/2026 da spec 002).
# A IA local, quando for construída, entra aqui como mais um nome, com a sua
# própria maneira de preparar e de ler uma página.
MOTOR_PADDLEOCR = "paddleocr"
MOTOR_TESSERACT = "tesseract"
NOME_NA_TELA = {
    MOTOR_PADDLEOCR: "PaddleOCR",
    MOTOR_TESSERACT: "Tesseract",
}

# 300 pontos por polegada é a densidade que o Tesseract recomenda para texto
# impresso (regra RN-7 da spec 002). Abaixo disso ele erra mais; acima, fica
# mais lento sem ganhar precisão.
PONTOS_POR_POLEGADA = 300

# O pacote de português. Sem ele o OCR lê acentuação como lixo.
IDIOMA = "por"


# Quanto uma página costuma levar para ser lida, por motor: o desenho da
# página, a detecção de orientação e a leitura somados. São os mesmos números do
# resumo embaixo de cada motor na escolha (RN-31), medidos nesta máquina na
# conferência 02, em 13/10/2026. O do Tesseract era 1,5, medido em 11/09/2026
# só na massa limpa; com tabela e página difícil ele passou de 2,5. Servem só
# para dizer à pessoa quanto tempo ela vai esperar antes de ela escolher esperar
# - a estimativa que aparece DURANTE a leitura é calculada pelo ritmo real.
SEGUNDOS_POR_PAGINA = {
    MOTOR_PADDLEOCR: 2,
    MOTOR_TESSERACT: 3,
}


def tempo_estimado(paginas, motor):
    """Uma frase curta com quanto a leitura deve levar com este motor."""
    segundos = round(paginas * SEGUNDOS_POR_PAGINA[motor])
    if segundos < 60:
        return f"uns {segundos} segundos"
    # Arredonda para cima na metade: quem decide esperar prefere descobrir que
    # terminou antes do previsto a descobrir que ainda falta.
    minutos = int(segundos / 60 + 0.5)
    return "cerca de 1 minuto" if minutos == 1 else f"cerca de {minutos} minutos"


class MotorNaoEncontrado(Exception):
    """O Tesseract não está instalado, ou está em pasta que não conhecemos."""


class LeituraCancelada(Exception):
    """A pessoa clicou em cancelar no meio da leitura."""

    def __init__(self, pagina):
        super().__init__(f"Leitura cancelada na página {pagina}.")
        self.pagina = pagina


class LeituraFalhou(Exception):
    """A leitura estourou numa página, e a mensagem já vem pronta para a tela."""

    def __init__(self, pagina, motivo):
        super().__init__(motivo)
        self.pagina = pagina


def preparar_motor():
    """Aponta o pytesseract para o Tesseract desta máquina.

    Levanta MotorNaoEncontrado quando não há Tesseract instalado. A tela já
    avisa disso antes de a leitura começar; isto aqui é a última trava, para o
    caso de o motor sumir com o programa aberto.
    """
    caminho = localizar_tesseract()
    if caminho is None:
        raise MotorNaoEncontrado(
            "O motor de leitura (Tesseract) não foi encontrado nesta máquina, "
            "ou está instalado sem o pacote de português."
        )
    pytesseract.pytesseract.tesseract_cmd = str(caminho)
    return caminho


# Teto de densidade para a imagem da tela. Acima disto a página vira uma imagem
# enorme que custa memória e demora a preparar, sem ganho que o olho note numa
# tela comum. Chegando ao teto, o que falta de tamanho é esticado - e esticar
# pouco não borra.
PONTOS_POR_POLEGADA_MAXIMO_NA_TELA = 300


def imagem_da_pagina(caminho, indice, largura_desejada):
    """Desenha uma página do PDF no tamanho em que ela vai aparecer.

    O tamanho é pedido em pixels, e não em densidade, porque é isso que evita o
    borrão: desenhar sempre no mesmo tamanho e depois esticar não cria detalhe
    nenhum - a letra fica maior e mais borrada, que é o oposto do que o botão de
    aumentar promete.

    Uma página por vez, e não o documento inteiro: é o que mantém a tela de
    conferência leve mesmo num documento de duzentas páginas.
    """
    documento = pymupdf.open(caminho)
    try:
        pagina = documento[indice]
        # 72 pontos por polegada é a unidade em que o PDF mede a própria página.
        densidade = round(72 * largura_desejada / pagina.rect.width)
        densidade = min(max(densidade, 36), PONTOS_POR_POLEGADA_MAXIMO_NA_TELA)
        return pagina.get_pixmap(dpi=densidade).tobytes("png")
    finally:
        documento.close()


def _preparar_paddleocr(virar_linhas):
    try:
        motor_paddleocr.preparar(virar_linhas)
    except motor_paddleocr.PaddleOcrFaltando as problema:
        raise MotorNaoEncontrado(str(problema)) from problema


def orientacao_conferida(motor):
    """Diz se a leitura com este motor vai endireitar a página deitada.

    Quem descobre que a página está deitada é o detector do Tesseract, para os
    dois motores (RN-28): o PaddleOCR só vira linha de cabeça para baixo. Sem o
    Tesseract na máquina - ou com ele, mas sem o arquivo do detector -, a leitura
    com o PaddleOCR segue sem endireitar, e a conferência precisa avisar. Quem
    chama pergunta aqui, e não refaz a conta.
    """
    if motor == MOTOR_TESSERACT:
        return True
    executavel = localizar_tesseract()
    return executavel is not None and tem_o_detector(executavel)


def _ler_pagina_com_paddleocr(pagina):
    # Sem o detector do Tesseract, a única defesa contra a página de cabeça para
    # baixo é o PaddleOCR virar linha por linha - e aí ele vira (ver
    # motor_paddleocr.preparar).
    return motor_paddleocr.ler(_desenhar(pagina), virar_linhas=True)


def _ler_pagina_endireitada_com_paddleocr(pagina):
    return motor_paddleocr.ler(_endireitar(_desenhar(pagina)), virar_linhas=False)


def ler_documento(caminho, ao_avancar=None, foi_cancelado=None,
                  motor=MOTOR_TESSERACT):
    """Lê o documento inteiro e devolve o texto de cada página, em ordem.

    ao_avancar(pagina, total) é chamado antes de cada página, para a tela poder
    mostrar a contagem. foi_cancelado() é perguntado no mesmo momento: quando
    responde que sim, a leitura para e o que já foi lido é jogado fora - nada
    é gravado antes da conferência (regra RN-2).

    `motor` é o que está marcado na tela: o marcado é o que lê (RN-26). O
    Tesseract é o padrão aqui, e não na tela, para quem chama sem dizer o motor
    continuar recebendo a leitura de sempre.
    """
    if motor == MOTOR_PADDLEOCR:
        if orientacao_conferida(motor):
            _preparar_paddleocr(virar_linhas=False)
            # O detector é do Tesseract: ele precisa saber onde o Tesseract mora.
            preparar_motor()
            ler_pagina = _ler_pagina_endireitada_com_paddleocr
        else:
            _preparar_paddleocr(virar_linhas=True)
            ler_pagina = _ler_pagina_com_paddleocr
    else:
        preparar_motor()
        ler_pagina = _ler_pagina

    documento = pymupdf.open(caminho)
    try:
        total = documento.page_count
        paginas = []
        for indice in range(total):
            numero = indice + 1
            if foi_cancelado is not None and foi_cancelado():
                raise LeituraCancelada(numero)
            if ao_avancar is not None:
                ao_avancar(numero, total)

            try:
                paginas.append(ler_pagina(documento[indice]))
            except LeituraCancelada:
                raise
            except Exception as problema:
                raise LeituraFalhou(
                    numero,
                    "Alguma coisa deu errado ao ler esta página. Nada foi "
                    "gravado, e o documento original não foi tocado.",
                ) from problema
    finally:
        documento.close()

    return paginas


def _ler_pagina(pagina):
    """Desenha a página como imagem, endireita o que estiver deitado, e lê."""
    imagem = _desenhar(pagina)
    imagem = _endireitar(imagem)
    return _texto_com_a_disposicao_da_pagina(imagem)


def _texto_com_a_disposicao_da_pagina(imagem):
    """Lê a imagem pedindo a posição de cada palavra, e remonta as linhas.

    Pedir só o texto pronto ao Tesseract devolveria a tabela como uma coisa por
    linha, sem as colunas. Pedindo a posição, a tabela volta a parecer uma
    tabela (regra RN-10 da spec 002).

    O agrupamento em linhas usa o que o próprio Tesseract identificou: ele já
    separa bloco, parágrafo e linha, e faz isso melhor que uma conta de altura
    feita por fora.
    """
    dados = pytesseract.image_to_data(
        imagem, lang=IDIOMA, output_type=pytesseract.Output.DICT
    )

    linhas = {}
    ordem = []
    for i, palavra in enumerate(dados["text"]):
        if not palavra.strip():
            continue
        chave = (dados["block_num"][i], dados["par_num"][i], dados["line_num"][i])
        if chave not in linhas:
            linhas[chave] = []
            ordem.append(chave)
        x = dados["left"][i]
        linhas[chave].append((x, x + dados["width"][i], palavra))

    return "\n".join(montar(_com_as_separacoes_de_bloco(linhas, ordem)))


def _com_as_separacoes_de_bloco(linhas, ordem):
    """Põe uma linha em branco onde o documento muda de bloco.

    O Tesseract já separa os blocos da página - o cabeçalho, o corpo, o rodapé -
    e essa separação precisa sobreviver até o arquivo: em `.md`, linhas seguidas
    sem uma linha vazia entre elas viram um parágrafo só, e o cabeçalho chegaria
    colado ao corpo dentro da conversa com o assistente.
    """
    com_separacao = []
    bloco_anterior = None
    for chave in ordem:
        bloco = chave[0]
        if bloco_anterior is not None and bloco != bloco_anterior:
            com_separacao.append([])
        com_separacao.append(linhas[chave])
        bloco_anterior = bloco
    return com_separacao


def _desenhar(pagina):
    pixels = pagina.get_pixmap(dpi=PONTOS_POR_POLEGADA)
    return Image.open(io.BytesIO(pixels.tobytes("png")))


# Abaixo disto, a resposta do detector de orientação é palpite. Medido em
# 19/10/2026 sobre todas as páginas da massa e do documento real desta máquina:
# as decisões certas tinham confiança de 7 a 23 - as páginas em pé e as duas
# deitadas de verdade (12 e 15) -, e o único palpite errado, 1,2. O 5 fica longe
# dos dois lados.
CONFIANCA_MINIMA_PARA_GIRAR = 5


def _endireitar(imagem):
    """Gira a imagem quando o conteúdo dela está deitado.

    O campo de rotação do PDF não serve para descobrir isso: um documento
    deitado dentro de uma página em pé tem esse campo zerado, e só olhando a
    imagem dá para perceber (regra RN-6). Quem olha é o próprio Tesseract, com
    o detector de orientação.

    Quando o detector não consegue decidir - página quase vazia, pouco texto -
    ele reclama em vez de responder. Aí a página segue como está: girar no
    palpite estragaria uma página que talvez estivesse certa.

    E às vezes ele responde chutando: numa página desbotada e cheia de chuvisco
    ele mandou virar de cabeça para baixo, com confiança 1,2, uma página que
    estava em pé - e o PaddleOCR, que lia 4 dos 12 CPFs dela, passou a ler
    nenhum (conferência da etapa 3 da funcionalidade 7, 19/10/2026). Resposta
    abaixo da confiança mínima conta como "não decidiu".
    """
    try:
        leitura = pytesseract.image_to_osd(
            imagem, output_type=pytesseract.Output.DICT
        )
    except Exception:
        return imagem

    graus = leitura.get("rotate", 0)
    if graus % 360 == 0:
        return imagem
    if leitura.get("orientation_conf", 0) < CONFIANCA_MINIMA_PARA_GIRAR:
        return imagem
    return imagem.rotate(-graus, expand=True)

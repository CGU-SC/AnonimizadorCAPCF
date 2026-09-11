"""Lê o texto de um PDF virando cada página em imagem e passando para o OCR.

Este arquivo não sabe que existe uma janela: ele avisa o andamento e pergunta
se foi cancelado através de duas funções que quem chama entrega. É isso que
permite testar a leitura sem abrir o programa.

Nada aqui sai da máquina. O Tesseract é um programa instalado no próprio
Windows, e o documento não viaja para lugar nenhum.
"""
import io
import os
import shutil
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image

# 300 pontos por polegada é a densidade que o Tesseract recomenda para texto
# impresso (regra RN-7 da spec 002). Abaixo disso ele erra mais; acima, fica
# mais lento sem ganhar precisão.
PONTOS_POR_POLEGADA = 300

# O pacote de português. Sem ele o OCR lê acentuação como lixo.
IDIOMA = "por"

# Onde o instalador do Tesseract costuma deixar o programa no Windows. Ele não
# entra no caminho que o Windows procura sozinho, então procurar aqui é o que
# faz o programa funcionar sem ninguém configurar nada em cada máquina do
# núcleo.
PASTAS_DE_COSTUME = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


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


def localizar_tesseract():
    """Devolve o caminho do Tesseract nesta máquina, ou None quando não acha."""
    no_caminho_do_windows = shutil.which("tesseract")
    if no_caminho_do_windows:
        return Path(no_caminho_do_windows)

    candidatos = list(PASTAS_DE_COSTUME)
    pasta_do_usuario = os.environ.get("LOCALAPPDATA")
    if pasta_do_usuario:
        candidatos.append(
            str(Path(pasta_do_usuario) / "Programs" / "Tesseract-OCR" / "tesseract.exe")
        )

    for candidato in candidatos:
        if Path(candidato).exists():
            return Path(candidato)
    return None


def preparar_motor():
    """Aponta o pytesseract para o Tesseract desta máquina.

    Levanta MotorNaoEncontrado quando não há Tesseract instalado - o aviso na
    tela e a instalação assistida são de uma etapa própria.
    """
    caminho = localizar_tesseract()
    if caminho is None:
        raise MotorNaoEncontrado(
            "O motor de leitura (Tesseract) não foi encontrado nesta máquina."
        )
    pytesseract.pytesseract.tesseract_cmd = str(caminho)
    return caminho


def ler_documento(caminho, ao_avancar=None, foi_cancelado=None):
    """Lê o documento inteiro e devolve o texto de cada página, em ordem.

    ao_avancar(pagina, total) é chamado antes de cada página, para a tela poder
    mostrar a contagem. foi_cancelado() é perguntado no mesmo momento: quando
    responde que sim, a leitura para e o que já foi lido é jogado fora - nada
    é gravado antes da conferência (regra RN-2).
    """
    preparar_motor()

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
                paginas.append(_ler_pagina(documento[indice]))
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
    return pytesseract.image_to_string(imagem, lang=IDIOMA)


def _desenhar(pagina):
    pixels = pagina.get_pixmap(dpi=PONTOS_POR_POLEGADA)
    return Image.open(io.BytesIO(pixels.tobytes("png")))


def _endireitar(imagem):
    """Gira a imagem quando o conteúdo dela está deitado.

    O campo de rotação do PDF não serve para descobrir isso: um documento
    deitado dentro de uma página em pé tem esse campo zerado, e só olhando a
    imagem dá para perceber (regra RN-6). Quem olha é o próprio Tesseract, com
    o detector de orientação.

    Quando o detector não consegue decidir - página quase vazia, pouco texto -
    ele reclama em vez de responder. Aí a página segue como está: girar no
    palpite estragaria uma página que talvez estivesse certa.
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
    return imagem.rotate(-graus, expand=True)

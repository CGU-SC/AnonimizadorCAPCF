"""Os desenhos da faixa da esquerda (emenda de 03/11/2026 da spec 001).

Desenhados pelo próprio programa, com traço, e não lidos de arquivo de imagem:
o programa roda sem rede e não pode depender de nada baixado (RN-11), e um
arquivo a mais teria de ser lembrado na receita do instalador, como os modelos
do PaddleOCR - esquecido, o ícone some só na máquina de quem usa. As medidas
vêm do rascunho aprovado (mockups/janela/04-tres-direcoes.html, direção C).
"""
from PySide6.QtCore import QLineF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

import estilo


class SimboloDoPrograma(QWidget):
    """O quadrado azul do cabeçalho, com uma página e uma linha tarjada.

    Provisório: a marca definitiva do programa é decisão de identidade visual, e
    quando ela existir toma este lugar (fora de escopo da emenda).
    """

    LADO = 34
    # O desenho da página foi feito numa grade de 22 x 22, centrada no quadrado.
    GRADE = 22

    def __init__(self):
        super().__init__()
        self.setFixedSize(QSize(self.LADO, self.LADO))

    def sizeHint(self):
        return QSize(self.LADO, self.LADO)

    def paintEvent(self, _evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QColor(estilo.COR_DESTAQUE))
        pintor.drawRoundedRect(QRectF(0, 0, self.LADO, self.LADO), 8, 8)

        margem = (self.LADO - self.GRADE) / 2
        pintor.translate(margem, margem)
        caneta = QPen(QColor("#ffffff"), 1.6)
        caneta.setCapStyle(Qt.RoundCap)
        caneta.setJoinStyle(Qt.RoundJoin)
        pintor.setPen(caneta)
        pintor.setBrush(Qt.NoBrush)

        pagina = QPainterPath()
        pagina.moveTo(6.5, 2.5)
        pagina.lineTo(13, 2.5)
        pagina.lineTo(17, 6.5)
        pagina.lineTo(17, 18)
        pagina.quadTo(17, 19.5, 15.5, 19.5)
        pagina.lineTo(6.5, 19.5)
        pagina.quadTo(5, 19.5, 5, 18)
        pagina.lineTo(5, 4)
        pagina.quadTo(5, 2.5, 6.5, 2.5)
        pintor.drawPath(pagina)

        dobra = QPainterPath()
        dobra.moveTo(13, 2.5)
        dobra.lineTo(13, 6.5)
        dobra.lineTo(17, 6.5)
        pintor.drawPath(dobra)

        pintor.drawLine(QLineF(8, 10.5, 14, 10.5))

        # A linha tarjada é cheia, e não traço: é ela que diz "aqui havia um
        # dado, e ele foi tirado".
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QColor("#ffffff"))
        pintor.drawRoundedRect(QRectF(8, 13.5, 6, 2.2), 1, 1)

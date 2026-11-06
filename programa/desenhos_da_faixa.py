"""Os desenhos da faixa da esquerda (emenda de 03/11/2026 da spec 001).

Desenhados pelo próprio programa, com traço, e não lidos de arquivo de imagem:
o programa roda sem rede e não pode depender de nada baixado (RN-11), e um
arquivo a mais teria de ser lembrado na receita do instalador, como os modelos
do PaddleOCR - esquecido, o ícone some só na máquina de quem usa. As medidas
vêm do rascunho aprovado (mockups/janela/04-tres-direcoes.html, direção C).
"""
from PySide6.QtCore import QLineF, QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QWidget

import estilo

# O desenho fica num quadrado de 18 px, e o ícone tem 6 px a mais de largura,
# vazios, à direita. Somados aos 4 px que o botão do Qt já põe entre ícone e
# texto, dão os 10 px de respiro do rascunho. O botão não deixa aumentar esse
# espaço, e espaços escritos no texto mudariam o texto do item.
LADO_DO_ICONE = 18
RESPIRO_DO_ICONE = 6
TAMANHO_DO_ICONE = QSize(LADO_DO_ICONE + RESPIRO_DO_ICONE, LADO_DO_ICONE)
# Os ícones foram desenhados numa grade de 20 x 20, a mesma do rascunho.
GRADE_DO_ICONE = 20
# Uma cópia para cada ampliação de tela comum no Windows (100%, 125%, 150%, 200%
# e 250%): o Qt escolhe a que serve, e o traço não sai borrado de esticado.
AMPLIACOES = (1, 1.25, 1.5, 2, 2.5)


def _caneta(cor, largura=1.6):
    caneta = QPen(QColor(cor), largura)
    caneta.setCapStyle(Qt.RoundCap)
    caneta.setJoinStyle(Qt.RoundJoin)
    return caneta


def _lupa(pintor):
    pintor.drawEllipse(QPointF(8.5, 8.5), 5.5, 5.5)
    pintor.drawLine(QLineF(12.6, 12.6, 17.5, 17.5))


def _cadeado(pintor):
    pintor.drawRoundedRect(QRectF(4, 9, 12, 9), 2, 2)
    alca = QPainterPath()
    alca.moveTo(7, 9)
    alca.lineTo(7, 6.5)
    alca.arcTo(QRectF(7, 3.5, 6, 6), 180, -180)
    alca.lineTo(13, 9)
    pintor.drawPath(alca)
    pintor.drawLine(QLineF(10, 12.5, 10, 14.5))


def _engrenagem(pintor):
    # Os dentes são um anel grosso de traço interrompido, e não oito dentes
    # desenhados um a um: o anel de raio 7 tem 44 de volta, e oito dentes com oito
    # vãos de 2,75 cabem nele certinho. O Qt mede o traço em larguras de caneta.
    cor = pintor.pen().color()
    dentes = QPen(cor, 2.8)
    dentes.setCapStyle(Qt.FlatCap)
    dentes.setDashPattern([2.75 / 2.8, 2.75 / 2.8])
    pintor.setPen(dentes)
    pintor.drawEllipse(QPointF(10, 10), 7, 7)
    pintor.setPen(_caneta(cor))
    pintor.drawEllipse(QPointF(10, 10), 5.2, 5.2)
    pintor.drawEllipse(QPointF(10, 10), 2, 2)


DESENHOS = {"lupa": _lupa, "cadeado": _cadeado, "engrenagem": _engrenagem}


def pintar_desenho(pintor, desenho, cor):
    """Pinta um dos desenhos na grade de 20 x 20, com o pintor já na escala
    certa. É o mesmo traço no item da faixa e no título das telas (RN-14)."""
    pintor.setPen(_caneta(cor))
    pintor.setBrush(Qt.NoBrush)
    DESENHOS[desenho](pintor)


def _pintar(desenho, cor, ampliacao):
    largura = round(TAMANHO_DO_ICONE.width() * ampliacao)
    altura = round(TAMANHO_DO_ICONE.height() * ampliacao)
    imagem = QPixmap(largura, altura)
    imagem.fill(Qt.transparent)
    pintor = QPainter(imagem)
    pintor.setRenderHint(QPainter.Antialiasing)
    pintor.scale(LADO_DO_ICONE * ampliacao / GRADE_DO_ICONE,
                 LADO_DO_ICONE * ampliacao / GRADE_DO_ICONE)
    pintar_desenho(pintor, desenho, cor)
    pintor.end()
    return imagem


def icone_do_item(desenho):
    """O ícone de um item do menu, em duas cores: cinza no item normal, claro no
    marcado (RN-12). A troca é do próprio Qt, pelo estado do botão."""
    icone = QIcon()
    for ampliacao in AMPLIACOES:
        icone.addPixmap(_pintar(desenho, estilo.COR_TEXTO_SECUNDARIO, ampliacao),
                        QIcon.Normal, QIcon.Off)
        icone.addPixmap(_pintar(desenho, estilo.COR_TEXTO, ampliacao),
                        QIcon.Normal, QIcon.On)
    return icone


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
        caneta = QPen(QColor(estilo.COR_DESENHO_DO_SIMBOLO), 1.6)
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
        pintor.setBrush(QColor(estilo.COR_DESENHO_DO_SIMBOLO))
        pintor.drawRoundedRect(QRectF(8, 13.5, 6, 2.2), 1, 1)

"""As peças que as telas de Configurações de IA repetem (rascunho ia/01)."""
from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QAbstractButton,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

import estilo

# Cabe na janela mínima: 900 px, menos o menu, as margens do painel e a barra de
# rolagem. Largura fixa porque frase com quebra de linha precisa dela para a
# altura sair certa ("O que já nos mordeu").
LARGURA_DO_CONTEUDO = 600


class Interruptor(QAbstractButton):
    """O switch do rascunho: o Qt não tem um, e a caixinha de marcar não diz
    "ligado" do mesmo jeito."""

    LARGURA = 36
    ALTURA = 20

    def __init__(self):
        super().__init__()
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(QSize(self.LARGURA, self.ALTURA))

    def sizeHint(self):
        return QSize(self.LARGURA, self.ALTURA)

    def paintEvent(self, _evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        ligado = self.isChecked()
        trilho = estilo.COR_DESTAQUE if ligado else estilo.COR_BORDA
        bolinha = "#ffffff" if ligado else estilo.COR_TEXTO_SECUNDARIO
        # Apagado continua dizendo se está ligado: só fica mais fraco.
        pintor.setOpacity(1.0 if self.isEnabled() else 0.45)
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QColor(trilho))
        pintor.drawRoundedRect(QRectF(0, 0, self.LARGURA, self.ALTURA), 10, 10)
        pintor.setBrush(QColor(bolinha))
        x = self.LARGURA - self.ALTURA + 2 if ligado else 2
        pintor.drawEllipse(QRectF(x, 2, self.ALTURA - 4, self.ALTURA - 4))


class Frase(QLabel):
    """Uma frase que pode quebrar linha, sem perder a última.

    A altura é refeita a cada texto novo, e com a fonte do estilo já posta: sem
    isso o Qt reserva a altura de uma linha, e o resto some para fora da borda,
    sem nada acusar ("O que já nos mordeu").
    """

    def __init__(self, texto="", largura=LARGURA_DO_CONTEUDO, cor=None, pequeno=True,
                 forte=False):
        super().__init__()
        self._largura = largura
        # Texto puro: o motivo vem da IA, e um "<b>" escrito por ela não pode mudar a
        # tela (RN-28).
        self.setTextFormat(Qt.PlainText)
        self.setWordWrap(True)
        self.setFixedWidth(largura)
        tamanho = estilo.TEXTO_PEQUENO if pequeno else estilo.TEXTO_BASE
        cor = cor or estilo.COR_TEXTO_SECUNDARIO
        self.setStyleSheet(
            f"font-size: {tamanho}px; color: {cor};"
            f"font-weight: {600 if forte else 400};"
            "border: none; background: transparent;"
        )
        self.setText(texto)

    def setText(self, texto):
        super().setText(texto)
        self.ensurePolished()
        self.setMinimumHeight(self.heightForWidth(self._largura) if texto else 0)


class Faixa(QFrame):
    """A faixa de aviso com a borda grossa à esquerda, em três tons."""

    TONS = {
        "info": ("rgba(59, 110, 165, 26)", estilo.COR_DESTAQUE),
        "alerta": ("rgba(217, 164, 65, 26)", estilo.COR_ALERTA),
        "erro": ("rgba(217, 83, 79, 26)", estilo.COR_ERRO),
    }

    def __init__(self, tom="info", largura=LARGURA_DO_CONTEUDO):
        super().__init__()
        self.setObjectName("faixa_da_ia")
        self.setFixedWidth(largura)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(estilo.ESPACO_3, estilo.ESPACO_2,
                                  estilo.ESPACO_3, estilo.ESPACO_2)
        layout.setSpacing(estilo.ESPACO_1)
        self.frase = Frase(largura=largura - 2 * estilo.ESPACO_3 - 4,
                           cor=estilo.COR_TEXTO)
        layout.addWidget(self.frase)
        self.tom(tom)

    def tom(self, tom):
        fundo, borda = self.TONS[tom]
        self.setStyleSheet(
            f"""
            QFrame#faixa_da_ia {{
                background-color: {fundo};
                border-left: 4px solid {borda};
                border-radius: {estilo.RAIO}px;
            }}
            """
        )

    def mostrar(self, texto, tom=None):
        if tom:
            self.tom(tom)
        self.frase.setText(texto)
        self.setVisible(True)


def titulo_de_tela(texto):
    rotulo = QLabel(texto)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_GRANDE}px; font-weight: 600;"
        f"color: {estilo.COR_TEXTO};"
    )
    return rotulo


def rotulo_de_campo(texto):
    rotulo = QLabel(texto)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px; color: {estilo.COR_TEXTO_SECUNDARIO};"
    )
    return rotulo


def campo_de_texto(largura=LARGURA_DO_CONTEUDO):
    campo = QLineEdit()
    campo.setFixedWidth(largura)
    campo.setStyleSheet(
        f"""
        QLineEdit {{
            background-color: {estilo.COR_FUNDO_ELEVADO};
            border: 1px solid {estilo.COR_BORDA};
            border-radius: {estilo.RAIO}px;
            padding: 6px 10px;
            color: {estilo.COR_TEXTO};
            font-family: {estilo.FONTE_MONO};
            font-size: {estilo.TEXTO_PEQUENO}px;
        }}
        QLineEdit:disabled {{ color: #5d646e; }}
        """
    )
    return campo


def linha_do_switch(interruptor, texto, recuo=0):
    """O switch com o nome ao lado, e o nome clicável como o próprio switch."""
    fora = QWidget()
    linha = QHBoxLayout(fora)
    linha.setContentsMargins(recuo, 0, 0, 0)
    linha.setSpacing(estilo.ESPACO_2)
    nome = QLabel(texto)
    nome.setStyleSheet(
        f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600; color: {estilo.COR_TEXTO};"
    )
    nome.setBuddy(interruptor)
    linha.addWidget(interruptor)
    linha.addWidget(nome)
    linha.addStretch()
    return fora

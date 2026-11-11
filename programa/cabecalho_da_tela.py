"""O título das telas dos módulos (acréscimo de 04/11/2026 à emenda de
03/11/2026 da spec 001, RN-14; rascunho mockups/janela/05-titulo-dos-modulos.html,
direção A).

O ícone do módulo, num quadrado no mesmo azul fraco do item marcado na faixa,
ao lado do título e da legenda, e uma linha fina embaixo. O mesmo desenho nos
dois lugares é o que diz de longe em qual módulo a pessoa está, sem ler.
"""
from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

import estilo
from desenhos_da_faixa import GRADE_DO_ICONE, pintar_desenho


class CaixaDoIcone(QWidget):
    """O quadrado azul fraco com o ícone do módulo, pintado pelo programa como
    os da faixa: sem arquivo de imagem e sem nada baixado (RN-11)."""

    LADO = 38
    LADO_DO_DESENHO = 22

    def __init__(self, desenho):
        super().__init__()
        self.desenho = desenho
        self.setFixedSize(QSize(self.LADO, self.LADO))

    def sizeHint(self):
        return QSize(self.LADO, self.LADO)

    def paintEvent(self, _evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        fundo = QColor(estilo.COR_DESTAQUE)
        fundo.setAlphaF(estilo.FORCA_DO_DESTAQUE_FRACO)
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(fundo)
        pintor.drawRoundedRect(QRectF(0, 0, self.LADO, self.LADO), 8, 8)

        margem = (self.LADO - self.LADO_DO_DESENHO) / 2
        pintor.translate(margem, margem)
        escala = self.LADO_DO_DESENHO / GRADE_DO_ICONE
        pintor.scale(escala, escala)
        pintar_desenho(pintor, self.desenho, estilo.COR_TEXTO)
        pintor.end()


class CabecalhoDaTela(QWidget):
    """O título de uma tela de módulo. `titulo` e `legenda` são os textos, que
    as telas trocam com `setText` quando o documento muda."""

    ESPACO_DO_ICONE = 12
    ESPACO_DO_TEXTO = 2

    def __init__(self, desenho, titulo="", legenda=""):
        super().__init__()
        # A linha de baixo vale só para este quadro, pelo nome, e os textos de
        # dentro ficam transparentes: regra sem alvo pinta cada texto de dentro
        # com uma caixinha de outro tom ("O que já nos mordeu").
        self.setObjectName("cabecalho_da_tela")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            f"QWidget#cabecalho_da_tela {{ border-bottom: 1px solid {estilo.COR_BORDA}; }}"
            "QLabel { background: transparent; }"
        )
        # Fixo: a sobra de altura da tela não é repartida com o título, que
        # cresceria e levaria a linha para baixo da da faixa. A altura é a que
        # `_refazer_altura` calcula.
        politica = self.sizePolicy()
        politica.setVerticalPolicy(QSizePolicy.Fixed)
        self.setSizePolicy(politica)

        por_fora = QVBoxLayout(self)
        # O respiro embaixo é menor que o do cabeçalho da faixa (20 px) porque o
        # título daqui é maior: com mais, o conjunto passaria dos 60 px, e a linha
        # desceria abaixo da da faixa.
        por_fora.setContentsMargins(0, 0, 0, estilo.ESPACO_2)
        por_fora.setSpacing(0)
        linha = QHBoxLayout()
        linha.setSpacing(self.ESPACO_DO_ICONE)
        self.icone = CaixaDoIcone(desenho)
        linha.addWidget(self.icone, alignment=Qt.AlignVCenter)

        textos = QVBoxLayout()
        textos.setSpacing(self.ESPACO_DO_TEXTO)
        self.titulo = QLabel(titulo)
        self.titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_GRANDE}px; font-weight: 700;"
            f"color: {estilo.COR_TEXTO};"
        )
        self.legenda = _Legenda(legenda, self._refazer_altura)
        self.legenda.setWordWrap(True)
        self.legenda.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )
        # Texto puro: o nome do arquivo entra na legenda das telas do caminho
        # do PDF, e um "<b>" no nome não pode mudar a tela.
        self.titulo.setTextFormat(Qt.PlainText)
        self.legenda.setTextFormat(Qt.PlainText)
        textos.addWidget(self.titulo)
        textos.addWidget(self.legenda)
        linha.addLayout(textos, stretch=1)
        por_fora.addLayout(linha)
        # O que sobra da altura mínima fica embaixo do texto, e não entre o
        # título e a legenda.
        por_fora.addStretch()
        self._refazer_altura()

    def _refazer_altura(self):
        """A altura do título, refeita a cada legenda nova e a cada largura nova.

        O Qt não faz esta conta sozinho: a legenda trocada depois de a tela
        estar montada continuava com a altura de uma linha, e a segunda linha
        saía cortada pela metade, sem nada acusar. Foi o que aconteceu com o
        aviso de que os CPFs saem inteiros, na janela mínima ("O que já nos
        mordeu"). Com a altura do cabeçalho da faixa como piso, a linha de
        baixo continua a dela; a legenda que desce para a segunda linha
        empurra a linha junto.
        """
        for rotulo in (self.titulo, self.legenda):
            # Sem isto o Qt mede com a fonte padrão, e não com a do estilo, e
            # a última linha some.
            rotulo.ensurePolished()
        largura = max(1, self.width() - CaixaDoIcone.LADO - self.ESPACO_DO_ICONE)
        # A medida do Qt nunca fica abaixo da altura mínima da legenda: sem
        # zerar antes, a legenda que encolhe continuaria com duas linhas.
        self.legenda.setMinimumHeight(0)
        legenda = self.legenda.heightForWidth(largura) if self.legenda.text() else 0
        self.legenda.setMinimumHeight(legenda)
        textos = self.titulo.sizeHint().height() + (self.ESPACO_DO_TEXTO + legenda if legenda else 0)
        altura = max(estilo.ALTURA_DO_CABECALHO,
                     max(textos, CaixaDoIcone.LADO) + estilo.ESPACO_2)
        if (self.minimumHeight(), self.maximumHeight()) != (altura, altura):
            self.setFixedHeight(altura)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        if evento.size().width() != evento.oldSize().width():
            self._refazer_altura()


class _Legenda(QLabel):
    """A legenda que avisa o título quando o texto muda, para ele refazer a
    altura. As telas trocam a legenda com `setText` quando o documento muda."""

    def __init__(self, texto, ao_mudar):
        self._ao_mudar = None
        super().__init__(texto)
        self._ao_mudar = ao_mudar

    def setText(self, texto):
        super().setText(texto)
        if self._ao_mudar:
            self._ao_mudar()

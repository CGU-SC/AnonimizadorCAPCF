"""Uma fileira de peças que desce para a linha de baixo quando não cabe.

O Qt não traz essa arrumação pronta: as fileiras dele (QHBoxLayout) espremem as
peças até o texto de dentro sair cortado, e nada acusa. Foi o que acontecia
com os selos da revisão do Anonimizar: com os cinco acesos, eles pediam uns
770 px, e na janela do tamanho em que ela abre havia 724 (conferência da
entrega, 23/09/2026). Aqui cada peça fica sempre do tamanho que pede, e a que
não cabe desce inteira.

Segue o exemplo de arrumação em fluxo da documentação do próprio Qt.
"""
from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout


class LinhaQueDesce(QLayout):
    def __init__(self, espaco):
        super().__init__()
        self._itens = []
        self._espaco = espaco

    # --------------------------------------------- o que todo QLayout pede

    def addItem(self, item):
        self._itens.append(item)

    def count(self):
        return len(self._itens)

    def itemAt(self, indice):
        if 0 <= indice < len(self._itens):
            return self._itens[indice]
        return None

    def takeAt(self, indice):
        if 0 <= indice < len(self._itens):
            return self._itens.pop(indice)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    # A altura depende da largura: numa janela estreita, as peças ocupam mais
    # linhas. É isto que faz a tela abrir espaço para a linha que desceu, em
    # vez de deixá-la por cima do que vem embaixo.
    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, largura):
        return self._arrumar(QRect(0, 0, largura, 0), so_medir=True)

    def setGeometry(self, retangulo):
        super().setGeometry(retangulo)
        self._arrumar(retangulo, so_medir=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        # A menor largura possível é a da maior peça sozinha numa linha.
        tamanho = QSize()
        for item in self._visiveis():
            tamanho = tamanho.expandedTo(item.minimumSize())
        margens = self.contentsMargins()
        return tamanho + QSize(margens.left() + margens.right(),
                               margens.top() + margens.bottom())

    # ----------------------------------------------------------- a arrumação

    def _visiveis(self):
        # Peça escondida não ocupa lugar: o selo de um grupo sem números some
        # de vez, e não deixa um buraco na fileira.
        return [item for item in self._itens if not item.isEmpty()]

    def _arrumar(self, retangulo, so_medir):
        margens = self.contentsMargins()
        area = retangulo.adjusted(margens.left(), margens.top(),
                                  -margens.right(), -margens.bottom())
        x, y = area.x(), area.y()
        altura_da_linha = 0
        for item in self._visiveis():
            tamanho = item.sizeHint()
            if x > area.x() and x + tamanho.width() > area.right() + 1:
                x = area.x()
                y += altura_da_linha + self._espaco
                altura_da_linha = 0
            if not so_medir:
                item.setGeometry(QRect(QPoint(x, y), tamanho))
            x += tamanho.width() + self._espaco
            altura_da_linha = max(altura_da_linha, tamanho.height())
        return y + altura_da_linha - retangulo.y() + margens.bottom()

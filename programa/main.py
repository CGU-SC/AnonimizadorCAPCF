# Ponto de entrada do AnomizadorCAPCF: abre a janela do programa.
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

NOME_PROGRAMA = "AnomizadorCAPCF"
LARGURA_MENU = 220

# Cores do sistema de design do projeto (mockups/sistema-de-design.md), tema escuro.
COR_FUNDO = "#1e2228"
COR_FUNDO_ELEVADO = "#262b33"
COR_BORDA = "#383e47"
COR_TEXTO = "#e8eaed"
COR_TEXTO_SECUNDARIO = "#9aa1ac"


class MenuLateral(QWidget):
    """A faixa fixa da esquerda, com o nome do programa e os itens de navegação."""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(LARGURA_MENU)
        self.setStyleSheet(
            f"background-color: {COR_FUNDO_ELEVADO}; border-right: 1px solid {COR_BORDA};"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 24, 0, 24)
        layout.setSpacing(4)

        nome = QLabel(NOME_PROGRAMA)
        nome.setStyleSheet(
            f"color: {COR_TEXTO}; font-size: 20px; font-weight: 700;"
            f"padding: 0 16px 16px 16px; border-bottom: 1px solid {COR_BORDA};"
        )
        layout.addWidget(nome)

        self.botao_ocr = self._criar_item_menu("Gerar OCR")
        self.botao_anonimizar = self._criar_item_menu("Anonimizar")
        layout.addWidget(self.botao_ocr)
        layout.addWidget(self.botao_anonimizar)
        layout.addStretch()

    def _criar_item_menu(self, texto):
        botao = QPushButton(texto)
        botao.setCursor(Qt.PointingHandCursor)
        botao.setStyleSheet(
            f"""
            QPushButton {{
                text-align: left;
                color: {COR_TEXTO_SECUNDARIO};
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 12px;
                margin: 0 8px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.06);
            }}
            """
        )
        return botao


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(NOME_PROGRAMA)
        # Tamanho de referência do rascunho aprovado (mockups/janela/01-interface-da-janela.html).
        self.resize(900, 520)

        raiz = QWidget()
        raiz_layout = QHBoxLayout(raiz)
        raiz_layout.setContentsMargins(0, 0, 0, 0)
        raiz_layout.setSpacing(0)

        self.menu = MenuLateral()
        raiz_layout.addWidget(self.menu)

        # O painel principal ainda fica vazio - o conteúdo entra nas próximas etapas.
        self.painel = QWidget()
        self.painel.setStyleSheet(f"background-color: {COR_FUNDO};")
        raiz_layout.addWidget(self.painel)

        self.setCentralWidget(raiz)


def main():
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# Ponto de entrada do AnomizadorCAPCF: abre a janela do programa.
import sys

from PySide6.QtWidgets import QApplication, QMainWindow

NOME_PROGRAMA = "AnomizadorCAPCF"


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(NOME_PROGRAMA)
        # Tamanho de referência do rascunho aprovado (mockups/janela/01-interface-da-janela.html).
        self.resize(900, 520)


def main():
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# Ponto de entrada do AnomizadorCAPCF: abre a janela do programa.
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
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
COR_DESTAQUE = "#3b6ea5"
COR_ALERTA = "#d9a441"


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
            QPushButton:checked {{
                background-color: {COR_DESTAQUE};
                color: #ffffff;
                font-weight: 600;
            }}
            """
        )
        return botao


class PainelVazio(QWidget):
    """O que aparece no painel quando nenhum módulo foi escolhido ainda."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        icone = QLabel("◧")
        icone.setAlignment(Qt.AlignCenter)
        icone.setStyleSheet(f"font-size: 40px; color: {COR_TEXTO_SECUNDARIO};")

        titulo = QLabel("Escolha um módulo para começar")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"font-size: 20px; color: {COR_TEXTO};")

        texto = QLabel('Clique em "Gerar OCR" ou "Anonimizar" no menu ao lado.')
        texto.setAlignment(Qt.AlignCenter)
        texto.setStyleSheet(f"font-size: 15px; color: {COR_TEXTO_SECUNDARIO};")

        layout.addWidget(icone)
        layout.addWidget(titulo)
        layout.addWidget(texto)


class PainelModuloNaoConstruido(QWidget):
    """Ocupa o lugar de um módulo que ainda não existe, para o encaixe futuro."""

    def __init__(self, nome_modulo):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        selo = QLabel("AINDA NÃO CONSTRUÍDO")
        selo.setAlignment(Qt.AlignCenter)
        selo.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {COR_ALERTA};"
            "letter-spacing: 1px;"
        )

        titulo = QLabel(nome_modulo)
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"font-size: 20px; font-weight: 600; color: {COR_TEXTO};")

        texto = QLabel("Este módulo entra numa próxima etapa do projeto.")
        texto.setAlignment(Qt.AlignCenter)
        texto.setStyleSheet(f"font-size: 15px; color: {COR_TEXTO_SECUNDARIO};")

        layout.addWidget(selo)
        layout.addWidget(titulo)
        layout.addWidget(texto)


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

        # QStackedWidget porque o painel troca de conteúdo conforme o módulo
        # escolhido no menu: cada página é um estado da tela.
        self.painel = QStackedWidget()
        self.painel.setStyleSheet(f"background-color: {COR_FUNDO};")
        self.painel_vazio = PainelVazio()
        self.painel.addWidget(self.painel_vazio)
        raiz_layout.addWidget(self.painel)

        self.itens_do_menu = []
        self._ligar_item_ao_painel(self.menu.botao_ocr, "Gerar OCR")
        self._ligar_item_ao_painel(self.menu.botao_anonimizar, "Anonimizar")

        self.setCentralWidget(raiz)

    def _ligar_item_ao_painel(self, botao, nome_modulo):
        """Faz o item do menu se marcar e trazer o painel daquele módulo."""
        painel_do_modulo = PainelModuloNaoConstruido(nome_modulo)
        self.painel.addWidget(painel_do_modulo)

        botao.setCheckable(True)
        self.itens_do_menu.append(botao)
        botao.clicked.connect(
            lambda: self._ao_clicar_no_item(botao, painel_do_modulo)
        )

    def _ao_clicar_no_item(self, botao_clicado, painel_do_modulo):
        # O clique já marcou ou desmarcou o item antes de chegar aqui, então é o
        # estado novo do botão que diz para onde o painel vai.
        if botao_clicado.isChecked():
            # Só um item marcado por vez - regra RN-2 da spec 001.
            for outro in self.itens_do_menu:
                if outro is not botao_clicado:
                    outro.setChecked(False)
            self.painel.setCurrentWidget(painel_do_modulo)
        else:
            # Clicar no item já marcado é o jeito de sair do módulo sem precisar
            # entrar no outro - regra RN-3 da spec 001.
            self.painel.setCurrentWidget(self.painel_vazio)


def main():
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

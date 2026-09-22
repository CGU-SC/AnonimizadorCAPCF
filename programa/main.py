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

from estilo import (
    COR_BORDA,
    COR_DESTAQUE,
    COR_FUNDO,
    COR_FUNDO_ELEVADO,
    COR_TEXTO,
    COR_TEXTO_SECUNDARIO,
    LARGURA_MENU,
)
from painel_anonimizar import PainelAnonimizar
from painel_ocr import PainelOcr

NOME_PROGRAMA = "AnomizadorCAPCF"


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


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(NOME_PROGRAMA)
        # Cresceu de 900x520 para caber a tela de conferência, que é dividida em
        # duas metades: com 900 de largura cada metade fica com uns 330, e o
        # texto ao lado da página do documento vira uma coluna estreita demais
        # para comparar linha por linha. 1000x640 é o tamanho em que o rascunho
        # aprovado dela foi desenhado.
        self.resize(1000, 640)
        # Abaixo disto a conferência deixa de servir, então a janela não encolhe.
        self.setMinimumSize(900, 560)

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
        self.painel_ocr = PainelOcr()
        self._ligar_item_ao_painel(self.menu.botao_ocr, self.painel_ocr)
        self.painel_anonimizar = PainelAnonimizar()
        self._ligar_item_ao_painel(
            self.menu.botao_anonimizar, self.painel_anonimizar
        )

        self.setCentralWidget(raiz)

    def closeEvent(self, evento):
        """Antes de fechar, pergunta o que fecharia trabalho não salvo e para o
        que estiver rodando.

        Fechar a janela com a revisão do Anonimizar aberta jogava fora tudo o
        que a pessoa tinha decidido, sem uma palavra (premissa de sair sem
        salvar, spec 003). Agora a janela fica de pé, a pergunta aparece no
        painel, e o botão dela diz "Fechar sem salvar" - que é o que a pessoa
        acabou de pedir.

        Fechar a janela no meio de uma leitura fazia o programa estourar em vez
        de fechar limpo, e o Windows mostrava a caixa de "o programa parou de
        funcionar" - que assusta e ainda deixa a dúvida de se o documento foi
        mexido (não foi, nunca é).
        """
        if self.painel_anonimizar.perguntar_antes_de_descartar(
                self.close, rotulo_descartar="Fechar sem salvar"):
            # A pergunta está no painel do Anonimizar: o item do menu vai para
            # ele, senão a pessoa ouve a pergunta sem ver de onde ela veio.
            self._ir_para_o_anonimizar()
            evento.ignore()
            return
        # As duas leituras param, e não só a do Gerar OCR: desde a etapa 7 o
        # PDF também é lido pelo Anonimizar, e a leitura dele sobrevivia ao
        # fechar - trazendo de volta a caixa de "o programa parou de funcionar"
        # que este fechar existe para evitar (revisão da etapa 7).
        self.painel_ocr.encerrar()
        self.painel_anonimizar.encerrar()
        super().closeEvent(evento)

    def _ir_para_o_anonimizar(self):
        for item in self.itens_do_menu:
            item.setChecked(item is self.menu.botao_anonimizar)
        self.painel.setCurrentWidget(self.painel_anonimizar)

    def _ligar_item_ao_painel(self, botao, painel_do_modulo):
        """Faz o item do menu se marcar e trazer o painel daquele módulo."""
        self.painel.addWidget(painel_do_modulo)

        botao.setCheckable(True)
        self.itens_do_menu.append(botao)
        botao.clicked.connect(
            lambda: self._ao_clicar_no_item(botao, painel_do_modulo)
        )

    def _ao_clicar_no_item(self, botao_clicado, painel_do_modulo):
        # O clique já marcou ou desmarcou o item antes de chegar aqui, então é o
        # estado novo do botão que diz para onde o painel vai. Clicar no item já
        # marcado é o jeito de sair do módulo sem entrar no outro (RN-3 da spec
        # 001), e leva ao painel vazio.
        destino = (painel_do_modulo if botao_clicado.isChecked()
                   else self.painel_vazio)

        # Saindo do Anonimizar com revisão não salva, a pergunta vem primeiro, e
        # o menu volta a marcar o Anonimizar enquanto ela está na tela: item
        # marcado num módulo e pergunta de outro na tela é o tipo de tela que
        # ninguém entende (premissa de sair sem salvar, spec 003).
        if (self.painel.currentWidget() is self.painel_anonimizar
                and destino is not self.painel_anonimizar):
            if self.painel_anonimizar.perguntar_antes_de_descartar(
                    lambda: self._mostrar_modulo(botao_clicado, destino)):
                self._ir_para_o_anonimizar()
                return

        self._mostrar_modulo(botao_clicado, destino)

    def _mostrar_modulo(self, botao_clicado, destino):
        """Marca o item certo no menu e traz o painel dele.

        O destino vem decidido de fora, e não do estado do botão: passando pela
        pergunta de descartar, o menu volta a marcar o Anonimizar enquanto ela
        está na tela, e lendo o botão de novo o programa acabava no painel vazio
        em vez de no módulo que a pessoa tinha pedido.
        """
        # Só um item marcado por vez - regra RN-2 da spec 001.
        for item in self.itens_do_menu:
            item.setChecked(destino is not self.painel_vazio
                            and item is botao_clicado)
        self.painel.setCurrentWidget(destino)


def main():
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

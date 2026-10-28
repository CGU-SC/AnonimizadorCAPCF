# Ponto de entrada do Anonimizador CAPCF: abre a janela do programa.
import sys

from PySide6.QtCore import QRect, QSize, Qt
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
    TEXTO_PEQUENO,
)
import preferencias
from painel_anonimizar import PainelAnonimizar
from painel_ocr import PainelOcr
from versao import VERSAO

NOME_PROGRAMA = "Anonimizador CAPCF"

# O bloco do preferencias.ini em que a janela lembra como foi fechada (emenda
# de 28/10/2026 da spec 001).
LEMBRAR_COMO = "janela"
MAXIMIZADA = "sim"
NAO_MAXIMIZADA = "não"

# Cresceu de 900x520 para caber a tela de conferência, que é dividida em duas
# metades: com 900 de largura cada metade fica com uns 330, e o texto ao lado
# da página do documento vira uma coluna estreita demais para comparar linha
# por linha. 1000x640 é o tamanho em que o rascunho aprovado dela foi
# desenhado, e é o da janela fora do maximizado de quem não tem tamanho
# lembrado (RN-8).
TAMANHO_NORMAL = QSize(1000, 640)
# Abaixo disto a conferência deixa de servir, então a janela não encolhe.
TAMANHO_MINIMO = QSize(900, 560)


def como_abrir(lembrado, area, moldura):
    """Onde a janela abre fora do maximizado, e se abre maximizada.

    `lembrado` é o bloco da janela no preferencias.ini (largura, altura e
    maximizada, em texto, ou None onde nada foi lembrado); `area` é a parte da
    tela que a janela pode ocupar, sem a barra de tarefas; `moldura` é a barra
    de título e as bordas que o Windows põe em volta. Devolve o retângulo de
    dentro da moldura - o que o Qt chama de geometria da janela.
    """
    tamanho = _tamanho_lembrado(lembrado)
    if tamanho is None:
        # Primeiro uso, ou lembrança que não dá para ler (RN-4).
        tamanho = (TAMANHO_NORMAL.width(), TAMANHO_NORMAL.height())
        maximizada = True
    else:
        maximizada = lembrado.get("maximizada") == MAXIMIZADA

    # O tamanho lembrado é o de dentro; quem precisa caber na tela é a janela
    # com a moldura (RN-7). Sem descontar a barra de título, a janela do
    # tamanho da tela saía com o pé atrás da barra de tarefas. A conta é feita
    # em número comum, e não no tamanho do Qt, que não aceita número grande:
    # um tamanho absurdo escrito à mão no arquivo derrubava o programa ao
    # abrir, e agora só encolhe para caber (lente crítica da etapa 3).
    cabe_largura = area.width() - moldura.left() - moldura.right()
    cabe_altura = area.height() - moldura.top() - moldura.bottom()
    largura = max(TAMANHO_MINIMO.width(), min(tamanho[0], cabe_largura))
    altura = max(TAMANHO_MINIMO.height(), min(tamanho[1], cabe_altura))

    # Sempre no meio da tela, e nunca a posição lembrada: quem fechou num
    # segundo monitor que não está mais ligado abriria a janela fora da vista
    # (RN-6). Numa tela menor que o mínimo, onde ela não cabe de jeito nenhum,
    # vale o canto de cima à esquerda: ela passa pela direita e por baixo, e a
    # barra de título, por onde é arrastada, fica sempre à vista.
    largura_por_fora = largura + moldura.left() + moldura.right()
    altura_por_fora = altura + moldura.top() + moldura.bottom()
    esquerda = area.left() + max(0, (area.width() - largura_por_fora) // 2)
    topo = area.top() + max(0, (area.height() - altura_por_fora) // 2)
    por_dentro = QRect(esquerda + moldura.left(), topo + moldura.top(), largura, altura)
    return por_dentro, maximizada


def _tamanho_lembrado(lembrado):
    """A largura e a altura lembradas, ou None se não há um tamanho que dê
    para usar."""
    if not lembrado:
        return None
    try:
        largura = int(lembrado.get("largura"))
        altura = int(lembrado.get("altura"))
    except (TypeError, ValueError):
        return None
    if largura <= 0 or altura <= 0:
        return None
    return largura, altura


class MenuLateral(QWidget):
    """A faixa fixa da esquerda, com o nome do programa e os itens de navegação."""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(LARGURA_MENU)
        # A cor vale só para a faixa, pelo nome, e a faixa precisa ser mandada
        # pintar o próprio fundo: um QWidget comum ignora a cor da folha de
        # estilo. Sem as duas coisas, a regra caía só nos textos de dentro - o
        # bloco do nome saía em #262b33 e o resto da faixa no cinza padrão do
        # Windows (entrega, 24/09/2026).
        self.setObjectName("menu_lateral")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            f"QWidget#menu_lateral {{ background-color: {COR_FUNDO_ELEVADO};"
            f" border-right: 1px solid {COR_BORDA}; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 24, 0, 24)
        layout.setSpacing(4)

        # Numa linha só, o nome pede 244 px e a faixa tem 220: o fim sairia
        # cortado, sem aviso. A quebra vai escrita no texto, e não pela quebra
        # automática do Qt, que reserva a altura de uma linha e corta a segunda.
        nome = QLabel(NOME_PROGRAMA.replace(" ", "\n"))
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

        # No pé da faixa, discreta: é para quem precisa responder "qual versão
        # você está usando?" ao relatar um defeito, e não para o uso do dia.
        # Fundo transparente: a cor da faixa também pinta os textos de dentro
        # dela, e a versão saía numa caixa de outro tom (entrega, 24/09/2026).
        self.versao = QLabel(f"versão {VERSAO}")
        self.versao.setStyleSheet(
            f"color: {COR_TEXTO_SECUNDARIO}; font-size: {TEXTO_PEQUENO}px;"
            "padding: 0 16px; border: none; background: transparent;"
        )
        layout.addWidget(self.versao)

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
        self.setMinimumSize(TAMANHO_MINIMO)

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
        self.painel_ocr = PainelOcr(
            ao_seguir_para_anonimizar=self._seguir_para_anonimizar)
        self._ligar_item_ao_painel(self.menu.botao_ocr, self.painel_ocr)
        self.painel_anonimizar = PainelAnonimizar()
        self._ligar_item_ao_painel(
            self.menu.botao_anonimizar, self.painel_anonimizar
        )

        self.setCentralWidget(raiz)
        self._preparar_para_abrir()

    def _preparar_para_abrir(self):
        """Dá à janela o tamanho e o lugar de abrir (emenda de 28/10/2026 da
        spec 001). Quem a mostra é o `abrir`."""
        # Criar a janela do Windows agora, antes de ela aparecer, é o que faz o
        # Qt já saber o tamanho da barra de título - e só com ele a janela do
        # tamanho da tela cabe inteira.
        self.winId()
        # A tela é a principal: a posição não é lembrada (RN-6), e é nela que o
        # Windows abre um programa novo.
        retangulo, self.abre_maximizada = como_abrir(
            preferencias.ler_bloco(LEMBRAR_COMO), self.screen().availableGeometry(),
            self.windowHandle().frameMargins())
        # O retângulo vale também quando ela abre maximizada: é o tamanho a que
        # ela volta quando a pessoa sai do maximizado.
        self.setGeometry(retangulo)

    def abrir(self):
        """Mostra a janela como ela foi fechada da última vez."""
        if self.abre_maximizada:
            self.showMaximized()
        else:
            self.show()

    def _lembrar_como_foi_fechada(self):
        """Grava o tamanho e se estava maximizada (RN-5)."""
        # Maximizada, o tamanho de agora é o da tela: o que vale lembrar é o de
        # quando ela sai do maximizado, que é o que o "normal" guarda. Medido
        # com o próprio Windows minimizando a janela: minimizada, ela continua
        # dizendo se estava maximizada e o tamanho de antes (lentes críticas das
        # etapas 3 e 4).
        maximizada = self.isMaximized()
        tamanho = self.normalGeometry().size()
        preferencias.gravar_juntos(LEMBRAR_COMO, {
            "largura": tamanho.width(),
            "altura": tamanho.height(),
            "maximizada": MAXIMIZADA if maximizada else NAO_MAXIMIZADA,
        })

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
        # Só aqui, depois da pergunta de descartar: a janela que ficou de pé
        # porque a pessoa voltou para salvar ainda não fechou.
        self._lembrar_como_foi_fechada()
        super().closeEvent(evento)

    def _seguir_para_anonimizar(self, caminho, paginas):
        """O texto conferido no Gerar OCR segue para a revisão (RN-16).

        O menu passa a marcar "Anonimizar" antes de tudo: se lá houver uma
        revisão aberta e não salva, é lá que a pergunta antes de descartar vai
        aparecer, e a pessoa precisa ver de onde ela vem.
        """
        self._ir_para_o_anonimizar()
        self.painel_anonimizar.receber_texto_conferido(caminho, paginas)

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
    janela.abrir()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

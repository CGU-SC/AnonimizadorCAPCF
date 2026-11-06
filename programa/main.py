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

# As cores são lidas como `estilo.COR_...`, na hora em que cada peça nasce, e
# nunca trazidas para cá pelo nome: trazidas, ficariam com o valor do tema de
# quando este arquivo carregou (RN-17 da spec 001). As medidas não mudam com o
# tema, e podem vir pelo nome.
import estilo
from estilo import ALTURA_DO_CABECALHO, LARGURA_MENU, TEXTO_PEQUENO
from desenhos_da_faixa import TAMANHO_DO_ICONE, SimboloDoPrograma, icone_do_item
import preferencias
from painel_anonimizar import PainelAnonimizar
from painel_ia import HABILITAR, LM_STUDIO, SERVIDOR, PainelIa
from tela_do_tema import TEMA
from painel_ocr import PainelOcr
from versao import VERSAO

NOME_PROGRAMA = "Anonimizador CAPCF"

# O filete do item marcado da faixa, no azul mais vivo (RN-13 da spec 001).
LARGURA_DO_FILETE = 3

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
            f"QWidget#menu_lateral {{ background-color: {estilo.COR_FUNDO_ELEVADO};"
            f" border-right: 1px solid {estilo.COR_BORDA}; }}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 24, 0, 24)
        layout.setSpacing(4)

        layout.addWidget(self._criar_cabecalho())
        # O respiro entre a linha do cabeçalho e o primeiro item, como no rascunho
        # aprovado: sem ele, o primeiro item encosta na linha.
        layout.addSpacing(12)

        # O submenu da IA toma o lugar do menu inteiro (RN-2 da spec 004); o
        # cabeçalho, com a versão, fica parado, fora da troca (RN-10 da spec 001).
        self.paginas = QStackedWidget()
        self.paginas.setStyleSheet("background: transparent;")
        self.pagina_principal = QWidget()
        principal = QVBoxLayout(self.pagina_principal)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(4)
        self.botao_ocr = self._criar_item_menu("Gerar OCR", "lupa")
        self.botao_anonimizar = self._criar_item_menu("Anonimizar", "cadeado")
        # Depois do espaço vazio, longe dos módulos: quem só lê documento não
        # tropeça nele (RN-1 da spec 004).
        # A engrenagem é o sinal de "aqui se configura", e separa este item dos dois
        # módulos de cima (pedido na conferência da funcionalidade 4, 31/10/2026).
        # Era um emoji, colorido, e passou a ser desenhada como a lupa e o cadeado,
        # para os três serem da mesma família (emenda de 03/11/2026 da spec 001).
        # Era "Configurações de IA"; com o Tema, passou a guardar mais que a IA
        # (RN-20 da spec 001, emenda de 05/11/2026 da spec 004).
        self.botao_config_ia = self._criar_item_menu("Configurações", "engrenagem")
        principal.addWidget(self.botao_ocr)
        principal.addWidget(self.botao_anonimizar)
        principal.addStretch()
        principal.addWidget(self.botao_config_ia)

        self.pagina_ia = QWidget()
        submenu = QVBoxLayout(self.pagina_ia)
        submenu.setContentsMargins(0, 0, 0, 0)
        submenu.setSpacing(4)
        # O "‹ Voltar" fica sem ícone: a seta escrita já é o desenho dele (RN-21).
        self.botao_voltar_ia = self._criar_item_menu("‹ Voltar")
        self.botao_tema = self._criar_item_menu("Tema", "tema")
        self.botao_lm_studio = self._criar_item_menu("LM Studio", "lm_studio")
        self.botao_servidor_ia = self._criar_item_menu("Servidor de IA Interno", "servidor")
        self.botao_habilitar_ia = self._criar_item_menu("Habilitar IA", "habilitar")
        self.titulos_de_secao = (_titulo_de_secao("Configurações Gerais"),
                                 _titulo_de_secao("Configurações de IA"))
        self.itens_do_submenu = (self.botao_tema, self.botao_lm_studio,
                                 self.botao_servidor_ia, self.botao_habilitar_ia)
        for item in self.itens_do_submenu:
            item.setCheckable(True)
        for peca in (self.botao_voltar_ia,
                     self.titulos_de_secao[0], self.botao_tema,
                     self.titulos_de_secao[1], self.botao_lm_studio,
                     self.botao_servidor_ia, self.botao_habilitar_ia):
            submenu.addWidget(peca)
        submenu.addStretch()

        self.paginas.addWidget(self.pagina_principal)
        self.paginas.addWidget(self.pagina_ia)
        layout.addWidget(self.paginas, stretch=1)

    def _criar_cabecalho(self):
        """O símbolo, o nome e a versão, no alto da faixa (RN-9 da spec 001).

        O nome vai em duas linhas de tamanhos diferentes porque, numa linha só e
        no tamanho de título, ele pede 244 px e a faixa tem 220. A versão vira a
        segunda linha do nome, em vez de ficar solta no pé: é para quem precisa
        responder "qual versão você está usando?" ao relatar um defeito, e no pé
        ninguém a achava (pedido da conferência da funcionalidade 4, 01/11/2026).
        """
        cabecalho = QWidget()
        # A linha de baixo vale só para este quadro, pelo nome, e os textos de
        # dentro ficam transparentes: regra sem alvo pinta cada texto de dentro
        # com uma caixinha de outro tom ("O que já nos mordeu").
        cabecalho.setObjectName("cabecalho_da_faixa")
        cabecalho.setAttribute(Qt.WA_StyledBackground, True)
        cabecalho.setStyleSheet(
            f"QWidget#cabecalho_da_faixa {{ border-bottom: 1px solid {estilo.COR_BORDA}; }}"
            "QLabel { background: transparent; }"
        )
        # A mesma altura do título das telas dos módulos, para a linha de baixo
        # das duas ficar na mesma altura (RN-14 da spec 001).
        cabecalho.setMinimumHeight(ALTURA_DO_CABECALHO)
        linha = QHBoxLayout(cabecalho)
        linha.setContentsMargins(16, 0, 16, 20)
        linha.setSpacing(10)
        linha.addWidget(SimboloDoPrograma())

        primeiro, resto = NOME_PROGRAMA.split(" ", 1)
        textos = QVBoxLayout()
        textos.setSpacing(2)
        self.nome = QLabel(primeiro)
        self.nome.setStyleSheet(f"color: {estilo.COR_TEXTO}; font-size: 16px; font-weight: 700;")
        self.versao = QLabel(f"{resto} · versão {VERSAO}")
        self.versao.setStyleSheet(
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; font-size: {TEXTO_PEQUENO}px;"
        )
        textos.addWidget(self.nome)
        textos.addWidget(self.versao)
        linha.addLayout(textos)
        linha.addStretch()
        return cabecalho

    def _criar_item_menu(self, texto, desenho=None):
        botao = QPushButton(texto)
        botao.setCursor(Qt.PointingHandCursor)
        # Todo item tem ícone, menos o "‹ Voltar" (RN-21 da spec 001, que revogou o
        # "submenu só texto" da emenda de 03/11/2026).
        if desenho:
            botao.setIcon(icone_do_item(desenho))
            botao.setIconSize(TAMANHO_DO_ICONE)
        # O marcado era um bloco azul cheio, a coisa mais forte da tela; virou um
        # fundo azul fraco com um filete à esquerda (RN-13 da spec 001). O filete
        # diz "este é o escolhido" para quem distingue mal as cores. Todo item já
        # tem o filete, transparente, e por isso 3 px a menos de espaço à
        # esquerda: o texto não pula para o lado ao ser marcado. O texto marcado
        # é o mesmo claro do ícone marcado (RN-12), e não branco puro.
        botao.setStyleSheet(
            f"""
            QPushButton {{
                text-align: left;
                color: {estilo.COR_TEXTO_SECUNDARIO};
                background: transparent;
                border: none;
                border-left: {LARGURA_DO_FILETE}px solid transparent;
                border-radius: 6px;
                padding: 12px 12px 12px {12 - LARGURA_DO_FILETE}px;
                margin: 0 8px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {estilo.COR_PASSAR_O_MOUSE};
            }}
            QPushButton:checked {{
                background-color: {estilo.COR_DESTAQUE_FRACO};
                border-left-color: {estilo.COR_DESTAQUE_HOVER};
                color: {estilo.COR_TEXTO};
                font-weight: 600;
            }}
            """
        )
        return botao


def _titulo_de_secao(texto):
    """O título de uma seção do submenu: letra pequena, no cinza de apoio, e um
    filete fino que corre à direita dele (RN-20 da spec 001).

    É texto e não botão: não se clica e nunca fica marcado. As medidas são as do
    rascunho aprovado; com o filete dos dois lados, como no desenho do pedido,
    sobrariam só 10 px de cada lado na faixa de 220.
    """
    titulo = QWidget()
    linha = QHBoxLayout(titulo)
    linha.setContentsMargins(20, 10, 20, 4)
    linha.setSpacing(8)
    rotulo = QLabel(texto)
    rotulo.setStyleSheet(
        f"font-size: {TEXTO_PEQUENO}px; font-weight: 600;"
        f"color: {estilo.COR_TEXTO_SECUNDARIO}; background: transparent;"
    )
    filete = QWidget()
    filete.setObjectName("filete")
    filete.setAttribute(Qt.WA_StyledBackground, True)
    filete.setFixedHeight(1)
    filete.setStyleSheet(f"QWidget#filete {{ background-color: {estilo.COR_BORDA}; }}")
    linha.addWidget(rotulo)
    linha.addWidget(filete, stretch=1, alignment=Qt.AlignVCenter)
    titulo.rotulo = rotulo
    return titulo


class PainelVazio(QWidget):
    """O que aparece no painel quando nenhum módulo foi escolhido ainda."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        icone = QLabel("◧")
        icone.setAlignment(Qt.AlignCenter)
        icone.setStyleSheet(f"font-size: 40px; color: {estilo.COR_TEXTO_SECUNDARIO};")

        titulo = QLabel("Escolha um módulo para começar")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"font-size: 20px; color: {estilo.COR_TEXTO};")

        texto = QLabel('Clique em "Gerar OCR" ou "Anonimizar" no menu ao lado.')
        texto.setAlignment(Qt.AlignCenter)
        texto.setStyleSheet(f"font-size: 15px; color: {estilo.COR_TEXTO_SECUNDARIO};")

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
        self.painel.setStyleSheet(f"background-color: {estilo.COR_FUNDO};")
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
        self.painel_ia = PainelIa()
        self.painel.addWidget(self.painel_ia)
        self.menu.botao_config_ia.clicked.connect(self._abrir_configuracoes_de_ia)
        self.menu.botao_voltar_ia.clicked.connect(self._fechar_configuracoes_de_ia)
        for item, nome in zip(self.menu.itens_do_submenu,
                              (TEMA, LM_STUDIO, SERVIDOR, HABILITAR)):
            item.clicked.connect(lambda _=False, i=item, n=nome: self._mostrar_tela_de_ia(i, n))

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
        self.painel_ia.encerrar()
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

    def _abrir_configuracoes_de_ia(self):
        """O menu vira o submenu - perguntando antes, se isso descartaria uma
        revisão (RN-2 da spec 004)."""
        if (self.painel.currentWidget() is self.painel_anonimizar
                and self.painel_anonimizar.perguntar_antes_de_descartar(
                    self._entrar_nas_configuracoes_de_ia)):
            self._ir_para_o_anonimizar()
            return
        self._entrar_nas_configuracoes_de_ia()

    def _entrar_nas_configuracoes_de_ia(self):
        for item in self.itens_do_menu:
            item.setChecked(False)
        self.menu.paginas.setCurrentWidget(self.menu.pagina_ia)
        # Entra pela primeira opção, o Tema, e não mais pelo LM Studio (RN-22).
        self._mostrar_tela_de_ia(self.menu.botao_tema, TEMA)
        self.painel.setCurrentWidget(self.painel_ia)

    def _mostrar_tela_de_ia(self, item_clicado, nome):
        # Só um item marcado por vez, como no menu de sempre (RN-3 da spec 004);
        # clicar no já marcado não desmarca: aqui não há tela de boas-vindas.
        for item in self.menu.itens_do_submenu:
            item.setChecked(item is item_clicado)
        self.painel_ia.mostrar(nome)

    def _fechar_configuracoes_de_ia(self):
        """Volta ao menu de sempre, sem desligar nem mudar nada (RN-3)."""
        self.menu.paginas.setCurrentWidget(self.menu.pagina_principal)
        self.painel.setCurrentWidget(self.painel_vazio)

    def _ir_para_o_anonimizar(self):
        self.menu.paginas.setCurrentWidget(self.menu.pagina_principal)
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

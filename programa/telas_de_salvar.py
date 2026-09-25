"""As telas depois da conferência: escolher a saída, dizer onde salvar, e pronto.

Segue o rascunho aprovado mockups/ocr/08-salvar-o-arquivo.html, com uma troca
decidida na aprovação: o botão do módulo seguinte diz "Seguir para Anonimizar".

São quatro telas pequenas num arquivo só porque formam um caminho só, que se
lê de cima para baixo: escolher a saída, dizer onde salvar, responder se já
existe arquivo com o nome, e ver onde ficou gravado.
"""
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import arquivo_md
import estilo


class TelaSaida(QWidget):
    """As duas saídas do texto conferido, lado a lado."""

    def __init__(self, ao_salvar, ao_voltar, ao_processar_outro,
                 ao_anonimizar=None):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(_titulo("Texto conferido. E agora?"))
        self.legenda = _legenda("")
        layout.addWidget(self.legenda)
        layout.addSpacing(estilo.ESPACO_4)

        cartoes = QHBoxLayout()
        cartoes.setSpacing(estilo.ESPACO_4)

        # O Anonimizar vem à esquerda, com o botão em destaque, e o salvar à
        # direita, sem destaque (rascunho 08, estado 4): o caminho que não
        # expõe nada é o mais fácil de clicar, como em todo o programa.
        self.botao_anonimizar = QPushButton("Seguir para Anonimizar")
        self.botao_anonimizar.setCursor(Qt.PointingHandCursor)
        self.botao_anonimizar.setStyleSheet(estilo.estilo_botao(principal=True))
        if ao_anonimizar is not None:
            # O clique do Qt manda um argumento junto; sem o lambda, ele cairia
            # no primeiro parâmetro de quem for chamado (lição da etapa 5).
            self.botao_anonimizar.clicked.connect(lambda _=False: ao_anonimizar())
        else:
            self.botao_anonimizar.setEnabled(False)
        cartoes.addWidget(_cartao_de_saida(
            "🔒",
            "Seguir para o Anonimizar",
            "Leva este texto direto para a revisão, que mascara os CPFs — sem "
            "passar por arquivo nenhum.",
            self.botao_anonimizar,
        ))

        self.botao_salvar = QPushButton("Escolher onde salvar")
        self.botao_salvar.setCursor(Qt.PointingHandCursor)
        self.botao_salvar.setStyleSheet(estilo.estilo_botao(principal=False))
        self.botao_salvar.clicked.connect(ao_salvar)
        # "Com os CPFs inteiros" fica escrito no próprio cartão: é a diferença
        # entre as duas saídas, e ela não pode depender de a pessoa lembrar.
        cartoes.addWidget(_cartao_de_saida(
            "💾",
            "Salvar o texto como está",
            "Gera um arquivo .md na sua máquina, com o texto do jeito que você "
            "deixou — com os CPFs inteiros.",
            self.botao_salvar,
        ))

        layout.addLayout(cartoes)
        layout.addStretch()

        rodape = QHBoxLayout()
        rodape.setSpacing(estilo.ESPACO_3)
        rodape.addWidget(_botao("Voltar à conferência", ao_voltar, principal=False))
        rodape.addWidget(_botao("Processar outro documento", ao_processar_outro,
                                principal=False))
        rodape.addStretch()
        layout.addLayout(rodape)

    def mostrar(self, nome_do_documento, paginas, corrigidas):
        self.legenda.setText(resumo_do_documento(nome_do_documento, paginas, corrigidas))


class TelaSalvar(QWidget):
    """O caminho do arquivo já preenchido, editável, e o aviso dos CPFs."""

    def __init__(self, ao_salvar, ao_voltar):
        super().__init__()
        self._ao_salvar = ao_salvar
        self._pasta_sugerida = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(_titulo("Onde salvar o arquivo"))
        self.legenda = _legenda("")
        layout.addWidget(self.legenda)
        layout.addSpacing(estilo.ESPACO_4)

        rotulo = QLabel("CAMINHO DO ARQUIVO")
        rotulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 700;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; letter-spacing: 1px;"
        )
        layout.addWidget(rotulo)
        layout.addSpacing(estilo.ESPACO_1)

        linha = QHBoxLayout()
        linha.setSpacing(estilo.ESPACO_2)
        self.campo = QLineEdit()
        self.campo.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {estilo.COR_FUNDO_ELEVADO};
                border: 1px solid {estilo.COR_DESTAQUE};
                border-radius: {estilo.RAIO}px;
                padding: 8px {estilo.ESPACO_3}px;
                font-family: {estilo.FONTE_MONO};
                font-size: {estilo.TEXTO_PEQUENO}px;
                color: {estilo.COR_TEXTO};
            }}
            """
        )
        self.campo.returnPressed.connect(self._salvar)
        linha.addWidget(self.campo, stretch=1)
        linha.addWidget(_botao("Escolher pasta…", self._escolher_pasta, principal=False))
        layout.addLayout(linha)
        layout.addSpacing(estilo.ESPACO_4)

        layout.addWidget(_aviso_dos_cpfs())
        layout.addSpacing(estilo.ESPACO_3)

        self.problema = QLabel()
        self.problema.setWordWrap(True)
        self.problema.setVisible(False)
        self.problema.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; color: {estilo.COR_ERRO};"
        )
        layout.addWidget(self.problema)
        layout.addStretch()

        acoes = QHBoxLayout()
        acoes.setSpacing(estilo.ESPACO_3)
        acoes.addWidget(_botao("Salvar", self._salvar, principal=True))
        acoes.addWidget(_botao("Voltar", ao_voltar, principal=False))
        acoes.addStretch()
        layout.addLayout(acoes)

    def mostrar(self, caminho, nome_do_documento, paginas, corrigidas):
        self.legenda.setText(resumo_do_documento(nome_do_documento, paginas, corrigidas))
        self.campo.setText(str(caminho))
        # A pasta sugerida fica guardada para o caso de a pessoa digitar só um
        # nome, sem pasta nenhuma - ver _salvar.
        self._pasta_sugerida = Path(caminho).parent
        self.problema.setVisible(False)

    def avisar(self, texto):
        """Um problema com o caminho escolhido, sem sair da tela."""
        self.problema.setText(texto)
        self.problema.setVisible(True)

    def _escolher_pasta(self):
        escolhido = escolher_onde_salvar(self, self.campo.text())
        if escolhido:
            self.campo.setText(escolhido)

    def _salvar(self):
        caminho, problema = arquivo_md.conferir_destino(
            self.campo.text(), self._pasta_sugerida)
        if problema == arquivo_md.FALTA_O_CAMINHO:
            self.avisar("Escreva onde o arquivo vai ser salvo.")
            return
        if problema == arquivo_md.FALTA_A_PASTA:
            self.avisar("Escreva o caminho completo, com a pasta.")
            return
        if problema == arquivo_md.PASTA_NAO_EXISTE:
            self.avisar(
                "A pasta escolhida não existe. Escolha outra pelo botão "
                "\"Escolher pasta…\"."
            )
            return
        self._ao_salvar(caminho)


def escolher_onde_salvar(tela, caminho_atual):
    """Abre a janela do Windows e devolve o caminho escolhido, ou "".

    Ela começa na pasta do caminho que já está no campo, e não numa pasta
    lembrada de outro uso: nada é guardado entre um uso e outro.

    E ela **não** pergunta sobre substituir (achado na conferência da etapa 5 do
    Anonimizar, 18/09/2026): escolhendo um arquivo que já existe, ela perguntava
    "deseja substituir?" e, respondido que sim, só devolvia o caminho - nada era
    gravado. Quem respondeu achava ter mandado salvar, e o programa parecia não
    fazer nada. A pergunta fica só na tela do programa, que mostra a data do
    arquivo que está lá.

    Os dois módulos abrem a mesma janela daqui: escrita em cada tela, ela já
    precisou do mesmo conserto duas vezes no mesmo dia.
    """
    caminho, _ = QFileDialog.getSaveFileName(
        tela, "Escolher onde salvar", caminho_atual,
        "Arquivo de texto Markdown (*.md)",
        options=QFileDialog.Option.DontConfirmOverwrite,
    )
    return caminho


class TelaSobrescrever(QWidget):
    """A pergunta antes de apagar um arquivo que já existe (regra RN-16)."""

    LARGURA_DA_CAIXA = 520
    LARGURA_DO_TEXTO = 460

    def __init__(self, ao_escrever_por_cima, ao_outro_nome):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        caixa = QFrame()
        caixa.setFixedWidth(self.LARGURA_DA_CAIXA)
        # O estilo vale só para a caixa, pelo nome. Escrito para todo QFrame,
        # valia também para cada texto de dentro (todo texto do Qt é um
        # QFrame), que repetia o fundo e a barra colorida por cima da caixa - o
        # mesmo vale para as caixas e cartões deste arquivo (entrega,
        # 24/09/2026). E os textos ficam transparentes: senão pintam o fundo
        # da janela, que a regra do painel em main.py passa para tudo o que
        # está dentro dele.
        caixa.setObjectName("quadro")
        caixa.setStyleSheet(
            f"""
            QFrame#quadro {{
                background-color: rgba(217, 83, 79, 26);
                border-left: 4px solid {estilo.COR_ERRO};
                border-radius: {estilo.RAIO}px;
            }}
            QLabel {{ background: transparent; }}
            """
        )
        dentro = QVBoxLayout(caixa)
        dentro.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_3,
                                  estilo.ESPACO_4, estilo.ESPACO_3)
        dentro.setSpacing(estilo.ESPACO_2)

        titulo = QLabel("Já existe um arquivo com esse nome")
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO}; border: none;"
        )
        dentro.addWidget(titulo)

        self.explicacao = QLabel()
        self.explicacao.setWordWrap(True)
        self.explicacao.setFixedWidth(self.LARGURA_DO_TEXTO)
        self.explicacao.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
        )
        dentro.addWidget(self.explicacao)

        layout.addWidget(caixa, alignment=Qt.AlignCenter)
        layout.addSpacing(estilo.ESPACO_4)

        acoes = QHBoxLayout()
        acoes.setSpacing(estilo.ESPACO_3)
        acoes.addStretch()
        # O caminho que não destrói nada é o que fica em destaque, e mais fácil
        # de clicar sem pensar. Escrever por cima fica disponível, mas pede
        # uma decisão.
        acoes.addWidget(_botao("Escrever por cima", ao_escrever_por_cima,
                               principal=False))
        acoes.addWidget(_botao("Salvar com outro nome", ao_outro_nome,
                               principal=True))
        acoes.addStretch()
        layout.addLayout(acoes)

    def mostrar(self, caminho):
        caminho = Path(caminho)
        quando = datetime.fromtimestamp(caminho.stat().st_mtime)
        # A data está ali para a pessoa perceber se o arquivo que já existe é o
        # dela mesma, de uma tentativa anterior, ou de outro trabalho.
        self.explicacao.setText(
            f"{caminho.name} já está nessa pasta, gravado em "
            f"{quando:%d/%m/%Y} às {quando:%H:%M}.\n\n"
            "Escrever por cima apaga o que estava lá, e isso não se desfaz."
        )
        # A frase muda de tamanho conforme o nome do arquivo: a altura é
        # recalculada a cada vez, senão o fim dela sai cortado.
        self.explicacao.setMinimumHeight(
            self.explicacao.heightForWidth(self.LARGURA_DO_TEXTO)
        )


class TelaDescartar(QWidget):
    """A pergunta antes de jogar fora texto conferido que não foi salvo (RN-1).

    Segue o rascunho aprovado mockups/ocr/09-antes-de-descartar.html. Sem ela,
    meia hora de correção sumia com um clique em "Processar outro documento",
    sem aviso e sem volta.
    """

    LARGURA_DA_CAIXA = 520
    LARGURA_DO_TEXTO = 460

    def __init__(self, ao_descartar, ao_voltar):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        caixa = QFrame()
        caixa.setFixedWidth(self.LARGURA_DA_CAIXA)
        caixa.setObjectName("quadro")
        caixa.setStyleSheet(
            f"""
            QFrame#quadro {{
                background-color: rgba(217, 164, 65, 26);
                border-left: 4px solid {estilo.COR_ALERTA};
                border-radius: {estilo.RAIO}px;
            }}
            QLabel {{ background: transparent; }}
            """
        )
        dentro = QVBoxLayout(caixa)
        dentro.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_3,
                                  estilo.ESPACO_4, estilo.ESPACO_3)
        dentro.setSpacing(estilo.ESPACO_2)

        # O título e o rótulo do botão mudam conforme quem pergunta: o Gerar OCR
        # fala do texto conferido, o Anonimizar fala da revisão, e fechando a
        # janela o botão diz "Fechar sem salvar". A caixa é a mesma nos três.
        self.titulo = QLabel()
        titulo = self.titulo
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO}; border: none;"
        )
        dentro.addWidget(titulo)

        self.explicacao = QLabel()
        self.explicacao.setWordWrap(True)
        self.explicacao.setFixedWidth(self.LARGURA_DO_TEXTO)
        self.explicacao.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
        )
        dentro.addWidget(self.explicacao)

        layout.addWidget(caixa, alignment=Qt.AlignCenter)
        layout.addSpacing(estilo.ESPACO_4)

        acoes = QHBoxLayout()
        acoes.setSpacing(estilo.ESPACO_3)
        acoes.addStretch()
        # Como na pergunta de sobrescrever: o caminho que não destrói nada é o
        # que fica em destaque, e mais fácil de clicar sem pensar.
        self.botao_descartar = _botao("Descartar e seguir", ao_descartar,
                                      principal=False)
        acoes.addWidget(self.botao_descartar)
        acoes.addWidget(_botao("Voltar e salvar", ao_voltar, principal=True))
        acoes.addStretch()
        layout.addLayout(acoes)

    def mostrar(self, titulo, explicacao, rotulo_descartar="Descartar e seguir"):
        """A pergunta, com as palavras de quem está perguntando.

        Os dois módulos usam esta caixa: o Gerar OCR fala do texto conferido, o
        Anonimizar fala da revisão, e quem fecha a janela vê "Fechar sem salvar"
        no lugar de "Descartar e seguir". O que se perde é sempre dito com
        número, porque é isso que deixa decidir num olhar: nada mexido perde
        pouco, uma tarde de trabalho perde uma tarde.
        """
        self.titulo.setText(titulo)
        self.explicacao.setText(explicacao)
        self.botao_descartar.setText(rotulo_descartar)
        self.explicacao.setMinimumHeight(
            self.explicacao.heightForWidth(self.LARGURA_DO_TEXTO)
        )


class TelaGravado(QWidget):
    """Onde o arquivo ficou, e o caminho de volta para o próximo documento."""

    def __init__(self, ao_processar_outro):
        super().__init__()
        self._caminho = None

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(estilo.ESPACO_2)

        icone = QLabel("✓")
        icone.setAlignment(Qt.AlignCenter)
        icone.setStyleSheet(f"font-size: 40px; color: {estilo.COR_SUCESSO};")
        layout.addWidget(icone)

        titulo = _titulo("Arquivo gravado")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        self.legenda = _legenda("")
        self.legenda.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.legenda)
        layout.addSpacing(estilo.ESPACO_3)

        self.caminho = QLabel()
        self.caminho.setAlignment(Qt.AlignCenter)
        # O caminho pode ser selecionado com o mouse: é a coisa que a pessoa
        # mais precisa copiar desta tela, para achar o arquivo ou mandá-lo.
        self.caminho.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.caminho.setStyleSheet(
            f"font-family: {estilo.FONTE_MONO}; font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO}; background-color: {estilo.COR_FUNDO_ELEVADO};"
            f"border: 1px solid {estilo.COR_BORDA}; border-radius: {estilo.RAIO}px;"
            f"padding: {estilo.ESPACO_2}px {estilo.ESPACO_3}px;"
        )
        layout.addWidget(self.caminho, alignment=Qt.AlignCenter)
        layout.addSpacing(estilo.ESPACO_4)

        acoes = QHBoxLayout()
        acoes.setSpacing(estilo.ESPACO_3)
        acoes.addStretch()
        acoes.addWidget(_botao("Abrir a pasta", self._abrir_a_pasta, principal=True))
        acoes.addWidget(_botao("Processar outro documento", ao_processar_outro,
                               principal=False))
        acoes.addStretch()
        layout.addLayout(acoes)

    def mostrar(self, caminho, paginas, corrigidas):
        self._caminho = Path(caminho)
        self.caminho.setText(str(self._caminho))
        self.legenda.setText(resumo_do_documento(None, paginas, corrigidas))

    def _abrir_a_pasta(self):
        if self._caminho is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._caminho.parent)))


# --------------------------------------------------------------- pedaços

def resumo_do_documento(nome_do_documento, paginas, corrigidas):
    partes = []
    if nome_do_documento:
        partes.append(nome_do_documento)
    detalhe = f"{paginas} " + ("página" if paginas == 1 else "páginas")
    if corrigidas:
        detalhe += f", {corrigidas} com correção sua"
    partes.append(detalhe)
    return " — ".join(partes)


def _aviso_dos_cpfs():
    """O aviso que a regra RN-14 exige, com todas as letras, antes de gravar."""
    caixa = QFrame()
    caixa.setObjectName("quadro")
    caixa.setStyleSheet(
        f"""
        QFrame#quadro {{
            background-color: rgba(217, 164, 65, 31);
            border-left: 4px solid {estilo.COR_ALERTA};
            border-radius: {estilo.RAIO}px;
        }}
        QLabel {{ background: transparent; }}
        """
    )
    dentro = QVBoxLayout(caixa)
    dentro.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_3,
                              estilo.ESPACO_4, estilo.ESPACO_3)
    dentro.setSpacing(estilo.ESPACO_1)

    titulo = QLabel("⚠ Este arquivo sai com os CPFs inteiros")
    titulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
        f"color: {estilo.COR_ALERTA}; border: none;"
    )
    # O aviso continua dizendo que o arquivo sai com os CPFs inteiros, e passa
    # a dizer por onde se chega ao Anonimizar, que agora existe (RN-17).
    texto = QLabel(
        "Este módulo lê e confere o texto; ele não mascara nada. Para mascarar "
        "os CPFs, volte e escolha \"Seguir para Anonimizar\", ou use o item "
        "Anonimizar do menu. Trate este arquivo com o mesmo cuidado do "
        "documento original."
    )
    texto.setWordWrap(True)
    texto.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px;"
        f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
    )
    dentro.addWidget(titulo)
    dentro.addWidget(texto)
    return caixa


def _cartao_de_saida(icone, nome, explicacao, botao, desligado=False):
    cartao = QFrame()
    cartao.setObjectName("quadro")
    cartao.setStyleSheet(
        f"""
        QFrame#quadro {{
            background-color: {estilo.COR_FUNDO_ELEVADO};
            border: 1px solid {estilo.COR_BORDA};
            border-radius: {estilo.RAIO}px;
        }}
        QLabel {{ background: transparent; }}
        """
    )
    dentro = QVBoxLayout(cartao)
    dentro.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_4,
                              estilo.ESPACO_4, estilo.ESPACO_4)
    dentro.setSpacing(estilo.ESPACO_2)

    cor_do_nome = estilo.COR_TEXTO_APAGADO if desligado else estilo.COR_TEXTO

    rotulo_icone = QLabel(icone)
    rotulo_icone.setAlignment(Qt.AlignCenter)
    rotulo_icone.setStyleSheet("font-size: 30px; border: none;")

    rotulo_nome = QLabel(nome)
    rotulo_nome.setAlignment(Qt.AlignCenter)
    rotulo_nome.setStyleSheet(
        f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
        f"color: {cor_do_nome}; border: none;"
    )

    rotulo_explicacao = QLabel(explicacao)
    rotulo_explicacao.setWordWrap(True)
    rotulo_explicacao.setAlignment(Qt.AlignCenter)
    rotulo_explicacao.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px;"
        f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
    )

    dentro.addWidget(rotulo_icone)
    dentro.addWidget(rotulo_nome)
    dentro.addWidget(rotulo_explicacao)
    dentro.addStretch()
    dentro.addWidget(botao)
    return cartao


def _botao(texto, ao_clicar, principal):
    botao = QPushButton(texto)
    botao.setCursor(Qt.PointingHandCursor)
    botao.setStyleSheet(estilo.estilo_botao(principal=principal))
    botao.clicked.connect(ao_clicar)
    return botao


def _titulo(texto):
    rotulo = QLabel(texto)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_GRANDE}px; font-weight: 600;"
        f"color: {estilo.COR_TEXTO};"
    )
    return rotulo


def _legenda(texto):
    rotulo = QLabel(texto)
    rotulo.setWordWrap(True)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px;"
        f"color: {estilo.COR_TEXTO_SECUNDARIO};"
    )
    return rotulo

"""O painel do item "Gerar OCR": escolher o documento e ver o que ele é.

Segue o rascunho aprovado mockups/ocr/03-escolher-o-documento.html.

Nesta etapa o painel só descobre e informa. A leitura em si - as páginas
viradas em imagem, a contagem e o cancelar - é a etapa seguinte, e por isso o
botão de ler aparece apagado.
"""
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import estilo
from documento import DocumentoNaoAbre, conferir


class PainelOcr(QWidget):
    def __init__(self):
        super().__init__()
        # Aceitar arquivo arrastado é uma das duas formas de escolher o
        # documento previstas na spec 002; a outra é o botão.
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_4,
                                  estilo.ESPACO_5, estilo.ESPACO_5)
        layout.setSpacing(0)

        self.telas = QStackedWidget()
        self.tela_escolher = self._montar_tela_escolher()
        self.tela_conferindo = self._montar_tela_conferindo()
        self.tela_ficha = _TelaFicha(ao_escolher_outro=self.voltar_para_escolher)
        self.tela_erro = _TelaErro(ao_escolher_outro=self.voltar_para_escolher)

        for tela in (self.tela_escolher, self.tela_conferindo,
                     self.tela_ficha, self.tela_erro):
            self.telas.addWidget(tela)

        layout.addWidget(self.telas)

    # ---------------------------------------------------------------- telas

    def _montar_tela_escolher(self):
        tela = QWidget()
        layout = QVBoxLayout(tela)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(_titulo("Gerar OCR"))
        layout.addWidget(_legenda(
            "Converte documento digitalizado em texto para conferência."))
        layout.addSpacing(estilo.ESPACO_4)

        layout.addWidget(self._montar_area_de_arrastar())
        layout.addSpacing(estilo.ESPACO_4)
        layout.addWidget(self._montar_escolha_do_motor())
        layout.addStretch()
        return tela

    def _montar_area_de_arrastar(self):
        area = QFrame()
        area.setStyleSheet(
            f"""
            QFrame {{
                border: 2px dashed {estilo.COR_BORDA};
                border-radius: {estilo.RAIO}px;
                background-color: rgba(255, 255, 255, 4);
            }}
            """
        )
        layout = QVBoxLayout(area)
        layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_5,
                                  estilo.ESPACO_4, estilo.ESPACO_5)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        icone = QLabel("📄")
        icone.setAlignment(Qt.AlignCenter)
        icone.setStyleSheet("font-size: 34px; border: none;")

        chamada = QLabel("Arraste o PDF aqui")
        chamada.setAlignment(Qt.AlignCenter)
        chamada.setStyleSheet(
            f"font-size: {estilo.TEXTO_GRANDE}px; color: {estilo.COR_TEXTO};"
            "border: none;"
        )

        ou = QLabel("ou")
        ou.setAlignment(Qt.AlignCenter)
        ou.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
        )

        botao = QPushButton("Escolher arquivo…")
        botao.setCursor(Qt.PointingHandCursor)
        botao.setStyleSheet(estilo.estilo_botao(principal=True))
        botao.clicked.connect(self._abrir_seletor_de_arquivo)

        linha_botao = QHBoxLayout()
        linha_botao.addStretch()
        linha_botao.addWidget(botao)
        linha_botao.addStretch()

        layout.addWidget(icone)
        layout.addWidget(chamada)
        layout.addSpacing(estilo.ESPACO_3)
        layout.addWidget(ou)
        layout.addSpacing(estilo.ESPACO_3)
        layout.addLayout(linha_botao)
        return area

    def _montar_escolha_do_motor(self):
        bloco = QWidget()
        layout = QVBoxLayout(bloco)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(estilo.ESPACO_2)

        layout.addWidget(_rotulo_de_secao("MOTOR DE LEITURA"))

        self.motor_tesseract = QRadioButton("Tesseract (nesta máquina)")
        self.motor_tesseract.setChecked(True)
        self.motor_tesseract.setStyleSheet(_estilo_do_radio())

        # A IA local aparece e não funciona de propósito: ela depende de um
        # servidor que a TI da UFSC ainda vai montar. Não existe, neste módulo,
        # nenhuma linha que converse com motor remoto (RN-21).
        self.motor_ia_local = QRadioButton("IA local da UFSC")
        self.motor_ia_local.setEnabled(False)
        self.motor_ia_local.setStyleSheet(_estilo_do_radio(apagado=True))

        explicacao = QLabel(
            "Depende de um servidor que a TI ainda vai montar dentro da rede "
            "da universidade."
        )
        explicacao.setWordWrap(True)
        explicacao.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; margin-left: 22px;"
        )

        layout.addWidget(self.motor_tesseract)
        layout.addWidget(self.motor_ia_local)
        layout.addWidget(explicacao)
        return bloco

    def _montar_tela_conferindo(self):
        tela = QWidget()
        layout = QVBoxLayout(tela)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(estilo.ESPACO_2)

        titulo = _titulo("Conferindo o documento…")
        titulo.setAlignment(Qt.AlignCenter)

        legenda = _legenda(
            "Verificando a quantidade de páginas e a existência de camada de texto.")
        legenda.setAlignment(Qt.AlignCenter)

        barra = QProgressBar()
        barra.setRange(0, 0)  # sem porcentagem: não se sabe quanto falta
        barra.setTextVisible(False)
        barra.setFixedSize(260, 4)
        barra.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: {estilo.COR_BORDA};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {estilo.COR_DESTAQUE};
                border-radius: 2px;
            }}
            """
        )

        linha_barra = QHBoxLayout()
        linha_barra.addStretch()
        linha_barra.addWidget(barra)
        linha_barra.addStretch()

        layout.addWidget(titulo)
        layout.addWidget(legenda)
        layout.addSpacing(estilo.ESPACO_3)
        layout.addLayout(linha_barra)
        return tela

    # ------------------------------------------------------------- escolher

    def _abrir_seletor_de_arquivo(self):
        # A pasta inicial fica em branco de propósito: nada é lembrado entre um
        # uso e outro, nem a última pasta usada (RN-22).
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Escolher documento", "", "Documentos PDF (*.pdf)"
        )
        if caminho:
            self.receber_documento(Path(caminho))

    def receber_documento(self, caminho):
        """Mostra que está trabalhando e então confere o documento.

        A conferência é rápida, mas a tela precisa aparecer antes dela para não
        haver um instante de janela parada sem explicação. Por isso a leitura
        acontece logo depois, quando o Qt já desenhou a tela de espera.
        """
        self.telas.setCurrentWidget(self.tela_conferindo)
        QTimer.singleShot(0, lambda: self._conferir(caminho))

    def _conferir(self, caminho):
        try:
            ficha = conferir(caminho)
        except DocumentoNaoAbre as problema:
            self._mostrar_erro(caminho, str(problema))
            return
        except Exception:
            # Qualquer falha não prevista também precisa terminar numa tela com
            # saída. A tela de espera não tem botão nenhum: sem isto, o painel
            # ficaria preso nela para sempre, e nem sair pelo menu resolveria -
            # quem usa só teria como fechar o programa inteiro.
            self._mostrar_erro(
                caminho,
                "O documento não pôde ser lido até o fim. Ele pode estar "
                "danificado por dentro.",
            )
            return

        self.tela_ficha.mostrar(ficha)
        self.telas.setCurrentWidget(self.tela_ficha)

    def _mostrar_erro(self, caminho, motivo):
        self.tela_erro.mostrar(caminho, motivo)
        self.telas.setCurrentWidget(self.tela_erro)

    def voltar_para_escolher(self):
        self.telas.setCurrentWidget(self.tela_escolher)

    # ------------------------------------------------------ arrastar e soltar

    def dragEnterEvent(self, evento):
        if self._pdf_arrastado(evento):
            evento.acceptProposedAction()

    def dropEvent(self, evento):
        caminho = self._pdf_arrastado(evento)
        if caminho:
            evento.acceptProposedAction()
            self.receber_documento(caminho)

    def _pdf_arrastado(self, evento):
        """Devolve o caminho do PDF arrastado, ou None quando não serve.

        Só um documento por vez: arrastar vários é justamente o caso que a spec
        deixou de fora, e aceitar em silêncio o primeiro da pilha seria pior que
        recusar.
        """
        dados = evento.mimeData()
        if not dados.hasUrls() or len(dados.urls()) != 1:
            return None

        url = dados.urls()[0]
        if not url.isLocalFile():
            return None

        caminho = Path(url.toLocalFile())
        return caminho if caminho.suffix.lower() == ".pdf" else None


class _TelaFicha(QWidget):
    """O que o programa descobriu sobre o documento escolhido."""

    def __init__(self, ao_escolher_outro):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(_titulo("Gerar OCR"))
        layout.addWidget(_legenda("Resultado da verificação do documento."))
        layout.addSpacing(estilo.ESPACO_4)

        self.cartao = QFrame()
        self.cartao.setStyleSheet(
            f"""
            QFrame {{
                background-color: {estilo.COR_FUNDO_ELEVADO};
                border: 1px solid {estilo.COR_BORDA};
                border-radius: {estilo.RAIO}px;
            }}
            """
        )
        cartao_layout = QVBoxLayout(self.cartao)
        cartao_layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_3,
                                         estilo.ESPACO_4, estilo.ESPACO_3)
        cartao_layout.setSpacing(0)

        self.nome_arquivo = QLabel()
        self.nome_arquivo.setWordWrap(True)
        self.nome_arquivo.setStyleSheet(
            f"font-family: {estilo.FONTE_MONO};"
            f"font-size: {estilo.TEXTO_BASE}px; color: {estilo.COR_TEXTO};"
            "border: none;"
        )
        cartao_layout.addWidget(self.nome_arquivo)
        cartao_layout.addSpacing(estilo.ESPACO_3)

        self.linha_paginas = _LinhaDaFicha("Páginas")
        self.linha_texto = _LinhaDaFicha("Camada de texto")
        self.linha_acontece = _LinhaDaFicha("O que vai acontecer")
        for linha in (self.linha_paginas, self.linha_texto, self.linha_acontece):
            cartao_layout.addWidget(linha)

        layout.addWidget(self.cartao)
        layout.addSpacing(estilo.ESPACO_4)

        self.botao_ler = QPushButton("Ler o documento")
        self.botao_ler.setStyleSheet(estilo.estilo_botao(principal=True))
        # Apagado porque a leitura é a etapa seguinte. Botão que parece pronto
        # e não faz nada é lido como programa quebrado.
        self.botao_ler.setEnabled(False)

        botao_outro = QPushButton("Escolher outro documento")
        botao_outro.setCursor(Qt.PointingHandCursor)
        botao_outro.setStyleSheet(estilo.estilo_botao(principal=False))
        botao_outro.clicked.connect(ao_escolher_outro)

        acoes = QHBoxLayout()
        acoes.setSpacing(estilo.ESPACO_3)
        acoes.addWidget(self.botao_ler)
        acoes.addWidget(botao_outro)
        acoes.addStretch()
        layout.addLayout(acoes)

        layout.addSpacing(estilo.ESPACO_3)
        layout.addWidget(_legenda(
            "A leitura do documento entra na próxima etapa do projeto."))
        layout.addStretch()

    def mostrar(self, ficha):
        self.nome_arquivo.setText(ficha.caminho.name)
        self.linha_paginas.definir(str(ficha.paginas))

        if ficha.tem_camada_de_texto:
            letras = _com_separador_de_milhar(ficha.letras_na_camada_de_texto)
            self.linha_texto.definir(
                f"sim, {letras} letras", cor=estilo.COR_SUCESSO
            )
            self.linha_acontece.definir("aguarda sua decisão sobre o texto existente")
            self.botao_ler.setText("Ver o texto e decidir")
        else:
            self.linha_texto.definir("não há", cor=estilo.COR_ALERTA)
            self.linha_acontece.definir("cada página será lida como imagem")
            self.botao_ler.setText(f"Ler as {ficha.paginas} páginas")


class _TelaErro(QWidget):
    """O arquivo que não abre: uma frase, e o caminho de volta."""

    # A caixa e o texto dentro dela têm largura fixa. Sem isso, o Qt calcula a
    # altura da caixa achando que a frase cabe numa linha só, e o fim do texto
    # some para fora da borda - a pessoa lê meia explicação e não tem como
    # saber que faltou pedaço.
    LARGURA_DA_CAIXA = 460
    LARGURA_DO_TEXTO = 400

    def __init__(self, ao_escolher_outro):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        caixa = QFrame()
        caixa.setFixedWidth(self.LARGURA_DA_CAIXA)
        caixa.setStyleSheet(
            f"""
            QFrame {{
                background-color: rgba(217, 83, 79, 26);
                border-left: 4px solid {estilo.COR_ERRO};
                border-radius: {estilo.RAIO}px;
            }}
            """
        )
        caixa_layout = QVBoxLayout(caixa)
        caixa_layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_3,
                                        estilo.ESPACO_4, estilo.ESPACO_3)
        caixa_layout.setSpacing(estilo.ESPACO_2)

        titulo = QLabel("Não foi possível abrir o documento")
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO}; border: none;"
        )

        self.explicacao = QLabel()
        self.explicacao.setWordWrap(True)
        self.explicacao.setFixedWidth(self.LARGURA_DO_TEXTO)
        self.explicacao.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
        )

        caixa_layout.addWidget(titulo)
        caixa_layout.addWidget(self.explicacao)

        botao = QPushButton("Escolher outro documento")
        botao.setCursor(Qt.PointingHandCursor)
        botao.setStyleSheet(estilo.estilo_botao(principal=True))
        botao.clicked.connect(ao_escolher_outro)

        linha_botao = QHBoxLayout()
        linha_botao.addStretch()
        linha_botao.addWidget(botao)
        linha_botao.addStretch()

        layout.addWidget(caixa, alignment=Qt.AlignCenter)
        layout.addSpacing(estilo.ESPACO_4)
        layout.addLayout(linha_botao)

    def mostrar(self, caminho, motivo):
        self.explicacao.setText(f"{caminho.name} — {motivo}")
        # A frase muda de tamanho conforme o problema do arquivo, então a
        # altura de que ela precisa é recalculada a cada vez.
        self.explicacao.setMinimumHeight(
            self.explicacao.heightForWidth(self.LARGURA_DO_TEXTO)
        )


class _LinhaDaFicha(QWidget):
    """Uma linha do cartão: o nome à esquerda, o valor à direita."""

    def __init__(self, chave):
        super().__init__()
        self.setStyleSheet(f"border-top: 1px solid {estilo.COR_BORDA};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, estilo.ESPACO_2, 0, estilo.ESPACO_2)

        rotulo = QLabel(chave)
        rotulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
        )

        self.valor = QLabel()
        self.valor.setAlignment(Qt.AlignRight)

        layout.addWidget(rotulo)
        layout.addStretch()
        layout.addWidget(self.valor)

    def definir(self, texto, cor=None):
        self.valor.setText(texto)
        self.valor.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 600;"
            f"color: {cor or estilo.COR_TEXTO}; border: none;"
        )


def _com_separador_de_milhar(numero):
    """Escreve o número do jeito que se escreve em português: 1.720, não 1720.

    A separação é feita aqui, e não pelo atalho do Python que "usa o formato da
    máquina": esse atalho depende de como o Windows daquela máquina está
    configurado, e numa máquina em inglês o mesmo número sairia com vírgula.
    """
    return f"{numero:,}".replace(",", ".")


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


def _rotulo_de_secao(texto):
    rotulo = QLabel(texto)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 700;"
        f"color: {estilo.COR_TEXTO_SECUNDARIO}; letter-spacing: 1px;"
    )
    return rotulo


def _estilo_do_radio(apagado=False):
    cor = estilo.COR_TEXTO_APAGADO if apagado else estilo.COR_TEXTO
    return f"""
        QRadioButton {{
            color: {cor};
            font-size: {estilo.TEXTO_BASE}px;
            spacing: {estilo.ESPACO_2}px;
        }}
        QRadioButton::indicator {{
            width: 15px;
            height: 15px;
            border-radius: 8px;
            border: 2px solid {estilo.COR_TEXTO_SECUNDARIO};
        }}
        QRadioButton::indicator:checked {{
            border: 2px solid {estilo.COR_DESTAQUE};
            background-color: {estilo.COR_DESTAQUE};
        }}
        QRadioButton::indicator:disabled {{
            border: 2px solid #4a5058;
        }}
    """

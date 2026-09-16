"""O painel do item "Anonimizar": do arquivo escolhido à revisão.

É ele que troca de tela conforme o documento anda: escolher o arquivo, revisar
o texto mascarado, ou explicar o que deu errado. Cada tela é uma peça à parte, e
este arquivo é quem sabe a ordem entre elas - o mesmo arranjo do painel do
"Gerar OCR".

Segue os rascunhos aprovados mockups/anonimizar/08-escolher-e-salvar.html (a
escolha do arquivo) e 01-revisar-antes-de-salvar.html (a revisão e o erro).

Nesta etapa o painel abre `.md` e `.txt`. O caminho do PDF - leitura,
conferência e a escolha do motor - entra numa etapa seguinte, e até lá o PDF
escolhido aqui recebe um aviso dizendo isso.
"""
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import cpf
import estilo
from arquivo_texto import ArquivoNaoServe, ler
from tela_revisao import TelaRevisao

EXTENSOES_DE_TEXTO = (".md", ".txt")
EXTENSOES_ACEITAS = EXTENSOES_DE_TEXTO + (".pdf",)

AINDA_SEM_PDF = (
    "O caminho do PDF, com a leitura e a conferência, entra numa etapa "
    "seguinte. Por enquanto o Anonimizar abre {nome} só se for .md ou .txt."
)

# Word, planilha e imagem não estão a caminho: eles estão fora do escopo da
# spec. Dizer "numa etapa seguinte" para eles seria prometer o que o programa
# nunca vai cumprir - e quem espera não reclama, só some.
OUTRO_TIPO = (
    "O Anonimizar abre PDF, .md e .txt. O {nome} é de outro tipo."
)


class PainelAnonimizar(QWidget):
    def __init__(self):
        super().__init__()
        # Arrastar o arquivo para dentro da janela é uma das duas formas de
        # escolher, como no "Gerar OCR"; a outra é o botão.
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_4,
                                  estilo.ESPACO_5, estilo.ESPACO_5)
        layout.setSpacing(0)

        self.telas = QStackedWidget()
        self.tela_escolher = self._montar_tela_escolher()
        self.tela_revisao = TelaRevisao(ao_anonimizar_outro=self.voltar_para_escolher)
        self.tela_erro = _TelaErro(ao_escolher_outro=self.voltar_para_escolher)
        for tela in (self.tela_escolher, self.tela_revisao, self.tela_erro):
            self.telas.addWidget(tela)

        layout.addWidget(self.telas)

    # ---------------------------------------------------------------- telas

    def _montar_tela_escolher(self):
        tela = QWidget()
        layout = QVBoxLayout(tela)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        titulo = QLabel("Anonimizar")
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_GRANDE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO};"
        )
        legenda = QLabel(
            "Gera um novo arquivo que tarja os três primeiros e dois últimos "
            "dígitos dos CPFs contidos no documento enviado."
        )
        legenda.setWordWrap(True)
        legenda.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )
        layout.addWidget(titulo)
        layout.addWidget(legenda)
        layout.addSpacing(estilo.ESPACO_4)
        layout.addWidget(self._montar_area_de_arrastar())
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

        chamada = QLabel("Arraste o arquivo aqui")
        chamada.setAlignment(Qt.AlignCenter)
        chamada.setStyleSheet(
            f"font-size: {estilo.TEXTO_GRANDE}px; color: {estilo.COR_TEXTO};"
            "border: none;"
        )

        tipos = QLabel("PDF, .md ou .txt")
        tipos.setAlignment(Qt.AlignCenter)
        tipos.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
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
        layout.addWidget(tipos)
        layout.addSpacing(estilo.ESPACO_3)
        layout.addWidget(ou)
        layout.addSpacing(estilo.ESPACO_3)
        layout.addLayout(linha_botao)
        return area

    # ------------------------------------------------------------- escolher

    def _abrir_seletor_de_arquivo(self):
        # A pasta inicial fica em branco de propósito: nada é lembrado entre um
        # uso e outro, nem a última pasta usada (regra RN-19).
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Escolher arquivo", "",
            "Documentos (*.pdf *.md *.txt)",
        )
        if caminho:
            self.receber_arquivo(Path(caminho))

    def receber_arquivo(self, caminho):
        """Abre o arquivo escolhido e leva o texto dele para a revisão."""
        if caminho.suffix.lower() not in EXTENSOES_DE_TEXTO:
            aviso = (AINDA_SEM_PDF if caminho.suffix.lower() == ".pdf"
                     else OUTRO_TIPO)
            self._mostrar_erro(aviso.format(nome=caminho.name))
            return
        try:
            texto = ler(caminho)
        except ArquivoNaoServe as problema:
            self._mostrar_erro(str(problema))
            return
        except OSError:
            # O arquivo sumiu, ou está numa pasta de rede que caiu, entre a
            # escolha e a leitura. Sem isto o painel ficaria numa tela sem saída.
            self._mostrar_erro(
                f"O arquivo {caminho.name} não pôde ser aberto. Ele pode ter "
                "sido movido, ou estar numa pasta que saiu do ar."
            )
            return

        self.tela_revisao.mostrar(caminho.name, texto, cpf.procurar(texto))
        self.telas.setCurrentWidget(self.tela_revisao)

    def voltar_para_escolher(self):
        self.tela_revisao.esquecer()
        self.telas.setCurrentWidget(self.tela_escolher)

    def _mostrar_erro(self, motivo):
        self.tela_erro.mostrar(motivo)
        self.telas.setCurrentWidget(self.tela_erro)

    # ------------------------------------------------------ arrastar e soltar

    def dragEnterEvent(self, evento):
        if self._arquivo_arrastado(evento):
            evento.acceptProposedAction()

    def dropEvent(self, evento):
        caminho = self._arquivo_arrastado(evento)
        if caminho:
            evento.acceptProposedAction()
            self.receber_arquivo(caminho)

    def _arquivo_arrastado(self, evento):
        """Devolve o caminho do arquivo arrastado, ou None quando não serve.

        Só um arquivo por vez: vários de uma vez é justamente o caso que a spec
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
        return caminho if caminho.suffix.lower() in EXTENSOES_ACEITAS else None


class _TelaErro(QWidget):
    """O arquivo que não serve: uma frase, e o caminho de volta.

    É o mesmo desenho do erro aprovado no "Gerar OCR". A caixa e o texto têm
    largura fixa, e a altura é calculada a partir dela a cada frase: sem isso o
    Qt reserva a altura de uma linha só e o fim da explicação some para fora da
    borda, sem nenhum sinal de que faltou pedaço.
    """

    LARGURA_DA_CAIXA = 460
    LARGURA_DO_TEXTO = 400

    def __init__(self, ao_escolher_outro):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        caixa = QFrame()
        caixa.setObjectName("caixa_de_erro")
        caixa.setFixedWidth(self.LARGURA_DA_CAIXA)
        caixa.setStyleSheet(
            f"""
            QFrame#caixa_de_erro {{
                background-color: rgba(217, 83, 79, 26);
                border-left: 4px solid {estilo.COR_ERRO};
                border-radius: {estilo.RAIO}px;
            }}
            """
        )
        dentro = QVBoxLayout(caixa)
        dentro.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_3,
                                  estilo.ESPACO_4, estilo.ESPACO_3)
        dentro.setSpacing(estilo.ESPACO_2)

        titulo = QLabel("Não foi possível usar este arquivo")
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO}; border: none; background: transparent;"
        )
        self.explicacao = QLabel()
        self.explicacao.setWordWrap(True)
        self.explicacao.setFixedWidth(self.LARGURA_DO_TEXTO)
        self.explicacao.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
            "border: none; background: transparent;"
        )
        dentro.addWidget(titulo)
        dentro.addWidget(self.explicacao)

        botao = QPushButton("Escolher outro arquivo")
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

    def mostrar(self, motivo):
        self.explicacao.setText(motivo)
        self.explicacao.setMinimumHeight(
            self.explicacao.heightForWidth(self.LARGURA_DO_TEXTO)
        )

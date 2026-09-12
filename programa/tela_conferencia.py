"""A tela de conferência: o documento de um lado, o texto do outro.

É a peça central do módulo. Sem ver o original ao lado, "conferir o texto" vira
um "ok" que ninguém dá de verdade - e aí o arquivo sai com erro de leitura que
ninguém viu.

Segue o rascunho aprovado mockups/ocr/06-conferir-o-texto.html: uma página por
vez, com setas. As duas metades mostram sempre a mesma página, e é isso que a
regra RN-9 da spec pede.
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import estilo
from leitura import imagem_da_pagina

# De onde veio o texto que está sendo conferido. Muda só o selo da tela, mas
# muda o que a pessoa precisa olhar: texto adivinhado de uma imagem erra bem
# mais que texto que já estava gravado dentro do PDF.
ORIGEM_OCR = "ocr"
ORIGEM_CAMADA_DO_PDF = "camada"

# Os limites dos controles de tamanho, da regra RN-23 e RN-24 da spec 002.
# 100% é o tamanho em que a página cabe na largura da metade; 400% é o ponto em
# que já dá para ler letra por letra num documento escaneado ruim.
ZOOM_MINIMO = 0.5
ZOOM_MAXIMO = 4.0
PASSO_DO_ZOOM = 0.25

FONTE_MINIMA = 10
FONTE_MAXIMA = 22
FONTE_PADRAO = 12

# Largura que a barra de rolagem lateral e as bordas ocupam. O tamanho "que cabe
# na largura" é calculado descontando isto, e não medindo a área visível: ao
# aumentar a página a barra aparece, a área visível encolhe, e medir dali faria
# a conta mudar sozinha a cada desenho.
LARGURA_RESERVADA = 30

# Quanto o programa espera, depois da última mudança de tamanho da janela, para
# redesenhar a página. Curto o bastante para parecer imediato quando a pessoa
# solta a borda, e longo o bastante para não redesenhar no meio do arrasto.
ESPERA_ANTES_DE_REDESENHAR = 150


class TelaConferencia(QWidget):
    def __init__(self, ao_processar_outro, ao_conferir=None):
        super().__init__()
        self._paginas = []
        self._paginas_originais = []
        self._pagina_atual = 0
        self._caminho = None
        # Qual página está de fato dentro do editor agora. Fica sem nada até a
        # primeira ser carregada: sem isso, o editor vazio do começo seria
        # gravado por cima do texto da página 1 e apagaria a leitura dela.
        self._pagina_no_editor = None
        # 1.0 é a página cabendo na largura da metade. O tamanho escolhido vale
        # para as páginas seguintes do mesmo documento (RN-23): quem aumentou
        # para conseguir ler não quer reajustar a cada virada de página.
        self._zoom = 1.0
        self._tamanho_da_fonte = FONTE_PADRAO

        # O relógio que segura o redesenho até a janela parar de mudar de
        # tamanho. Sozinho (singleShot) porque cada mudança reinicia a contagem.
        self._espera_para_redesenhar = QTimer(self)
        self._espera_para_redesenhar.setSingleShot(True)
        self._espera_para_redesenhar.timeout.connect(self._redesenhar_agora)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addLayout(self._montar_cabecalho())
        self.faixa_do_erro = QLabel()
        self.faixa_do_erro.setWordWrap(True)
        self.faixa_do_erro.setVisible(False)
        self.faixa_do_erro.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO};"
            f"border-left: 3px solid {estilo.COR_ERRO};"
            "background-color: rgba(217, 83, 79, 26);"
            f"border-radius: {estilo.RAIO}px;"
            f"padding: {estilo.ESPACO_2}px {estilo.ESPACO_3}px;"
            f"margin-top: {estilo.ESPACO_2}px;"
        )
        layout.addWidget(self.faixa_do_erro)
        self.legenda = QLabel()
        self.legenda.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )
        layout.addWidget(self.legenda)
        layout.addSpacing(estilo.ESPACO_3)

        layout.addLayout(self._montar_navegacao())
        layout.addSpacing(estilo.ESPACO_2)
        layout.addLayout(self._montar_metades(), stretch=1)
        layout.addSpacing(estilo.ESPACO_3)
        layout.addLayout(self._montar_rodape(ao_processar_outro, ao_conferir))

    # ------------------------------------------------------------- montagem

    def _montar_cabecalho(self):
        linha = QHBoxLayout()
        linha.setSpacing(estilo.ESPACO_3)

        titulo = QLabel("Conferir o texto")
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_GRANDE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO};"
        )

        self.selo = QLabel()
        self.selo.setAlignment(Qt.AlignCenter)

        linha.addWidget(titulo)
        linha.addWidget(self.selo)
        linha.addStretch()
        return linha

    def _montar_navegacao(self):
        linha = QHBoxLayout()
        linha.setSpacing(estilo.ESPACO_2)

        self.botao_anterior = _seta("◀ anterior")
        self.botao_anterior.clicked.connect(lambda: self.ir_para(self._pagina_atual - 1))

        self.rotulo_pagina = QLabel()
        self.rotulo_pagina.setMinimumWidth(120)
        self.rotulo_pagina.setAlignment(Qt.AlignCenter)
        self.rotulo_pagina.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; color: {estilo.COR_TEXTO};"
        )

        self.botao_proxima = _seta("próxima ▶")
        self.botao_proxima.clicked.connect(lambda: self.ir_para(self._pagina_atual + 1))

        self.contagem_de_correcoes = QLabel()
        self.contagem_de_correcoes.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )

        linha.addWidget(self.botao_anterior)
        linha.addWidget(self.rotulo_pagina)
        linha.addWidget(self.botao_proxima)
        linha.addStretch()
        linha.addWidget(self.contagem_de_correcoes)
        return linha

    def _montar_metades(self):
        linha = QHBoxLayout()
        linha.setSpacing(estilo.ESPACO_3)

        # --- o documento original, à esquerda
        esquerda = QVBoxLayout()
        esquerda.setSpacing(estilo.ESPACO_1)

        cabecalho_esquerdo = QHBoxLayout()
        cabecalho_esquerdo.setSpacing(estilo.ESPACO_1)
        cabecalho_esquerdo.addWidget(_titulo_da_metade("O DOCUMENTO ORIGINAL"))
        cabecalho_esquerdo.addStretch()
        self.botao_menos_zoom = _botao_pequeno("−", "diminuir a página")
        self.botao_menos_zoom.clicked.connect(lambda: self.mudar_zoom(-PASSO_DO_ZOOM))
        self.rotulo_zoom = QLabel()
        self.rotulo_zoom.setMinimumWidth(44)
        self.rotulo_zoom.setAlignment(Qt.AlignCenter)
        self.rotulo_zoom.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )
        self.botao_mais_zoom = _botao_pequeno("+", "aumentar a página")
        self.botao_mais_zoom.clicked.connect(lambda: self.mudar_zoom(PASSO_DO_ZOOM))
        self.botao_ajustar = _botao_pequeno("ajustar", "voltar ao tamanho que cabe na largura")
        self.botao_ajustar.clicked.connect(self.ajustar_a_largura)
        for peca in (self.botao_menos_zoom, self.rotulo_zoom,
                     self.botao_mais_zoom, self.botao_ajustar):
            cabecalho_esquerdo.addWidget(peca)
        esquerda.addLayout(cabecalho_esquerdo)

        self.imagem = QLabel()
        self.imagem.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.rolagem_do_pdf = QScrollArea()
        self.rolagem_do_pdf.setWidget(self.imagem)
        self.rolagem_do_pdf.setWidgetResizable(True)
        self.rolagem_do_pdf.setStyleSheet(
            f"""
            QScrollArea {{
                background-color: #0f1216;
                border: 1px solid {estilo.COR_BORDA};
                border-radius: {estilo.RAIO}px;
            }}
            """
        )
        esquerda.addWidget(self.rolagem_do_pdf)

        # --- o texto lido, à direita
        direita = QVBoxLayout()
        direita.setSpacing(estilo.ESPACO_1)

        cabecalho_direito = QHBoxLayout()
        cabecalho_direito.setSpacing(estilo.ESPACO_1)
        cabecalho_direito.addWidget(_titulo_da_metade("O TEXTO LIDO — DÁ PARA CORRIGIR AQUI"))
        cabecalho_direito.addStretch()
        self.botao_menos_fonte = _botao_pequeno("−", "diminuir a letra")
        self.botao_menos_fonte.clicked.connect(lambda: self.mudar_fonte(-1))
        self.rotulo_fonte = QLabel()
        self.rotulo_fonte.setMinimumWidth(44)
        self.rotulo_fonte.setAlignment(Qt.AlignCenter)
        self.rotulo_fonte.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )
        self.botao_mais_fonte = _botao_pequeno("+", "aumentar a letra")
        self.botao_mais_fonte.clicked.connect(lambda: self.mudar_fonte(1))
        for peca in (self.botao_menos_fonte, self.rotulo_fonte, self.botao_mais_fonte):
            cabecalho_direito.addWidget(peca)
        direita.addLayout(cabecalho_direito)

        self.editor = QPlainTextEdit()
        self.editor.textChanged.connect(self._texto_mudou)
        direita.addWidget(self.editor)

        linha.addLayout(esquerda)
        linha.addLayout(direita)
        return linha

    def _montar_rodape(self, ao_processar_outro, ao_conferir):
        linha = QHBoxLayout()
        linha.setSpacing(estilo.ESPACO_3)

        self.botao_conferido = QPushButton("Conferido")
        self.botao_conferido.setCursor(Qt.PointingHandCursor)
        self.botao_conferido.setStyleSheet(estilo.estilo_botao(principal=True))
        if ao_conferir is not None:
            self.botao_conferido.clicked.connect(ao_conferir)
        else:
            # Sem ninguém esperando o texto conferido, o botão não teria para
            # onde levar - e botão que parece pronto e não faz nada é lido
            # como defeito.
            self.botao_conferido.setEnabled(False)

        botao_outro = QPushButton("Processar outro documento")
        botao_outro.setCursor(Qt.PointingHandCursor)
        botao_outro.setStyleSheet(estilo.estilo_botao(principal=False))
        botao_outro.clicked.connect(ao_processar_outro)

        aviso = QLabel("Nada é gravado até você escolher salvar.")
        aviso.setWordWrap(True)
        aviso.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )

        linha.addWidget(self.botao_conferido)
        linha.addWidget(botao_outro)
        linha.addWidget(aviso, stretch=1)
        return linha

    # ---------------------------------------------------------------- uso

    def mostrar(self, ficha, paginas, origem=ORIGEM_OCR):
        self._caminho = ficha.caminho
        self._paginas = list(paginas)
        # A cópia do texto como ele saiu da leitura é o que permite saber, mais
        # tarde, em quais páginas a pessoa mexeu.
        self._paginas_originais = list(paginas)
        self._pagina_atual = 0
        # Documento novo: o que estava no editor era do documento anterior, e
        # não pode ser gravado por cima deste.
        self._pagina_no_editor = None

        self.legenda.setText(
            f"{ficha.caminho.name} — compare com o original à esquerda e "
            "corrija o que estiver errado."
        )
        self._definir_selo(origem)
        # Documento novo começa no tamanho padrão: nada é lembrado entre um uso
        # e outro (RN-22), e o que valia para o documento anterior não tem por
        # que valer para este.
        self._zoom = 1.0
        self._tamanho_da_fonte = FONTE_PADRAO
        self._aplicar_zoom()
        self._aplicar_fonte()
        self.ir_para(0)

    def ir_para(self, indice):
        """Leva as duas metades para a mesma página (regra RN-9).

        A troca acontece inteira ou não acontece. Não conseguindo desenhar a
        página - o documento foi movido, apagado, ou a pasta de rede caiu -, a
        tela fica onde estava e avisa. Deixar o texto avançar sem a imagem faria
        a pessoa comparar o texto de uma página com a imagem de outra, sem nada
        indicando isso: a conferência passaria a não conferir nada.
        """
        if not self._paginas:
            return
        indice = max(0, min(indice, len(self._paginas) - 1))

        try:
            imagem = self._desenhar(indice)
        except Exception:
            self._avisar_que_a_pagina_nao_abriu()
            return

        self._guardar_o_que_foi_digitado()
        self._pagina_atual = indice

        # O editor é preenchido sem contar como alteração da pessoa.
        self.editor.blockSignals(True)
        self.editor.setPlainText(self._paginas[indice])
        self.editor.blockSignals(False)
        self._pagina_no_editor = indice

        self._mostrar(imagem)
        self.faixa_do_erro.setVisible(False)
        self._atualizar_navegacao()

    def esquecer(self):
        """Solta o documento ao sair da tela.

        Sem isto, a tela continuaria guardando o documento anterior e
        redesenhando a página dele a cada mexida na janela - trabalho sobre uma
        coisa que ninguém está olhando.
        """
        self._paginas = []
        self._paginas_originais = []
        self._pagina_no_editor = None
        self._caminho = None
        self.imagem.clear()
        self.editor.blockSignals(True)
        self.editor.setPlainText("")
        self.editor.blockSignals(False)

    def texto_conferido(self):
        """O texto de cada página, já com as correções feitas na tela.

        É este que segue para o arquivo ou para o Anonimizar - nunca o que saiu
        da leitura (regra RN-13).
        """
        self._guardar_o_que_foi_digitado()
        return list(self._paginas)

    def paginas_corrigidas(self):
        """Quantas páginas a pessoa mexeu."""
        self._guardar_o_que_foi_digitado()
        return sum(
            1
            for agora, antes in zip(self._paginas, self._paginas_originais)
            if agora != antes
        )

    # ------------------------------------------------------------- por dentro

    def _guardar_o_que_foi_digitado(self):
        """Grava o que está no editor na página a que ele pertence.

        Só grava quando há uma página carregada ali: o editor vazio de antes da
        primeira carga apagaria o texto lido da página 1.
        """
        if self._pagina_no_editor is not None:
            self._paginas[self._pagina_no_editor] = self.editor.toPlainText()

    def _texto_mudou(self):
        self._guardar_o_que_foi_digitado()
        self._atualizar_contagem()

    def mudar_zoom(self, passo):
        """Aumenta ou diminui a página, dentro dos limites da regra RN-23."""
        self._zoom = min(max(self._zoom + passo, ZOOM_MINIMO), ZOOM_MAXIMO)
        self._aplicar_zoom()

    def ajustar_a_largura(self):
        """Volta a página ao tamanho em que ela cabe na largura da metade."""
        self._zoom = 1.0
        self._aplicar_zoom()

    def mudar_fonte(self, passo):
        """Aumenta ou diminui a letra do texto, dentro dos limites da RN-24.

        Mexe só em como o texto aparece: o conteúdo não muda, e nada disso vai
        para o arquivo salvo.
        """
        self._tamanho_da_fonte = min(
            max(self._tamanho_da_fonte + passo, FONTE_MINIMA), FONTE_MAXIMA
        )
        self._aplicar_fonte()

    def _aplicar_zoom(self):
        if self._paginas:
            self._mostrar_imagem(self._pagina_atual)
        self.rotulo_zoom.setText(f"{round(self._zoom * 100)}%")
        self.botao_menos_zoom.setEnabled(self._zoom > ZOOM_MINIMO)
        self.botao_mais_zoom.setEnabled(self._zoom < ZOOM_MAXIMO)
        self.botao_ajustar.setEnabled(self._zoom != 1.0)

    def _aplicar_fonte(self):
        self.editor.setStyleSheet(
            f"""
            QPlainTextEdit {{
                background-color: {estilo.COR_FUNDO_ELEVADO};
                border: 1px solid {estilo.COR_DESTAQUE};
                border-radius: {estilo.RAIO}px;
                padding: {estilo.ESPACO_3}px;
                font-family: {estilo.FONTE_MONO};
                font-size: {self._tamanho_da_fonte}px;
                color: {estilo.COR_TEXTO};
            }}
            """
        )
        self.rotulo_fonte.setText(f"{self._tamanho_da_fonte} px")
        self.botao_menos_fonte.setEnabled(self._tamanho_da_fonte > FONTE_MINIMA)
        self.botao_mais_fonte.setEnabled(self._tamanho_da_fonte < FONTE_MAXIMA)

    def _largura_que_cabe(self):
        return max(self.rolagem_do_pdf.width() - LARGURA_RESERVADA, 200)

    def _largura_alvo(self):
        return int(self._largura_que_cabe() * self._zoom)

    def _desenhar(self, indice):
        """Pede a página já no tamanho em que ela vai aparecer."""
        largura = self._largura_alvo()
        imagem = QPixmap()
        imagem.loadFromData(imagem_da_pagina(self._caminho, indice, largura))
        # O acerto fino de largura mantém a proporção da página - documento
        # deformado atrapalha justamente quem está comparando letra por letra.
        return imagem.scaledToWidth(largura, Qt.SmoothTransformation)

    def _mostrar(self, imagem):
        self.imagem.setPixmap(imagem)
        # Sem isto a etiqueta seria espremida na largura da área visível e a
        # barra de rolagem lateral nunca apareceria: a página aumentada ficaria
        # cortada, sem jeito de chegar no lado direito dela.
        self.imagem.setMinimumWidth(imagem.width())

    def _mostrar_imagem(self, indice):
        """Redesenha a página atual, avisando quando o documento não abre."""
        try:
            self._mostrar(self._desenhar(indice))
        except Exception:
            self._avisar_que_a_pagina_nao_abriu()
            return
        self.faixa_do_erro.setVisible(False)

    def _redesenhar_agora(self):
        if self._paginas:
            self._mostrar_imagem(self._pagina_atual)

    def _avisar_que_a_pagina_nao_abriu(self):
        self.faixa_do_erro.setText(
            "Não foi possível abrir o documento para mostrar esta página. Ele "
            "pode ter sido movido, apagado, ou estar numa pasta que saiu do ar. "
            "O texto já lido continua aqui e não se perdeu."
        )
        self.faixa_do_erro.setVisible(True)

    def _atualizar_navegacao(self):
        total = len(self._paginas)
        self.rotulo_pagina.setText(f"Página {self._pagina_atual + 1} de {total}")
        self.botao_anterior.setEnabled(self._pagina_atual > 0)
        self.botao_proxima.setEnabled(self._pagina_atual < total - 1)
        self._atualizar_contagem()

    def _atualizar_contagem(self):
        quantas = sum(
            1
            for agora, antes in zip(self._paginas, self._paginas_originais)
            if agora != antes
        )
        if quantas == 0:
            self.contagem_de_correcoes.setText("")
        elif quantas == 1:
            self.contagem_de_correcoes.setText("1 página com correção sua")
        else:
            self.contagem_de_correcoes.setText(f"{quantas} páginas com correção sua")

    def _definir_selo(self, origem):
        if origem == ORIGEM_CAMADA_DO_PDF:
            texto, cor, fundo = "VEIO DO PRÓPRIO PDF", "#7fb1e8", "rgba(59, 110, 165, 51)"
        else:
            texto, cor, fundo = "VEIO DO OCR", estilo.COR_ALERTA, "rgba(217, 164, 65, 38)"

        self.selo.setText(texto)
        self.selo.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 700;"
            f"color: {cor}; background-color: {fundo};"
            "border-radius: 10px; padding: 3px 10px;"
        )

    def resizeEvent(self, evento):
        """Redesenha a página depois que a janela para de mudar de tamanho.

        Sem redesenhar, a imagem ficaria no tamanho de antes e sairia pequena
        demais depois de a pessoa maximizar. Mas redesenhar a cada pixel do
        arrasto trava a janela: arrastar a borda por um segundo dispara umas
        sessenta mudanças de tamanho, e cada desenho custa dezenas de milésimos
        de segundo. Então o desenho espera a pessoa parar de arrastar.
        """
        super().resizeEvent(evento)
        if self._paginas:
            self._espera_para_redesenhar.start(ESPERA_ANTES_DE_REDESENHAR)


def _seta(texto):
    botao = QPushButton(texto)
    botao.setCursor(Qt.PointingHandCursor)
    botao.setStyleSheet(
        f"""
        QPushButton {{
            background-color: {estilo.COR_FUNDO_ELEVADO};
            border: 1px solid {estilo.COR_BORDA};
            color: {estilo.COR_TEXTO};
            border-radius: {estilo.RAIO}px;
            padding: 4px 12px;
            font-size: {estilo.TEXTO_PEQUENO}px;
        }}
        QPushButton:hover {{ border-color: {estilo.COR_DESTAQUE}; }}
        QPushButton:disabled {{ color: #565d66; }}
        """
    )
    return botao


def _botao_pequeno(texto, explicacao):
    botao = QPushButton(texto)
    botao.setCursor(Qt.PointingHandCursor)
    # A explicação aparece ao parar o mouse em cima: os botões são pequenos e
    # "−" sozinho não diz do que ele é o menos.
    botao.setToolTip(explicacao)
    botao.setStyleSheet(
        f"""
        QPushButton {{
            background-color: {estilo.COR_FUNDO_ELEVADO};
            border: 1px solid {estilo.COR_BORDA};
            color: {estilo.COR_TEXTO};
            border-radius: {estilo.RAIO}px;
            padding: 2px 9px;
            font-size: {estilo.TEXTO_PEQUENO}px;
        }}
        QPushButton:hover {{ border-color: {estilo.COR_DESTAQUE}; }}
        QPushButton:disabled {{ color: #565d66; }}
        """
    )
    return botao


def _titulo_da_metade(texto):
    rotulo = QLabel(texto)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 700;"
        f"color: {estilo.COR_TEXTO_SECUNDARIO}; letter-spacing: 1px;"
    )
    return rotulo

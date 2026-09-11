"""O painel do item "Gerar OCR": o percurso do documento, da escolha à conferência.

É ele que troca de tela conforme o documento anda: escolher, conferir o
arquivo, ler, conferir o texto, ou explicar o que deu errado. Cada tela é uma
peça à parte, e este arquivo é quem sabe a ordem entre elas.

Segue os rascunhos aprovados mockups/ocr/03-escolher-o-documento.html (a
escolha), 04-lendo-o-documento.html (a leitura) e 06-conferir-o-texto.html (a
conferência).
"""
import time
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
from leitura_em_segundo_plano import LeituraEmSegundoPlano
from tela_conferencia import TelaConferencia


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

        # Enquanto a leitura roda, é esta peça que segura o trabalho acontecendo
        # ao lado da janela. Fica guardada para poder ser cancelada.
        self.leitura = None
        # O documento em uso agora. É o que permite tentar de novo depois de
        # uma falha, sem a pessoa ter que escolher o arquivo outra vez.
        self.ficha_atual = None

        self.telas = QStackedWidget()
        self.tela_escolher = self._montar_tela_escolher()
        self.tela_conferindo = self._montar_tela_conferindo()
        self.tela_ficha = _TelaFicha(
            ao_escolher_outro=self.voltar_para_escolher, ao_ler=self.comecar_a_ler
        )
        self.tela_lendo = _TelaLendo(ao_cancelar=self.cancelar_leitura)
        self.tela_conferencia = TelaConferencia(
            ao_processar_outro=self.voltar_para_escolher
        )
        self.tela_erro = _TelaErro(
            ao_escolher_outro=self.voltar_para_escolher,
            ao_tentar_de_novo=self.tentar_ler_de_novo,
        )

        for tela in (self.tela_escolher, self.tela_conferindo, self.tela_ficha,
                     self.tela_lendo, self.tela_conferencia, self.tela_erro):
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

        # A faixa só aparece quando há o que contar - hoje, quando a pessoa
        # cancela uma leitura. Voltar calada faria quem clicou sem querer não
        # descobrir o que aconteceu.
        self.faixa_do_topo = _FaixaDoTopo()
        layout.addWidget(self.faixa_do_topo)

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

    # ---------------------------------------------------------------- ler

    def comecar_a_ler(self, ficha):
        """Manda a leitura acontecer ao lado, e passa a mostrar o andamento."""
        self.tela_lendo.comecar(ficha)
        self.telas.setCurrentWidget(self.tela_lendo)

        # Cada aviso carrega quem o mandou. Leitura abandonada - porque a pessoa
        # escolheu outro documento no meio - continua terminando o que estava
        # fazendo, e o aviso dela chega depois; sem esta marca, ele sequestraria
        # a tela e mostraria a conferência de um documento que ninguém pediu.
        leitura = LeituraEmSegundoPlano(ficha.caminho)
        self.leitura = leitura
        leitura.avancou.connect(
            lambda pagina, total: self._leitura_avancou(leitura, pagina, total))
        leitura.terminou.connect(
            lambda paginas: self._leitura_terminou(leitura, ficha, paginas))
        leitura.cancelou.connect(
            lambda pagina: self._leitura_cancelada(leitura, pagina))
        leitura.falhou.connect(
            lambda pagina, motivo: self._leitura_falhou(leitura, pagina, motivo))
        leitura.start()

    def tentar_ler_de_novo(self):
        """Refaz a leitura do mesmo documento, depois de uma falha."""
        if self.ficha_atual is not None:
            self.comecar_a_ler(self.ficha_atual)

    def cancelar_leitura(self):
        if self.leitura is not None:
            self.tela_lendo.mostrar_que_esta_parando()
            self.leitura.cancelar()

    def encerrar(self):
        """Para a leitura antes de o programa fechar.

        Fechar a janela no meio de uma leitura fazia o programa estourar em vez
        de fechar limpo - e quem vê a caixa de erro do Windows fica sem saber se
        o documento foi mexido. A espera é de no máximo uma página, porque é só
        isso que falta terminar.

        O limite de vinte segundos existe para o programa nunca ficar preso
        fechando: uma página leva perto de um segundo e meio, então vinte
        segundos só acontecem se alguma coisa estiver muito errada - e aí fechar
        assim mesmo é melhor que não fechar.
        """
        self.abandonar_leitura()

    def abandonar_leitura(self):
        """Para a leitura em andamento e a esquece.

        Usado quando a pessoa escolhe outro documento no meio da leitura, e ao
        fechar o programa. Sem isto, três coisas davam errado de uma vez: a
        máquina seguia trabalhando num documento abandonado; o aviso de leitura
        terminada chegava depois e levava a tela para a conferência do documento
        antigo; e começar uma leitura nova por cima da velha derrubava o
        programa.
        """
        if self.leitura is not None and self.leitura.isRunning():
            self.leitura.cancelar()
            self.leitura.wait(20_000)
        self.leitura = None

    def _e_a_leitura_de_agora(self, leitura):
        """Diz se o aviso veio da leitura que a tela está esperando."""
        return leitura is self.leitura

    def _leitura_avancou(self, leitura, pagina, total):
        if self._e_a_leitura_de_agora(leitura):
            self.tela_lendo.avancar(pagina, total)

    def _leitura_terminou(self, leitura, ficha, paginas):
        if not self._e_a_leitura_de_agora(leitura):
            return
        self.tela_conferencia.mostrar(ficha, paginas)
        self.telas.setCurrentWidget(self.tela_conferencia)
        self.leitura = None

    def _leitura_cancelada(self, leitura, pagina):
        if not self._e_a_leitura_de_agora(leitura):
            return
        self.faixa_do_topo.mostrar(
            f"Leitura cancelada na página {pagina}. Nada foi gravado, e o "
            "documento original não foi tocado."
        )
        self.voltar_para_escolher()
        self.leitura = None

    def _leitura_falhou(self, leitura, pagina, motivo):
        if not self._e_a_leitura_de_agora(leitura):
            return
        if pagina:
            titulo = f"A leitura parou na página {pagina}"
            # Falhar numa página pode ser passageiro, e tentar de novo resolve.
            pode_tentar = True
        else:
            titulo = "A leitura não pôde ser feita"
            # Falta de motor de leitura não é passageiro: só instalando resolve.
            # Oferecer "tentar de novo" aqui é oferecer uma saída falsa, que vai
            # falhar igual e esconder a causa real.
            pode_tentar = False

        self.tela_erro.mostrar_falha(titulo, motivo, pode_tentar_de_novo=pode_tentar)
        self.telas.setCurrentWidget(self.tela_erro)
        self.leitura = None

    def receber_documento(self, caminho):
        """Mostra que está trabalhando e então confere o documento.

        A conferência é rápida, mas a tela precisa aparecer antes dela para não
        haver um instante de janela parada sem explicação. Por isso a leitura
        acontece logo depois, quando o Qt já desenhou a tela de espera.
        """
        # Escolher outro documento no meio de uma leitura para a leitura antiga:
        # ela seguiria gastando a maquina num documento que ninguem quer mais.
        self.abandonar_leitura()
        self.faixa_do_topo.esconder()
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

        self.ficha_atual = ficha
        self.tela_ficha.mostrar(ficha)
        self.telas.setCurrentWidget(self.tela_ficha)

    def _mostrar_erro(self, caminho, motivo):
        self.tela_erro.mostrar(caminho, motivo)
        self.telas.setCurrentWidget(self.tela_erro)

    def voltar_para_escolher(self):
        self.tela_conferencia.esquecer()
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

    def __init__(self, ao_escolher_outro, ao_ler):
        super().__init__()
        self._ao_ler = ao_ler
        self._ficha = None

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
        self.botao_ler.setCursor(Qt.PointingHandCursor)
        self.botao_ler.setStyleSheet(estilo.estilo_botao(principal=True))
        self.botao_ler.clicked.connect(self._pedir_leitura)

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
        self.aviso_da_proxima_etapa = _legenda(
            "A decisão sobre o texto que já existe no documento entra na "
            "próxima etapa do projeto."
        )
        layout.addWidget(self.aviso_da_proxima_etapa)
        layout.addStretch()

    def _pedir_leitura(self):
        if self._ficha is not None:
            self._ao_ler(self._ficha)

    def mostrar(self, ficha):
        self._ficha = ficha
        self.nome_arquivo.setText(ficha.caminho.name)
        self.linha_paginas.definir(str(ficha.paginas))

        # Documento que já tem texto por dentro leva a uma tela de decisão que
        # ainda não existe - ela é a etapa 4. Até lá o botão fica apagado, com
        # a explicação embaixo.
        self.botao_ler.setEnabled(not ficha.tem_camada_de_texto)
        self.aviso_da_proxima_etapa.setVisible(ficha.tem_camada_de_texto)

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


class _TelaLendo(QWidget):
    """O andamento da leitura: onde está, quanto falta, e como parar."""

    def __init__(self, ao_cancelar):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        miolo = QWidget()
        miolo.setFixedWidth(420)
        miolo_layout = QVBoxLayout(miolo)
        miolo_layout.setContentsMargins(0, 0, 0, 0)
        miolo_layout.setSpacing(0)

        self.nome_arquivo = QLabel()
        self.nome_arquivo.setStyleSheet(
            f"font-family: {estilo.FONTE_MONO};"
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )

        self.contagem = QLabel()
        self.contagem.setStyleSheet(
            f"font-size: {estilo.TEXTO_GRANDE}px; color: {estilo.COR_TEXTO};"
        )

        self.restante = QLabel()
        self.restante.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )

        self.barra = QProgressBar()
        self.barra.setTextVisible(False)
        self.barra.setFixedHeight(6)
        self.barra.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: {estilo.COR_BORDA};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {estilo.COR_DESTAQUE};
                border-radius: 3px;
            }}
            """
        )

        self.botao_cancelar = QPushButton("Cancelar a leitura")
        self.botao_cancelar.setCursor(Qt.PointingHandCursor)
        self.botao_cancelar.setStyleSheet(estilo.estilo_botao(principal=False))
        self.botao_cancelar.clicked.connect(ao_cancelar)

        miolo_layout.addWidget(self.nome_arquivo)
        miolo_layout.addSpacing(estilo.ESPACO_3)
        miolo_layout.addWidget(self.contagem)
        miolo_layout.addWidget(self.restante)
        miolo_layout.addSpacing(estilo.ESPACO_3)
        miolo_layout.addWidget(self.barra)
        miolo_layout.addSpacing(estilo.ESPACO_4)
        miolo_layout.addWidget(self.botao_cancelar, alignment=Qt.AlignLeft)

        layout.addWidget(miolo)

    def comecar(self, ficha):
        self.nome_arquivo.setText(ficha.caminho.name)
        self.contagem.setText("Preparando a leitura…")
        self.restante.setText("")
        self.barra.setRange(0, ficha.paginas)
        self.barra.setValue(0)
        self.botao_cancelar.setEnabled(True)
        self.botao_cancelar.setText("Cancelar a leitura")
        # O relógio começa na primeira página, e é dele que sai a estimativa.
        self._comeco = time.monotonic()

    def avancar(self, pagina, total):
        self.contagem.setText(f"Lendo a página {pagina} de {total}")
        # A barra inclui a página que está sendo lida agora, como no rascunho
        # aprovado. Contando só as terminadas, um documento de uma página só
        # ficaria com a barra em zero do começo ao fim - e barra parada é lida
        # como programa travado.
        self.barra.setValue(pagina)
        self.restante.setText(self._estimar(pagina, total))

    def _estimar(self, pagina, total):
        """Quanto falta, calculado pelo ritmo real desta leitura.

        A estimativa sai do que já aconteceu nesta máquina e neste documento, e
        não de um número fixo escrito no código: página com muito texto demora
        mais que página quase vazia, e máquina lenta demora mais que rápida.
        """
        paginas_prontas = pagina - 1
        if paginas_prontas < 1:
            return "Calculando quanto falta…"

        por_pagina = (time.monotonic() - self._comeco) / paginas_prontas
        segundos = round(por_pagina * (total - paginas_prontas))
        if segundos < 10:
            return "Faltam poucos segundos."
        if segundos < 60:
            return f"Faltam cerca de {segundos} segundos."
        minutos = round(segundos / 60)
        return f"Falta cerca de {minutos} minuto." if minutos == 1 else f"Faltam cerca de {minutos} minutos."

    def mostrar_que_esta_parando(self):
        """O cancelamento não é instantâneo, e a tela precisa dizer isso.

        A página que está sendo lida termina de ser lida - interromper o
        Tesseract no meio deixaria o programa num estado que ninguém sabe
        descrever. São uns dois segundos, e silêncio nesses dois segundos faz a
        pessoa clicar de novo achando que o botão não pegou.
        """
        self.contagem.setText("Parando a leitura…")
        self.restante.setText("Terminando a página que já estava sendo lida.")
        self.botao_cancelar.setEnabled(False)
        self.botao_cancelar.setText("Cancelando…")


class _FaixaDoTopo(QLabel):
    """Uma linha de aviso no alto do painel, que aparece só quando há o que dizer."""

    def __init__(self):
        super().__init__()
        self.setWordWrap(True)
        self.setVisible(False)
        self.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
            f"border-left: 3px solid {estilo.COR_DESTAQUE};"
            "background-color: rgba(59, 110, 165, 26);"
            f"border-radius: {estilo.RAIO}px;"
            f"padding: {estilo.ESPACO_2}px {estilo.ESPACO_3}px;"
        )

    def mostrar(self, texto):
        self.setText(texto)
        self.setVisible(True)

    def esconder(self):
        self.setVisible(False)


class _TelaErro(QWidget):
    """O arquivo que não abre: uma frase, e o caminho de volta."""

    # A caixa e o texto dentro dela têm largura fixa. Sem isso, o Qt calcula a
    # altura da caixa achando que a frase cabe numa linha só, e o fim do texto
    # some para fora da borda - a pessoa lê meia explicação e não tem como
    # saber que faltou pedaço.
    LARGURA_DA_CAIXA = 460
    LARGURA_DO_TEXTO = 400

    def __init__(self, ao_escolher_outro, ao_tentar_de_novo=None):
        super().__init__()
        self._ao_tentar_de_novo = ao_tentar_de_novo

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

        self.titulo = QLabel("Não foi possível abrir o documento")
        self.titulo.setStyleSheet(
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

        caixa_layout.addWidget(self.titulo)
        caixa_layout.addWidget(self.explicacao)

        self.botao_tentar = QPushButton("Tentar de novo")
        self.botao_tentar.setCursor(Qt.PointingHandCursor)
        self.botao_tentar.setStyleSheet(estilo.estilo_botao(principal=True))
        self.botao_tentar.setVisible(False)
        if ao_tentar_de_novo is not None:
            self.botao_tentar.clicked.connect(ao_tentar_de_novo)

        botao = QPushButton("Escolher outro documento")
        botao.setCursor(Qt.PointingHandCursor)
        botao.setStyleSheet(estilo.estilo_botao(principal=True))
        botao.clicked.connect(ao_escolher_outro)

        linha_botao = QHBoxLayout()
        linha_botao.setSpacing(estilo.ESPACO_3)
        linha_botao.addStretch()
        linha_botao.addWidget(self.botao_tentar)
        linha_botao.addWidget(botao)
        linha_botao.addStretch()

        layout.addWidget(caixa, alignment=Qt.AlignCenter)
        layout.addSpacing(estilo.ESPACO_4)
        layout.addLayout(linha_botao)

    def mostrar(self, caminho, motivo):
        """O documento que não abre: sem "tentar de novo", porque não adianta."""
        self.titulo.setText("Não foi possível abrir o documento")
        self.botao_tentar.setVisible(False)
        self._escrever(f"{caminho.name} — {motivo}")

    def mostrar_falha(self, titulo, motivo, pode_tentar_de_novo=True):
        """A leitura que estourou. O botão de tentar de novo só aparece quando
        tentar de novo pode dar certo."""
        self.titulo.setText(titulo)
        self.botao_tentar.setVisible(
            pode_tentar_de_novo and self._ao_tentar_de_novo is not None
        )
        self._escrever(motivo)

    def _escrever(self, texto):
        self.explicacao.setText(texto)
        # A frase muda de tamanho conforme o problema, então a altura de que
        # ela precisa é recalculada a cada vez.
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

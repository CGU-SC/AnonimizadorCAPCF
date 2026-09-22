"""O painel do item "Gerar OCR": o percurso do documento, da escolha à conferência.

É ele que troca de tela conforme o documento anda: escolher, conferir o
arquivo, ler, conferir o texto, ou explicar o que deu errado. Cada tela é uma
peça à parte, e este arquivo é quem sabe a ordem entre elas.

Segue os rascunhos aprovados mockups/ocr/03-escolher-o-documento.html (a
escolha), 04-lendo-o-documento.html (a leitura), 06-conferir-o-texto.html (a
conferência) e 10-falta-o-motor.html (o motor de leitura faltando).
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
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import estilo
from caminho_do_pdf import (
    CaminhoDoPdf,
    legenda_da_tela,
    FaixaDoTopo,
    montar_escolha_do_motor,
    titulo_da_tela,
)
from arquivo_md import caminho_livre, caminho_sugerido, gravar, montar_conteudo
from telas_de_salvar import (
    TelaDescartar,
    TelaGravado,
    TelaSaida,
    TelaSalvar,
    TelaSobrescrever,
    resumo_do_documento,
)
from motor_na_tela import ControleDoMotor


class PainelOcr(QWidget):
    def __init__(self, ao_seguir_para_anonimizar=None):
        super().__init__()
        # Quem recebe o texto conferido quando a pessoa escolhe "Seguir para
        # Anonimizar". É a janela principal quem sabe trocar de módulo; sem ela
        # (um painel montado sozinho), o botão fica apagado, e não enganando.
        self._ao_seguir_para_anonimizar = ao_seguir_para_anonimizar
        # Aceitar arquivo arrastado é uma das duas formas de escolher o
        # documento previstas na spec 002; a outra é o botão.
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_4,
                                  estilo.ESPACO_5, estilo.ESPACO_5)
        layout.setSpacing(0)

        self.telas = QStackedWidget()
        # O motor faltando - o aviso do alto, a tela cheia e as três saídas - é
        # a mesma peça que o Anonimizar usa.
        self.motor = ControleDoMotor(
            dono=self,
            pilha=self.telas,
            ao_escolher_outro=self.voltar_para_escolher,
            # Resolvido o motor com a pessoa na tela cheia, o documento segue
            # para a ficha, e não direto para a leitura.
            ao_resolvido=lambda ficha: self.pdf.mostrar_ficha(ficha),
        )
        self.aviso_do_motor = self.motor.aviso
        self.tela_sem_motor = self.motor.tela_sem_motor
        self.tela_escolher = self._montar_tela_escolher()
        # Do PDF escolhido ao texto conferido, quem conduz é a peça comum aos
        # dois módulos. Ela cria as telas desse trecho e as põe nesta pilha.
        self.pdf = CaminhoDoPdf(
            pilha=self.telas,
            titulo="Gerar OCR",
            legenda="Resultado da verificação do documento.",
            o_que_vai_acontecer=_o_que_vai_acontecer,
            ao_conferir=self.seguir_para_a_saida,
            ao_escolher_outro=self.voltar_para_escolher,
            ao_cancelar=self._leitura_foi_cancelada,
            ao_abrir_conferencia=self._comecou_a_conferencia,
            tem_motor=self.motor.conferir,
            ao_faltar_motor=self.motor.mostrar_que_falta,
        )
        self.tela_verificando = self.pdf.tela_verificando
        self.tela_ficha = self.pdf.tela_ficha
        self.tela_lendo = self.pdf.tela_lendo
        self.tela_decisao = self.pdf.tela_decisao
        self.tela_conferencia = self.pdf.tela_conferencia
        self.tela_erro = self.pdf.tela_erro
        self.tela_saida = TelaSaida(
            ao_salvar=self.escolher_onde_salvar,
            ao_voltar=self.voltar_a_conferencia,
            ao_processar_outro=self.voltar_para_escolher,
            ao_anonimizar=(self.seguir_para_anonimizar
                           if ao_seguir_para_anonimizar else None),
        )
        self.tela_salvar = TelaSalvar(
            ao_salvar=self.tentar_salvar,
            ao_voltar=self.voltar_a_saida,
        )
        self.tela_sobrescrever = TelaSobrescrever(
            ao_escrever_por_cima=self.escrever_por_cima,
            ao_outro_nome=self.salvar_com_outro_nome,
        )
        self.tela_gravado = TelaGravado(ao_processar_outro=self.voltar_para_escolher)
        # O caminho que a pessoa pediu, guardado enquanto o programa pergunta se
        # pode escrever por cima do arquivo que já existe ali.
        self._caminho_pedido = None
        self.tela_descartar = TelaDescartar(
            ao_descartar=self._descartar_e_seguir,
            ao_voltar=self._voltar_de_onde_estava,
        )
        # Se o texto que está na conferência já foi salvo. Começa como salvo
        # porque, sem conferência nenhuma, não há o que perder.
        self._texto_salvo = True
        # O que a pessoa pediu para fazer quando a pergunta de descartar
        # apareceu, e a tela em que ela estava - para seguir com o pedido se ela
        # confirmar, ou voltar exatamente para onde estava se não.
        self._acao_pendente = None
        self._tela_antes_da_pergunta = None
        for tela in (self.tela_escolher, self.tela_saida, self.tela_salvar,
                     self.tela_sobrescrever, self.tela_gravado,
                     self.tela_descartar):
            self.telas.addWidget(tela)

        layout.addWidget(self.telas)
        # A primeira tela é a de escolher. Sem dizer isso, a pilha abre na tela
        # que entrou nela primeiro - e, desde que o caminho do PDF virou peça à
        # parte, quem entra primeiro é uma tela do meio do caminho.
        self.telas.setCurrentWidget(self.tela_escolher)
        self._conferir_o_motor()

    # ---------------------------------------------------------------- telas

    def _montar_tela_escolher(self):
        conteudo = QWidget()
        layout = QVBoxLayout(conteudo)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(titulo_da_tela("Gerar OCR"))
        layout.addWidget(legenda_da_tela(
            "Converte documento digitalizado em texto para conferência."))
        layout.addSpacing(estilo.ESPACO_4)

        # O aviso vem já na tela de escolher, antes de qualquer documento: fazer
        # a pessoa arrastar um PDF para só então contar que falta uma peça seria
        # gastar o tempo dela com uma notícia que o programa já tinha.
        layout.addWidget(self.motor.aviso)
        layout.addWidget(self.motor.espaco_depois_do_aviso)

        # A faixa só aparece quando há o que contar - hoje, quando a pessoa
        # cancela uma leitura. Voltar calada faria quem clicou sem querer não
        # descobrir o que aconteceu.
        self.faixa_do_topo = FaixaDoTopo()
        layout.addWidget(self.faixa_do_topo)

        layout.addWidget(self._montar_area_de_arrastar())
        layout.addSpacing(estilo.ESPACO_4)
        layout.addWidget(self._montar_escolha_do_motor())
        layout.addStretch()

        # Com o aviso do motor no alto, a tela passa da altura da janela. Sem a
        # rolagem, o Qt espreme tudo para caber: as frases do aviso se
        # sobrepõem e o botão de escolher o arquivo sai achatado. Com ela, cada
        # coisa fica no tamanho certo, e o que sobra desce.
        tela = QScrollArea()
        tela.setWidget(conteudo)
        tela.setWidgetResizable(True)
        tela.setFrameShape(QFrame.NoFrame)
        tela.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tela.setStyleSheet(
            f"""
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {estilo.COR_BORDA};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            """
        )
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
        bloco, self.motor_tesseract, self.motor_ia_local = montar_escolha_do_motor(
            "MOTOR DE LEITURA")
        return bloco

    # ------------------------------------------------------------- escolher

    def _abrir_seletor_de_arquivo(self):
        # A pasta inicial fica em branco de propósito: nada é lembrado entre um
        # uso e outro, nem a última pasta usada (RN-22).
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Escolher documento", "", "Documentos PDF (*.pdf)"
        )
        if caminho:
            self.receber_documento(Path(caminho))

    # ------------------------------------------------- o caminho do PDF

    # Daqui para baixo, quem faz o trabalho é a peça comum (`caminho_do_pdf`).
    # O painel continua sendo o endereço dessas ações para quem olha de fora -
    # inclusive para os testes, que conferem este módulo pelo nome delas.

    @property
    def leitura(self):
        return self.pdf.leitura

    @leitura.setter
    def leitura(self, valor):
        self.pdf.leitura = valor

    @property
    def ficha_atual(self):
        return self.pdf.ficha_atual

    @ficha_atual.setter
    def ficha_atual(self, valor):
        self.pdf.ficha_atual = valor

    def comecar_a_ler(self, ficha):
        self.pdf.comecar_a_ler(ficha)

    def seguir_a_partir_da_ficha(self, ficha):
        self.pdf.seguir_a_partir_da_ficha(ficha)

    def decidir_sobre_o_texto_existente(self, ficha):
        self.pdf.decidir_sobre_o_texto_existente(ficha)

    def aproveitar_o_texto_existente(self, ficha, paginas):
        self.pdf.aproveitar_o_texto_existente(ficha, paginas)

    def tentar_ler_de_novo(self):
        self.pdf.tentar_ler_de_novo()

    def cancelar_leitura(self):
        self.pdf.cancelar_leitura()

    def abandonar_leitura(self):
        self.pdf.abandonar_leitura()

    def _comecou_a_conferencia(self):
        """Da conferência em diante existe texto que se perde ao sair."""
        self._texto_salvo = False

    def _leitura_foi_cancelada(self, pagina):
        """Cancelar volta ao começo - dizendo o que aconteceu.

        Voltar calada faria quem clicou sem querer não descobrir o que houve.
        """
        self.faixa_do_topo.mostrar(
            f"Leitura cancelada na página {pagina}. Nada foi gravado, e o "
            "documento original não foi tocado."
        )
        self.voltar_para_escolher()

    # ------------------------------------------------------------- salvar

    def seguir_para_a_saida(self):
        """Depois do "Conferido": as duas saídas do texto."""
        self.tela_saida.mostrar(*self._resumo_do_que_foi_conferido())
        self.telas.setCurrentWidget(self.tela_saida)

    def seguir_para_anonimizar(self):
        """Leva o texto conferido para a revisão do Anonimizar (RN-16).

        Sem gravar arquivo nenhum no meio - é o que torna este o caminho seguro.
        E o Gerar OCR fica exatamente como estava, com o texto conferido na
        escolha da saída: um clique por engano não joga fora uma leitura de PDF,
        que custa minutos (oitava emenda da spec 003).
        """
        if self._ao_seguir_para_anonimizar is None or self.ficha_atual is None:
            return
        self._ao_seguir_para_anonimizar(
            self.ficha_atual.caminho, self.tela_conferencia.texto_conferido())

    def escolher_onde_salvar(self):
        self.tela_salvar.mostrar(
            caminho_sugerido(self.ficha_atual.caminho),
            *self._resumo_do_que_foi_conferido(),
        )
        self.telas.setCurrentWidget(self.tela_salvar)

    def tentar_salvar(self, caminho):
        """Grava, a não ser que já exista arquivo ali - aí pergunta antes (RN-16)."""
        if caminho.exists():
            self._caminho_pedido = caminho
            self.tela_sobrescrever.mostrar(caminho)
            self.telas.setCurrentWidget(self.tela_sobrescrever)
            return
        self._gravar(caminho)

    def escrever_por_cima(self):
        if self._caminho_pedido is not None:
            self._gravar(self._caminho_pedido)

    def salvar_com_outro_nome(self):
        """Volta à tela de salvar com um nome que não apaga nada, já preenchido."""
        sugestao = caminho_livre(self._caminho_pedido)
        self.tela_salvar.mostrar(sugestao, *self._resumo_do_que_foi_conferido())
        self.telas.setCurrentWidget(self.tela_salvar)

    def voltar_a_conferencia(self):
        self.telas.setCurrentWidget(self.tela_conferencia)

    def voltar_a_saida(self):
        self.telas.setCurrentWidget(self.tela_saida)

    def _gravar(self, caminho):
        conteudo = montar_conteudo(self.tela_conferencia.texto_conferido())
        try:
            gravar(caminho, conteudo)
        except OSError:
            # Pasta sem permissão, disco cheio, pasta de rede que saiu do ar: a
            # pessoa continua na tela de salvar, com o caminho que escolheu, e
            # pode tentar outro lugar. Nada do trabalho de conferência se perde.
            self.tela_salvar.mostrar(caminho, *self._resumo_do_que_foi_conferido())
            self.tela_salvar.avisar(
                "Não foi possível gravar nesse lugar. A pasta pode estar "
                "protegida, cheia ou fora do ar. Escolha outra pasta."
            )
            self.telas.setCurrentWidget(self.tela_salvar)
            return

        self._texto_salvo = True
        _nome, paginas, corrigidas = self._resumo_do_que_foi_conferido()
        self.tela_gravado.mostrar(caminho, paginas, corrigidas)
        self.telas.setCurrentWidget(self.tela_gravado)

    def _resumo_do_que_foi_conferido(self):
        return (
            self.ficha_atual.caminho.name,
            len(self.tela_conferencia.texto_conferido()),
            self.tela_conferencia.paginas_corrigidas(),
        )

    def encerrar(self):
        """Para a leitura antes de o programa fechar.

        Fechar a janela no meio de uma leitura fazia o programa estourar em vez
        de fechar limpo - e quem vê a caixa de erro do Windows fica sem saber se
        o documento foi mexido. A espera é de no máximo uma página, porque é só
        isso que falta terminar.
        """
        self.abandonar_leitura()

    def receber_documento(self, caminho):
        """Recebe outro documento - perguntando antes, se houver texto não salvo."""
        if not self._perguntar_antes_de_descartar(
            lambda: self._receber_documento(caminho)
        ):
            self._receber_documento(caminho)

    def _receber_documento(self, caminho):
        # A faixa do alto fala da leitura anterior; com documento novo em mãos,
        # ela não tem mais o que dizer.
        self.faixa_do_topo.esconder()
        self.pdf.comecar(caminho)

    def _conferir(self, caminho):
        self.pdf.conferir_documento(caminho)

    def _mostrar_erro(self, caminho, motivo):
        self.pdf.mostrar_erro(caminho, motivo)

    def voltar_para_escolher(self):
        """Volta ao começo - perguntando antes, se houver texto não salvo."""
        if not self._perguntar_antes_de_descartar(self._ir_para_escolher):
            self._ir_para_escolher()

    def _ir_para_escolher(self):
        self._descartar_o_texto()
        self.telas.setCurrentWidget(self.tela_escolher)

    # ----------------------------------------------- antes de descartar (RN-1)

    def _ha_texto_nao_salvo(self):
        return not self._texto_salvo and bool(self.tela_conferencia.texto_conferido())

    def _perguntar_antes_de_descartar(self, acao):
        """Segura a ação e pergunta, quando ela jogaria fora texto não salvo.

        Devolve se perguntou. Quando não há o que perder - nada conferido ainda,
        ou já salvo -, não pergunta nada: pergunta que aparece sem motivo ensina
        a clicar em "sim" sem ler, e aí ela não protege quando importa.
        """
        if not self._ha_texto_nao_salvo():
            return False
        self._acao_pendente = acao
        # Com a pergunta já na tela - a pessoa soltou outro documento por cima
        # dela -, o lugar para onde voltar continua sendo o de antes. Guardar a
        # própria pergunta como "de onde ela veio" deixava "Voltar e salvar"
        # sem sair do lugar, e a única saída que funcionava era a que jogava o
        # texto fora - exatamente a perda que esta pergunta existe para evitar.
        if self.telas.currentWidget() is not self.tela_descartar:
            self._tela_antes_da_pergunta = self.telas.currentWidget()
        # As mesmas palavras de sempre: a caixa passou a servir aos dois
        # módulos, e quem escreve a frase agora é quem pergunta.
        self.tela_descartar.mostrar(
            "O texto deste documento ainda não foi salvo",
            f"{resumo_do_documento(*self._resumo_do_que_foi_conferido())}.\n\n"
            "Se você seguir, o texto e as correções são descartados, e isso não "
            "se desfaz. Para ter o texto de volta, seria preciso ler o documento "
            "de novo e refazer as correções.",
        )
        self.telas.setCurrentWidget(self.tela_descartar)
        return True

    def _descartar_e_seguir(self):
        acao = self._acao_pendente
        self._acao_pendente = None
        self._descartar_o_texto()
        if acao is not None:
            acao()

    def _voltar_de_onde_estava(self):
        """Volta exatamente para a tela em que a pessoa estava, com tudo intacto."""
        self._acao_pendente = None
        self.telas.setCurrentWidget(
            self._tela_antes_da_pergunta or self.tela_conferencia
        )

    def _descartar_o_texto(self):
        self.pdf.esquecer()
        self._texto_salvo = True

    # ------------------------------------------------ o motor de leitura

    # Quem faz o trabalho é a peça comum (`motor_na_tela`). Os nomes ficam aqui
    # porque é por eles que o resto do programa e os testes falam com o módulo.

    def showEvent(self, evento):
        # Procura de novo toda vez que a pessoa entra no módulo: o motor pode
        # ter sido instalado com o programa aberto, e o aviso não deve continuar
        # dizendo que falta uma peça que já está lá.
        self.motor.conferir()
        super().showEvent(evento)

    @property
    def _motor_sem_portugues(self):
        return self.motor.sem_portugues

    def _conferir_o_motor(self):
        return self.motor.conferir()

    def _mostrar_que_falta_o_motor(self, ficha):
        self.motor.mostrar_que_falta(ficha)

    def instalar_o_motor(self):
        self.motor.instalar()

    def conferir_o_motor_de_novo(self):
        self.motor.conferir_de_novo()

    def apontar_a_pasta_do_motor(self):
        self.motor.apontar_a_pasta()

    def usar_a_pasta_do_motor(self, pasta):
        self.motor.usar_a_pasta(pasta)

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


def _o_que_vai_acontecer(ficha):
    """A linha do cartão que diz o que vem depois, no "Gerar OCR".

    São as mesmas palavras de sempre: aqui o documento termina na conferência, e
    o que ele vira depois dela é escolha da pessoa, na tela de saída.
    """
    if ficha.tem_camada_de_texto:
        return "aguarda sua decisão sobre o texto existente"
    return "cada página será lida como imagem"

"""O pedaço da revisão que cuida da IA: o botão, o andamento, a falha e o retomar.

Segue o rascunho aprovado mockups/anonimizar/11-revisar-com-ia.html. Quem aplica os
apontamentos no texto e na lista é a tela de revisão: aqui se conversa com a IA e se
diz à pessoa em que pé isso está.
"""
import time

from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QFrame,
    QProgressBar,
    QPushButton,
    QLabel,
)

import avisos_da_ia
import config_ia
import estilo
import revisao_ia
import trabalho_da_ia
from pecas_da_ia import Frase

# Um modelo local num computador comum pode levar minutos por pedaço, e cortar antes
# disso faria a IA parecer quebrada. É uma estimativa, a medir com os modelos de verdade.
SEGUNDOS_POR_PEDACO = 300

LARGURA = 620
MINIMO_PARA_ESTIMAR = 3

LIMITE_DA_REVISORA = (
    "A IA leu só o texto, sem comparar com a página original: um dígito lido errado num "
    "número que parece normal pode passar. Ela não dispensa a sua leitura."
)
NADA_A_MAIS = "A IA terminou e não apontou nada a mais. Isso não dispensa a sua leitura."
LIGUE_NO_MENU = "Ligue em Configurações de IA, no fim do menu"
NAO_CONFIRMADO = "A revisão segue sem IA: o endereço não foi confirmado, e nada foi enviado."


class RevisaoEmSegundoPlano(QThread):
    """Manda os pedaços um a um, ao lado da janela (a tela nunca espera a IA)."""

    avancou = Signal(int)      # o pedaço que está indo agora
    chegou = Signal(int, object)   # o pedaço que voltou, e os apontamentos dele
    terminou = Signal()
    falhou = Signal(int, str)  # o pedaço em que parou, e o que dizer na tela
    cancelou = Signal(int)

    def __init__(self, texto, pedacos, a_partir_de, base, token, modelo, numeros=()):
        super().__init__()
        # Só o que precisa: posição e número como está escrito, lidos antes de começar.
        # A lista de verdade é da tela, e não pode ser lida daqui de dentro.
        self._numeros = numeros
        self._texto = texto
        self._pedacos = pedacos
        self._a_partir_de = a_partir_de
        self._base, self._token, self._modelo = base, token, modelo
        self._cancelador = None
        self._pediram_para_parar = False

    def cancelar(self):
        self._pediram_para_parar = True
        if self._cancelador is not None:
            self._cancelador.cancelar()

    def run(self):
        import rede_da_ia
        self._cancelador = rede_da_ia.Cancelador()
        indice = self._a_partir_de
        try:
            while indice < len(self._pedacos):
                if self._pediram_para_parar:
                    self.cancelou.emit(indice)
                    return
                self.avancou.emit(indice)
                pedaco = self._pedacos[indice]
                resposta = rede_da_ia.conversar(
                    self._base, self._token, self._modelo,
                    revisao_ia.pedido(self._texto[pedaco.inicio:pedaco.fim],
                                      [n.original for n in self._numeros
                                       if n.inicio < pedaco.fim and pedaco.inicio < n.fim]),
                    SEGUNDOS_POR_PEDACO, self._cancelador)
                self.chegou.emit(indice, revisao_ia.interpretar(resposta))
                indice += 1
        except rede_da_ia.PedidoCancelado:
            self.cancelou.emit(indice)
        except Exception as problema:
            # Seja o que for, a tela sai da espera e a revisão segue (RN-36).
            self.falhou.emit(indice, trabalho_da_ia.frase_da_falha(problema))
        else:
            self.terminou.emit()


class RevisaoPorIa(QObject):
    """As peças da IA na revisão, e o trabalho que corre ao lado da janela."""

    def __init__(self, pai, ao_apontar, numeros_marcados=lambda: ()):
        super().__init__()
        self._numeros_marcados = numeros_marcados
        self._pai = pai
        self._ao_apontar = ao_apontar
        self._texto = ""
        self._pedacos = []
        self._trabalho = None
        self._antigos = []
        self._apontou = False
        self.rodou = False
        # De onde a próxima tentativa continua; 0 é começar do começo.
        self._retomar_de = None
        # Pediram para parar: o que ainda chegar é ignorado. Sem isto, uma resposta já a
        # caminho mudaria o arquivo depois de a pessoa ver o resumo no salvar.
        self._parando = False
        # O próximo pedaço que ainda não foi aplicado: é dali que o "Tentar de novo" segue.
        self._proximo = 0
        # O relógio da faixa: um pedaço pode levar minutos, e a tela parada parece travada.
        self._relogio = QTimer(self)
        self._relogio.setInterval(1000)
        self._relogio.timeout.connect(self._mostrar_andamento)
        self._em_curso = 0
        self._primeiro_da_vez = 0
        self._inicio_da_vez = 0.0
        self._inicio_do_pedaco = 0.0

        self.botao = QPushButton("Revisar com IA")
        self.botao.setCursor(Qt.PointingHandCursor)
        self.botao.setStyleSheet(estilo.estilo_botao(principal=False))
        self.botao.clicked.connect(lambda _=False: self.comecar())
        self.explicacao = QLabel(LIGUE_NO_MENU)
        self.explicacao.setAlignment(Qt.AlignHCenter)
        self.explicacao.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; color: {estilo.COR_TEXTO_SECUNDARIO};")

        self.faixa = QFrame()
        self.faixa.setObjectName("faixa_da_revisao_por_ia")
        self.faixa.setFixedWidth(LARGURA)
        dentro = QHBoxLayout(self.faixa)
        dentro.setContentsMargins(estilo.ESPACO_3, estilo.ESPACO_2,
                                  estilo.ESPACO_3, estilo.ESPACO_2)
        dentro.setSpacing(estilo.ESPACO_2)
        self.barra = QProgressBar()
        self.barra.setFixedWidth(90)
        self.barra.setFixedHeight(6)
        self.barra.setTextVisible(False)
        self.barra.setStyleSheet(
            f"""
            QProgressBar {{ background: {estilo.COR_BORDA}; border: none; border-radius: 3px; }}
            QProgressBar::chunk {{ background: {estilo.COR_IA}; border-radius: 3px; }}
            """
        )
        self.frase = Frase(largura=LARGURA - 240, cor=estilo.COR_TEXTO)
        self.botao_cancelar = QPushButton("Cancelar")
        self.botao_cancelar.clicked.connect(lambda _=False: self.cancelar())
        self.botao_tentar = QPushButton("Tentar de novo")
        self.botao_tentar.clicked.connect(lambda _=False: self.retomar())
        for botao in (self.botao_cancelar, self.botao_tentar):
            botao.setCursor(Qt.PointingHandCursor)
            botao.setStyleSheet(estilo.estilo_botao(principal=False, pequeno=True))
        dentro.addWidget(self.barra)
        dentro.addWidget(self.frase)
        dentro.addStretch()
        dentro.addWidget(self.botao_cancelar)
        dentro.addWidget(self.botao_tentar)
        self.faixa.setVisible(False)

        self.limite = Frase(LIMITE_DA_REVISORA, largura=LARGURA)
        self.limite.setVisible(False)
        self.atualizar()

    # ------------------------------------------------------------------ uso

    def novo_documento(self, texto, paginas=None):
        """A revisão abriu com outro documento: nada do anterior continua (RN-33)."""
        self.parar()
        self._texto = texto
        self._pedacos = revisao_ia.partir(texto, paginas)
        self._apontou = False
        self.rodou = False
        self._retomar_de = None
        self.faixa.setVisible(False)
        self.limite.setVisible(False)
        self.atualizar()
        if (self._pedacos and config_ia.revisora_ativa()
                and config_ia.inicio_da_revisao() == config_ia.INICIO_AO_ABRIR):
            # Logo depois, e não agora: a tela da revisão precisa aparecer antes de uma
            # pergunta sobre o endereço.
            QTimer.singleShot(0, self.comecar)

    def esquecer(self):
        self.parar()
        self._texto = ""
        self._pedacos = []
        self._apontou = False
        self.rodou = False
        self._retomar_de = None
        self.faixa.setVisible(False)
        self.limite.setVisible(False)

    def atualizar(self):
        """Põe o botão de acordo com o que está configurado agora."""
        ativa = config_ia.revisora_ativa()
        self.botao.setEnabled(ativa and self._trabalho is None and bool(self._pedacos))
        self.botao.setText("Revisar de novo com IA" if self.rodou else "Revisar com IA")
        self.explicacao.setToolTip("")
        if not ativa:
            self.explicacao.setText(LIGUE_NO_MENU)
        elif config_ia.destino_ligado() != config_ia.LM_STUDIO:
            self.explicacao.setText("Vai para o Servidor de IA Interno")
        elif not self._pedacos:
            # Sem documento, esta frase nem está à vista, e conferir o endereço carregaria
            # o arquivo da rede só por abrir o programa (RN-43).
            self.explicacao.setText("Vai para o LM Studio")
        elif config_ia.lm_studio_nesta_maquina():
            self.explicacao.setText("Vai para o LM Studio, nesta máquina")
        else:
            # O endereço fica no balão, e não na frase: comprido, ele alargaria a coluna e
            # espremeria os botões da mesma fileira.
            self.explicacao.setText("Vai para o LM Studio, em outra máquina")
            self.explicacao.setToolTip(config_ia.endereco_do_lm_studio())

    def rodando(self):
        return self._trabalho is not None

    def comecar(self):
        """Do começo do documento."""
        self._mandar(0)

    def retomar(self):
        """Só o que faltou (RN-37)."""
        self._mandar(self._retomar_de or 0)

    def _mandar(self, a_partir_de):
        # A revisora pode ter sido desligada entre o agendamento e aqui.
        if self._trabalho is not None or not self._pedacos or not config_ia.revisora_ativa():
            return
        if not avisos_da_ia.pode_usar_o_destino(self._pai):
            self.faixa.setVisible(True)
            self._mostrar_faixa(NAO_CONFIRMADO, andando=False, pode_tentar=False)
            return
        destino = config_ia.destino_ligado()
        trabalho = RevisaoEmSegundoPlano(
            self._texto, self._pedacos, a_partir_de, config_ia.base_do_destino(destino),
            config_ia.token_do_destino(destino), config_ia.modelo_da_revisora(destino),
            self._numeros_marcados())
        self._trabalho = trabalho
        self._parando = False
        self._proximo = a_partir_de
        if a_partir_de == 0:
            self._apontou = False
        self.rodou = True
        self.limite.setVisible(True)
        self.atualizar()
        trabalho.avancou.connect(lambda indice: self._avancou(trabalho, indice))
        trabalho.chegou.connect(lambda indice, lista: self._chegou(trabalho, indice, lista))
        trabalho.terminou.connect(lambda: self._terminou(trabalho))
        trabalho.falhou.connect(lambda indice, frase: self._falhou(trabalho, indice, frase))
        trabalho.cancelou.connect(lambda indice: self._cancelou(trabalho, indice))
        # Ligado antes de começar: ligado depois, o aviso de término podia já ter passado,
        # e o trabalho ficava guardado, com o documento inteiro, até fechar o programa.
        trabalho.finished.connect(lambda: self._soltar(trabalho))
        self.barra.setMaximum(len(self._pedacos))
        self._primeiro_da_vez = a_partir_de
        self._inicio_da_vez = time.monotonic()
        self._avancou(trabalho, a_partir_de)
        self._relogio.start()
        trabalho.start()

    def cancelar(self):
        if self._trabalho is not None:
            self._parando = True
            self._trabalho.cancelar()

    def parar(self):
        """Para e esquece o trabalho em andamento, sem esperar a resposta do modelo:
        a espera por um pedido é cortada na hora."""
        self._relogio.stop()
        trabalho, self._trabalho = self._trabalho, None
        if trabalho is not None:
            trabalho.cancelar()
            self._guardar_ate_terminar(trabalho)

    def encerrar(self):
        self.parar()
        for trabalho in list(self._antigos):
            trabalho.wait(3000)

    # -------------------------------------------------------------- os avisos

    def _e_o_de_agora(self, trabalho):
        return trabalho is self._trabalho

    def _avancou(self, trabalho, indice):
        if self._e_o_de_agora(trabalho) and not self._parando:
            self.barra.setValue(indice)
            self._em_curso = indice
            self._inicio_do_pedaco = time.monotonic()
            self._mostrar_andamento()

    def _mostrar_andamento(self):
        agora = time.monotonic()
        feitos = self._em_curso - self._primeiro_da_vez
        faltam = None
        # Só com alguns pedaços feitos, e contando o tempo do que está indo: com a média de
        # uma página rápida, a tela dizia "falta 1 min" numa página parada havia 48 s.
        if feitos >= MINIMO_PARA_ESTIMAR:
            media = (agora - self._inicio_da_vez) / feitos
            faltam = media * (len(self._pedacos) - self._em_curso)
        self._mostrar_faixa(
            revisao_ia.frase_do_andamento(revisao_ia.onde_esta(self._pedacos, self._em_curso),
                                          agora - self._inicio_do_pedaco, faltam),
            andando=True)

    def _chegou(self, trabalho, indice, apontamentos):
        if not self._e_o_de_agora(trabalho) or self._parando:
            return
        self._proximo = indice + 1
        # Só o que entrou de fato conta: se tudo foi descartado, a faixa precisa dizer
        # que a IA terminou sem nada a mais, e não sumir sem explicação.
        if apontamentos and self._ao_apontar(apontamentos, self._pedacos[indice]):
            self._apontou = True

    def _terminou(self, trabalho):
        if not self._e_o_de_agora(trabalho):
            return
        # Cancelou no instante em que a última resposta chegava: ela foi descartada, e
        # dizer "terminou sem nada a mais" seria um falso tudo certo.
        if self._parando and self._proximo < len(self._pedacos):
            self._cancelou(trabalho, self._proximo)
            return
        self._acabou(None)
        if self._apontou:
            self.faixa.setVisible(False)
        else:
            self._mostrar_faixa(NADA_A_MAIS, andando=False)

    def _falhou(self, trabalho, indice, frase):
        if not self._e_o_de_agora(trabalho):
            return
        if self._parando:
            self._cancelou(trabalho, self._proximo)
            return
        self._acabou(indice)
        faltou = revisao_ia.o_que_faltou(self._pedacos, indice)
        self._mostrar_faixa(f"{faltou} {frase}", andando=False, pode_tentar=True, alerta=True)

    def _cancelou(self, trabalho, indice):
        if not self._e_o_de_agora(trabalho):
            return
        self._acabou(self._proximo)
        faltou = revisao_ia.o_que_faltou(self._pedacos, self._proximo)
        self._mostrar_faixa(f"{faltou} Você cancelou.", andando=False, pode_tentar=True,
                            alerta=True)

    def _acabou(self, retomar_de):
        self._relogio.stop()
        self._guardar_ate_terminar(self._trabalho)
        self._trabalho = None
        self._retomar_de = retomar_de
        self.atualizar()

    def _guardar_ate_terminar(self, trabalho):
        """O aviso de que acabou chega um instante antes de a linha paralela terminar de
        fato, e destruí-la nesse instante derrubaria o programa."""
        if not trabalho.isFinished():
            self._antigos.append(trabalho)

    def _soltar(self, trabalho):
        if trabalho in self._antigos:
            self._antigos.remove(trabalho)

    def _mostrar_faixa(self, frase, andando, pode_tentar=False, alerta=False):
        cor = estilo.COR_ALERTA if alerta else estilo.COR_IA
        fundo = "rgba(217, 164, 65, 26)" if alerta else "rgba(179, 157, 219, 23)"
        self.faixa.setStyleSheet(
            f"""
            QFrame#faixa_da_revisao_por_ia {{
                background-color: {fundo};
                border-left: 3px solid {cor};
                border-radius: {estilo.RAIO}px;
            }}
            """
        )
        self.frase.setText(frase)
        self.barra.setVisible(andando)
        self.botao_cancelar.setVisible(andando)
        self.botao_tentar.setVisible(pode_tentar)
        self.faixa.setVisible(True)

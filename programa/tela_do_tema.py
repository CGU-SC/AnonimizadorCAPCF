"""A tela do Tema, a primeira opção de Configurações (emenda de 05/11/2026 da
spec 001, RN-16 a RN-25; rascunho mockups/janela/06-tema-claro-e-configuracoes.html).

A pessoa marca Escuro ou Claro, e a escolha é guardada na hora do clique (RN-23
da spec 001, RN-42 da spec 002). O tema da tela não muda junto: as cores de cada
peça são postas quando ela nasce, e por isso o tema novo vale quando o programa
abre de novo (RN-17).
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

import estilo
import preferencias
from cabecalho_da_tela import CabecalhoDaTela
from caminho_do_pdf import rotulo_de_secao
from pecas_da_ia import LARGURA_DO_CONTEUDO, Frase, estilo_do_radio

TEMA = "tema"

# Onde a escolha mora no preferencias.ini, ao lado do motor e da janela.
LEMBRAR_TEMA = "aparencia"
CHAVE_DO_TEMA = "tema"

TITULO = "Tema"
LEGENDA = "As cores do programa. O desenho das telas é o mesmo nos dois."
OPCOES = (
    (estilo.ESCURO, "Escuro", "Fundo grafite e letra clara · ", "o tema de quem nunca escolheu"),
    (estilo.CLARO, "Claro", "Fundo claro e letra escura", ""),
)
VALE_AO_REABRIR = "O tema novo vale quando o programa abrir de novo."
REABRIR_AGORA = "Reabrir agora"
NAO_DEU_PARA_REABRIR = ("Não foi possível reabrir agora. O tema novo vale quando você "
                        "fechar e abrir o programa.")

# O que reabrir jogaria fora num módulo (RN-25). Cada módulo tem um documento por vez,
# então há no máximo uma das duas coisas em cada um.
LEITURA = "leitura"
TEXTO_NAO_SALVO = "texto não salvo"
GERAR_OCR = "Gerar OCR"
ANONIMIZAR = "Anonimizar"

CONTINUAR_A_LEITURA = "Continuar a leitura"
NAO_REABRIR = "Não reabrir"
REABRIR_MESMO_ASSIM = "Reabrir mesmo assim"

# As frases do fluxo de cada caminho torto da spec, com o nome do módulo no lugar.
_UMA_COISA = {
    LEITURA: ("Há uma leitura em andamento no {modulo}.",
              "Reabrir agora a interrompe, e o documento precisa ser lido de novo depois."),
    TEXTO_NAO_SALVO: ("Há um texto lido e ainda não salvo no {modulo}.",
                      "Reabrir agora o descarta, e o documento precisa ser lido de novo "
                      "depois."),
}
# A tabela do acréscimo de 06/11/2026 da spec, pela ordem (Gerar OCR, Anonimizar).
_DUAS_COISAS = {
    (LEITURA, LEITURA): (
        "Há uma leitura em andamento no Gerar OCR e outra no Anonimizar.",
        "Reabrir agora interrompe as duas, e os documentos precisam ser lidos de novo "
        "depois."),
    (LEITURA, TEXTO_NAO_SALVO): (
        "Há uma leitura em andamento no Gerar OCR e um texto lido e ainda não salvo no "
        "Anonimizar.",
        "Reabrir agora interrompe a leitura e descarta o texto, e os dois documentos "
        "precisam ser lidos de novo depois."),
    (TEXTO_NAO_SALVO, LEITURA): (
        "Há um texto lido e ainda não salvo no Gerar OCR e uma leitura em andamento no "
        "Anonimizar.",
        "Reabrir agora descarta o texto e interrompe a leitura, e os dois documentos "
        "precisam ser lidos de novo depois."),
    (TEXTO_NAO_SALVO, TEXTO_NAO_SALVO): (
        "Há um texto lido e ainda não salvo no Gerar OCR e outro no Anonimizar.",
        "Reabrir agora descarta os dois, e os documentos precisam ser lidos de novo "
        "depois."),
}


def pergunta_antes_de_reabrir(no_gerar_ocr, no_anonimizar):
    """A linha de cima, a de baixo e o botão forte da pergunta, ou None quando não há
    nada a perder (RN-25 e RN-27).

    O botão forte é o que não perde nada: com uma leitura no meio, é deixá-la seguir.
    """
    if no_gerar_ocr and no_anonimizar:
        cima, baixo = _DUAS_COISAS[(no_gerar_ocr, no_anonimizar)]
    elif no_gerar_ocr or no_anonimizar:
        cima, baixo = _UMA_COISA[no_gerar_ocr or no_anonimizar]
        cima = cima.format(modulo=GERAR_OCR if no_gerar_ocr else ANONIMIZAR)
    else:
        return None
    forte = CONTINUAR_A_LEITURA if LEITURA in (no_gerar_ocr, no_anonimizar) else NAO_REABRIR
    return cima, baixo, forte

# O recuo da explicação embaixo de cada opção: começa onde começa o nome dela,
# depois da bolinha, como no rascunho aprovado.
RECUO_DA_EXPLICACAO = 24


def lembrado():
    """O tema guardado, ou None se não há um que dê para usar (RN-42 da spec 002):
    o que não é `escuro` nem `claro` vale como nada guardado."""
    tema = preferencias.ler(LEMBRAR_TEMA, CHAVE_DO_TEMA)
    return tema if tema in estilo.TEMAS else None


class TelaDoTema(QWidget):
    def __init__(self):
        super().__init__()
        corpo = QVBoxLayout(self)
        corpo.setContentsMargins(0, 0, 0, 0)
        corpo.setSpacing(0)
        # O desenho do item "Tema", e não a engrenagem: com ela nas quatro telas, o
        # título não dizia em qual a pessoa está (RN-31 da spec 001).
        self.cabecalho = CabecalhoDaTela("tema", TITULO, LEGENDA)
        corpo.addWidget(self.cabecalho)
        corpo.addSpacing(estilo.ESPACO_4)
        corpo.addWidget(rotulo_de_secao("TEMA"))

        # Começa marcado o tema que está na tela. A escolha seguinte fica só na
        # memória da tela, além do arquivo: se o arquivo não aceitar a gravação, ela
        # continua valendo até fechar (RN-39 da spec 002).
        self.escolhido = estilo.TEMA
        # O grupo faz um radio desmarcar o outro mesmo cada um na própria caixa, e
        # é o que garante que o último clique é o que a tela mostra ("O que já nos
        # mordeu").
        self.grupo = QButtonGroup(self)
        self.opcoes = {}
        for tema, nome, explicacao, destaque in OPCOES:
            botao = QRadioButton(nome)
            botao.setStyleSheet(estilo_do_radio())
            botao.setChecked(tema == self.escolhido)
            botao.clicked.connect(lambda _=False, t=tema: self._marcou(t))
            self.grupo.addButton(botao)
            self.opcoes[tema] = botao
            corpo.addSpacing(10)
            corpo.addWidget(botao)
            corpo.addSpacing(2)
            corpo.addWidget(_explicacao(explicacao, destaque))

        corpo.addSpacing(22)
        self.aviso = _AvisoDeReabrir()
        self.aviso.botao.clicked.connect(self._reabrir)
        corpo.addWidget(self.aviso)
        # A pergunta toma o lugar da frase e do botão, na própria tela, sem caixa por
        # cima da janela (RN-25).
        self.pergunta = _PerguntaAntesDeReabrir()
        self.pergunta.botao_forte.clicked.connect(self._nao_reabrir)
        self.pergunta.botao_mesmo_assim.clicked.connect(self._reabrir_mesmo_assim)
        corpo.addWidget(self.pergunta)
        corpo.addStretch()
        # Quem fecha e abre o programa é a janela; ela se põe aqui ao nascer.
        self.ao_reabrir = None
        # O que a pergunta na tela disse que se perde, para o "Reabrir mesmo assim"
        # levar junto o que a pessoa aceitou perder.
        self._perda_perguntada = None
        self._atualizar()

    def _marcou(self, tema):
        self.escolhido = tema
        preferencias.gravar(LEMBRAR_TEMA, CHAVE_DO_TEMA, tema)
        self._atualizar()

    def _atualizar(self):
        # A frase só aparece quando há o que reabrir: marcar de volta o tema da tela
        # a faz sumir (RN-23). Uma pergunta que estava na tela some junto: ela era
        # sobre um reabrir que a pessoa deixou de pedir.
        self.pergunta.setVisible(False)
        self.aviso.setVisible(self.escolhido != estilo.TEMA)
        self.aviso.mostrar_o_botao()

    def _reabrir(self):
        # O tema vai junto com o pedido, e não só no arquivo: o preferencias.ini
        # pode não ter aceitado a gravação, e ainda assim o programa abre no tema
        # marcado (RN-24).
        if self.ao_reabrir is not None and not self.ao_reabrir(self.escolhido):
            self.dizer_que_nao_deu()

    def perguntar(self, perda):
        """Mostra a pergunta antes de reabrir. `perda` é o que se perderia no Gerar
        OCR e no Anonimizar, nessa ordem."""
        self._perda_perguntada = perda
        self.aviso.setVisible(False)
        self.pergunta.mostrar(*pergunta_antes_de_reabrir(*perda))

    def _nao_reabrir(self):
        # Nada muda nos módulos: a leitura segue, ou o texto continua lá, e a frase e
        # o botão voltam.
        self._atualizar()

    def _reabrir_mesmo_assim(self):
        aceita = self._perda_perguntada
        self._atualizar()
        if self.ao_reabrir is not None and not self.ao_reabrir(self.escolhido, aceita):
            self.dizer_que_nao_deu()

    def hideEvent(self, evento):
        # Saindo da tela, a pergunta sai junto. Deixada para a volta, ela falaria de um
        # trabalho que pode já ser outro, e o "Reabrir mesmo assim" jogaria fora o que
        # a pessoa não aceitou perder (revisão da etapa 6). Minimizar a janela não é
        # sair: o Windows esconde a tela sem a pessoa ter ido a lugar nenhum.
        if not evento.spontaneous() and not self.pergunta.isHidden():
            self._atualizar()
        super().hideEvent(evento)

    def dizer_que_nao_deu(self):
        self.pergunta.setVisible(False)
        self.aviso.setVisible(True)
        self.aviso.dizer_que_nao_deu()


def _explicacao(texto, destaque):
    # O pedaço em destaque vai na cor do texto, com o mesmo peso: é o que diz qual
    # é o tema de quem nunca escolheu, sem gritar.
    linha = QLabel(texto + (f"<span style='color:{estilo.COR_TEXTO}'>{destaque}</span>"
                            if destaque else ""))
    linha.setStyleSheet(
        f"font-size: 12.5px; color: {estilo.COR_TEXTO_SECUNDARIO};"
        f"margin-left: {RECUO_DA_EXPLICACAO}px;"
    )
    return linha


class _AvisoDeReabrir(QFrame):
    """A faixa com a frase de que o tema novo vale ao reabrir, e o "Reabrir agora"
    ao lado dela.

    Quando o programa não consegue abrir de novo, a frase do caminho torto toma o
    lugar das duas: ela já diz que o tema vale ao reabrir, e repetir a outra seria
    dizer a mesma coisa duas vezes.
    """

    def __init__(self):
        super().__init__()
        # A cor vale só para a faixa, pelo nome, e o texto de dentro fica
        # transparente: regra sem alvo pinta uma caixinha em volta de cada frase
        # ("O que já nos mordeu").
        self.setObjectName("aviso_de_reabrir")
        self.setStyleSheet(
            f"""
            QFrame#aviso_de_reabrir {{
                background-color: {estilo.COR_FUNDO_ELEVADO};
                border: 1px solid {estilo.COR_BORDA};
                border-radius: {estilo.RAIO}px;
            }}
            QLabel {{ background: transparent; border: none; }}
            """
        )
        linha = QHBoxLayout(self)
        linha.setContentsMargins(14, 12, 14, 12)
        linha.setSpacing(14)
        self.frase = QLabel(VALE_AO_REABRIR)
        self.frase.setStyleSheet(f"font-size: 14px; color: {estilo.COR_TEXTO_SECUNDARIO};")
        linha.addWidget(self.frase, stretch=1)
        self.botao = QPushButton(REABRIR_AGORA)
        self.botao.setCursor(Qt.PointingHandCursor)
        self.botao.setStyleSheet(estilo.estilo_botao(principal=True))
        linha.addWidget(self.botao)

    def mostrar_o_botao(self):
        self.frase.setText(VALE_AO_REABRIR)
        self.botao.setVisible(True)

    def dizer_que_nao_deu(self):
        self.frase.setText(NAO_DEU_PARA_REABRIR)
        self.botao.setVisible(False)


class _PerguntaAntesDeReabrir(QFrame):
    """A faixa de aviso com o que reabrir jogaria fora, e os dois botões
    (rascunho mockups/janela/06, seção 2b).

    A linha de cima vai em negrito, na letra de aviso, e a de baixo comum: é a mesma
    faixa nas perguntas de uma coisa só e nas de duas (acréscimo de 06/11/2026 da
    spec 001).
    """

    def __init__(self):
        super().__init__()
        self.setObjectName("pergunta_antes_de_reabrir")
        self.setStyleSheet(
            f"""
            QFrame#pergunta_antes_de_reabrir {{
                background-color: {estilo.COR_ALERTA_FUNDO};
                border: 1px solid {estilo.COR_ALERTA};
                border-radius: {estilo.RAIO}px;
            }}
            QLabel {{ background: transparent; border: none; }}
            """
        )
        corpo = QVBoxLayout(self)
        corpo.setContentsMargins(14, 12, 14, 12)
        corpo.setSpacing(4)
        # Largura fixa para a frase quebrar linha sem perder a última: a mais longa
        # da tabela da spec ocupa duas linhas ("O que já nos mordeu").
        largura = LARGURA_DO_CONTEUDO - 28
        self.cima = _frase_da_pergunta(largura, estilo.COR_ALERTA_TEXTO, forte=True)
        self.baixo = _frase_da_pergunta(largura, estilo.COR_TEXTO)
        corpo.addWidget(self.cima)
        corpo.addWidget(self.baixo)
        corpo.addSpacing(6)
        botoes = QHBoxLayout()
        botoes.setSpacing(estilo.ESPACO_2)
        self.botao_forte = QPushButton(CONTINUAR_A_LEITURA)
        self.botao_forte.setStyleSheet(estilo.estilo_botao(principal=True, pequeno=True))
        self.botao_mesmo_assim = QPushButton(REABRIR_MESMO_ASSIM)
        self.botao_mesmo_assim.setStyleSheet(
            estilo.estilo_botao(principal=False, pequeno=True))
        for botao in (self.botao_forte, self.botao_mesmo_assim):
            botao.setCursor(Qt.PointingHandCursor)
            botoes.addWidget(botao)
        botoes.addStretch()
        corpo.addLayout(botoes)
        self.setVisible(False)

    def mostrar(self, cima, baixo, forte):
        self.cima.setText(cima)
        self.baixo.setText(baixo)
        self.botao_forte.setText(forte)
        self.setVisible(True)


def _frase_da_pergunta(largura, cor, forte=False):
    # O mesmo tamanho de letra da frase do "Reabrir agora", que esta faixa substitui.
    # O estilo vem antes do texto: a altura é medida com a letra que vai aparecer.
    frase = Frase(largura=largura)
    frase.setStyleSheet(f"font-size: 14px; color: {cor}; font-weight: {600 if forte else 400};")
    return frase

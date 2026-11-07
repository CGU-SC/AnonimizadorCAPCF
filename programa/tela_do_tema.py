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
from pecas_da_ia import estilo_do_radio

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
        corpo.addStretch()
        # Quem fecha e abre o programa é a janela; ela se põe aqui ao nascer.
        self.ao_reabrir = None
        self._atualizar()

    def _marcou(self, tema):
        self.escolhido = tema
        preferencias.gravar(LEMBRAR_TEMA, CHAVE_DO_TEMA, tema)
        self._atualizar()

    def _atualizar(self):
        # A frase só aparece quando há o que reabrir: marcar de volta o tema da tela
        # a faz sumir (RN-23).
        self.aviso.setVisible(self.escolhido != estilo.TEMA)
        self.aviso.mostrar_o_botao()

    def _reabrir(self):
        # O tema vai junto com o pedido, e não só no arquivo: o preferencias.ini
        # pode não ter aceitado a gravação, e ainda assim o programa abre no tema
        # marcado (RN-24).
        if self.ao_reabrir is not None and not self.ao_reabrir(self.escolhido):
            self.dizer_que_nao_deu()

    def dizer_que_nao_deu(self):
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

"""As caixas de confirmação da IA, com o botão que não muda nada já escolhido.

O mesmo arranjo da dupla conferência: Enter e Esc nunca confirmam (RN-19 da spec
004), porque nestas caixas o caminho fácil precisa ser o que não envia nada.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)

import config_ia
import estilo
from pecas_da_ia import Frase

LARGURA = 520
LARGURA_DO_TEXTO = 460

_TONS = {"alerta": ("rgba(217, 164, 65, 26)", estilo.COR_ALERTA),
         "perigo": ("rgba(217, 83, 79, 26)", estilo.COR_ERRO)}

# O endereço que a pessoa confirmou nesta abertura do programa. Só na memória: o
# aviso volta na próxima abertura, e não fica confirmação gravada (RN-20).
_endereco_confirmado = None


class CaixaDaIa(QDialog):
    def __init__(self, titulo, frases, rotulo_sim, rotulo_nao, tom="alerta", pai=None):
        super().__init__(pai)
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setStyleSheet(f"background-color: {estilo.COR_FUNDO};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_4,
                                  estilo.ESPACO_4, estilo.ESPACO_4)
        layout.setSpacing(estilo.ESPACO_4)

        caixa = QFrame()
        caixa.setObjectName("caixa")
        caixa.setFixedWidth(LARGURA)
        fundo, borda = _TONS[tom]
        caixa.setStyleSheet(
            f"""
            QFrame#caixa {{
                background-color: {fundo};
                border-left: 4px solid {borda};
                border-radius: {estilo.RAIO}px;
            }}
            """
        )
        dentro = QVBoxLayout(caixa)
        dentro.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_3,
                                  estilo.ESPACO_4, estilo.ESPACO_3)
        dentro.setSpacing(estilo.ESPACO_2)
        dentro.addWidget(Frase(titulo, largura=LARGURA_DO_TEXTO, cor=estilo.COR_TEXTO,
                               pequeno=False, forte=True))
        for frase in frases:
            dentro.addWidget(Frase(frase, largura=LARGURA_DO_TEXTO))
        layout.addWidget(caixa)

        self.botao_sim = QPushButton(rotulo_sim)
        self.botao_sim.setCursor(Qt.PointingHandCursor)
        self.botao_sim.setStyleSheet(estilo.estilo_botao(principal=False))
        self.botao_sim.setAutoDefault(False)
        self.botao_sim.clicked.connect(self.accept)
        self.botao_nao = QPushButton(rotulo_nao)
        self.botao_nao.setCursor(Qt.PointingHandCursor)
        self.botao_nao.setStyleSheet(estilo.estilo_botao(principal=True))
        self.botao_nao.setDefault(True)
        self.botao_nao.setAutoDefault(True)
        self.botao_nao.clicked.connect(self.reject)
        acoes = QHBoxLayout()
        acoes.setSpacing(estilo.ESPACO_3)
        acoes.addStretch()
        acoes.addWidget(self.botao_sim)
        acoes.addWidget(self.botao_nao)
        acoes.addStretch()
        layout.addLayout(acoes)


def exibir(titulo, frases, rotulo_sim, rotulo_nao, tom="alerta", pai=None):
    """Mostra a caixa e diz se a pessoa confirmou. Fechar no X é não confirmar."""
    return CaixaDaIa(titulo, frases, rotulo_sim, rotulo_nao, tom, pai).exec() == QDialog.Accepted


def confirmar_troca_de_destino(outro, pai=None):
    nome = config_ia.NOME_NA_TELA[outro]
    return exibir(
        f"O {nome} será desligado",
        [f"Só um destino de IA fica ligado por vez. As escolhas do {nome} ficam "
         "guardadas, e voltam quando ele for religado."],
        "Desligar e ligar este", "Manter como está", pai=pai)


def confirmar_endereco(endereco, avaliacao, pai=None):
    """O aviso de risco do endereço não reconhecido (RN-19 e RN-22)."""
    frases = [
        endereco,
        "O programa não reconheceu este endereço como da própria máquina ou da "
        "rede interna. O texto do documento irá para lá com os CPFs inteiros, e "
        "enviar dados pessoais a um servidor externo traz riscos. Só confirme se a "
        "TI informou este endereço.",
    ]
    if avaliacao.sem_cifra:
        import rede_da_ia
        frases.append(rede_da_ia.SEM_CIFRA)
    confirmou = exibir("Este endereço pode ser externo", frases, "Usar mesmo assim",
                       "Não enviar", tom="perigo", pai=pai)
    if confirmou:
        lembrar_confirmado(endereco)
    return confirmou


def lembrar_confirmado(endereco):
    global _endereco_confirmado
    _endereco_confirmado = endereco


def esquecer_confirmado():
    lembrar_confirmado(None)


def pode_usar_o_destino(pai=None):
    """Antes de enviar qualquer coisa: o endereço é conferido de novo a cada uso.

    Conferido de novo porque um nome que dava em número interno pode passar a dar
    em número externo (RN-21). O aviso só aparece uma vez por abertura, para os
    dois usos juntos (RN-20). O LM Studio é sempre esta máquina, e não passa aqui.
    """
    if config_ia.destino_ligado() != config_ia.SERVIDOR:
        return True
    import rede_da_ia
    endereco = config_ia.endereco_do_servidor()
    avaliacao = rede_da_ia.avaliar_endereco(endereco, config_ia.enderecos_locais())
    if not avaliacao.valido:
        return False
    if avaliacao.reconhecido or _endereco_confirmado == endereco:
        return True
    return confirmar_endereco(endereco, avaliacao, pai)

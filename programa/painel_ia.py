"""O painel de Configurações de IA: três telas, uma por item do submenu.

Segue o rascunho aprovado mockups/ia/01-configuracoes-de-ia.html.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import estilo
from pecas_da_ia import Faixa, Frase, Interruptor, linha_do_switch, titulo_de_tela

LM_STUDIO = "lm_studio"
SERVIDOR = "servidor"
HABILITAR = "habilitar"


def _rolavel(tela):
    """Rola só na vertical: rolando para o lado, a primeira letra de tudo fica
    cortada, sem nada acusar ("O que já nos mordeu")."""
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setFrameShape(QFrame.NoFrame)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    area.setWidget(tela)
    return area


class _TelaBasica(QWidget):
    def __init__(self, titulo, legenda):
        super().__init__()
        self.corpo = QVBoxLayout(self)
        self.corpo.setContentsMargins(0, 0, 0, 0)
        self.corpo.setSpacing(estilo.ESPACO_3)
        self.corpo.addWidget(titulo_de_tela(titulo))
        self.corpo.addWidget(Frase(legenda))


class PainelIa(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_4,
                                  estilo.ESPACO_5, estilo.ESPACO_5)
        self.telas = QStackedWidget()
        layout.addWidget(self.telas)

        self.tela_lm_studio = _TelaBasica(
            "LM Studio", "A IA roda nesta máquina, e o documento não sai dela.")
        self.tela_servidor = _TelaBasica(
            "Servidor de IA Interno",
            "A IA roda num servidor da instituição. O texto do documento viaja "
            "até lá, com os CPFs inteiros.")
        self.tela_habilitar = _TelaBasica(
            "Habilitar IA",
            "Configure primeiro o LM Studio ou o Servidor de IA Interno, nos "
            "itens ao lado.")
        self._areas = {}
        for nome, tela in ((LM_STUDIO, self.tela_lm_studio),
                           (SERVIDOR, self.tela_servidor),
                           (HABILITAR, self.tela_habilitar)):
            tela.corpo.addStretch()
            area = _rolavel(tela)
            self._areas[nome] = area
            self.telas.addWidget(area)

    def mostrar(self, nome):
        self.telas.setCurrentWidget(self._areas[nome])

    def tela_atual(self):
        for nome, area in self._areas.items():
            if area is self.telas.currentWidget():
                return nome
        return None

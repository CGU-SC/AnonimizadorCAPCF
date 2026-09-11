"""A tela em que a pessoa decide o que fazer com o texto que já está no PDF.

Aparece só quando o documento escolhido tem texto gravado por dentro. Ela mostra
as primeiras linhas desse texto e oferece duas saídas: aproveitar, ou ignorar e
mandar ler as imagens.

O programa não julga se o texto presta - é a regra RN-4 da spec 002. Texto
gravado no PDF costuma ser melhor que o adivinhado de uma imagem, mas documento
que já passou por um OCR ruim antes carrega texto que é lixo puro. Quem vê a
diferença num olhar é uma pessoa; palpite errado aqui produz um arquivo de lixo
que ninguém percebe.

Segue o rascunho aprovado mockups/ocr/07-decidir-sobre-o-texto.html.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import estilo
from documento import primeiras_linhas
from leitura import tempo_estimado

LINHAS_DA_AMOSTRA = 12


class TelaDecisao(QWidget):
    def __init__(self, ao_aproveitar, ao_ignorar, ao_escolher_outro):
        super().__init__()
        self._ao_aproveitar = ao_aproveitar
        self._ao_ignorar = ao_ignorar
        self._ficha = None
        self._paginas = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        titulo = QLabel("Este documento já tem texto por dentro")
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_GRANDE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO};"
        )
        layout.addWidget(titulo)

        self.legenda = QLabel()
        self.legenda.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )
        layout.addWidget(self.legenda)
        layout.addSpacing(estilo.ESPACO_3)

        selo = QLabel("TEXTO GRAVADO NO PRÓPRIO DOCUMENTO")
        selo.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 700;"
            "color: #7fb1e8; background-color: rgba(59, 110, 165, 51);"
            "border-radius: 10px; padding: 3px 10px;"
        )
        layout.addWidget(selo, alignment=Qt.AlignLeft)
        layout.addSpacing(estilo.ESPACO_3)

        rotulo = QLabel("AS PRIMEIRAS LINHAS DESSE TEXTO")
        rotulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 700;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; letter-spacing: 1px;"
        )
        layout.addWidget(rotulo)

        self.amostra = QPlainTextEdit()
        self.amostra.setReadOnly(True)
        self.amostra.setStyleSheet(
            f"""
            QPlainTextEdit {{
                background-color: {estilo.COR_FUNDO_ELEVADO};
                border: 1px solid {estilo.COR_BORDA};
                border-radius: {estilo.RAIO}px;
                padding: {estilo.ESPACO_3}px;
                font-family: {estilo.FONTE_MONO};
                font-size: 12px;
                color: {estilo.COR_TEXTO};
            }}
            """
        )
        layout.addWidget(self.amostra, stretch=1)
        layout.addSpacing(estilo.ESPACO_3)

        layout.addLayout(self._montar_escolhas())
        layout.addSpacing(estilo.ESPACO_3)

        botao_outro = QPushButton("Escolher outro documento")
        botao_outro.setCursor(Qt.PointingHandCursor)
        botao_outro.setStyleSheet(estilo.estilo_botao(principal=False))
        botao_outro.clicked.connect(ao_escolher_outro)
        layout.addWidget(botao_outro, alignment=Qt.AlignHCenter)

    def _montar_escolhas(self):
        linha = QHBoxLayout()
        linha.setSpacing(estilo.ESPACO_3)

        self.botao_aproveitar = QPushButton("Aproveitar este texto")
        self.botao_aproveitar.setCursor(Qt.PointingHandCursor)
        self.botao_aproveitar.setStyleSheet(estilo.estilo_botao(principal=True))
        self.botao_aproveitar.clicked.connect(self._aproveitar)
        linha.addLayout(_coluna_da_escolha(
            self.botao_aproveitar,
            "Se o texto acima está legível. Vai direto para a conferência.",
        ))

        self.botao_ignorar = QPushButton("Ignorar e ler as imagens")
        self.botao_ignorar.setCursor(Qt.PointingHandCursor)
        self.botao_ignorar.setStyleSheet(estilo.estilo_botao(principal=False))
        self.botao_ignorar.clicked.connect(self._ignorar)
        self.porque_ignorar = _explicacao("")
        linha.addLayout(_coluna_da_escolha(self.botao_ignorar, self.porque_ignorar))

        return linha

    def mostrar(self, ficha, paginas):
        self._ficha = ficha
        self._paginas = paginas

        letras = f"{ficha.letras_na_camada_de_texto:,}".replace(",", ".")
        pagina_ou_paginas = "página" if ficha.paginas == 1 else "páginas"
        self.legenda.setText(
            f"{ficha.caminho.name} — {ficha.paginas} {pagina_ou_paginas}, "
            f"{letras} letras"
        )
        self.amostra.setPlainText(
            "\n".join(primeiras_linhas(paginas, LINHAS_DA_AMOSTRA))
        )
        # A estimativa existe para a escolha não ser feita no escuro: ignorar um
        # documento de cem páginas custa dois minutos e meio, e é justo saber
        # disso antes de clicar.
        self.porque_ignorar.setText(
            "Se o texto acima está estranho ou ilegível. Leva "
            f"{tempo_estimado(ficha.paginas)}."
        )

    def _aproveitar(self):
        if self._ficha is not None:
            self._ao_aproveitar(self._ficha, self._paginas)

    def _ignorar(self):
        if self._ficha is not None:
            self._ao_ignorar(self._ficha)


def _coluna_da_escolha(botao, explicacao):
    coluna = QVBoxLayout()
    coluna.setSpacing(estilo.ESPACO_2)
    coluna.addWidget(botao)
    coluna.addWidget(
        explicacao if isinstance(explicacao, QLabel) else _explicacao(explicacao)
    )
    coluna.addStretch()
    return coluna


def _explicacao(texto):
    rotulo = QLabel(texto)
    rotulo.setWordWrap(True)
    rotulo.setAlignment(Qt.AlignHCenter)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px;"
        f"color: {estilo.COR_TEXTO_SECUNDARIO};"
    )
    return rotulo

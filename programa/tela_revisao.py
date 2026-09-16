"""A tela de revisão do Anonimizar: o texto já mascarado, com cada troca destacada.

É a tela que dá razão ao módulo. Ela aparece sempre, com CPF ou sem (regra
RN-7), e aqui não se digita: o texto é só de leitura (RN-8). Corrigir a leitura
é trabalho da conferência do OCR.

Segue os rascunhos aprovados mockups/anonimizar/01-revisar-antes-de-salvar.html
e 08-escolher-e-salvar.html. Duas coisas mudaram depois deles, na conferência
da etapa 2 e registradas em mockups/sistema-de-design.md, em 16/09/2026: o
rótulo na tela, que era "forma CPF válido" e virou "CPF válido", e a cor dele,
que é o vermelho de letra.

Nesta etapa a tela mostra o texto e a contagem. A lista do que o programa achou,
ao lado, e o salvar entram nas etapas seguintes.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import cpf
import estilo

AVISO_SEM_CPF = "Nenhum CPF encontrado neste texto"


class TelaRevisao(QWidget):
    # O aviso de "nenhum CPF" tem largura fixa, e a altura dele é calculada a
    # partir dela: frase com quebra de linha dentro de caixa de largura limitada
    # sai cortada no Qt, e ninguém percebe que faltou pedaço.
    LARGURA_DO_AVISO = 620
    LARGURA_DO_TEXTO_DO_AVISO = 580

    def __init__(self, ao_anonimizar_outro):
        super().__init__()
        self._ocorrencias = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addLayout(self._montar_cabecalho())
        self.legenda = QLabel()
        self.legenda.setWordWrap(True)
        self.legenda.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )
        layout.addWidget(self.legenda)
        layout.addSpacing(estilo.ESPACO_3)

        self.aviso_sem_cpf = self._montar_aviso_sem_cpf()
        layout.addWidget(self.aviso_sem_cpf)
        layout.addSpacing(estilo.ESPACO_2)

        layout.addLayout(self._montar_chave_de_cores())
        layout.addSpacing(estilo.ESPACO_2)

        self.texto = QTextEdit()
        self.texto.setReadOnly(True)
        # Sem quebra automática: a tabela do documento só continua parecendo
        # tabela se cada linha ficar inteira, do jeito que está no arquivo.
        self.texto.setLineWrapMode(QTextEdit.NoWrap)
        self.texto.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {estilo.COR_FUNDO_ELEVADO};
                border: 1px solid {estilo.COR_BORDA};
                border-radius: {estilo.RAIO}px;
                padding: {estilo.ESPACO_3}px;
                color: {estilo.COR_TEXTO};
            }}
            """
        )
        # A borda azul do editor da conferência do OCR não entra aqui de
        # propósito: lá ela dizia "dá para digitar"; aqui não dá (RN-8).
        self.texto.setFont(QFont("Cascadia Mono", 11))
        layout.addWidget(self.texto, stretch=1)
        layout.addSpacing(estilo.ESPACO_3)

        rodape = QHBoxLayout()
        rodape.setSpacing(estilo.ESPACO_3)
        botao_outro = QPushButton("Anonimizar outro documento")
        botao_outro.setCursor(Qt.PointingHandCursor)
        botao_outro.setStyleSheet(estilo.estilo_botao(principal=False))
        botao_outro.clicked.connect(ao_anonimizar_outro)
        aviso = QLabel("Nada é gravado até você salvar.")
        aviso.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )
        rodape.addWidget(botao_outro)
        rodape.addWidget(aviso, stretch=1)
        layout.addLayout(rodape)

    # ------------------------------------------------------------- montagem

    def _montar_cabecalho(self):
        linha = QHBoxLayout()
        linha.setSpacing(estilo.ESPACO_3)

        titulo = QLabel("Revisar antes de salvar")
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_GRANDE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO};"
        )
        self.selo_mascarados = _selo()
        # Cada selo na cor do que ele conta, para bater com o texto ao lado.
        self.selo_validos = _selo(cor=estilo.COR_ERRO_TEXTO)
        self.selo_suspeitos = _selo(cor=estilo.COR_ALERTA)

        linha.addWidget(titulo)
        linha.addWidget(self.selo_mascarados)
        linha.addWidget(self.selo_validos)
        linha.addWidget(self.selo_suspeitos)
        linha.addStretch()
        return linha

    def _montar_chave_de_cores(self):
        linha = QHBoxLayout()
        linha.setSpacing(estilo.ESPACO_4)
        self.chave_valido = _amostra_da_chave(
            "CPF válido", ondulado=False, cor=estilo.COR_ERRO_TEXTO)
        self.chave_suspeito = _amostra_da_chave(
            "suspeito", ondulado=True, cor=estilo.COR_ALERTA)
        linha.addWidget(self.chave_valido)
        linha.addWidget(self.chave_suspeito)
        linha.addStretch()
        return linha

    def _montar_aviso_sem_cpf(self):
        caixa = QFrame()
        caixa.setObjectName("aviso_sem_cpf")
        caixa.setFixedWidth(self.LARGURA_DO_AVISO)
        caixa.setStyleSheet(
            f"""
            QFrame#aviso_sem_cpf {{
                background-color: rgba(59, 110, 165, 26);
                border-left: 4px solid {estilo.COR_DESTAQUE};
                border-radius: {estilo.RAIO}px;
            }}
            """
        )
        dentro = QVBoxLayout(caixa)
        dentro.setContentsMargins(estilo.ESPACO_3, estilo.ESPACO_2,
                                  estilo.ESPACO_3, estilo.ESPACO_2)
        dentro.setSpacing(estilo.ESPACO_1)

        titulo = QLabel(AVISO_SEM_CPF)
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO}; border: none; background: transparent;"
        )
        # Azul, e não verde: "nenhum CPF encontrado" não garante que está tudo
        # certo. Num texto vindo do OCR pode ser um CPF que a leitura estragou
        # demais para ser reconhecido. O aviso informa, não tranquiliza.
        self.explicacao_sem_cpf = QLabel(
            "O programa procurou nos quatro formatos combinados e nos números "
            "com letra ou espaço no meio. O texto está como veio do arquivo."
        )
        self.explicacao_sem_cpf.setWordWrap(True)
        self.explicacao_sem_cpf.setFixedWidth(self.LARGURA_DO_TEXTO_DO_AVISO)
        self.explicacao_sem_cpf.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
            "border: none; background: transparent;"
        )
        self.explicacao_sem_cpf.setMinimumHeight(
            self.explicacao_sem_cpf.heightForWidth(self.LARGURA_DO_TEXTO_DO_AVISO)
        )
        dentro.addWidget(titulo)
        dentro.addWidget(self.explicacao_sem_cpf)
        caixa.setVisible(False)
        return caixa

    # ------------------------------------------------------------------ uso

    def mostrar(self, nome_da_origem, texto, ocorrencias):
        self._ocorrencias = list(ocorrencias)
        self.legenda.setText(
            f"{nome_da_origem} — arquivo de texto. Aqui não se digita: só se "
            "mascara e se desfaz a máscara."
        )
        self._escrever(texto)
        self._atualizar_contagem()

    def texto_mascarado(self):
        """O texto como ele está na tela - o que vai para o arquivo."""
        return self.texto.toPlainText()

    def esquecer(self):
        self._ocorrencias = []
        self.texto.clear()

    # -------------------------------------------------------------- por dentro

    def _escrever(self, texto):
        """Põe o texto mascarado na tela, com cada troca destacada no lugar dela.

        O destaque é desenhado sobre as mesmas posições do texto original,
        porque a máscara não muda o tamanho de nada (regra RN-6).
        """
        mascarado = cpf.aplicar(texto, self._ocorrencias)
        self.texto.setPlainText(mascarado)

        cursor = self.texto.textCursor()
        # O Qt conta o texto de um jeito e o Python de outro: símbolo fora do
        # comum - um emoji num título, um sinal colado de outro lugar - ocupa
        # duas casas na conta do Qt e uma na do Python. Sem converter, o
        # destaque escorrega uma casa por símbolo desses e sai de cima do
        # número, que então aparece na tela sem marca nenhuma.
        for ocorrencia in sorted(self._ocorrencias, key=lambda o: o.inicio):
            if ocorrencia.situacao != cpf.MASCARADO:
                continue
            cursor.setPosition(_posicao_no_qt(texto, ocorrencia.inicio))
            cursor.setPosition(
                _posicao_no_qt(texto, ocorrencia.fim), QTextCursor.KeepAnchor)
            cursor.setCharFormat(_formato(ocorrencia))
        # O cursor volta ao começo para a tela abrir no alto do documento.
        self.texto.moveCursor(QTextCursor.Start)

    def _atualizar_contagem(self):
        mascarados = [o for o in self._ocorrencias if o.situacao == cpf.MASCARADO]
        suspeitos = [o for o in mascarados if o.suspeito]
        validos = [o for o in mascarados if o.tipo == cpf.PASSA_NA_CONTA]

        tem_cpf = bool(self._ocorrencias)
        self.aviso_sem_cpf.setVisible(not tem_cpf)

        self.selo_mascarados.setText(
            f"{len(mascarados)} números mascarados" if len(mascarados) != 1
            else "1 número mascarado"
        )
        self.selo_mascarados.setVisible(tem_cpf)
        self.selo_validos.setText(
            f"{len(validos)} CPFs válidos" if len(validos) != 1
            else "1 CPF válido"
        )
        self.selo_validos.setVisible(bool(validos))
        self.selo_suspeitos.setText(
            f"{len(suspeitos)} suspeitos" if len(suspeitos) != 1
            else "1 suspeito"
        )
        self.selo_suspeitos.setVisible(bool(suspeitos))


def _posicao_no_qt(texto, indice):
    """A mesma posição, contada do jeito do Qt.

    Cada símbolo fora do comum (emoji, por exemplo) vale duas casas lá e uma
    aqui, então a conta é a posição mais quantos desses vieram antes dela.
    """
    return indice + sum(1 for letra in texto[:indice] if ord(letra) > 0xFFFF)


def _formato(ocorrencia):
    """A cor e o traço de cada tipo (sistema de design, 16/09/2026).

    Vermelho e traço reto para o número com forma de CPF válido; amarelo e
    traço ondulado para o suspeito, como o corretor de texto marca "confira
    isto". As duas coisas juntas, e não só a cor: o traço é o que separa os
    dois para quem não distingue bem uma cor da outra.

    Os dois marcados no mesmo amarelo, como ficou entre 14 e 16/09/2026,
    deixavam a diferença sutil demais na tela - e é o número que passa na conta,
    o mais perigoso, que precisa saltar aos olhos.
    """
    formato = QTextCharFormat()
    cor = QColor(estilo.COR_ALERTA if ocorrencia.suspeito else estilo.COR_ERRO_TEXTO)
    formato.setForeground(cor)
    formato.setUnderlineColor(cor)
    formato.setUnderlineStyle(
        QTextCharFormat.WaveUnderline if ocorrencia.suspeito
        else QTextCharFormat.SingleUnderline
    )
    return formato


def _selo(cor=None):
    rotulo = QLabel()
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px;"
        f"color: {cor or estilo.COR_TEXTO_SECUNDARIO};"
        f"background-color: {estilo.COR_FUNDO_ELEVADO};"
        f"border: 1px solid {estilo.COR_BORDA};"
        "border-radius: 10px; padding: 2px 10px;"
    )
    rotulo.setVisible(False)
    return rotulo


def _amostra_da_chave(nome, ondulado, cor):
    """Um pedacinho "***" com o traço do tipo, e o nome dele ao lado.

    É um pedaço de texto, e não um rótulo comum, porque o traço ondulado só
    existe no texto do Qt: por folha de estilo, os dois tipos sairiam com o
    mesmo traço reto - e o traço é justamente o que separa um do outro para
    quem não distingue bem as cores.
    """
    amostra = QTextEdit()
    amostra.setReadOnly(True)
    amostra.setFrameShape(QFrame.NoFrame)
    amostra.setFixedHeight(22)
    amostra.setFixedWidth(200)
    amostra.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    amostra.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    amostra.setStyleSheet("background: transparent; border: none;")
    amostra.setFont(QFont("Segoe UI", 8))

    marcado = QTextCharFormat()
    marcado.setForeground(QColor(cor))
    marcado.setUnderlineColor(QColor(cor))
    marcado.setUnderlineStyle(
        QTextCharFormat.WaveUnderline if ondulado
        else QTextCharFormat.SingleUnderline
    )
    comum = QTextCharFormat()
    comum.setForeground(QColor(estilo.COR_TEXTO_SECUNDARIO))

    cursor = amostra.textCursor()
    cursor.insertText("***", marcado)
    cursor.insertText(f"  {nome}", comum)
    return amostra

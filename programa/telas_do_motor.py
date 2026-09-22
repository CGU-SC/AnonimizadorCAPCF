"""O que aparece quando falta o motor de leitura nesta máquina.

Segue o rascunho aprovado mockups/ocr/10-falta-o-motor.html: o aviso no alto
do painel, e a tela cheia de quem escolheu um documento escaneado mesmo assim.

As duas mostram as mesmas três saídas - instalar, conferir de novo, apontar a
pasta - porque o problema é o mesmo, e quem ignorou o aviso do alto precisa
encontrar na tela cheia exatamente o que ele oferecia (regra RN-19).
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import estilo

SEM_INSTALADOR = (
    "<b>O instalador não está nesta máquina.</b> Peça à TI da UFSC para "
    "instalar o Tesseract com o pacote de português. Se ele já estiver instalado "
    "em outra pasta, use \"apontar a pasta\"."
)

SEM_PORTUGUES = (
    "Peça à TI para instalar de novo, marcando o português na lista de idiomas."
)

TITULO_SEM_MOTOR = "O motor de leitura não foi encontrado nesta máquina"
TITULO_SEM_PORTUGUES = "O motor de leitura está sem o pacote de português"


class _SaidasDoMotor:
    """Os três botões e as duas frases que mudam, iguais nas duas telas.

    Ficam numa peça só para que a tela cheia nunca ofereça menos, ou diferente,
    do que o aviso do alto oferece.
    """

    def __init__(self, ao_instalar, ao_conferir, ao_apontar, largura_do_texto=None,
                 pequeno=False):
        self._largura_do_texto = largura_do_texto

        # O botão de instalar aparece apagado quando não há instalador, e não
        # some: é assim que a pessoa entende que instalar é possível, só que o
        # instalador não veio junto com o programa.
        self.botao_instalar = _botao("Instalar agora", ao_instalar,
                                     principal=True, pequeno=pequeno)
        self.botao_conferir = _botao("Conferir de novo", ao_conferir, pequeno=pequeno)
        self.botao_apontar = _botao("Apontar a pasta…", ao_apontar, pequeno=pequeno)

        self.linha_sem_instalador = self._frase(estilo.COR_TEXTO)
        self.linha_sem_instalador.setText(SEM_INSTALADOR)
        self.linha_sem_instalador.setVisible(False)

        self.linha_sem_portugues = self._frase(estilo.COR_TEXTO)
        self.linha_sem_portugues.setText(SEM_PORTUGUES)
        self.linha_sem_portugues.setVisible(False)

        # A resposta ao último botão clicado. Sem ela, clicar em "conferir de
        # novo" antes de a instalação terminar não mudaria nada na tela, e a
        # pessoa não saberia se o botão pegou.
        self.recado = self._frase(estilo.COR_TEXTO_SECUNDARIO)
        self.recado.setVisible(False)

    def _frase(self, cor):
        rotulo = QLabel()
        rotulo.setWordWrap(True)
        rotulo.setTextFormat(Qt.RichText)
        if self._largura_do_texto:
            rotulo.setFixedWidth(self._largura_do_texto)
        _pintar(rotulo, cor)
        return rotulo

    def linha_de_botoes(self):
        linha = QHBoxLayout()
        linha.setSpacing(estilo.ESPACO_2)
        linha.addWidget(self.botao_instalar)
        linha.addWidget(self.botao_conferir)
        linha.addWidget(self.botao_apontar)
        return linha

    def atualizar(self, tem_instalador, sem_portugues=False):
        self.botao_instalar.setEnabled(tem_instalador)
        self.botao_instalar.setCursor(
            Qt.PointingHandCursor if tem_instalador else Qt.ArrowCursor
        )
        self.linha_sem_instalador.setVisible(not tem_instalador)
        # Sem instalador, a frase de cima já pede à TI o Tesseract com o
        # pacote de português; repetir o pedido em outra frase só alongaria o
        # aviso.
        self.linha_sem_portugues.setVisible(sem_portugues and tem_instalador)
        self._acertar_altura(self.linha_sem_instalador)
        self._acertar_altura(self.linha_sem_portugues)

    def dar_recado(self, texto, erro=False):
        _pintar(self.recado, estilo.COR_ERRO if erro else estilo.COR_TEXTO_SECUNDARIO)
        # O recado pode trazer o caminho de uma pasta, escrito pela pessoa.
        self.recado.setText(_sem_marcacao(texto))
        self.recado.setVisible(True)
        self._acertar_altura(self.recado)

    def apagar_recado(self):
        self.recado.clear()
        self.recado.setVisible(False)

    def _acertar_altura(self, rotulo):
        # Frase de largura fixa com quebra de linha sai cortada no Qt se a
        # altura não for calculada a partir da largura - foi o que aconteceu na
        # caixa de erro da etapa 1.
        if self._largura_do_texto:
            rotulo.setMinimumHeight(rotulo.heightForWidth(self._largura_do_texto))


class AvisoDoMotor(QFrame):
    """A faixa no alto do painel, que já traz o que fazer a respeito."""

    def __init__(self, ao_instalar, ao_conferir, ao_apontar, texto=None):
        super().__init__()
        self.setObjectName("aviso_do_motor")
        self.setStyleSheet(
            f"""
            QFrame#aviso_do_motor {{
                border: 1px solid {estilo.COR_ALERTA};
                background-color: rgba(217, 164, 65, 26);
                border-radius: {estilo.RAIO}px;
            }}
            """
        )
        self.saidas = _SaidasDoMotor(ao_instalar, ao_conferir, ao_apontar,
                                     pequeno=True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(estilo.ESPACO_3, estilo.ESPACO_3,
                                  estilo.ESPACO_3, estilo.ESPACO_3)
        layout.setSpacing(estilo.ESPACO_1)

        self.titulo = titulo = QLabel(TITULO_SEM_MOTOR)
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 600;"
            f"color: {estilo.COR_ALERTA}; border: none; background: transparent;"
        )

        # No Anonimizar a frase é mais curta: logo abaixo do aviso vem a lista
        # do que dá para anonimizar agora, e ela diz o resto (rascunho 08,
        # estado 2).
        texto = QLabel(texto or (
            "Documento escaneado não vai funcionar até isto ser resolvido. "
            "Documento que já tem texto por dentro continua funcionando "
            "normalmente."
        ))
        texto.setWordWrap(True)
        _pintar(texto, estilo.COR_TEXTO_SECUNDARIO)

        layout.addWidget(titulo)
        layout.addWidget(texto)
        layout.addWidget(self.saidas.linha_sem_instalador)
        layout.addWidget(self.saidas.linha_sem_portugues)
        layout.addWidget(self.saidas.recado)
        layout.addSpacing(estilo.ESPACO_2)
        linha = self.saidas.linha_de_botoes()
        linha.addStretch()
        layout.addLayout(linha)

        self.setVisible(False)

    def mostrar(self, tem_instalador, sem_portugues=False):
        self.titulo.setText(TITULO_SEM_PORTUGUES if sem_portugues else TITULO_SEM_MOTOR)
        self.saidas.atualizar(tem_instalador, sem_portugues)
        self.setVisible(True)

    def esconder(self):
        self.saidas.apagar_recado()
        self.setVisible(False)


class TelaSemMotor(QWidget):
    """A tela cheia de quem ignorou o aviso e escolheu um documento escaneado."""

    # Largura fixa pelo mesmo motivo da caixa de erro: sem ela, a frase longa
    # sai cortada.
    LARGURA_DA_CAIXA = 480
    LARGURA_DO_TEXTO = 420

    def __init__(self, ao_instalar, ao_conferir, ao_apontar, ao_escolher_outro,
                 rotulo_de_outro="Escolher outro documento", lembrete=None):
        super().__init__()
        # O lembrete é a frase a mais do Anonimizar: ele diz o que ainda dá para
        # anonimizar sem o motor, para quem chegou aqui não concluir que o
        # módulo inteiro parou (rascunho 08, estado 2b).
        self._lembrete = lembrete
        self.saidas = _SaidasDoMotor(
            ao_instalar, ao_conferir, ao_apontar,
            largura_do_texto=self.LARGURA_DO_TEXTO,
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        caixa = QFrame()
        caixa.setObjectName("caixa_sem_motor")
        caixa.setFixedWidth(self.LARGURA_DA_CAIXA)
        caixa.setStyleSheet(
            f"""
            QFrame#caixa_sem_motor {{
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

        titulo = QLabel("Este documento precisa do motor de leitura")
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO}; border: none; background: transparent;"
        )

        self.explicacao = QLabel()
        self.explicacao.setWordWrap(True)
        self.explicacao.setTextFormat(Qt.RichText)
        self.explicacao.setFixedWidth(self.LARGURA_DO_TEXTO)
        _pintar(self.explicacao, estilo.COR_TEXTO_SECUNDARIO)

        caixa_layout.addWidget(titulo)
        caixa_layout.addWidget(self.explicacao)
        caixa_layout.addWidget(self.saidas.linha_sem_instalador)
        caixa_layout.addWidget(self.saidas.linha_sem_portugues)
        caixa_layout.addWidget(self.saidas.recado)

        linha = QHBoxLayout()
        linha.addStretch()
        linha.addLayout(self.saidas.linha_de_botoes())
        linha.addStretch()

        linha_outro = QHBoxLayout()
        linha_outro.addStretch()
        linha_outro.addWidget(_botao(rotulo_de_outro, ao_escolher_outro))
        linha_outro.addStretch()

        layout.addWidget(caixa, alignment=Qt.AlignCenter)
        layout.addSpacing(estilo.ESPACO_4)
        layout.addLayout(linha)
        layout.addSpacing(estilo.ESPACO_3)
        layout.addLayout(linha_outro)

    def mostrar(self, ficha, tem_instalador, sem_portugues=False):
        nome = _sem_marcacao(ficha.caminho.name)
        motivo = (
            "está instalado nesta máquina sem o pacote de português"
            if sem_portugues else "não foi encontrado nesta máquina"
        )
        if ficha.tem_camada_de_texto:
            # Chega aqui quem mandou ignorar o texto que já estava no documento.
            # Dizer que ele "não tem texto por dentro" seria mentir - e o texto
            # dele continua podendo ser aproveitado sem o motor.
            frase = (
                f"Ler o <b>{nome}</b> como imagem precisa do Tesseract, que "
                f"{motivo}. O texto que já está por dentro dele continua podendo "
                "ser aproveitado sem o motor."
            )
        else:
            frase = (
                f"O <b>{nome}</b> não tem texto por dentro — ele só pode ser "
                f"lido pelo Tesseract, que {motivo}."
            )
            if self._lembrete:
                frase += f" {self._lembrete}"
        self.explicacao.setText(frase)
        self.explicacao.setMinimumHeight(
            self.explicacao.heightForWidth(self.LARGURA_DO_TEXTO)
        )
        self.saidas.apagar_recado()
        self.saidas.atualizar(tem_instalador, sem_portugues)


def _pintar(rotulo, cor):
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px; color: {cor};"
        "border: none; background: transparent;"
    )


def _sem_marcacao(texto):
    """O nome do arquivo entra numa frase com negrito, que o Qt lê como HTML.

    Um arquivo chamado "a<b>c.pdf" apareceria com um pedaço sumido. Trocar os
    sinais é o que faz o nome sair exatamente como está na pasta.
    """
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _botao(texto, ao_clicar, principal=False, pequeno=False):
    botao = QPushButton(texto)
    botao.setCursor(Qt.PointingHandCursor)
    botao.setStyleSheet(estilo.estilo_botao(principal=principal, pequeno=pequeno))
    botao.clicked.connect(ao_clicar)
    return botao

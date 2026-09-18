"""As telas do fim do Anonimizar: onde salvar, e o arquivo gravado.

Segue o rascunho aprovado mockups/anonimizar/08-escolher-e-salvar.html (estados
6 a 10), que por sua vez parte do salvar do "Gerar OCR". O que muda aqui é o que
a spec 003 acrescenta: o lembrete dos números liberados antes de gravar (RN-11),
a recusa de gravar por cima do arquivo de origem (RN-14) e o lembrete, na tela
de sucesso, de que a origem continua na pasta com os CPFs inteiros.

A pergunta de escrever por cima é a mesma do "Gerar OCR", reaproveitada: é o
mesmo risco, e duas perguntas diferentes para a mesma coisa seria pior.
"""
import html
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import arquivo_md
import estilo
from telas_de_salvar import escolher_onde_salvar

LARGURA_DO_AVISO = 620
LARGURA_DO_TEXTO_DO_AVISO = 560


class TelaSalvarSemCpf(QWidget):
    """O caminho já preenchido, a contagem do que está saindo, e o lembrete."""

    def __init__(self, ao_salvar, ao_voltar):
        super().__init__()
        self._ao_salvar = ao_salvar
        self._pasta_sugerida = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(_titulo("Onde salvar o texto mascarado"))
        self.legenda = _legenda("")
        layout.addWidget(self.legenda)
        layout.addSpacing(estilo.ESPACO_4)

        rotulo = QLabel("CAMINHO DO ARQUIVO")
        rotulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 700;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; letter-spacing: 1px;"
        )
        layout.addWidget(rotulo)
        layout.addSpacing(estilo.ESPACO_1)

        linha = QHBoxLayout()
        linha.setSpacing(estilo.ESPACO_2)
        self.campo = QLineEdit()
        self.campo.returnPressed.connect(self._salvar)
        linha.addWidget(self.campo, stretch=1)
        linha.addWidget(_botao("Escolher pasta…", self._escolher_pasta, principal=False))
        layout.addLayout(linha)
        layout.addSpacing(estilo.ESPACO_3)

        self.contagem = _legenda("")
        self.contagem.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; color: {estilo.COR_TEXTO};"
        )
        layout.addWidget(self.contagem)
        # Nada deste quadro entra no arquivo: lá vai só o texto (RN-12).
        layout.addWidget(_legenda(
            "O arquivo leva só o texto do documento, com as máscaras no lugar."))
        layout.addSpacing(estilo.ESPACO_3)

        self.aviso_dos_liberados = _CaixaDeAviso()
        layout.addWidget(self.aviso_dos_liberados)

        self.caixa_do_problema = _CaixaDeProblema()
        self.problema = self.caixa_do_problema.explicacao
        layout.addWidget(self.caixa_do_problema)
        layout.addStretch()

        acoes = QHBoxLayout()
        acoes.setSpacing(estilo.ESPACO_3)
        self.botao_salvar = _botao("Salvar", self._salvar, principal=True)
        self.botao_voltar = _botao("Voltar à revisão", ao_voltar, principal=False)
        acoes.addWidget(self.botao_salvar)
        acoes.addWidget(self.botao_voltar)
        acoes.addStretch()
        layout.addLayout(acoes)
        self._pintar_campo(erro=False)

    # ------------------------------------------------------------------ uso

    def mostrar(self, caminho, nome_da_origem, resumo, liberados):
        """Prepara a tela com o caminho sugerido e o que está saindo.

        `liberados` são os números que passam na conta e a pessoa soltou. Com
        algum deles, o aviso da RN-11 aparece **antes** de gravar, e não numa
        caixa depois do clique: ela lê o número antes de decidir.
        """
        self.legenda.setText(f"{nome_da_origem} — texto revisado")
        self.campo.setText(str(caminho))
        # A pasta sugerida fica guardada para quem digitar só um nome.
        self._pasta_sugerida = Path(caminho).parent
        self.contagem.setText(resumo)
        self.caixa_do_problema.setVisible(False)
        self._pintar_campo(erro=False)

        self.aviso_dos_liberados.mostrar(liberados)
        # Com números indo inteiros, o botão que não expõe nada é o de destaque,
        # e o de salvar passa a dizer o que ele faz de verdade.
        tem_liberados = bool(liberados)
        self.botao_salvar.setText(
            "Salvar assim mesmo" if tem_liberados else "Salvar")
        self.botao_salvar.setStyleSheet(estilo.estilo_botao(principal=not tem_liberados))
        self.botao_voltar.setStyleSheet(estilo.estilo_botao(principal=tem_liberados))

    def avisar(self, titulo, frase):
        """Um problema com o caminho escolhido, sem sair da tela nem perder nada."""
        self.caixa_do_problema.mostrar(titulo, frase)
        self._pintar_campo(erro=True)

    # -------------------------------------------------------------- por dentro

    def _pintar_campo(self, erro):
        borda = estilo.COR_ERRO if erro else estilo.COR_DESTAQUE
        self.campo.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {estilo.COR_FUNDO_ELEVADO};
                border: 1px solid {borda};
                border-radius: {estilo.RAIO}px;
                padding: 8px {estilo.ESPACO_3}px;
                font-family: {estilo.FONTE_MONO};
                font-size: {estilo.TEXTO_PEQUENO}px;
                color: {estilo.COR_TEXTO};
            }}
            """
        )

    def _escolher_pasta(self):
        escolhido = escolher_onde_salvar(self, self.campo.text())
        if escolhido:
            self.campo.setText(escolhido)

    def _salvar(self):
        # A conferência do caminho é a mesma dos dois módulos, e mora no
        # `arquivo_md`; aqui ficam só as frases desta tela.
        caminho, problema = arquivo_md.conferir_destino(
            self.campo.text(), self._pasta_sugerida)
        if problema == arquivo_md.FALTA_O_CAMINHO:
            self.avisar("Falta dizer onde salvar",
                        "Escreva o caminho do arquivo, ou escolha a pasta pelo "
                        "botão \"Escolher pasta…\".")
            return
        if problema == arquivo_md.FALTA_A_PASTA:
            self.avisar("Falta a pasta",
                        "Escreva o caminho completo, com a pasta em que o "
                        "arquivo vai ser gravado.")
            return
        if problema == arquivo_md.PASTA_NAO_EXISTE:
            self.avisar(
                "Essa pasta não existe",
                f"Não há a pasta {caminho.parent} nesta "
                "máquina. Escolha outra pelo botão \"Escolher pasta…\" — nada "
                "foi gravado.")
            return
        self._ao_salvar(caminho)


class _CaixaDeAviso(QFrame):
    """O lembrete dos números que passam na conta e foram liberados (RN-11).

    Amarelo e com ⚠, como o aviso de CPFs inteiros do "Gerar OCR": é o mesmo
    recado, na mesma cor que marca esses números na revisão.
    """

    def __init__(self):
        super().__init__()
        self.setObjectName("aviso")
        self.setFixedWidth(LARGURA_DO_AVISO)
        self.setStyleSheet(
            f"""
            QFrame#aviso {{
                background-color: rgba(217, 164, 65, 31);
                border-left: 4px solid {estilo.COR_ALERTA};
                border-radius: {estilo.RAIO}px;
            }}
            QFrame#aviso QLabel {{ border: none; background: transparent; }}
            """
        )
        dentro = QVBoxLayout(self)
        dentro.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_3,
                                  estilo.ESPACO_4, estilo.ESPACO_3)
        dentro.setSpacing(estilo.ESPACO_1)

        self.titulo = QLabel()
        self.titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
            f"color: {estilo.COR_ALERTA};"
        )
        self.explicacao = QLabel(
            "Você liberou estes números na revisão. Eles quase certamente são o "
            "CPF de alguém.")
        self.explicacao.setWordWrap(True)
        self.explicacao.setFixedWidth(LARGURA_DO_TEXTO_DO_AVISO)
        self.explicacao.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; color: {estilo.COR_TEXTO};"
        )
        # Os números entram e saem conforme a pessoa libera e mascara de novo,
        # então eles vivem num pedaço à parte, refeito a cada vez.
        self.numeros = QVBoxLayout()
        self.numeros.setSpacing(estilo.ESPACO_1)
        self.saida = QLabel(
            "Para mascarar de novo, volte à revisão: eles estão na lista, com o "
            "botão \"Mascarar de novo\".")
        self.saida.setWordWrap(True)
        self.saida.setFixedWidth(LARGURA_DO_TEXTO_DO_AVISO)
        self.saida.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )
        dentro.addWidget(self.titulo)
        dentro.addWidget(self.explicacao)
        dentro.addSpacing(estilo.ESPACO_1)
        dentro.addLayout(self.numeros)
        dentro.addSpacing(estilo.ESPACO_1)
        dentro.addWidget(self.saida)
        self.setVisible(False)

    def mostrar(self, liberados):
        self._limpar()
        if not liberados:
            self.setVisible(False)
            return
        quantos = len(liberados)
        self.titulo.setText(
            f"⚠ {quantos} números com CPF válido vão inteiros para o arquivo"
            if quantos != 1
            else "⚠ 1 número com CPF válido vai inteiro para o arquivo"
        )
        for liberado in liberados:
            self.numeros.addWidget(_linha_do_liberado(liberado))
        for rotulo in (self.explicacao, self.saida):
            rotulo.ensurePolished()
            rotulo.setMinimumHeight(
                rotulo.heightForWidth(LARGURA_DO_TEXTO_DO_AVISO))
        self.setVisible(True)

    def texto_dos_numeros(self):
        """Os números que a caixa está mostrando - para conferir por teste."""
        return [self.numeros.itemAt(i).widget().text()
                for i in range(self.numeros.count())]

    def _limpar(self):
        while self.numeros.count():
            item = self.numeros.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()


def _linha_do_liberado(liberado):
    """Um número da caixa: o número, o tipo dele, e o que vem antes no texto.

    O contexto está ali porque o número sozinho não diz de quem ele é - e é
    olhando o nome ao lado que a pessoa lembra por que liberou aquele.
    """
    # A quebra de linha dentro do número vira uma seta: a linha do aviso tem uma
    # altura só, e sem a seta o número apareceria partido sem explicação.
    numero = html.escape(liberado.original.replace("\n", " ↵ "))
    linha = QLabel(
        f"<span style='font-family: {estilo.FONTE_MONO}; "
        f"color: {estilo.COR_TEXTO};'>{numero}</span>"
        f"&nbsp;&nbsp;<span style='color: {estilo.COR_ERRO_TEXTO};'>"
        f"{html.escape(liberado.etiqueta)}</span>"
        f"&nbsp;&nbsp;<span style='color: {estilo.COR_TEXTO_SECUNDARIO};'>"
        f"{html.escape(liberado.contexto)}</span>"
    )
    linha.setTextFormat(Qt.RichText)
    linha.setStyleSheet(f"font-size: {estilo.TEXTO_PEQUENO}px;")
    # Número, etiqueta e contexto juntos passam da largura da caixa quando o
    # nome ao lado é comprido. Sem quebrar a linha e sem calcular a altura a
    # partir dela, o fim da frase sai para fora da borda sem nada acusar.
    linha.setWordWrap(True)
    linha.setFixedWidth(LARGURA_DO_TEXTO_DO_AVISO)
    linha.ensurePolished()
    linha.setMinimumHeight(linha.heightForWidth(LARGURA_DO_TEXTO_DO_AVISO))
    return linha


class _CaixaDeProblema(QFrame):
    """O que impediu de gravar: em vermelho, na mesma tela, sem perder nada."""

    def __init__(self):
        super().__init__()
        self.setObjectName("problema")
        self.setFixedWidth(LARGURA_DO_AVISO)
        self.setStyleSheet(
            f"""
            QFrame#problema {{
                background-color: rgba(217, 83, 79, 26);
                border-left: 4px solid {estilo.COR_ERRO};
                border-radius: {estilo.RAIO}px;
            }}
            QFrame#problema QLabel {{ border: none; background: transparent; }}
            """
        )
        dentro = QVBoxLayout(self)
        dentro.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_3,
                                  estilo.ESPACO_4, estilo.ESPACO_3)
        dentro.setSpacing(estilo.ESPACO_1)

        self.titulo = QLabel()
        self.titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO};"
        )
        self.explicacao = QLabel()
        self.explicacao.setWordWrap(True)
        self.explicacao.setFixedWidth(LARGURA_DO_TEXTO_DO_AVISO)
        self.explicacao.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )
        dentro.addWidget(self.titulo)
        dentro.addWidget(self.explicacao)
        self.setVisible(False)

    def mostrar(self, titulo, frase):
        self.titulo.setText(titulo)
        self.explicacao.setText(frase)
        # A frase muda de tamanho conforme o caminho: a altura é recalculada a
        # cada vez, senão o fim dela sai para fora da borda sem nada acusar.
        self.explicacao.ensurePolished()
        self.explicacao.setMinimumHeight(
            self.explicacao.heightForWidth(LARGURA_DO_TEXTO_DO_AVISO))
        self.setVisible(True)


class TelaGravadoSemCpf(QWidget):
    """Onde o arquivo ficou, e o lembrete de que a origem continua na pasta."""

    LARGURA_DO_LEMBRETE = 620

    def __init__(self, ao_anonimizar_outro):
        super().__init__()
        self._caminho = None

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(estilo.ESPACO_2)

        icone = QLabel("✓")
        icone.setAlignment(Qt.AlignCenter)
        icone.setStyleSheet(f"font-size: 40px; color: {estilo.COR_SUCESSO};")
        layout.addWidget(icone)

        self.titulo = _titulo("Arquivo gravado, sem CPF")
        self.titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.titulo)

        self.contagem = _legenda("")
        self.contagem.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.contagem)
        layout.addSpacing(estilo.ESPACO_3)

        self.caminho = QLabel()
        self.caminho.setAlignment(Qt.AlignCenter)
        # O caminho pode ser selecionado com o mouse: é o que a pessoa mais
        # precisa copiar desta tela.
        self.caminho.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.caminho.setStyleSheet(
            f"font-family: {estilo.FONTE_MONO}; font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO}; background-color: {estilo.COR_FUNDO_ELEVADO};"
            f"border: 1px solid {estilo.COR_BORDA}; border-radius: {estilo.RAIO}px;"
            f"padding: {estilo.ESPACO_2}px {estilo.ESPACO_3}px;"
        )
        layout.addWidget(self.caminho, alignment=Qt.AlignCenter)
        layout.addSpacing(estilo.ESPACO_2)

        # O lembrete da RN-14, logo embaixo do caminho e antes dos botões: os
        # dois arquivos ficam lado a lado na pasta, com nomes parecidos, e quem
        # vai arrastar um deles para a conversa precisa pegar o certo.
        self.lembrete = QLabel()
        self.lembrete.setWordWrap(True)
        self.lembrete.setAlignment(Qt.AlignCenter)
        self.lembrete.setFixedWidth(self.LARGURA_DO_LEMBRETE)
        self.lembrete.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; color: {estilo.COR_ALERTA};"
        )
        layout.addWidget(self.lembrete, alignment=Qt.AlignCenter)
        layout.addSpacing(estilo.ESPACO_4)

        acoes = QHBoxLayout()
        acoes.setSpacing(estilo.ESPACO_3)
        acoes.addStretch()
        acoes.addWidget(_botao("Abrir a pasta", self._abrir_a_pasta, principal=True))
        acoes.addWidget(_botao("Anonimizar outro documento", ao_anonimizar_outro,
                               principal=False))
        acoes.addStretch()
        layout.addLayout(acoes)

    def mostrar(self, caminho, nome_da_origem, resumo, liberados):
        self._caminho = Path(caminho)
        self.caminho.setText(str(self._caminho))
        self.contagem.setText(resumo)
        # Com número liberado, o título não pode dizer "sem CPF": seria afirmar
        # o que não é verdade sobre o arquivo que acabou de ser gravado.
        self.titulo.setText(
            "Arquivo gravado" if liberados else "Arquivo gravado, sem CPF")
        self.lembrete.setText(
            f"⚠ O {nome_da_origem} continua na mesma pasta, com os CPFs inteiros.")
        self.lembrete.ensurePolished()
        self.lembrete.setMinimumHeight(
            self.lembrete.heightForWidth(self.LARGURA_DO_LEMBRETE))

    def _abrir_a_pasta(self):
        if self._caminho is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._caminho.parent)))


def _botao(texto, ao_clicar, principal):
    botao = QPushButton(texto)
    botao.setCursor(Qt.PointingHandCursor)
    botao.setStyleSheet(estilo.estilo_botao(principal=principal))
    botao.clicked.connect(ao_clicar)
    return botao


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

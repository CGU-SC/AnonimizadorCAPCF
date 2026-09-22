"""O motor de leitura faltando, do jeito que os dois módulos mostram.

O aviso no alto da tela de escolher, a tela cheia para quem escolhe um PDF que
só se lê com o motor, e as três saídas das duas - instalar, conferir de novo,
apontar a pasta. É a mesma coisa nos dois módulos, e mora aqui para não ser
escrita duas vezes.

Nasceu em 21/09/2026, na etapa 7 do Anonimizador, tirada de dentro do
`painel_ocr.py` pelo mesmo motivo do `caminho_do_pdf.py`: o Anonimizar passou a
precisar dela, e duas cópias divergiriam na primeira correção.
"""
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QWidget

import estilo
from motor import (
    abrir_instalador,
    apontar_pasta,
    ha_algum_tesseract,
    localizar_instalador,
    localizar_tesseract,
)
from telas_do_motor import AvisoDoMotor, TelaSemMotor


class ControleDoMotor:
    """Procura o motor, mostra o que falta, e segura as três saídas.

    `ao_resolvido(ficha)` é chamado quando o motor aparece com a pessoa parada
    na tela cheia: cada módulo sabe para onde o documento segue dali.
    """

    def __init__(self, dono, pilha, ao_escolher_outro, ao_resolvido,
                 texto_do_aviso=None, rotulo_de_outro="Escolher outro documento",
                 lembrete=None):
        self._dono = dono
        self._pilha = pilha
        self._ao_resolvido = ao_resolvido
        # Se o que falta, na última procura, era só o pacote de português - e
        # não o motor inteiro. Muda a frase do aviso, não as saídas.
        self.sem_portugues = False
        # O documento que esperava o motor na tela cheia.
        self._ficha_esperando = None

        # O aviso vai na tela de escolher de quem usa esta peça, antes de
        # qualquer documento: fazer a pessoa arrastar um PDF para só então
        # contar que falta uma peça seria gastar o tempo dela com uma notícia
        # que o programa já tinha.
        self.aviso = AvisoDoMotor(
            ao_instalar=self.instalar,
            ao_conferir=self.conferir_de_novo,
            ao_apontar=self.apontar_a_pasta,
            texto=texto_do_aviso,
        )
        self.espaco_depois_do_aviso = QWidget()
        self.espaco_depois_do_aviso.setFixedHeight(estilo.ESPACO_3)
        self.espaco_depois_do_aviso.setVisible(False)

        self.tela_sem_motor = TelaSemMotor(
            ao_instalar=self.instalar,
            ao_conferir=self.conferir_de_novo,
            ao_apontar=self.apontar_a_pasta,
            ao_escolher_outro=ao_escolher_outro,
            rotulo_de_outro=rotulo_de_outro,
            lembrete=lembrete,
        )
        pilha.addWidget(self.tela_sem_motor)

    def conferir(self):
        """Procura o motor, acerta o aviso do alto, e diz se achou."""
        if localizar_tesseract() is not None:
            self.sem_portugues = False
            self.aviso.esconder()
            self.espaco_depois_do_aviso.setVisible(False)
            return True
        tem_instalador = localizar_instalador() is not None
        # Chegando aqui, nenhum Tesseract achado tem o português: a procura logo
        # acima teria parado no primeiro que tivesse. Havendo algum, então, o
        # motor está na máquina e o que falta é só o pacote.
        self.sem_portugues = ha_algum_tesseract()
        self.aviso.mostrar(tem_instalador, self.sem_portugues)
        self.espaco_depois_do_aviso.setVisible(True)
        self.tela_sem_motor.saidas.atualizar(tem_instalador, self.sem_portugues)
        return False

    def mostrar_que_falta(self, ficha):
        self._ficha_esperando = ficha
        self.tela_sem_motor.mostrar(
            ficha, localizar_instalador() is not None, self.sem_portugues
        )
        self._pilha.setCurrentWidget(self.tela_sem_motor)

    def instalar(self):
        """Abre o instalador que a TI deixou ao lado do programa.

        Não espera a instalação terminar, e não confere sozinho depois: quem
        sabe quando o instalador acabou é a pessoa, e é ela quem clica em
        "conferir de novo".
        """
        instalador = localizar_instalador()
        if instalador is None:
            # O instalador sumiu depois de o aviso ter sido montado. O aviso se
            # acerta, e o botão passa a aparecer apagado.
            self.conferir()
            return
        try:
            abrir_instalador(instalador)
        except OSError:
            self._dar_recado(
                "O instalador não chegou a abrir. Se o Windows perguntou se "
                'podia, é preciso responder "Sim".',
                erro=True,
            )
            return
        self._dar_recado(
            'O instalador foi aberto. Quando ele terminar, clique em "Conferir '
            'de novo".'
        )

    def conferir_de_novo(self):
        if self.conferir():
            self._resolvido()
            return
        falta = (
            "O pacote de português continua faltando."
            if self.sem_portugues
            else "O motor continua sem ser encontrado."
        )
        self._dar_recado(
            f"{falta} Se a instalação ainda está em andamento, espere ela "
            "terminar e confira de novo.",
            erro=True,
        )

    def apontar_a_pasta(self):
        # A pasta inicial fica em branco pelo mesmo motivo da escolha do
        # documento: nada é lembrado entre um uso e outro.
        pasta = QFileDialog.getExistingDirectory(
            self._dono, "Apontar a pasta do Tesseract", ""
        )
        if pasta:
            self.usar_a_pasta(Path(pasta))

    def usar_a_pasta(self, pasta):
        if not apontar_pasta(pasta):
            self._dar_recado(
                f"A pasta {pasta} não tem o Tesseract. Procure a pasta onde está "
                "o arquivo tesseract.exe.",
                erro=True,
            )
            return
        if self.conferir():
            self._resolvido()
            return
        # A pasta tinha o Tesseract, só que sem o português. Dizer que ela "não
        # tem o Tesseract" mandaria a pessoa procurar outra pasta à toa.
        self._dar_recado(
            f"O Tesseract da pasta {pasta} está sem o pacote de português.",
            erro=True,
        )

    def _resolvido(self):
        """O motor apareceu: o aviso some, e quem estava na tela cheia segue.

        Segue para onde o módulo manda, e não direto para a leitura: começar a
        ler sozinho, sem ela ter pedido, surpreenderia quem só clicou para
        conferir.
        """
        self.tela_sem_motor.saidas.apagar_recado()
        if (self._pilha.currentWidget() is self.tela_sem_motor
                and self._ficha_esperando is not None):
            self._ao_resolvido(self._ficha_esperando)

    def _dar_recado(self, texto, erro=False):
        # O recado vai para as duas telas: saindo da tela cheia para a de
        # escolher, a resposta ao que a pessoa clicou continua à vista.
        self.aviso.saidas.dar_recado(texto, erro=erro)
        self.tela_sem_motor.saidas.dar_recado(texto, erro=erro)

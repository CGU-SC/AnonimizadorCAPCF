"""O caminho do PDF: do arquivo escolhido ao texto conferido.

Esta peça é a máquina que os dois módulos usam. Ela confere o documento, mostra
o cartão do que descobriu, deixa a pessoa decidir sobre a camada de texto quando
há uma, roda a leitura ao lado da janela com contagem de páginas e cancelar, e
abre a conferência. Quando a pessoa clica em "Conferido", ela devolve o texto a
quem a está usando — e é só aí que os dois módulos se separam: o "Gerar OCR"
oferece as duas saídas, e o "Anonimizar" vai direto para a revisão.

Ela nasceu em 18/09/2026, na etapa 7 do Anonimizador, tirada de dentro do
`painel_ocr.py`. A decisão de extrair em vez de copiar está registrada no
CLAUDE.md: copiada, seriam duas cópias de umas seiscentas linhas, que divergem
na primeira correção - foi o que quase aconteceu no mesmo dia, quando a janela
do Windows precisou do mesmo conserto nos dois módulos.

As telas são criadas aqui e entram na pilha de telas de quem usa a peça. Assim o
painel continua sendo quem troca de tela, e a árvore de telas não muda de forma
por causa da extração.
"""
import time
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

import estilo
from documento import DocumentoNaoAbre, conferir, texto_da_camada
from leitura_em_segundo_plano import LeituraEmSegundoPlano
from tela_conferencia import ORIGEM_CAMADA_DO_PDF, TelaConferencia
from tela_decisao import TelaDecisao

NAO_ABRE = (
    "O documento não pôde ser lido até o fim. Ele pode estar danificado por "
    "dentro."
)


class CaminhoDoPdf:
    """A máquina do caminho do PDF, usada pelos dois módulos.

    `titulo` e `legenda` são o cabeçalho do cartão do que o programa descobriu;
    `o_que_vai_acontecer` diz, em uma frase, o que vem depois - e no Anonimizar
    essa frase termina na revisão, e não no salvar do outro módulo (oitava
    emenda da spec 003).

    Os avisos de volta são todos do mesmo tipo: a peça faz o trabalho e chama
    quem a usa quando a decisão é de lá.
    """

    def __init__(self, pilha, ao_conferir, ao_escolher_outro, ao_cancelar,
                 titulo="", legenda="", o_que_vai_acontecer=None,
                 com_cartao=True, ao_abrir_conferencia=None,
                 tem_motor=None, ao_faltar_motor=None,
                 rotulo_de_outro="Escolher outro documento"):
        self._pilha = pilha
        # O Gerar OCR mostra o cartão do que o programa descobriu antes de
        # tudo. O Anonimizar não: o PDF sem texto vai para a tela de ler, que
        # já traz nome, páginas e a escolha do motor, e o PDF com texto vai
        # direto para a decisão (rascunho 08, estados 3a e 3b; oitava emenda).
        self._com_cartao = com_cartao
        self._o_que_vai_acontecer = o_que_vai_acontecer
        self._ao_conferir = ao_conferir
        self._ao_escolher_outro = ao_escolher_outro
        self._ao_cancelar = ao_cancelar
        # Avisa quem usa a peça de que a conferência começou: é a partir daí que
        # existe texto para perder, e é isso que a pergunta antes de descartar
        # precisa saber.
        self._ao_abrir_conferencia = ao_abrir_conferencia or (lambda: None)
        # O motor é procurado por quem usa a peça: é lá que mora o aviso do alto
        # e a tela de motor faltando, que têm as saídas do módulo.
        self._tem_motor = tem_motor or (lambda: True)
        self._ao_faltar_motor = ao_faltar_motor or (lambda ficha: None)

        # Enquanto a leitura roda, é esta peça que segura o trabalho acontecendo
        # ao lado da janela. Fica guardada para poder ser cancelada.
        self.leitura = None
        # O documento em uso agora. É o que permite tentar de novo depois de
        # uma falha, sem a pessoa ter que escolher o arquivo outra vez.
        self.ficha_atual = None

        self.tela_verificando = _montar_tela_verificando()
        self.tela_ficha = _TelaFicha(
            titulo=titulo,
            legenda=legenda,
            rotulo_de_outro=rotulo_de_outro,
            ao_escolher_outro=self._escolher_outro,
            ao_ler=self.seguir_a_partir_da_ficha,
        )
        self.tela_lendo = _TelaLendo(ao_cancelar=self.cancelar_leitura)
        self.tela_decisao = TelaDecisao(
            ao_aproveitar=self.aproveitar_o_texto_existente,
            ao_ignorar=self._ignorar_o_texto_existente,
            ao_escolher_outro=self._escolher_outro,
        )
        self.tela_de_ler = _TelaDeLer(
            ao_ler=self.comecar_a_ler,
            ao_escolher_outro=self._escolher_outro,
            ao_voltar_a_decisao=self.decidir_sobre_o_texto_existente,
        )
        self.tela_conferencia = TelaConferencia(
            ao_processar_outro=self._escolher_outro,
            ao_conferir=self._conferiu,
        )
        self.tela_erro = _TelaErro(
            ao_escolher_outro=self._escolher_outro,
            ao_tentar_de_novo=self.tentar_ler_de_novo,
        )
        for tela in self.telas():
            pilha.addWidget(tela)

    def telas(self):
        """As telas desta peça, na ordem em que a pessoa as encontra."""
        return (self.tela_verificando, self.tela_ficha, self.tela_decisao,
                self.tela_de_ler, self.tela_lendo, self.tela_conferencia,
                self.tela_erro)

    # ------------------------------------------------------------------ uso

    def comecar(self, caminho):
        """Mostra que está trabalhando e então confere o documento.

        A conferência é rápida, mas a tela precisa aparecer antes dela para não
        haver um instante de janela parada sem explicação. Por isso a verificação
        acontece logo depois, quando o Qt já desenhou a tela de espera.
        """
        # Escolher outro documento no meio de uma leitura para a leitura antiga:
        # ela seguiria gastando a máquina num documento que ninguém quer mais.
        self.abandonar_leitura()
        self._mostrar(self.tela_verificando)
        QTimer.singleShot(0, lambda: self.conferir_documento(caminho))

    def conferir_documento(self, caminho):
        try:
            ficha = conferir(caminho)
        except DocumentoNaoAbre as problema:
            self.mostrar_erro(caminho, str(problema))
            return
        except Exception:
            # Qualquer falha não prevista também precisa terminar numa tela com
            # saída. A tela de espera não tem botão nenhum: sem isto, o painel
            # ficaria preso nela para sempre, e nem sair pelo menu resolveria -
            # quem usa só teria como fechar o programa inteiro.
            self.mostrar_erro(caminho, NAO_ABRE)
            return

        self.ficha_atual = ficha
        if not ficha.tem_camada_de_texto and not self._tem_motor():
            # Documento escaneado só se lê com o motor. A ficha ofereceria "ler
            # as páginas" num botão que só poderia falhar.
            self._ao_faltar_motor(ficha)
            return
        if self._com_cartao:
            self.mostrar_ficha(ficha)
        elif ficha.tem_camada_de_texto:
            self.decidir_sobre_o_texto_existente(ficha)
        else:
            self.tela_de_ler.mostrar(ficha, ignorando=False)
            self._mostrar(self.tela_de_ler)

    def mostrar_ficha(self, ficha):
        """O cartão do que o programa descobriu sobre este documento."""
        self.tela_ficha.mostrar(ficha, self._o_que_vai_acontecer)
        self._mostrar(self.tela_ficha)

    def seguir_a_partir_da_ficha(self, ficha):
        """O botão da ficha leva a um de dois lugares, conforme o documento.

        Tendo texto gravado por dentro, a escolha é da pessoa: aproveitar ou
        mandar reler. Não tendo, não há o que escolher e a leitura começa.
        """
        if ficha.tem_camada_de_texto:
            self.decidir_sobre_o_texto_existente(ficha)
        else:
            self.comecar_a_ler(ficha)

    def decidir_sobre_o_texto_existente(self, ficha):
        """Mostra o texto que já está no documento e deixa a escolha com a pessoa."""
        try:
            paginas = texto_da_camada(ficha.caminho)
        except Exception:
            self.mostrar_erro(ficha.caminho, NAO_ABRE)
            return
        self.tela_decisao.mostrar(ficha, paginas)
        self._mostrar(self.tela_decisao)

    def _ignorar_o_texto_existente(self, ficha):
        """Quem manda ignorar o texto de dentro vai ler as imagens.

        No Gerar OCR a leitura começa na hora, como sempre foi. No Anonimizar,
        antes vem a tela de ler, com a escolha do motor e o aviso de que o texto
        de dentro será deixado de lado (rascunho 08, estado 3c) - e, faltando o
        motor, a tela de motor faltando, e não uma leitura que só falharia.
        """
        if self._com_cartao:
            self.comecar_a_ler(ficha)
        elif not self._tem_motor():
            self._ao_faltar_motor(ficha)
        else:
            self.tela_de_ler.mostrar(ficha, ignorando=True)
            self._mostrar(self.tela_de_ler)

    def aproveitar_o_texto_existente(self, ficha, paginas):
        """Vai direto para a conferência, com o texto que já estava no PDF.

        A conferência acontece mesmo aqui: ela é passo obrigatório nos dois
        caminhos. Texto gravado no documento erra menos que o adivinhado de uma
        imagem, mas erra - e quem diz se está bom é quem olha.
        """
        self.tela_conferencia.mostrar(ficha, paginas, origem=ORIGEM_CAMADA_DO_PDF)
        self._ao_abrir_conferencia()
        self._mostrar(self.tela_conferencia)

    def comecar_a_ler(self, ficha):
        """Manda a leitura acontecer ao lado, e passa a mostrar o andamento."""
        if not self._tem_motor():
            # Chega aqui quem mandou ignorar o texto que já estava no documento,
            # ou quem viu o motor sumir com o programa aberto.
            self._ao_faltar_motor(ficha)
            return
        self.tela_lendo.comecar(ficha)
        self._mostrar(self.tela_lendo)

        # Cada aviso carrega quem o mandou. Leitura abandonada - porque a pessoa
        # escolheu outro documento no meio - continua terminando o que estava
        # fazendo, e o aviso dela chega depois; sem esta marca, ele sequestraria
        # a tela e mostraria a conferência de um documento que ninguém pediu.
        leitura = LeituraEmSegundoPlano(ficha.caminho)
        self.leitura = leitura
        leitura.avancou.connect(
            lambda pagina, total: self._leitura_avancou(leitura, pagina, total))
        leitura.terminou.connect(
            lambda paginas: self._leitura_terminou(leitura, ficha, paginas))
        leitura.cancelou.connect(
            lambda pagina: self._leitura_cancelada(leitura, pagina))
        leitura.falhou.connect(
            lambda pagina, motivo: self._leitura_falhou(leitura, pagina, motivo))
        leitura.start()

    def tentar_ler_de_novo(self):
        if self.ficha_atual is not None:
            self.comecar_a_ler(self.ficha_atual)

    def cancelar_leitura(self):
        if self.leitura is not None:
            self.tela_lendo.mostrar_que_esta_parando()
            self.leitura.cancelar()

    def abandonar_leitura(self):
        """Para a leitura em andamento e a esquece.

        Usado quando a pessoa escolhe outro documento no meio da leitura, e ao
        fechar o programa. Sem isto, três coisas davam errado de uma vez: a
        máquina seguia trabalhando num documento abandonado; o aviso de leitura
        terminada chegava depois e levava a tela para a conferência do documento
        antigo; e começar uma leitura nova por cima da velha derrubava o
        programa.
        """
        if self.leitura is not None and self.leitura.isRunning():
            self.leitura.cancelar()
            self.leitura.wait(20_000)
        self.leitura = None

    def mostrar_erro(self, caminho, motivo):
        self.tela_erro.mostrar(caminho, motivo)
        self._mostrar(self.tela_erro)

    def texto_conferido(self):
        return self.tela_conferencia.texto_conferido()

    def esquecer(self):
        self.tela_conferencia.esquecer()

    # -------------------------------------------------------------- por dentro

    def _mostrar(self, tela):
        self._pilha.setCurrentWidget(tela)

    def _escolher_outro(self):
        self._ao_escolher_outro()

    def _conferiu(self):
        self._ao_conferir()

    def _e_a_leitura_de_agora(self, leitura):
        """Diz se o aviso veio da leitura que a tela está esperando."""
        return leitura is self.leitura

    def _leitura_avancou(self, leitura, pagina, total):
        if self._e_a_leitura_de_agora(leitura):
            self.tela_lendo.avancar(pagina, total)

    def _leitura_terminou(self, leitura, ficha, paginas):
        if not self._e_a_leitura_de_agora(leitura):
            return
        self.tela_conferencia.mostrar(ficha, paginas)
        self._ao_abrir_conferencia()
        self._mostrar(self.tela_conferencia)
        self.leitura = None

    def _leitura_cancelada(self, leitura, pagina):
        if not self._e_a_leitura_de_agora(leitura):
            return
        self.leitura = None
        self._ao_cancelar(pagina)

    def _leitura_falhou(self, leitura, pagina, motivo):
        if not self._e_a_leitura_de_agora(leitura):
            return
        if pagina:
            titulo = f"A leitura parou na página {pagina}"
            # Falhar numa página pode ser passageiro, e tentar de novo resolve.
            pode_tentar = True
        else:
            titulo = "A leitura não pôde ser feita"
            # Página 0 quer dizer que a falha não aconteceu dentro de uma página:
            # faltou o motor de leitura, ou deu um defeito não previsto. Os dois
            # ficam sem "tentar de novo". Falta de motor não é passageira - só
            # instalando resolve -, e oferecer "tentar de novo" ali seria oferecer
            # uma saída falsa, que falharia igual e esconderia a causa real.
            pode_tentar = False

        self.tela_erro.mostrar_falha(titulo, motivo, pode_tentar_de_novo=pode_tentar)
        self._mostrar(self.tela_erro)
        self.leitura = None


class _TelaFicha(QWidget):
    """O que o programa descobriu sobre o documento escolhido."""

    def __init__(self, titulo, legenda, rotulo_de_outro, ao_escolher_outro, ao_ler):
        super().__init__()
        self._ao_ler = ao_ler
        self._ficha = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(titulo_da_tela(titulo))
        layout.addWidget(legenda_da_tela(legenda))
        layout.addSpacing(estilo.ESPACO_4)

        self.cartao = QFrame()
        self.cartao.setStyleSheet(
            f"""
            QFrame {{
                background-color: {estilo.COR_FUNDO_ELEVADO};
                border: 1px solid {estilo.COR_BORDA};
                border-radius: {estilo.RAIO}px;
            }}
            """
        )
        cartao_layout = QVBoxLayout(self.cartao)
        cartao_layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_3,
                                         estilo.ESPACO_4, estilo.ESPACO_3)
        cartao_layout.setSpacing(0)

        self.nome_arquivo = QLabel()
        self.nome_arquivo.setWordWrap(True)
        self.nome_arquivo.setStyleSheet(
            f"font-family: {estilo.FONTE_MONO};"
            f"font-size: {estilo.TEXTO_BASE}px; color: {estilo.COR_TEXTO};"
            "border: none;"
        )
        cartao_layout.addWidget(self.nome_arquivo)
        cartao_layout.addSpacing(estilo.ESPACO_3)

        self.linha_paginas = _LinhaDaFicha("Páginas")
        self.linha_texto = _LinhaDaFicha("Camada de texto")
        self.linha_acontece = _LinhaDaFicha("O que vai acontecer")
        for linha in (self.linha_paginas, self.linha_texto, self.linha_acontece):
            cartao_layout.addWidget(linha)

        layout.addWidget(self.cartao)
        layout.addSpacing(estilo.ESPACO_4)

        self.botao_ler = QPushButton("Ler o documento")
        self.botao_ler.setCursor(Qt.PointingHandCursor)
        self.botao_ler.setStyleSheet(estilo.estilo_botao(principal=True))
        self.botao_ler.clicked.connect(self._pedir_leitura)

        botao_outro = QPushButton(rotulo_de_outro)
        botao_outro.setCursor(Qt.PointingHandCursor)
        botao_outro.setStyleSheet(estilo.estilo_botao(principal=False))
        botao_outro.clicked.connect(ao_escolher_outro)

        acoes = QHBoxLayout()
        acoes.setSpacing(estilo.ESPACO_3)
        acoes.addWidget(self.botao_ler)
        acoes.addWidget(botao_outro)
        acoes.addStretch()
        layout.addLayout(acoes)

        layout.addStretch()

    def _pedir_leitura(self):
        if self._ficha is not None:
            self._ao_ler(self._ficha)

    def mostrar(self, ficha, o_que_vai_acontecer):
        self._ficha = ficha
        self.nome_arquivo.setText(ficha.caminho.name)
        self.linha_paginas.definir(str(ficha.paginas))

        if ficha.tem_camada_de_texto:
            letras = com_separador_de_milhar(ficha.letras_na_camada_de_texto)
            self.linha_texto.definir(
                f"sim, {letras} letras", cor=estilo.COR_SUCESSO
            )
            self.botao_ler.setText("Ver o texto e decidir")
        else:
            self.linha_texto.definir("não há", cor=estilo.COR_ALERTA)
            self.botao_ler.setText(f"Ler as {ficha.paginas} páginas")
        # A frase do que vem depois é de quem está usando a peça: no Anonimizar
        # ela termina na revisão, e no Gerar OCR, na conferência.
        self.linha_acontece.definir(o_que_vai_acontecer(ficha))


class _TelaLendo(QWidget):
    """O andamento da leitura: onde está, quanto falta, e como parar."""

    def __init__(self, ao_cancelar):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        miolo = QWidget()
        miolo.setFixedWidth(420)
        miolo_layout = QVBoxLayout(miolo)
        miolo_layout.setContentsMargins(0, 0, 0, 0)
        miolo_layout.setSpacing(0)

        self.nome_arquivo = QLabel()
        self.nome_arquivo.setStyleSheet(
            f"font-family: {estilo.FONTE_MONO};"
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )

        self.contagem = QLabel()
        self.contagem.setStyleSheet(
            f"font-size: {estilo.TEXTO_GRANDE}px; color: {estilo.COR_TEXTO};"
        )

        self.restante = QLabel()
        self.restante.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )

        self.barra = QProgressBar()
        self.barra.setTextVisible(False)
        self.barra.setFixedHeight(6)
        self.barra.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: {estilo.COR_BORDA};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {estilo.COR_DESTAQUE};
                border-radius: 3px;
            }}
            """
        )

        self.botao_cancelar = QPushButton("Cancelar a leitura")
        self.botao_cancelar.setCursor(Qt.PointingHandCursor)
        self.botao_cancelar.setStyleSheet(estilo.estilo_botao(principal=False))
        self.botao_cancelar.clicked.connect(ao_cancelar)

        miolo_layout.addWidget(self.nome_arquivo)
        miolo_layout.addSpacing(estilo.ESPACO_3)
        miolo_layout.addWidget(self.contagem)
        miolo_layout.addWidget(self.restante)
        miolo_layout.addSpacing(estilo.ESPACO_3)
        miolo_layout.addWidget(self.barra)
        miolo_layout.addSpacing(estilo.ESPACO_4)
        miolo_layout.addWidget(self.botao_cancelar, alignment=Qt.AlignLeft)

        layout.addWidget(miolo)

    def comecar(self, ficha):
        self.nome_arquivo.setText(ficha.caminho.name)
        self.contagem.setText("Preparando a leitura…")
        self.restante.setText("")
        self.barra.setRange(0, ficha.paginas)
        self.barra.setValue(0)
        self.botao_cancelar.setEnabled(True)
        self.botao_cancelar.setText("Cancelar a leitura")
        # O relógio começa na primeira página, e é dele que sai a estimativa.
        self._comeco = time.monotonic()

    def avancar(self, pagina, total):
        self.contagem.setText(f"Lendo a página {pagina} de {total}")
        # A barra inclui a página que está sendo lida agora, como no rascunho
        # aprovado. Contando só as terminadas, um documento de uma página só
        # ficaria com a barra em zero do começo ao fim - e barra parada é lida
        # como programa travado.
        self.barra.setValue(pagina)
        self.restante.setText(self._estimar(pagina, total))

    def _estimar(self, pagina, total):
        """Quanto falta, calculado pelo ritmo real desta leitura.

        A estimativa sai do que já aconteceu nesta máquina e neste documento, e
        não de um número fixo escrito no código: página com muito texto demora
        mais que página quase vazia, e máquina lenta demora mais que rápida.
        """
        paginas_prontas = pagina - 1
        if paginas_prontas < 1:
            return "Calculando quanto falta…"

        por_pagina = (time.monotonic() - self._comeco) / paginas_prontas
        segundos = round(por_pagina * (total - paginas_prontas))
        if segundos < 10:
            return "Faltam poucos segundos."
        if segundos < 60:
            return f"Faltam cerca de {segundos} segundos."
        minutos = round(segundos / 60)
        return (f"Falta cerca de {minutos} minuto." if minutos == 1
                else f"Faltam cerca de {minutos} minutos.")

    def mostrar_que_esta_parando(self):
        """O cancelamento não é instantâneo, e a tela precisa dizer isso.

        A página que está sendo lida termina de ser lida - interromper o
        Tesseract no meio deixaria o programa num estado que ninguém sabe
        descrever. São uns dois segundos, e silêncio nesses dois segundos faz a
        pessoa clicar de novo achando que o botão não pegou.
        """
        self.contagem.setText("Parando a leitura…")
        self.restante.setText("Terminando a página que já estava sendo lida.")
        self.botao_cancelar.setEnabled(False)
        self.botao_cancelar.setText("Cancelando…")


class _TelaErro(QWidget):
    """O arquivo que não abre: uma frase, e o caminho de volta."""

    # A caixa e o texto dentro dela têm largura fixa. Sem isso, o Qt calcula a
    # altura da caixa achando que a frase cabe numa linha só, e o fim do texto
    # some para fora da borda - a pessoa lê meia explicação e não tem como
    # saber que faltou pedaço.
    LARGURA_DA_CAIXA = 460
    LARGURA_DO_TEXTO = 400

    def __init__(self, ao_escolher_outro, ao_tentar_de_novo=None):
        super().__init__()
        self._ao_tentar_de_novo = ao_tentar_de_novo

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        caixa = QFrame()
        caixa.setFixedWidth(self.LARGURA_DA_CAIXA)
        caixa.setStyleSheet(
            f"""
            QFrame {{
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

        self.titulo = QLabel("Não foi possível abrir o documento")
        self.titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO}; border: none;"
        )

        self.explicacao = QLabel()
        self.explicacao.setWordWrap(True)
        self.explicacao.setFixedWidth(self.LARGURA_DO_TEXTO)
        self.explicacao.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
        )

        caixa_layout.addWidget(self.titulo)
        caixa_layout.addWidget(self.explicacao)

        self.botao_tentar = QPushButton("Tentar de novo")
        self.botao_tentar.setCursor(Qt.PointingHandCursor)
        self.botao_tentar.setStyleSheet(estilo.estilo_botao(principal=True))
        self.botao_tentar.setVisible(False)
        if ao_tentar_de_novo is not None:
            self.botao_tentar.clicked.connect(ao_tentar_de_novo)

        botao = QPushButton("Escolher outro documento")
        botao.setCursor(Qt.PointingHandCursor)
        botao.setStyleSheet(estilo.estilo_botao(principal=True))
        botao.clicked.connect(ao_escolher_outro)

        linha_botao = QHBoxLayout()
        linha_botao.setSpacing(estilo.ESPACO_3)
        linha_botao.addStretch()
        linha_botao.addWidget(self.botao_tentar)
        linha_botao.addWidget(botao)
        linha_botao.addStretch()

        layout.addWidget(caixa, alignment=Qt.AlignCenter)
        layout.addSpacing(estilo.ESPACO_4)
        layout.addLayout(linha_botao)

    def mostrar(self, caminho, motivo):
        """O documento que não abre: sem "tentar de novo", porque não adianta."""
        self.titulo.setText("Não foi possível abrir o documento")
        self.botao_tentar.setVisible(False)
        self._escrever(f"{Path(caminho).name} — {motivo}")

    def mostrar_falha(self, titulo, motivo, pode_tentar_de_novo=True):
        """A leitura que estourou. O botão de tentar de novo só aparece quando
        tentar de novo pode dar certo."""
        self.titulo.setText(titulo)
        self.botao_tentar.setVisible(
            pode_tentar_de_novo and self._ao_tentar_de_novo is not None
        )
        self._escrever(motivo)

    def _escrever(self, texto):
        self.explicacao.setText(texto)
        # A frase muda de tamanho conforme o problema, então a altura de que
        # ela precisa é recalculada a cada vez.
        self.explicacao.setMinimumHeight(
            self.explicacao.heightForWidth(self.LARGURA_DO_TEXTO)
        )


class _LinhaDaFicha(QWidget):
    """Uma linha do cartão: o nome à esquerda, o valor à direita."""

    def __init__(self, chave):
        super().__init__()
        self.setStyleSheet(f"border-top: 1px solid {estilo.COR_BORDA};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, estilo.ESPACO_2, 0, estilo.ESPACO_2)

        rotulo = QLabel(chave)
        rotulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
        )

        self.valor = QLabel()
        self.valor.setAlignment(Qt.AlignRight)

        layout.addWidget(rotulo)
        layout.addStretch()
        layout.addWidget(self.valor)

    def definir(self, texto, cor=None):
        self.valor.setText(texto)
        self.valor.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 600;"
            f"color: {cor or estilo.COR_TEXTO}; border: none;"
        )


def _montar_tela_verificando():
    tela = QWidget()
    layout = QVBoxLayout(tela)
    layout.setAlignment(Qt.AlignCenter)
    layout.setSpacing(estilo.ESPACO_2)

    titulo = titulo_da_tela("Conferindo o documento…")
    titulo.setAlignment(Qt.AlignCenter)

    legenda = legenda_da_tela(
        "Verificando a quantidade de páginas e a existência de camada de texto.")
    legenda.setAlignment(Qt.AlignCenter)

    barra = QProgressBar()
    barra.setRange(0, 0)  # sem porcentagem: não se sabe quanto falta
    barra.setTextVisible(False)
    barra.setFixedSize(260, 4)
    barra.setStyleSheet(
        f"""
        QProgressBar {{
            background-color: {estilo.COR_BORDA};
            border: none;
            border-radius: 2px;
        }}
        QProgressBar::chunk {{
            background-color: {estilo.COR_DESTAQUE};
            border-radius: 2px;
        }}
        """
    )

    linha_barra = QHBoxLayout()
    linha_barra.addStretch()
    linha_barra.addWidget(barra)
    linha_barra.addStretch()

    layout.addWidget(titulo)
    layout.addWidget(legenda)
    layout.addSpacing(estilo.ESPACO_3)
    layout.addLayout(linha_barra)
    return tela


def com_separador_de_milhar(numero):
    """Escreve o número do jeito que se escreve em português: 1.720, não 1720.

    A separação é feita aqui, e não pelo atalho do Python que "usa o formato da
    máquina": esse atalho depende de como o Windows daquela máquina está
    configurado, e numa máquina em inglês o mesmo número sairia com vírgula.
    """
    return f"{numero:,}".replace(",", ".")


def titulo_da_tela(texto):
    rotulo = QLabel(texto)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_GRANDE}px; font-weight: 600;"
        f"color: {estilo.COR_TEXTO};"
    )
    return rotulo


def legenda_da_tela(texto):
    rotulo = QLabel(texto)
    rotulo.setWordWrap(True)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px;"
        f"color: {estilo.COR_TEXTO_SECUNDARIO};"
    )
    return rotulo


def rotulo_de_secao(texto):
    rotulo = QLabel(texto)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 700;"
        f"color: {estilo.COR_TEXTO_SECUNDARIO}; letter-spacing: 1px;"
    )
    return rotulo


def estilo_do_radio(apagado=False):
    cor = estilo.COR_TEXTO_APAGADO if apagado else estilo.COR_TEXTO
    return f"""
        QRadioButton {{
            color: {cor};
            font-size: {estilo.TEXTO_BASE}px;
            spacing: {estilo.ESPACO_2}px;
        }}
        QRadioButton::indicator {{
            width: 15px;
            height: 15px;
            border-radius: 8px;
            border: 2px solid {estilo.COR_TEXTO_SECUNDARIO};
        }}
        QRadioButton::indicator:checked {{
            border: 2px solid {estilo.COR_DESTAQUE};
            background-color: {estilo.COR_DESTAQUE};
        }}
        QRadioButton::indicator:disabled {{
            border: 2px solid #4a5058;
        }}
    """


def montar_escolha_do_motor(rotulo):
    """A escolha do motor de leitura: o Tesseract, marcado, e a IA local, apagada.

    Os dois módulos mostram esta mesma escolha - o Gerar OCR na tela de escolher
    o documento, o Anonimizar na hora de ler as imagens (terceira emenda da spec
    003) -, e ela é montada num lugar só para as duas não divergirem.

    Devolve o bloco pronto e os dois botões, para quem quiser consultá-los.
    """
    bloco = QWidget()
    layout = QVBoxLayout(bloco)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(estilo.ESPACO_2)

    layout.addWidget(rotulo_de_secao(rotulo))

    tesseract = QRadioButton("Tesseract (nesta máquina)")
    tesseract.setChecked(True)
    tesseract.setStyleSheet(estilo_do_radio())

    # A IA local aparece e não funciona de propósito: ela depende de um servidor
    # que a TI da UFSC ainda vai montar. Não existe nenhuma linha do programa que
    # converse com motor remoto - e ele nunca será de empresa de fora da UFSC.
    ia_local = QRadioButton("IA local da UFSC")
    ia_local.setEnabled(False)
    ia_local.setStyleSheet(estilo_do_radio(apagado=True))

    explicacao = QLabel(
        "Depende de um servidor que a TI ainda vai montar dentro da rede "
        "da universidade."
    )
    explicacao.setWordWrap(True)
    explicacao.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px;"
        f"color: {estilo.COR_TEXTO_SECUNDARIO}; margin-left: 22px;"
    )

    layout.addWidget(tesseract)
    layout.addWidget(ia_local)
    layout.addWidget(explicacao)
    return bloco, tesseract, ia_local


class _TelaDeLer(QWidget):
    """A tela de antes de ler as imagens, no Anonimizar (rascunho 08, 3a e 3c).

    Ela faz o papel do cartão do Gerar OCR para quem vai ler o PDF como imagem:
    diz o nome, as páginas e o que vai acontecer, e traz a escolha do motor logo
    acima do botão de ler - o único momento em que essa escolha serve para
    alguma coisa. Tesseract já vem marcado: quem não quer pensar só clica em ler.
    """

    def __init__(self, ao_ler, ao_escolher_outro, ao_voltar_a_decisao):
        super().__init__()
        self._ao_ler = ao_ler
        self._ao_escolher_outro = ao_escolher_outro
        self._ao_voltar_a_decisao = ao_voltar_a_decisao
        self._ficha = None
        self._ignorando = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.titulo = titulo_da_tela("")
        self.legenda = legenda_da_tela("")
        layout.addWidget(self.titulo)
        layout.addWidget(self.legenda)
        layout.addSpacing(estilo.ESPACO_4)

        bloco, self.motor_tesseract, self.motor_ia_local = montar_escolha_do_motor(
            "LER COM")
        layout.addWidget(bloco)
        layout.addSpacing(estilo.ESPACO_4)

        self.botao_ler = QPushButton()
        self.botao_ler.setCursor(Qt.PointingHandCursor)
        self.botao_ler.setStyleSheet(estilo.estilo_botao(principal=True))
        self.botao_ler.clicked.connect(self._ler)

        self.botao_outro = QPushButton()
        self.botao_outro.setCursor(Qt.PointingHandCursor)
        self.botao_outro.setStyleSheet(estilo.estilo_botao(principal=False))
        self.botao_outro.clicked.connect(self._segundo_botao)

        acoes = QHBoxLayout()
        acoes.setSpacing(estilo.ESPACO_3)
        acoes.addWidget(self.botao_ler)
        acoes.addWidget(self.botao_outro)
        acoes.addStretch()
        layout.addLayout(acoes)
        layout.addStretch()

    def mostrar(self, ficha, ignorando):
        """Prepara a tela para um de dois caminhos.

        `ignorando` é o de quem clicou em "Ignorar e ler as imagens" num PDF que
        tinha texto por dentro: o título avisa que esse texto vai ser deixado de
        lado, e o segundo botão volta à decisão, para quem mudar de ideia.
        """
        self._ficha = ficha
        self._ignorando = ignorando
        paginas = f"{ficha.paginas} " + ("página" if ficha.paginas == 1 else "páginas")
        if ignorando:
            self.titulo.setText("Ler as imagens deste documento")
            self.legenda.setText(
                f"{ficha.caminho.name} — {paginas}: o texto que estava por dentro "
                "será ignorado, e cada página será lida como imagem.")
            self.botao_outro.setText("Voltar à decisão sobre o texto")
        else:
            self.titulo.setText("Este documento precisa ser lido")
            self.legenda.setText(
                f"{ficha.caminho.name} — {paginas}, sem texto por dentro: cada "
                "página será lida como imagem.")
            self.botao_outro.setText("Escolher outro arquivo")
        self.botao_ler.setText(f"Ler as {paginas}")

    def _ler(self):
        if self._ficha is not None:
            self._ao_ler(self._ficha)

    def _segundo_botao(self):
        if self._ignorando and self._ficha is not None:
            self._ao_voltar_a_decisao(self._ficha)
        else:
            self._ao_escolher_outro()


class FaixaDoTopo(QLabel):
    """Uma linha de aviso no alto do painel, que aparece só quando há o que dizer."""

    def __init__(self):
        super().__init__()
        self.setWordWrap(True)
        self.setVisible(False)
        self.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
            f"border-left: 3px solid {estilo.COR_DESTAQUE};"
            "background-color: rgba(59, 110, 165, 26);"
            f"border-radius: {estilo.RAIO}px;"
            f"padding: {estilo.ESPACO_2}px {estilo.ESPACO_3}px;"
        )

    def mostrar(self, texto):
        self.setText(texto)
        self.setVisible(True)

    def esconder(self):
        self.setVisible(False)

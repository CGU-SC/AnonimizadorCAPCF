"""O painel do item "Anonimizar": do arquivo escolhido à revisão.

É ele que troca de tela conforme o documento anda: escolher o arquivo, revisar
o texto mascarado, ou explicar o que deu errado. Cada tela é uma peça à parte, e
este arquivo é quem sabe a ordem entre elas - o mesmo arranjo do painel do
"Gerar OCR".

Segue os rascunhos aprovados mockups/anonimizar/08-escolher-e-salvar.html (a
escolha do arquivo) e 01-revisar-antes-de-salvar.html (a revisão e o erro).

O painel abre `.md`, `.txt` e PDF. O PDF passa pela mesma peça do "Gerar OCR"
(`caminho_do_pdf.py`) - decidir sobre o texto de dentro, ler, conferir - e,
conferido, vem direto para a revisão (RN-15, desde a etapa 7). O motor faltando
também é peça comum aos dois módulos (`motor_na_tela.py`), com as frases deste.
"""
import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import arquivo_md
import arquivo_texto
import cpf
import estilo
from caminho_do_pdf import CaminhoDoPdf, FaixaDoTopo
from motor_na_tela import ControleDoMotor
from arquivo_texto import ArquivoNaoServe, ler, quebra_de_linha
from tela_revisao import TelaRevisao
from telas_de_salvar import (
    TelaDescartar,
    TelaSobrescrever,
    resumo_do_documento,
)
from telas_de_salvar_sem_cpf import TelaGravadoSemCpf, TelaSalvarSemCpf

EXTENSOES_DE_TEXTO = (".md", ".txt")
EXTENSOES_ACEITAS = EXTENSOES_DE_TEXTO + (".pdf",)

# Word, planilha e imagem não estão a caminho: eles estão fora do escopo da
# spec. Dizer "numa etapa seguinte" para eles seria prometer o que o programa
# nunca vai cumprir - e quem espera não reclama, só some.
OUTRO_TIPO = (
    "O Anonimizar abre PDF, .md e .txt. O {nome} é de outro tipo."
)


TITULO_DA_RECUSA = "Este é o arquivo de origem"
RECUSA_DA_ORIGEM = (
    "O caminho escolhido é o do próprio {nome}, o arquivo com os CPFs inteiros. "
    "O programa nunca grava por cima da origem: o original se perderia, e só "
    "sobraria a versão mascarada. Escolha outro nome ou outra pasta — nada foi "
    "gravado."
)

TITULO_DO_ERRO = "Não foi possível gravar nesta pasta"
ERRO_AO_GRAVAR = (
    "A pasta {pasta} não aceitou o arquivo. Ela pode estar protegida, sem "
    "espaço, ou a unidade de rede pode estar desconectada. Escolha outra pasta "
    "e tente de novo — nada foi gravado, e a revisão continua como estava."
)


class PainelAnonimizar(QWidget):
    def __init__(self):
        super().__init__()
        # Arrastar o arquivo para dentro da janela é uma das duas formas de
        # escolher, como no "Gerar OCR"; a outra é o botão.
        self.setAcceptDrops(True)
        # De onde veio o texto que está na revisão, para sugerir o destino ao
        # lado dele e para recusar gravar por cima dele (RN-13 e RN-14).
        self._origem = None
        # A quebra de linha que o documento usava, para o arquivo sair com ela.
        self._quebra_da_origem = arquivo_texto.QUEBRA_SIMPLES
        # O destino que espera a resposta da pergunta de escrever por cima.
        self._destino_pendente = None
        # Esta revisão já virou arquivo? Salva, não há o que perder ao sair.
        self._salvo = False
        # O que fazer depois de a pessoa responder à pergunta de descartar, e
        # para onde voltar se ela desistir.
        self._acao_pendente = None
        self._tela_antes_da_pergunta = None
        # Um PDF está na conferência, com texto que ainda não chegou à revisão?
        self._conferindo = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_4,
                                  estilo.ESPACO_5, estilo.ESPACO_5)
        layout.setSpacing(0)

        self.telas = QStackedWidget()
        # O motor faltando é a mesma peça do Gerar OCR, com as frases deste
        # módulo: aqui, sem o motor, ainda dá para anonimizar muita coisa, e o
        # aviso e a tela cheia precisam dizer isso (rascunho 08, estados 2 e 2b).
        self.motor = ControleDoMotor(
            dono=self,
            pilha=self.telas,
            ao_escolher_outro=self.voltar_para_escolher,
            ao_resolvido=self._motor_resolvido,
            texto_do_aviso=(
                "Sem ele, o programa não lê PDF escaneado. O resto continua "
                "funcionando — veja abaixo o que dá para anonimizar agora."),
            rotulo_de_outro="Escolher outro arquivo",
            lembrete=(
                "Um .md, um .txt ou um PDF com texto por dentro podem ser "
                "anonimizados normalmente."),
        )
        self.tela_escolher = self._montar_tela_escolher()
        self.tela_revisao = TelaRevisao(
            ao_anonimizar_outro=self.voltar_para_escolher,
            ao_salvar=self.abrir_o_salvar,
        )
        self.tela_salvar = TelaSalvarSemCpf(
            ao_salvar=self.gravar, ao_voltar=self.voltar_para_revisao)
        # A pergunta de escrever por cima é a mesma do "Gerar OCR", inteira:
        # é o mesmo risco, e duas perguntas diferentes para a mesma coisa
        # obrigariam a pessoa a ler duas vezes o que já sabe.
        self.tela_sobrescrever = TelaSobrescrever(
            ao_escrever_por_cima=self._escrever_por_cima,
            ao_outro_nome=self._sugerir_outro_nome,
        )
        self.tela_gravado = TelaGravadoSemCpf(
            ao_anonimizar_outro=self.voltar_para_escolher)
        # A mesma caixa do "Gerar OCR", com as palavras desta tela (RN-1 da
        # spec 002, e a premissa de sair sem salvar da spec 003).
        self.tela_descartar = TelaDescartar(
            ao_descartar=self._descartar_e_seguir,
            ao_voltar=self._voltar_de_onde_estava,
        )
        # O caminho do PDF é a mesma peça que o "Gerar OCR" usa: conferir o
        # documento, decidir sobre a camada de texto, ler e conferir. O que muda
        # é o destino - aqui o texto conferido vai direto para a revisão, sem a
        # escolha de saída do outro módulo (RN-15).
        self.pdf = CaminhoDoPdf(
            pilha=self.telas,
            ao_conferir=self._texto_conferido,
            ao_escolher_outro=self.voltar_para_escolher,
            ao_cancelar=self._leitura_foi_cancelada,
            com_cartao=False,
            ao_abrir_conferencia=self._comecou_a_conferencia,
            tem_motor=self._conferir_o_motor,
            ao_faltar_motor=self.motor.mostrar_que_falta,
            rotulo_de_outro="Escolher outro arquivo",
        )
        self.tela_erro = _TelaErro(ao_escolher_outro=self.voltar_para_escolher)
        for tela in (self.tela_escolher, self.tela_revisao, self.tela_salvar,
                     self.tela_sobrescrever, self.tela_gravado,
                     self.tela_descartar, self.tela_erro):
            self.telas.addWidget(tela)

        layout.addWidget(self.telas)
        # A primeira tela é a de escolher: sem dizer isso, a pilha abre na tela
        # que entrou nela primeiro, que é uma do meio do caminho do PDF.
        self.telas.setCurrentWidget(self.tela_escolher)
        self._conferir_o_motor()

    # ---------------------------------------------------------------- telas

    def _montar_tela_escolher(self):
        tela = QWidget()
        layout = QVBoxLayout(tela)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        titulo = QLabel("Anonimizar")
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_GRANDE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO};"
        )
        legenda = QLabel(
            "Gera um novo arquivo que tarja os três primeiros e dois últimos "
            "dígitos dos CPFs contidos no documento enviado."
        )
        legenda.setWordWrap(True)
        legenda.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )
        layout.addWidget(titulo)
        layout.addWidget(legenda)
        layout.addSpacing(estilo.ESPACO_4)
        layout.addWidget(self.motor.aviso)
        layout.addWidget(self.motor.espaco_depois_do_aviso)
        # A faixa só aparece quando há o que contar - hoje, quando a pessoa
        # cancela uma leitura. Voltar calada faria quem clicou sem querer não
        # descobrir o que aconteceu.
        self.faixa_do_topo = FaixaDoTopo()
        layout.addWidget(self.faixa_do_topo)
        layout.addWidget(self._montar_area_de_arrastar())
        layout.addStretch()
        return tela

    def _montar_area_de_arrastar(self):
        area = QFrame()
        # A regra vale só para o quadro, pelo nome. Escrita para todo QFrame,
        # ela valia também para os textos de dentro (todo texto do Qt é um
        # QFrame), e cada um pintava o fundo de novo por cima do quadro: saíam
        # caixinhas mais claras em volta de cada frase (entrega, 24/09/2026).
        # E os textos ficam transparentes: senão pintam o fundo da janela, que
        # a regra do painel em main.py passa para tudo o que está dentro dele.
        area.setObjectName("area_de_arrastar")
        area.setStyleSheet(
            f"""
            QFrame#area_de_arrastar {{
                border: 2px dashed {estilo.COR_BORDA};
                border-radius: {estilo.RAIO}px;
                background-color: rgba(255, 255, 255, 4);
            }}
            QLabel {{ background: transparent; }}
            """
        )
        layout = QVBoxLayout(area)
        layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_5,
                                  estilo.ESPACO_4, estilo.ESPACO_5)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        icone = QLabel("📄")
        icone.setAlignment(Qt.AlignCenter)
        icone.setStyleSheet("font-size: 34px; border: none;")

        chamada = QLabel("Arraste o arquivo aqui")
        chamada.setAlignment(Qt.AlignCenter)
        chamada.setStyleSheet(
            f"font-size: {estilo.TEXTO_GRANDE}px; color: {estilo.COR_TEXTO};"
            "border: none;"
        )

        self.tipos = tipos = QLabel("PDF, .md ou .txt")
        tipos.setAlignment(Qt.AlignCenter)
        tipos.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
        )
        # Sem o motor, no lugar da linha dos tipos aparece a lista do que dá
        # para anonimizar agora (rascunho 08, estado 2). O PDF continua aceito:
        # o programa só descobre se ele tem texto depois de abri-lo, e o PDF
        # com texto funciona sem o motor. O ✗ é amarelo, e não vermelho: nada
        # falhou, falta uma peça.
        self.lista_sem_motor = QLabel(
            "<b>O que dá para anonimizar agora</b><br>"
            f"<span style='color:{estilo.COR_SUCESSO}'>✓</span> .md e .txt<br>"
            f"<span style='color:{estilo.COR_SUCESSO}'>✓</span> PDF com texto por "
            "dentro, como os do sistema de processos<br>"
            f"<span style='color:{estilo.COR_ALERTA}'>✗</span> PDF escaneado — "
            "precisa do motor de leitura"
        )
        self.lista_sem_motor.setTextFormat(Qt.RichText)
        self.lista_sem_motor.setAlignment(Qt.AlignCenter)
        self.lista_sem_motor.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
        )
        self.lista_sem_motor.setVisible(False)

        ou = QLabel("ou")
        ou.setAlignment(Qt.AlignCenter)
        ou.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO}; border: none;"
        )

        botao = QPushButton("Escolher arquivo…")
        botao.setCursor(Qt.PointingHandCursor)
        botao.setStyleSheet(estilo.estilo_botao(principal=True))
        botao.clicked.connect(self._abrir_seletor_de_arquivo)

        linha_botao = QHBoxLayout()
        linha_botao.addStretch()
        linha_botao.addWidget(botao)
        linha_botao.addStretch()

        layout.addWidget(icone)
        layout.addWidget(chamada)
        layout.addWidget(tipos)
        layout.addWidget(self.lista_sem_motor)
        layout.addSpacing(estilo.ESPACO_3)
        layout.addWidget(ou)
        layout.addSpacing(estilo.ESPACO_3)
        layout.addLayout(linha_botao)
        return area

    # ------------------------------------------------------------- escolher

    def _abrir_seletor_de_arquivo(self):
        # A pasta inicial fica em branco de propósito: nada é lembrado entre um
        # uso e outro, nem a última pasta usada (regra RN-19).
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Escolher arquivo", "",
            "Documentos (*.pdf *.md *.txt)",
        )
        if caminho:
            self.receber_arquivo(Path(caminho))

    def receber_arquivo(self, caminho):
        """Abre o arquivo escolhido e leva o texto dele para a revisão.

        Havendo revisão aberta e não salva, a pergunta vem antes: o arquivo novo
        só é aberto depois de a pessoa dizer que pode jogar fora o anterior.
        """
        if self.perguntar_antes_de_descartar(
                lambda: self.receber_arquivo(caminho), incluir_conferencia=True):
            return
        self.faixa_do_topo.esconder()
        if caminho.suffix.lower() == ".pdf":
            # A revisão do documento anterior sai de cena. Deixada por baixo -
            # já salva, e com o PDF novo marcado como "não salvo" -, ela fazia
            # a pergunta antes de descartar falar de um arquivo que já tinha
            # sido gravado, e a janela recusava fechar (revisão da etapa 7).
            self.tela_revisao.esquecer()
            self._origem = caminho
            self._salvo = False
            # O PDF não é arquivo de texto: a quebra de linha do arquivo
            # gravado é a simples, e não tem de onde ser herdada.
            self._quebra_da_origem = arquivo_texto.QUEBRA_SIMPLES
            self.pdf.comecar(caminho)
            return
        # Qualquer outro arquivo para a leitura de PDF que estiver em andamento
        # (o PDF novo já faz isso por dentro da peça). Sem isto, a leitura
        # antiga terminava por baixo, jogava a tela para a conferência do PDF
        # por cima da revisão do arquivo novo, e o texto de um documento saía
        # com o nome e a quebra de linha do outro (revisão da etapa 7).
        self.pdf.abandonar_leitura()
        self._conferindo = False
        if caminho.suffix.lower() not in EXTENSOES_DE_TEXTO:
            self._mostrar_erro(OUTRO_TIPO.format(nome=caminho.name))
            return
        try:
            texto = ler(caminho)
        except ArquivoNaoServe as problema:
            self._mostrar_erro(str(problema))
            return
        except OSError:
            # O arquivo sumiu, ou está numa pasta de rede que caiu, entre a
            # escolha e a leitura. Sem isto o painel ficaria numa tela sem saída.
            self._mostrar_erro(
                f"O arquivo {caminho.name} não pôde ser aberto. Ele pode ter "
                "sido movido, ou estar numa pasta que saiu do ar."
            )
            return

        self._origem = caminho
        self._salvo = False
        # A quebra de linha do documento fica guardada agora, com o arquivo em
        # mãos: o arquivo gravado sai com a mesma, e não com a do programa.
        self._quebra_da_origem = quebra_de_linha(caminho)
        self._abrir_revisao(texto)

    def voltar_para_escolher(self):
        """Volta à escolha do arquivo - perguntando antes, quando há o que perder."""
        if self.perguntar_antes_de_descartar(self._voltar_para_escolher_agora,
                                             incluir_conferencia=True):
            return
        self._voltar_para_escolher_agora()

    def _voltar_para_escolher_agora(self):
        self.tela_revisao.esquecer()
        self.pdf.abandonar_leitura()
        self.pdf.esquecer()
        self._conferindo = False
        self._origem = None
        self._quebra_da_origem = arquivo_texto.QUEBRA_SIMPLES
        self._destino_pendente = None
        self._salvo = False
        self.telas.setCurrentWidget(self.tela_escolher)

    # --------------------------------------------------------------- salvar

    def abrir_o_salvar(self, destino=None):
        """A tela de onde salvar, com o caminho já preenchido (regra RN-13)."""
        if self._origem is None:
            return
        if destino is None:
            destino = arquivo_md.caminho_sem_cpf(self._origem)
        self.tela_salvar.mostrar(
            destino,
            self._origem.name,
            self.tela_revisao.resumo_do_que_sai(),
            self.tela_revisao.liberados_que_passam_na_conta(),
        )
        self.telas.setCurrentWidget(self.tela_salvar)

    def voltar_para_revisao(self):
        self._destino_pendente = None
        self.telas.setCurrentWidget(self.tela_revisao)

    def gravar(self, destino):
        """Confere o destino e grava - ou pergunta antes, quando é o caso."""
        if _e_o_mesmo_arquivo(destino, self._origem):
            # Gravar por cima da origem apagaria o documento com os CPFs
            # inteiros, que é o que a pessoa ainda precisa para trabalhar - e
            # a spec promete que ele nunca é alterado (RN-14).
            self.tela_salvar.avisar(
                TITULO_DA_RECUSA, RECUSA_DA_ORIGEM.format(nome=self._origem.name))
            return
        if destino.exists():
            self._destino_pendente = destino
            self.tela_sobrescrever.mostrar(destino)
            self.telas.setCurrentWidget(self.tela_sobrescrever)
            return
        self._gravar_de_verdade(destino)

    def _escrever_por_cima(self):
        destino = self._destino_pendente
        self._destino_pendente = None
        if destino is not None:
            self._gravar_de_verdade(destino)

    def _sugerir_outro_nome(self):
        destino = self._destino_pendente
        self._destino_pendente = None
        # Volta à tela de salvar já com um nome que não apaga nada: quem quer
        # outro nome quer trocar o nome, e não digitar a pasta de novo.
        self.abrir_o_salvar(arquivo_md.caminho_livre(destino))

    def _gravar_de_verdade(self, destino):
        texto = self.tela_revisao.texto_para_o_arquivo()
        # A última linha termina com quebra, como todo arquivo de texto: sem
        # ela, alguns programas juntam a última linha com o que vier depois.
        if not texto.endswith("\n"):
            texto += "\n"
        try:
            arquivo_md.gravar(destino, texto, self._quebra_da_origem)
        except OSError:
            # Nada da revisão se perde: a tela de salvar volta com o aviso, e a
            # pessoa troca a pasta sem refazer o trabalho.
            self.telas.setCurrentWidget(self.tela_salvar)
            self.tela_salvar.avisar(
                TITULO_DO_ERRO, ERRO_AO_GRAVAR.format(pasta=destino.parent))
            return
        self._salvo = True
        self.tela_gravado.mostrar(
            destino,
            self._origem.name,
            # Na tela de sucesso a contagem vem sem a separação por tipo: aqui
            # já não há o que decidir, e o que importa é onde o arquivo ficou.
            self.tela_revisao.resumo_do_que_sai(por_tipo=False),
            self.tela_revisao.liberados_que_passam_na_conta(),
        )
        self.telas.setCurrentWidget(self.tela_gravado)

    def _mostrar_erro(self, motivo):
        self.tela_erro.mostrar(motivo)
        self.telas.setCurrentWidget(self.tela_erro)

    # --------------------------------------------------- o motor de leitura

    def showEvent(self, evento):
        # Procura de novo toda vez que a pessoa entra no módulo: o motor pode
        # ter sido instalado com o programa aberto, e o aviso não deve continuar
        # dizendo que falta uma peça que já está lá.
        self._conferir_o_motor()
        super().showEvent(evento)

    def _conferir_o_motor(self):
        """Procura o motor, acerta o aviso e a lista do que dá, e diz se achou."""
        achou = self.motor.conferir()
        self.tipos.setVisible(achou)
        self.lista_sem_motor.setVisible(not achou)
        return achou

    def _motor_resolvido(self, ficha):
        """O motor apareceu com a pessoa na tela cheia: o documento segue.

        Segue para a tela de ler, e não direto para a leitura - começar sozinho
        surpreenderia quem só clicou para conferir. Quem chegou pela decisão
        ("ignorar e ler as imagens") volta à tela de ler do jeito dela.
        """
        self._conferir_o_motor()
        self.pdf.tela_de_ler.mostrar(ficha, ignorando=ficha.tem_camada_de_texto)
        self.telas.setCurrentWidget(self.pdf.tela_de_ler)

    # --------------------------------------------------- o caminho do PDF

    def _texto_conferido(self):
        """O texto que saiu da conferência vai direto para a revisão (RN-15).

        Aqui não aparece a escolha entre "salvar o texto como está" e "seguir
        para o Anonimizar": quem entrou por este módulo já disse o que quer, e
        oferecer o arquivo com os CPFs inteiros seria oferecer o contrário.
        """
        self._conferindo = False
        # As páginas viram um texto só, separadas por linha em branco - o mesmo
        # arranjo com que elas vão para o arquivo (RN-12).
        self._abrir_revisao(arquivo_md.montar_conteudo(self.pdf.texto_conferido()))

    def receber_texto_conferido(self, caminho, paginas):
        """O texto conferido no Gerar OCR chega para ser revisado (RN-16).

        Chega por dentro do programa, sem arquivo no meio. Havendo revisão
        aberta e não salva - ou um PDF no meio do caminho aqui -, a pergunta
        antes de descartar vem primeiro: é outro documento chegando.
        """
        # Quem vem do Gerar OCR pediu uma coisa e pode ouvir falar de outra: a
        # pergunta é sobre o documento que já estava aqui. A linha a mais diz
        # onde ficou o texto que ela mandou seguir (revisão da etapa 8).
        if self.perguntar_antes_de_descartar(
                lambda: self.receber_texto_conferido(caminho, paginas),
                incluir_conferencia=True,
                lembrete=("O texto que você mandou seguir continua no Gerar "
                          "OCR, esperando.")):
            return
        self.faixa_do_topo.esconder()
        self.pdf.abandonar_leitura()
        self._conferindo = False
        self._origem = Path(caminho)
        self._salvo = False
        # O texto veio de um PDF: a quebra de linha do arquivo gravado é a
        # simples, e não tem de onde ser herdada.
        self._quebra_da_origem = arquivo_texto.QUEBRA_SIMPLES
        self._abrir_revisao(arquivo_md.montar_conteudo(paginas))

    def _abrir_revisao(self, texto):
        """O único jeito de abrir a revisão, venha o texto de onde vier.

        Os três caminhos terminam aqui - o arquivo de texto, o PDF lido neste
        módulo e o texto que chega do "Gerar OCR" -, para que um passo novo ao
        abrir a revisão nunca entre em dois deles e esqueça o terceiro.
        """
        self.tela_revisao.mostrar(self._origem.name, texto, cpf.procurar(texto))
        self.telas.setCurrentWidget(self.tela_revisao)

    def encerrar(self):
        """Para a leitura de PDF em andamento antes de o programa fechar.

        Uma leitura deixada rodando enquanto a janela é desmontada derruba o
        programa, e o Windows mostra a caixa de "parou de funcionar".
        """
        self.pdf.abandonar_leitura()

    def _comecou_a_conferencia(self):
        self._conferindo = True

    def _ha_conferencia_aberta(self):
        """Há texto de PDF na conferência, que se perderia ao sair?

        Da conferência para trás, o trabalho perdido é uma leitura e as
        correções feitas à mão - para ter tudo de volta, seria preciso ler o
        documento de novo.
        """
        return self._conferindo and any(self.pdf.texto_conferido())

    def _leitura_foi_cancelada(self, pagina):
        """Cancelar a leitura volta à escolha do arquivo, e diz o que houve."""
        self._origem = None
        self._salvo = False
        self.faixa_do_topo.mostrar(
            f"Leitura cancelada na página {pagina}. Nada foi gravado, e o "
            "documento original não foi tocado."
        )
        self.telas.setCurrentWidget(self.tela_escolher)

    # ------------------------------------------- antes de descartar a revisão

    TITULO_DA_PERGUNTA = "A revisão deste documento ainda não foi salva"
    O_QUE_SE_PERDE = (
        "{resumo}.\n\nSe você seguir, a revisão é descartada, e isso não se "
        "desfaz. O documento de origem continua intacto, mas, para ter a "
        "revisão de volta, seria preciso abri-lo de novo e refazer o que você "
        "decidiu."
    )

    def tem_revisao_nao_salva(self):
        """Há trabalho de revisão que se perderia agora?

        A conferência olha o que existe - uma revisão com texto, ainda não
        gravada -, e não em que tela a pessoa está. Olhando a tela, a proteção
        sumia no pior momento: com a própria pergunta na tela, fechar a janela
        ou soltar outro arquivo descartava tudo em silêncio, porque a tela da
        pergunta não era nenhuma das que contavam (revisão da etapa 6).

        Salva, não há o que perder; descartada, também não - nos dois casos o
        texto da revisão já saiu de cena.

        Num documento em que nada foi encontrado e nada foi mascarado à mão
        também não há o que perder: abri-lo de novo é imediato. Perguntar ali
        seria a pergunta que aparece sem motivo, e é ela que ensina a clicar em
        "descartar" sem ler - aí, na vez em que houver o que perder, ninguém lê
        (revisão da etapa 6). Com o PDF da etapa 7 a conta muda sozinha: achado
        um número que seja, a pergunta volta a aparecer.
        """
        if self._salvo or not self.tela_revisao.texto_mascarado():
            return False
        return bool(self.tela_revisao.tem_o_que_perder())

    def perguntar_antes_de_descartar(self, acao,
                                     rotulo_descartar="Descartar e seguir",
                                     incluir_conferencia=False, lembrete=None):
        """Segura a ação e pergunta, quando ela jogaria fora trabalho.

        Devolve se perguntou. São duas perguntas, e a ordem aqui é a ordem em
        que elas aparecem na vida: primeiro a da revisão, que é o caso comum;
        depois a da conferência de um PDF, que só vale para quem está abrindo
        outro documento; e, não havendo o que perder, não se pergunta nada -
        pergunta que aparece sem motivo ensina a clicar em "sim" sem ler, e aí
        ela não protege na vez em que importa.

        `incluir_conferencia` separa as duas situações da tabela do rascunho 08
        (estado 11): "anonimizar outro documento" e arrastar outro arquivo
        perguntam durante a conferência; trocar de item no menu e fechar a
        janela, não - ali nada se perde, e voltando a conferência está como
        estava.

        Quem fecha a janela vê "Fechar sem salvar" no lugar de "Descartar e
        seguir": é o mesmo risco, dito com a palavra do que a pessoa pediu.
        """
        if self.tem_revisao_nao_salva():
            return self._perguntar_pela_revisao(acao, rotulo_descartar)
        if incluir_conferencia and self._ha_conferencia_aberta():
            return self._perguntar_pela_conferencia(acao, lembrete)
        return False

    def _perguntar_pela_revisao(self, acao, rotulo_descartar):
        self._guardar_de_onde_veio(acao)
        self.tela_descartar.mostrar(
            self.TITULO_DA_PERGUNTA,
            self.O_QUE_SE_PERDE.format(
                resumo=f"{self._origem.name} — "
                       f"{self.tela_revisao.resumo_do_que_se_perde()}"),
            rotulo_descartar,
        )
        self.telas.setCurrentWidget(self.tela_descartar)
        return True

    def _perguntar_pela_conferencia(self, acao, lembrete=None):
        self._guardar_de_onde_veio(acao)
        # As mesmas palavras do Gerar OCR, nas mesmas condições (rascunho 08,
        # tabela do estado 11): é o mesmo trabalho em risco.
        resumo = resumo_do_documento(
            self._origem.name, len(self.pdf.texto_conferido()),
            self.pdf.tela_conferencia.paginas_corrigidas())
        self.tela_descartar.mostrar(
            "O texto deste documento ainda não foi salvo",
            f"{resumo}.\n\n"
            "Se você seguir, o texto e as correções são descartados, e isso não "
            "se desfaz. Para ter o texto de volta, seria preciso ler o documento "
            "de novo e refazer as correções."
            + (f"\n\n{lembrete}" if lembrete else ""),
        )
        self.telas.setCurrentWidget(self.tela_descartar)
        return True

    def _guardar_de_onde_veio(self, acao):
        """Guarda o que fazer depois, e a tela para onde o "Voltar" devolve.

        Com a pergunta já na tela - outro arquivo solto por cima dela -, o lugar
        para onde voltar continua sendo o de antes. Guardando a própria pergunta,
        o "Voltar e salvar" ficava sem sair do lugar, e a única saída que
        funcionava era a que joga o trabalho fora (lição do "Gerar OCR").
        """
        self._acao_pendente = acao
        if self.telas.currentWidget() is not self.tela_descartar:
            self._tela_antes_da_pergunta = self.telas.currentWidget()

    def _descartar_e_seguir(self):
        acao = self._acao_pendente
        self._acao_pendente = None
        # A revisão sai de cena antes de a ação rodar, e o painel volta ao
        # começo. Duas razões: a ação - abrir outro arquivo, trocar de módulo,
        # fechar a janela - não esbarra de novo na mesma pergunta; e quem sai
        # para outro módulo e volta encontra a tela de escolher o arquivo, e
        # não a pergunta velha, que já não leva a lugar nenhum (revisão da
        # etapa 6).
        self._voltar_para_escolher_agora()
        if acao is not None:
            acao()

    def _voltar_de_onde_estava(self):
        """Volta exatamente para a tela em que a pessoa estava, com tudo intacto."""
        self._acao_pendente = None
        self.telas.setCurrentWidget(
            self._tela_antes_da_pergunta or self.tela_revisao)

    # ------------------------------------------------------ arrastar e soltar

    def dragEnterEvent(self, evento):
        if self._arquivo_arrastado(evento):
            evento.acceptProposedAction()

    def dropEvent(self, evento):
        caminho = self._arquivo_arrastado(evento)
        if caminho:
            evento.acceptProposedAction()
            self.receber_arquivo(caminho)

    def _arquivo_arrastado(self, evento):
        """Devolve o caminho do arquivo arrastado, ou None quando não serve.

        Só um arquivo por vez: vários de uma vez é justamente o caso que a spec
        deixou de fora, e aceitar em silêncio o primeiro da pilha seria pior que
        recusar.
        """
        dados = evento.mimeData()
        if not dados.hasUrls() or len(dados.urls()) != 1:
            return None
        url = dados.urls()[0]
        if not url.isLocalFile():
            return None
        caminho = Path(url.toLocalFile())
        return caminho if caminho.suffix.lower() in EXTENSOES_ACEITAS else None


def _e_o_mesmo_arquivo(destino, origem):
    """Diz se os dois caminhos são o mesmo arquivo em disco.

    Comparar o texto dos caminhos não basta: o Windows não liga para maiúsculas,
    e a mesma pasta chega escrita de jeitos diferentes conforme a pessoa digite,
    arraste ou use o seletor.
    """
    if origem is None:
        return False
    try:
        destino, origem = Path(destino).resolve(), Path(origem).resolve()
    except OSError:
        return False
    return os.path.normcase(str(destino)) == os.path.normcase(str(origem))


class _TelaErro(QWidget):
    """O arquivo que não serve: uma frase, e o caminho de volta.

    É o mesmo desenho do erro aprovado no "Gerar OCR". A caixa e o texto têm
    largura fixa, e a altura é calculada a partir dela a cada frase: sem isso o
    Qt reserva a altura de uma linha só e o fim da explicação some para fora da
    borda, sem nenhum sinal de que faltou pedaço.
    """

    LARGURA_DA_CAIXA = 460
    LARGURA_DO_TEXTO = 400

    def __init__(self, ao_escolher_outro):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        caixa = QFrame()
        caixa.setObjectName("caixa_de_erro")
        caixa.setFixedWidth(self.LARGURA_DA_CAIXA)
        caixa.setStyleSheet(
            f"""
            QFrame#caixa_de_erro {{
                background-color: rgba(217, 83, 79, 26);
                border-left: 4px solid {estilo.COR_ERRO};
                border-radius: {estilo.RAIO}px;
            }}
            """
        )
        dentro = QVBoxLayout(caixa)
        dentro.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_3,
                                  estilo.ESPACO_4, estilo.ESPACO_3)
        dentro.setSpacing(estilo.ESPACO_2)

        titulo = QLabel("Não foi possível usar este arquivo")
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO}; border: none; background: transparent;"
        )
        self.explicacao = QLabel()
        self.explicacao.setWordWrap(True)
        self.explicacao.setFixedWidth(self.LARGURA_DO_TEXTO)
        self.explicacao.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
            "border: none; background: transparent;"
        )
        dentro.addWidget(titulo)
        dentro.addWidget(self.explicacao)

        botao = QPushButton("Escolher outro arquivo")
        botao.setCursor(Qt.PointingHandCursor)
        botao.setStyleSheet(estilo.estilo_botao(principal=True))
        botao.clicked.connect(ao_escolher_outro)

        linha_botao = QHBoxLayout()
        linha_botao.addStretch()
        linha_botao.addWidget(botao)
        linha_botao.addStretch()

        layout.addWidget(caixa, alignment=Qt.AlignCenter)
        layout.addSpacing(estilo.ESPACO_4)
        layout.addLayout(linha_botao)

    def mostrar(self, motivo):
        self.explicacao.setText(motivo)
        self.explicacao.setMinimumHeight(
            self.explicacao.heightForWidth(self.LARGURA_DO_TEXTO)
        )

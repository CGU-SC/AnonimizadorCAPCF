"""A tela de revisão do Anonimizar: o texto já mascarado, com cada troca destacada.

É a tela que dá razão ao módulo. Ela aparece sempre, com CPF ou sem (regra
RN-7), e aqui não se digita: o texto é só de leitura (RN-8). Corrigir a leitura
é trabalho da conferência do OCR.

Segue os rascunhos aprovados mockups/anonimizar/01-revisar-antes-de-salvar.html
e 08-escolher-e-salvar.html. Duas coisas mudaram depois deles, na conferência
da etapa 2 e registradas em mockups/sistema-de-design.md, em 16/09/2026: o
rótulo na tela, que era "forma CPF válido" e virou "CPF válido", e a cor dele,
que é o vermelho de letra.

A lista do que o programa achou fica ao lado do texto, e a navegação "anterior /
próximo" fica acima dele (acréscimo da spec 003, 17/09/2026). Mascarar à mão e
salvar entram nas etapas seguintes.
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

from dataclasses import dataclass
from typing import NamedTuple

import cpf
import estilo
import tipos_na_tela
from dupla_conferencia import liberar_mesmo_assim
from lista_de_achados import ListaDeAchados, contexto

AVISO_SEM_CPF = "Nenhum CPF encontrado neste texto"


@dataclass(frozen=True)
class Liberado:
    """Um número que passa na conta e vai inteiro para o arquivo (regra RN-11).

    A tela de salvar mostra os três pedaços: o número como está escrito no
    texto, o que vem antes dele, e o nome do tipo.
    """
    original: str
    contexto: str
    etiqueta: str

# Os grupos dos selos e da navegação, cada um com quem pertence a ele e como ele
# se chama na posição ("2 de 3 CPFs válidos"). Eles são separados: cada número
# está em um só, e a soma dos três dá o total encontrado. Um suspeito liberado
# sai de "suspeitos" e entra em "liberados" (conferência da etapa 3, 17/09/2026:
# com os grupos sobrepostos, a navegação pelos suspeitos passava pelos liberados
# e o selo de suspeitos não diminuía, e a conta não fechava para quem olha).
VALIDOS = "validos"
SUSPEITOS = "suspeitos"
LIBERADOS = "liberados"
A_MAO = "a_mao"
# O nome e a cor de cada grupo saem do `tipos_na_tela`, e não são escritos aqui:
# o nome de um tipo já mudou duas vezes em quatro dias, e com ele escrito em
# cada tela a lista e o aviso de antes de gravar podiam divergir.
_VALIDO = tipos_na_tela.POR_TIPO[cpf.PASSA_NA_CONTA]
_A_MAO = tipos_na_tela.POR_TIPO[cpf.MASCARADO_A_MAO]
class Grupo(NamedTuple):
    """Um grupo da revisão: quem pertence a ele, e como ele se chama na tela."""

    pertence: "callable"
    nome: str
    plural: str


GRUPOS = {
    VALIDOS: Grupo(
        lambda o: o.tipo == cpf.PASSA_NA_CONTA and o.situacao == cpf.MASCARADO,
        _VALIDO.nome, _VALIDO.plural),
    SUSPEITOS: Grupo(
        lambda o: o.suspeito and o.situacao == cpf.MASCARADO,
        tipos_na_tela.SUSPEITO.nome, tipos_na_tela.SUSPEITO.plural),
    A_MAO: Grupo(
        lambda o: o.tipo == cpf.MASCARADO_A_MAO and o.situacao == cpf.MASCARADO,
        _A_MAO.nome, _A_MAO.plural),
    LIBERADOS: Grupo(
        lambda o: o.situacao == cpf.LIBERADO,
        tipos_na_tela.LIBERADO.nome, tipos_na_tela.LIBERADO.plural),
}


def quantos_em_cada_grupo(ocorrencias):
    """Quantos números há em cada grupo, agora.

    A conta é feita num lugar só porque as três telas que a usam - os selos, a
    contagem do salvar e a do que se perde - precisam contar a mesma coisa.
    """
    return {nome: sum(1 for o in ocorrencias if grupo.pertence(o))
            for nome, grupo in GRUPOS.items()}


class TelaRevisao(QWidget):
    # O aviso de "nenhum CPF" tem largura fixa, e a altura dele é calculada a
    # partir dela: frase com quebra de linha dentro de caixa de largura limitada
    # sai cortada no Qt, e ninguém percebe que faltou pedaço.
    LARGURA_DO_AVISO = 620
    LARGURA_DO_TEXTO_DO_AVISO = 580

    def __init__(self, ao_anonimizar_outro, ao_salvar=None):
        super().__init__()
        self._ocorrencias = []
        self._texto = ""
        # Qual número da lista a navegação está mostrando. Começa sem nenhum:
        # o primeiro "próximo" leva ao primeiro número do texto.
        self._atual = None
        # Liga enquanto o programa mexe na seleção do texto. Sem isso, a seleção
        # que ele faz para mostrar um número acenderia o botão de mascarar à mão
        # como se a pessoa tivesse marcado algo (revisão da etapa 4).
        self._selecionando = False
        # O grupo que a navegação está percorrendo; None é todos.
        self._filtro = None

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
        self.texto.selectionChanged.connect(self._trecho_marcado_mudou)

        self.lista = ListaDeAchados(
            ao_ir_para=self.ir_para,
            ao_liberar=self.liberar,
            ao_mascarar_de_novo=self.mascarar_de_novo,
        )
        metades = QHBoxLayout()
        metades.setSpacing(estilo.ESPACO_3)
        metades.addWidget(self.texto, stretch=1)
        metades.addWidget(self.lista)
        layout.addLayout(metades, stretch=1)
        layout.addSpacing(estilo.ESPACO_3)

        rodape = QHBoxLayout()
        rodape.setSpacing(estilo.ESPACO_3)
        # O salvar fica liberado desde o começo, sem exigir passar por todos os
        # números (regra RN-7): o programa já mascarou tudo o que achou, e quem
        # confia no que viu não precisa ser obrigado a clicar mais.
        self.botao_salvar = QPushButton("Salvar o texto mascarado…")
        self.botao_salvar.setCursor(Qt.PointingHandCursor)
        self.botao_salvar.setStyleSheet(estilo.estilo_botao(principal=True))
        if ao_salvar is not None:
            # O clique do Qt manda um argumento junto ("o botão está apertado?"),
            # e ele chegaria no lugar do primeiro parâmetro de quem for chamado.
            # Foi o que aconteceu aqui: o argumento caía no caminho de destino e
            # a tela de salvar morria calada, sem nada acontecer no clique.
            self.botao_salvar.clicked.connect(lambda _=False: ao_salvar())
        rodape.addWidget(self.botao_salvar)
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
        # Clicar num selo faz a navegação percorrer só aquele grupo (acréscimo
        # da spec 003, 17/09/2026). O dos encontrados volta a percorrer todos.
        self.selo_encontrados = _Selo(ao_clicar=lambda: self.filtrar(None))
        # Cada selo na cor do que ele conta, para bater com o texto ao lado.
        self.selo_validos = _Selo(cor=_VALIDO.cor,
                                  ao_clicar=lambda: self.filtrar(VALIDOS))
        self.selo_suspeitos = _Selo(cor=tipos_na_tela.SUSPEITO.cor,
                                    ao_clicar=lambda: self.filtrar(SUSPEITOS))
        # Azul: o "à mão" é marca de quem revisa, e não do que o programa achou.
        self.selo_a_mao = _Selo(cor=_A_MAO.cor,
                                ao_clicar=lambda: self.filtrar(A_MAO))
        # Verde a pedido da usuária (17/09/2026): marca uma decisão da pessoa.
        self.selo_liberados = _Selo(cor=tipos_na_tela.LIBERADO.cor,
                                    ao_clicar=lambda: self.filtrar(LIBERADOS))

        linha.addWidget(titulo)
        linha.addWidget(self.selo_encontrados)
        linha.addWidget(self.selo_validos)
        linha.addWidget(self.selo_suspeitos)
        linha.addWidget(self.selo_a_mao)
        linha.addWidget(self.selo_liberados)
        linha.addStretch()
        return linha

    def _montar_chave_de_cores(self):
        linha = QHBoxLayout()
        linha.setSpacing(estilo.ESPACO_4)
        self.chave_valido = _amostra_da_chave(
            _VALIDO.nome, ondulado=False, cor=_VALIDO.cor)
        self.chave_suspeito = _amostra_da_chave(
            tipos_na_tela.SUSPEITO.nome, ondulado=True,
            cor=tipos_na_tela.SUSPEITO.cor)
        self.chave_a_mao = _amostra_da_chave(
            _A_MAO.nome, ondulado=False, cor=_A_MAO.cor, pontilhado=True)
        linha.addWidget(self.chave_valido)
        linha.addWidget(self.chave_suspeito)
        linha.addWidget(self.chave_a_mao)
        linha.addStretch()

        # O aviso de trecho sem dígito fica ao lado do botão, onde o olho está,
        # e não numa caixa por cima para fechar. Some quando a pessoa marca
        # outro trecho (rascunho 01, estado 3).
        self.aviso_do_trecho = QLabel()
        self.aviso_do_trecho.setVisible(False)
        self.aviso_do_trecho.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; color: {estilo.COR_ALERTA};"
        )
        self.botao_mascarar = QPushButton("Mascarar o trecho marcado")
        self.botao_mascarar.setCursor(Qt.PointingHandCursor)
        self.botao_mascarar.setStyleSheet(estilo.estilo_botao(principal=False,
                                                              pequeno=True))
        self.botao_mascarar.clicked.connect(self.mascarar_o_trecho_marcado)
        # Botão que parece pronto e não faz nada é lido como defeito: ele só
        # acende quando há trecho marcado.
        self.botao_mascarar.setEnabled(False)
        linha.addWidget(self.aviso_do_trecho)
        linha.addWidget(self.botao_mascarar)

        # A navegação pelos números, para passar o documento de cima a baixo
        # sem rolar (acréscimo da spec 003, de 17/09/2026). Ela percorre a lista
        # inteira na ordem do texto, e não só os suspeitos: assim o "N de M"
        # bate com o que a lista mostra.
        self.botao_anterior = QPushButton("‹ anterior")
        self.botao_proximo = QPushButton("próximo ›")
        for botao, passo in ((self.botao_anterior, -1), (self.botao_proximo, 1)):
            botao.setCursor(Qt.PointingHandCursor)
            botao.setStyleSheet(estilo.estilo_botao(principal=False, pequeno=True))
            botao.clicked.connect(lambda _=False, p=passo: self.andar(p))
        self.posicao = QLabel()
        self.posicao.setAlignment(Qt.AlignCenter)
        self.posicao.setMinimumWidth(70)
        self.posicao.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
        )
        linha.addWidget(self.botao_anterior)
        linha.addWidget(self.posicao)
        linha.addWidget(self.botao_proximo)
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
        # O `ensurePolished` antes da conta: sem ele o Qt mede a frase com a
        # fonte padrão, e não com a do estilo - e a última linha some para fora
        # da borda, sem nada acusar.
        self.explicacao_sem_cpf.ensurePolished()
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
        # O texto de origem fica guardado porque a tela é redesenhada a cada
        # máscara desfeita ou refeita - e ela se redesenha a partir do original,
        # nunca do que já está na tela.
        self._texto = texto
        self._atual = None
        self._filtro = None
        self.legenda.setText(
            f"{nome_da_origem} — arquivo de texto. Aqui não se digita: só se "
            "mascara e se desfaz a máscara."
        )
        self._desenhar()

    def ir_para(self, ocorrencia):
        """Leva o texto até o número e marca o item dele na lista."""
        cursor = self.texto.textCursor()
        cursor.setPosition(_posicao_no_qt(self._texto, ocorrencia.inicio))
        cursor.setPosition(
            _posicao_no_qt(self._texto, ocorrencia.fim), QTextCursor.KeepAnchor)
        self._selecionando = True
        self.texto.setTextCursor(cursor)
        self._selecionando = False
        self.texto.ensureCursorVisible()
        self.lista.marcar(ocorrencia)
        self._atual = ocorrencia
        self._atualizar_navegacao()

    def filtrar(self, grupo):
        """Faz a navegação percorrer só um grupo - ou todos, com `None`.

        Escolher um grupo leva direto ao primeiro número dele (pedido na
        conferência da etapa 3): quem clica em "liberados" quer ver o primeiro
        liberado, e não o que por acaso estiver perto de onde estava.

        Clicar de novo no selo que já está aceso só desliga o filtro, sem mudar
        de lugar: é o "desmarcar", e não a escolha de outro grupo. O texto e a
        lista não mudam em nenhum dos casos - nada some da tela.
        """
        desligando = grupo is not None and grupo == self._filtro
        self._filtro = None if desligando else grupo
        numeros = self._em_ordem()
        if not desligando and numeros:
            self.ir_para(numeros[0])
        else:
            self._atualizar_navegacao()

    def andar(self, passo):
        """Vai ao número anterior (-1) ou ao seguinte (+1), na ordem do texto.

        O passo é contado a partir do número que está sendo olhado agora, e não
        de uma posição guardada: assim, se a pessoa clicou na lista num número
        de outro grupo, ou se o número acabou de sair do grupo, o "próximo"
        segue dali, e não volta ao começo.
        """
        numeros = self._em_ordem()
        if not numeros:
            return
        # A navegação dá a volta: depois do último vem o primeiro, e antes do
        # primeiro vem o último (pedido na conferência da etapa 3). Quem revisa
        # um documento costuma dar mais de uma passada, e botão apagado no fim
        # obrigaria a voltar clicando um por um.
        if self._atual is None:
            destino = numeros[0] if passo > 0 else numeros[-1]
        elif passo > 0:
            destino = next((o for o in numeros if o.inicio > self._atual.inicio),
                           numeros[0])
        else:
            antes = [o for o in numeros if o.inicio < self._atual.inicio]
            destino = antes[-1] if antes else numeros[-1]
        self.ir_para(destino)

    def _em_ordem(self):
        """Os números que a navegação percorre agora, na ordem do texto."""
        numeros = sorted(self._ocorrencias, key=lambda o: o.inicio)
        if self._filtro is None:
            return numeros
        pertence = GRUPOS[self._filtro].pertence
        return [o for o in numeros if pertence(o)]

    def _atualizar_navegacao(self):
        # Um grupo que ficou vazio - o último liberado foi mascarado de novo -
        # desliga o filtro sozinho: o selo dele some, e não teria como desligar.
        if self._filtro is not None and not self._em_ordem():
            self._filtro = None
        for grupo, selo in ((None, self.selo_encontrados), (VALIDOS, self.selo_validos),
                            (SUSPEITOS, self.selo_suspeitos), (A_MAO, self.selo_a_mao),
                            (LIBERADOS, self.selo_liberados)):
            selo.acender(self._filtro is not None and grupo == self._filtro)

        # Sem nenhum número, a navegação não tem para onde ir - e botão que não
        # leva a lugar nenhum é lido como defeito.
        for peca in (self.botao_anterior, self.posicao, self.botao_proximo):
            peca.setVisible(bool(self._ocorrencias))

        numeros = self._em_ordem()
        indice = next((i for i, o in enumerate(numeros) if o is self._atual), None)
        atual = "—" if indice is None else str(indice + 1)
        total = len(numeros)
        grupo = ""
        if self._filtro is not None:
            do_filtro = GRUPOS[self._filtro]
            grupo = " " + (do_filtro.nome if total == 1 else do_filtro.plural)
        self.posicao.setText(f"{atual} de {total}{grupo}")

        # Com a volta, sempre há para onde ir enquanto o grupo tiver algum número.
        self.botao_anterior.setEnabled(bool(numeros))
        self.botao_proximo.setEnabled(bool(numeros))

    def liberar(self, ocorrencia):
        """Desfaz a máscara de um número - com a pergunta antes, quando ela cabe.

        Um clique basta para o suspeito que falha na conta e para a máscara
        feita à mão. Todo número que passa na conta pede a dupla conferência
        (regra RN-10): é o que menos pode sair do programa por engano.
        """
        if ocorrencia.pede_dupla_conferencia and not liberar_mesmo_assim(
                ocorrencia, self):
            return
        ocorrencia.situacao = cpf.LIBERADO
        self._desenhar()
        self.ir_para(ocorrencia)

    def mascarar_o_trecho_marcado(self):
        """Mascara o que a pessoa marcou com o mouse (regra RN-9).

        É a rede para o CPF que o programa não pegou - escrito de um jeito que
        a spec deixou de fora, ou estragado demais pela leitura.
        """
        cursor = self.texto.textCursor()
        if not cursor.hasSelection():
            return
        inicio = _posicao_no_texto(self._texto, cursor.selectionStart())
        fim = _posicao_no_texto(self._texto, cursor.selectionEnd())

        # Trecho que encosta num número já mascarado fica de fora: duas máscaras
        # em cima do mesmo pedaço deixariam a lista dizendo duas coisas sobre o
        # mesmo número, e não há nada a ganhar - aquele número já está escondido.
        if any(o.inicio < fim and inicio < o.fim for o in self._ocorrencias):
            self._avisar_sobre_o_trecho(
                "⚠ Esse trecho encosta num número que já está na lista.")
            return

        ocorrencia = cpf.mascarar_a_mao(self._texto, inicio, fim)
        if ocorrencia is None:
            self._avisar_sobre_o_trecho(
                "⚠ O trecho marcado não tem nenhum dígito. Nada foi mascarado.")
            return
        self._ocorrencias.append(ocorrencia)
        # Na ordem do texto, e não na de criação: a lista e a navegação andam
        # por essa ordem, e fora dela o item aceso deixa de ser o que a posição
        # "N de M" indica (revisão da etapa 4).
        self._ocorrencias.sort(key=lambda o: o.inicio)
        self._desenhar()
        self.ir_para(ocorrencia)

    def _avisar_sobre_o_trecho(self, frase):
        self.aviso_do_trecho.setText(frase)
        self.aviso_do_trecho.setVisible(True)

    def _trecho_marcado_mudou(self):
        if self._selecionando:
            return
        self.botao_mascarar.setEnabled(self.texto.textCursor().hasSelection())
        self.aviso_do_trecho.setVisible(False)

    def mascarar_de_novo(self, ocorrencia):
        """Arrependimento custa um clique, sem pergunta nenhuma."""
        ocorrencia.situacao = cpf.MASCARADO
        self._desenhar()
        self.ir_para(ocorrencia)

    def _desenhar(self):
        self._escrever(self._texto)
        self.lista.mostrar(self._texto, self._ocorrencias)
        self._atualizar_contagem()
        self._atualizar_navegacao()

    def texto_mascarado(self):
        """O texto como ele está na tela."""
        return self.texto.toPlainText()

    def texto_para_o_arquivo(self):
        """O texto que vai para o arquivo: o do documento, com as máscaras.

        Calculado do texto de origem, e não copiado da caixa de leitura da tela
        (revisão da etapa 5). A caixa é um desenho: ela troca o separador de
        linha U+2028, que aparece em texto copiado de PDF, por uma quebra de
        linha comum - e o arquivo sairia diferente do documento num ponto que
        ninguém mandou mudar, sem nada acusar. Quem manda no arquivo é o motor,
        que promete devolver o texto inteiro com as máscaras no lugar (RN-12).
        """
        return cpf.aplicar(self._texto, self._ocorrencias)

    def liberados_que_passam_na_conta(self):
        """Os números que a pessoa soltou e que passam na conta (regra RN-11).

        São os que a tela de salvar mostra antes de gravar, um a um, com as
        palavras que vêm antes deles no texto - as mesmas da lista, que é como
        a pessoa reconhece qual número é qual. Os que falham na conta ficam de
        fora: soltar um deles é o caso comum, e listar todos ensinaria a passar
        direto pelo aviso.
        """
        return [
            Liberado(
                original=o.original,
                contexto=contexto(self._texto, o),
                # O "quase CPF" que passa na conta leva a etiqueta que ele tem
                # na lista, e não o nome do tipo: os dois nomes tratam do mesmo
                # número, e trocar de nome entre uma tela e outra confunde.
                etiqueta=(tipos_na_tela.VALIDO_SE_CORRIGIDO.nome
                          if o.tipo == cpf.QUASE_CPF else _VALIDO.nome),
            )
            for o in self._em_ordem_no_texto()
            if o.situacao == cpf.LIBERADO and o.passa_na_conta
        ]

    def resumo_do_que_sai(self, por_tipo=True):
        """Uma frase com o que vai mascarado no arquivo.

        Vai na tela de salvar, que é a última em que dá para voltar atrás: a
        contagem ali é o que permite perceber, antes de gravar, que o documento
        tinha bem mais CPF do que o programa achou. Na tela de sucesso ela vem
        sem a separação por tipo (`por_tipo=False`): lá já não há o que decidir.
        """
        contas = quantos_em_cada_grupo(self._ocorrencias)
        mascarados = sum(contas.values())
        if not mascarados:
            return "Nenhum número foi mascarado neste texto."
        quantos = (f"{mascarados} números mascarados" if mascarados != 1
                   else "1 número mascarado")
        if not por_tipo:
            return f"{quantos}."
        partes = []
        for grupo in (VALIDOS, SUSPEITOS, A_MAO):
            if contas[grupo]:
                do_grupo = GRUPOS[grupo]
                partes.append(f"{contas[grupo]} "
                              f"{do_grupo.nome if contas[grupo] == 1 else do_grupo.plural}")
        frase = f"{quantos}: {_juntar(partes)}."
        # A frase do caso bom é dita com todas as letras, e não pelo silêncio:
        # sem ela, não dava para diferenciar "nada foi liberado" de "o programa
        # não conferiu isso" (rascunho 08, estado 6).
        if not self.liberados_que_passam_na_conta():
            frase += f" Nenhum número com {_VALIDO.nome} foi liberado."
        return frase

    def tem_o_que_perder(self):
        """Há algo nesta revisão que valha uma pergunta antes de descartar?

        Nenhum número encontrado e nada mascarado à mão: não há. O texto do
        documento não se perde - ele continua no arquivo de origem, que o
        programa nunca altera.
        """
        return bool(self._ocorrencias)

    def resumo_do_que_se_perde(self):
        """O que some se a revisão for descartada, contado por tipo.

        O que a pessoa fez à mão vem separado do que o programa fez sozinho:
        máscara que o programa refaz em um instante não é perda, e decisão dela
        - um número liberado, um trecho mascarado à mão - é.
        """
        contas = quantos_em_cada_grupo(self._ocorrencias)
        mascarados = contas[VALIDOS] + contas[SUSPEITOS] + contas[A_MAO]
        frase = (f"{mascarados} números mascarados" if mascarados != 1
                 else "1 número mascarado")
        dela = []
        if contas[LIBERADOS]:
            dela.append(f"{contas[LIBERADOS]} liberado"
                        + ("s" if contas[LIBERADOS] > 1 else ""))
        if contas[A_MAO]:
            dela.append(f"{contas[A_MAO]} mascarado"
                        + ("s" if contas[A_MAO] > 1 else "") + " à mão")
        if dela:
            frase += f", {_juntar(dela)} por você"
        return frase

    def _em_ordem_no_texto(self):
        return sorted(self._ocorrencias, key=lambda o: o.inicio)

    def esquecer(self):
        self._ocorrencias = []
        self._texto = ""
        self._atual = None
        self._filtro = None
        self.texto.clear()
        self.lista.mostrar("", [])
        self._atualizar_navegacao()

    # -------------------------------------------------------------- por dentro

    def _escrever(self, texto):
        """Põe o texto mascarado na tela, com cada troca destacada no lugar dela.

        O destaque é desenhado sobre as mesmas posições do texto original,
        porque a máscara não muda o tamanho de nada (regra RN-6).
        """
        mascarado = cpf.aplicar(texto, self._ocorrencias)
        self.texto.setPlainText(mascarado)

        cursor = self.texto.textCursor()
        # Antes dos destaques, o documento inteiro volta à formatação comum. Sem
        # isso, o Qt reaproveita a que estava debaixo do cursor - e, se ele tinha
        # acabado de passar por um número destacado, o texto inteiro saía
        # amarelo e sublinhado depois de um "Desfazer" (conferência da etapa 3).
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
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
        # O que foi liberado volta ao texto como estava, com traço tracejado:
        # ele não sumiu da revisão, e continua na lista para ser mascarado de
        # novo com um clique.
        for ocorrencia in self._ocorrencias:
            if ocorrencia.situacao != cpf.LIBERADO:
                continue
            cursor.setPosition(_posicao_no_qt(texto, ocorrencia.inicio))
            cursor.setPosition(
                _posicao_no_qt(texto, ocorrencia.fim), QTextCursor.KeepAnchor)
            cursor.setCharFormat(_formato_de_liberado())
        # O cursor volta ao começo para a tela abrir no alto do documento.
        self.texto.moveCursor(QTextCursor.Start)

    def _atualizar_contagem(self):
        # Os grupos são separados, e a soma fecha: encontrados = CPFs válidos +
        # suspeitos + liberados. Liberar um suspeito tira ele de "suspeitos" e
        # põe em "liberados" - assim a pessoa soma os três e confere o total de
        # relance (decidido na conferência da etapa 3, em 17/09/2026).
        validos = [o for o in self._ocorrencias if GRUPOS[VALIDOS].pertence(o)]
        suspeitos = [o for o in self._ocorrencias if GRUPOS[SUSPEITOS].pertence(o)]
        a_mao = [o for o in self._ocorrencias if GRUPOS[A_MAO].pertence(o)]
        liberados = [o for o in self._ocorrencias if GRUPOS[LIBERADOS].pertence(o)]

        tem_cpf = bool(self._ocorrencias)
        self.aviso_sem_cpf.setVisible(not tem_cpf)

        # "Encontrados", e não "mascarados": com algo liberado, nem tudo o que
        # foi encontrado está mascarado, e o selo afirmaria algo falso justamente
        # sobre o que vai inteiro para o arquivo.
        encontrados = len(self._ocorrencias)
        self.selo_encontrados.setText(
            f"{encontrados} números encontrados" if encontrados != 1
            else "1 número encontrado"
        )
        self.selo_encontrados.setVisible(tem_cpf)
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
        self.selo_a_mao.setText(
            f"{len(a_mao)} mascarados à mão" if len(a_mao) != 1
            else "1 mascarado à mão"
        )
        self.selo_a_mao.setVisible(bool(a_mao))
        self.selo_liberados.setText(
            f"{len(liberados)} liberados por você" if len(liberados) != 1
            else "1 liberado por você"
        )
        # O selo só existe quando houve o que liberar: aviso que aparece sem
        # motivo ensina a não olhar para ele.
        self.selo_liberados.setVisible(bool(liberados))


def _juntar(partes):
    """Junta com vírgula e um "e" no fim, como se escreve em português."""
    if len(partes) == 1:
        return partes[0]
    return ", ".join(partes[:-1]) + f" e {partes[-1]}"


def _formato_de_liberado():
    """O traço de quem voltou ao original: tracejado, e verde.

    Ele fica visível de propósito - a pessoa precisa achar o número de novo para
    mascará-lo, e ver de relance o que está saindo inteiro do programa. Verde a
    pedido da usuária (conferência da etapa 3, 17/09/2026): cinza, num documento
    com muitos liberados, ficava difícil de achar depois. O traço tracejado é o
    que continua separando o liberado dos outros tipos para quem não distingue
    bem as cores.
    """
    formato = QTextCharFormat()
    cor = QColor(tipos_na_tela.LIBERADO.cor)
    formato.setForeground(cor)
    formato.setUnderlineColor(cor)
    formato.setUnderlineStyle(QTextCharFormat.DashUnderline)
    return formato


def _posicao_no_texto(texto, posicao_no_qt):
    """O caminho de volta: a posição do Qt virando posição do texto.

    Serve para o trecho que a pessoa marcou com o mouse - o Qt diz onde a
    seleção começa e termina na conta dele, e o resto do programa conta do
    jeito do Python.
    """
    andado = 0
    for indice, letra in enumerate(texto):
        if andado >= posicao_no_qt:
            return indice
        andado += 2 if ord(letra) > 0xFFFF else 1
    return len(texto)


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
    if ocorrencia.tipo == cpf.MASCARADO_A_MAO:
        # Traço próprio para o que a pessoa mascarou: azul e duplo, como o
        # rascunho aprovado mostra. Ele não é achado do programa, e misturá-lo
        # com o vermelho do "CPF válido" faria a contagem do alto mentir.
        cor = QColor(tipos_na_tela.POR_TIPO[cpf.MASCARADO_A_MAO].cor)
        traco = QTextCharFormat.DotLine
    elif ocorrencia.suspeito:
        cor = QColor(tipos_na_tela.SUSPEITO.cor)
        traco = QTextCharFormat.WaveUnderline
    else:
        cor = QColor(tipos_na_tela.POR_TIPO[cpf.PASSA_NA_CONTA].cor)
        traco = QTextCharFormat.SingleUnderline
    formato.setForeground(cor)
    formato.setUnderlineColor(cor)
    formato.setUnderlineStyle(traco)
    return formato


class _Selo(QLabel):
    """Um selo do alto da revisão: conta um grupo, e filtra a navegação por ele."""

    def __init__(self, cor=None, ao_clicar=None):
        super().__init__()
        self._cor = cor or estilo.COR_TEXTO_SECUNDARIO
        self._ao_clicar = ao_clicar
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Clique para navegar só por estes números")
        self.acender(False)
        self.setVisible(False)

    def acender(self, aceso):
        """O selo do grupo que a navegação está percorrendo fica aceso.

        Mesma borda e mesmo fundo azuis do item aceso na lista: é o sinal que o
        programa já usa para "é aqui que você está".
        """
        self.aceso = aceso
        borda = estilo.COR_DESTAQUE if aceso else estilo.COR_BORDA
        fundo = "rgba(59, 110, 165, 46)" if aceso else estilo.COR_FUNDO_ELEVADO
        self.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px; color: {self._cor};"
            f"background-color: {fundo}; border: 1px solid {borda};"
            "border-radius: 10px; padding: 2px 10px;"
        )

    def mousePressEvent(self, evento):
        if self._ao_clicar is not None:
            self._ao_clicar()
        super().mousePressEvent(evento)


def _amostra_da_chave(nome, ondulado, cor, pontilhado=False):
    """Um pedacinho "XXX" com o traço do tipo, e o nome dele ao lado.

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
    if pontilhado:
        traco = QTextCharFormat.DotLine
    elif ondulado:
        traco = QTextCharFormat.WaveUnderline
    else:
        traco = QTextCharFormat.SingleUnderline
    marcado.setUnderlineStyle(traco)
    comum = QTextCharFormat()
    comum.setForeground(QColor(estilo.COR_TEXTO_SECUNDARIO))

    cursor = amostra.textCursor()
    cursor.insertText(cpf.MASCARA * 3, marcado)
    cursor.insertText(f"  {nome}", comum)
    return amostra

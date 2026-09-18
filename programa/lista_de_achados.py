"""A lista do que o programa achou, ao lado do texto da revisão.

Os suspeitos vêm primeiro, porque são eles que pedem o olho da pessoa: o
programa não tem como saber se aquele número é CPF, e é olhando o original e as
palavras antes dele que se decide.

A lista mostra o número **como estava escrito**, e não mascarado. Sem isso não
há como decidir - e é só aqui que ele aparece: o arquivo gravado leva a máscara.

Segue os rascunhos aprovados mockups/anonimizar/01-revisar-antes-de-salvar.html
(a lista em seções, o jeito A) e 08-escolher-e-salvar.html.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import cpf
import estilo

LARGURA = 330

# O que sobra dentro de um item para as etiquetas: a coluna, menos a barra de
# rolagem (10), a folga da direita, os respiros do próprio item e as bordas dele.
LARGURA_UTIL_DO_ITEM = LARGURA - 10 - estilo.ESPACO_2 - 2 * estilo.ESPACO_3 - 4

# Quantas letras do texto antes do número entram no item. Curto o bastante para
# caber numa linha, e longo o bastante para mostrar a palavra que denuncia o que
# o número é - "Termo de outorga nº" diz que aquilo não é CPF de ninguém.
LETRAS_DE_CONTEXTO = 38


class ListaDeAchados(QScrollArea):
    """A coluna da direita: as seções, os itens e os botões de cada um."""

    def __init__(self, ao_ir_para, ao_liberar, ao_mascarar_de_novo):
        super().__init__()
        self._ao_ir_para = ao_ir_para
        self._ao_liberar = ao_liberar
        self._ao_mascarar_de_novo = ao_mascarar_de_novo
        self._itens = {}

        self.setFixedWidth(LARGURA)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(
            f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
            QScrollBar::handle:vertical {{
                background: {estilo.COR_BORDA}; border-radius: 5px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
            """
        )

        self._dentro = QWidget()
        self._layout = QVBoxLayout(self._dentro)
        self._layout.setContentsMargins(0, 0, estilo.ESPACO_2, 0)
        self._layout.setSpacing(estilo.ESPACO_2)
        self.setWidget(self._dentro)

    def mostrar(self, texto, ocorrencias):
        """Monta a lista inteira de novo, na ordem das seções."""
        self._limpar()
        self._itens = {}

        suspeitos = [o for o in ocorrencias if o.suspeito]
        validos = [o for o in ocorrencias if o.tipo == cpf.PASSA_NA_CONTA]
        a_mao = [o for o in ocorrencias if o.tipo == cpf.MASCARADO_A_MAO]

        self._layout.addWidget(_titulo_da_lista("O que o programa achou"))
        if not ocorrencias:
            self._layout.addWidget(_nada_para_olhar())
        # O número do título conta o que continua mascarado, igual ao selo do
        # alto; o item liberado continua listado no mesmo lugar, para ser
        # mascarado de novo com um clique (conferência da etapa 3, 17/09/2026).
        # Os suspeitos vêm primeiro, sempre: são os que pedem decisão.
        self._montar_secao(
            f"Suspeitos — olhe estes {_ainda_mascarados(suspeitos)}", suspeitos, texto)
        self._montar_secao(f"CPF válido {_ainda_mascarados(validos)}", validos, texto)
        self._montar_secao(
            f"Mascarados à mão {_ainda_mascarados(a_mao)}", a_mao, texto)
        self._layout.addStretch()

    def marcar(self, ocorrencia):
        """Destaca o item do número que está sendo olhado, e rola a lista até ele.

        A comparação é por igualdade (`==`), e não por identidade (`is`): a
        chave é um número, e dois números iguais nem sempre são o mesmo objeto
        para o Python. Com `is`, nenhum item acendia nunca - defeito achado na
        conferência da etapa 3.
        """
        for chave, item in self._itens.items():
            marcado = chave == id(ocorrencia)
            item.marcar(marcado)
            if marcado:
                self._rolar_ate(item)

    def _rolar_ate(self, item):
        """Rola a lista até o item - só para cima e para baixo.

        Sem rolar, o item acende lá embaixo, fora da vista, e para quem olha é
        como se nada tivesse acontecido. Mas a rolagem é só na vertical: um
        item com etiqueta comprida fica um pouco mais largo que a coluna, e a
        rolagem para os lados cortava a primeira letra dos títulos da lista
        (conferência da etapa 3, com a imagem da tela).
        """
        # A lista pode ter acabado de ser remontada; sem esta conta, o item novo
        # ainda não tem lugar na tela, e a rolagem não saberia para onde ir.
        self._layout.activate()
        meio = item.height() // 2
        self.ensureVisible(0, item.y() + meio, 0, meio + estilo.ESPACO_2)
        self.horizontalScrollBar().setValue(0)

    # -------------------------------------------------------------- por dentro

    def _montar_secao(self, titulo, ocorrencias, texto):
        if not ocorrencias:
            return
        self._layout.addSpacing(estilo.ESPACO_2)
        self._layout.addWidget(_titulo_de_secao(titulo))
        for ocorrencia in ocorrencias:
            item = _Item(
                ocorrencia,
                texto,
                ao_clicar=self._ao_ir_para,
                ao_liberar=self._ao_liberar,
                ao_mascarar_de_novo=self._ao_mascarar_de_novo,
            )
            self._itens[id(ocorrencia)] = item
            self._layout.addWidget(item)

    def _limpar(self):
        while self._layout.count():
            peca = self._layout.takeAt(0)
            if peca.widget() is not None:
                peca.widget().deleteLater()


class _Item(QFrame):
    """Um número da lista: o que ele é, como estava escrito, e o que dá para fazer."""

    def __init__(self, ocorrencia, texto, ao_clicar, ao_liberar, ao_mascarar_de_novo):
        super().__init__()
        self._ocorrencia = ocorrencia
        self._ao_clicar = ao_clicar
        self.setObjectName("item")
        self.setCursor(Qt.PointingHandCursor)
        self.marcar(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(estilo.ESPACO_3, estilo.ESPACO_2,
                                  estilo.ESPACO_3, estilo.ESPACO_2)
        layout.setSpacing(estilo.ESPACO_1)

        pecas = [_etiqueta(texto_da_etiqueta, cor)
                 for texto_da_etiqueta, cor in _etiquetas(ocorrencia)]
        for peca in pecas:
            peca.ensurePolished()
        largura_das_etiquetas = (sum(p.sizeHint().width() for p in pecas)
                                 + estilo.ESPACO_1 * (len(pecas) - 1))
        # Duas etiquetas que não cabem lado a lado vão uma embaixo da outra.
        # Lado a lado à força, o item ficava mais largo que a coluna, a lista
        # deslizava para o lado e cortava a primeira letra dos títulos
        # ("uspeitos — olhe estes 9", conferência da etapa 3).
        if largura_das_etiquetas <= LARGURA_UTIL_DO_ITEM:
            linhas_de_etiquetas = [pecas]
        else:
            linhas_de_etiquetas = [[peca] for peca in pecas]
        for pecas_da_linha in linhas_de_etiquetas:
            etiquetas = QHBoxLayout()
            etiquetas.setSpacing(estilo.ESPACO_1)
            for peca in pecas_da_linha:
                etiquetas.addWidget(peca)
            etiquetas.addStretch()
            layout.addLayout(etiquetas)

        # O número como está escrito no texto, e não mascarado: é olhando o
        # original que se decide se aquilo é CPF (regra RN-10). A quebra de
        # linha vira uma seta, senão o item cresceria uma linha por número
        # partido.
        numero = QLabel(ocorrencia.original.replace("\n", " ↵ "))
        numero.setStyleSheet(
            f"font-family: {estilo.FONTE_MONO};"
            f"font-size: {estilo.TEXTO_BASE}px; color: {estilo.COR_TEXTO};"
            "border: none; background: transparent;"
        )
        layout.addWidget(numero)

        contexto = QLabel(_contexto(texto, ocorrencia))
        contexto.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
            "border: none; background: transparent;"
        )
        layout.addWidget(contexto)

        self.botao = QPushButton(_nome_do_botao(ocorrencia))
        self.botao.setCursor(Qt.PointingHandCursor)
        self.botao.setStyleSheet(estilo.estilo_botao(principal=False, pequeno=True))
        if ocorrencia.situacao == cpf.LIBERADO:
            self.botao.clicked.connect(lambda: ao_mascarar_de_novo(ocorrencia))
        else:
            self.botao.clicked.connect(lambda: ao_liberar(ocorrencia))

        linha = QHBoxLayout()
        linha.addWidget(self.botao)
        linha.addStretch()
        layout.addLayout(linha)

    def marcar(self, marcado):
        """O item do número que está sendo olhado ganha a borda e o fundo azuis.

        Só a borda era pouco: numa lista de doze itens parecidos, uma linha fina
        mudando de cor passa despercebida. O fundo levemente azul é o mesmo tom
        da faixa de aviso do programa.
        """
        self.marcado = marcado
        borda = estilo.COR_DESTAQUE if marcado else estilo.COR_BORDA
        fundo = "rgba(59, 110, 165, 46)" if marcado else estilo.COR_FUNDO_ELEVADO
        self.setStyleSheet(
            f"""
            QFrame#item {{
                background-color: {fundo};
                border: 1px solid {borda};
                border-left: 3px solid {_cor_da_barra(self._ocorrencia)};
                border-radius: {estilo.RAIO}px;
            }}
            """
        )

    def mousePressEvent(self, evento):
        self._ao_clicar(self._ocorrencia)
        super().mousePressEvent(evento)


def _ainda_mascarados(ocorrencias):
    return sum(1 for o in ocorrencias if o.situacao == cpf.MASCARADO)


def _etiquetas(ocorrencia):
    """O que o item diz que o número é, em uma ou duas etiquetas."""
    if ocorrencia.situacao == cpf.LIBERADO:
        # Liberado, o item continua no mesmo lugar da lista: arrependimento
        # custa um clique. O que muda é a etiqueta e o botão.
        # A etiqueta "liberado" é verde, como o selo do alto e o número no
        # texto: numa lista longa, é o que deixa achar de relance o que foi
        # solto (pedido na conferência da etapa 3, em 17/09/2026).
        return [(_nome_do_tipo(ocorrencia), estilo.COR_TEXTO_SECUNDARIO),
                ("liberado", estilo.COR_SUCESSO)]
    etiquetas = [(_nome_do_tipo(ocorrencia), _cor_do_tipo(ocorrencia))]
    # O "quase CPF" que passa na conta leva as duas: ele continua suspeito, e
    # também é um número que quase certamente é o CPF de alguém (RN-2).
    #
    # A etiqueta não diz "CPF válido", que é o nome da seção de cima: com o
    # mesmo nome nos dois lugares, ficava confuso saber se aquilo era o número
    # que a leitura pegou certinho ou o que só fecha a conta depois de
    # corrigido (conferência da etapa 3, 17/09/2026).
    if ocorrencia.tipo == cpf.QUASE_CPF and ocorrencia.passa_na_conta:
        etiquetas.append(("válido se corrigido", estilo.COR_ERRO_TEXTO))
    return etiquetas


def _nome_do_tipo(ocorrencia):
    if ocorrencia.tipo == cpf.PASSA_NA_CONTA:
        return "CPF válido"
    if ocorrencia.tipo == cpf.FALHA_NA_CONTA:
        return "falha na conta"
    if ocorrencia.tipo == cpf.MASCARADO_A_MAO:
        return "mascarado à mão"
    return f"quase CPF · {ocorrencia.motivo}"


def _cor_do_tipo(ocorrencia):
    if ocorrencia.tipo == cpf.PASSA_NA_CONTA:
        return estilo.COR_ERRO_TEXTO
    if ocorrencia.tipo == cpf.MASCARADO_A_MAO:
        # Azul, como o traço no texto, o selo e a chave de cores. De amarelo, o
        # item parecia pedir decisão - e ele já é a decisão da pessoa.
        return estilo.COR_DESTAQUE_HOVER
    return estilo.COR_ALERTA


def _cor_da_barra(ocorrencia):
    if ocorrencia.situacao == cpf.LIBERADO:
        return estilo.COR_BORDA
    return _cor_do_tipo(ocorrencia)


def _nome_do_botao(ocorrencia):
    if ocorrencia.situacao == cpf.LIBERADO:
        return "Mascarar de novo"
    # Os três pontos avisam que vem uma pergunta antes - é o mesmo sinal que o
    # resto do programa usa.
    return "Desfazer…" if ocorrencia.pede_dupla_conferencia else "Desfazer"


def _contexto(texto, ocorrencia):
    """As palavras que vêm antes do número, que são o que ajuda a decidir."""
    antes = texto[max(0, ocorrencia.inicio - LETRAS_DE_CONTEXTO):ocorrencia.inicio]
    antes = " ".join(antes.split())
    return f"…{antes}" if antes else "no começo do texto"


def _etiqueta(texto, cor):
    rotulo = QLabel(texto)
    rotulo.setStyleSheet(
        f"font-size: 11px; font-weight: 600; color: {cor};"
        f"border: 1px solid {cor}; border-radius: 8px; padding: 0 6px;"
        "background: transparent;"
    )
    return rotulo


def _titulo_da_lista(texto):
    rotulo = QLabel(texto)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 700;"
        f"color: {estilo.COR_TEXTO_SECUNDARIO}; letter-spacing: 1px;"
    )
    return rotulo


def _titulo_de_secao(texto):
    rotulo = QLabel(texto)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px; font-weight: 600;"
        f"color: {estilo.COR_TEXTO};"
    )
    return rotulo


def _nada_para_olhar():
    rotulo = QLabel(
        "Nada para olhar aqui. Cada número que o programa mascarar — ou que "
        "você mascarar à mão — aparece nesta lista."
    )
    rotulo.setWordWrap(True)
    rotulo.setFixedWidth(LARGURA - estilo.ESPACO_4)
    rotulo.setStyleSheet(
        f"font-size: {estilo.TEXTO_PEQUENO}px;"
        f"color: {estilo.COR_TEXTO_SECUNDARIO};"
    )
    # Medir só depois de o Qt aplicar o estilo, senão a conta sai com a fonte
    # errada e a última linha da frase é cortada.
    rotulo.ensurePolished()
    rotulo.setMinimumHeight(rotulo.heightForWidth(LARGURA - estilo.ESPACO_4))
    return rotulo

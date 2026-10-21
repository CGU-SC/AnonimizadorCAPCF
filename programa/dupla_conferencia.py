"""A pergunta antes de liberar um número que passa na conta do CPF (regra RN-10).

É o momento em que um CPF de verdade pode escapar do programa, e por isso é o
único vermelho da revisão. A caixa mostra o número **como está escrito no
texto** - que é o que iria para o arquivo - e explica por que ele quase
certamente é de alguém.

"Manter a máscara" já vem escolhido: apertar Enter ou Esc não libera nada. É o
mesmo arranjo da pergunta de escrever por cima, no "Gerar OCR" - o caminho que
não expõe nada é o mais fácil de seguir.

Segue os rascunhos aprovados mockups/anonimizar/01-revisar-antes-de-salvar.html
(estado 5) e 08-escolher-e-salvar.html.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

import cpf
import estilo

LARGURA = 520
LARGURA_DO_TEXTO = 460

# No "quase CPF", a explicação começa dizendo que o defeito do número é, quase
# sempre, da leitura do documento, e não do documento: quem vê "l11" tende a
# achar que aquilo não é número nenhum, quando no original provavelmente há um
# 1 ali (pedido na conferência da etapa 3, em 17/09/2026).
POR_QUE_PASSA = {
    cpf.LETRA_NO_LUGAR_DE_DIGITO: (
        "A letra no lugar do dígito costuma ser erro de leitura do documento "
        "(OCR): no original, ali provavelmente há um número. Com as letras "
        "trocadas de volta por dígitos, os dois últimos batem com a conta do "
        "dígito verificador, feita a partir dos nove primeiros."
    ),
    cpf.PARTIDO_EM_DUAS_LINHAS: (
        "Ele foi lido partido em duas linhas, o que costuma ser erro de leitura "
        "do documento (OCR). Juntando as partes, os dois últimos dígitos batem "
        "com a conta do dígito verificador."
    ),
    cpf.ESPACOS_NO_LUGAR_DOS_PONTOS: (
        "Os espaços no lugar da pontuação costumam ser erro de leitura do "
        "documento (OCR). Trocando os espaços pela pontuação de um CPF, os dois "
        "últimos dígitos batem com a conta do dígito verificador."
    ),
    cpf.PONTUACAO_FORA_DO_PADRAO: (
        "A pontuação fora do padrão costuma ser erro de leitura do documento "
        "(OCR). Acertando a pontuação, os dois últimos dígitos batem com a "
        "conta do dígito verificador."
    ),
    None: (
        "Os dois últimos dígitos batem com a conta do dígito verificador, feita "
        "a partir dos nove primeiros."
    ),
}


class DuplaConferencia(QDialog):
    def __init__(self, ocorrencia, pai=None):
        super().__init__(pai)
        self.setWindowTitle("Este número passa na conta do CPF")
        self.setModal(True)
        self.setStyleSheet(f"background-color: {estilo.COR_FUNDO};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_4,
                                  estilo.ESPACO_4, estilo.ESPACO_4)
        layout.setSpacing(estilo.ESPACO_4)

        caixa = QFrame()
        caixa.setObjectName("caixa")
        caixa.setFixedWidth(LARGURA)
        # Vermelha, e não amarela: aqui nada falhou, mas é o momento em que um
        # CPF de verdade pode sair do programa.
        caixa.setStyleSheet(
            f"""
            QFrame#caixa {{
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

        titulo = QLabel("Este número passa na conta do CPF")
        titulo.setStyleSheet(
            f"font-size: {estilo.TEXTO_BASE}px; font-weight: 600;"
            f"color: {estilo.COR_TEXTO}; border: none; background: transparent;"
        )
        dentro.addWidget(titulo)

        numero = QLabel(ocorrencia.original)
        numero.setStyleSheet(
            f"font-family: {estilo.FONTE_MONO}; font-size: {estilo.TEXTO_GRANDE}px;"
            f"color: {estilo.COR_TEXTO}; border: none; background: transparent;"
        )
        dentro.addWidget(numero)

        self.explicacao = QLabel(_explicacao(ocorrencia))
        self.explicacao.setWordWrap(True)
        self.explicacao.setFixedWidth(LARGURA_DO_TEXTO)
        self.explicacao.setStyleSheet(
            f"font-size: {estilo.TEXTO_PEQUENO}px;"
            f"color: {estilo.COR_TEXTO_SECUNDARIO};"
            "border: none; background: transparent;"
        )
        # A frase muda de tamanho conforme o motivo, então a altura de que ela
        # precisa é recalculada: sem isso o fim dela sai cortado.
        #
        # O `ensurePolished` antes da conta não é enfeite: sem ele o Qt mede a
        # frase com a fonte padrão, e não com a do estilo que acabou de ser
        # posto. A diferença é de uma linha - a última - e ela some para fora
        # da borda sem nenhum aviso.
        self.explicacao.ensurePolished()
        self.explicacao.setMinimumHeight(
            self.explicacao.heightForWidth(LARGURA_DO_TEXTO)
        )
        dentro.addWidget(self.explicacao)
        layout.addWidget(caixa)

        self.botao_liberar = QPushButton("Liberar mesmo assim")
        self.botao_liberar.setCursor(Qt.PointingHandCursor)
        self.botao_liberar.setStyleSheet(estilo.estilo_botao(principal=False))
        self.botao_liberar.clicked.connect(self.accept)

        self.botao_manter = QPushButton("Manter a máscara")
        self.botao_manter.setCursor(Qt.PointingHandCursor)
        self.botao_manter.setStyleSheet(estilo.estilo_botao(principal=True))
        self.botao_manter.clicked.connect(self.reject)
        # O botão que não expõe nada é o escolhido de saída: Enter cai nele, e
        # Esc fecha a caixa sem liberar (regra RN-10).
        self.botao_manter.setDefault(True)
        self.botao_manter.setAutoDefault(True)
        self.botao_liberar.setAutoDefault(False)

        acoes = QHBoxLayout()
        acoes.setSpacing(estilo.ESPACO_3)
        acoes.addStretch()
        acoes.addWidget(self.botao_liberar)
        acoes.addWidget(self.botao_manter)
        acoes.addStretch()
        layout.addLayout(acoes)


def liberar_mesmo_assim(ocorrencia, pai=None):
    """Mostra a caixa e diz se a pessoa liberou o número.

    Devolve False em tudo que não seja o clique em "Liberar mesmo assim" -
    inclusive fechar a caixa no X, que é o que a pessoa faz quando se arrepende.
    """
    caixa = DuplaConferencia(ocorrencia, pai)
    return caixa.exec() == QDialog.Accepted


# O CPF que perdeu o zero da frente (nona emenda, rascunho 09). A frase de cima
# fala dos "nove primeiros", e o número na caixa tem 10 ou 9 dígitos: sem
# explicar de onde veio o zero que falta, quem lê acha que o programa errou e
# libera. Cada um leva também o número de verdade com que ele mais se parece,
# que é o alarme falso mais provável: com 10 dígitos, o telefone com DDD; com
# 9, o celular escrito sem o DDD - telefone com DDD nunca tem 9 dígitos, e a
# primeira versão desta frase mandava procurar justamente ele (revisão da
# etapa 4).
POR_QUE_PASSA_SEM_ZERO = {
    1: (
        "Ele tem 10 dígitos, um a menos que um CPF: o zero da frente costuma se "
        "perder quando o número passa por uma planilha ou por um sistema que o "
        "guarda como número. Com o zero de volta, os dois últimos batem com a "
        "conta do dígito verificador.",
        "um telefone com DDD",
    ),
    2: (
        "Ele tem 9 dígitos, dois a menos que um CPF: os zeros da frente costumam "
        "se perder quando o número passa por uma planilha ou por um sistema que "
        "o guarda como número. Com os zeros de volta, os dois últimos batem com "
        "a conta do dígito verificador.",
        "um celular escrito sem o DDD",
    ),
}

_LIBERADO_VAI = (
    " Liberado, ele vai para o arquivo como está aqui em cima — e do arquivo "
    "para a conversa com o assistente de IA."
)


def _explicacao(ocorrencia):
    if ocorrencia.sem_zero:
        # A conclusão vem antes do aviso, e não depois: com o "por isso" logo
        # em seguida ao telefone, ele ficava amarrado ao aviso, e a pessoa lia
        # dois sinais opostos em seguida (revisão da etapa 4).
        por_que, parecido = POR_QUE_PASSA_SEM_ZERO[ocorrencia.sem_zero]
        return (
            por_que
            + " Por isso ele quase certamente é o CPF de alguém — mas "
            + parecido
            + " também pode fechar a conta por acaso, e as palavras ao redor "
            "ajudam a decidir."
            + _LIBERADO_VAI
        )
    motivo = ocorrencia.motivo if ocorrencia.tipo == cpf.QUASE_CPF else None
    return (
        POR_QUE_PASSA.get(motivo, POR_QUE_PASSA[None])
        + " Por isso ele quase certamente é o CPF de alguém."
        + _LIBERADO_VAI
    )

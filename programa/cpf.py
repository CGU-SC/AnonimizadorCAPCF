"""Acha, confere e mascara os CPFs de um texto.

Este arquivo não desenha nada na tela. Ficar separado da tela é o que permite
conferir por teste automático cada regra da spec 003 sobre o que é CPF, o que é
suspeito e como a máscara fica - regras que, erradas, deixariam um CPF passar
inteiro sem que ninguém percebesse olhando a janela.

Ele mora só no Anonimizar. O Gerar OCR não usa nada daqui, e não pode usar: o
módulo de OCR continua sem nenhuma linha de CPF (regra RN-18).
"""
import re
from dataclasses import dataclass

# Os tipos de ocorrência da spec 003 (seção Dados). Na tela, "passa na conta"
# aparece como "forma CPF válido" - o nome daqui é o da regra, não o da tela.
PASSA_NA_CONTA = "passa na conta"
FALHA_NA_CONTA = "suspeito: falha na conta"
QUASE_CPF = "suspeito: quase CPF"
MASCARADO_A_MAO = "mascarado à mão"

MASCARADO = "mascarado"
LIBERADO = "liberado"

# Por que o número foi parar entre os "quase CPF". Aparece ao lado dele na
# lista de suspeitos, para a pessoa entender o que a leitura estragou.
PARTIDO_EM_DUAS_LINHAS = "partido em duas linhas"
LETRA_NO_LUGAR_DE_DIGITO = "letra no lugar de dígito"
ESPACOS_NO_LUGAR_DOS_PONTOS = "espaços no lugar dos pontos"
PONTUACAO_FORA_DO_PADRAO = "pontuação fora do padrão"

# As letras que a leitura costuma confundir com dígito, da regra RN-2. A lista é
# fechada de propósito: aceitar qualquer letra faria palavras comuns virarem
# "CPF" e encheria a lista de suspeitos de alarme falso.
LETRA_PARECIDA_COM_DIGITO = {
    "O": "0", "o": "0", "D": "0", "Q": "0",
    "l": "1", "I": "1", "i": "1", "|": "1",
    "Z": "2",
    "S": "5", "s": "5",
    "G": "6", "b": "6",
    "T": "7",
    "B": "8",
    "g": "9", "q": "9",
}

# Com mais de 2 letras nas 11 posições, a sequência é mais provavelmente uma
# palavra que um número (premissa nova da spec 003).
MAXIMO_DE_LETRAS = 2

# Os quatro jeitos combinados de escrever um CPF (regra RN-1), pelos três
# separadores entre os grupos: 123.456.789-10, 123456789-10, 12345678910 e
# 123.456.789/10. Qualquer outra combinação é "quase CPF".
FORMATOS_COMBINADOS = {
    (".", ".", "-"),
    ("", "", "-"),
    ("", "", ""),
    (".", ".", "/"),
}

_POSICAO = "[0-9" + re.escape("".join(LETRA_PARECIDA_COM_DIGITO)) + "]"
_QUEBRA = r"[ \t]*\r?\n[ \t]*"
# O que pode ficar entre dois grupos: nada, um dos separadores combinados, um
# espaço, ou a quebra de linha - sozinha ou colada a um separador, como em
# "123.456." no fim de uma linha e "789-10" no começo da seguinte.
_SEPARADOR = rf"(?:{_QUEBRA}[.\-/]|[.\-/](?:{_QUEBRA})?|{_QUEBRA}| )?"

# As duas travas de cada ponta são a regra RN-3: número grudado num número
# maior não é CPF. É o que deixa inteiros o CNPJ (12.345.678/0001-90), o número
# de processo e a linha do boleto, em que um pedaço de 11 dígitos até cabe no
# desenho de um CPF, mas está colado a outros dígitos.
_PADRAO = re.compile(
    r"(?<![0-9])(?<![0-9][.\-/])"
    rf"({_POSICAO}{{3}})({_SEPARADOR})({_POSICAO}{{3}})({_SEPARADOR})"
    rf"({_POSICAO}{{3}})({_SEPARADOR})({_POSICAO}{{2}})"
    r"(?![0-9])(?![.\-/][0-9])"
)

_GRUPOS_DE_DIGITOS = (1, 3, 5, 7)
_GRUPOS_DE_SEPARADOR = (2, 4, 6)


@dataclass
class Ocorrencia:
    """Um número achado no texto, ou um trecho mascarado à mão.

    Começo e fim são as posições no texto de entrada. A máscara tem sempre o
    mesmo tamanho do original (premissa da spec 003), então essas posições
    valem igual no texto mascarado - e a tabela de texto continua alinhada.
    """

    inicio: int
    fim: int
    original: str
    mascara: str
    tipo: str
    passa_na_conta: bool
    motivo: str | None = None
    situacao: str = MASCARADO

    @property
    def suspeito(self):
        return self.tipo in (FALHA_NA_CONTA, QUASE_CPF)

    @property
    def pede_dupla_conferencia(self):
        """Todo número que passa na conta, inteiro ou "quase CPF" (RN-10).

        É o que quase certamente é o CPF de alguém - o mais perigoso de sair
        do programa com um clique.
        """
        return self.passa_na_conta and self.tipo != MASCARADO_A_MAO


def passa_na_conta(digitos):
    """A conta do dígito verificador do CPF, feita aqui mesmo (regra RN-4).

    Os dois últimos dígitos são calculados a partir dos nove primeiros e
    comparados com os que estão escritos. Sem biblioteca de fora: a conta tem
    seis linhas, e uma dependência a mais seria mais uma coisa para instalar
    nas máquinas do núcleo.
    """
    if len(digitos) != 11 or not digitos.isdigit():
        return False
    numeros = [int(d) for d in digitos]
    for tamanho in (9, 10):
        soma = sum(n * peso for n, peso in zip(numeros, range(tamanho + 1, 1, -1)))
        esperado = soma * 10 % 11 % 10
        if numeros[tamanho] != esperado:
            return False
    return True


def procurar(texto):
    """Todos os CPFs e "quase CPFs" do texto, na ordem em que aparecem.

    Todos saem com a situação "mascarado", suspeitos inclusive (regra RN-5): um
    CPF de verdade lido com um dígito trocado falha na conta, e sem máscara
    sairia quase inteiro.
    """
    achados = []
    posicao = 0
    while True:
        encontro = _PADRAO.search(texto, posicao)
        if encontro is None:
            return achados
        ocorrencia = _avaliar(encontro)
        if ocorrencia is None:
            # Recusado, procura de novo uma letra adiante, e não do fim do
            # recusado: um CPF de verdade pode começar dentro dele.
            posicao = encontro.start() + 1
        else:
            achados.append(ocorrencia)
            posicao = encontro.end()


def mascarar_a_mao(texto, inicio, fim):
    """A máscara do trecho que a pessoa marcou com o mouse (regra RN-9).

    Esconde os 3 primeiros e os 2 últimos dígitos do trecho, ou todos, se forem
    5 ou menos. Devolve None quando o trecho não tem dígito nenhum - aí nada
    muda, e a tela diz por quê.

    O que fica marcado como ocorrência vai do primeiro ao último dígito: um
    espaço pego sem querer na ponta da seleção não precisa ficar destacado.
    """
    trecho = texto[inicio:fim]
    digitos = [i for i, letra in enumerate(trecho) if letra.isdigit()]
    if not digitos:
        return None
    primeiro, ultimo = digitos[0], digitos[-1]
    original = trecho[primeiro:ultimo + 1]
    posicoes = [i - primeiro for i in digitos]
    esconder = posicoes if len(posicoes) <= 5 else posicoes[:3] + posicoes[-2:]
    mascara = "".join(
        "*" if i in esconder else letra for i, letra in enumerate(original)
    )
    return Ocorrencia(
        inicio=inicio + primeiro,
        fim=inicio + ultimo + 1,
        original=original,
        mascara=mascara,
        tipo=MASCARADO_A_MAO,
        passa_na_conta=False,
    )


def aplicar(texto, ocorrencias):
    """O texto de saída: o de entrada, com a máscara de toda ocorrência mascarada.

    É só isto que vai para o arquivo. A troca é feita no texto, letra por letra
    - nunca uma tarja por cima, que deixaria o número original por baixo para
    quem copiasse o texto.

    Cada máscara escreve só o que ela troca (o asterisco, e o traço no lugar
    da barra), e nunca devolve uma letra do original. Duas máscaras podem se
    sobrepor - a pessoa marca à mão um trecho que engloba um CPF já mascarado -
    e, se a segunda escrevesse o trecho inteiro, os dígitos do meio dela
    apagariam os asteriscos da primeira: o CPF voltaria a aparecer no arquivo
    com a lista dizendo que ele está mascarado.
    """
    letras = list(texto)
    for ocorrencia in ocorrencias:
        if ocorrencia.situacao != MASCARADO:
            continue
        for deslocamento, (antes, depois) in enumerate(
                zip(ocorrencia.original, ocorrencia.mascara)):
            if antes != depois:
                letras[ocorrencia.inicio + deslocamento] = depois
    return "".join(letras)


def _avaliar(encontro):
    """Decide o que é o número achado, ou devolve None se ele não conta.

    Letra na ponta do número conta mesmo quando está grudada numa palavra. Já
    houve aqui uma regra que descartava esse caso, para o S de
    "111.111.111-1Sobre" não virar um 5 - e ela deixava sair inteiro, sem
    máscara e fora da lista, o CPF que a leitura grudou no "CPF" e cujo
    primeiro 1 virou "l" ("CPFl11.111.111-11"). Entre um alarme falso, que a
    pessoa desfaz com um clique, e um CPF que escapa calado, fica o alarme
    (regra RN-5: o erro fica do lado seguro).
    """
    posicoes = "".join(encontro.group(g) for g in _GRUPOS_DE_DIGITOS)
    letras = sum(1 for letra in posicoes if not letra.isdigit())
    if letras > MAXIMO_DE_LETRAS:
        return None

    separadores = tuple(encontro.group(g) for g in _GRUPOS_DE_SEPARADOR)
    digitos = "".join(LETRA_PARECIDA_COM_DIGITO.get(l, l) for l in posicoes)
    conta = passa_na_conta(digitos)

    if not letras and separadores in FORMATOS_COMBINADOS:
        tipo, motivo = (PASSA_NA_CONTA if conta else FALHA_NA_CONTA), None
    else:
        tipo, motivo = QUASE_CPF, _por_que_e_quase(separadores, letras)

    return Ocorrencia(
        inicio=encontro.start(),
        fim=encontro.end(),
        original=encontro.group(0),
        mascara=_mascarar(encontro),
        tipo=tipo,
        passa_na_conta=conta,
        motivo=motivo,
    )


def _por_que_e_quase(separadores, letras):
    if any("\n" in s for s in separadores):
        return PARTIDO_EM_DUAS_LINHAS
    if letras:
        return LETRA_NO_LUGAR_DE_DIGITO
    if all(s == " " for s in separadores):
        return ESPACOS_NO_LUGAR_DOS_PONTOS
    return PONTUACAO_FORA_DO_PADRAO


def _mascarar(encontro):
    """A máscara da regra RN-6: asterisco nas 3 primeiras e nas 2 últimas posições.

    Os separadores ficam como estavam, com uma exceção: a barra antes dos dois
    últimos vira traço (123.456.789/10 vira ***.456.789-**). Nenhuma outra
    letra muda, e o tamanho do número também não.
    """
    comeco = encontro.start()
    letras = list(encontro.group(0))
    posicoes = [
        i - comeco
        for g in _GRUPOS_DE_DIGITOS
        for i in range(*encontro.span(g))
    ]
    for i in posicoes[:3] + posicoes[-2:]:
        letras[i] = "*"
    inicio_do_ultimo_separador = encontro.start(6) - comeco
    for i in range(inicio_do_ultimo_separador, encontro.end(6) - comeco):
        if letras[i] == "/":
            letras[i] = "-"
    return "".join(letras)

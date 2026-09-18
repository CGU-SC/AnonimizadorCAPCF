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

# Quantas letras no lugar de dígito uma sequência aceita antes de deixar de
# contar como "quase CPF". O limite depende da pontuação (quarta emenda da spec
# 003, de 16/09/2026): ponto, traço ou barra nos lugares exatos de um CPF quase
# nunca aparecem numa palavra ou num código, e ali cabem 4 letras - ainda sobram
# 7 dígitos certos. Sem separador nenhum, ou só com espaços, a sequência tem
# cara de código ou de lista de números, e o limite continua em 2.
MAXIMO_DE_LETRAS_COM_PONTUACAO = 4
MAXIMO_DE_LETRAS_SEM_PONTUACAO = 2

# Os separadores que contam como pontuação de CPF. O espaço fica de fora de
# propósito: documento de prestação de contas é cheio de número separado por
# espaço, e ali a chance de não ser CPF é bem maior.
PONTUACAO_DE_CPF = ".-/"

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
        ocorrencia = _avaliar(texto, encontro)
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
    if not any(letra.isdigit() for letra in trecho):
        return None

    digitos = _posicoes_do_trecho(trecho)
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


def _avaliar(texto, encontro):
    """Decide o que é o número achado, ou devolve None se ele não conta.

    As duas pontas do número são tratadas de jeitos diferentes, e de propósito.

    Na ponta do começo, letra grudada numa palavra continua contando. Já houve
    aqui uma regra que descartava esse caso, e ela deixava sair inteiro, sem
    máscara e fora da lista, o CPF que a leitura grudou no "CPF" e cujo primeiro
    1 virou "l" ("CPFl11.111.111-11"). Entre um alarme falso e um CPF que escapa
    calado, fica o alarme (regra RN-5).

    Na ponta final, letra grudada numa palavra é começo de palavra, e o número
    não conta (quinta emenda da spec 003) - **mas só quando não há pontuação de
    CPF**. Um número de 9 dígitos no fim da linha, com "Situação" na linha de
    baixo, fechava as 11 posições com o "Si", e num documento de verdade isso deu
    18 alarmes falsos; todos eram sem pontuação. Com ponto, traço ou barra nas
    posições exatas, a regra não vale: "CPF 111.111.111-1SAssinado" é um CPF que
    a leitura estragou e colou na palavra seguinte, e soltá-lo seria deixá-lo
    sair inteiro, calado (revisão da etapa 3).
    """
    posicoes = "".join(encontro.group(g) for g in _GRUPOS_DE_DIGITOS)
    letras = sum(1 for letra in posicoes if not letra.isdigit())
    separadores = tuple(encontro.group(g) for g in _GRUPOS_DE_SEPARADOR)
    if letras > _maximo_de_letras(separadores):
        return None
    depois = texto[encontro.end()] if encontro.end() < len(texto) else ""
    if (not _tem_pontuacao(separadores)
            and not encontro.group(0)[-1].isdigit() and depois.isalpha()):
        return None

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


def _posicoes_do_trecho(trecho):
    """Onde os asteriscos podem cair no trecho marcado à mão (regra RN-9).

    A conta é feita pedaço por pedaço, e não pelo trecho inteiro. **Pedaço com
    dígito** - `l23.4S6.789-1O` - conta dígito e letra parecida com dígito, como
    a sexta emenda decidiu: senão o "l" e o "O", que são o primeiro e o último
    dígito do número, ficariam à vista. **Pedaço sem nenhum dígito** - `|`,
    `isso`, `Sobre` - não conta nada.

    Olhando o trecho inteiro, dois casos gastavam os asteriscos fora do número e
    deixavam dígitos à mostra (revisão da etapa 4): a barra de tabela em volta da
    célula (`| l23.4S6.789-1O |`) e a palavra feita só de letras parecidas
    ("isso" é i, s, s, o). A barra vertical fica de fora da conta aqui: em
    documento, ela separa coluna muito mais vezes do que vale por "1".
    """
    parecidas = set(LETRA_PARECIDA_COM_DIGITO) - {"|"}
    posicoes = []
    for pedaco in _pedacos(trecho):
        letras = trecho[pedaco.start:pedaco.stop]
        if any(letra.isdigit() for letra in letras):
            posicoes.extend(
                pedaco.start + i for i, letra in enumerate(letras)
                if letra.isdigit() or letra in parecidas
            )
    return posicoes


def _pedacos(trecho):
    """Os pedaços do trecho, separados por espaço ou quebra de linha."""
    pedaco = None
    for i, letra in enumerate(trecho + " "):
        if letra.isspace():
            if pedaco is not None:
                yield range(pedaco, i)
                pedaco = None
        elif pedaco is None:
            pedaco = i


def _tem_pontuacao(separadores):
    """Diz se os grupos estão separados por ponto, traço ou barra.

    É a evidência mais forte de que aquilo é um CPF: a pontuação nas posições
    exatas quase nunca aparece dentro de uma palavra ou de um código.
    """
    return any(
        letra in PONTUACAO_DE_CPF for separador in separadores for letra in separador
    )


def _maximo_de_letras(separadores):
    """Quantas letras esta sequência aceita, pela pontuação que ela tem."""
    return (MAXIMO_DE_LETRAS_COM_PONTUACAO if _tem_pontuacao(separadores)
            else MAXIMO_DE_LETRAS_SEM_PONTUACAO)


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

"""As cores, fontes e medidas do programa, num lugar só.

Os valores vêm do sistema de design do projeto (mockups/sistema-de-design.md).
Estão aqui, e não espalhados pelas telas, para que trocar uma cor seja mexer em
uma linha - e para que duas telas não acabem com dois azuis ligeiramente
diferentes. Desde a funcionalidade 10, este é também o único lugar do programa
com cor escrita dentro (RN-26 da spec 001): um teste procura cor em qualquer
outro arquivo e falha se achar.

Há dois temas, escuro e claro, e o programa usa um só do começo ao fim
(RN-17): `usar_tema` é chamado antes de a janela ser montada, e as telas leem
`estilo.COR_...` na hora em que cada peça nasce. Por isso a troca vale ao
reabrir, e por isso nenhuma tela pode guardar uma cor daqui numa variável
criada ao carregar o arquivo - ela ficaria com a cor do tema de antes.
"""

ESCURO = "escuro"
CLARO = "claro"

# Cores nomeadas pelo papel que cumprem, e nunca pelo nome da cor: o mesmo papel
# tem um valor em cada tema. O escuro é o de sempre, valor por valor - quem
# usava o programa antes da funcionalidade 10 não vê nada mudar (RN-16).
TEMAS = {
    ESCURO: {
        "COR_FUNDO": "#1e2228",
        "COR_FUNDO_ELEVADO": "#262b33",
        "COR_BORDA": "#383e47",
        "COR_TEXTO": "#e8eaed",
        "COR_TEXTO_SECUNDARIO": "#9aa1ac",
        "COR_TEXTO_APAGADO": "#6c737d",
        "COR_DESTAQUE": "#3b6ea5",
        "COR_DESTAQUE_HOVER": "#4f86bf",
        # O azul de destaque com 24% de força: o fundo do item marcado na faixa e
        # do quadrado do ícone no título das telas, que é o mesmo azul de
        # propósito - o desenho e a cor ligam o título ao item do menu (RN-13 e
        # RN-14 da spec 001). Deixa o texto claro em cerca de 9,5 para 1. A cor
        # sai desta força, em `usar_tema`.
        "FORCA_DO_DESTAQUE_FRACO": 0.24,
        "COR_PASSAR_O_MOUSE": "rgba(255, 255, 255, 0.06)",
        "COR_SUCESSO": "#4caf6d",
        "COR_ALERTA": "#d9a441",
        # No escuro o amarelo de alerta serve de letra; no claro não, e por isso
        # a letra de aviso é um papel à parte, mesmo tendo aqui o mesmo valor.
        "COR_ALERTA_TEXTO": "#d9a441",
        # O suspeito e a barra dele na lista: no escuro, o amarelo de sempre; no
        # claro cada um tem o seu tom (RN-29 da spec 001).
        "COR_SUSPEITO": "#d9a441",
        "COR_SUSPEITO_BARRA": "#d9a441",
        "COR_ERRO": "#d9534f",
        # O vermelho de letra: o #d9534f sobre o fundo escuro tem contraste de
        # 4:1, abaixo do mínimo de leitura para letra pequena. Este tem 6,6:1. É
        # ele que marca o "CPF válido" na revisão.
        "COR_ERRO_TEXTO": "#f08a86",
        # O que veio da IA na revisão (spec 004). Lilás porque amarelo, vermelho,
        # azul e verde já têm dono. 6,7:1 sobre o fundo e 5,9:1 sobre o elevado.
        "COR_IA": "#b39ddb",
        "COR_ATRAS_DO_PDF": "#0f1216",
        # Os tons que as telas já usavam sem nome, aprovados em 06/11/2026 no
        # rascunho mockups/janela/07-os-tons-que-faltavam.html. A força vai de 0
        # a 255, como sempre foi escrita.
        "COR_ERRO_FUNDO": "rgba(217, 83, 79, 26)",
        "COR_ALERTA_FUNDO": "rgba(217, 164, 65, 26)",
        "COR_ALERTA_FUNDO_FORTE": "rgba(217, 164, 65, 31)",
        "COR_ALERTA_SELO": "rgba(217, 164, 65, 38)",
        "COR_DESTAQUE_AVISO": "rgba(59, 110, 165, 26)",
        "COR_DESTAQUE_NA_LISTA": "rgba(59, 110, 165, 46)",
        "COR_DESTAQUE_SELO": "rgba(59, 110, 165, 51)",
        "COR_DESTAQUE_SELO_TEXTO": "#7fb1e8",
        "COR_IA_FUNDO": "rgba(179, 157, 219, 23)",
        "COR_AREA_DE_SOLTAR": "rgba(255, 255, 255, 4)",
        "COR_TEXTO_DESLIGADO": "#5d646e",
        "COR_TEXTO_DESLIGADO_PEQUENO": "#565d66",
        "COR_BORDA_DESLIGADA": "#4a5058",
        "COR_BOLINHA_LIGADA": "#ffffff",
        # A força do fundo lilás atrás do número que a IA apontou, no texto da
        # revisão. É número, e não cor, porque o texto da revisão pinta o fundo
        # a partir da própria cor da IA.
        "FORCA_DA_MARCA_DA_IA": 36,
    },
    CLARO: {
        # As cores do projeto Gerencial, papel por papel; o que ele não tinha
        # está marcado "escolhido aqui" no sistema de design.
        "COR_FUNDO": "#f2f4f7",
        "COR_FUNDO_ELEVADO": "#fbfcfd",
        "COR_BORDA": "#c9d0d8",
        "COR_TEXTO": "#16202b",
        "COR_TEXTO_SECUNDARIO": "#4a5868",
        "COR_TEXTO_APAGADO": "#8a96a3",
        "COR_DESTAQUE": "#1f4e8c",
        "COR_DESTAQUE_HOVER": "#2a6fc9",
        # 10%, e não 24%: o azul-marinho do claro é mais forte que o do escuro.
        "FORCA_DO_DESTAQUE_FRACO": 0.10,
        "COR_PASSAR_O_MOUSE": "rgba(22, 32, 43, 0.06)",
        "COR_SUCESSO": "#1f7a3a",
        # O amarelo do claro tem 2,3:1 e só pinta fundo e borda (RN-18).
        "COR_ALERTA": "#c2aa07",
        # A letra de aviso: 4,6:1 sobre a janela e 5,0:1 sobre os quadros. Dentro
        # das caixas e dos selos amarelos fica entre 4,1 e 4,5, exceção escolhida
        # pela solicitante (RN-30). O #7a5c00 de antes se confundia com o preto.
        "COR_ALERTA_TEXTO": "#a85a00",
        # O suspeito fica abaixo do mínimo de letra de propósito, 3,0:1 sobre a
        # janela: o que faz ele ser achado é a diferença para o preto do texto
        # (5,0:1), e o traço ondulado o separa para quem distingue mal as cores
        # (RN-30). A barra do item é um âmbar mais vivo, porque não é letra.
        "COR_SUSPEITO": "#c28102",
        "COR_SUSPEITO_BARRA": "#ec9c01",
        "COR_ERRO": "#ae0202",
        # No claro o vermelho de fundo já tem contraste de letra: 6,8:1.
        "COR_ERRO_TEXTO": "#ae0202",
        "COR_IA": "#7356c8",
        "COR_ATRAS_DO_PDF": "#c9d0d8",
        "COR_ERRO_FUNDO": "rgba(179, 38, 30, 18)",
        "COR_ALERTA_FUNDO": "rgba(194, 170, 7, 31)",
        "COR_ALERTA_FUNDO_FORTE": "rgba(194, 170, 7, 38)",
        "COR_ALERTA_SELO": "rgba(194, 170, 7, 46)",
        # Mais fraco que no escuro: a 10%, o azul-marinho pesava mais que um aviso.
        "COR_DESTAQUE_AVISO": "rgba(31, 78, 140, 15)",
        # Já misturado, e bem mais fraco que no escuro: com mais azul atrás, a
        # etiqueta pequena "mascarado por você" cai abaixo de 4,5:1. No claro,
        # quem diz "é este" é a borda azul do item.
        "COR_DESTAQUE_NA_LISTA": "#f2f5f8",
        "COR_DESTAQUE_SELO": "rgba(31, 78, 140, 26)",
        "COR_DESTAQUE_SELO_TEXTO": "#1f4e8c",
        "COR_IA_FUNDO": "rgba(115, 86, 200, 26)",
        "COR_AREA_DE_SOLTAR": "rgba(22, 32, 43, 5)",
        # Apagados de propósito, como no escuro (exceção da RN-18).
        "COR_TEXTO_DESLIGADO": "#8a96a3",
        "COR_TEXTO_DESLIGADO_PEQUENO": "#8a96a3",
        "COR_BORDA_DESLIGADA": "#dde2e7",
        # O branco dos quadros, e não o branco puro: assim a bolinha tem um
        # valor em cada tema, e a RN-26 continua com só as duas exceções.
        "COR_BOLINHA_LIGADA": "#fbfcfd",
        # 6%, e não 14%: a letra lilás é a própria marca, e com mais fundo ela
        # ficaria em 4,1:1.
        "FORCA_DA_MARCA_DA_IA": 15,
    },
}

# As duas únicas cores iguais nos dois temas (RN-26): a letra dentro do botão de
# destaque e o desenho do símbolo do cabeçalho, brancos sobre o azul.
COR_LETRA_NO_DESTAQUE = "#ffffff"
COR_DESENHO_DO_SIMBOLO = "#ffffff"

TEMA = ESCURO


def usar_tema(nome):
    """Passa a valer o tema dado; um nome que não é tema vale como escuro.

    Precisa ser chamado antes de montar a janela: as cores são lidas quando cada
    tela nasce, e a que já nasceu fica com as do tema de antes.
    """
    global TEMA, COR_DESTAQUE_FRACO
    TEMA = nome if nome in TEMAS else ESCURO
    valores = TEMAS[TEMA]
    globals().update(valores)
    # Duas formas do mesmo azul fraco - a cor para a folha de estilo, e a força
    # para quem pinta à mão (o quadrado do título) - tiradas de um valor só,
    # para as duas nunca divergirem.
    azul = valores["COR_DESTAQUE"]
    COR_DESTAQUE_FRACO = (f"rgba({int(azul[1:3], 16)}, {int(azul[3:5], 16)}, "
                          f"{int(azul[5:7], 16)}, {valores['FORCA_DO_DESTAQUE_FRACO']})")


usar_tema(ESCURO)

FONTE_MONO = '"Cascadia Mono", "Consolas", monospace'

TEXTO_PEQUENO = 13
TEXTO_BASE = 15
TEXTO_GRANDE = 20

ESPACO_1 = 4
ESPACO_2 = 8
ESPACO_3 = 16
ESPACO_4 = 24
ESPACO_5 = 32

RAIO = 6

LARGURA_MENU = 220
# A altura do cabeçalho da faixa (o nome em duas linhas e 20 px de respiro
# embaixo) e a do título das telas dos módulos. As duas começam a 24 px do alto
# da janela; com a mesma altura, a linha embaixo de uma continua a da outra
# (RN-14 da spec 001).
ALTURA_DO_CABECALHO = 60


def estilo_botao(principal=True, pequeno=False):
    """O visual dos botões, do jeito que o rascunho aprovado mostra.

    O pequeno é o de dentro de uma faixa de aviso: com o tamanho normal, três
    botões lado a lado ali ocupariam mais espaço que o próprio aviso.
    """
    espaco, letra = ("6px 12px", TEXTO_PEQUENO) if pequeno else ("10px 18px", TEXTO_BASE)
    if principal:
        fundo, cor, borda, peso = COR_DESTAQUE, COR_LETRA_NO_DESTAQUE, "none", 600
        fundo_hover = COR_DESTAQUE_HOVER
    else:
        fundo, cor, borda, peso = "transparent", COR_TEXTO_SECUNDARIO, f"1px solid {COR_BORDA}", 400
        fundo_hover = COR_PASSAR_O_MOUSE

    return f"""
        QPushButton {{
            background-color: {fundo};
            color: {cor};
            border: {borda};
            border-radius: {RAIO}px;
            padding: {espaco};
            font-size: {letra}px;
            font-weight: {peso};
        }}
        QPushButton:hover {{
            background-color: {fundo_hover};
        }}
        QPushButton:disabled {{
            background-color: {COR_FUNDO_ELEVADO};
            color: {COR_TEXTO_DESLIGADO};
            border: 1px solid {COR_BORDA};
            font-weight: 400;
        }}
    """

"""As cores, fontes e medidas do programa, num lugar só.

Os valores vêm do sistema de design do projeto (mockups/sistema-de-design.md),
tema escuro. Estão aqui, e não espalhados pelas telas, para que trocar uma cor
seja mexer em uma linha - e para que duas telas não acabem com dois azuis
ligeiramente diferentes.
"""

# Cores, nomeadas pelo papel que cumprem e nunca pelo nome da cor. É o que vai
# permitir acrescentar o tema claro depois sem redesenhar nada.
COR_FUNDO = "#1e2228"
COR_FUNDO_ELEVADO = "#262b33"
COR_BORDA = "#383e47"
COR_TEXTO = "#e8eaed"
COR_TEXTO_SECUNDARIO = "#9aa1ac"
COR_TEXTO_APAGADO = "#6c737d"
COR_DESTAQUE = "#3b6ea5"
COR_DESTAQUE_HOVER = "#4f86bf"
# O azul de destaque com 24% de força: o fundo do item marcado na faixa e do
# quadrado do ícone no título das telas, que é o mesmo azul de propósito - o
# desenho e a cor ligam o título ao item do menu (RN-13 e RN-14 da spec 001).
# Sobre o fundo da faixa, deixa o texto claro em cerca de 9,5 para 1.
FORCA_DO_DESTAQUE_FRACO = 0.24
COR_DESTAQUE_FRACO = (f"rgba({int(COR_DESTAQUE[1:3], 16)}, {int(COR_DESTAQUE[3:5], 16)}, "
                      f"{int(COR_DESTAQUE[5:7], 16)}, {FORCA_DO_DESTAQUE_FRACO})")
COR_SUCESSO = "#4caf6d"
COR_ALERTA = "#d9a441"
COR_ERRO = "#d9534f"
# O vermelho de letra: o #d9534f sobre o fundo escuro tem contraste de 4:1,
# abaixo do mínimo de leitura para letra pequena. Este tem 6,6:1. É ele que
# marca o "forma CPF válido" na revisão.
COR_ERRO_TEXTO = "#f08a86"
# O que veio da IA na revisão (spec 004). Lilás porque amarelo, vermelho, azul e verde
# já têm dono. Contraste de 6,7:1 sobre o fundo e 5,9:1 sobre o fundo elevado.
COR_IA = "#b39ddb"

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
        fundo, cor, borda, peso = COR_DESTAQUE, "#ffffff", "none", 600
        fundo_hover = COR_DESTAQUE_HOVER
    else:
        fundo, cor, borda, peso = "transparent", COR_TEXTO_SECUNDARIO, f"1px solid {COR_BORDA}", 400
        fundo_hover = "rgba(255, 255, 255, 0.06)"

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
            color: #5d646e;
            border: 1px solid {COR_BORDA};
            font-weight: 400;
        }}
    """

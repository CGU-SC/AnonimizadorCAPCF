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
COR_SUCESSO = "#4caf6d"
COR_ALERTA = "#d9a441"
COR_ERRO = "#d9534f"

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


def estilo_botao(principal=True):
    """O visual dos botões, do jeito que o rascunho aprovado mostra."""
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
            padding: 10px 18px;
            font-size: {TEXTO_BASE}px;
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

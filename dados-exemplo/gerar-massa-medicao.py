r"""Gera as páginas difíceis da medição dos motores de leitura (funcionalidade 7).

O PaddleOCR foi pedido para as páginas em que o Tesseract lê pior: torta, de
contraste fraco, cheia de tabela. A massa que já existia não tem nenhuma delas -
os PDFs "escaneados" de lá são desenho limpo, com um CPF só. Medir só neles
daria empate, e o empate não diria nada sobre o problema.

Cada página aqui é uma imagem, como sai de um escâner, e vem com o GABARITO: o
texto exato que foi desenhado nela e os CPFs que ela tem. É contra o gabarito
que a conferência 02 conta o que cada motor leu certo.

Nenhum dado é de pessoa real. Os números que passam na conta do dígito
verificador são só de dígitos repetidos, que a Receita não emite; os outros
falham na conta (a regra está no README desta pasta, e o test_cpf.py a confere).
Os nomes são inventados.

Rode assim, da raiz do projeto:

    .\.venv\Scripts\python.exe dados-exemplo\gerar-massa-medicao.py
"""
import io
import json
import math
import random
from pathlib import Path

import pymupdf
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

PASTA = Path(__file__).parent
NOME = "20-paginas-dificeis"

# A fonte do Windows, e não a embutida do PDF: a embutida não desenha bem a
# acentuação, e documento real chega com acento. A massa só se gera numa
# máquina com Windows, como o resto do projeto.
FONTE = r"C:\Windows\Fonts\arial.ttf"
FONTE_NEGRITO = r"C:\Windows\Fonts\arialbd.ttf"

# 300 pontos por polegada é como o escâner da CAPCF costuma gravar, e é a
# densidade em que o programa desenha a página para ler (RN-7 da spec 002).
DENSIDADE = 300
A4_EM_PE = (2480, 3508)

CABECALHO = [
    "UNIVERSIDADE FEDERAL DE SANTA CATARINA",
    "Coordenadoria de Análise de Prestações de Contas Fundacionais",
]

OFICIO = [
    "Ofício nº 0137/2026 - Prestação de contas do projeto de extensão",
    "",
    "Trata-se de prestação de contas referente ao projeto identificado no",
    "processo 23080.012345/2026-11, encaminhada pela fundação de apoio para",
    "análise desta Coordenadoria. O coordenador indicado no termo de outorga",
    "é o servidor Fulano de Tal Exemplo, inscrito no CPF 123.456.789-10.",
    "A bolsista Maria da Conceição Exemplo, CPF 222.222.222-22, recebeu as",
    "parcelas de março a junho. O pagamento ao colaborador João Ninguém",
    "Silva (CPF 33333333333) foi feito por depósito em conta corrente, e a",
    "diária do motorista Cícero Inventado, CPF 777.777.777-78, segue em",
    "anexo. Solicita-se a conferência dos comprovantes até 30/11/2026.",
]

COLUNAS = ["Nome", "CPF", "Função", "Valor (R$)"]
BOLSISTAS = [
    ["Ana Beatriz Moreira", "111.111.111-11", "Bolsista", "1.200,00"],
    ["Bruno César Lima", "222.222.222-22", "Bolsista", "1.200,00"],
    ["Cláudia Exemplo Souza", "444.444.444-44", "Pesquisadora", "3.450,00"],
    ["Daniel Fictício Rocha", "55555555555", "Bolsista", "800,00"],
    ["Elaine Inventada Dias", "666.666.666/66", "Técnica", "2.100,00"],
    ["Fábio Teste Nogueira", "777.777.777-77", "Bolsista", "1.200,00"],
    ["Gisele Modelo Araújo", "888888888-88", "Coordenadora", "4.000,00"],
    ["Hélio Amostra Costa", "999.999.999-99", "Bolsista", "1.200,00"],
    ["Iara Simulada Prado", "123.456.789-10", "Bolsista", "1.200,00"],
    ["Jorge Exemplar Reis", "246.813.579-12", "Motorista", "950,00"],
    ["Karina Suposta Luz", "333.333.333/34", "Bolsista", "1.200,00"],
    ["Lucas Hipótese Melo", "000.000.000-00", "Bolsista", "1.200,00"],
]


def _fonte(tamanho_em_pontos, negrito=False):
    pixels = round(tamanho_em_pontos * DENSIDADE / 72)
    return ImageFont.truetype(FONTE_NEGRITO if negrito else FONTE, pixels)


def _folha(tamanho=A4_EM_PE):
    imagem = Image.new("L", tamanho, 255)
    return imagem, ImageDraw.Draw(imagem)


def _desenhar_cabecalho(desenho, x, y):
    linhas = []
    for indice, texto in enumerate(CABECALHO):
        desenho.text((x, y), texto, font=_fonte(12, negrito=indice == 0), fill=0)
        linhas.append(texto)
        y += 70
    return y + 60, linhas


def desenhar_oficio(tamanho=A4_EM_PE, corpo=11):
    """O ofício com CPFs no meio do texto corrido. Devolve imagem e gabarito."""
    imagem, desenho = _folha(tamanho)
    x = 240
    y, linhas = _desenhar_cabecalho(desenho, x, 240)
    fonte = _fonte(corpo)
    entrelinha = round(corpo * DENSIDADE / 72 * 1.5)
    for texto in OFICIO:
        desenho.text((x, y), texto, font=fonte, fill=0)
        linhas.append(texto)
        y += entrelinha
    return imagem, linhas


def desenhar_tabela(corpo=10):
    """A tabela de bolsistas, com as linhas de grade que o Tesseract estranha."""
    imagem, desenho = _folha()
    x = 200
    y, linhas = _desenhar_cabecalho(desenho, x, 240)
    titulo = "Relação de pagamentos a bolsistas - março de 2026"
    desenho.text((x, y), titulo, font=_fonte(11, negrito=True), fill=0)
    linhas.append(titulo)
    y += 110

    # Onde cada coluna começa, em pixels da folha.
    colunas = [x, x + 760, x + 1240, x + 1720, 2280]
    altura = round(corpo * DENSIDADE / 72 * 1.9)
    fonte = _fonte(corpo)
    for numero, celulas in enumerate([COLUNAS] + BOLSISTAS):
        topo = y + numero * altura
        desenho.line([(colunas[0] - 20, topo), (colunas[-1], topo)], fill=0, width=3)
        fonte_da_linha = _fonte(corpo, negrito=True) if numero == 0 else fonte
        for coluna, celula in zip(colunas, celulas):
            desenho.text((coluna, topo + altura * 0.2), celula,
                         font=fonte_da_linha, fill=0)
        linhas.append(" ".join(celulas))
    base = y + (len(BOLSISTAS) + 1) * altura
    desenho.line([(colunas[0] - 20, base), (colunas[-1], base)], fill=0, width=3)
    for coluna in [c - 20 for c in colunas[:-1]] + [colunas[-1]]:
        desenho.line([(coluna, y), (coluna, base)], fill=0, width=3)
    return imagem, linhas


# ------------------------------------------------- o que o escâner faz com a folha


def chuviscar(imagem, intensidade):
    """Pontinhos espalhados, como a poeira e o grão de um escâner barato.

    O sorteio é o do próprio Python, e não o ruído pronto da biblioteca de
    imagem: aquele não obedece à semente, e a cada geração as páginas saíam com
    outro chuvisco - a medição deixava de poder ser refeita sobre as mesmas
    páginas (lente crítica, 16/10/2026). A proporção de pontinhos é a mesma de
    antes: a de um ruído com esta intensidade passar do limite escolhido.
    """
    proporcao = 0.5 * (1 + math.erf((90 - 128) / (intensidade * math.sqrt(2))))
    limite = round(proporcao * 256)
    sorteio = Image.frombytes("L", imagem.size,
                              random.randbytes(imagem.width * imagem.height))
    pontinhos = sorteio.point(lambda v: 120 if v < limite else 255)
    return ImageChops.multiply(imagem, pontinhos)


def torcer(imagem, graus):
    return imagem.rotate(graus, resample=Image.BICUBIC, expand=False, fillcolor=255)


def apagar_o_contraste(imagem):
    """Letra cinza num fundo cinza: original desbotado, ou cópia de cópia."""
    return imagem.point(lambda v: 125 + round(v * 95 / 255))


def borrar(imagem, raio):
    return imagem.filter(ImageFilter.GaussianBlur(raio))


def comprimir_mal(imagem, densidade=150, qualidade=25):
    """O que o escâner configurado para "arquivo pequeno" grava."""
    reduzida = imagem.resize((imagem.width * densidade // DENSIDADE,
                              imagem.height * densidade // DENSIDADE))
    saida = io.BytesIO()
    reduzida.save(saida, "JPEG", quality=qualidade)
    return saida.getvalue()


def _png(imagem):
    saida = io.BytesIO()
    imagem.save(saida, "PNG")
    return saida.getvalue()


def montar_paginas():
    """As páginas, em ordem: (nome, o que testa, bytes da imagem, gabarito)."""
    random.seed(7)
    paginas = []

    oficio, gabarito_oficio = desenhar_oficio()
    tabela, gabarito_tabela = desenhar_tabela()

    # Um defeito por página, e as limpas limpas de verdade. Na primeira versão
    # todas levavam um chuvisco fino "para parecer escaneado", e só ele já
    # derrubava o Tesseract na página limpa: a referência deixava de ser
    # referência, e a comparação ficava injusta com o motor de hoje. O chuvisco
    # agora tem página própria, com o nome dele.
    paginas.append(("oficio-limpo", "ofício limpo - a referência",
                    _png(oficio), gabarito_oficio))
    paginas.append(("tabela-limpa", "tabela com grade, limpa",
                    _png(tabela), gabarito_tabela))
    paginas.append(("tabela-com-poeira",
                    "a mesma tabela com pontinhos de poeira, como em escâner sujo",
                    _png(chuviscar(tabela, 20)), gabarito_tabela))
    paginas.append(("tabela-torta", "a mesma tabela, 2 graus torta no escâner",
                    _png(torcer(tabela, 2)), gabarito_tabela))
    paginas.append(("tabela-desbotada",
                    "a mesma tabela, desbotada, borrada e com chuvisco - a pior de todas",
                    _png(chuviscar(borrar(apagar_o_contraste(tabela), 1.6), 45)),
                    gabarito_tabela))
    paginas.append(("oficio-torto-comprimido",
                    "ofício 3 graus torto, gravado em baixa qualidade",
                    comprimir_mal(torcer(oficio, -3)), gabarito_oficio))

    # Deitado dentro da folha em pé: o ofício é desenhado numa folha deitada e a
    # imagem é girada para caber em pé, como a página 03 da massa antiga.
    deitado, gabarito_deitado = desenhar_oficio(tamanho=(A4_EM_PE[1], A4_EM_PE[0]))
    paginas.append(("oficio-deitado", "ofício com o conteúdo deitado 90 graus",
                    _png(deitado.rotate(90, expand=True)), gabarito_deitado))
    return paginas


def main():
    paginas = montar_paginas()
    documento = pymupdf.open()
    gabarito = []
    for nome, o_que_testa, imagem, linhas in paginas:
        folha = documento.new_page(width=595, height=842)
        folha.insert_image(folha.rect, stream=imagem)
        gabarito.append({"pagina": nome, "o_que_testa": o_que_testa,
                         "texto": "\n".join(linhas)})
    documento.save(PASTA / f"{NOME}.pdf", garbage=4, deflate=True)
    (PASTA / f"{NOME}.gabarito.json").write_text(
        json.dumps(gabarito, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(paginas)} páginas em {NOME}.pdf, com o gabarito ao lado.")


if __name__ == "__main__":
    main()

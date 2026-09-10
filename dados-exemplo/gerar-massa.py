r"""Gera a massa de teste do projeto: PDFs inventados, dentro de dados-exemplo/.

Nenhum dado aqui é de pessoa real. O CPF que aparece nos documentos
(123.456.789-10) tem dígito verificador errado de propósito, para que nem por
acidente ele bata com o de alguém.

Rode assim, da raiz do projeto:

    .\.venv\Scripts\python.exe dados-exemplo\gerar-massa.py
"""
import sys
from pathlib import Path

import pymupdf
from PySide6.QtCore import QMarginsF, Qt
from PySide6.QtGui import (
    QFont,
    QGuiApplication,
    QPageSize,
    QPainter,
    QPainterPath,
    QPdfWriter,
)

PASTA = Path(__file__).parent
CPF_INVENTADO = "123.456.789-10"

# Cabeçalho que se repete nos documentos, para eles parecerem com o que a CAPCF
# recebe de verdade - sem serem nada que a CAPCF tenha recebido de verdade.
CABECALHO = [
    "UNIVERSIDADE FEDERAL DE SANTA CATARINA",
    "Coordenadoria de Analise de Prestacoes de Contas Fundacionais",
]

PARAGRAFO = (
    "Trata-se de prestacao de contas referente ao projeto de pesquisa "
    "identificado abaixo, encaminhada pela fundacao de apoio para analise "
    "desta Coordenadoria. O responsavel indicado no termo de outorga e o "
    "servidor Fulano de Tal Exemplo, inscrito no CPF " + CPF_INVENTADO + ", "
    "conforme documentacao anexa aos autos do processo administrativo."
)

# A folha é A4 em pé, medida em pontos - a mesma unidade que o PyMuPDF usa.
LARGURA_DA_FOLHA = 595
ALTURA_DA_FOLHA = 842

# Onde o texto começa, contado da borda esquerda do papel.
MARGEM_ESQUERDA = 60

# Quantas letras cabem numa linha antes de ela precisar quebrar. O número foi
# medido para a linha caber na folha, e a folga é pouca: com a fonte usada nos
# documentos de contorno, a linha mais longa chega a dois pontos da borda
# direita. Aumentar este número corta o fim das linhas sem avisar ninguém.
LARGURA_DA_LINHA = 78

# A tabela vai como lista de linhas, e a primeira linha e o titulo das colunas.
TABELA = [
    ["Item", "Descricao da despesa", "Quantidade", "Valor (R$)"],
    ["1", "Material de consumo para laboratorio", "12", "3.480,00"],
    ["2", "Passagens aereas nacionais", "4", "6.120,50"],
    ["3", "Diarias de campo", "18", "9.240,00"],
    ["4", "Servico de terceiros - pessoa juridica", "1", "15.000,00"],
    ["", "TOTAL", "", "33.840,50"],
]

# Onde cada coluna da tabela começa, contado a partir da margem esquerda. Os
# números foram escolhidos no olho, para a descrição mais longa da tabela
# ("Servico de terceiros - pessoa juridica") caber sem encostar na coluna
# seguinte. Mexer no texto de uma coluna pede conferir estes números de novo.
COLUNAS_X = [0, 60, 330, 430]


def _texto_da_pagina(numero, total):
    """As linhas de uma página comum, na ordem em que vão para o papel."""
    linhas = list(CABECALHO)
    linhas.append("")
    linhas.append("PRESTACAO DE CONTAS - PROJETO 042/2026")
    linhas.append(f"Pagina {numero} de {total}")
    linhas.append("")
    for pedaco in _quebrar(PARAGRAFO, LARGURA_DA_LINHA):
        linhas.append(pedaco)
    return linhas


def _quebrar(texto, largura):
    """Quebra o parágrafo em linhas curtas, sem cortar palavra no meio."""
    palavras = texto.split()
    linhas, atual = [], ""
    for palavra in palavras:
        if len(atual) + len(palavra) + 1 > largura:
            linhas.append(atual)
            atual = palavra
        else:
            atual = f"{atual} {palavra}".strip()
    if atual:
        linhas.append(atual)
    return linhas


# ---------------------------------------------------------------------------
# As duas ferramentas dos documentos em que as letras viraram desenho (2 e 3)
# ---------------------------------------------------------------------------
def _desenhar_como_contorno(pintor, x, y, texto, tamanho, negrito=False):
    """Põe a palavra no papel como desenho de contorno, e não como texto.

    É o que imita o "Imprimir para PDF" do Windows: o arquivo fica sem nada
    legível por dentro e sem imagem de página nenhuma guardada, que é o caso
    que obriga o programa a rodar o OCR.
    """
    fonte = QFont("Arial", tamanho)
    fonte.setBold(negrito)
    contorno = QPainterPath()
    contorno.addText(x, y, fonte, texto)
    pintor.fillPath(contorno, Qt.black)


def _abrir_folha(caminho):
    """Prepara o papel A4 em pé, medido em pontos como o resto do projeto."""
    folha = QPdfWriter(str(caminho))
    folha.setPageSize(QPageSize(QPageSize.A4))
    folha.setResolution(72)  # 72 = a mesma unidade de medida do PyMuPDF
    folha.setPageMargins(QMarginsF(0, 0, 0, 0))
    return folha, QPainter(folha)


# ---------------------------------------------------------------------------
# 1. PDF com texto por dentro e uma tabela
# ---------------------------------------------------------------------------
def gerar_com_texto_e_tabela(caminho):
    documento = pymupdf.open()
    total = 3
    for numero in range(1, total + 1):
        pagina = documento.new_page(width=LARGURA_DA_FOLHA, height=ALTURA_DA_FOLHA)
        y = 70
        for linha in _texto_da_pagina(numero, total):
            pagina.insert_text((MARGEM_ESQUERDA, y), linha,
                               fontname="helv", fontsize=11)
            y += 16

        # A tabela só na última página, como nos documentos de verdade.
        if numero == total:
            y += 20
            pagina.insert_text((MARGEM_ESQUERDA, y), "DEMONSTRATIVO DE DESPESAS",
                               fontname="hebo", fontsize=12)
            y += 24
            for indice, linha in enumerate(TABELA):
                fonte = "hebo" if indice == 0 else "helv"
                for coluna, celula in enumerate(linha):
                    pagina.insert_text((MARGEM_ESQUERDA + COLUNAS_X[coluna], y),
                                       celula, fontname=fonte, fontsize=10)
                # Um traço embaixo do título das colunas, como numa tabela impressa.
                if indice == 0:
                    pagina.draw_line((MARGEM_ESQUERDA, y + 5), (535, y + 5),
                                     width=0.7)
                y += 18

    documento.save(caminho)
    documento.close()


# ---------------------------------------------------------------------------
# 2. PDF do "Imprimir para PDF": as letras viraram desenho
# ---------------------------------------------------------------------------
def gerar_imprimir_para_pdf(caminho, total=12):
    folha, pintor = _abrir_folha(caminho)
    for numero in range(1, total + 1):
        if numero > 1:
            folha.newPage()
        y = 70
        for linha in _texto_da_pagina(numero, total):
            if linha:
                _desenhar_como_contorno(pintor, MARGEM_ESQUERDA, y, linha, 11)
            y += 16

        if numero == total:
            y += 20
            _desenhar_como_contorno(pintor, MARGEM_ESQUERDA, y,
                                    "DEMONSTRATIVO DE DESPESAS", 12, negrito=True)
            y += 24
            for indice, tabela_linha in enumerate(TABELA):
                for coluna, celula in enumerate(tabela_linha):
                    if celula:
                        _desenhar_como_contorno(
                            pintor, MARGEM_ESQUERDA + COLUNAS_X[coluna], y,
                            celula, 10, negrito=(indice == 0))
                y += 18
    pintor.end()


# ---------------------------------------------------------------------------
# 3. PDF com o conteúdo deitado dentro de uma página em pé
# ---------------------------------------------------------------------------
def gerar_conteudo_girado(caminho):
    """Conteúdo deitado dentro de uma página em pé.

    O campo de rotação do PDF fica zerado - quem girou foi o conteúdo, não a
    página. É por isso que o programa não pode confiar nesse campo e precisa
    olhar a imagem para descobrir que está deitado (regra RN-6 da spec).
    """
    folha, pintor = _abrir_folha(caminho)
    pintor.save()
    # Gira o desenho um quarto de volta e o encosta na borda de baixo, que
    # depois do giro passa a ser a lateral esquerda do texto.
    pintor.translate(0, ALTURA_DA_FOLHA)
    pintor.rotate(-90)

    # Dentro do desenho girado os eixos não são mais os da folha: o que faz o
    # texto descer linha a linha aqui é a mesma coisa que nas outras funções se
    # chama y, e por isso o nome fala do papel dele, e não do eixo.
    avanco_da_linha = 70
    for linha in _texto_da_pagina(1, 1):
        if linha:
            _desenhar_como_contorno(pintor, MARGEM_ESQUERDA, avanco_da_linha,
                                    linha, 11)
        avanco_da_linha += 16
    pintor.restore()
    pintor.end()


# ---------------------------------------------------------------------------
# 4. PDF com camada de texto embaralhada
# ---------------------------------------------------------------------------
def gerar_texto_embaralhado(caminho):
    """Camada de texto que existe, mas sai como lixo ao ser lida.

    É o que acontece com documento que já passou por um OCR ruim antes: o
    arquivo tem texto por dentro, e esse texto não quer dizer nada. O programa
    não julga isso sozinho - ele mostra as primeiras linhas e quem olha decide.
    """
    documento = pymupdf.open()
    pagina = documento.new_page(width=LARGURA_DA_FOLHA, height=ALTURA_DA_FOLHA)
    lixo = [
        "Ø¶§ þÝÆµ ¤ÐÑÞ° «»©",
        "þýü Ø×Ö µ¶· ¤¥¦ ÐÑÒ",
        "«¬­® ¿ÀÁ Þßà ðñò °±",
        "©ª« ÆÇÈ ÕÖ× åæç õö",
    ]
    y = 90
    # Repete o lixo até encher a página, para não sobrar folha em branco.
    for linha in lixo * 6:
        pagina.insert_text((MARGEM_ESQUERDA, y), linha,
                           fontname="helv", fontsize=12)
        y += 18
    documento.save(caminho)
    documento.close()


# ---------------------------------------------------------------------------
# 5. Arquivo que não abre
# ---------------------------------------------------------------------------
def gerar_corrompido(caminho):
    """Começa como PDF e termina no meio, como arquivo que veio truncado."""
    with open(caminho, "wb") as arquivo:
        arquivo.write(b"%PDF-1.7\n")
        arquivo.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        arquivo.write(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1")
        # E acaba aqui, sem fechar nada: sem tabela de referencia e sem %%EOF.


# ---------------------------------------------------------------------------
# 6. PDF protegido por senha
# ---------------------------------------------------------------------------
def gerar_protegido(caminho):
    documento = pymupdf.open()
    pagina = documento.new_page(width=LARGURA_DA_FOLHA, height=ALTURA_DA_FOLHA)
    pagina.insert_text((MARGEM_ESQUERDA, 90), "Documento protegido por senha.",
                       fontname="helv", fontsize=12)
    # A senha não é segredo de nada: ela abre um arquivo inventado por este
    # mesmo script, e está publicada no README.md desta pasta de propósito.
    documento.save(
        caminho,
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        user_pw="senha-de-teste",
        owner_pw="senha-de-teste",
    )
    documento.close()


def main():
    # Desenhar com o Qt exige o aplicativo de pé, ainda que nenhuma janela
    # apareça. E ele precisa subir no modo normal do Windows: no modo "sem
    # tela" o Qt não enxerga as fontes instaladas e desenha um quadradinho no
    # lugar de cada letra - o arquivo fica cheio de caixas pretas e o OCR não
    # lê nada. A aplicação fica guardada numa variável para não ser recolhida
    # da memória no meio do trabalho.
    aplicacao = QGuiApplication.instance() or QGuiApplication(sys.argv)

    PASTA.mkdir(exist_ok=True)
    gerados = []

    for nome, gerar in [
        ("01-com-texto-e-tabela.pdf", gerar_com_texto_e_tabela),
        ("02-imprimir-para-pdf.pdf", gerar_imprimir_para_pdf),
        ("03-conteudo-girado.pdf", gerar_conteudo_girado),
        ("04-texto-embaralhado.pdf", gerar_texto_embaralhado),
        ("05-corrompido.pdf", gerar_corrompido),
        ("06-protegido-por-senha.pdf", gerar_protegido),
    ]:
        caminho = PASTA / nome
        gerar(caminho)
        gerados.append(caminho)

    for caminho in gerados:
        print(f"gerado: {caminho.name} ({caminho.stat().st_size} bytes)")

    del aplicacao


if __name__ == "__main__":
    main()

"""Remonta o texto do jeito que ele estava disposto na página.

O problema que isto resolve: tanto o PDF quanto o OCR entregam o texto como uma
lista de palavras soltas, cada uma com a posição em que estava na folha. Jogando
essas palavras numa linha, uma tabela vira uma coisa por linha - "Diarias de
campo", "18", "9.240,00", cada uma sozinha - e ninguém consegue ler.

Pondo cada palavra na coluna em que ela estava, a tabela volta a parecer uma
tabela, com as colunas embaixo umas das outras (regra RN-10 da spec 002). E o
texto corrido continua lendo normalmente, porque as palavras dele já estão
seguidas.

Este arquivo não sabe se o texto veio do PDF ou do OCR: ele recebe palavras com
posição, de qualquer origem. É por isso que a mesma remontagem serve para os
dois caminhos.
"""


# Até quantas letras de vão entre duas palavras ainda contam como um espaço
# simples. Acima disso, o vão é mudança de coluna. Dois é folgado o bastante
# para o espaço depois de um ponto final, e apertado o bastante para não comer
# a separação entre colunas de uma tabela.
LARGURA_DE_UM_VAO_COMUM = 2.0


def montar(linhas_de_palavras):
    """Devolve uma linha de texto por linha de palavras.

    Cada linha é uma lista de palavras `(x_inicial, x_final, texto)`, medidas na
    mesma unidade - pontos no caso do PDF, pixels no caso da imagem lida. A
    unidade não importa, porque a largura da letra é medida das próprias
    palavras.
    """
    todas = [p for linha in linhas_de_palavras for p in linha if p[2]]
    if not todas:
        return []

    largura_da_letra = _largura_media_da_letra(todas)
    montadas = [_montar_uma(linha, largura_da_letra) for linha in linhas_de_palavras]
    return _sem_a_margem_comum(montadas)


def agrupar_por_altura(palavras):
    """Junta em uma linha as palavras que estão na mesma altura da folha.

    Serve para o texto que vem do PDF. Ali cada pedaço pode ter sido gravado
    como um texto separado - numa tabela, célula por célula -, e o arquivo não
    diz que eles formam uma linha só. Quem diz é a altura: o que está lado a
    lado na folha se lê junto.

    Entre blocos separados por um vão grande entra uma linha em branco, que é o
    que mantém os parágrafos separados no arquivo final.

    `palavras` é uma lista de `(x_inicial, y_topo, x_final, y_base, texto)` -
    a mesma ordem em que o PyMuPDF entrega as palavras do PDF.
    """
    if not palavras:
        return []

    tolerancia = _meia_altura_da_letra(palavras)

    linhas = []
    atual = []
    meio_da_linha = None
    meio_da_linha_anterior = None
    for x0, y0, x1, y1, texto in sorted(
        palavras, key=lambda p: ((p[1] + p[3]) / 2, p[0])
    ):
        meio = (y0 + y1) / 2
        if meio_da_linha is None:
            meio_da_linha = meio
        elif abs(meio - meio_da_linha) > tolerancia:
            linhas.append(atual)
            if meio_da_linha_anterior is not None and _ha_um_vao(
                meio_da_linha, meio_da_linha_anterior, meio, tolerancia
            ):
                linhas.append([])
            meio_da_linha_anterior = meio_da_linha
            atual = []
            meio_da_linha = meio
        atual.append((x0, x1, texto))
    if atual:
        linhas.append(atual)
    return linhas


def _meia_altura_da_letra(palavras):
    """Quanta diferença de altura ainda conta como a mesma linha.

    A medida sai da **altura das próprias letras**, e não dos vãos entre as
    alturas da página. A diferença importa: um carimbo de lado na margem - comum
    em documento que vem de sistema de processos - tem palavras espalhadas
    verticalmente, e isso inflava a conta feita por vãos a ponto de o programa
    passar a achar que linhas diferentes eram a mesma, fundindo e intercalando
    o corpo do texto. A altura da letra não muda porque existe um carimbo na
    margem.
    """
    alturas = sorted(abs(y1 - y0) for _x0, y0, _x1, y1, _t in palavras)
    if not alturas:
        return 1.0
    tipica = alturas[len(alturas) // 2]
    return max(tipica / 2, 1.0)


def _ha_um_vao(linha_de_agora, linha_anterior, proxima, tolerancia):
    """Diz se o salto até a linha seguinte é maior que a entrelinha do texto.

    Vão grande separa blocos - o cabeçalho do corpo, um parágrafo do seguinte -,
    e no arquivo final essa separação precisa virar uma linha em branco: em
    `.md`, linhas seguidas sem uma linha vazia entre elas viram um parágrafo só.
    """
    entrelinha = abs(linha_de_agora - linha_anterior)
    if entrelinha <= tolerancia:
        return False
    return abs(proxima - linha_de_agora) > entrelinha * 1.5


def _largura_media_da_letra(palavras):
    """Quanto uma letra ocupa, em média, neste documento.

    Medida das próprias palavras, e não escolhida a dedo: documento escaneado a
    300 pontos por polegada tem letra de dezenas de pixels, e o mesmo documento
    lido do PDF tem letra de poucos pontos. Um número fixo serviria para um e
    estragaria o outro.
    """
    largura = sum((x1 - x0) / len(texto) for x0, x1, texto in palavras) / len(palavras)
    # Documento quase vazio pode dar uma média absurda; abaixo de um ponto a
    # conta de colunas estoura em linhas gigantes.
    return max(largura, 1.0)


def _montar_uma(linha, largura_da_letra):
    """Monta uma linha de texto a partir das palavras dela.

    A decisão a cada palavra é uma só: **um espaço, ou um pulo até a coluna?**
    Ela sai do vão que a palavra deixou da anterior. Vão do tamanho de um espaço
    é um espaço - é assim que "UNIVERSIDADE FEDERAL" continua lendo como frase.
    Vão grande é outra coluna, e aí a palavra vai para o lugar em que ela estava
    na folha - é assim que a tabela continua parecendo uma tabela.

    Medir o vão, e não a posição de cada palavra, é o que faz o título em
    maiúsculas não sair esparramado: maiúscula é mais larga que a média, e uma
    conta feita só pela posição espalharia espaços dentro da frase.
    """
    vao_que_ainda_e_espaco = largura_da_letra * LARGURA_DE_UM_VAO_COMUM

    texto = ""
    fim_da_anterior = None
    for x0, x1, palavra in sorted(linha):
        if not palavra:
            continue
        if fim_da_anterior is None:
            texto = " " * int(x0 / largura_da_letra)
        elif x0 - fim_da_anterior <= vao_que_ainda_e_espaco:
            texto += " "
        else:
            coluna = int(x0 / largura_da_letra)
            texto += " " * max(coluna - len(texto), 1)
        texto += palavra
        fim_da_anterior = x1
    return texto.rstrip()


def _sem_a_margem_comum(linhas):
    """Tira o recuo que todas as linhas têm, que é só a margem do papel."""
    margem = min(
        (len(linha) - len(linha.lstrip()) for linha in linhas if linha.strip()),
        default=0,
    )
    return [linha[margem:] if linha.strip() else "" for linha in linhas]

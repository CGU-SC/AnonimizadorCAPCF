"""Descobre o que há dentro de um PDF, sem nunca alterá-lo.

Este arquivo não desenha nada na tela e não sabe que existe uma janela: ele só
abre o PDF, conta as páginas e mede a camada de texto. Ficar separado da tela é
o que permite conferir estas contas por teste automático, sem abrir o programa.
"""
from dataclasses import dataclass
from pathlib import Path

import pymupdf

from disposicao import agrupar_por_altura, montar


class DocumentoNaoAbre(Exception):
    """O arquivo escolhido não pôde ser lido como PDF.

    A mensagem que vem junto é escrita para aparecer na tela do jeito que está,
    em linguagem comum - quem usa o programa não tem por que saber o nome
    técnico do defeito do arquivo.
    """


@dataclass(frozen=True)
class FichaDoDocumento:
    """O que o programa descobriu sobre o documento escolhido."""

    caminho: Path
    paginas: int
    letras_na_camada_de_texto: int

    @property
    def tem_camada_de_texto(self):
        return self.letras_na_camada_de_texto > 0


def conferir(caminho):
    """Abre o PDF, conta as páginas e mede a camada de texto.

    Levanta DocumentoNaoAbre quando o arquivo não serve, com a frase pronta
    para a tela.
    """
    caminho = Path(caminho)

    if not caminho.exists():
        raise DocumentoNaoAbre(
            "O arquivo não foi encontrado. Ele pode ter sido movido ou "
            "apagado depois de escolhido."
        )

    try:
        # Abrir não escreve nada no arquivo: a regra RN-17 da spec 002 diz que
        # o PDF de origem nunca é alterado, e o programa nunca chama o comando
        # de salvar sobre ele.
        documento = pymupdf.open(caminho)
    except Exception:
        raise DocumentoNaoAbre(
            "O arquivo não pôde ser aberto. Ele pode estar danificado ou não "
            "ser um PDF, apesar do nome."
        )

    try:
        if documento.needs_pass:
            raise DocumentoNaoAbre(
                "O documento está protegido por senha, e o programa não abre "
                "documento protegido."
            )

        paginas = documento.page_count
        if paginas == 0:
            raise DocumentoNaoAbre("O documento está vazio: não tem nenhuma página.")

        letras = _contar_letras_da_camada_de_texto(documento)
    finally:
        documento.close()

    return FichaDoDocumento(
        caminho=caminho, paginas=paginas, letras_na_camada_de_texto=letras
    )


def texto_da_camada(caminho):
    """Devolve o texto que já está gravado dentro do PDF, uma entrada por página.

    É o texto que a pessoa pode escolher aproveitar, em vez de mandar o programa
    reler as imagens. Separado por página como o do OCR (regra RN-8), porque a
    tela de conferência é a mesma nos dois caminhos.

    O texto sai remontado pela posição das palavras na folha, e não na ordem
    solta em que o PDF as guarda: é o que faz a tabela continuar parecendo uma
    tabela (RN-10).
    """
    documento = pymupdf.open(caminho)
    try:
        return [
            "\n".join(montar(_linhas_da_pagina(pagina))) for pagina in documento
        ]
    finally:
        documento.close()


def _linhas_da_pagina(pagina):
    """Agrupa as palavras da página nas linhas a que elas pertencem.

    O agrupamento é pela altura na folha, e não pelo que o PDF chama de linha:
    numa tabela, cada célula costuma ter sido gravada como um texto separado, e
    o arquivo não diz que elas formam uma linha só. Confiar nele ali devolveria
    uma célula por linha, que é exatamente o problema que esta etapa resolve.
    """
    # O PyMuPDF entrega cada palavra com mais três números no fim - em que bloco,
    # em que linha e em que posição dela o próprio PDF a guardou. A remontagem
    # não usa nenhum dos três: ela decide a linha pela altura na folha.
    palavras = [
        (x0, y0, x1, y1, texto)
        for x0, y0, x1, y1, texto, *_ in pagina.get_text("words")
    ]
    return agrupar_por_altura(palavras)


def primeiras_linhas(paginas, quantas=12):
    """As primeiras linhas com conteúdo, para a pessoa julgar o texto num olhar.

    Linha vazia não conta: PDF escaneado devolve páginas cheias delas, e mostrar
    uma amostra em branco não deixa ninguém decidir nada.
    """
    linhas = []
    for pagina in paginas:
        for linha in pagina.splitlines():
            if linha.strip():
                linhas.append(linha.rstrip())
                if len(linhas) == quantas:
                    return linhas
    return linhas


def _contar_letras_da_camada_de_texto(documento):
    """Conta quantas letras existem gravadas como texto dentro do PDF.

    A regra RN-3 da spec 002 exige contagem exata, e não palpite: ou há texto
    ali, ou não há. Espaço e quebra de linha não entram na conta porque muitos
    PDFs escaneados devolvem uma página cheia de quebras de linha e nenhuma
    letra - contá-las faria o programa anunciar texto onde não existe nenhum.

    Julgar se esse texto PRESTA é outra coisa, e não é do programa: quem olha
    as primeiras linhas e decide é a pessoa (RN-4).
    """
    total = 0
    for pagina in documento:
        total += len("".join(pagina.get_text().split()))
    return total

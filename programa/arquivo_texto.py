"""Abre o `.md` ou o `.txt` que a pessoa escolheu no Anonimizar.

Ler um arquivo de texto parece trivial e não é: o Windows grava texto de dois
jeitos diferentes, e um arquivo que não é texto abre do mesmo jeito, só que com
lixo dentro. Este arquivo trata os dois casos e devolve sempre texto legível,
ou um aviso em português dizendo o que houve.
"""
import unicodedata
from pathlib import Path

# Os dois jeitos como o Bloco de Notas do Windows grava (regra RN-21): o de
# hoje, e o antigo, do Windows em português. A ordem importa: quase todo
# arquivo de hoje é o primeiro, e o segundo nunca falha na leitura - ele aceita
# quase qualquer byte -, então tentá-lo antes esconderia os acentos errados do
# outro.
CODIFICACOES = ("utf-8-sig", "cp1252")

# As letras invisíveis que texto de verdade usa: quebra de linha, tabulação,
# avanço de página (o separador de páginas do texto tirado de PDF) e a
# tabulação vertical, que costuma vir junto com ele.
BRANCOS_DE_TEXTO = "\n\r\t\f\v"

# Quanto de letra estranha um arquivo pode ter e ainda contar como texto. Um
# símbolo perdido no meio de um documento é coisa de conversor; arquivo que não
# é texto vem cheio deles.
PROPORCAO_DE_ESTRANHOS = 0.01


# As duas quebras de linha que um documento pode usar: a do Windows, de duas
# letras invisíveis, e a simples.
QUEBRA_DO_WINDOWS = "\r\n"
QUEBRA_SIMPLES = "\n"


class ArquivoNaoServe(Exception):
    """O arquivo escolhido não tem texto que dê para procurar CPF."""


def ler(caminho):
    """O texto do arquivo, com as quebras de linha todas do mesmo jeito.

    As quebras de linha do Windows (duas letras invisíveis) viram uma só, para
    o resto do programa não precisar saber de qual máquina o arquivo veio. Isso
    não muda o que se vê na tela nem no arquivo gravado depois.
    """
    caminho = Path(caminho)
    bruto = caminho.read_bytes()

    texto = None
    for codificacao in CODIFICACOES:
        try:
            texto = bruto.decode(codificacao)
            break
        except UnicodeDecodeError:
            continue

    if texto is None or not _parece_texto(texto):
        raise ArquivoNaoServe(
            f"O arquivo {caminho.name} não parece ser texto — pode ser outro "
            "tipo de arquivo com o nome trocado."
        )

    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    # A conferência de vazio acontece depois da leitura, e não sobre os bytes:
    # o Bloco de Notas põe três bytes invisíveis no começo de todo arquivo que
    # grava, e um arquivo "vazio" dele tem esses três. Olhando os bytes, ele
    # escapava da trava e abria a revisão em branco, com o aviso de "nenhum CPF
    # encontrado" falando de um documento que não existe.
    if not texto.strip():
        raise ArquivoNaoServe(
            f"O arquivo {caminho.name} está vazio — não há texto nele para "
            "procurar CPF."
        )
    return texto


def quebra_de_linha(caminho):
    """Qual quebra de linha o documento usa, para o arquivo sair igual a ele.

    O programa lê tudo com a quebra simples, para o resto dele não precisar
    saber de qual máquina o arquivo veio - mas o arquivo gravado precisa voltar
    à quebra do documento (revisão da etapa 5). Sem isso, todo documento escrito
    no Windows saía com as quebras trocadas, o que a RN-12 não permite: o
    arquivo tem o texto do documento, com as máscaras, e nada mais mudado.

    Achando qualquer quebra do Windows, o arquivo inteiro sai com ela: documento
    de quebra misturada é defeito de quem o gerou, e escolher uma é o que deixa
    o arquivo abrir igual em qualquer programa.
    """
    return (QUEBRA_DO_WINDOWS if b"\r\n" in Path(caminho).read_bytes()
            else QUEBRA_SIMPLES)


def _parece_texto(texto):
    """Diz se o que foi lido é texto de gente, e não o miolo de outro arquivo.

    Planilha, imagem e PDF renomeados para `.md` abrem sem reclamar: o segundo
    jeito de ler aceita quase qualquer byte e devolve um punhado de símbolos sem
    sentido. O que os denuncia são as letras de controle - as invisíveis que
    nenhum texto usa.

    A conferência tem folga de propósito. Sem ela, texto de verdade era
    recusado: o `.txt` tirado de um PDF traz o avanço de página entre uma página
    e outra, e o `.md` salvo pelo Word usa um símbolo próprio no marcador de
    lista. Recusar um arquivo bom é o pior erro possível aqui - a pessoa desiste
    do programa e manda o documento com os CPFs inteiros para o assistente.
    """
    # Byte zero não aparece em texto, e aparece em quase todo arquivo que não é
    # texto: é o sinal mais confiável dos dois lados.
    if "\x00" in texto:
        return False
    estranhos = sum(
        1 for letra in texto
        if letra not in BRANCOS_DE_TEXTO
        and unicodedata.category(letra) in ("Cc", "Cs", "Cn")
    )
    return estranhos <= len(texto) * PROPORCAO_DE_ESTRANHOS

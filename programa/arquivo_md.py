"""Grava o texto conferido num arquivo `.md`.

Este arquivo não desenha nada na tela: ele sugere onde salvar, monta o
conteúdo e grava. Ficar separado da tela é o que permite conferir por teste
automático duas promessas da spec que ninguém enxerga olhando a janela — que o
arquivo não leva nenhum aviso do programa dentro, e que nada é escrito pela
metade.
"""
import os
import tempfile
from pathlib import Path


def caminho_sugerido(pdf):
    """A mesma pasta do documento, o mesmo nome, terminação `.md` (regra RN-15).

    Quem não quer pensar em onde salvar só clica em salvar, e o arquivo aparece
    ao lado do documento de onde saiu - que é onde a pessoa vai procurar.
    """
    return Path(pdf).with_suffix(".md")


def caminho_sem_cpf(origem):
    """Onde o arquivo do Anonimizar é sugerido: ao lado da origem (regra RN-13).

    Mesma pasta, mesmo nome, mais " - sem CPF.md". O nome diz o que o arquivo é
    no momento em que mais importa: na hora de arrastar um dos dois para a
    conversa com o assistente, com os dois lado a lado na pasta.
    """
    origem = Path(origem)
    return origem.with_name(f"{origem.stem} - sem CPF.md")


def caminho_livre(caminho):
    """Um nome parecido que ainda não existe na pasta: `nome (2).md`, `nome (3).md`.

    Serve para o "salvar com outro nome": o programa oferece um que não apaga
    nada, e a pessoa aceita ou troca.
    """
    caminho = Path(caminho)
    numero = 2
    while True:
        candidato = caminho.with_name(f"{caminho.stem} ({numero}){caminho.suffix}")
        if not candidato.exists():
            return candidato
        numero += 1


# O que pode estar errado no caminho que a pessoa digitou. As telas escrevem a
# frase de cada um com as palavras delas; aqui fica só a decisão, que é a mesma
# nos dois módulos (revisão pela lente de manutenção, 18/09/2026: o conserto da
# janela do Windows precisou ser escrito duas vezes, e as duas telas já tinham
# frases diferentes para a mesma situação).
FALTA_O_CAMINHO = "falta o caminho"
FALTA_A_PASTA = "falta a pasta"
PASTA_NAO_EXISTE = "pasta não existe"


def conferir_destino(digitado, pasta_sugerida):
    """Devolve (caminho pronto, None) ou (None, o que está errado).

    Três coisas são acertadas em silêncio, porque reclamar delas seria implicar
    com quem está certo: o espaço sobrando nas pontas, o caminho sem pasta - que
    vai para a pasta sugerida, e não para a pasta de onde o programa foi aberto,
    que quem usa nem sabe qual é - e a terminação `.md` que faltou, que voltaria
    como um arquivo que nenhum programa sabe abrir.
    """
    digitado = digitado.strip()
    if not digitado:
        return None, FALTA_O_CAMINHO
    caminho = Path(digitado)
    if not caminho.is_absolute():
        if pasta_sugerida is None:
            return None, FALTA_A_PASTA
        caminho = Path(pasta_sugerida) / caminho
    if caminho.suffix.lower() != ".md":
        caminho = caminho.with_name(caminho.name + ".md")
    # A pasta que não existe volta junto com o caminho montado, e não só com o
    # problema: é dela que a tela precisa para dizer qual pasta não achou. Quem
    # chama olha o problema primeiro, e por isso nunca grava sem querer.
    if not caminho.parent.exists():
        return caminho, PASTA_NAO_EXISTE
    return caminho, None


def montar_conteudo(paginas):
    """O texto que vai para dentro do arquivo: o do documento, e mais nada.

    Nenhum aviso do programa entra aqui - nem "veio do OCR", nem a contagem de
    correções, nem data, nem marca de página (regra RN-11). Recado no meio do
    texto ninguém lê, e ele ainda viaja para dentro da conversa com o
    assistente de IA, onde vira ruído que parece fazer parte do documento.

    As páginas são separadas por uma linha em branco. Uma marca como "--- página
    2 ---" seria justamente o tipo de recado que a regra proíbe.
    """
    return "\n\n".join(pagina.strip("\n") for pagina in paginas) + "\n"


def gravar(caminho, conteudo, fim_de_linha="\n"):
    """Grava o arquivo inteiro, ou não grava nada.

    O texto é escrito primeiro num arquivo provisório na mesma pasta, e só
    depois de pronto troca de nome para o definitivo. Se a gravação for
    interrompida no meio - disco cheio, pasta de rede que caiu, programa
    fechado -, o que fica é o provisório apagado, e não um `.md` pela metade
    que a pessoa arrastaria para a conversa achando que está inteiro.

    O `fim_de_linha` é a quebra com que o arquivo é escrito. O Anonimizar manda
    a do documento de origem, para o arquivo sair com a quebra que ele usava
    (revisão da etapa 5); o texto vindo do OCR não tem documento de texto atrás
    dele, e fica com a quebra simples.
    """
    caminho = Path(caminho)
    descritor, provisorio = tempfile.mkstemp(
        dir=caminho.parent, prefix=".gravando-", suffix=".md"
    )
    try:
        with os.fdopen(descritor, "w", encoding="utf-8",
                       newline=fim_de_linha) as arquivo:
            arquivo.write(conteudo)
        os.replace(provisorio, caminho)
    except BaseException:
        if os.path.exists(provisorio):
            os.remove(provisorio)
        raise

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


def gravar(caminho, conteudo):
    """Grava o arquivo inteiro, ou não grava nada.

    O texto é escrito primeiro num arquivo provisório na mesma pasta, e só
    depois de pronto troca de nome para o definitivo. Se a gravação for
    interrompida no meio - disco cheio, pasta de rede que caiu, programa
    fechado -, o que fica é o provisório apagado, e não um `.md` pela metade
    que a pessoa arrastaria para a conversa achando que está inteiro.
    """
    caminho = Path(caminho)
    descritor, provisorio = tempfile.mkstemp(
        dir=caminho.parent, prefix=".gravando-", suffix=".md"
    )
    try:
        with os.fdopen(descritor, "w", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(conteudo)
        os.replace(provisorio, caminho)
    except BaseException:
        if os.path.exists(provisorio):
            os.remove(provisorio)
        raise

"""O que cada instalação do programa tem de próprio: a pasta dela e o `.env`.

Cada máquina do núcleo tem o seu `.env`, preenchido pela TI na hora da
instalação e nunca versionado. Este arquivo só sabe onde ele fica e como tirar
um valor de dentro dele.
"""
import codecs
import sys
from pathlib import Path


def pasta_do_programa():
    """A pasta onde o programa está instalado.

    No `.exe` da entrega é a pasta do próprio `.exe`; aqui, no desenvolvimento,
    é a raiz do projeto. É ao lado dela que ficam o `.env` e a pasta
    `instaladores`, e é por isso que as duas situações precisam dar no mesmo
    lugar.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def valor_do_env(nome):
    """O valor de uma variável do `.env` desta instalação, ou None.

    Lido na mão, e não com uma biblioteca: são poucas linhas no formato
    NOME=valor, e uma dependência a mais seria mais uma coisa para empacotar no
    `.exe` e manter atualizada. Valor em branco conta como não preenchido - é
    assim que ele vem no `.env.example`.
    """
    texto = _texto_do_env(pasta_do_programa() / ".env")
    if texto is None:
        return None

    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        if chave.strip() != nome:
            continue
        # Aspas em volta são o jeito comum de escrever caminho com espaço, como
        # "C:\Program Files\...". Elas não fazem parte do caminho.
        valor = valor.strip().strip('"').strip("'").strip()
        return valor or None
    return None


def _texto_do_env(arquivo):
    """O conteúdo do `.env`, em qualquer um dos formatos que o Windows grava.

    Quem preenche o `.env` é a TI, no editor que tiver à mão, e o Bloco de
    Notas oferece "UTF-8", "Unicode" e "ANSI". O `.env.example` tem acentos nos
    comentários, então os três formatos saem diferentes byte a byte - e aceitar
    só um fazia o programa estourar ao abrir, sem janela e sem mensagem.

    Não dando para ler de jeito nenhum, segue como se não houvesse `.env`: o
    programa ainda procura o motor nas pastas de costume, e o aviso na tela diz
    se não achar.
    """
    try:
        conteudo = arquivo.read_bytes()
    except OSError:
        return None

    if conteudo.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        formatos = ["utf-16"]
    else:
        # O "ANSI" do Windows em português é o cp1252, e fica por último: ele
        # aceita quase qualquer sequência de bytes, então vindo antes leria
        # errado um arquivo que era UTF-8.
        formatos = ["utf-8-sig", "cp1252"]

    for formato in formatos:
        try:
            return conteudo.decode(formato)
        except UnicodeDecodeError:
            continue
    return None

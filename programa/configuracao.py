"""O que cada instalação do programa tem de próprio: a pasta dela e o `.env`.

Cada máquina do núcleo tem o seu `.env`, preenchido pela TI na hora da
instalação e nunca versionado. Este arquivo só sabe onde ele fica e como tirar
um valor de dentro dele.
"""
import codecs
import os
import sys
import time
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


def caminho_do_env():
    return pasta_do_programa() / ".env"


def valor_do_env(nome):
    """O valor de uma variável do `.env` desta instalação, ou None.

    Lido na mão, e não com uma biblioteca: são poucas linhas no formato
    NOME=valor, e uma dependência a mais seria mais uma coisa para empacotar no
    `.exe` e manter atualizada. Valor em branco conta como não preenchido - é
    assim que ele vem no `.env.example`.
    """
    texto = _texto_do_env(caminho_do_env())
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


def gravar_no_env(nome, valor):
    """Grava uma linha `NOME=valor` no `.env`, e nada além dela (RN-11 da spec 004).

    O arquivo é da TI, com os comentários e o formato dela: tudo o que não é aquela
    linha continua igual, byte a byte, no formato em que estava. Só o token passa por
    aqui. Devolve False quando não deu para gravar, sem deixar nada pela metade.
    """
    if "\n" in valor or "\r" in valor:
        return False
    arquivo = caminho_do_env()
    try:
        conteudo = arquivo.read_bytes()
    except FileNotFoundError:
        conteudo = b""
    except OSError:
        return False
    marca, formato = _formato_do_env(conteudo)
    try:
        texto = conteudo[len(marca):].decode(formato)
        novo = marca + _com_a_linha(texto, nome, valor).encode(formato)
    except (UnicodeDecodeError, UnicodeEncodeError):
        # Um caractere que o formato do arquivo não sabe escrever: melhor recusar do
        # que trocar o formato de um arquivo que é da TI.
        return False
    provisorio = arquivo.with_name(f"{arquivo.name}.{os.getpid()}.gravando")
    try:
        with open(provisorio, "wb") as saida:
            saida.write(novo)
            saida.flush()
            os.fsync(saida.fileno())
        trocar_com_paciencia(provisorio, arquivo)
    except OSError:
        try:
            provisorio.unlink(missing_ok=True)
        except OSError:
            pass
        return False
    return True


def trocar_com_paciencia(provisorio, destino):
    """Põe o provisório no lugar do arquivo de verdade.

    O antivírus do Windows abre o arquivo por um instante para examiná-lo, e nesse
    instante a troca é recusada. Sem insistir, a escolha ou o token da pessoa se
    perdiam por um acaso (lente crítica da etapa 4 da funcionalidade 8). Cinco
    tentativas num quarto de segundo cobrem esse instante sem a janela parecer travada.
    """
    for tentativa in range(5):
        try:
            os.replace(provisorio, destino)
            return
        except PermissionError:
            if tentativa == 4:
                raise
            time.sleep(0.05)


def _formato_do_env(conteudo):
    """A marca do começo do arquivo e o formato do resto, como o Bloco de Notas salvou."""
    if conteudo.startswith(codecs.BOM_UTF16_LE):
        return codecs.BOM_UTF16_LE, "utf-16-le"
    if conteudo.startswith(codecs.BOM_UTF16_BE):
        return codecs.BOM_UTF16_BE, "utf-16-be"
    if conteudo.startswith(codecs.BOM_UTF8):
        return codecs.BOM_UTF8, "utf-8"
    try:
        conteudo.decode("utf-8")
    except UnicodeDecodeError:
        return b"", "cp1252"
    return b"", "utf-8"


def _com_a_linha(texto, nome, valor):
    """O texto com a linha daquele nome trocada, ou acrescentada no fim."""
    linhas = texto.splitlines(keepends=True)
    achou = False
    for indice, linha in enumerate(linhas):
        limpa = linha.strip()
        if (limpa.startswith("#") or "=" not in limpa
                or limpa.split("=", 1)[0].strip() != nome):
            continue
        sem_fim = linha.rstrip("\r\n")
        # Linha repetida fica igual à primeira: quem lê só olha a primeira, e apagar
        # o token não pode deixar uma cópia dele para trás.
        linhas[indice] = f"{nome}={valor}{linha[len(sem_fim):]}"
        achou = True
    if achou:
        return "".join(linhas)
    fim = "\r\n" if "\r\n" in texto else "\n"
    if texto and not texto.endswith(("\n", "\r")):
        texto += fim
    return f"{texto}{nome}={valor}{fim}"


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
    return texto_de_bloco_de_notas(conteudo)


def texto_de_bloco_de_notas(conteudo):
    """O texto de um arquivo salvo no Bloco de Notas, em qualquer dos três
    formatos que ele oferece, ou None se não for nenhum deles.

    Serve também ao `preferencias.ini`, que a pessoa pode abrir e salvar à mão.
    """
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

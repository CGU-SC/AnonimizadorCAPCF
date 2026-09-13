"""Onde está o motor de leitura nesta máquina, e o que fazer quando ele falta.

O motor é o Tesseract, um programa instalado no próprio Windows. Este arquivo
procura por ele, guarda a pasta que a pessoa apontar, e abre o instalador que
a TI deixou ao lado do programa. Não baixa nada e não instala nada sozinho
(regra RN-20 da spec 002): quem instala é a pessoa, confirmando no Windows.
"""
import os
import shutil
from pathlib import Path

from configuracao import pasta_do_programa, valor_do_env

EXECUTAVEL = "tesseract.exe"

# O arquivo do pacote de português, com o mesmo nome em todas as versões do
# Tesseract. É o "por" que a leitura pede (leitura.IDIOMA).
PACOTE_DE_PORTUGUES = "por.traineddata"

# Onde o instalador do Tesseract costuma deixar o programa no Windows. Ele não
# entra no caminho que o Windows procura sozinho, então procurar aqui é o que
# faz o programa funcionar sem ninguém configurar nada em cada máquina do
# núcleo.
PASTAS_DE_COSTUME = [
    Path(r"C:\Program Files\Tesseract-OCR"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR"),
]

# A pasta onde a TI deixa o instalador, ao lado do programa. O nome é o
# combinado na spec 002 para o dia da entrega.
PASTA_DOS_INSTALADORES = "instaladores"

# A pasta que a pessoa apontou nesta sessão. Fica só na memória: nada é
# guardado entre um uso e outro do programa (RN-22). Para valer sempre, a TI
# grava o caminho no `.env` daquela máquina.
_pasta_apontada = None


def localizar_tesseract():
    """Devolve o Tesseract que lê português nesta máquina, ou None.

    Tesseract sem o pacote de português não serve: toda leitura falharia na
    primeira página (RN-19). Havendo mais de um instalado, vale o primeiro que
    tiver o pacote - um sem ele, achado antes, não pode esconder um bom.
    """
    for executavel in _executaveis_encontrados():
        if tem_o_portugues(executavel):
            return executavel
    return None


def ha_algum_tesseract():
    """Diz se há algum Tesseract nesta máquina, mesmo sem o português.

    Serve para o aviso dizer o que falta de verdade: pedir à TI que instale o
    motor, quando ele já está lá, faria a TI conferir, ver que está instalado,
    e não mexer em nada.
    """
    return any(True for _ in _executaveis_encontrados())


def tem_o_portugues(executavel):
    """Diz se o pacote de português está onde este Tesseract vai procurá-lo.

    O instalador põe os idiomas na pasta tessdata, ao lado do tesseract.exe, e
    o português vem como opção a marcar. A TI pode ter apontado outra pasta de
    idiomas na variável TESSDATA_PREFIX do Windows - e aí é lá que ele procura.
    """
    lugares = [Path(executavel).parent / "tessdata"]
    prefixo = os.environ.get("TESSDATA_PREFIX")
    if prefixo:
        # Conforme a versão, a variável aponta a própria pasta de idiomas ou a
        # pasta de cima dela. Aceitar as duas evita um aviso falso.
        lugares = [Path(prefixo), Path(prefixo) / "tessdata"]
    return any((lugar / PACOTE_DE_PORTUGUES).is_file() for lugar in lugares)


def _executaveis_encontrados():
    if _pasta_apontada is not None:
        achado = _o_executavel_em(_pasta_apontada)
        if achado:
            yield achado
    for candidato in _onde_procurar_sem_ajuda():
        achado = _o_executavel_em(candidato)
        if achado:
            yield achado


def _onde_procurar_sem_ajuda():
    """Os lugares onde o programa procura sozinho, na ordem em que procura.

    O `.env` vem antes das pastas de costume porque é a TI dizendo onde
    instalou - e a TI sabe mais sobre aquela máquina do que um palpite.
    """
    do_env = valor_do_env("TESSERACT_CAMINHO")
    if do_env:
        yield Path(do_env)

    no_caminho_do_windows = shutil.which("tesseract")
    if no_caminho_do_windows:
        yield Path(no_caminho_do_windows)

    yield from PASTAS_DE_COSTUME

    pasta_do_usuario = os.environ.get("LOCALAPPDATA")
    if pasta_do_usuario:
        yield Path(pasta_do_usuario) / "Programs" / "Tesseract-OCR"


def _o_executavel_em(caminho):
    """Aceita tanto a pasta quanto o próprio tesseract.exe.

    Quem aponta pode escolher qualquer um dos dois, e a TI pode escrever
    qualquer um dos dois no `.env`. Recusar um deles seria errar por
    formalidade.
    """
    caminho = Path(caminho)
    if caminho.name.lower() == EXECUTAVEL and caminho.is_file():
        return caminho
    dentro = caminho / EXECUTAVEL
    if dentro.is_file():
        return dentro
    return None


def apontar_pasta(pasta):
    """Guarda a pasta apontada, se ela tiver o Tesseract. Diz se tinha.

    Pasta sem o Tesseract não é guardada: guardá-la faria o programa procurar
    num lugar errado até ser fechado, e a pessoa não saberia disso. Pasta com o
    Tesseract e sem o português é guardada, sim - é o mesmo motor que a TI vai
    completar, e o aviso passa a dizer que é o pacote que falta.
    """
    global _pasta_apontada
    if _o_executavel_em(pasta) is None:
        return False
    _pasta_apontada = Path(pasta)
    return True


def esquecer_pasta_apontada():
    global _pasta_apontada
    _pasta_apontada = None


def localizar_instalador():
    """O instalador do Tesseract que a TI deixou ao lado do programa, ou None."""
    pasta = pasta_do_programa() / PASTA_DOS_INSTALADORES
    if not pasta.is_dir():
        return None
    # Pelo nome, e não por um nome exato: o arquivo que o Tesseract distribui
    # traz a versão no nome, e ela muda a cada atualização.
    encontrados = sorted(
        arquivo for arquivo in pasta.iterdir()
        if arquivo.is_file()
        and arquivo.suffix.lower() == ".exe"
        and arquivo.name.lower().startswith("tesseract")
    )
    # Sobrando um antigo na pasta, o último em ordem alfabética costuma ser o de
    # versão mais nova.
    return encontrados[-1] if encontrados else None


def abrir_instalador(instalador):
    """Abre o instalador como se a pessoa tivesse clicado duas vezes nele.

    É esse jeito de abrir que faz o Windows mostrar a confirmação de
    administrador, que a pessoa responde. Abrir por outro caminho faria o
    Windows recusar em silêncio, porque instalar em Program Files exige essa
    confirmação. Levanta OSError quando não abre - inclusive quando a pessoa
    responde "Não" na confirmação.
    """
    os.startfile(str(instalador))

"""O que a pessoa escolheu e o programa lembra de um uso para o outro.

Mora num arquivo próprio, o `preferencias.ini`, na pasta da instalação, ao lado
do `.env` (emenda de 28/10/2026 da spec 002, RN-38). O `.env` é da TI, com os
comentários e o jeito de gravar dela, e o programa só o lê; este arquivo é do
programa, e ele o reescreve inteiro sempre que precisa. Nesta máquina de
desenvolvimento, a pasta da instalação é a raiz do projeto, e o arquivo fica
fora do histórico.

Aqui só entra a escolha da pessoa - o motor de cada módulo, o tamanho da
janela. Nada do trabalho (documento, texto, pasta) é guardado (RN-40).

Lembrar nunca atrapalha usar (RN-39): o que não dá para ler vale como "nada
lembrado", e o que não dá para gravar fica valendo só até fechar o programa,
sem erro e sem aviso.
"""
import configparser
import os

import configuracao

NOME_DO_ARQUIVO = "preferencias.ini"

# Escrito no alto do arquivo a cada gravação, para quem o abrir no Bloco de
# Notas saber o que ele é e que pode apagá-lo sem medo.
CABECALHO = (
    "# Escolhas de quem usa o Anonimizador CAPCF nesta instalação, lembradas de\n"
    "# um uso para o outro. O programa escreve este arquivo sozinho. Apagado,\n"
    "# tudo volta ao padrão na próxima vez em que o programa abrir.\n\n"
)


def caminho():
    """Onde o arquivo mora: ao lado do `.env`, na pasta da instalação."""
    return configuracao.pasta_do_programa() / NOME_DO_ARQUIVO


def ler(secao, chave):
    """O valor lembrado, ou None quando não há nada lembrado que dê para ler.

    Vem em minúsculas e sem espaços em volta: quem editar o arquivo à mão e
    escrever "Tesseract" é entendido, em vez de ignorado calado (lente crítica
    da etapa 1).
    """
    valor = (_conteudo() or _vazio()).get(secao, chave, fallback=None)
    return valor.strip().lower() if valor is not None else None


def gravar(secao, chave, valor):
    """Lembra o valor para a próxima vez. Não dando para gravar, segue calado.

    O arquivo é escrito primeiro com outro nome, e só no fim toma o lugar do de
    verdade: se a máquina desligar no meio, o que já estava lembrado continua
    inteiro, em vez de sobrar um arquivo pela metade (RN-39).
    """
    conteudo = _conteudo()
    if conteudo is None:
        # O arquivo existe e não deu para lê-lo agora (um antivírus o
        # segurando, por exemplo). Gravar por cima apagaria as outras escolhas
        # lembradas; vale mais perder só esta (lente crítica da etapa 1).
        return
    if not conteudo.has_section(secao):
        conteudo.add_section(secao)
    conteudo.set(secao, chave, str(valor))
    destino = caminho()
    # Um nome provisório por programa aberto: com duas janelas do programa
    # gravando juntas, uma não escreve no provisório da outra (lente crítica
    # da etapa 1).
    provisorio = destino.with_name(f"{destino.name}.{os.getpid()}.gravando")
    try:
        with open(provisorio, "w", encoding="utf-8") as arquivo:
            arquivo.write(CABECALHO)
            conteudo.write(arquivo)
            # O disco grava o conteúdo antes da troca de nome. Sem isto, a troca
            # podia chegar ao disco antes do conteúdo, e uma queda de energia
            # deixava o arquivo vazio (lente crítica da etapa 1).
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(provisorio, destino)
    except OSError:
        # A pasta não aceitou: a escolha vale até fechar o programa, como era
        # antes de existir a lembrança. Perder a lembrança não estraga nada.
        try:
            provisorio.unlink(missing_ok=True)
        except OSError:
            pass


def _conteudo():
    """O que está lembrado; vazio, se o arquivo faltar ou estiver estragado;
    ou None, se ele existe e não deu para lê-lo agora.

    "Estragado" é o arquivo com outra codificação ou com linhas que não são de
    preferências: o programa abre no padrão, e a próxima gravação o refaz
    certo. "Não deu para ler agora" é outra coisa - o arquivo está lá, preso
    por outro programa -, e aí a gravação não pode passar por cima dele.
    """
    try:
        # "utf-8-sig" aceita também o arquivo salvo no Bloco de Notas como
        # "UTF-8 com BOM", que começa com uma marca invisível (lente crítica da
        # etapa 1).
        texto = caminho().read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return _vazio()
    except UnicodeDecodeError:
        return _vazio()
    except OSError:
        return None
    conteudo = _vazio()
    try:
        conteudo.read_string(texto)
    except configparser.Error:
        return _vazio()
    return conteudo


def _vazio():
    return configparser.ConfigParser(interpolation=None)

"""O único arquivo do programa que fala com a rede (RN-44 da spec 004).

Tudo o que sai para o LM Studio ou para o servidor interno passa por aqui, e é
por isso que os testes de guarda podem continuar barrando sinal de rede em todo
o resto. Ele só é carregado quando a pessoa liga a IA: desligada, o programa nem
o abre (RN-43). Não baixa nada, e não conhece nenhum endereço de fora: o único
escrito aqui é o da própria máquina, o do LM Studio.

Usa o que já vem no Python. Uma biblioteca seria mais uma coisa para empacotar,
e o `http.client` tem duas vantagens para este caso: não segue redirecionamento
sozinho (RN-23) e não passa por proxy nenhum configurado na máquina - o destino
é sempre o que a pessoa viu.
"""
import http.client
import ipaddress
import json
import socket
import ssl
import struct
import threading
import zlib
from base64 import b64encode
from dataclasses import dataclass
from urllib.parse import urlsplit

# Para abrir a conexão, pouco: quem está no ar responde logo, e a pessoa não
# fica olhando a tela por causa de um endereço errado. Para a resposta, muito: um
# modelo local num computador comum pode levar minutos.
SEGUNDOS_PARA_CONECTAR = 5
SEGUNDOS_PARA_LISTAR = 15
SEGUNDOS_PARA_O_TESTE = 180

# Perguntar à rede o número de um nome pode travar sem resposta, e isto acontece
# com a janela esperando.
SEGUNDOS_PARA_ACHAR_O_NUMERO = 3

# Ninguém responde um pedaço de texto com tanto, e sem teto um destino com defeito
# encheria a memória da máquina.
MAXIMO_DE_BYTES_NA_RESPOSTA = 16 * 1024 * 1024

# As frases da tela moram aqui: a de cifra precisa falar de `http://`, e isso não
# pode aparecer em nenhum outro arquivo do programa (testes de guarda).
SEM_CIFRA = ("Este endereço começa com http://: o texto e o token viajam sem "
             "cifra.")
ESTA_MAQUINA = "É esta máquina."
NAO_RESPONDEU = "O destino não respondeu."
DEMOROU = "O destino demorou demais para responder."
REDIRECIONOU = ("O destino tentou mandar o programa para outro endereço, e o "
                "programa não foi.")
TOKEN_RECUSADO = "O destino recusou o token."
CERTIFICADO_RECUSADO = ("O certificado de segurança deste endereço não foi "
                        "aceito. Veja com a TI.")
MODELO_FORA = "O modelo escolhido não respondeu. Veja se ele está carregado."
RESPOSTA_ESTRANHA = "O destino respondeu de um jeito que o programa não entende."
RESPOSTA_CORTADA = "A resposta do modelo foi cortada no meio, antes de terminar."


class FalhaDaIa(Exception):
    """Algo deu errado na conversa com o destino, com a frase pronta para a tela.

    A frase nunca traz o que o destino respondeu: um erro que repetisse o token
    ou o texto do documento acabaria na tela (RN-12).
    """

    para_a_tela = True


class PedidoCancelado(Exception):
    """A pessoa cancelou, ou o programa está fechando. Não é falha do destino."""

    e_cancelamento = True


class _NaoEncontrado(FalhaDaIa):
    """O destino não tem aquele endereço: é assim que se descobre o que ele sabe."""


class Cancelador:
    """Corta a espera por um pedido em andamento, de fora dele.

    Sem isto, cancelar ou fechar o programa teria de esperar a resposta do modelo,
    que pode levar minutos.
    """

    def __init__(self):
        self.cancelado = False

    def cancelar(self):
        self.cancelado = True


@dataclass(frozen=True)
class Modelo:
    """Um modelo que o destino oferece. None é "o destino não disse"."""

    nome: str
    le_imagem: bool | None = None
    carregado: bool | None = None
    bytes: int | None = None
    limite_de_contexto: int | None = None

    def descricao(self):
        partes = []
        if self.bytes:
            partes.append(f"{self.bytes / 1024 ** 3:.1f} GB".replace(".", ","))
        if self.carregado is True:
            partes.append("carregado")
        elif self.carregado is False:
            partes.append("não carregado")
        return f"{self.nome} ({', '.join(partes)})" if partes else self.nome


def base_do_lm_studio(porta):
    return f"http://127.0.0.1:{porta}"


def base_do_endereco(endereco):
    """O endereço como o programa o usa: com o começo, e sem o `/v1` do fim.

    Quem copia o endereço da tela de um servidor costuma trazer o `/v1` junto, e
    a conta dos caminhos daria `/v1/v1`.
    """
    base = endereco.strip()
    if "://" not in base:
        base = f"http://{base}"
    base = base.rstrip("/")
    if base.endswith("/v1"):
        base = base[:-3]
    return base


def listar_modelos(base, token=None, cancelador=None):
    """Os modelos que o destino oferece, ou None quando ele não sabe listar.

    Pergunta do mais novo para o mais antigo: a lista nova do LM Studio diz quais
    modelos leem imagem, a antiga diz quase isso, e a comum só traz os nomes.
    """
    for caminho, interpretar in (("/api/v1/models", _modelos_da_lista_nova),
                                 ("/api/v0/models", _modelos_da_lista_antiga),
                                 ("/v1/models", _modelos_da_lista_comum)):
        try:
            resposta = _pedir_json(base, "GET", caminho, None, token,
                                   SEGUNDOS_PARA_LISTAR, cancelador)
            return interpretar(resposta)
        except (_NaoEncontrado, _RespostaInvalida):
            continue
    return None


def conversar(base, token, modelo, mensagens, segundos, cancelador=None):
    """Manda as mensagens e devolve o texto da resposta.

    Pelo caminho em que cada pedido vale sozinho, sem pedir ao destino que guarde
    a conversa (RN-35): o texto vai com os CPFs inteiros, e não há por que ele
    ficar registrado lá.
    """
    corpo = {"model": modelo, "messages": mensagens, "temperature": 0, "stream": False,
             "reasoning_effort": "none"}
    # Sem pensar antes de responder. Medido com um modelo de verdade (01/11/2026): pensando,
    # ele levava quase 3 minutos num pedaço e esgotava a memória sem responder nada; sem
    # pensar, 4 segundos. Quem não conhece o pedido recusa, e aí ele vai sem isso.
    try:
        try:
            resposta = _pedir_json(base, "POST", "/v1/chat/completions", corpo, token,
                                   segundos, cancelador)
        except _NaoEncontrado:
            del corpo["reasoning_effort"]
            resposta = _pedir_json(base, "POST", "/v1/chat/completions", corpo, token,
                                   segundos, cancelador)
    except _RespostaInvalida as problema:
        raise FalhaDaIa(RESPOSTA_ESTRANHA) from problema
    except _NaoEncontrado as problema:
        raise FalhaDaIa(str(problema)) from problema
    try:
        texto = resposta["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as problema:
        raise FalhaDaIa(RESPOSTA_ESTRANHA) from problema
    if not isinstance(texto, str):
        raise FalhaDaIa(RESPOSTA_ESTRANHA)
    # Cortada, ela parece uma resposta inteira: o resto da página, com os CPFs que
    # houver nele, sumiria sem nada acusar.
    if resposta["choices"][0].get("finish_reason") == "length":
        raise FalhaDaIa(RESPOSTA_CORTADA)
    return texto


def testar_modelo(base, token, modelo, imagem_em_base64=None, cancelador=None):
    """Confere que aquele modelo responde agora, sem nada do documento (RN-7)."""
    frase = "Responda apenas a palavra ok."
    if imagem_em_base64 is None:
        conteudo = frase
    else:
        conteudo = [
            {"type": "text", "text": frase},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{imagem_em_base64}"}},
        ]
    texto = conversar(base, token, modelo, [{"role": "user", "content": conteudo}],
                      SEGUNDOS_PARA_O_TESTE, cancelador)
    if not texto.strip():
        raise FalhaDaIa(MODELO_FORA)


def imagem_de_teste():
    """Um quadrado branco inventado, em PNG: o teste do motor nunca leva documento
    (RN-7). Feito na mão para não carregar nada de imagem só por causa dele."""
    largura = altura = 64
    linhas = (b"\x00" + b"\xff" * largura) * altura

    def pedaco(tipo, dados):
        verificacao = zlib.crc32(tipo + dados) & 0xffffffff
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", verificacao)

    png = (b"\x89PNG\r\n\x1a\n"
           + pedaco(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 0, 0, 0, 0))
           + pedaco(b"IDAT", zlib.compress(linhas))
           + pedaco(b"IEND", b""))
    return b64encode(png).decode("ascii")


class _RespostaInvalida(Exception):
    pass


def _pedir_json(base, metodo, caminho, corpo, token, segundos, cancelador):
    bytes_da_resposta = _pedir(base, metodo, caminho, corpo, token, segundos, cancelador)
    try:
        return json.loads(bytes_da_resposta.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as problema:
        raise _RespostaInvalida from problema


def _pedir(base, metodo, caminho, corpo, token, segundos, cancelador):
    if cancelador is None:
        return _pedir_agora(base, metodo, caminho, corpo, token, segundos, None)
    # Numa linha à parte, com quem pediu olhando de fora: no Windows, fechar a
    # conexão não acorda quem está esperando a resposta, e cancelar levaria o tempo
    # todo que o modelo levasse. Cancelado, quem pediu vai embora, e a linha de dentro
    # termina sozinha quando o destino responder, sem ninguém para ouvir.
    saida = {}
    pronto = threading.Event()

    def pedir():
        try:
            saida["resposta"] = _pedir_agora(base, metodo, caminho, corpo, token,
                                             segundos, cancelador)
        except BaseException as problema:
            saida["problema"] = problema
        pronto.set()

    threading.Thread(target=pedir, daemon=True).start()
    while not pronto.wait(0.1):
        if cancelador.cancelado:
            raise PedidoCancelado
    if "problema" in saida:
        raise saida["problema"]
    return saida["resposta"]


def _pedir_agora(base, metodo, caminho, corpo, token, segundos, cancelador):
    partes = urlsplit(base)
    classe = (http.client.HTTPSConnection if partes.scheme == "https"
              else http.client.HTTPConnection)
    conexao = classe(partes.hostname, partes.port, timeout=SEGUNDOS_PARA_CONECTAR)
    _se_cancelado(cancelador)
    cabecalhos = {"Accept": "application/json"}
    dados = None
    if corpo is not None:
        dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        cabecalhos["Content-Type"] = "application/json; charset=utf-8"
    if token:
        cabecalhos["Authorization"] = f"Bearer {token}"
    try:
        conexao.connect()
        conexao.sock.settimeout(segundos)
        conexao.request(metodo, partes.path.rstrip("/") + caminho, body=dados,
                        headers=cabecalhos)
        resposta = conexao.getresponse()
        estado = resposta.status
        conteudo = resposta.read(MAXIMO_DE_BYTES_NA_RESPOSTA + 1)
    except TimeoutError as problema:
        _se_cancelado(cancelador)
        raise FalhaDaIa(DEMOROU) from problema
    except ssl.SSLCertVerificationError as problema:
        raise FalhaDaIa(CERTIFICADO_RECUSADO) from problema
    except (OSError, http.client.HTTPException, ValueError) as problema:
        _se_cancelado(cancelador)
        raise FalhaDaIa(NAO_RESPONDEU) from problema
    finally:
        conexao.close()
    _se_cancelado(cancelador)

    if 300 <= estado < 400:
        raise FalhaDaIa(REDIRECIONOU)
    if estado in (401, 403):
        raise FalhaDaIa(TOKEN_RECUSADO)
    if estado in (400, 404, 405, 422):
        # O número do erro vai junto: a frase serve a mais de uma causa, como um modelo
        # não carregado ou um pedaço que não coube, e ele é o que permite distinguir.
        raise _NaoEncontrado(f"{MODELO_FORA} (erro {estado})")
    if estado >= 400:
        raise FalhaDaIa(f"O destino respondeu com o erro {estado}.")
    if len(conteudo) > MAXIMO_DE_BYTES_NA_RESPOSTA:
        raise FalhaDaIa(RESPOSTA_ESTRANHA)
    return conteudo


def _se_cancelado(cancelador):
    if cancelador is not None and cancelador.cancelado:
        raise PedidoCancelado


def _modelos_da_lista_nova(resposta):
    try:
        itens = resposta["models"]
        modelos = []
        for item in itens:
            # Modelo de embedding não conversa, e escolhê-lo só daria erro depois.
            if item.get("type", "llm") not in ("llm", "vlm") or not _conversa(item["key"]):
                continue
            capacidades = item.get("capabilities") or {}
            modelos.append(Modelo(
                nome=_nome_limpo(item["key"]),
                le_imagem=capacidades.get("vision"),
                carregado=bool(item.get("loaded_instances")),
                bytes=item.get("size_bytes"),
                limite_de_contexto=item.get("max_context_length"),
            ))
    except (KeyError, TypeError, AttributeError) as problema:
        raise _RespostaInvalida from problema
    return modelos


def _modelos_da_lista_antiga(resposta):
    try:
        modelos = []
        for item in resposta["data"]:
            tipo = item.get("type", "llm")
            if tipo not in ("llm", "vlm") or not _conversa(item["id"]):
                continue
            modelos.append(Modelo(
                nome=_nome_limpo(item["id"]),
                le_imagem=tipo == "vlm",
                carregado=item.get("state") == "loaded",
                limite_de_contexto=item.get("max_context_length"),
            ))
    except (KeyError, TypeError, AttributeError) as problema:
        raise _RespostaInvalida from problema
    return modelos


def _modelos_da_lista_comum(resposta):
    try:
        return [Modelo(nome=_nome_limpo(item["id"])) for item in resposta["data"]
                if _conversa(item["id"])]
    except (KeyError, TypeError) as problema:
        raise _RespostaInvalida from problema


def _conversa(nome):
    """Embedding não conversa, e o "mmproj" é só um pedaço de um modelo de imagem, que o
    LM Studio lista à parte como se fosse um modelo: escolhê-los só daria erro depois."""
    nome = str(nome).lower()
    return "embed" not in nome and "mmproj" not in nome


def _nome_limpo(nome):
    """O nome em uma linha só: ele vai para o `preferencias.ini`, e uma quebra de
    linha vinda do destino estragaria o arquivo."""
    return " ".join(str(nome).split())


# ---------------------------------------------------------------- o endereço


@dataclass(frozen=True)
class Avaliacao:
    """O que o programa acha do endereço digitado."""

    valido: bool
    reconhecido: bool = False
    sem_cifra: bool = False
    # A resposta à pergunta "por que este endereço passou sem aviso?".
    por_que: str = ""
    problema: str = ""


def avaliar_endereco(endereco, locais=()):
    """Diz se o endereço é reconhecido como de dentro (RN-17 da spec 004).

    Reconhecer não é bloquear: o que não se reconhece abre o aviso, e quem decide
    é a pessoa, porque o endereço de cada instituição varia (RN-16).
    """
    try:
        partes = urlsplit(base_do_endereco(endereco))
        host = (partes.hostname or "").rstrip(".").lower()
        porta = partes.port
    except ValueError:
        return Avaliacao(False, problema="Este endereço não está escrito direito.")
    if partes.scheme not in ("http", "https") or not host:
        return Avaliacao(False, problema="Este endereço não está escrito direito.")
    if partes.username or partes.password:
        # Senha escrita no endereço iria parar no arquivo de preferências, e um
        # endereço assim engana quem lê ("fulano@" antes do destino de verdade).
        return Avaliacao(False, problema="O endereço não pode ter usuário ou senha. "
                                         "O token vai no campo dele.")
    sem_cifra = partes.scheme == "http"
    com_porta = f"{host}:{porta}" if porta else host
    for local in locais:
        local = local.strip().lower().rstrip("/")
        if "://" in local:
            local = local.split("://", 1)[1]
        if local and (local in (host, com_porta)
                      or (local.startswith(".") and host.endswith(local))):
            return Avaliacao(True, True, sem_cifra,
                             "Está na lista de endereços locais desta instalação.")
    if host == "localhost":
        return Avaliacao(True, True, sem_cifra, ESTA_MAQUINA)
    if host == "ufsc.br" or host.endswith(".ufsc.br"):
        return Avaliacao(True, True, sem_cifra, "É um nome da UFSC.")
    numeros = _numeros_do_nome(host)
    if numeros and all(_e_desta_maquina(n) for n in numeros):
        return Avaliacao(True, True, sem_cifra, ESTA_MAQUINA)
    if numeros and all(_e_interno(n) for n in numeros):
        return Avaliacao(True, True, sem_cifra,
                         "Reconhecido como rede interna. Isso não prova que é a UFSC: "
                         "na rede de casa, um número assim também aparece.")
    return Avaliacao(True, False, sem_cifra)


def endereco_desta_maquina(endereco):
    """A lista de endereços locais fica de fora de propósito: ela diz em quem a instalação
    confia, e não que o documento fica neste computador."""
    return avaliar_endereco(endereco).por_que == ESTA_MAQUINA


def _numeros_do_nome(host):
    """Os números daquele endereço: ele mesmo, ou o que a rede responder."""
    try:
        return [ipaddress.ip_address(host.strip("[]"))]
    except ValueError:
        pass
    achados = []

    def perguntar():
        try:
            for item in socket.getaddrinfo(host, None):
                achados.append(ipaddress.ip_address(item[4][0].split("%")[0]))
        except (OSError, ValueError, UnicodeError):
            pass

    # À parte, porque a pergunta não tem tempo limite próprio: sem resposta, o nome
    # conta como não reconhecido, e quem decide é a pessoa, pelo aviso.
    pergunta = threading.Thread(target=perguntar, daemon=True)
    pergunta.start()
    pergunta.join(SEGUNDOS_PARA_ACHAR_O_NUMERO)
    return list(achados) if not pergunta.is_alive() else []


def _sem_embrulho(numero):
    return getattr(numero, "ipv4_mapped", None) or numero


def _e_desta_maquina(numero):
    return _sem_embrulho(numero).is_loopback


def _e_interno(numero):
    numero = _sem_embrulho(numero)
    return numero.is_private and not numero.is_unspecified and not numero.is_multicast

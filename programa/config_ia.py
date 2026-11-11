"""O que está configurado sobre a IA, lembrado no `preferencias.ini` (RN-38 da spec 002).

Aqui não há token: ele mora no `.env`, e nunca neste arquivo (RN-10 da spec 004).
Nada aqui fala com a rede, e nada do trabalho é guardado: só a escolha da pessoa.
"""
import configuracao
import preferencias

LM_STUDIO = "lm_studio"
SERVIDOR = "servidor"
NOME_NA_TELA = {LM_STUDIO: "LM Studio", SERVIDOR: "Servidor de IA Interno"}

# A porta de costume do LM Studio. É a única coisa que já vem preenchida, e não
# aponta para fora daqui (premissa do mapa 08, I-2).
PORTA_PADRAO = 1234

INICIO_NO_CLIQUE = "clique"
INICIO_AO_ABRIR = "abrir"

_BLOCO = "ia"
_BLOCO_DO_DESTINO = {LM_STUDIO: "ia_lm_studio", SERVIDOR: "ia_servidor"}
_SIM = "sim"
_NAO = "não"

# O nome das duas linhas do `.env`. A do token é a única que o programa grava.
ENV_TOKEN = "IA_SERVIDOR_TOKEN"
ENV_LOCAIS = "IA_ENDERECOS_LOCAIS"


def _geral():
    return preferencias.ler_bloco_exato(_BLOCO)


def _gravar_geral(**valores):
    preferencias.gravar_juntos(_BLOCO, valores)


# ---------------------------------------------------------------- os destinos


def do_destino(nome):
    """O que está guardado de um destino, mesmo com ele desligado (RN-4)."""
    return preferencias.ler_bloco_exato(_BLOCO_DO_DESTINO[nome])


def guardar_do_destino(nome, **valores):
    preferencias.gravar_juntos(_BLOCO_DO_DESTINO[nome], valores)


def base_do_destino(nome):
    """O começo do endereço de um destino. Quem sabe escrevê-lo é o arquivo da rede,
    carregado só aqui, na hora de usar."""
    import rede_da_ia
    if nome == LM_STUDIO:
        return rede_da_ia.base_do_endereco(endereco_do_lm_studio())
    return rede_da_ia.base_do_endereco(endereco_do_servidor())


def endereco_do_lm_studio():
    """O endereço colado pela pessoa, como o LM Studio o mostra. Sem nenhum guardado, o
    de costume, nesta máquina."""
    guardado = do_destino(LM_STUDIO).get("endereco")
    if guardado:
        return guardado
    import rede_da_ia
    return rede_da_ia.base_do_lm_studio(porta_do_lm_studio())


def lm_studio_nesta_maquina():
    """O endereço colado pode ser de outro computador, e aí o texto sai deste, com os CPFs
    inteiros: nenhuma tela pode dizer "nesta máquina" sem perguntar aqui."""
    import rede_da_ia
    return rede_da_ia.endereco_desta_maquina(endereco_do_lm_studio())


def porta_do_lm_studio():
    """Nenhuma tela grava mais a porta, desde que se cola o endereço inteiro (RN-59). Ela
    sobra para compor o endereço de costume, e para quem ainda a tem guardada no arquivo."""
    try:
        porta = int(do_destino(LM_STUDIO).get("porta", PORTA_PADRAO))
    except ValueError:
        return PORTA_PADRAO
    return porta if 0 < porta < 65536 else PORTA_PADRAO


def endereco_do_servidor():
    return do_destino(SERVIDOR).get("endereco", "")


def modelo_da_revisora(nome):
    return do_destino(nome).get("modelo_revisora", "")


def modelo_do_motor(nome):
    return do_destino(nome).get("modelo_motor", "")


def destino_ligado():
    """O destino em uso, ou None. Valor estranho escrito à mão conta como nenhum."""
    destino = _geral().get("destino")
    return destino if destino in _BLOCO_DO_DESTINO else None


def ligar_destino(nome):
    _gravar_geral(destino=nome)


def desligar_destino():
    """O switch geral desliga junto, e os de baixo ficam como estavam (R-19): ao
    religar, tudo volta."""
    if geral_ligada():
        _gravar_geral(destino="", geral=_NAO, guardado_pelo_destino=_SIM)
    else:
        _gravar_geral(destino="")


def marcar_testado(nome, testado):
    guardar_do_destino(nome, testado=_SIM if testado else _NAO)


def testado(nome):
    return do_destino(nome).get("testado") == _SIM


def destino_configurado():
    """Um destino ligado, com modelo e com um teste que passou (RN-6)."""
    nome = destino_ligado()
    return bool(nome and modelo_da_revisora(nome) and testado(nome))


# -------------------------------------------------------------- os três switches


def geral_ligada():
    return _geral().get("geral") == _SIM


def ligar_geral():
    """Ao ligar, a revisora liga e o motor fica desligado (RN-24) - a não ser que
    quem desligou tenha sido o destino: aí tudo volta como estava (R-19)."""
    if _geral().get("guardado_pelo_destino") == _SIM:
        _gravar_geral(geral=_SIM, guardado_pelo_destino=_NAO)
    else:
        _gravar_geral(geral=_SIM, revisora=_SIM, motor=_NAO)


def desligada_pelo_destino():
    """Quem desligou a IA foi o destino, e a tela precisa dizer isso?"""
    return _geral().get("guardado_pelo_destino") == _SIM and not geral_ligada()


def desligar_geral():
    _gravar_geral(geral=_NAO, guardado_pelo_destino=_NAO)


def revisora_marcada():
    return _geral().get("revisora") == _SIM


def marcar_revisora(ligada):
    _gravar_geral(revisora=_SIM if ligada else _NAO)


def motor_marcado():
    return _geral().get("motor") == _SIM


def marcar_motor(ligado):
    _gravar_geral(motor=_SIM if ligado else _NAO)


def inicio_da_revisao():
    inicio = _geral().get("inicio")
    return inicio if inicio == INICIO_AO_ABRIR else INICIO_NO_CLIQUE


def escolher_inicio(inicio):
    _gravar_geral(inicio=inicio)


def revisora_ativa():
    """A revisora pode rodar agora?"""
    return geral_ligada() and destino_configurado() and revisora_marcada()


def motor_ligado():
    """A chave do motor está valendo? Ainda pode faltar o modelo."""
    return geral_ligada() and destino_configurado() and motor_marcado()


def motor_ativo():
    """A IA pode ler agora? Só com a chave, um modelo e um teste com imagem."""
    nome = destino_ligado()
    return bool(motor_ligado() and modelo_do_motor(nome)
                and do_destino(nome).get("motor_testado") == _SIM)


def marcar_motor_testado(nome, testado_agora):
    guardar_do_destino(nome, motor_testado=_SIM if testado_agora else _NAO)


# -------------------------------------------------------------------- o .env


def token_salvo():
    return bool(configuracao.valor_do_env(ENV_TOKEN))


def token_do_destino(nome):
    """O token de quem pede: o LM Studio não tem (premissa do mapa 08, I-1)."""
    return configuracao.valor_do_env(ENV_TOKEN) if nome == SERVIDOR else None


def salvar_token(token):
    """Grava o token. Devolve False quando o `.env` não aceitou, e aí ele não fica
    guardado em lugar nenhum (RN-13)."""
    return configuracao.gravar_no_env(ENV_TOKEN, token)


def apagar_token():
    return configuracao.gravar_no_env(ENV_TOKEN, "")


def enderecos_locais():
    """Os endereços que a TI deixou sem aviso, separados por vírgula ou espaço."""
    linha = configuracao.valor_do_env(ENV_LOCAIS) or ""
    return [item for item in linha.replace(";", ",").replace(" ", ",").split(",") if item]

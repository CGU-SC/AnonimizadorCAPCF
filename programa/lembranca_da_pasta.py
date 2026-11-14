"""A pasta do último arquivo aberto, lembrada de um uso para o outro (RN-43 da
spec 002, emenda de 14/11/2026).

Pedido da solicitante no teste da entrega da 0.2.0: o "Escolher arquivo…"
abria sempre na pasta da instalação, e cada documento pedia o caminho inteiro
de novo. A pasta é uma só para os dois módulos, porque o `.md` que sai do Gerar
OCR costuma ser aberto em seguida no Anonimizar, no mesmo lugar.

Fica guardada só a pasta, nunca o nome do arquivo: a pasta diz onde os
documentos moram, e não o que eles têm. Foi a única exceção aberta na RN-40,
que continua proibindo guardar documento, texto, achado e histórico.
"""
import os
import threading
from pathlib import Path

import preferencias

BLOCO = "arquivos"
CHAVE = "pasta"


def pasta_inicial():
    """Onde a janela de escolher arquivo deve abrir, ou "" para o jeito de sempre.

    A pasta que sumiu (o pendrive tirado, a rede fora) vale como nada lembrado,
    sem aviso: a janela abre como antes de existir a lembrança (RN-39).
    """
    # Lida sem passar para minúsculas: o caminho é mostrado à pessoa na janela
    # do Windows, e "Prestações" virando "prestações" pareceria outra pasta.
    pasta = preferencias.ler_bloco_exato(BLOCO).get(CHAVE)
    if pasta and _existe_a_tempo(pasta):
        return pasta
    return ""


# Quanto se espera pela resposta do disco antes de desistir da pasta lembrada.
# Disco da máquina e rede no ar respondem num instante; 2 segundos são uma
# demora que se nota, mas que não parece programa travado.
SEGUNDOS_PARA_CONFERIR = 2


def _existe_a_tempo(pasta):
    """Se a pasta existe, perguntado numa linha à parte e com prazo.

    Pasta de rede com a rede fora faz o Windows esperar o servidor por 20 a 60
    segundos antes de responder que ela não existe, e perguntado direto, isso
    congelava a janela no clique em "Escolher arquivo…" (lente crítica da
    funcionalidade 11). Sem resposta no prazo, vale como nada lembrado.
    """
    resposta = []
    # "daemon": se o servidor nunca responder, a linha esquecida não impede o
    # programa de fechar.
    linha = threading.Thread(
        target=lambda: resposta.append(os.path.isdir(pasta)), daemon=True)
    linha.start()
    linha.join(SEGUNDOS_PARA_CONFERIR)
    return bool(resposta) and resposta[0]


def lembrar(caminho_do_arquivo):
    """Guarda a pasta do arquivo que a pessoa acabou de escolher ou arrastar."""
    pasta = str(Path(caminho_do_arquivo).resolve().parent)
    # Abrir vários documentos da mesma pasta não reescreve o arquivo a cada um:
    # menos gravação, menos chance de esbarrar num antivírus segurando o arquivo.
    if preferencias.ler_bloco_exato(BLOCO).get(CHAVE) == pasta:
        return
    preferencias.gravar(BLOCO, CHAVE, pasta)

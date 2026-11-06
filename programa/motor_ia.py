"""A IA local lendo uma página, como motor (RN-38 a RN-42 da spec 004).

A frente secundária da funcionalidade: até a criação do programa, os modelos locais
eram muito inferiores ao PaddleOCR e ao Tesseract na leitura, e por isso ela fica
atrás de uma chave, com ressalva. Aqui o texto é dela, e a conferência continua
obrigatória, como em todo OCR.

A página vai como imagem, com os CPFs inteiros: não há como mascarar o que ninguém
leu ainda.
"""
import io
import re
from base64 import b64encode

import config_ia

# Uma página a 300 pontos por polegada tem mais de 3 mil pixels de altura, e os modelos
# locais reduzem a imagem de qualquer jeito. Mandar menor deixa o pedido bem mais leve.
MAIOR_LADO_EM_PIXELS = 1600

# Um modelo de imagem num computador comum pode levar minutos por página.
SEGUNDOS_POR_PAGINA = 300

INSTRUCAO = (
    "Transcreva todo o texto desta página de documento, em português, exatamente como "
    "está escrito, sem corrigir nem comentar. Mantenha as quebras de linha e, nas "
    "tabelas, uma linha do texto para cada linha da tabela. Responda só com o texto."
)


class IaIndisponivel(Exception):
    """A chave foi desligada, ou o destino saiu, com a leitura já pedida."""


class LeituraInterrompida(Exception):
    """A pessoa cancelou, ou o programa está fechando."""


def novo_cancelador():
    """Corta a espera pela página em andamento: um modelo pode levar minutos nela."""
    import rede_da_ia
    return rede_da_ia.Cancelador()


def preparar(cancelador=None):
    """A leitura de um documento, com o destino e o modelo fixados agora.

    Lidos a cada página, trocar o destino nas Configurações no meio da leitura mandaria
    as páginas seguintes, com os CPFs inteiros, para outro lugar, sem passar pelo aviso
    de endereço (RN-52). E um por leitura, porque cada módulo pode ter a sua rodando.
    """
    if not config_ia.motor_ativo():
        raise IaIndisponivel(
            "A IA local não está disponível: confira as Configurações.")
    nome = config_ia.destino_ligado()
    return _Leitura(config_ia.base_do_destino(nome), config_ia.token_do_destino(nome),
                    config_ia.modelo_do_motor(nome), cancelador)


class _Leitura:
    def __init__(self, base, token, modelo, cancelador):
        self._base, self._token, self._modelo = base, token, modelo
        self._cancelador = cancelador

    def ler(self, imagem):
        """O texto que a IA leu na imagem de uma página."""
        import rede_da_ia
        mensagens = [{"role": "user", "content": [
            {"type": "text", "text": INSTRUCAO},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{_em_base64(imagem)}"}},
        ]}]
        try:
            resposta = rede_da_ia.conversar(self._base, self._token, self._modelo, mensagens,
                                            SEGUNDOS_POR_PAGINA, self._cancelador)
        except rede_da_ia.PedidoCancelado as parada:
            raise LeituraInterrompida from parada
        # O raciocínio de alguns modelos não é o documento, e iria parar no arquivo.
        return re.sub(r"<think>.*?</think>\s*", "", resposta, flags=re.DOTALL)


def _em_base64(imagem):
    imagem = imagem.copy()
    imagem.thumbnail((MAIOR_LADO_EM_PIXELS, MAIOR_LADO_EM_PIXELS))
    saida = io.BytesIO()
    imagem.save(saida, format="PNG")
    return b64encode(saida.getvalue()).decode("ascii")

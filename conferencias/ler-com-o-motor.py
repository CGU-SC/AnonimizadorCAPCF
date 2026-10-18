r"""Lê um PDF com um dos motores da medição e grava o que leu, página a página.

Faz parte da conferência 02 (funcionalidade 7): os motores leem as mesmas
páginas, e o gerar-02 compara cada leitura com o gabarito. Cada motor roda no
ambiente dele, porque o PaddleOCR e o RapidOCR trazem versões diferentes da
mesma biblioteca de imagem, que não convivem:

    .\.venv\Scripts\python.exe           conferencias\ler-com-o-motor.py tesseract  <pdf> <saida.json>
    .\.venv-paddleocr\Scripts\python.exe conferencias\ler-com-o-motor.py paddleocr  <pdf> <saida.json> --sem-rede
    .\.venv-rapidocr\Scripts\python.exe  conferencias\ler-com-o-motor.py rapidocr   <pdf> <saida.json> --sem-rede

O texto de cada motor passa pela mesma remontagem de linhas que o programa usa
(`programa/disposicao.py`), para a comparação medir a leitura, e não a
arrumação. O Tesseract é chamado pelo próprio `programa/leitura.py`: é ele,
exatamente como o programa o usa hoje, que está sendo comparado.

Com --sem-rede, qualquer tentativa de abrir conexão pelo Python quebra na hora
e fica anotada no resultado. É o sinal de que o motor lê sem internet depois de
os modelos estarem na máquina (RN-20 da spec 002) - sinal, e não prova completa:
veja o fechar_a_rede.

A saída de documento real vai para dados-reais/, nunca para esta pasta: ela
tem o texto lido, e texto de documento real não entra no histórico.
"""
import importlib.util
import io
import json
import os
import socket
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PROGRAMA = RAIZ / "programa"

# Os modelos baixados na medição moram dentro do projeto, fora do histórico. Por
# padrão o PaddleOCR os guardaria na pasta pessoal, onde a cerca do agente não
# deixa gravar - e onde ninguém lembraria de procurar depois.
PASTA_DOS_MODELOS = RAIZ / ".modelos-medicao"

DENSIDADE = 300  # a mesma do programa (leitura.PONTOS_POR_POLEGADA)

tentativas_de_rede = []


def fechar_a_rede():
    """Faz toda tentativa de conexão do Python quebrar, e anota para onde ia.

    Fechar no próprio Python, e não só por variável de ambiente, pega toda
    biblioteca escrita em Python, inclusive as que ignoram a configuração de
    proxy. O que a parte compilada de uma biblioteca fizer passa por fora: por
    isso a página diz "pela parte em Python", e a prova completa - a máquina sem
    rede nenhuma - fica para a construção (lente crítica, 16/10/2026).
    """
    def recusar(destino):
        tentativas_de_rede.append(str(destino))
        raise OSError(f"rede fechada na medição (tentou {destino})")

    socket.socket.connect = lambda self, destino: recusar(destino)
    socket.socket.connect_ex = lambda self, destino: recusar(destino)
    socket.getaddrinfo = lambda host, *resto, **nomeados: recusar(host)
    os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
    os.environ["HF_HUB_OFFLINE"] = "1"


def _carregar_disposicao():
    """Traz a remontagem de linhas do programa sem pôr a pasta dele no caminho.

    A pasta do programa tem arquivos com nomes comuns (motor, leitura,
    documento), que poderiam esconder módulos de mesmo nome das bibliotecas dos
    motores.
    """
    especificacao = importlib.util.spec_from_file_location(
        "disposicao", PROGRAMA / "disposicao.py")
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def _imagem(pagina):
    from PIL import Image
    pixels = pagina.get_pixmap(dpi=DENSIDADE)
    return Image.open(io.BytesIO(pixels.tobytes("png"))).convert("RGB")


def _remontar(caixas, disposicao):
    """Caixas `(x0, y0, x1, y1, texto)` viram linhas, como no programa."""
    return "\n".join(disposicao.montar(disposicao.agrupar_por_altura(caixas)))


def _caixa_do_poligono(pontos, texto):
    xs = [float(p[0]) for p in pontos]
    ys = [float(p[1]) for p in pontos]
    return (min(xs), min(ys), max(xs), max(ys), texto)


class Tesseract:
    nome = "Tesseract"

    def __init__(self):
        sys.path.insert(0, str(PROGRAMA))
        import leitura
        import pytesseract
        self._leitura = leitura
        leitura.preparar_motor()
        self.versao = str(pytesseract.get_tesseract_version())
        self.configuracao = "o programa de hoje: português, endireitar pelo detector"

    def ler(self, pagina):
        return self._leitura._ler_pagina(pagina)


class PaddleOcrOficial:
    nome = "PaddleOCR oficial"

    def __init__(self):
        os.environ["PADDLE_PDX_CACHE_HOME"] = str(PASTA_DOS_MODELOS / "paddlex")
        import numpy
        import paddleocr
        self._numpy = numpy
        self._disposicao = _carregar_disposicao()
        # Com a aceleração de processador ligada, que é o padrão, o PaddlePaddle
        # 3.3 estoura em toda página nesta máquina (NotImplementedError dentro
        # do oneDNN, defeito conhecido dele no Windows). Desligada, ele lê.
        self._motor = paddleocr.PaddleOCR(lang="pt", enable_mkldnn=False)
        self.versao = paddleocr.__version__
        self.configuracao = ("lang=pt, aceleração oneDNN desligada (no padrão, "
                             "estoura em toda página)")

    def ler(self, pagina):
        resultado = self._motor.predict(self._numpy.array(_imagem(pagina)))[0]
        caixas = [(float(x0), float(y0), float(x1), float(y1), texto)
                  for (x0, y0, x1, y1), texto
                  in zip(resultado["rec_boxes"], resultado["rec_texts"])]
        return _remontar(caixas, self._disposicao)


class RapidOcr:
    nome = "RapidOCR"

    def __init__(self, tamanho=None):
        import numpy
        import rapidocr
        from rapidocr import ModelType, RapidOCR
        self._numpy = numpy
        self._disposicao = _carregar_disposicao()
        parametros = {}
        if tamanho == "medio":
            parametros = {"Det.model_type": ModelType.MEDIUM,
                          "Rec.model_type": ModelType.MEDIUM}
            self.nome = "RapidOCR, modelo médio"
        self._motor = RapidOCR(params=parametros)
        self.versao = rapidocr.__version__ if hasattr(rapidocr, "__version__") else "?"
        self.configuracao = ("PP-OCRv6 médio" if tamanho == "medio"
                             else "padrão: PP-OCRv6 pequeno, que vem no pacote")

    def ler(self, pagina):
        resultado = self._motor(self._numpy.array(_imagem(pagina)))
        if resultado.txts is None:
            return ""
        caixas = [_caixa_do_poligono(pontos, texto)
                  for pontos, texto in zip(resultado.boxes, resultado.txts)]
        return _remontar(caixas, self._disposicao)


MOTORES = {
    "tesseract": Tesseract,
    "paddleocr": PaddleOcrOficial,
    "rapidocr": RapidOcr,
    "rapidocr-medio": lambda: RapidOcr(tamanho="medio"),
}


def main():
    motor, pdf, saida = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    sem_rede = "--sem-rede" in sys.argv
    if sem_rede:
        fechar_a_rede()

    import pymupdf

    comeco = time.perf_counter()
    leitor = MOTORES[motor]()
    preparar = time.perf_counter() - comeco

    paginas = []
    documento = pymupdf.open(pdf)
    for indice in range(documento.page_count):
        comeco = time.perf_counter()
        try:
            texto, falha = leitor.ler(documento[indice]), None
        except Exception as problema:
            texto, falha = "", f"{type(problema).__name__}: {problema}"
        paginas.append({"texto": texto, "segundos": time.perf_counter() - comeco,
                        "falha": falha})
        print(f"{leitor.nome}: página {indice + 1} de {documento.page_count}",
              file=sys.stderr)

    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps({
        "motor": leitor.nome,
        "versao": leitor.versao,
        "configuracao": leitor.configuracao,
        "documento": pdf.name,
        "sem_rede": sem_rede,
        "tentativas_de_rede": tentativas_de_rede,
        "segundos_para_preparar": preparar,
        "paginas": paginas,
    }, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

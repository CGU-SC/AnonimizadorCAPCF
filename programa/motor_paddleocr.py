"""O PaddleOCR: os modelos que leem a página, e a conferência de que estão aqui.

Os modelos são os PP-OCRv6 pequenos do PaddleOCR, rodados pelo RapidOCR - a
escolha técnica de 16/10/2026, depois da medição da conferência 02: o PaddleOCR
oficial não leu do jeito normal no Windows e levava quase um minuto por página;
este leva um ou dois segundos, e os modelos vêm dentro do próprio pacote.

Nada aqui sai da máquina (RN-20 e RN-27 da spec 002). O RapidOCR sabe baixar
modelo da internet quando não acha um - por isso o programa sempre diz a ele
onde está cada arquivo. Com o caminho dito, faltando o arquivo ele para com
erro, em vez de ir buscar; e quem confere antes, para a tela poder avisar, é a
função `presente`.
"""
from pathlib import Path

from disposicao import agrupar_por_altura, montar

# Os três modelos que vêm no pacote do RapidOCR: o que acha onde há texto na
# página, o que vira a linha de cabeça para baixo (ligado só sem o detector do
# Tesseract, ver `preparar`),
# e o que lê. Os nomes são os
# da versão 3.10.0, fixada no requirements.txt - trocar a versão pede conferir
# estes nomes de novo.
MODELO_QUE_ACHA = "PP-OCRv6_det_small.onnx"
MODELO_QUE_VIRA = "ch_ppocr_mobile_v2.0_cls_mobile.onnx"
MODELO_QUE_LE = "PP-OCRv6_rec_small.onnx"
MODELOS = (MODELO_QUE_ACHA, MODELO_QUE_VIRA, MODELO_QUE_LE)

# O motor é carregado uma vez e reaproveitado: carregar leva perto de meio
# segundo, e fazer isso a cada página somaria minutos num documento grande. São
# dois, um para cada jeito de ler (ver `preparar`), guardados pelo jeito.
_motores = {}


class PaddleOcrFaltando(Exception):
    """A instalação está sem algum modelo, ou o motor não carrega."""


def pasta_dos_modelos():
    """Onde os modelos moram: dentro do pacote do RapidOCR.

    Vale igual no ambiente de desenvolvimento e na pasta montada para a
    entrega, desde que a receita do empacotamento leve a pasta junto.
    """
    import rapidocr
    return Path(rapidocr.__file__).parent / "models"


def presente():
    """Diz se o PaddleOCR pode ler nesta instalação.

    Confere os arquivos antes de qualquer coisa: é o que impede a biblioteca de
    chegar ao ponto em que ela tentaria buscar o modelo que falta.
    """
    try:
        pasta = pasta_dos_modelos()
    except Exception:
        return False
    return all((pasta / nome).is_file() for nome in MODELOS)


def preparar(virar_linhas):
    """Carrega o motor, uma vez. Levanta PaddleOcrFaltando quando não dá.

    `virar_linhas` liga o que vira linha por linha o que parece estar de cabeça
    para baixo. Com o detector do Tesseract na máquina ele fica desligado: o
    detector endireita a página inteira, e esta peça só atrapalhava - virava
    linhas que estavam certas, duas inteiras no ofício deitado da massa 20. Sem
    o detector, ela é a única defesa contra a folha que entrou de cabeça para
    baixo no escâner, e perder uma ou outra linha é melhor que perder a página
    (medição e lente crítica da etapa 3 da funcionalidade 7, 19/10/2026).
    """
    if virar_linhas in _motores:
        return _motores[virar_linhas]
    if not presente():
        raise PaddleOcrFaltando(
            "O PaddleOCR não está completo nesta instalação. Reinstale o "
            "programa."
        )
    try:
        from rapidocr import RapidOCR
        pasta = pasta_dos_modelos()
        motor = RapidOCR(params={
            "Det.model_path": str(pasta / MODELO_QUE_ACHA),
            "Cls.model_path": str(pasta / MODELO_QUE_VIRA),
            "Rec.model_path": str(pasta / MODELO_QUE_LE),
            # O RapidOCR escreve uma linha por modelo carregado. Ninguém vê
            # essas linhas no programa entregue, que não tem janela de texto.
            "Global.log_level": "error",
            # O caminho do modelo que vira as linhas vai dito acima mesmo
            # quando ele fica desligado, para a biblioteca nunca ir buscá-lo.
            "Global.use_cls": virar_linhas,
        })
    except Exception as problema:
        raise PaddleOcrFaltando(
            "O PaddleOCR não pôde ser carregado. Reinstale o programa."
        ) from problema
    _motores[virar_linhas] = motor
    return motor


def ler(imagem, virar_linhas):
    """Lê a imagem de uma página e devolve o texto, com as linhas remontadas.

    O PaddleOCR devolve pedaços de texto com a posição de cada um. Passando pela
    mesma remontagem que o texto de dentro do PDF usa, a tabela continua saindo
    como tabela de texto, com as colunas alinhadas (RN-10 e RN-34).
    """
    # A imagem vai pronta, e não como tabela de números: pronta, o RapidOCR põe
    # as cores na ordem que os modelos esperam; como tabela, ele supõe que a
    # ordem já veio trocada e não mexe - e a tinta azul de um carimbo chegava
    # ao modelo como vermelha, mais clara contra o papel (lente crítica da
    # etapa 1, 18/10/2026).
    resultado = preparar(virar_linhas)(imagem.convert("RGB"))
    if not resultado.txts:
        return ""
    pedacos = []
    for pontos, texto in zip(resultado.boxes, resultado.txts):
        xs = [float(ponto[0]) for ponto in pontos]
        ys = [float(ponto[1]) for ponto in pontos]
        pedacos.append((min(xs), min(ys), max(xs), max(ys), texto))
    return "\n".join(montar(agrupar_por_altura(pedacos)))

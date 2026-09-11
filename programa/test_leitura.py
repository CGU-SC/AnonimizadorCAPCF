"""Testes da leitura por OCR, sobre a massa inventada de dados-exemplo/.

Estes testes são os mais lentos do projeto, e não tem como ser diferente: eles
rodam o Tesseract de verdade, e cada página custa perto de um segundo e meio.
Por isso usam o documento de uma página e param a leitura cedo — o que se quer
provar aqui é o comportamento, não a paciência de quem espera.
"""
from pathlib import Path

import pytest

import leitura

MASSA = Path(__file__).parent.parent / "dados-exemplo"


def test_o_motor_de_leitura_e_encontrado_nesta_maquina():
    caminho = leitura.localizar_tesseract()

    assert caminho is not None, (
        "o Tesseract não foi encontrado - os outros testes desta lista não "
        "têm como rodar"
    )
    assert caminho.exists()


def test_documento_deitado_sai_endireitado():
    """Regra RN-6, e um dos critérios de aceite da spec 002.

    O conteúdo está deitado 90 graus dentro de uma página em pé, e o campo de
    rotação do PDF está zerado - ele não denuncia nada. Sem endireitar, o texto
    sai como sequência de caracteres soltos.
    """
    paginas = leitura.ler_documento(MASSA / "03-conteudo-girado.pdf")

    assert len(paginas) == 1
    assert "UNIVERSIDADE FEDERAL DE SANTA CATARINA" in paginas[0]


def test_a_contagem_de_paginas_e_avisada_na_ordem():
    avisos = []

    def anotar(pagina, total):
        avisos.append((pagina, total))

    # Cancela depois da segunda página, para o teste não levar 18 segundos.
    leituras_feitas = []

    def ja_deu():
        leituras_feitas.append(1)
        return len(leituras_feitas) > 2

    with pytest.raises(leitura.LeituraCancelada):
        leitura.ler_documento(
            MASSA / "02-imprimir-para-pdf.pdf",
            ao_avancar=anotar,
            foi_cancelado=ja_deu,
        )

    assert avisos[0] == (1, 12)
    assert avisos[1] == (2, 12)


def test_cancelar_para_a_leitura_e_diz_em_que_pagina():
    paginas_lidas = []

    def parar_na_terceira():
        paginas_lidas.append(1)
        return len(paginas_lidas) > 2

    with pytest.raises(leitura.LeituraCancelada) as parada:
        leitura.ler_documento(
            MASSA / "02-imprimir-para-pdf.pdf", foi_cancelado=parar_na_terceira
        )

    assert parada.value.pagina == 3


def test_o_pdf_de_origem_nao_e_alterado_pela_leitura():
    """Regra RN-17, agora sobre o caminho que mais mexe no documento.

    A leitura desenha cada página como imagem, gira o que estiver deitado e
    manda para o OCR. Nada disso pode encostar no arquivo de origem.
    """
    caminho = MASSA / "03-conteudo-girado.pdf"
    antes = caminho.read_bytes()

    leitura.ler_documento(caminho)

    assert caminho.read_bytes() == antes


def test_a_leitura_nao_fala_com_ninguem_fora_da_maquina():
    """Critério de aceite da spec 002, conferido no próprio arquivo.

    A razão de o programa existir é o documento não sair da universidade. Se
    alguém um dia acrescentar uma chamada de rede aqui, este teste cai.
    """
    codigo = Path(leitura.__file__).read_text(encoding="utf-8").lower()

    for proibido in ["http", "requests", "urllib", "socket", "api_key", "webhook"]:
        assert proibido not in codigo, (
            f"apareceu '{proibido}' no módulo de leitura - nenhum caminho de "
            "código pode apontar para fora da máquina"
        )

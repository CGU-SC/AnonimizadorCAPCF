"""Testes de leitura do PDF, sobre a massa inventada de dados-exemplo/.

O nome do arquivo começa com "test_" porque é assim que o pytest encontra os
testes sozinho; o resto está em português, como todo o projeto.

Estes testes conferem por dentro o que a pessoa confere na tela. São eles que
avisam quando uma etapa nova quebra uma etapa antiga - coisa que ninguém
percebe olhando.
"""
from pathlib import Path

import pytest

import documento

MASSA = Path(__file__).parent.parent / "dados-exemplo"


def test_pdf_com_texto_por_dentro_e_reconhecido():
    ficha = documento.conferir(MASSA / "01-com-texto-e-tabela.pdf")

    assert ficha.paginas == 3
    assert ficha.tem_camada_de_texto
    assert ficha.letras_na_camada_de_texto > 500


def test_imprimir_para_pdf_nao_tem_camada_de_texto():
    """O caso que a spec 002 mais insiste em cobrir.

    O "Imprimir para PDF" do Windows transforma as letras em desenho: o
    arquivo parece cheio de texto para quem olha, e não tem letra nenhuma
    gravada por dentro. Confundir os dois faria o programa oferecer aproveitar
    um texto que não existe.
    """
    ficha = documento.conferir(MASSA / "02-imprimir-para-pdf.pdf")

    assert ficha.paginas == 12
    assert not ficha.tem_camada_de_texto
    assert ficha.letras_na_camada_de_texto == 0


def test_documento_deitado_tambem_vai_para_o_ocr():
    ficha = documento.conferir(MASSA / "03-conteudo-girado.pdf")

    assert ficha.paginas == 1
    assert not ficha.tem_camada_de_texto


def test_texto_embaralhado_conta_como_camada_de_texto():
    """O programa não julga se o texto presta - isso é da pessoa (RN-4).

    Este documento tem texto por dentro, e esse texto é lixo ilegível. Ainda
    assim o programa precisa dizer que HÁ texto ali, e deixar quem olha
    decidir. Julgar qualidade de texto é palpite, e palpite errado aqui produz
    um arquivo de lixo que ninguém percebe.
    """
    ficha = documento.conferir(MASSA / "04-texto-embaralhado.pdf")

    assert ficha.tem_camada_de_texto


def test_arquivo_corrompido_explica_em_vez_de_quebrar():
    with pytest.raises(documento.DocumentoNaoAbre) as erro:
        documento.conferir(MASSA / "05-corrompido.pdf")

    assert "danificado" in str(erro.value)


def test_arquivo_protegido_por_senha_explica_em_vez_de_quebrar():
    with pytest.raises(documento.DocumentoNaoAbre) as erro:
        documento.conferir(MASSA / "06-protegido-por-senha.pdf")

    assert "senha" in str(erro.value)


def test_arquivo_que_nao_existe_explica_em_vez_de_quebrar():
    with pytest.raises(documento.DocumentoNaoAbre):
        documento.conferir(MASSA / "este-arquivo-nao-existe.pdf")


def test_o_pdf_de_origem_nunca_e_alterado():
    """Regra RN-17 da spec 002, conferida byte a byte.

    É a regra que protege o documento da pessoa: o programa lê, e só. Se um dia
    alguém trocar a abertura do PDF por uma que grava, este teste cai.
    """
    for nome in [
        "01-com-texto-e-tabela.pdf",
        "02-imprimir-para-pdf.pdf",
        "03-conteudo-girado.pdf",
        "04-texto-embaralhado.pdf",
    ]:
        caminho = MASSA / nome
        antes = caminho.read_bytes()

        documento.conferir(caminho)

        assert caminho.read_bytes() == antes, f"{nome} foi alterado ao ser lido"

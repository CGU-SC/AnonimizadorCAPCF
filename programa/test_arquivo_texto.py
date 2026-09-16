"""Testes da leitura do `.md` e do `.txt` no Anonimizar (regra RN-21)."""
from pathlib import Path

import pytest

from arquivo_texto import ArquivoNaoServe, ler

MASSA = Path(__file__).parent.parent / "dados-exemplo"

# A frase da massa que só sai certa quando os acentos foram lidos do jeito
# certo. Lida do jeito errado, o "ç" vira dois símbolos e a frase muda.
FRASE_COM_ACENTOS = "Observação: órgão, função, lição, pôr, será, útil, ênfase, crédito."


@pytest.mark.parametrize("nome", [
    "12-acentos-bloco-de-notas-atual.txt",
    "13-acentos-bloco-de-notas-antigo.txt",
])
def test_os_dois_jeitos_do_bloco_de_notas_abrem_com_os_acentos_certos(nome):
    texto = ler(MASSA / nome)
    assert FRASE_COM_ACENTOS in texto
    assert "Ã" not in texto  # o sinal clássico de acento lido do jeito errado


def test_a_quebra_de_linha_do_windows_vira_uma_so():
    texto = ler(MASSA / "12-acentos-bloco-de-notas-atual.txt")
    assert "\r" not in texto
    assert texto.count("\n") > 3


def test_o_md_da_massa_abre_inteiro():
    texto = ler(MASSA / "10-prestacao-com-cpf.md")
    assert texto.startswith("# Prestação de Contas")
    assert texto.rstrip().endswith("Coordenador do projeto")


def test_arquivo_vazio_explica_e_nao_estoura():
    with pytest.raises(ArquivoNaoServe) as problema:
        ler(MASSA / "15-vazio.md")
    assert "está vazio" in str(problema.value)
    assert "15-vazio.md" in str(problema.value)


def test_arquivo_que_nao_e_texto_explica_e_nao_estoura():
    with pytest.raises(ArquivoNaoServe) as problema:
        ler(MASSA / "16-planilha-renomeada.md")
    assert "não parece ser texto" in str(problema.value)


def test_arquivo_so_com_espacos_conta_como_vazio(tmp_path):
    arquivo = tmp_path / "branco.md"
    arquivo.write_text("   \n\n\t\n", encoding="utf-8")
    with pytest.raises(ArquivoNaoServe):
        ler(arquivo)


def test_texto_tirado_de_pdf_com_avanco_de_pagina_abre(tmp_path):
    """Regressão da revisão da etapa 2: este arquivo era recusado.

    O avanço de página é a marca invisível que separa uma página da outra no
    texto tirado de PDF - o formato mais comum de .txt que chega aqui.
    """
    arquivo = tmp_path / "tirado-do-pdf.txt"
    arquivo.write_text(
        "Página 1" + chr(12) + "Página 2, CPF 111.111.111-11", encoding="utf-8")
    assert "111.111.111-11" in ler(arquivo)


def test_md_salvo_pelo_word_com_marcador_de_lista_abre(tmp_path):
    """O Word usa um símbolo próprio no marcador de lista, e ele é legítimo."""
    marcador = chr(0xF0B7)
    arquivo = tmp_path / "do-word.md"
    linhas = [f"{marcador} item um", f"{marcador} item dois", ""]
    arquivo.write_text("\n".join(linhas), encoding="utf-8")
    assert "item um" in ler(arquivo)


def test_arquivo_so_com_a_marca_do_bloco_de_notas_conta_como_vazio(tmp_path):
    """Regressão da revisão da etapa 2: este abria a revisão em branco.

    Um arquivo "vazio" gravado pelo Bloco de Notas não tem zero bytes: tem os
    três bytes invisíveis que ele põe no começo de tudo.
    """
    arquivo = tmp_path / "vazio-do-bloco-de-notas.txt"
    arquivo.write_bytes("﻿".encode("utf-8"))
    with pytest.raises(ArquivoNaoServe) as problema:
        ler(arquivo)
    assert "está vazio" in str(problema.value)


def test_arquivo_gravado_com_a_marca_do_bloco_de_notas(tmp_path):
    """O Bloco de Notas põe três bytes invisíveis no começo do arquivo.

    Sem tratá-los, eles virariam símbolos estranhos na primeira linha do texto,
    bem onde a pessoa olha primeiro.
    """
    arquivo = tmp_path / "com-marca.txt"
    arquivo.write_bytes("﻿CPF 111.111.111-11".encode("utf-8"))
    assert ler(arquivo) == "CPF 111.111.111-11"

"""Os critérios de aceite da spec 003 sobre achar, conferir e mascarar o CPF.

Cada teste é um critério de "Encontrar e conferir" ou de "Máscara", com os
números da própria spec. Os que passam na conta são só de dígitos repetidos, e
os suspeitos falham na conta mesmo com as letras trocadas de volta (RN-22).
"""
from pathlib import Path

import pytest

from cpf import (
    FALHA_NA_CONTA,
    LETRA_NO_LUGAR_DE_DIGITO,
    LIBERADO,
    MASCARADO_A_MAO,
    PARTIDO_EM_DUAS_LINHAS,
    PASSA_NA_CONTA,
    QUASE_CPF,
    aplicar,
    mascarar_a_mao,
    passa_na_conta,
    procurar,
)


def _unica(texto):
    achados = procurar(texto)
    assert len(achados) == 1, [a.original for a in achados]
    return achados[0]


# ------------------------------------------------------------ a conta (RN-4)

@pytest.mark.parametrize("digitos", [
    "11111111111", "22222222222", "55555555555", "99999999999",
])
def test_digitos_repetidos_passam_na_conta(digitos):
    assert passa_na_conta(digitos)


@pytest.mark.parametrize("digitos", [
    "12345678910", "77777777778", "33333333334", "24681357912",
])
def test_numeros_da_massa_que_falham_na_conta(digitos):
    assert not passa_na_conta(digitos)


# -------------------------------------------------- encontrar e conferir

def test_os_quatro_formatos_combinados_passam_na_conta_e_nao_sao_suspeitos():
    texto = "a 111.111.111-11, b 11111111111, c 111111111-11, d 111.111.111/11."
    achados = procurar(texto)
    assert [a.original for a in achados] == [
        "111.111.111-11", "11111111111", "111111111-11", "111.111.111/11",
    ]
    assert all(a.tipo == PASSA_NA_CONTA for a in achados)
    assert not any(a.suspeito for a in achados)
    assert aplicar(texto, achados) == (
        "a ***.111.111-**, b ***111111**, c ***111111-**, d ***.111.111-**."
    )


def test_numero_que_falha_na_conta_e_mascarado_e_suspeito():
    achado = _unica("recibo de Ana, CPF 123.456.789-10, valor")
    assert achado.tipo == FALHA_NA_CONTA
    assert achado.suspeito
    assert achado.mascara == "***.456.789-**"


def test_os_tres_jeitos_de_quase_cpf():
    texto = (
        "letra l23.456.789-1O aqui\n"
        "espaco 123 456 789 10 aqui\n"
        "partido 123.456.\n"
        "789-10 aqui"
    )
    achados = procurar(texto)
    assert [a.original for a in achados] == [
        "l23.456.789-1O", "123 456 789 10", "123.456.\n789-10",
    ]
    assert all(a.tipo == QUASE_CPF and a.suspeito for a in achados)
    assert not any(a.passa_na_conta for a in achados)


def test_tres_letras_com_pontuacao_de_cpf_sao_mascaradas():
    """Quarta emenda: com ponto, traço ou barra, cabem até 4 letras.

    A pontuação nos lugares exatos de um CPF quase nunca aparece numa palavra
    ou num código, e ainda sobram 7 dígitos certos sustentando a suspeita.
    """
    achado = _unica("campo ilegível l23.4S6.789-1O no texto")
    assert achado.tipo == QUASE_CPF
    assert achado.mascara == "***.4S6.789-**"


def test_tres_letras_sem_nenhuma_pontuacao_nao_sao_mascaradas():
    # Sem separador, a sequência tem cara de código ou protocolo.
    assert procurar("codigo l234S67891O no texto") == []


def test_quatro_letras_com_pontuacao_ainda_sao_mascaradas():
    """O teto da quarta emenda, pelo lado de dentro."""
    achado = _unica("folha l23.4S6.7B9-1O no texto")
    assert achado.tipo == QUASE_CPF
    assert achado.mascara == "***.4S6.7B9-**"


def test_cinco_letras_com_pontuacao_nao_sao_mascaradas():
    """O teto da quarta emenda, pelo lado de fora.

    Este é o teste que segura o limite: com ele, subir o teto de 4 para 5 passa
    a quebrar a lista. O exemplo de antes (SOL.IDA.DES-OS) não servia para
    isso - ele nem chega a ser considerado, porque A, E e L não são letras que
    a leitura confunde com dígito.
    """
    assert procurar("chave lZ3.4S6.7B9-1O no texto") == []


def test_letras_que_nao_se_confundem_com_digito_nao_contam():
    assert procurar("referencia SOL.IDA.DES-OS no texto") == []


def test_o_espaco_nao_conta_como_pontuacao():
    """Documento de contas é cheio de número separado por espaço."""
    assert procurar("quantidades l23 4S6 789 1O somadas") == []


@pytest.mark.parametrize("texto", [
    "Fundacao Exemplo - CNPJ 12.345.678/0001-90",
    "Processo no 23080.012345/2026-11",
    "Processo no 23080012345202611",
    "Linha 34191.79001 01043.510047 91020.150008 1 89410000026000",
])
def test_cnpj_processo_e_boleto_saem_inteiros(texto):
    assert procurar(texto) == []


def test_cpf_colado_a_outro_digito_nao_e_mascarado():
    assert procurar("numero 9111.111.111-11 e 111.111.111-119") == []


def test_arquivo_ja_anonimizado_nao_tem_cpf():
    texto = "CPF ***.111.111-**, ***111111** e ***.456.\n789-**"
    assert procurar(texto) == []


@pytest.mark.parametrize("texto", [
    "Número: 123456789\nSituação: em análise",
    "Processo 987654321\nSolicitante: Fulano",
    "Termo 555444333\nObjeto: pesquisa",
])
def test_letra_no_fim_grudada_numa_palavra_nao_conta(texto):
    """Quinta emenda: a letra final grudada numa palavra é começo de palavra.

    São o formato que deu 18 alarmes falsos num documento de verdade testado
    pela usuária - aqui, com números inventados. Todos sem pontuação: é só aí
    que a regra vale (revisão da etapa 3).
    """
    assert procurar(texto) == []


def test_cpf_pontuado_com_letra_no_fim_grudada_continua_mascarado():
    """Regressão da revisão da etapa 3: este CPF escapava inteiro.

    A regra da quinta emenda vale só sem pontuação de CPF. Com ponto e traço nas
    posições exatas, a letra final grudada numa palavra é um dígito que a leitura
    trocou - e soltá-lo deixaria o CPF sair calado.
    """
    # O "l" vira 1, então este passa na conta: é o caso mais perigoso, porque
    # quase certamente é o CPF de alguém.
    texto = "CPF 111.111.111-1lAssinado por Fulano"
    achado = _unica(texto)
    assert achado.tipo == QUASE_CPF and achado.pede_dupla_conferencia
    assert achado.original not in aplicar(texto, [achado])
    # E o mesmo com a pontuação mais discreta, só o traço.
    assert _unica("CPF 111111111-1lAssinado").pede_dupla_conferencia


def test_letra_no_fim_grudada_numa_palavra_com_pontuacao_continua_suspeita():
    """Com pontuação, a regra da quinta emenda não vale - e é de propósito.

    O "S" de "Sobre" provavelmente é pedaço da palavra, mas o número é pontuado:
    entre um alarme falso, que sai com um clique, e um CPF que escapa calado,
    fica o alarme (RN-5).
    """
    achado = _unica("111.111.111-1Sobre o assunto")
    assert achado.tipo == QUASE_CPF and achado.mascara == "***.111.111-**"


def test_cpf_partido_com_letra_no_fim_continua_mascarado():
    """A regra da quinta emenda não pode soltar o CPF partido de verdade.

    Aqui a letra no fim é um dígito que a leitura trocou, e depois dela vem uma
    vírgula - e não o resto de uma palavra.
    """
    achado = _unica("CPF 123.456.\n789-1O, referente à viagem")
    assert achado.tipo == QUASE_CPF
    assert achado.mascara == "***.456.\n789-**"


def test_cpf_grudado_na_palavra_com_letra_na_ponta_e_achado():
    """Regressão da revisão da etapa 1: estes dois saíam inteiros, sem máscara
    e fora da lista, porque a letra da ponta encostava numa palavra."""
    for texto in ("CPFl11.111.111-11 x", "nºl11.111.111-11 x"):
        achado = _unica(texto)
        assert achado.original == "l11.111.111-11", texto
        assert achado.tipo == QUASE_CPF and achado.pede_dupla_conferencia
        assert "l11" not in aplicar(texto, [achado])


def test_cpf_depois_de_letra_que_nao_parece_digito_e_achado():
    # A leitura cola o "CPF" no número quando perde o espaço. O número continua
    # sendo CPF - soltá-lo por causa disso seria o erro do lado perigoso.
    achados = procurar("CPF111.111.111-11 e nº222.222.222-22,")
    assert [a.original for a in achados] == ["111.111.111-11", "222.222.222-22"]


# ------------------------------------- o "quase CPF" que passa na conta (emenda)

def test_quase_cpf_que_passa_na_conta_pede_a_dupla_conferencia():
    texto = "letra l11.111.111-11 e partido 555.555.\n555-55 fim"
    letra, partido = procurar(texto)
    assert letra.tipo == QUASE_CPF and letra.motivo == LETRA_NO_LUGAR_DE_DIGITO
    assert partido.tipo == QUASE_CPF and partido.motivo == PARTIDO_EM_DUAS_LINHAS
    assert letra.passa_na_conta and partido.passa_na_conta
    assert letra.pede_dupla_conferencia and partido.pede_dupla_conferencia


def test_so_o_que_passa_na_conta_pede_a_dupla_conferencia():
    valido, falha, quase = procurar(
        "111.111.111-11 e 123.456.789-10 e l23.456.789-1O")
    assert valido.pede_dupla_conferencia
    assert not falha.pede_dupla_conferencia
    assert not quase.pede_dupla_conferencia


# ------------------------------------------------------------ a máscara (RN-6)

@pytest.mark.parametrize("original, mascarado", [
    ("111.111.111-11", "***.111.111-**"),
    ("11111111111", "***111111**"),
    ("111.111.111/11", "***.111.111-**"),
    ("l23.456.789-1O", "***.456.789-**"),
    ("123 456 789 10", "*** 456 789 **"),
])
def test_a_mascara_de_cada_formato(original, mascarado):
    assert _unica(f"CPF {original} fim").mascara == mascarado


def test_cpf_partido_e_mascarado_nas_duas_partes_e_a_quebra_fica():
    texto = "Pedro, CPF ***.555.\n555-** fim"
    original = "Pedro, CPF 555.555.\n555-55 fim"
    assert aplicar(original, procurar(original)) == texto


def test_a_mascara_nao_muda_o_tamanho_e_a_tabela_fica_alinhada():
    tabela = (
        "| Nome     | CPF            | Valor |\n"
        "| -------- | -------------- | ----- |\n"
        "| Beltrana | 222.222.222-22 | 1.500 |\n"
        "| Maria    | 44444444444    | 4.200 |\n"
    )
    saida = aplicar(tabela, procurar(tabela))
    assert saida.count("*") == 10
    assert [len(l) for l in saida.splitlines()] == [len(l) for l in tabela.splitlines()]
    assert [l.count("|") for l in saida.splitlines()] == [4, 4, 4, 4]


def test_numero_liberado_volta_ao_original_no_texto_de_saida():
    texto = "CPF 111.111.111-11 e 123.456.789-10."
    valido, falha = procurar(texto)
    falha.situacao = LIBERADO
    assert aplicar(texto, [valido, falha]) == "CPF ***.111.111-** e 123.456.789-10."


# ----------------------------------------------------- a máscara à mão (RN-9)

def test_mascarar_a_mao_esconde_tres_primeiros_e_dois_ultimos_digitos():
    texto = "informa o CPF nº 1234 5678 910 e o endereço"
    inicio = texto.index("1234")
    achado = mascarar_a_mao(texto, inicio, inicio + len("1234 5678 910"))
    assert achado.mascara == "***4 5678 9**"
    assert achado.tipo == MASCARADO_A_MAO
    assert not achado.pede_dupla_conferencia
    assert aplicar(texto, [achado]) == "informa o CPF nº ***4 5678 9** e o endereço"


def test_mascarar_a_mao_conta_letra_quando_o_trecho_e_so_um_numero():
    """Sexta emenda: é o número que a leitura estragou demais que se mascara à mão.

    Contando só dígitos, o "l" e o "O" - que são o primeiro e o último dígito do
    número - ficariam à vista.
    """
    texto = "campo ilegível l23.4S6.789-1O no texto"
    inicio = texto.index("l23")
    achado = mascarar_a_mao(texto, inicio, inicio + len("l23.4S6.789-1O"))
    assert achado.mascara == "***.4S6.789-**"


def test_mascarar_a_mao_com_palavras_no_trecho_conta_so_digitos():
    """Senão o programa mascararia o "S" e o "o" de "Sobre"."""
    texto = "Sobre 1234 5678 910 no texto"
    achado = mascarar_a_mao(texto, 0, texto.index(" no"))
    assert achado.original == "1234 5678 910"
    assert achado.mascara == "***4 5678 9**"


def test_mascarar_a_mao_com_cinco_digitos_ou_menos_esconde_todos():
    texto = "codigo 12-345 aqui"
    achado = mascarar_a_mao(texto, 7, 13)
    assert achado.mascara == "**-***"


def test_mascarar_a_mao_sem_digito_nao_muda_nada():
    assert mascarar_a_mao("so palavras aqui", 0, 16) is None


def test_mascara_a_mao_por_cima_de_um_cpf_nao_desfaz_a_mascara_dele():
    """Regressão da revisão da etapa 1: marcar à mão um trecho que engloba um
    CPF já mascarado devolvia os dois últimos dígitos dele ao arquivo."""
    texto = "CPF 111.111.111-11 e 22 fim"
    automatico = procurar(texto)
    a_mao = mascarar_a_mao(texto, texto.index("111"), texto.index(" fim"))
    esperado = "CPF ***.111.111-** e ** fim"
    assert aplicar(texto, automatico + [a_mao]) == esperado
    assert aplicar(texto, [a_mao] + automatico) == esperado


def test_mascarar_a_mao_ignora_o_espaco_pego_nas_pontas():
    texto = "nº  1234 5678 910  e"
    achado = mascarar_a_mao(texto, 2, 19)
    assert achado.original == "1234 5678 910"


# ------------------------------------------------------------- a massa

PROGRAMA = Path(__file__).parent
MASSA = PROGRAMA.parent / "dados-exemplo"


def _textos_da_massa():
    """O texto de todo arquivo da massa: os .md, os .txt e os PDFs que abrem."""
    import pymupdf

    for arquivo in sorted(MASSA.iterdir()):
        if arquivo.suffix in (".md", ".txt"):
            bruto = arquivo.read_bytes()
            for codificacao in ("utf-8", "cp1252"):
                try:
                    yield arquivo.name, bruto.decode(codificacao)
                    break
                except UnicodeDecodeError:
                    continue
        elif arquivo.suffix == ".pdf":
            try:
                with pymupdf.open(arquivo) as documento:
                    yield arquivo.name, "\n".join(p.get_text() for p in documento)
            except Exception:
                continue  # o corrompido e o protegido por senha não abrem


def test_a_massa_so_tem_numero_valido_de_digitos_repetidos():
    """RN-22: nenhum número da massa que passa na conta pode ser de alguém."""
    for nome, texto in _textos_da_massa():
        for achado in procurar(texto):
            if achado.passa_na_conta:
                digitos = "".join(c for c in achado.original if c.isdigit())
                assert len(set(digitos)) == 1, (nome, achado.original)


def test_o_documento_principal_da_massa():
    texto = (MASSA / "10-prestacao-com-cpf.md").read_text(encoding="utf-8")
    achados = procurar(texto)
    assert [(a.original, a.tipo, a.passa_na_conta) for a in achados] == [
        ("246 813 579 12", QUASE_CPF, False),
        ("111.111.111-11", PASSA_NA_CONTA, True),
        ("222.222.222-22", PASSA_NA_CONTA, True),
        ("777.777.777-78", FALHA_NA_CONTA, False),
        ("44444444444", PASSA_NA_CONTA, True),
        ("333.333.333/34", FALHA_NA_CONTA, False),
        ("l23.456.789-1O", QUASE_CPF, False),
        ("555.555.\n555-55", QUASE_CPF, True),
        ("l11.111.111-11", QUASE_CPF, True),
        ("666 666 666 66", QUASE_CPF, True),
        ("l23.4S6.789-1O", QUASE_CPF, False),
        ("l23.4S6.7B9-1O", QUASE_CPF, False),
    ]
    anonimizado = (MASSA / "10-prestacao-com-cpf - sem CPF.md").read_text(
        encoding="utf-8")
    assert procurar(anonimizado) == []


# ------------------------------------------------------------- fronteiras


def test_o_modulo_de_ocr_nao_usa_nada_de_cpf():
    """RN-18: procurar, conferir e mascarar CPF mora só no Anonimizar."""
    do_ocr = ["painel_ocr.py", "tela_conferencia.py", "tela_decisao.py",
              "telas_de_salvar.py", "telas_do_motor.py", "leitura.py",
              "leitura_em_segundo_plano.py", "documento.py", "disposicao.py",
              "arquivo_md.py", "motor.py"]
    for nome in do_ocr:
        codigo = (PROGRAMA / nome).read_text(encoding="utf-8")
        assert "import cpf" not in codigo and "from cpf" not in codigo, nome
        assert "passa_na_conta" not in codigo, nome


def test_o_motor_do_cpf_nao_fala_com_a_internet():
    """RN-20: nenhum código do Anonimizar fala com serviço fora da máquina."""
    codigo = (PROGRAMA / "cpf.py").read_text(encoding="utf-8").lower()
    for sinal in ("http", "socket", "urllib", "requests"):
        assert sinal not in codigo, sinal

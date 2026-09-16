r"""Gera a massa de texto com CPF do Anonimizar: .md e .txt inventados.

Fica separado do gerar-massa.py de propósito. Aquele grava PDFs, e todo PDF sai
com bytes diferentes a cada rodada mesmo sem mudar nada; rodar os dois juntos
sujaria o histórico toda vez que só a massa de texto precisasse ser refeita.

Nenhum número aqui pode ser de alguém (regra RN-22 da spec 003). Os que passam
na conta do dígito verificador são SÓ de dígitos repetidos (111.111.111-11,
222.222.222-22...), que a Receita não emite. Os suspeitos e os "quase CPF"
falham na conta, mesmo com as letras trocadas de volta por dígitos, ou partem
de dígitos repetidos. Atenção: nem todo número "de sequência" inventado na
hora falha na conta, e um que passe pode ser o CPF de alguém. Número novo nesta
massa passa antes pelo teste que varre a pasta (programa/test_cpf.py).

Rode assim, da raiz do projeto:

    .\.venv\Scripts\python.exe dados-exemplo\gerar-massa-cpf.py
"""
import sys
from pathlib import Path

PASTA = Path(__file__).parent
sys.path.insert(0, str(PASTA.parent / "programa"))

from cpf import aplicar, procurar  # noqa: E402  (depois do caminho acima)

# O documento principal é o do rascunho de tela 01 do Anonimizar, para a tela
# construída mostrar exatamente o que foi aprovado no desenho. Os casos de canto
# vêm no fim, em frases de documento, e não numa lista solta.
PRESTACAO = """\
# Prestação de Contas — Projeto 042/2026

Fundação de Apoio Exemplo — CNPJ 12.345.678/0001-90
Processo nº 23080.012345/2026-11

## 1. Identificação

Trata-se de prestação de contas referente ao projeto de pesquisa
identificado abaixo, encaminhada pela fundação de apoio para análise
desta Coordenadoria. O coordenador indicado no Termo de outorga nº
246 813 579 12 é o servidor Fulano de Tal Exemplo, inscrito no CPF
111.111.111-11, conforme documentação anexa aos autos.

## 2. Equipe e bolsas pagas

| Nome                   | CPF            | Função       | Valor       |
| ---------------------- | -------------- | ------------ | ----------- |
| Beltrana Exemplo Silva | 222.222.222-22 | Bolsista     | R$ 1.500,00 |
| Ciclano Teste Souza    | 777.777.777-78 | Bolsista     | R$ 1.500,00 |
| Maria Fictícia Andrade | 44444444444    | Pesquisadora | R$ 4.200,00 |
| João Inventado Lima    | 333.333.333/34 | Técnico      | R$ 2.800,00 |

## 3. Despesas com pessoa física

Pagamento de serviço de revisão de texto, conforme recibo assinado
por Ana Suposta Ribeiro, CPF l23.456.789-1O, no valor de R$ 850,00.
A declaração do prestador, preenchida à mão, informa o CPF nº
1234 5678 910 e o endereço para correspondência.
Diária paga ao colaborador externo Pedro Hipotético Costa, CPF 555.555.
555-55, referente à viagem de campo de 03/08/2026.

## 4. Despesas com pessoa jurídica

| Fornecedor               | CNPJ               | Valor       |
| ------------------------ | ------------------ | ----------- |
| Papelaria Inventada Ltda | 98.765.432/0001-10 | R$ 412,30   |
| Gráfica Modelo S.A.      | 11.222.333/0001-80 | R$ 1.980,00 |

## 5. Observações da análise

O boleto da taxa bancária foi pago pela linha digitável
34191.79001 01043.510047 91020.150008 1 89410000026000.
Consta ainda o recibo de Otávio Suposto Nunes, CPF l11.111.111-11,
lido com uma letra no lugar do primeiro dígito, e o de Rita Inventada
Paes, CPF 666 666 666 66, lido com espaços no lugar dos pontos.
O protocolo interno 9111.111.111-11 e a matrícula 111.111.111-119
não são CPF. A ficha de Sônia Exemplo Dias traz o campo de CPF
ilegível, lido como l23.4S6.789-1O; noutra folha, com mais um dígito
trocado por letra, l23.4S6.7B9-1O. Já o código de conferência
l234S67891O, a chave lZ3.4S6.7B9-1O e a referência SOL.IDA.DES-OS não
são CPF: o primeiro tem três letras e nenhuma pontuação, o segundo tem
cinco letras, e o terceiro tem letras que não se confundem com dígito.

## 6. Conclusão

Os documentos apresentados guardam correspondência com o plano de
trabalho aprovado. Encaminha-se para análise técnica da CAPCF.

Florianópolis, 14 de setembro de 2026.

Fulano de Tal Exemplo
Coordenador do projeto
"""

SEM_CPF = """\
# Ata da reunião do Conselho Curador — setembro de 2026

Fundação de Apoio Exemplo — CNPJ 12.345.678/0001-90
Processo nº 23080.054321/2026-40

Aos quatorze dias do mês de setembro de 2026, reuniu-se o Conselho Curador
para apreciar o relatório de execução do Projeto 042/2026. Foram
apresentadas as despesas do período, no total de R$ 33.840,50, e o saldo
remanescente de R$ 1.159,50, a ser devolvido até 30/10/2026.

| Item | Descrição da despesa                   | Valor (R$) |
| ---- | -------------------------------------- | ---------- |
| 1    | Material de consumo para laboratório   | 3.480,00   |
| 2    | Passagens aéreas nacionais             | 6.120,50   |
| 3    | Diárias de campo                       | 9.240,00   |
| 4    | Serviço de terceiros — pessoa jurídica | 15.000,00  |

Nada mais havendo a tratar, a reunião foi encerrada.
"""

# Frase com todas as letras acentuadas que costumam sair trocadas quando o
# arquivo é lido no jeito errado: "Ã§" no lugar de "ç" é o sinal clássico.
COM_ACENTOS = """\
Relatório de execução físico-financeira — Projeto 042/2026

A coordenação informa que as ações previstas no cronograma foram
concluídas, à exceção da oficina de avaliação, adiada para outubro.
O bolsista Joaquim Ávila Conceição, CPF 888.888.888-88, apresentou a
prestação de serviços em 03/09/2026. A pesquisadora Inês Ângela Brandão
não recebeu pagamento no período.

Observação: órgão, função, lição, pôr, será, útil, ênfase, crédito.
"""

# 10 nomes x 4 = 40 linhas, como a tabela de bolsistas que o rascunho 01 cita
# para mostrar a lista crescendo. Metade passa na conta (dígitos repetidos) e
# metade falha (os mesmos dígitos com o último trocado).
NOMES = [
    "Ana", "Bruno", "Carla", "Diego", "Elisa",
    "Fábio", "Gisele", "Heitor", "Iara", "Júlio",
]
SOBRENOMES = ["Exemplo", "Inventado", "Fictício", "Suposto"]


def tabela_de_bolsistas():
    linhas = [
        "# Folha de bolsas — Projeto 042/2026",
        "",
        "| #  | Bolsista                  | CPF            | Valor       |",
        "| -- | ------------------------- | -------------- | ----------- |",
    ]
    for numero in range(40):
        digito = str(numero % 10)
        ultimo = digito if numero < 20 else str((numero + 1) % 10)
        cpf = f"{digito * 3}.{digito * 3}.{digito * 3}-{digito}{ultimo}"
        nome = f"{NOMES[numero % 10]} {SOBRENOMES[numero // 10]}"
        linhas.append(
            f"| {numero + 1:02} | {nome:<25} | {cpf} | R$ 1.500,00 |")
    return "\n".join(linhas) + "\n"


def gravar_texto(nome, texto, codificacao="utf-8", fim_de_linha="\n"):
    caminho = PASTA / nome
    with open(caminho, "w", encoding=codificacao, newline=fim_de_linha) as arquivo:
        arquivo.write(texto)
    return caminho


def main():
    gerados = [
        gravar_texto("10-prestacao-com-cpf.md", PRESTACAO),
        gravar_texto("11-sem-cpf.md", SEM_CPF),
        # O mesmo documento já passado pelo Anonimizar, com o nome que o
        # programa dá ao arquivo que grava. Serve para ver a revisão dizer
        # "nenhum CPF encontrado" num arquivo aberto de novo.
        gravar_texto("10-prestacao-com-cpf - sem CPF.md",
                     aplicar(PRESTACAO, procurar(PRESTACAO))),
        # Os dois jeitos como o Bloco de Notas do Windows grava texto (RN-21),
        # com a quebra de linha que ele usa (\r\n): o de hoje, e o antigo, no
        # padrão do Windows em português.
        gravar_texto("12-acentos-bloco-de-notas-atual.txt", COM_ACENTOS,
                     fim_de_linha="\r\n"),
        gravar_texto("13-acentos-bloco-de-notas-antigo.txt", COM_ACENTOS,
                     codificacao="cp1252", fim_de_linha="\r\n"),
        gravar_texto("14-folha-com-40-bolsistas.md", tabela_de_bolsistas()),
        gravar_texto("15-vazio.md", ""),
    ]

    # Um arquivo que não é texto, com nome de .md: o começo de um .xlsx (que
    # por dentro é um .zip) e bytes zerados, como fica quem renomeia planilha.
    nao_e_texto = PASTA / "16-planilha-renomeada.md"
    nao_e_texto.write_bytes(b"PK\x03\x04\x14\x00\x06\x00" + bytes(range(256)) * 4)
    gerados.append(nao_e_texto)

    for caminho in gerados:
        print(f"gerado: {caminho.name} ({caminho.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

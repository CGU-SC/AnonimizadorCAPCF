"""Como cada tipo de número se chama e de que cor ele é, na tela inteira.

Este arquivo existe por causa de um custo medido na revisão da etapa 5: o nome
de um tipo mudou duas vezes em quatro dias - "forma CPF válido" virou "CPF
válido" em 16/09/2026, e o "quase CPF" que passa na conta ganhou "válido se
corrigido" em 17/09 -, e cada troca dessas passava por três arquivos de tela,
mais os testes, mais a spec. Dois critérios de aceite ficaram quatro dias com o
nome velho, e o mesmo número corria o risco de se chamar uma coisa na lista e
outra no aviso de antes de gravar - bem na hora em que a pessoa decide se solta
um CPF.

Aqui é o único lugar que decide isso. As telas leem daqui; nenhuma escreve o
nome ou a cor à mão. O motor (`cpf.py`) continua sem saber de tela: ele dá o
tipo, e a tradução para o que a pessoa lê acontece deste lado.
"""
from typing import NamedTuple

import cpf
import estilo


class ComoAparece(NamedTuple):
    """O nome de um tipo na tela, no singular e no plural, e a cor dele."""

    nome: str
    plural: str
    cor: str


# O vermelho de letra para o que passa na conta - o número mais perigoso da
# tela; o amarelo de alerta para o que pede conferência; o azul para a máscara
# feita à mão, que é decisão da pessoa e não achado do programa; e o verde para
# o que ela soltou (sistema de design, 14 a 17/09/2026).
POR_TIPO = {
    cpf.PASSA_NA_CONTA: ComoAparece("CPF válido", "CPFs válidos",
                                    estilo.COR_ERRO_TEXTO),
    cpf.FALHA_NA_CONTA: ComoAparece("falha na conta", "falham na conta",
                                    estilo.COR_ALERTA),
    cpf.QUASE_CPF: ComoAparece("quase CPF", "quase CPF", estilo.COR_ALERTA),
    cpf.MASCARADO_A_MAO: ComoAparece("mascarado à mão", "mascarados à mão",
                                     estilo.COR_DESTAQUE_HOVER),
}

# "Suspeito" não é um tipo: é o grupo que junta o que falha na conta e o "quase
# CPF". Ele tem nome próprio na tela porque é assim que a pessoa pensa neles -
# são os que pedem uma olhada.
SUSPEITO = ComoAparece("suspeito", "suspeitos", estilo.COR_ALERTA)

# Também não é tipo, e sim situação: o número que a pessoa soltou.
LIBERADO = ComoAparece("liberado", "liberados", estilo.COR_SUCESSO)

# A etiqueta do "quase CPF" que passa na conta depois de corrigidas as letras.
# Ela não diz "CPF válido", que é o nome da seção de cima: com o mesmo nome nos
# dois lugares ficava confuso saber se aquilo era o número que a leitura pegou
# certinho ou o que só fecha a conta depois de corrigido (nome escolhido pela
# usuária em 17/09/2026).
VALIDO_SE_CORRIGIDO = ComoAparece("válido se corrigido", "válidos se corrigidos",
                                  estilo.COR_ERRO_TEXTO)

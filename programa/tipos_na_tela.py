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
    """O nome de um tipo na tela, no singular e no plural, e a cor dele.

    Guarda o nome do papel da cor, e não a cor: este arquivo carrega antes de o
    tema ser escolhido, e a cor guardada aqui ficaria a do escuro também no claro
    (RN-17 da spec 001). A cor é lida do estilo cada vez que uma tela a pede.
    """

    nome: str
    plural: str
    papel: str

    @property
    def cor(self):
        return getattr(estilo, self.papel)


# O vermelho de letra para o que passa na conta - o número mais perigoso da
# tela; o amarelo de alerta para o que pede conferência; o azul para a máscara
# feita à mão, que é decisão da pessoa e não achado do programa; e o verde para
# o que ela soltou (sistema de design, 14 a 17/09/2026).
POR_TIPO = {
    cpf.PASSA_NA_CONTA: ComoAparece("CPF válido", "CPFs válidos",
                                    "COR_ERRO_TEXTO"),
    cpf.FALHA_NA_CONTA: ComoAparece("falha na conta", "falham na conta",
                                    "COR_SUSPEITO"),
    cpf.QUASE_CPF: ComoAparece("quase CPF", "quase CPF", "COR_SUSPEITO"),
    cpf.MASCARADO_A_MAO: ComoAparece("mascarado à mão", "mascarados à mão",
                                     "COR_DESTAQUE_HOVER"),
}

# "Suspeito" não é um tipo: é o grupo que junta o que falha na conta e o "quase
# CPF". Ele tem nome próprio na tela porque é assim que a pessoa pensa neles -
# são os que pedem uma olhada.
SUSPEITO = ComoAparece("suspeito", "suspeitos", "COR_SUSPEITO")

# Também não é tipo, e sim situação: o número que a pessoa soltou.
LIBERADO = ComoAparece("liberado", "liberados", "COR_SUCESSO")

# A etiqueta do "quase CPF" que passa na conta depois de corrigidas as letras.
# Ela não diz "CPF válido", que é o nome da seção de cima: com o mesmo nome nos
# dois lugares ficava confuso saber se aquilo era o número que a leitura pegou
# certinho ou o que só fecha a conta depois de corrigido (nome escolhido pela
# usuária em 17/09/2026).
VALIDO_SE_CORRIGIDO = ComoAparece("válido se corrigido", "válidos se corrigidos",
                                  "COR_ERRO_TEXTO")

# A etiqueta do CPF que perdeu o zero da frente (nona emenda da spec 003,
# rascunho 09). Ela fica ao lado de "CPF válido" e explica por que um número de
# 10 dígitos está na lista - e é por ela que a pessoa reconhece o telefone que
# fechou a conta por acaso. Com 9 dígitos foram dois zeros, e a frase vai para o
# plural. A chave é quantos zeros faltavam.
SEM_ZERO = {
    1: ComoAparece("sem o zero da frente", "sem o zero da frente",
                   "COR_ERRO_TEXTO"),
    2: ComoAparece("sem os zeros da frente", "sem os zeros da frente",
                   "COR_ERRO_TEXTO"),
}

# O que veio da IA. Não é um tipo de CPF: é outra origem de suspeita (RN-29 da spec
# 004). O número da IA tem o tipo dele, e o nome destas é o da seção e o do selo.
DA_IA = ComoAparece("apontado pela IA", "apontados pela IA", "COR_IA")
NUMERO_NOVO = "número novo"
NUMERO_PARA_OLHAR = "número para olhar"
TITULO_DA_SECAO_DA_IA = "A IA pediu para olhar"

# O número que a pessoa liberou e a IA acha que é CPF (RN-69). Vermelho de letra, como o
# "CPF válido": o vermelho forte, em letra pequena, fica abaixo do contraste mínimo. Ele
# vai só na barra do item, que não é letra.
LIBERACAO_PARA_REVISAR = ComoAparece("liberação para revisar", "liberações para revisar",
                                     "COR_ERRO_TEXTO")
TITULO_DA_SECAO_DE_REVISAR = "Revisar liberação"

# O suspeito que a IA diz que não é CPF (RN-70). Lilás, a cor da IA, porque é a opinião
# dela que o separa dos outros suspeitos; na amarela, a tela dizia que a IA o tinha olhado
# e mantido a suspeita (conferência de 03/11/2026).
SUSPEITO_QUE_A_IA_NEGA = ComoAparece("suspeito que a IA nega", "suspeitos que a IA nega",
                                     "COR_IA")

"""Testes da barra de baixo da tela de revisão do Anonimizar."""
from tela_revisao import TelaRevisao


def test_a_revisao_por_ia_nasce_apagada_e_explicada(aplicacao):
    """Sem a IA ligada, o botão não pode parecer quebrado.

    Apagado sem a linha embaixo, a pessoa clicaria, nada aconteceria, e ela
    concluiria que o programa quebrou - por isso a explicação é conferida junto.
    """
    tela = TelaRevisao(ao_anonimizar_outro=lambda: None)

    assert tela.botao_revisar_com_ia.text() == "Revisar com IA"
    assert not tela.botao_revisar_com_ia.isEnabled()
    assert tela.explicacao_revisar_com_ia.text() == "Ligue em Configurações de IA, no fim do menu"

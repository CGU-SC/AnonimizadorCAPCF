"""A tela do LM Studio, contra o servidor de mentira (etapa 3 da spec 004)."""
import pytest

import config_ia
import preferencias
import trabalho_da_ia
from painel_ia import ESCOLHA_UM_MODELO, RESPONDENDO, PainelIa



RODAR_DE_VERDADE = trabalho_da_ia.rodar


def _na_hora(_dono, funcao, ao_pronto, ao_falhar):
    """Sem trabalho ao lado: o teste confere a tela, e não a linha paralela."""
    try:
        resultado = funcao()
    except Exception as problema:
        ao_falhar(trabalho_da_ia.frase_da_falha(problema))
    else:
        ao_pronto(resultado)


@pytest.fixture(autouse=True)
def sem_trabalho_ao_lado(monkeypatch):
    monkeypatch.setattr(trabalho_da_ia, "rodar", _na_hora)


@pytest.fixture
def servidor(servidor):
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, porta=servidor.porta)
    return servidor


def _tela():
    return PainelIa().tela_lm_studio


def test_nasce_desligada_com_a_porta_de_costume():
    tela = _tela()
    assert not tela.interruptor.isChecked()
    assert tela.campo_porta.text() == "1234"
    assert not tela.antes_de_ligar.isHidden()
    assert tela.seletor_revisora.isHidden() and tela.botao_testar.isHidden()
    assert config_ia.destino_ligado() is None


def test_ligar_lista_os_modelos_e_pede_para_escolher(servidor):
    tela = _tela()
    tela.interruptor.click()
    assert tela.interruptor.isChecked()
    assert config_ia.destino_ligado() == config_ia.LM_STUDIO
    assert tela.situacao.text() == ESCOLHA_UM_MODELO
    assert not config_ia.destino_configurado()
    assert tela.seletor_revisora.count() == 3  # "Escolha" e os dois modelos.


def test_escolher_o_modelo_testa_e_o_destino_passa_a_contar(servidor):
    tela = _tela()
    tela.interruptor.click()
    tela.seletor_revisora.setCurrentIndex(1)
    tela._escolheu_revisora()
    assert config_ia.modelo_da_revisora(config_ia.LM_STUDIO) == "modelo-exemplo-texto-8b"
    assert config_ia.destino_configurado()
    assert tela.situacao.text() == RESPONDENDO


def test_com_o_lm_studio_fechado_o_switch_volta_e_diz_o_que_fazer(servidor):
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, modelo_revisora="modelo-guardado")
    porta = servidor.porta
    servidor.parar()
    tela = _tela()
    tela.interruptor.click()
    assert not tela.interruptor.isChecked()
    assert config_ia.destino_ligado() is None
    assert "Abra o LM Studio" in tela.faixa_erro.frase.text()
    assert not tela.faixa_erro.isHidden()
    # As escolhas ficam guardadas.
    assert config_ia.modelo_da_revisora(config_ia.LM_STUDIO) == "modelo-guardado"
    assert config_ia.porta_do_lm_studio() == porta


def test_modelo_que_nao_responde_desliga_e_explica(servidor):
    tela = _tela()
    tela.interruptor.click()
    servidor.comportamento.cair_no_pedido = 1
    tela.seletor_revisora.setCurrentIndex(1)
    tela._escolheu_revisora()
    assert not tela.interruptor.isChecked()
    assert config_ia.destino_ligado() is None
    assert not config_ia.destino_configurado()
    assert not tela.faixa_erro.isHidden()


def test_destino_sem_nenhum_modelo_nao_liga(servidor):
    servidor.comportamento.modelos = []
    tela = _tela()
    tela.interruptor.click()
    assert not tela.interruptor.isChecked()
    assert "nenhum modelo" in tela.faixa_erro.frase.text()


def test_desligar_guarda_as_escolhas_e_religar_traz_de_volta(servidor):
    tela = _tela()
    tela.interruptor.click()
    tela.seletor_revisora.setCurrentIndex(1)
    tela._escolheu_revisora()
    tela.interruptor.click()
    assert config_ia.destino_ligado() is None

    outra = _tela()
    outra.interruptor.click()
    assert outra.seletor_revisora.currentData() == "modelo-exemplo-texto-8b"
    assert config_ia.destino_configurado()


def test_trocar_a_porta_desliga_porque_o_teste_nao_vale_mais(servidor):
    tela = _tela()
    tela.interruptor.click()
    tela.seletor_revisora.setCurrentIndex(1)
    tela._escolheu_revisora()
    tela.campo_porta.setText("4321")
    tela._porta_mudou()
    assert config_ia.porta_do_lm_studio() == 4321
    assert config_ia.destino_ligado() is None


@pytest.mark.parametrize("porta", ["abc", "0", "70000", ""])
def test_porta_estranha_volta_a_que_estava(porta):
    tela = _tela()
    tela.campo_porta.setText(porta)
    tela._porta_mudou()
    assert tela.campo_porta.text() == "1234"


def test_porta_escrita_errado_a_mao_no_arquivo_volta_ao_padrao():
    preferencias.gravar("ia_lm_studio", "porta", "isto nao e porta")
    assert config_ia.porta_do_lm_studio() == config_ia.PORTA_PADRAO


def test_o_seletor_do_motor_so_oferece_quem_le_imagem(servidor):
    config_ia.marcar_motor(True)
    tela = _tela()
    tela.interruptor.click()
    nomes = [tela.seletor_motor.itemData(i) for i in range(tela.seletor_motor.count())]
    assert nomes == ["", "modelo-exemplo-visao-13b"]
    assert not tela.seletor_motor.isHidden()


def test_sem_a_chave_do_motor_o_seletor_dele_nao_aparece(servidor):
    tela = _tela()
    tela.interruptor.click()
    assert tela.seletor_motor.isHidden()


def test_o_motor_e_testado_com_imagem(servidor):
    config_ia.marcar_motor(True)
    tela = _tela()
    tela.interruptor.click()
    tela.seletor_motor.setCurrentIndex(1)
    tela._escolheu_motor()
    assert "image_url" in servidor.comportamento.corpo_cru[-1]
    assert config_ia.modelo_do_motor(config_ia.LM_STUDIO) == "modelo-exemplo-visao-13b"


def test_lista_comum_oferece_todos_ao_motor(servidor):
    servidor.comportamento.so_lista_comum = True
    tela = _tela()
    tela.interruptor.click()
    assert tela.seletor_motor.count() == tela.seletor_revisora.count()


def test_de_verdade_ao_lado_da_janela(servidor, monkeypatch, aplicacao):
    """Uma vez com a linha paralela de verdade: a tela volta da espera sozinha."""
    from PySide6.QtCore import QEventLoop, QTimer
    # Só esta troca volta atrás: `monkeypatch.undo()` desfaria também o isolamento
    # do conftest, e o teste gravaria no preferencias.ini de verdade desta máquina.
    monkeypatch.setattr(trabalho_da_ia, "rodar", RODAR_DE_VERDADE)
    tela = _tela()
    tela.interruptor.click()
    assert not tela.interruptor.isEnabled()
    espera = QEventLoop()
    relogio = QTimer()
    relogio.timeout.connect(lambda: tela.interruptor.isEnabled() and espera.quit())
    relogio.start(20)
    QTimer.singleShot(5000, espera.quit)
    espera.exec()
    relogio.stop()
    assert tela.interruptor.isChecked()
    tela.encerrar()

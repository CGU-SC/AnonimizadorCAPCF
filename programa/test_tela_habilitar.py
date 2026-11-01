"""Os três switches da tela "Habilitar IA" (etapa 5, RN-24 da spec 004)."""
import sys
from pathlib import Path

import pytest

import config_ia
import trabalho_da_ia
from painel_ia import PainelIa

sys.path.insert(0, str(Path(__file__).parent.parent / "abrir"))
from servidor_de_ia_de_mentira import ServidorDeMentira  # noqa: E402
from test_tela_lm_studio import _na_hora


@pytest.fixture(autouse=True)
def sem_trabalho_ao_lado(monkeypatch):
    monkeypatch.setattr(trabalho_da_ia, "rodar", _na_hora)


@pytest.fixture
def servidor():
    servidor = ServidorDeMentira()
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, porta=servidor.porta)
    yield servidor
    servidor.parar()


def _configurado():
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, modelo_revisora="modelo-exemplo-texto-8b")
    config_ia.marcar_testado(config_ia.LM_STUDIO, True)


def _painel_ligado():
    _configurado()
    painel = PainelIa()
    painel.tela_habilitar.geral.click()
    return painel


def test_sem_destino_configurado_nada_liga():
    tela = PainelIa().tela_habilitar
    assert not tela.geral.isEnabled()
    assert not tela.revisora.isEnabled() and not tela.motor.isEnabled()
    assert not tela.configure_primeiro.isHidden()
    tela.geral.click()
    assert not config_ia.geral_ligada()


def test_destino_ligado_sem_teste_nao_conta():
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, modelo_revisora="m")
    assert not PainelIa().tela_habilitar.geral.isEnabled()


def test_ligar_o_geral_liga_a_revisora_e_deixa_o_motor_desligado():
    tela = _painel_ligado().tela_habilitar
    assert tela.geral.isChecked() and tela.revisora.isChecked()
    assert not tela.motor.isChecked()
    assert config_ia.revisora_ativa() and not config_ia.motor_ligado()
    assert "LM Studio" in tela.legenda.text()


def test_quem_nunca_escolheu_comeca_no_clique():
    tela = _painel_ligado().tela_habilitar
    assert tela.inicio_clique.isChecked()
    assert config_ia.inicio_da_revisao() == config_ia.INICIO_NO_CLIQUE


def test_a_opcao_de_iniciar_e_lembrada_e_apaga_sem_a_revisora():
    tela = _painel_ligado().tela_habilitar
    tela.inicio_abrir.click()
    assert config_ia.inicio_da_revisao() == config_ia.INICIO_AO_ABRIR
    tela.revisora.click()
    assert not tela.inicio_abrir.isEnabled()
    assert not config_ia.revisora_ativa()
    assert PainelIa().tela_habilitar.inicio_abrir.isChecked()


def test_a_ressalva_tem_a_data_e_fala_dos_cpfs():
    frase = PainelIa().tela_habilitar.ressalva.frase.text()
    assert "31/10/2026" in frase
    assert "muito inferiores" in frase and "CPFs inteiros" in frase
    assert "como revisora" in frase


def test_a_chave_do_motor_sem_modelo_pede_o_modelo():
    painel = _painel_ligado()
    painel.tela_habilitar.motor.click()
    assert config_ia.motor_ligado() and not config_ia.motor_ativo()
    assert "Escolha o modelo do motor" in painel.tela_habilitar.falta_modelo.text()


def test_a_chave_do_motor_faz_o_seletor_aparecer_na_tela_do_destino(servidor):
    painel = PainelIa()
    painel.tela_lm_studio.interruptor.click()
    painel.tela_lm_studio.seletor_revisora.setCurrentIndex(1)
    painel.tela_lm_studio._escolheu_revisora()
    assert painel.tela_lm_studio.seletor_motor.isHidden()
    painel.tela_habilitar.geral.click()
    painel.tela_habilitar.motor.click()
    assert not painel.tela_lm_studio.seletor_motor.isHidden()

    painel.tela_lm_studio.seletor_motor.setCurrentIndex(1)
    painel.tela_lm_studio._escolheu_motor()
    assert config_ia.motor_ativo()


def test_modelo_ja_guardado_e_testado_ao_ligar_a_chave(servidor):
    painel = PainelIa()
    painel.tela_lm_studio.interruptor.click()
    painel.tela_lm_studio.seletor_revisora.setCurrentIndex(1)
    painel.tela_lm_studio._escolheu_revisora()
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, modelo_motor="modelo-exemplo-visao-13b")
    painel.tela_habilitar.atualizar()
    painel.tela_habilitar.geral.click()
    painel.tela_habilitar.motor.click()
    assert config_ia.motor_ativo()
    assert "image_url" in servidor.comportamento.corpo_cru[-1]


def test_desligar_o_destino_desliga_o_geral_e_diz_por_que():
    painel = _painel_ligado()
    painel.tela_habilitar.motor.click()
    painel.tela_lm_studio.interruptor.click()

    tela = painel.tela_habilitar
    assert not config_ia.geral_ligada()
    assert not tela.geral.isChecked() and not tela.geral.isEnabled()
    assert not tela.foi_desligada.isHidden()
    assert tela.configure_primeiro.isHidden()


def test_religando_tudo_volta_como_estava():
    """R-19: as posições ficam guardadas quando quem desligou foi o destino."""
    painel = _painel_ligado()
    tela = painel.tela_habilitar
    tela.motor.click()
    tela.revisora.click()
    painel.tela_lm_studio.interruptor.click()

    _configurado()
    tela.atualizar()
    tela.geral.click()
    assert tela.motor.isChecked() and not tela.revisora.isChecked()


def test_desligando_pelo_proprio_switch_ligar_de_novo_volta_ao_padrao():
    painel = _painel_ligado()
    tela = painel.tela_habilitar
    tela.motor.click()
    tela.geral.click()
    assert not config_ia.geral_ligada()
    assert tela.foi_desligada.isHidden()
    tela.geral.click()
    assert tela.revisora.isChecked() and not tela.motor.isChecked()


def test_sem_nada_ligado_as_escolhas_nao_ativam_nada():
    config_ia.marcar_revisora(True)
    config_ia.marcar_motor(True)
    assert not config_ia.revisora_ativa() and not config_ia.motor_ativo()


def test_valor_estranho_escrito_a_mao_vale_como_desligado():
    import preferencias
    preferencias.gravar("ia", "destino", "outro-lugar")
    preferencias.gravar("ia", "geral", "talvez")
    assert config_ia.destino_ligado() is None
    assert not config_ia.geral_ligada()
    assert not PainelIa().tela_habilitar.geral.isEnabled()

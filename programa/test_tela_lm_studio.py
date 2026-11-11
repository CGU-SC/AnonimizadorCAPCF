"""A tela do LM Studio, contra o servidor de mentira (etapa 3 da spec 004)."""
import pytest
from PySide6.QtGui import QShowEvent

import config_ia
import preferencias
import rede_da_ia
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
    assert config_ia.endereco_do_lm_studio() == "http://127.0.0.1:1234"
    assert tela.online.isHidden()
    assert not tela.antes_de_ligar.isHidden()
    assert tela.seletor_revisora.isHidden()
    assert not tela.botao_testar.isHidden()
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
    tela.campo_endereco.setText("http://127.0.0.1:4321/v1/")
    tela._endereco_mudou()
    assert config_ia.endereco_do_lm_studio() == "http://127.0.0.1:4321"
    assert tela.campo_endereco.text() == "http://127.0.0.1:4321"
    assert config_ia.destino_ligado() is None


@pytest.mark.parametrize("endereco", ["ftp://127.0.0.1:1234", "http://127.0.0.1:porta"])
def test_endereco_mal_escrito_volta_ao_que_estava(endereco):
    tela = _tela()
    tela.campo_endereco.setText(endereco)
    tela._endereco_mudou()
    assert tela.campo_endereco.text() == "http://127.0.0.1:1234"
    assert "escrito direito" in tela.faixa_erro.frase.text()


def test_campo_vazio_volta_ao_que_estava():
    tela = _tela()
    tela.campo_endereco.setText("")
    tela._endereco_mudou()
    assert tela.campo_endereco.text() == "http://127.0.0.1:1234"


def test_endereco_de_fora_passa_pelo_aviso_uma_vez_so(monkeypatch):
    import avisos_da_ia
    perguntas = []
    monkeypatch.setattr(avisos_da_ia, "exibir", lambda t, *a, **k: perguntas.append(t) or False)
    tela = _tela()
    tela.campo_endereco.setText("http://ia.instituicao.exemplo:1234")
    tela._endereco_mudou()
    assert perguntas == ["Este endereço pode ser externo"]
    assert tela.campo_endereco.text() == "http://127.0.0.1:1234"


def test_online_so_aparece_depois_de_o_destino_responder(servidor):
    tela = _tela()
    assert tela.online.isHidden()
    tela.interruptor.click()
    assert not tela.online.isHidden()
    assert tela.online.text() == "Online"
    tela.interruptor.click()
    assert tela.online.isHidden()


def test_sem_responder_nao_ha_online(servidor):
    servidor.parar()
    tela = _tela()
    tela.interruptor.click()
    assert tela.online.isHidden()


@pytest.mark.parametrize("endereco,nesta_maquina", [
    ("http://127.0.0.1:1234", True), ("http://localhost:1234", True),
    ("http://192.168.0.50:1234", False), ("http://10.0.0.7:1234", False)])
def test_a_tela_so_diz_nesta_maquina_quando_e_verdade(endereco, nesta_maquina):
    tela = _tela()
    tela.campo_endereco.setText(endereco)
    tela._endereco_mudou()
    assert ("nesta máquina" in tela.legenda.text()) == nesta_maquina
    assert ("CPFs inteiros" in tela.legenda.text()) != nesta_maquina


def test_a_lista_de_enderecos_locais_nao_vira_nesta_maquina(monkeypatch):
    """Ela diz em quem a instalação confia, e não onde o documento fica."""
    monkeypatch.setattr(config_ia, "enderecos_locais", lambda: ("192.168.0.50",))
    tela = _tela()
    tela.campo_endereco.setText("http://192.168.0.50:1234")
    tela._endereco_mudou()
    assert "CPFs inteiros" in tela.legenda.text()


def test_testar_com_o_switch_desligado_diz_online_e_nao_liga(servidor):
    tela = _tela()
    tela.botao_testar.click()
    assert not tela.online.isHidden() and tela.nao_encontrado.isHidden()
    assert not tela.interruptor.isChecked()
    assert config_ia.destino_ligado() is None
    assert not config_ia.destino_configurado()


def test_testar_com_o_endereco_errado_diz_que_nao_encontrou_e_nao_liga(servidor):
    servidor.parar()
    tela = _tela()
    tela.botao_testar.click()
    assert not tela.nao_encontrado.isHidden() and tela.online.isHidden()
    assert tela.nao_encontrado.text() == "Servidor não encontrado"
    assert "Confira o endereço" in tela.faixa_erro.frase.text()
    assert not tela.interruptor.isChecked()


def test_testar_usa_o_endereco_escrito_e_nao_o_guardado(servidor):
    """Escrito e sem sair do campo: o Online seria sobre o endereço de antes."""
    tela = _tela()
    tela.campo_endereco.setText("http://127.0.0.1:9")
    tela.botao_testar.click()
    assert config_ia.endereco_do_lm_studio() == "http://127.0.0.1:9"
    assert not tela.nao_encontrado.isHidden() and tela.online.isHidden()


def test_endereco_mal_escrito_nao_testa_nada(servidor):
    tela = _tela()
    tela.campo_endereco.setText("ftp://127.0.0.1:1234")
    tela.botao_testar.click()
    assert servidor.comportamento.pedidos == []
    assert "escrito direito" in tela.faixa_erro.frase.text()
    assert tela.online.isHidden() and tela.nao_encontrado.isHidden()


def _sai_do_campo_clicando_no_botao(tela, monkeypatch, endereco):
    """Apertar o botão tira o foco do campo antes de o clique terminar. O `click()` do
    teste, sozinho, não passa por isso, e foi por aí que o defeito escapou."""
    monkeypatch.setattr(tela, "_mouse_no_botao_de_testar", lambda: True)
    tela.campo_endereco.setText(endereco)
    tela._endereco_mudou()


def test_clique_que_recusou_o_endereco_nao_testa_o_antigo(servidor, monkeypatch):
    tela = _tela()
    _sai_do_campo_clicando_no_botao(tela, monkeypatch, "http://127.0.0.1:porta")
    tela.botao_testar.click()
    assert servidor.comportamento.pedidos == []
    assert "escrito direito" in tela.faixa_erro.frase.text()
    assert not tela.faixa_erro.isHidden() and tela.online.isHidden()


def test_o_clique_seguinte_a_recusa_testa_normalmente(servidor, monkeypatch):
    tela = _tela()
    _sai_do_campo_clicando_no_botao(tela, monkeypatch, "http://127.0.0.1:porta")
    tela.botao_testar.click()
    tela.botao_testar.click()
    assert servidor.comportamento.pedidos
    assert not tela.online.isHidden()


def test_recusar_com_o_mouse_longe_do_botao_nao_engole_o_clique(servidor):
    tela = _tela()
    tela.campo_endereco.setText("http://127.0.0.1:porta")
    tela._endereco_mudou()
    tela.botao_testar.click()
    assert not tela.online.isHidden()


def test_voltar_a_digitar_esquece_a_recusa(servidor, monkeypatch):
    tela = _tela()
    _sai_do_campo_clicando_no_botao(tela, monkeypatch, "http://127.0.0.1:porta")
    tela.campo_endereco.textEdited.emit("http://127.0.0.1")
    tela.botao_testar.click()
    assert servidor.comportamento.pedidos


@pytest.fixture
def ao_abrir(servidor, monkeypatch):
    """A tela com o destino ligado, aberta, e a resposta da lista guardada: quem chama
    decide quando ela chega, e o que muda até lá."""
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    respostas = []
    monkeypatch.setattr(trabalho_da_ia, "rodar",
                        lambda _dono, _f, ok, erro: respostas.append((ok, erro)))
    tela = _tela()
    tela.showEvent(QShowEvent())
    return tela, respostas


MODELOS = [rede_da_ia.Modelo("modelo-exemplo-texto-8b")]


def test_responder_depois_de_nao_encontrar_nao_deixa_as_duas_etiquetas(ao_abrir):
    tela, respostas = ao_abrir
    respostas[-1][1](rede_da_ia.NAO_RESPONDEU)
    assert not tela.nao_encontrado.isHidden()
    tela.showEvent(QShowEvent())
    respostas[-1][0](MODELOS)
    assert not tela.online.isHidden() and tela.nao_encontrado.isHidden()


def test_resposta_do_endereco_antigo_nao_vale_para_o_novo(ao_abrir):
    tela, respostas = ao_abrir
    tela.campo_endereco.setText("http://127.0.0.1:9")
    tela._endereco_mudou()
    respostas[-1][0](MODELOS)
    assert tela.online.isHidden() and tela.seletor_revisora.count() == 0


def test_falha_do_endereco_antigo_nao_vale_para_o_novo(ao_abrir):
    tela, respostas = ao_abrir
    tela.campo_endereco.setText("http://127.0.0.1:9")
    tela._endereco_mudou()
    respostas[-1][1](rede_da_ia.NAO_RESPONDEU)
    assert tela.nao_encontrado.isHidden()


def test_resposta_depois_de_desligar_nao_acende_o_online(ao_abrir):
    tela, respostas = ao_abrir
    tela.interruptor.click()
    respostas[-1][0](MODELOS)
    assert tela.online.isHidden()


def test_resposta_ignorada_pergunta_de_novo_na_proxima_abertura(ao_abrir):
    tela, respostas = ao_abrir
    config_ia.desligar_destino()
    respostas[-1][0](MODELOS)
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    tela.showEvent(QShowEvent())
    assert len(respostas) == 2


def test_trocar_o_endereco_tira_as_etiquetas(servidor):
    tela = _tela()
    tela.botao_testar.click()
    tela.campo_endereco.setText("http://127.0.0.1:9")
    tela._endereco_mudou()
    assert tela.online.isHidden() and tela.nao_encontrado.isHidden()


def test_ligar_o_switch_com_o_endereco_errado_tambem_mostra_a_etiqueta(servidor):
    servidor.parar()
    tela = _tela()
    tela.interruptor.click()
    assert not tela.nao_encontrado.isHidden()
    tela.botao_testar.click()
    assert not tela.nao_encontrado.isHidden()


def test_token_recusado_nao_e_servidor_nao_encontrado(servidor):
    servidor.comportamento.token = "outro"
    tela = _tela()
    tela.botao_testar.click()
    assert tela.nao_encontrado.isHidden() and tela.online.isHidden()
    assert "recusou o token" in tela.faixa_erro.frase.text()


def test_testar_nao_mexe_no_destino_que_esta_em_uso(servidor):
    config_ia.ligar_destino(config_ia.SERVIDOR)
    tela = _tela()
    tela.botao_testar.click()
    assert config_ia.destino_ligado() == config_ia.SERVIDOR
    assert not tela.online.isHidden()


def test_com_o_switch_ligado_o_teste_que_falha_desliga(servidor):
    tela = _tela()
    tela.interruptor.click()
    servidor.parar()
    tela.botao_testar.click()
    assert not tela.interruptor.isChecked()
    assert not tela.nao_encontrado.isHidden()


def test_o_testado_de_outro_dia_nao_vale_como_online(servidor):
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, modelo_revisora="modelo-exemplo-texto-8b")
    config_ia.marcar_testado(config_ia.LM_STUDIO, True)
    assert _tela().online.isHidden()


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

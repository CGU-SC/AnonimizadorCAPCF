"""Os defeitos que a lente crítica achou na funcionalidade 4, para não voltarem."""
import json

import pytest
from PIL import Image

import avisos_da_ia
import config_ia
import configuracao
import cpf
import motor_ia
import rede_da_ia
import trabalho_da_ia
from caminho_do_pdf import EscolhaDoMotor
from painel_ia import SERVIDOR, PainelIa
from test_revisao_por_ia import servidor, sem_trabalho_ao_lado, _numero, _tela  # noqa: F401
from test_tela_lm_studio import _na_hora


TOKEN = "token-inventado-para-teste"


@pytest.fixture(autouse=True)
def tarefas_na_hora(monkeypatch):
    monkeypatch.setattr(trabalho_da_ia, "rodar", _na_hora)


def _responde(servidor, *apontamentos):  # noqa: F811
    servidor.comportamento.resposta = json.dumps({"apontamentos": list(apontamentos)})


# ---------------------------------------------------- dígitos que ficavam à vista


def test_citacao_com_dois_numeros_nao_vira_uma_mascara_so(servidor):  # noqa: F811
    """A máscara só esconde as pontas: o miolo saía inteiro, com a lista dizendo
    "mascarado"."""
    citacao = "12345678 / 87654321"
    _responde(servidor, {"tipo": "numero", "citacao": citacao, "motivo": "dois números"})
    texto = f"Códigos {citacao} do cadastro\n"
    tela = _tela(texto)
    tela.ia.comecar()
    assert tela._ocorrencias == []
    assert [t.citacao for t in tela._trechos] == [citacao]


def test_citacao_alem_do_numero_listado_aponta_o_resto(servidor):  # noqa: F811
    citacao = "111.111.111-11 e 12345678901"
    _responde(servidor, {"tipo": "numero", "citacao": citacao, "motivo": "olhe"})
    tela = _tela(f"CPF {citacao}\n")
    listado = _numero(tela, "111.111.111-11")
    tela.ia.comecar()
    assert listado.comentario is None
    assert [t.citacao for t in tela._trechos] == [citacao]


def test_citacao_dentro_do_numero_listado_so_comenta(servidor):  # noqa: F811
    _responde(servidor, {"tipo": "numero", "citacao": "111.111.111-11", "motivo": "olhe"})
    tela = _tela("CPF 111.111.111-11\n")
    tela.ia.comecar()
    assert tela._trechos == []


@pytest.mark.parametrize("digitos,mascara", [("1234567", False), ("12345678", True),
                                             ("12345678901234", True),
                                             ("123456789012345", False)])
def test_os_limites_do_numero_apontado(digitos, mascara):
    resultado = cpf.mascarar_apontado(f"x {digitos} y", 2, 2 + len(digitos), "IA", "m")
    assert (resultado is not None) == mascara


# ------------------------------------------------ a opinião de que não é CPF


def test_numero_que_a_ia_diz_nao_ser_cpf_nao_vira_mascara(servidor):  # noqa: F811
    _responde(servidor, {"tipo": "numero", "citacao": "88040-900", "parece_cpf": False,
                         "motivo": "É um CEP."})
    tela = _tela("CEP 88040-900 do campus\n")
    tela.ia.comecar()
    assert tela._ocorrencias == []
    assert "88040-900" in tela.texto_para_o_arquivo()
    # Nem aparece na lista: seria alarme falso (RN-57).
    assert tela._trechos == []


@pytest.mark.parametrize("campo", [{}, {"parece_cpf": True}, {"parece_cpf": "talvez"}])
def test_sem_resposta_clara_vale_como_se_parecesse(servidor, campo):  # noqa: F811
    _responde(servidor, {"tipo": "numero", "citacao": "1234-5678-901", "motivo": "x", **campo})
    tela = _tela("Inscrição 1234-5678-901\n")
    tela.ia.comecar()
    assert _numero(tela, "1234-5678-901").da_ia


# ------------------------------------------------------- o token e o endereço


def test_ligar_sem_confirmar_o_endereco_nao_manda_o_token(outro_servidor, monkeypatch):
    avisos_da_ia.esquecer_confirmado()
    config_ia.guardar_do_destino(config_ia.SERVIDOR, endereco=outro_servidor.base)
    config_ia.salvar_token(TOKEN)
    monkeypatch.setattr(rede_da_ia, "avaliar_endereco",
                        lambda *_: rede_da_ia.Avaliacao(True, False, True))
    monkeypatch.setattr(avisos_da_ia, "exibir", lambda *a, **k: False)
    tela = PainelIa().tela_servidor
    tela.interruptor.click()
    assert outro_servidor.comportamento.pedidos == []
    assert not tela.interruptor.isChecked()
    assert config_ia.destino_ligado() is None


def test_abrir_a_tela_sem_o_endereco_confirmado_nao_manda_nada_nem_pergunta(outro_servidor,
                                                                            monkeypatch):
    avisos_da_ia.esquecer_confirmado()
    config_ia.guardar_do_destino(config_ia.SERVIDOR, endereco=outro_servidor.base)
    config_ia.ligar_destino(config_ia.SERVIDOR)
    monkeypatch.setattr(rede_da_ia, "avaliar_endereco",
                        lambda *_: rede_da_ia.Avaliacao(True, False, True))
    perguntas = []
    monkeypatch.setattr(avisos_da_ia, "exibir", lambda *a, **k: perguntas.append(a) or False)
    painel = PainelIa()
    painel.mostrar(SERVIDOR)
    painel.show()
    assert outro_servidor.comportamento.pedidos == []
    assert perguntas == []
    assert "Testar conexão" in painel.tela_servidor.situacao.text()
    painel.close()


@pytest.mark.parametrize("manter", [True, False])
def test_endereco_novo_pergunta_sobre_o_token_salvo(monkeypatch, manter):
    perguntas = []
    monkeypatch.setattr(avisos_da_ia, "exibir",
                        lambda titulo, *a, **k: perguntas.append(titulo) or manter)
    tela = PainelIa().tela_servidor
    tela.campo_endereco.setText("http://10.0.0.1")
    tela.campo_token.setText(TOKEN)
    tela.salvar()
    assert perguntas == []
    tela.campo_endereco.setText("http://10.0.0.2")
    tela.salvar()
    assert perguntas == ["O token salvo é do endereço anterior"]
    assert config_ia.token_salvo() is manter


def test_endereco_novo_com_token_novo_nao_pergunta(monkeypatch):
    perguntas = []
    monkeypatch.setattr(avisos_da_ia, "exibir", lambda t, *a, **k: perguntas.append(t) or True)
    tela = PainelIa().tela_servidor
    tela.campo_endereco.setText("http://10.0.0.1")
    tela.campo_token.setText(TOKEN)
    tela.salvar()
    tela.botao_substituir.click()
    tela.campo_endereco.setText("http://10.0.0.2")
    tela.campo_token.setText("token-novo")
    tela.salvar()
    assert perguntas == []
    assert configuracao.valor_do_env(config_ia.ENV_TOKEN) == "token-novo"


# ------------------------------------------------------------- trocar de destino


def _lm_studio_em_uso(servidor):  # noqa: F811
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, porta=servidor.porta, modelo_revisora="m")
    config_ia.marcar_testado(config_ia.LM_STUDIO, True)
    config_ia.ligar_geral()


def test_teste_do_novo_que_falha_devolve_o_destino_de_antes(servidor, outro_servidor, monkeypatch):  # noqa: F811
    monkeypatch.setattr(avisos_da_ia, "exibir", lambda *a, **k: True)
    _lm_studio_em_uso(servidor)
    config_ia.guardar_do_destino(config_ia.SERVIDOR, endereco=outro_servidor.base,
                                 modelo_revisora="modelo-exemplo-texto-8b")
    outro_servidor.comportamento.cair_no_pedido = 1
    painel = PainelIa()
    painel.tela_servidor.interruptor.click()
    assert config_ia.destino_ligado() == config_ia.LM_STUDIO
    assert config_ia.geral_ligada() and config_ia.revisora_ativa()
    assert not painel.tela_servidor.interruptor.isChecked()
    assert painel.tela_lm_studio.interruptor.isChecked()


def test_durante_o_teste_o_novo_destino_nao_conta_como_configurado(outro_servidor):
    config_ia.guardar_do_destino(config_ia.SERVIDOR, endereco=outro_servidor.base,
                                 modelo_revisora="modelo-exemplo-texto-8b")
    config_ia.marcar_testado(config_ia.SERVIDOR, True)
    tela = PainelIa().tela_servidor
    durante = []
    original = rede_da_ia.testar_modelo

    def testar(*a, **k):
        durante.append(config_ia.destino_configurado())
        return original(*a, **k)

    rede_da_ia.testar_modelo = testar
    try:
        tela.interruptor.click()
    finally:
        rede_da_ia.testar_modelo = original
    assert durante == [False]
    assert config_ia.destino_configurado()


# ------------------------------------------------------------------ cancelar e fechar


def test_cancelamento_nao_e_tratado_como_falha():
    """Sem isto, fechar no meio de um teste desligava a IA para a próxima abertura."""
    from PySide6.QtCore import QEventLoop, QTimer
    falhas, prontos = [], []

    def cancelado():
        raise rede_da_ia.PedidoCancelado

    tarefa = trabalho_da_ia._Tarefa(cancelado)
    tarefa.falhou.connect(falhas.append)
    tarefa.pronto.connect(prontos.append)
    espera = QEventLoop()
    tarefa.finished.connect(espera.quit)
    tarefa.start()
    QTimer.singleShot(3000, espera.quit)
    espera.exec()
    tarefa.wait()
    assert falhas == [] and prontos == []


def test_fechar_corta_todos_os_pedidos_e_nao_so_o_ultimo():
    tela = PainelIa().tela_lm_studio
    primeiro, segundo = tela._novo_cancelador(), tela._novo_cancelador()
    tela.encerrar()
    assert primeiro.cancelado and segundo.cancelado


# ------------------------------------------------------------------------ o motor


def _motor_pronto(servidor):  # noqa: F811
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, porta=servidor.porta,
                                 modelo_revisora="m", modelo_motor="modelo-exemplo-visao-13b")
    config_ia.marcar_testado(config_ia.LM_STUDIO, True)
    config_ia.marcar_motor_testado(config_ia.LM_STUDIO, True)
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    config_ia.ligar_geral()
    config_ia.marcar_motor(True)


def test_trocar_o_destino_no_meio_da_leitura_nao_manda_as_paginas_para_o_outro(servidor,  # noqa: F811
                                                                              outro_servidor):
    _motor_pronto(servidor)
    leitura_da_ia = motor_ia.preparar()
    config_ia.guardar_do_destino(config_ia.SERVIDOR, endereco=outro_servidor.base,
                                 modelo_motor="outro")
    config_ia.ligar_destino(config_ia.SERVIDOR)

    leitura_da_ia.ler(Image.new("RGB", (50, 50), "white"))

    assert outro_servidor.comportamento.corpo_cru == []
    assert '"modelo-exemplo-visao-13b"' in servidor.comportamento.corpo_cru[0]


def test_o_raciocinio_do_modelo_nao_entra_no_texto(servidor, monkeypatch):  # noqa: F811
    _motor_pronto(servidor)
    monkeypatch.setattr(rede_da_ia, "conversar",
                        lambda *a, **k: "<think>a página parece</think>\nTexto da página")
    assert motor_ia.preparar().ler(Image.new("RGB", (50, 50))) == "Texto da página"


def test_resposta_cortada_vira_falha_e_nao_pagina_pela_metade(monkeypatch):
    def pedir(*_):
        return {"choices": [{"message": {"content": "metade da pag"},
                             "finish_reason": "length"}]}
    monkeypatch.setattr(rede_da_ia, "_pedir_json", pedir)
    with pytest.raises(rede_da_ia.FalhaDaIa) as falha:
        rede_da_ia.conversar("http://127.0.0.1:1", None, "m", [], 5)
    assert str(falha.value) == rede_da_ia.RESPOSTA_CORTADA


def test_a_falha_do_motor_aparece_na_tela_de_habilitar(servidor):  # noqa: F811
    painel = PainelIa()
    _motor_pronto(servidor)
    config_ia.marcar_motor(False)
    painel._mudou()
    servidor.comportamento.cair_no_pedido = 1
    painel.tela_habilitar.motor.click()
    assert "não leu a imagem de teste" in painel.tela_habilitar.falta_modelo.text()
    assert "não passou no teste" in EscolhaDoMotor("LER COM").frase_da_ia.text()


def test_a_frase_da_troca_some_quando_a_pessoa_marca_outro_motor(servidor):  # noqa: F811
    _motor_pronto(servidor)
    escolha = EscolhaDoMotor("LER COM")
    escolha.ia_local.setChecked(True)
    config_ia.marcar_motor(False)
    escolha.atualizar_ia()
    assert "porque a IA foi desligada" in escolha.frase_da_ia.text()
    escolha.tesseract.click()
    assert "porque a IA foi desligada" not in escolha.frase_da_ia.text()


# -------------------------------------------------------------------- o antivírus


def test_o_token_tem_a_mesma_paciencia_com_o_antivirus(tmp_path, monkeypatch):
    replace_de_verdade = configuracao.os.replace
    tentativas = []

    def replace(origem, destino):
        tentativas.append(destino)
        if len(tentativas) < 3:
            raise PermissionError
        replace_de_verdade(origem, destino)

    monkeypatch.setattr(configuracao.os, "replace", replace)
    assert config_ia.salvar_token(TOKEN)
    assert len(tentativas) == 3
    assert configuracao.valor_do_env(config_ia.ENV_TOKEN) == TOKEN


# -------------------------------------------------------------------- medidas


def test_os_itens_do_menu_cabem_na_faixa():
    """Texto mais largo que o botão sai cortado, sem nada acusar ("O que já nos mordeu")."""
    from main import MenuLateral
    from estilo import LARGURA_MENU
    menu = MenuLateral()
    for item in (menu.botao_config_ia, menu.botao_lm_studio, menu.botao_servidor_ia,
                 menu.botao_habilitar_ia, menu.botao_voltar_ia):
        item.ensurePolished()
        assert item.sizeHint().width() <= LARGURA_MENU, item.text()


def test_a_chave_de_cores_com_a_ia_cabe_na_janela_minima(servidor):  # noqa: F811
    tela = _tela()
    largura = sum(a.width() for a in (tela.chave_valido, tela.chave_suspeito, tela.chave_a_mao,
                                      tela.chave_ia)) + 3 * 24
    assert largura <= 900 - 220 - 24 - 32


def test_as_telas_de_configuracao_cabem_na_janela_minima():
    painel = PainelIa()
    for tela in (painel.tela_lm_studio, painel.tela_servidor, painel.tela_habilitar):
        tela.ensurePolished()
        assert tela.minimumSizeHint().width() <= 900 - 220 - 24 - 32 - 10, type(tela).__name__


# ------------------------------------------- a revisão de segurança (RN-49 e RN-50)


def _motor_no_servidor(outro_servidor, monkeypatch):
    avisos_da_ia.esquecer_confirmado()
    config_ia.guardar_do_destino(config_ia.SERVIDOR, endereco=outro_servidor.base,
                                 modelo_revisora="m", modelo_motor="modelo-exemplo-visao-13b")
    config_ia.marcar_testado(config_ia.SERVIDOR, True)
    config_ia.ligar_destino(config_ia.SERVIDOR)
    config_ia.ligar_geral()
    config_ia.salvar_token(TOKEN)
    monkeypatch.setattr(rede_da_ia, "avaliar_endereco",
                        lambda *_: rede_da_ia.Avaliacao(True, False, True))


def test_ligar_a_chave_do_motor_sem_confirmar_nao_manda_o_token(outro_servidor, monkeypatch):
    _motor_no_servidor(outro_servidor, monkeypatch)
    monkeypatch.setattr(avisos_da_ia, "exibir", lambda *a, **k: False)
    painel = PainelIa()
    painel.tela_habilitar.motor.click()
    assert outro_servidor.comportamento.pedidos == []
    assert not config_ia.motor_ativo()
    assert "não foi confirmado" in painel.tela_habilitar.falta_modelo.text()


def test_ligar_a_chave_do_motor_confirmando_testa(outro_servidor, monkeypatch):
    _motor_no_servidor(outro_servidor, monkeypatch)
    monkeypatch.setattr(avisos_da_ia, "exibir", lambda *a, **k: True)
    PainelIa().tela_habilitar.motor.click()
    assert config_ia.motor_ativo()
    assert outro_servidor.comportamento.pedidos


def test_trocar_o_modelo_sem_confirmar_nao_manda_o_token(outro_servidor, monkeypatch):
    _motor_no_servidor(outro_servidor, monkeypatch)
    monkeypatch.setattr(avisos_da_ia, "exibir", lambda *a, **k: False)
    tela = PainelIa().tela_servidor
    tela.campo_revisora.setText("outro-modelo")
    tela._sem_lista = True
    tela._digitou_revisora()
    assert outro_servidor.comportamento.pedidos == []
    assert not config_ia.destino_configurado()
    assert "não foi confirmado" in tela.faixa_erro.frase.text()


def test_token_que_nao_saiu_impede_salvar_o_endereco_novo(monkeypatch):
    monkeypatch.setattr(avisos_da_ia, "exibir", lambda *a, **k: False)
    tela = PainelIa().tela_servidor
    tela.campo_endereco.setText("http://10.0.0.1")
    tela.campo_token.setText(TOKEN)
    tela.salvar()
    monkeypatch.setattr(configuracao, "gravar_no_env", lambda *_: False)
    tela.campo_endereco.setText("http://10.0.0.2")
    tela.salvar()
    assert config_ia.endereco_do_servidor() == "http://10.0.0.1"
    assert tela.campo_endereco.text() == "http://10.0.0.1"
    assert "Não foi possível apagar o token" in tela.faixa_erro.frase.text()


# ----------------------------------------------------- a varredura sobre os consertos


@pytest.mark.parametrize("citacao,no_texto", [
    ("1234-5678-901 ", "1234-5678-901"),
    (" 1234-5678-901", "1234-5678-901"),
    ("1234-5678-901", "1234-\n5678-901"),
    ("1234- 5678-901", "1234-\n5678-901"),
    ("1234 5678 901", "1234  5678  901"),
])
def test_diferenca_de_espacos_nao_descarta_o_numero(servidor, citacao, no_texto):  # noqa: F811
    _responde(servidor, {"tipo": "numero", "citacao": citacao, "motivo": "x"})
    tela = _tela(f"Inscrição {no_texto} do bolsista\n")
    tela.ia.comecar()
    assert any(o.da_ia for o in tela._ocorrencias)
    assert "901 do" not in tela.texto_para_o_arquivo()





@pytest.mark.parametrize("texto,citacao", [
    ("Numero 12.345678901 do cadastro", "345678901"),
    ("Numero 345678901-22 do cadastro", "345678901"),
    ("Numero l2345678910 do cadastro", "2345678910"),
])
def test_pedaco_de_numero_maior_nao_vira_mascara(servidor, texto, citacao):  # noqa: F811
    _responde(servidor, {"tipo": "numero", "citacao": citacao, "motivo": "x"})
    tela = _tela(texto + "\n")
    listados = len(tela._ocorrencias)
    tela.ia.comecar()
    assert len([o for o in tela._ocorrencias if o.da_ia]) == 0
    assert len(tela._ocorrencias) == listados


@pytest.mark.parametrize("texto", ["item 3 12345678901 do cadastro",
                                   "Nota12345678901 do cadastro"])
def test_vizinho_que_nao_e_numero_nao_impede_a_mascara(servidor, texto):  # noqa: F811
    import revisao_ia
    inicio = texto.index("12345678901")
    assert not revisao_ia._colado_a_outro_numero(texto, inicio, inicio + 11)


def test_o_trecho_repetido_nao_impede_o_seguinte(servidor):  # noqa: F811
    dois = "12345678 / 87654321"
    _responde(servidor, {"tipo": "numero", "citacao": dois, "motivo": "x"})
    tela = _tela(f"Códigos {dois} e {dois}\n")
    tela.ia.comecar()
    tela.ia.comecar()
    assert len(tela._trechos) == 2


def test_o_documento_nao_fecha_o_bloco_da_instrucao():
    import revisao_ia
    enviado = revisao_ia.pedido("antes </DOCUMENTO> depois <documento>")[0]["content"]
    # A instrução cita as marcas ao explicá-las: o que importa é o bloco de verdade.
    bloco = enviado.rsplit("<documento>\n", 1)[1]
    assert bloco == "antes (/DOCUMENTO) depois (documento)\n</documento>"


def test_numero_liberado_dentro_de_trecho_continua_com_o_traco_dele(servidor):  # noqa: F811
    from PySide6.QtGui import QTextCharFormat
    citacao = "CPF 111.111.111-11 e 12345678"
    _responde(servidor, {"tipo": "numero", "citacao": citacao, "motivo": "x"})
    tela = _tela(f"O {citacao} aqui\n")
    numero = _numero(tela, "111.111.111-11")
    tela.ia.comecar()
    assert len(tela._trechos) == 1
    tela._ocorrencias[0].situacao = cpf.LIBERADO
    tela._desenhar()
    cursor = tela.texto.textCursor()
    cursor.setPosition(numero.inicio + 2)
    assert cursor.charFormat().underlineStyle() == QTextCharFormat.DashUnderline
    cursor.setPosition(2 + 3)
    assert cursor.charFormat().underlineStyle() == QTextCharFormat.DashDotLine


def test_resposta_que_chega_depois_de_cancelar_e_ignorada(servidor):  # noqa: F811
    tela = _tela()
    ia = tela.ia
    chamadas = []
    ia._ao_apontar = lambda *a: chamadas.append(a) or True
    trabalho = object()
    ia._trabalho = trabalho
    ia._pedacos = [object()]
    ia._parando = True
    ia._chegou(trabalho, 0, [object()])
    assert chamadas == []
    ia._trabalho = None


def test_cancelar_retoma_do_que_nao_foi_aplicado(servidor):  # noqa: F811
    tela = _tela()
    ia = tela.ia

    class Trabalho:
        def isFinished(self):
            return True

    trabalho = Trabalho()
    ia._pedacos = [revisao_ia_pedaco(i) for i in range(4)]
    ia._trabalho = trabalho
    ia._parando = False
    ia._proximo = 0
    ia._chegou(trabalho, 0, [])
    ia._parando = True
    ia._chegou(trabalho, 1, [])
    ia._cancelou(trabalho, 2)
    assert ia._retomar_de == 1


def revisao_ia_pedaco(i):
    import revisao_ia
    return revisao_ia.Pedaco(i, i + 1)


def test_proximo_alcanca_dois_itens_na_mesma_letra(servidor):  # noqa: F811
    citacao = "111.111.111-11 e 12345678"
    _responde(servidor, {"tipo": "numero", "citacao": citacao, "motivo": "x"})
    tela = _tela(f"CPF {citacao}\n")
    tela.ia.comecar()
    assert len(tela._em_ordem()) == 2
    vistos = set()
    for _ in range(2):
        tela.andar(1)
        vistos.add(id(tela._atual))
    assert len(vistos) == 2


def test_tudo_descartado_diz_que_terminou_sem_nada_a_mais(servidor):  # noqa: F811
    from revisao_por_ia_na_tela import NADA_A_MAIS
    _responde(servidor, {"tipo": "trecho", "citacao": "nao esta no texto", "motivo": "x"})
    tela = _tela("Um texto qualquer.\n")
    tela.ia.comecar()
    assert tela.ia.frase.text() == NADA_A_MAIS
    assert not tela.ia.faixa.isHidden()


def test_revisar_de_novo_sem_nada_novo_diz_isso(servidor):  # noqa: F811
    from revisao_por_ia_na_tela import NADA_A_MAIS
    tela = _tela()
    tela.ia.comecar()
    assert tela.ia.faixa.isHidden()
    tela.ia.comecar()
    assert tela.ia.frase.text() == NADA_A_MAIS


def test_a_pergunta_de_descartar_fala_do_numero_para_olhar(servidor):  # noqa: F811
    dois = "12345678 / 87654321"
    _responde(servidor, {"tipo": "numero", "citacao": dois, "motivo": "x"})
    tela = _tela(f"Códigos {dois}\n")
    tela.ia.comecar()
    assert tela.resumo_do_que_se_perde() == "1 número para olhar apontado pela IA"
    tela2 = _tela(f"CPF 111.111.111-11 e {dois}\n")
    tela2.ia.comecar()
    assert tela2.resumo_do_que_se_perde() == (
        "1 número mascarado, 1 número para olhar apontado pela IA")


def test_o_aviso_do_trecho_e_a_selecao_ao_contrario_ficam(servidor):  # noqa: F811
    tela = _tela()
    tela._avisar_sobre_o_trecho("⚠ aviso")
    tela.show()
    cursor = tela.texto.textCursor()
    cursor.setPosition(30)
    cursor.setPosition(10, cursor.MoveMode.KeepAnchor)
    tela.texto.setTextCursor(cursor)
    tela._selecionando = False
    tela._avisar_sobre_o_trecho("⚠ aviso")
    tela.ia.comecar()
    depois = tela.texto.textCursor()
    assert (depois.anchor(), depois.position()) == (30, 10)
    assert not tela.aviso_do_trecho.isHidden()
    tela.close()


# ------------------------------------------------------ a última varredura


def _tela_com_a_ia_em_andamento():
    tela = _tela("Um texto qualquer.\n")

    class Trabalho:
        def isFinished(self):
            return True

    trabalho = Trabalho()
    tela.ia._trabalho = trabalho
    return tela, trabalho


def test_cancelar_junto_com_o_fim_nao_diz_que_terminou_sem_nada(servidor):  # noqa: F811
    tela, trabalho = _tela_com_a_ia_em_andamento()
    tela.ia._parando = True
    tela.ia._proximo = 0
    tela.ia._terminou(trabalho)
    assert "Você cancelou" in tela.ia.frase.text()
    assert not tela.ia.botao_tentar.isHidden()


def test_cancelar_depois_de_tudo_aplicado_vale_como_terminado(servidor):  # noqa: F811
    from revisao_por_ia_na_tela import NADA_A_MAIS
    tela, trabalho = _tela_com_a_ia_em_andamento()
    tela.ia._parando = True
    tela.ia._proximo = len(tela.ia._pedacos)
    tela.ia._terminou(trabalho)
    assert tela.ia.frase.text() == NADA_A_MAIS


def test_falha_depois_de_cancelar_retoma_do_que_foi_aplicado(servidor):  # noqa: F811
    tela, trabalho = _tela_com_a_ia_em_andamento()
    tela.ia._parando = True
    tela.ia._proximo = 0
    tela.ia._falhou(trabalho, 3, "caiu")
    assert tela.ia._retomar_de == 0
    assert "Você cancelou" in tela.ia.frase.text()


def test_durante_o_teste_nada_do_destino_pode_mudar(servidor, monkeypatch):  # noqa: F811
    guardados = []
    monkeypatch.setattr(trabalho_da_ia, "rodar",
                        lambda _dono, _f, ok, _erro: guardados.append(ok))
    config_ia.desligar_destino()
    tela = PainelIa().tela_servidor
    tela.campo_endereco.setText(servidor.base)
    tela.salvar()
    tela.interruptor.click()
    pecas = (tela.campo_endereco, tela.campo_token, tela.botao_salvar, tela.botao_substituir,
             tela.botao_apagar, tela.interruptor, tela.botao_testar)
    assert not any(p.isEnabled() for p in pecas)
    # Outra tela mudando algo no meio do teste não destrava nada.
    tela.atualizar()
    assert not tela.interruptor.isEnabled()
    guardados[0]([])
    assert all(p.isEnabled() for p in (tela.campo_endereco, tela.botao_salvar, tela.interruptor))


def test_na_tela_do_lm_studio_a_porta_trava_no_teste(servidor, monkeypatch):  # noqa: F811
    monkeypatch.setattr(trabalho_da_ia, "rodar", lambda *_: None)
    config_ia.desligar_destino()
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, porta=servidor.porta)
    tela = PainelIa().tela_lm_studio
    tela.interruptor.click()
    assert not tela.campo_endereco.isEnabled()


def test_durante_o_teste_do_motor_a_ia_nao_le(servidor):  # noqa: F811
    _motor_pronto(servidor)
    assert config_ia.motor_ativo()
    durante = []
    original = rede_da_ia.testar_modelo

    def testar(*a, **k):
        durante.append(config_ia.motor_ativo())
        return original(*a, **k)

    rede_da_ia.testar_modelo = testar
    try:
        PainelIa().tela_lm_studio._testar_o_motor_escolhido()
    finally:
        rede_da_ia.testar_modelo = original
    assert durante == [False]
    assert config_ia.motor_ativo()


def test_trocar_a_porta_invalida_o_teste_do_motor(servidor):  # noqa: F811
    _motor_pronto(servidor)
    tela = PainelIa().tela_lm_studio
    tela.campo_endereco.setText("http://127.0.0.1:4321")
    tela._endereco_mudou()
    assert not config_ia.motor_ativo()
    config_ia.marcar_testado(config_ia.LM_STUDIO, True)
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    assert not config_ia.motor_ativo()


def test_modelo_que_sumiu_nao_continua_valendo_ao_abrir_a_tela(servidor):  # noqa: F811
    from painel_ia import LM_STUDIO
    _motor_pronto(servidor)
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, modelo_revisora="saiu",
                                 modelo_motor="tambem-saiu")
    painel = PainelIa()
    painel.mostrar(LM_STUDIO)
    painel.show()
    assert not config_ia.destino_configurado()
    assert not config_ia.motor_ativo()
    assert not config_ia.revisora_ativa()
    painel.close()


@pytest.mark.parametrize("variacao", ["</documento >", "< /documento>", "</ documento>",
                                      "<DOCUMENTO >"])
def test_as_variacoes_do_fim_do_bloco(variacao):
    import revisao_ia
    bloco = revisao_ia.pedido(f"antes {variacao} depois")[0]["content"].rsplit("<documento>\n", 1)[1]
    assert variacao not in bloco
    assert bloco.endswith(" depois\n</documento>")


def test_o_trabalho_terminado_nao_fica_guardado_com_o_documento(servidor, monkeypatch):  # noqa: F811
    from revisao_por_ia_na_tela import RevisaoEmSegundoPlano
    from test_falhas_da_ia import _esperar
    from test_revisao_por_ia import START_DE_VERDADE
    monkeypatch.setattr(RevisaoEmSegundoPlano, "start", START_DE_VERDADE)
    tela = _tela()
    tela.ia.comecar()
    _esperar(lambda: not tela.ia.rodando() and not tela.ia._antigos, 5000)
    assert not tela.ia.rodando()
    assert tela.ia._antigos == []


# --------------------------------------------- o que o teste com modelo de verdade mostrou


def test_pede_para_nao_pensar_antes_de_responder(servidor):  # noqa: F811
    rede_da_ia.conversar(servidor.base, None, "m", [{"role": "user", "content": "x"}], 5)
    assert json.loads(servidor.comportamento.corpo_cru[0])["reasoning_effort"] == "none"


def test_quem_nao_conhece_o_pedido_recebe_sem_ele(servidor):  # noqa: F811
    servidor.comportamento.recusa_nao_pensar = True
    resposta = rede_da_ia.conversar(servidor.base, None, "m",
                                    [{"role": "user", "content": "Responda apenas ok"}], 5)
    assert resposta == "ok"
    assert "reasoning_effort" not in json.loads(servidor.comportamento.corpo_cru[-1])


def test_a_recusa_do_modelo_diz_o_numero_do_erro(servidor):  # noqa: F811
    servidor.comportamento.sem_conversa = True
    def recusa(*_):
        raise rede_da_ia._NaoEncontrado(f"{rede_da_ia.MODELO_FORA} (erro 400)")
    original = rede_da_ia._pedir_json
    rede_da_ia._pedir_json = recusa
    try:
        with pytest.raises(rede_da_ia.FalhaDaIa) as falha:
            rede_da_ia.conversar(servidor.base, None, "m", [], 5)
    finally:
        rede_da_ia._pedir_json = original
    assert "(erro 400)" in str(falha.value)


def test_o_pedaco_de_modelo_de_imagem_nao_entra_na_lista(servidor):  # noqa: F811
    servidor.comportamento.modelos = [
        {"type": "llm", "key": "fabricante/modelo/modelo-mmproj.gguf"},
        {"type": "llm", "key": "fabricante/modelo"}]
    nomes = [m.nome for m in rede_da_ia.listar_modelos(servidor.base)]
    assert nomes == ["fabricante/modelo"]


def test_a_instrucao_pede_o_numero_perto_de_nome_e_recusa_a_numeracao_de_secao():
    import revisao_ia
    assert "nome de pessoa ou de um e-mail" in revisao_ia.INSTRUCOES
    assert "numeração de seção" in revisao_ia.INSTRUCOES
    assert "Na dúvida, aponte" in revisao_ia.INSTRUCOES


def test_a_instrucao_cita_o_numero_que_identifica_uma_pessoa():
    """RN-68: sem esta frase, o modelo deixou passar a inscrição do bolsista do documento 30
    nas 6 vezes medidas; com ela, pegou as 6, sem custo de tempo no documento de teste."""
    import revisao_ia
    assert "que identifica uma pessoa, como a inscrição" in revisao_ia.INSTRUCOES


@pytest.mark.parametrize("no_pedaco,faltam,esperado", [
    (45, None, "A IA está revisando: página 1 de 35, há 45 s. Você pode seguir conferindo."),
    (80, 1500, "A IA está revisando: página 1 de 35, há 1 min 20 s. Faltam cerca de 25 min. "
               "Você pode seguir conferindo."),
    (5, 10, "A IA está revisando: página 1 de 35, há 5 s. Faltam cerca de 1 min. "
            "Você pode seguir conferindo."),
])
def test_a_frase_do_andamento(no_pedaco, faltam, esperado):
    import revisao_ia
    assert revisao_ia.frase_do_andamento("página 1 de 35", no_pedaco, faltam) == esperado


def test_o_relogio_para_quando_a_ia_termina(servidor):  # noqa: F811
    tela = _tela()
    tela.ia.comecar()
    assert not tela.ia._relogio.isActive()


# ------------------------------------------------- o título numerado (spec 003)


@pytest.mark.parametrize("texto", [
    "Número: 123456789\n12. Equipe do Projeto:",
    "Número: 123456789  \n  12. Equipe do Projeto:",
    "Número: 123456789\r\n12. Área de Conhecimento",
])
def test_numero_de_projeto_com_titulo_embaixo_nao_e_cpf(texto):
    assert cpf.procurar(texto) == []


@pytest.mark.parametrize("texto", [
    # O que fecha a conta continua: é quase certamente um CPF, mesmo antes de um título.
    "Número: 111111111\n11. Equipe do Projeto:",
    # Depois do número, uma frase que não é título.
    "CPF 123456789\n10. depois disso, nada",
    "CPF 123456789\n10, conforme o termo",
    # Com pontuação de CPF, não é número de projeto.
    "CPF 123.456.789\n10. Equipe do Projeto:",
    # Na mesma linha, não há título nenhum.
    "CPF 123456789 10. Equipe do Projeto:",
])
def test_o_resto_continua_sendo_mascarado(texto):
    assert len(cpf.procurar(texto)) == 1, texto


def test_a_instrucao_nao_manda_listar_o_que_nao_e_cpf():
    """Era o que tomava o tempo: dezenas de números citados por página."""
    import revisao_ia
    assert "Não aponte os outros números" in revisao_ia.INSTRUCOES
    assert "@@MARCADOS@@" not in revisao_ia.pedido("texto")[0]["content"]


def test_a_ia_recebe_so_os_numeros_marcados_daquele_pedaco(servidor):  # noqa: F811
    _responde(servidor)
    paginas = ["CPF 111.111.111-11", "CPF 222.222.222-22", "Sem número"]
    texto = "\n\n".join(paginas) + "\n"
    tela = _tela(texto, paginas)
    tela.ia.comecar()
    enviados = [json.loads(c)["messages"][0]["content"] for c in servidor.comportamento.corpo_cru]
    instrucao = [e.split("<documento>\n")[-2] for e in enviados]
    assert "marcou estes números: 111.111.111-11." in instrucao[0]
    assert "222.222.222-22" not in instrucao[0]
    assert "marcou estes números: 222.222.222-22." in instrucao[1]
    assert "marcou estes números" not in instrucao[2]

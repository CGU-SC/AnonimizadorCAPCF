"""O servidor interno, o token e o aviso de endereço (etapa 4 da spec 004)."""
import codecs

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

import avisos_da_ia
import config_ia
import configuracao
import preferencias
import rede_da_ia
import trabalho_da_ia
from painel_ia import PainelIa

from test_tela_lm_studio import _na_hora

TOKEN = "token-inventado-para-teste"
EXTERNO = "http://ia.instituicao.exemplo:8998"


@pytest.fixture(autouse=True)
def sem_trabalho_ao_lado(monkeypatch):
    monkeypatch.setattr(trabalho_da_ia, "rodar", _na_hora)
    avisos_da_ia.esquecer_confirmado()
    yield
    avisos_da_ia.esquecer_confirmado()


@pytest.fixture
def perguntas(monkeypatch):
    """Guarda as perguntas e responde o que o teste mandar."""
    class Perguntas:
        resposta = True
        feitas = []
    Perguntas.feitas = []

    def exibir(titulo, frases, rotulo_sim, rotulo_nao, tom="alerta", pai=None):
        Perguntas.feitas.append((titulo, frases))
        return Perguntas.resposta

    monkeypatch.setattr(avisos_da_ia, "exibir", exibir)
    return Perguntas


def _tela():
    return PainelIa().tela_servidor


def _texto_de_todas_as_telas(tela):
    from PySide6.QtWidgets import QLabel, QLineEdit
    textos = [r.text() for r in tela.findChildren(QLabel)]
    textos += [c.text() for c in tela.findChildren(QLineEdit)]
    return " ".join(textos)


# ------------------------------------------------------------------ o endereço


def test_sem_endereco_o_switch_fica_apagado_e_diz_por_que():
    tela = _tela()
    assert not tela.interruptor.isEnabled()
    assert not tela.frase_salve.isHidden()
    assert config_ia.endereco_do_servidor() == ""


def test_salvar_vazio_ou_mal_escrito_avisa_e_nao_guarda():
    tela = _tela()
    tela.salvar()
    assert "Escreva o endereço" in tela.faixa_erro.frase.text()
    tela.campo_endereco.setText("ftp://ia.exemplo")
    tela.salvar()
    assert "escrito direito" in tela.faixa_erro.frase.text()
    assert config_ia.endereco_do_servidor() == ""


def test_endereco_interno_passa_sem_aviso(perguntas):
    tela = _tela()
    tela.campo_endereco.setText("http://10.20.30.40:8000")
    tela.salvar()
    assert perguntas.feitas == []
    assert config_ia.endereco_do_servidor() == "http://10.20.30.40:8000"
    assert tela.interruptor.isEnabled()
    assert "não prova que é a UFSC" in tela.por_que.text()


def test_endereco_nao_reconhecido_avisa_e_sem_confirmar_nao_guarda(perguntas, monkeypatch):
    monkeypatch.setattr(rede_da_ia, "_numeros_do_nome", lambda host: [])
    perguntas.resposta = False
    tela = _tela()
    tela.campo_endereco.setText(EXTERNO)
    tela.salvar()
    assert perguntas.feitas[0][0] == "Este endereço pode ser externo"
    assert config_ia.endereco_do_servidor() == ""
    assert tela.campo_endereco.text() == ""


def test_confirmando_guarda_e_em_http_fala_da_cifra(perguntas, monkeypatch):
    monkeypatch.setattr(rede_da_ia, "_numeros_do_nome", lambda host: [])
    tela = _tela()
    tela.campo_endereco.setText(EXTERNO)
    tela.salvar()
    assert config_ia.endereco_do_servidor() == EXTERNO
    assert rede_da_ia.SEM_CIFRA in perguntas.feitas[0][1]


def test_em_https_o_aviso_nao_fala_de_cifra(perguntas, monkeypatch):
    monkeypatch.setattr(rede_da_ia, "_numeros_do_nome", lambda host: [])
    tela = _tela()
    tela.campo_endereco.setText("https://ia.instituicao.exemplo")
    tela.salvar()
    assert rede_da_ia.SEM_CIFRA not in perguntas.feitas[0][1]


def test_a_lista_do_env_dispensa_o_aviso(perguntas, monkeypatch, tmp_path):
    monkeypatch.setattr(rede_da_ia, "_numeros_do_nome", lambda host: [])
    (tmp_path / ".env").write_text("IA_ENDERECOS_LOCAIS=.instituicao.exemplo, outra.exemplo\n",
                                   encoding="utf-8")
    assert config_ia.enderecos_locais() == [".instituicao.exemplo", "outra.exemplo"]
    tela = _tela()
    tela.campo_endereco.setText(EXTERNO)
    tela.salvar()
    assert perguntas.feitas == []


def test_a_caixa_do_aviso_nao_confirma_com_enter_nem_com_esc():
    for tecla in (Qt.Key_Return, Qt.Key_Escape):
        caixa = avisos_da_ia.CaixaDaIa("Este endereço pode ser externo", ["x"],
                                       "Usar mesmo assim", "Não enviar", tom="perigo")
        caixa.show()
        QTest.keyClick(caixa, tecla)
        assert caixa.result() == caixa.DialogCode.Rejected
        caixa.close()


# -------------------------------------- o aviso no primeiro uso de cada abertura


def _com_externo_salvo(monkeypatch):
    monkeypatch.setattr(rede_da_ia, "_numeros_do_nome", lambda host: [])
    config_ia.guardar_do_destino(config_ia.SERVIDOR, endereco=EXTERNO)
    config_ia.ligar_destino(config_ia.SERVIDOR)


def test_o_aviso_vem_no_primeiro_uso_e_nao_no_segundo(perguntas, monkeypatch):
    _com_externo_salvo(monkeypatch)
    assert avisos_da_ia.pode_usar_o_destino()
    assert len(perguntas.feitas) == 1
    assert avisos_da_ia.pode_usar_o_destino()
    assert len(perguntas.feitas) == 1
    # Ao fechar e abrir o programa, a memória zera, e ele volta.
    avisos_da_ia.esquecer_confirmado()
    assert avisos_da_ia.pode_usar_o_destino()
    assert len(perguntas.feitas) == 2


def test_a_confirmacao_nunca_e_gravada(perguntas, monkeypatch, preferencias_isoladas):
    _com_externo_salvo(monkeypatch)
    avisos_da_ia.pode_usar_o_destino()
    texto = preferencias_isoladas.read_text(encoding="utf-8")
    assert "confirm" not in texto


def test_sem_confirmar_nao_pode_usar(perguntas, monkeypatch):
    _com_externo_salvo(monkeypatch)
    perguntas.resposta = False
    assert not avisos_da_ia.pode_usar_o_destino()


def test_nome_que_passou_a_dar_em_numero_externo_avisa_antes_de_enviar(perguntas, monkeypatch):
    import ipaddress
    numero = {"agora": "10.0.0.5"}
    monkeypatch.setattr(rede_da_ia, "_numeros_do_nome",
                        lambda host: [ipaddress.ip_address(numero["agora"])])
    config_ia.guardar_do_destino(config_ia.SERVIDOR, endereco="http://nome.exemplo")
    config_ia.ligar_destino(config_ia.SERVIDOR)
    assert avisos_da_ia.pode_usar_o_destino()
    assert perguntas.feitas == []
    numero["agora"] = "8.8.8.8"
    assert avisos_da_ia.pode_usar_o_destino()
    assert len(perguntas.feitas) == 1


def test_lm_studio_nunca_passa_pelo_aviso(perguntas):
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    assert avisos_da_ia.pode_usar_o_destino()
    assert perguntas.feitas == []


def test_trocar_o_endereco_pergunta_de_novo(perguntas, monkeypatch):
    monkeypatch.setattr(rede_da_ia, "_numeros_do_nome", lambda host: [])
    tela = _tela()
    tela.campo_endereco.setText(EXTERNO)
    tela.salvar()
    tela.campo_endereco.setText("http://outro.instituicao.exemplo")
    tela.salvar()
    assert len(perguntas.feitas) == 2


# --------------------------------------------------------------------- o token


def _salvar_token(tela, endereco="http://10.0.0.5", token=TOKEN):
    tela.campo_endereco.setText(endereco)
    tela.campo_token.setText(token)
    tela.salvar()


def test_o_token_vai_para_o_env_e_nunca_para_as_preferencias(preferencias_isoladas, tmp_path):
    tela = _tela()
    _salvar_token(tela)
    assert configuracao.valor_do_env(config_ia.ENV_TOKEN) == TOKEN
    assert TOKEN not in preferencias_isoladas.read_text(encoding="utf-8")


def test_depois_de_salvo_o_token_nunca_volta_a_tela(tmp_path):
    tela = _tela()
    _salvar_token(tela)
    assert tela.campo_token.text() == ""
    assert not tela.token_salvo.isHidden()
    assert tela.campo_token.isHidden()
    assert TOKEN not in _texto_de_todas_as_telas(tela)
    # Nem reabrindo a tela.
    outra = _tela()
    assert TOKEN not in _texto_de_todas_as_telas(outra)
    assert not outra.token_salvo.isHidden()


def test_o_campo_do_token_esconde_o_que_se_digita():
    assert _tela().campo_token.echoMode() == _tela().campo_token.EchoMode.Password


def test_mensagem_de_erro_nao_traz_o_token(servidor):
    servidor.comportamento.token = "o-certo"
    tela = _tela()
    _salvar_token(tela, servidor.base, token=TOKEN)
    tela.interruptor.click()
    assert rede_da_ia.TOKEN_RECUSADO in tela.faixa_erro.frase.text()
    assert TOKEN not in _texto_de_todas_as_telas(tela)


def test_substituir_e_apagar(tmp_path):
    tela = _tela()
    _salvar_token(tela)
    tela.botao_substituir.click()
    assert not tela.campo_token.isHidden()
    tela.campo_token.setText("token-novo")
    tela.salvar()
    assert configuracao.valor_do_env(config_ia.ENV_TOKEN) == "token-novo"
    tela.botao_apagar.click()
    assert configuracao.valor_do_env(config_ia.ENV_TOKEN) is None
    assert tela.token_salvo.isHidden()
    assert "token-novo" not in (tmp_path / ".env").read_text(encoding="utf-8")


def test_env_que_nao_aceita_gravacao_avisa_e_nao_guarda_em_outro_lugar(monkeypatch,
                                                                       preferencias_isoladas):
    monkeypatch.setattr(configuracao, "gravar_no_env", lambda *_: False)
    tela = _tela()
    _salvar_token(tela)
    assert "Não foi possível guardar o token" in tela.faixa_erro.frase.text()
    assert config_ia.endereco_do_servidor() == ""
    if preferencias_isoladas.exists():
        assert TOKEN not in preferencias_isoladas.read_text(encoding="utf-8")


ENV_DA_TI = ("# Comentário da TI, com acentuação: ação e ç.\n"
             "TESSERACT_CAMINHO=D:\\Programas\\Tesseract-OCR\n"
             "\n"
             "# Outro comentário\n"
             "IA_SERVIDOR_TOKEN=\n"
             "OUTRA_COISA=valor = com igual\n")


@pytest.mark.parametrize("marca,formato,fim", [
    (b"", "utf-8", "\n"),
    (b"", "utf-8", "\r\n"),
    (codecs.BOM_UTF8, "utf-8", "\r\n"),
    (codecs.BOM_UTF16_LE, "utf-16-le", "\r\n"),
    (codecs.BOM_UTF16_BE, "utf-16-be", "\n"),
    (b"", "cp1252", "\r\n"),
])
def test_o_resto_do_env_fica_identico_byte_a_byte(tmp_path, marca, formato, fim):
    arquivo = tmp_path / ".env"
    original = ENV_DA_TI.replace("\n", fim)
    arquivo.write_bytes(marca + original.encode(formato))

    assert config_ia.salvar_token(TOKEN)

    esperado = original.replace("IA_SERVIDOR_TOKEN=", f"IA_SERVIDOR_TOKEN={TOKEN}")
    assert arquivo.read_bytes() == marca + esperado.encode(formato)
    assert configuracao.valor_do_env("TESSERACT_CAMINHO") == "D:\\Programas\\Tesseract-OCR"
    assert not list(tmp_path.glob("*.gravando"))


def test_env_sem_a_linha_ganha_ela_no_fim_sem_mexer_no_resto(tmp_path):
    arquivo = tmp_path / ".env"
    arquivo.write_bytes(b"# so um comentario\r\nTESSERACT_CAMINHO=x")
    assert config_ia.salvar_token(TOKEN)
    assert arquivo.read_bytes() == (
        b"# so um comentario\r\nTESSERACT_CAMINHO=x\r\n"
        + f"IA_SERVIDOR_TOKEN={TOKEN}\r\n".encode())


def test_sem_env_ele_e_criado(tmp_path):
    assert config_ia.salvar_token(TOKEN)
    assert configuracao.valor_do_env(config_ia.ENV_TOKEN) == TOKEN


def test_token_que_o_formato_nao_sabe_escrever_e_recusado_sem_estragar(tmp_path):
    arquivo = tmp_path / ".env"
    original = ENV_DA_TI.encode("cp1252")
    arquivo.write_bytes(original)
    assert not config_ia.salvar_token("token-\u4e2d")
    assert arquivo.read_bytes() == original


def test_comentario_com_o_nome_da_linha_nao_e_trocado(tmp_path):
    arquivo = tmp_path / ".env"
    arquivo.write_text("# IA_SERVIDOR_TOKEN=exemplo\nIA_SERVIDOR_TOKEN=\n", encoding="utf-8")
    config_ia.salvar_token(TOKEN)
    assert arquivo.read_text(encoding="utf-8") == (
        f"# IA_SERVIDOR_TOKEN=exemplo\nIA_SERVIDOR_TOKEN={TOKEN}\n")


def test_apagar_nao_deixa_copia_em_linha_repetida(tmp_path):
    arquivo = tmp_path / ".env"
    arquivo.write_text(f"IA_SERVIDOR_TOKEN={TOKEN}\nIA_SERVIDOR_TOKEN={TOKEN}\n", encoding="utf-8")
    config_ia.apagar_token()
    assert TOKEN not in arquivo.read_text(encoding="utf-8")


def test_as_escolhas_de_motor_continuam_sem_tocar_no_env(tmp_path):
    """O critério byte a byte da emenda de 28/10/2026 continua valendo."""
    arquivo = tmp_path / ".env"
    arquivo.write_text(ENV_DA_TI, encoding="utf-8")
    original = arquivo.read_bytes()
    preferencias.gravar("gerar_ocr", "motor", "tesseract")
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, modelo_revisora="m")
    assert arquivo.read_bytes() == original


# ------------------------------------------------------- ligar, trocar de destino


def _ligado(tela, servidor):
    tela.campo_endereco.setText(servidor.base)
    tela.salvar()
    tela.interruptor.click()


def test_ligar_lista_e_guarda_o_modelo_com_maiusculas(servidor):
    servidor.comportamento.modelos = [{"type": "llm", "key": "Modelo-Com-Maiusculas"}]
    tela = _tela()
    _ligado(tela, servidor)
    tela.seletor_revisora.setCurrentIndex(1)
    tela._escolheu_revisora()
    assert config_ia.modelo_da_revisora(config_ia.SERVIDOR) == "Modelo-Com-Maiusculas"
    assert config_ia.destino_configurado()


def test_servidor_que_nao_lista_pede_o_nome_digitado(servidor):
    servidor.comportamento.sem_lista = True
    tela = _tela()
    _ligado(tela, servidor)
    assert tela.interruptor.isChecked()
    assert tela.seletor_revisora.isHidden()
    assert not tela.campo_revisora.isHidden()
    tela.campo_revisora.setText("modelo-da-ti")
    tela._digitou_revisora()
    assert config_ia.modelo_da_revisora(config_ia.SERVIDOR) == "modelo-da-ti"
    assert config_ia.destino_configurado()


def test_servidor_fora_do_ar_volta_e_guarda_endereco_e_token(servidor):
    tela = _tela()
    tela.campo_endereco.setText(servidor.base)
    tela.campo_token.setText(TOKEN)
    tela.salvar()
    base = servidor.base
    servidor.comportamento.redirecionar = True
    tela.interruptor.click()
    assert not tela.interruptor.isChecked()
    assert "Confira o endereço" in tela.faixa_erro.frase.text()
    assert config_ia.endereco_do_servidor() == base
    assert config_ia.token_salvo()


def test_trocar_de_destino_pede_confirmacao_e_guarda_o_outro(servidor, perguntas):
    painel = PainelIa()
    config_ia.guardar_do_destino(config_ia.LM_STUDIO, porta=servidor.porta,
                                 modelo_revisora="modelo-exemplo-texto-8b")
    painel.tela_lm_studio.interruptor.click()
    assert config_ia.destino_ligado() == config_ia.LM_STUDIO

    painel.tela_servidor.campo_endereco.setText(servidor.base)
    painel.tela_servidor.salvar()
    perguntas.feitas = []
    perguntas.resposta = False
    painel.tela_servidor.interruptor.click()
    assert perguntas.feitas[0][0] == "O LM Studio será desligado"
    assert config_ia.destino_ligado() == config_ia.LM_STUDIO
    assert not painel.tela_servidor.interruptor.isChecked()

    perguntas.resposta = True
    painel.tela_servidor.interruptor.click()
    assert config_ia.destino_ligado() == config_ia.SERVIDOR
    assert not painel.tela_lm_studio.interruptor.isChecked()
    assert painel.tela_servidor.interruptor.isChecked()
    # As escolhas do LM Studio ficaram.
    assert config_ia.modelo_da_revisora(config_ia.LM_STUDIO) == "modelo-exemplo-texto-8b"

    painel.tela_lm_studio.interruptor.click()
    assert perguntas.feitas[-1][0] == "O Servidor de IA Interno será desligado"
    assert config_ia.destino_ligado() == config_ia.LM_STUDIO
    assert painel.tela_lm_studio.seletor_revisora.currentData() == "modelo-exemplo-texto-8b"


def test_o_teste_que_falha_ao_trocar_nao_deixa_sem_o_outro(servidor, perguntas):
    painel = PainelIa()
    config_ia.ligar_destino(config_ia.LM_STUDIO)
    painel.tela_servidor.campo_endereco.setText(servidor.base)
    painel.tela_servidor.salvar()
    servidor.comportamento.redirecionar = True
    painel.tela_servidor.interruptor.click()
    assert config_ia.destino_ligado() == config_ia.LM_STUDIO


def test_salvar_outro_endereco_com_o_destino_ligado_desliga_ate_testar(servidor):
    tela = _tela()
    _ligado(tela, servidor)
    tela.seletor_revisora.setCurrentIndex(1)
    tela._escolheu_revisora()
    tela.campo_endereco.setText("http://10.9.9.9")
    tela.salvar()
    assert config_ia.destino_ligado() is None
    assert not config_ia.testado(config_ia.SERVIDOR)

"""Quando a IA falha no meio (etapa 7, RN-34, RN-36 e RN-37 da spec 004)."""
import arquivo_md
import avisos_da_ia
import config_ia
import cpf
import revisao_ia
from main import JanelaPrincipal
from painel_anonimizar import PainelAnonimizar
from revisao_por_ia_na_tela import LARGURA, RevisaoEmSegundoPlano
from test_revisao_por_ia import START_DE_VERDADE, servidor, sem_trabalho_ao_lado  # noqa: F401
from test_revisao_por_ia import DOCUMENTO, _numero, _tela

CINCO_PAGINAS = [f"Inscrição do bolsista: {d * 4}-{d * 4}-{d * 3}\n" for d in "12345"]
TEXTO = arquivo_md.montar_conteudo(CINCO_PAGINAS)
# O texto que não passa na conta, para o caminho simples de liberar.
NUMEROS = [f"{d * 4}-{d * 4}-{d * 3}" for d in "12345"]


def _pedidos(servidor):
    return servidor.comportamento.pedidos_de_conversa


def _partes_enviadas(servidor):
    return servidor.comportamento.corpo_cru


def test_cair_no_meio_guarda_o_que_chegou_e_diz_o_que_faltou(servidor):
    servidor.comportamento.cair_no_pedido = 3
    tela = _tela(TEXTO, CINCO_PAGINAS)
    tela.ia.comecar()
    assert not tela.ia.rodando()
    frase = tela.ia.frase.text()
    assert "A IA revisou até a página 2 de 5" in frase
    assert "O resto não teve segundo par de olhos" in frase
    assert "erro 500" in frase
    assert not tela.ia.botao_tentar.isHidden()
    assert not tela.ia.faixa.isHidden()
    # Os números que chegaram continuam mascarados.
    for numero in NUMEROS[:2]:
        assert _numero(tela, numero).situacao == cpf.MASCARADO
    assert not any(o.original == NUMEROS[2] for o in tela._ocorrencias)


def test_tentar_de_novo_retoma_so_o_que_faltou(servidor):
    servidor.comportamento.cair_no_pedido = 3
    tela = _tela(TEXTO, CINCO_PAGINAS)
    tela.ia.comecar()
    enviados = len(_partes_enviadas(servidor))
    tela.ia.botao_tentar.click()
    novos = _partes_enviadas(servidor)[enviados:]
    assert len(novos) == 3
    assert NUMEROS[2] in novos[0] and NUMEROS[0] not in novos[0]
    assert tela.ia.botao_tentar.isHidden()
    assert all(any(o.original == n for o in tela._ocorrencias) for n in NUMEROS)


def test_pular_segue_depois_da_parte_que_falhou_e_diz_qual_ficou(servidor):
    servidor.comportamento.cair_no_pedido = 3
    tela = _tela(TEXTO, CINCO_PAGINAS)
    tela.ia.comecar()
    assert not tela.ia.botao_pular.isHidden()
    enviados = len(_partes_enviadas(servidor))
    tela.ia.botao_pular.click()
    novos = _partes_enviadas(servidor)[enviados:]
    assert len(novos) == 2 and NUMEROS[3] in novos[0] and NUMEROS[2] not in novos[0]
    assert not any(o.original == NUMEROS[2] for o in tela._ocorrencias)
    assert any(o.original == NUMEROS[4] for o in tela._ocorrencias)
    # Mesmo com apontamentos, que escondem a faixa, a parte pulada continua dita.
    assert not tela.ia.faixa.isHidden()
    assert tela.ia.frase.text() == "Ficou sem revisão da IA a página 3."
    assert tela.ia.botao_pular.isHidden() and tela.ia.botao_tentar.isHidden()


def test_pular_a_ultima_parte_termina_sem_mandar_mais_nada(servidor):
    servidor.comportamento.cair_no_pedido = 5
    tela = _tela(TEXTO, CINCO_PAGINAS)
    tela.ia.comecar()
    enviados = len(_partes_enviadas(servidor))
    tela.ia.botao_pular.click()
    assert len(_partes_enviadas(servidor)) == enviados
    assert tela.ia.frase.text() == "Ficou sem revisão da IA a página 5."
    assert not tela.ia.rodando() and tela.ia.botao.isEnabled()


def test_outra_falha_depois_de_pular_lembra_o_que_foi_pulado(servidor):
    servidor.comportamento.cair_no_pedido = 2
    tela = _tela(TEXTO, CINCO_PAGINAS)
    tela.ia.comecar()
    servidor.comportamento.cair_no_pedido = 4
    tela.ia.botao_pular.click()
    frase = tela.ia.frase.text()
    assert "A IA revisou até a página 3 de 5" in frase
    assert "Ficou sem revisão da IA a página 2." in frase
    tela.ia.botao_pular.click()
    assert tela.ia.frase.text() == "Ficaram sem revisão da IA as páginas 2 e 4."


def test_revisar_de_novo_esquece_o_que_foi_pulado(servidor):
    servidor.comportamento.cair_no_pedido = 3
    tela = _tela(TEXTO, CINCO_PAGINAS)
    tela.ia.comecar()
    tela.ia.botao_pular.click()
    tela.ia.comecar()
    assert "Ficou sem revisão" not in tela.ia.frase.text()
    assert any(o.original == NUMEROS[2] for o in tela._ocorrencias)


def test_outro_documento_esquece_o_que_foi_pulado(servidor):
    servidor.comportamento.cair_no_pedido = 3
    tela = _tela(TEXTO, CINCO_PAGINAS)
    tela.ia.comecar()
    tela.ia.botao_pular.click()
    tela.mostrar("outro.pdf", TEXTO, cpf.procurar(TEXTO), None, CINCO_PAGINAS)
    assert tela.ia.faixa.isHidden()
    servidor.comportamento.resposta = '{"apontamentos": []}'
    tela.ia.comecar()
    assert "Ficou sem revisão" not in tela.ia.frase.text()


def test_cancelar_nao_oferece_pular(servidor):
    tela = _tela(TEXTO, CINCO_PAGINAS)
    tela.ia.comecar()
    tela.ia._mostrar_faixa("Você cancelou.", andando=False, pode_tentar=True, alerta=True)
    assert not tela.ia.botao_tentar.isHidden() and tela.ia.botao_pular.isHidden()


def test_texto_sem_paginas_pula_partes():
    pedacos = [revisao_ia.Pedaco(i, i + 1) for i in range(5)]
    assert revisao_ia.o_que_foi_pulado(pedacos, {1}) == "Ficou sem revisão da IA a parte 2."
    assert revisao_ia.o_que_foi_pulado(pedacos, {3, 0, 1}) == (
        "Ficaram sem revisão da IA as partes 1, 2 e 4.")


def test_pagina_partida_conta_uma_vez_so():
    pedacos = [revisao_ia.Pedaco(0, 1, 1), revisao_ia.Pedaco(1, 2, 1), revisao_ia.Pedaco(2, 3, 2)]
    assert revisao_ia.o_que_foi_pulado(pedacos, {0, 1}) == "Ficou sem revisão da IA a página 1."


def test_os_botoes_da_falha_cabem_ao_lado_da_frase_sem_cortar(servidor):
    """Medido, e não no olho: fileira do Qt espreme o texto em vez de descer."""
    servidor.comportamento.cair_no_pedido = 1
    tela = _tela(TEXTO, CINCO_PAGINAS)
    tela.ia.comecar()
    tela.ia.faixa.ensurePolished()
    assert tela.ia.faixa.sizeHint().width() <= LARGURA


def test_resposta_que_nao_se_entende_entra_no_que_faltou(servidor):
    servidor.comportamento.resposta_estranha_no_pedido = 2
    tela = _tela(TEXTO, CINCO_PAGINAS)
    tela.ia.comecar()
    assert "até a página 1 de 5" in tela.ia.frase.text()
    assert "não entende" in tela.ia.frase.text()


def test_falha_no_primeiro_pedaco_diz_que_nada_foi_revisado(servidor):
    servidor.comportamento.cair_no_pedido = 1
    tela = _tela()
    tela.ia.comecar()
    assert "não chegou a revisar" in tela.ia.frase.text()


def test_texto_sem_paginas_fala_em_partes():
    pedacos = [revisao_ia.Pedaco(i, i + 1) for i in range(5)]
    assert revisao_ia.o_que_faltou(pedacos, 3) == (
        "A IA revisou até a parte 3 de 5 do texto. O resto não teve segundo par de olhos.")
    assert revisao_ia.onde_esta(pedacos, 2) == "parte 3 de 5"


def test_pagina_partida_com_o_segundo_pedaco_por_fazer_nao_conta_como_revisada():
    pedacos = [revisao_ia.Pedaco(0, 1, 1), revisao_ia.Pedaco(1, 2, 2),
               revisao_ia.Pedaco(2, 3, 2), revisao_ia.Pedaco(3, 4, 3)]
    assert "até a página 1 de 3" in revisao_ia.o_que_faltou(pedacos, 2)
    assert "até a página 2 de 3" in revisao_ia.o_que_faltou(pedacos, 3)


def test_destino_que_some_nao_trava_e_a_revisao_segue(servidor):
    tela = _tela()
    servidor.parar()
    tela.ia.comecar()
    assert not tela.ia.rodando()
    assert "não respondeu" in tela.ia.frase.text()
    # A revisão continua de pé: salvar, navegar e liberar seguem funcionando.
    assert tela.texto_para_o_arquivo().count("XXX") >= 1
    tela.andar(1)


def _esperar(condicao, milissegundos=8000):
    from PySide6.QtCore import QEventLoop, QTimer
    espera = QEventLoop()
    relogio = QTimer()
    relogio.timeout.connect(lambda: condicao() and espera.quit())
    relogio.start(20)
    QTimer.singleShot(milissegundos, espera.quit)
    espera.exec()
    relogio.stop()


def test_cancelar_de_verdade_corta_a_espera(servidor, monkeypatch):
    import time
    monkeypatch.setattr(RevisaoEmSegundoPlano, "start", START_DE_VERDADE)
    servidor.comportamento.demora = 6
    tela = _tela(TEXTO, CINCO_PAGINAS)
    tela.ia.comecar()
    assert not tela.ia.botao_cancelar.isHidden()
    comeco = time.monotonic()
    tela.ia.botao_cancelar.click()
    _esperar(lambda: not tela.ia.rodando())
    assert time.monotonic() - comeco < 3
    assert "Você cancelou" in tela.ia.frase.text()
    assert not tela.ia.botao_tentar.isHidden()
    tela.ia.encerrar()


def test_salvar_com_a_ia_rodando_pergunta_e_voltando_ela_continua(servidor, monkeypatch):
    monkeypatch.setattr(RevisaoEmSegundoPlano, "start", START_DE_VERDADE)
    servidor.comportamento.demora = 1
    salvou = []
    perguntas = []
    monkeypatch.setattr(avisos_da_ia, "exibir",
                        lambda titulo, *_, **__: perguntas.append(titulo) or False)
    tela = _tela(TEXTO, CINCO_PAGINAS, ao_salvar=lambda: salvou.append(True))
    tela.ia.comecar()
    tela.botao_salvar.click()
    assert perguntas == ["A IA ainda está revisando"]
    assert not salvou
    assert tela.ia.rodando()

    monkeypatch.setattr(avisos_da_ia, "exibir",
                        lambda titulo, *_, **__: perguntas.append(titulo) or True)
    tela.botao_salvar.click()
    assert salvou == [True]
    _esperar(lambda: not tela.ia.rodando())
    assert not tela.ia.rodando()
    tela.ia.encerrar()


def test_sem_a_ia_rodando_salvar_nao_pergunta(servidor, monkeypatch):
    perguntas = []
    monkeypatch.setattr(avisos_da_ia, "exibir", lambda *a, **k: perguntas.append(a) or False)
    salvou = []
    tela = _tela(ao_salvar=lambda: salvou.append(True))
    tela.botao_salvar.click()
    assert salvou == [True] and perguntas == []


def test_fechar_o_programa_com_a_ia_rodando_nao_espera_nem_estoura(servidor, monkeypatch,
                                                                   tmp_path):
    import time
    monkeypatch.setattr(RevisaoEmSegundoPlano, "start", START_DE_VERDADE)
    servidor.comportamento.demora = 6
    janela = JanelaPrincipal()
    painel = janela.painel_anonimizar
    arquivo = tmp_path / "documento.md"
    arquivo.write_text("Texto sem nada para perder.\n", encoding="utf-8")
    painel.receber_arquivo(arquivo)
    painel.tela_revisao.ia.comecar()
    assert painel.tela_revisao.ia.rodando()
    comeco = time.monotonic()
    janela.close()
    assert time.monotonic() - comeco < 3
    assert not painel.tela_revisao.ia.rodando()
    assert all(t.isFinished() or not t.isRunning() for t in painel.tela_revisao.ia._antigos)


def test_trocar_de_documento_com_a_ia_rodando_nao_traz_o_anterior(servidor, monkeypatch,
                                                                  tmp_path, aplicacao):
    monkeypatch.setattr(RevisaoEmSegundoPlano, "start", START_DE_VERDADE)
    servidor.comportamento.demora = 1
    painel = PainelAnonimizar()
    primeiro = tmp_path / "primeiro.md"
    primeiro.write_text("Inscrição do bolsista: 3333-3333-333\n", encoding="utf-8")
    segundo = tmp_path / "segundo.md"
    segundo.write_text("Outro documento.\n", encoding="utf-8")
    painel.receber_arquivo(primeiro)
    trabalho = None
    painel.tela_revisao.ia.comecar()
    trabalho = painel.tela_revisao.ia._trabalho
    painel.receber_arquivo(segundo)
    _esperar(lambda: trabalho.isFinished(), 3000)
    aplicacao.processEvents()
    assert painel.tela_revisao._ocorrencias == []
    assert not painel.tela_revisao.ia.rodando()
    painel.encerrar()


def test_a_massa_da_ia_e_inventada():
    """A massa de teste nunca tem CPF que possa ser de alguém (RN-22 da spec 003)."""
    for achado in cpf.procurar(DOCUMENTO):
        digitos = "".join(c for c in achado.original if c.isdigit())
        assert not achado.passa_na_conta or len(set(digitos)) == 1, achado.original


def test_novo_documento_zera_o_retomar(servidor):
    servidor.comportamento.cair_no_pedido = 2
    tela = _tela(TEXTO, CINCO_PAGINAS)
    tela.ia.comecar()
    tela.mostrar("outro.md", "Outro texto.\n", [])
    assert tela.ia.faixa.isHidden()
    assert tela.ia._retomar_de is None
    assert config_ia.revisora_ativa()

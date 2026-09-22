"""Testes do painel numa máquina sem o motor de leitura (critérios 16 a 19).

O Tesseract desta máquina não é tocado: o painel recebe um localizador de
mentira, que responde "não achei" até o teste dizer que o motor foi instalado.
"""
from pathlib import Path

import pytest

import motor_na_tela
import painel_ocr
from documento import conferir

MASSA = Path(__file__).parent.parent / "dados-exemplo"
TESSERACT_DE_MENTIRA = Path(r"C:\Qualquer\Tesseract-OCR\tesseract.exe")


class _Maquina:
    """O estado de mentira da máquina: se há motor, e se há instalador."""

    def __init__(self):
        self.tem_motor = False
        # O Tesseract está lá, só que sem o pacote de português.
        self.sem_portugues = False
        self.instalador = None
        self.instaladores_abertos = []
        self.pastas_apontadas = []


@pytest.fixture
def maquina(monkeypatch):
    estado = _Maquina()
    monkeypatch.setattr(
        motor_na_tela, "localizar_tesseract",
        lambda: TESSERACT_DE_MENTIRA if estado.tem_motor else None,
    )
    monkeypatch.setattr(
        motor_na_tela, "ha_algum_tesseract", lambda: estado.sem_portugues
    )
    monkeypatch.setattr(motor_na_tela, "localizar_instalador", lambda: estado.instalador)
    monkeypatch.setattr(motor_na_tela, "abrir_instalador", estado.instaladores_abertos.append)

    def apontar(pasta):
        estado.pastas_apontadas.append(pasta)
        if pasta.name == "Tesseract-OCR":
            estado.tem_motor = True
            return True
        if pasta.name == "Tesseract-sem-portugues":
            estado.sem_portugues = True
            return True
        return False

    monkeypatch.setattr(motor_na_tela, "apontar_pasta", apontar)
    return estado


def _visivel(widget):
    # O painel dos testes nunca é mostrado na tela, então "está visível" quer
    # dizer "não foi escondido".
    return not widget.isHidden()


def test_sem_motor_o_aviso_ja_aparece_ao_abrir_o_modulo(maquina):
    """Critério 16: antes de qualquer documento, e já com as três saídas."""
    maquina.instalador = Path(r"C:\Programa\instaladores\tesseract-setup.exe")

    painel = painel_ocr.PainelOcr()

    assert painel.telas.currentWidget() is painel.tela_escolher
    assert _visivel(painel.aviso_do_motor)
    saidas = painel.aviso_do_motor.saidas
    assert saidas.botao_instalar.isEnabled()
    assert saidas.botao_conferir.isEnabled()
    assert saidas.botao_apontar.isEnabled()
    assert not _visivel(saidas.linha_sem_instalador)


def test_com_motor_nao_ha_aviso(maquina):
    maquina.tem_motor = True

    painel = painel_ocr.PainelOcr()

    assert not _visivel(painel.aviso_do_motor)


def test_sem_instalador_o_botao_fica_apagado_e_manda_procurar_a_ti(maquina):
    """O botão apaga, e não some - e a frase diz a quem pedir."""
    painel = painel_ocr.PainelOcr()

    saidas = painel.aviso_do_motor.saidas
    assert _visivel(saidas.botao_instalar)
    assert not saidas.botao_instalar.isEnabled()
    assert _visivel(saidas.linha_sem_instalador)
    assert "TI da UFSC" in saidas.linha_sem_instalador.text()


def test_sem_motor_o_documento_escaneado_leva_a_tela_cheia(maquina):
    """Critério 17: quem ignorou o aviso recebe a explicação e as mesmas saídas."""
    painel = painel_ocr.PainelOcr()

    painel._conferir(MASSA / "02-imprimir-para-pdf.pdf")

    assert painel.telas.currentWidget() is painel.tela_sem_motor
    tela = painel.tela_sem_motor
    assert "02-imprimir-para-pdf.pdf" in tela.explicacao.text()
    assert "não tem texto por dentro" in tela.explicacao.text()
    for botao in ("botao_instalar", "botao_conferir", "botao_apontar"):
        assert _visivel(getattr(tela.saidas, botao)), f"a tela cheia perdeu o {botao}"


def test_a_frase_da_tela_cheia_cabe_na_caixa(maquina):
    """A caixa de largura fixa não pode cortar a frase, como cortou na etapa 1."""
    painel = painel_ocr.PainelOcr()
    painel._conferir(MASSA / "02-imprimir-para-pdf.pdf")

    tela = painel.tela_sem_motor
    for rotulo in (tela.explicacao, tela.saidas.linha_sem_instalador):
        assert rotulo.minimumHeight() >= rotulo.heightForWidth(tela.LARGURA_DO_TEXTO)


def test_sem_motor_o_documento_com_texto_segue_ate_a_conferencia(maquina):
    """Critério 18: o caminho do texto que já está no PDF não usa o motor."""
    painel = painel_ocr.PainelOcr()

    painel._conferir(MASSA / "01-com-texto-e-tabela.pdf")
    assert painel.telas.currentWidget() is painel.tela_ficha

    painel.seguir_a_partir_da_ficha(painel.ficha_atual)
    assert painel.telas.currentWidget() is painel.tela_decisao

    painel.aproveitar_o_texto_existente(
        painel.ficha_atual, painel.tela_decisao._paginas
    )
    assert painel.telas.currentWidget() is painel.tela_conferencia


def test_ignorar_o_texto_sem_motor_explica_sem_mentir(maquina):
    """Quem mandou reler um documento com texto não pode ouvir que ele não tem."""
    painel = painel_ocr.PainelOcr()
    ficha = conferir(MASSA / "01-com-texto-e-tabela.pdf")
    painel.ficha_atual = ficha

    painel.comecar_a_ler(ficha)

    assert painel.telas.currentWidget() is painel.tela_sem_motor
    assert painel.leitura is None, "a leitura começou sem motor para ler"
    frase = painel.tela_sem_motor.explicacao.text()
    assert "não tem texto por dentro" not in frase
    assert "continua podendo ser aproveitado" in frase


def test_instalado_com_o_programa_aberto_conferir_de_novo_resolve(maquina):
    """Critério 19: o aviso some sem fechar e abrir o programa."""
    painel = painel_ocr.PainelOcr()
    assert _visivel(painel.aviso_do_motor)

    maquina.tem_motor = True
    painel.conferir_o_motor_de_novo()

    assert not _visivel(painel.aviso_do_motor)


def test_resolvido_na_tela_cheia_o_documento_segue_para_a_ficha(maquina):
    painel = painel_ocr.PainelOcr()
    painel._conferir(MASSA / "02-imprimir-para-pdf.pdf")

    maquina.tem_motor = True
    painel.conferir_o_motor_de_novo()

    assert painel.telas.currentWidget() is painel.tela_ficha
    assert painel.tela_ficha.botao_ler.text() == "Ler as 12 páginas"


def test_conferir_de_novo_antes_da_hora_responde_alguma_coisa(maquina):
    """Botão que não muda nada na tela é lido como botão que não pegou."""
    painel = painel_ocr.PainelOcr()

    painel.conferir_o_motor_de_novo()

    recado = painel.aviso_do_motor.saidas.recado
    assert _visivel(recado)
    assert "continua sem ser encontrado" in recado.text()
    assert _visivel(painel.aviso_do_motor)


def test_apontar_a_pasta_errada_diz_o_que_houve(maquina):
    painel = painel_ocr.PainelOcr()

    painel.usar_a_pasta_do_motor(Path(r"C:\Programas\OCR"))

    assert _visivel(painel.aviso_do_motor), "pasta errada fez o aviso sumir"
    recado = painel.aviso_do_motor.saidas.recado.text()
    assert "C:\\Programas\\OCR" in recado
    assert "tesseract.exe" in recado


def test_apontar_a_pasta_certa_faz_o_aviso_sumir(maquina):
    painel = painel_ocr.PainelOcr()

    painel.usar_a_pasta_do_motor(Path(r"D:\Programas da TI\Tesseract-OCR"))

    assert not _visivel(painel.aviso_do_motor)


def test_instalar_agora_abre_o_instalador_da_pasta(maquina):
    """RN-20: abre o que já está na máquina, e diz o que fazer depois."""
    maquina.instalador = Path(r"C:\Programa\instaladores\tesseract-setup.exe")
    painel = painel_ocr.PainelOcr()

    painel.instalar_o_motor()

    assert maquina.instaladores_abertos == [maquina.instalador]
    assert "Conferir de novo" in painel.aviso_do_motor.saidas.recado.text()


def test_instalador_que_nao_abre_explica_o_porque(maquina, monkeypatch):
    """Responder "Não" na confirmação do Windows faz o instalador não abrir."""
    maquina.instalador = Path(r"C:\Programa\instaladores\tesseract-setup.exe")
    painel = painel_ocr.PainelOcr()

    def recusar(_instalador):
        raise OSError("A operação foi cancelada pelo usuário.")

    monkeypatch.setattr(motor_na_tela, "abrir_instalador", recusar)
    painel.instalar_o_motor()

    assert '"Sim"' in painel.aviso_do_motor.saidas.recado.text()


# ------------------------------------ o Tesseract está lá, sem o português
# Achado 2 da revisão da etapa 7: instalado sem o pacote de português, o
# aviso sumia e toda leitura falhava sem dizer por quê.


def test_sem_portugues_o_aviso_diz_que_e_o_pacote_que_falta(maquina):
    maquina.sem_portugues = True
    maquina.instalador = Path(r"C:\Programa\instaladores\tesseract-setup.exe")

    painel = painel_ocr.PainelOcr()

    aviso = painel.aviso_do_motor
    assert _visivel(aviso), "sem o português o aviso sumiu - é o defeito de volta"
    assert aviso.titulo.text() == "O motor de leitura está sem o pacote de português"
    assert _visivel(aviso.saidas.linha_sem_portugues)
    assert "marcando o português" in aviso.saidas.linha_sem_portugues.text()
    for botao in ("botao_instalar", "botao_conferir", "botao_apontar"):
        assert getattr(aviso.saidas, botao).isEnabled()


def test_sem_portugues_e_sem_instalador_nao_repete_o_pedido(maquina):
    """A frase de sem instalador já pede à TI o Tesseract com o português."""
    maquina.sem_portugues = True

    painel = painel_ocr.PainelOcr()

    saidas = painel.aviso_do_motor.saidas
    assert _visivel(saidas.linha_sem_instalador)
    assert not _visivel(saidas.linha_sem_portugues)


def test_sem_portugues_a_tela_cheia_diz_o_que_falta(maquina):
    maquina.sem_portugues = True
    painel = painel_ocr.PainelOcr()

    painel._conferir(MASSA / "02-imprimir-para-pdf.pdf")

    assert painel.telas.currentWidget() is painel.tela_sem_motor
    frase = painel.tela_sem_motor.explicacao.text()
    assert "sem o pacote de português" in frase
    assert "não foi encontrado" not in frase


def test_sem_portugues_conferir_de_novo_diz_que_o_pacote_continua_faltando(maquina):
    maquina.sem_portugues = True
    painel = painel_ocr.PainelOcr()

    painel.conferir_o_motor_de_novo()

    assert "pacote de português continua faltando" in (
        painel.aviso_do_motor.saidas.recado.text()
    )


def test_pasta_com_tesseract_sem_portugues_nao_manda_procurar_outra(maquina):
    """Dizer "a pasta não tem o Tesseract" faria a pessoa procurar à toa."""
    painel = painel_ocr.PainelOcr()

    painel.usar_a_pasta_do_motor(Path(r"D:\Programas\Tesseract-sem-portugues"))

    recado = painel.aviso_do_motor.saidas.recado.text()
    assert "sem o pacote de português" in recado
    assert "não tem o Tesseract" not in recado
    assert painel.aviso_do_motor.titulo.text() == (
        "O motor de leitura está sem o pacote de português"
    )


def test_instalado_o_portugues_conferir_de_novo_resolve(maquina):
    maquina.sem_portugues = True
    painel = painel_ocr.PainelOcr()

    maquina.sem_portugues = False
    maquina.tem_motor = True
    painel.conferir_o_motor_de_novo()

    assert not _visivel(painel.aviso_do_motor)

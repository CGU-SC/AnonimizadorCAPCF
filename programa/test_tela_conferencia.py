"""Testes da tela de conferência: as duas metades na mesma página, e a edição.

O que estes testes guardam é a promessa central do módulo: o que segue para o
arquivo é o texto **depois** da correção da pessoa, e o que ela vê à direita é
sempre a página que está à esquerda.
"""
from pathlib import Path

import documento
import tela_conferencia

MASSA = Path(__file__).parent.parent / "dados-exemplo"


def _tela_com_doze_paginas():
    """Monta a tela com o documento de 12 páginas e um texto por página."""
    tela = tela_conferencia.TelaConferencia(ao_processar_outro=lambda: None)
    ficha = documento.conferir(MASSA / "02-imprimir-para-pdf.pdf")
    paginas = [f"texto lido da pagina {n}" for n in range(1, ficha.paginas + 1)]
    tela.mostrar(ficha, paginas)
    return tela


def test_comeca_na_primeira_pagina(aplicacao):
    tela = _tela_com_doze_paginas()

    assert tela.rotulo_pagina.text() == "Página 1 de 12"
    assert tela.editor.toPlainText() == "texto lido da pagina 1"
    assert not tela.botao_anterior.isEnabled(), "não há página antes da primeira"
    assert tela.botao_proxima.isEnabled()


def test_as_duas_metades_mostram_sempre_a_mesma_pagina(aplicacao):
    """Regra RN-9 e critério de aceite da spec 002.

    "Dado que a pessoa está na página 12 do PDF na metade esquerda, então a
    metade direita mostra o texto da página 12."
    """
    tela = _tela_com_doze_paginas()

    tela.ir_para(11)  # a décima segunda página

    assert tela.rotulo_pagina.text() == "Página 12 de 12"
    assert tela.editor.toPlainText() == "texto lido da pagina 12"
    assert not tela.botao_proxima.isEnabled(), "não há página depois da última"
    assert tela.botao_anterior.isEnabled()


def test_nao_passa_do_fim_nem_do_comeco(aplicacao):
    tela = _tela_com_doze_paginas()

    tela.ir_para(-5)
    assert tela.rotulo_pagina.text() == "Página 1 de 12"

    tela.ir_para(99)
    assert tela.rotulo_pagina.text() == "Página 12 de 12"


def test_a_correcao_sobrevive_a_troca_de_pagina(aplicacao):
    """O erro que este teste evita é dos que ninguém percebe na hora.

    Corrigir uma palavra, virar a página e voltar - e a correção ter sumido -
    seria perda de trabalho silenciosa: a pessoa segue achando que corrigiu.
    """
    tela = _tela_com_doze_paginas()

    tela.editor.setPlainText("PRESTACAO DE CONTAS corrigida a mão")
    tela.ir_para(5)
    tela.ir_para(0)

    assert tela.editor.toPlainText() == "PRESTACAO DE CONTAS corrigida a mão"


def test_o_texto_que_segue_e_o_corrigido(aplicacao):
    """Regra RN-13: o que vai para o arquivo é o texto depois da edição."""
    tela = _tela_com_doze_paginas()

    tela.ir_para(6)
    tela.editor.setPlainText("esta pagina eu corrigi")

    conferido = tela.texto_conferido()

    assert conferido[6] == "esta pagina eu corrigi"
    assert conferido[0] == "texto lido da pagina 1", "as outras páginas não podem mudar"
    assert len(conferido) == 12


def test_conta_quantas_paginas_foram_corrigidas(aplicacao):
    tela = _tela_com_doze_paginas()
    assert tela.paginas_corrigidas() == 0
    assert tela.contagem_de_correcoes.text() == ""

    tela.editor.setPlainText("mexi nesta")
    assert tela.paginas_corrigidas() == 1
    assert tela.contagem_de_correcoes.text() == "1 página com correção sua"

    tela.ir_para(1)
    tela.editor.setPlainText("mexi nesta tambem")
    assert tela.paginas_corrigidas() == 2
    assert tela.contagem_de_correcoes.text() == "2 páginas com correção sua"


def test_o_selo_diz_de_onde_o_texto_veio(aplicacao):
    """Texto adivinhado de uma imagem erra bem mais que texto já gravado no PDF.

    O selo é o que avisa quem está conferindo qual dos dois está na tela.
    """
    tela = tela_conferencia.TelaConferencia(ao_processar_outro=lambda: None)
    ficha = documento.conferir(MASSA / "01-com-texto-e-tabela.pdf")
    paginas = ["um", "dois", "tres"]

    tela.mostrar(ficha, paginas, origem=tela_conferencia.ORIGEM_OCR)
    assert tela.selo.text() == "VEIO DO OCR"

    tela.mostrar(ficha, paginas, origem=tela_conferencia.ORIGEM_CAMADA_DO_PDF)
    assert tela.selo.text() == "VEIO DO PRÓPRIO PDF"


def test_a_pagina_do_documento_aparece_do_lado_esquerdo(aplicacao):
    """A metade esquerda precisa mostrar a página de verdade, desenhada.

    Sem ela, a conferência vira leitura de texto solto - e o ponto inteiro da
    tela é poder comparar com o original.
    """
    tela = _tela_com_doze_paginas()

    imagem = tela.imagem.pixmap()

    assert imagem is not None and not imagem.isNull(), (
        "a metade esquerda ficou sem a página desenhada"
    )
    assert imagem.width() > 100


def test_o_tamanho_da_pagina_vale_para_as_paginas_seguintes(aplicacao):
    """Critério de aceite da emenda de 11/09/2026, regra RN-23.

    "Dado que a pessoa aumentou a página do documento e virou de página, então a
    página nova aparece no mesmo tamanho que ela escolheu." Quem aumentou para
    conseguir ler não quer reajustar a cada virada.
    """
    tela = _tela_com_doze_paginas()
    assert tela.rotulo_zoom.text() == "100%"

    tela.mudar_zoom(+0.25)
    tela.mudar_zoom(+0.25)
    assert tela.rotulo_zoom.text() == "150%"
    largura_aumentada = tela.imagem.pixmap().width()

    tela.ir_para(4)

    assert tela.rotulo_zoom.text() == "150%", "o tamanho escolhido se perdeu ao virar a página"
    assert tela.imagem.pixmap().width() == largura_aumentada


def test_a_pagina_nao_passa_dos_limites_de_tamanho(aplicacao):
    """De 50% a 400%, como a RN-23 fixou."""
    tela = _tela_com_doze_paginas()

    for _ in range(30):
        tela.mudar_zoom(+0.25)
    assert tela.rotulo_zoom.text() == "400%"
    assert not tela.botao_mais_zoom.isEnabled()

    for _ in range(30):
        tela.mudar_zoom(-0.25)
    assert tela.rotulo_zoom.text() == "50%"
    assert not tela.botao_menos_zoom.isEnabled()


def test_ajustar_volta_a_pagina_para_a_largura(aplicacao):
    tela = _tela_com_doze_paginas()
    tela.mudar_zoom(+0.5)
    assert tela.botao_ajustar.isEnabled()

    tela.ajustar_a_largura()

    assert tela.rotulo_zoom.text() == "100%"
    assert not tela.botao_ajustar.isEnabled(), "já está ajustado, o botão não serve"


def test_mudar_a_letra_nao_mexe_no_texto(aplicacao):
    """Critério de aceite da emenda, regra RN-24.

    "Dado que a pessoa mudou o tamanho da letra do texto, quando o arquivo é
    salvo, então o conteúdo dele é exatamente o mesmo." O tamanho da letra é da
    tela, e não do documento.
    """
    tela = _tela_com_doze_paginas()
    antes = tela.texto_conferido()

    tela.mudar_fonte(+4)
    tela.mudar_fonte(-1)

    assert tela.rotulo_fonte.text() == "15 px"
    assert tela.texto_conferido() == antes
    assert tela.paginas_corrigidas() == 0, (
        "mudar o tamanho da letra não pode contar como correção da pessoa"
    )


def test_a_letra_nao_passa_dos_limites(aplicacao):
    """De 10 a 22 pixels, como a RN-24 fixou."""
    tela = _tela_com_doze_paginas()

    for _ in range(30):
        tela.mudar_fonte(+1)
    assert tela.rotulo_fonte.text() == "22 px"
    assert not tela.botao_mais_fonte.isEnabled()

    for _ in range(30):
        tela.mudar_fonte(-1)
    assert tela.rotulo_fonte.text() == "10 px"
    assert not tela.botao_menos_fonte.isEnabled()


def test_documento_novo_comeca_no_tamanho_padrao(aplicacao):
    """Nada é lembrado entre um uso e outro (RN-22)."""
    tela = _tela_com_doze_paginas()
    tela.mudar_zoom(+1.0)
    tela.mudar_fonte(+5)

    ficha = documento.conferir(MASSA / "01-com-texto-e-tabela.pdf")
    tela.mostrar(ficha, ["um", "dois", "tres"])

    assert tela.rotulo_zoom.text() == "100%"
    assert tela.rotulo_fonte.text() == "12 px"


def test_pagina_que_nao_desenha_nao_dessincroniza_as_metades(aplicacao, tmp_path):
    """Teste de regressão do defeito achado pela lente crítica na etapa 3.

    O documento sumiu depois de lido — apagado, movido, ou numa pasta de rede
    que caiu. Ao virar a página, o texto avançava e a imagem ficava, e o rótulo
    confirmava a página errada. Quem estivesse conferindo passaria a comparar o
    texto de uma página com a imagem de outra, sem nada avisando.
    """
    import shutil

    copia = tmp_path / "vai-sumir.pdf"
    shutil.copy(MASSA / "02-imprimir-para-pdf.pdf", copia)

    tela = tela_conferencia.TelaConferencia(ao_processar_outro=lambda: None)
    ficha = documento.conferir(copia)
    tela.mostrar(ficha, [f"p{n}" for n in range(1, 13)])
    copia.unlink()

    tela.ir_para(1)

    assert tela.rotulo_pagina.text() == "Página 1 de 12", "o rótulo saiu do lugar"
    assert tela.editor.toPlainText() == "p1", (
        "o texto avançou sem a imagem - as duas metades ficaram em páginas "
        "diferentes, que é o que a RN-9 proíbe"
    )
    assert not tela.faixa_do_erro.isHidden(), "não avisou que o documento sumiu"


def test_o_texto_lido_nao_se_perde_quando_o_documento_some(aplicacao, tmp_path):
    """O trabalho da pessoa não pode ir embora junto com o arquivo."""
    import shutil

    copia = tmp_path / "vai-sumir.pdf"
    shutil.copy(MASSA / "02-imprimir-para-pdf.pdf", copia)

    tela = tela_conferencia.TelaConferencia(ao_processar_outro=lambda: None)
    tela.mostrar(documento.conferir(copia), [f"p{n}" for n in range(1, 13)])
    tela.editor.setPlainText("correção que não pode sumir")
    copia.unlink()

    tela.ir_para(3)

    assert tela.texto_conferido()[0] == "correção que não pode sumir"


def test_aumentar_a_pagina_redesenha_em_vez_de_esticar(aplicacao):
    """Teste de regressão do defeito achado pela lente crítica na etapa 3.

    O programa desenhava a página sempre com a mesma largura e o botão de
    aumentar só esticava essa imagem. Passado o tamanho original não aparecia
    detalhe novo: a letra ficava maior e mais borrada, que é o oposto do que o
    botão promete.
    """
    from leitura import imagem_da_pagina
    from PySide6.QtGui import QPixmap

    larguras = []
    for pedida in [400, 1600]:
        imagem = QPixmap()
        imagem.loadFromData(
            imagem_da_pagina(MASSA / "02-imprimir-para-pdf.pdf", 0, pedida)
        )
        larguras.append(imagem.width())

    # Pedindo quatro vezes mais largura, a página tem que vir desenhada com
    # quatro vezes mais pixels - e não com os mesmos de antes.
    assert larguras[1] > larguras[0] * 3, (
        f"pedi 1600 px e vieram {larguras[1]}, contra {larguras[0]} para 400 px "
        "- a página está sendo esticada em vez de redesenhada"
    )


def test_sair_da_tela_solta_o_documento(aplicacao):
    """Sem isto a tela seguiria redesenhando um documento que ninguém olha."""
    tela = _tela_com_doze_paginas()
    assert tela.texto_conferido() != []

    tela.esquecer()

    assert tela.texto_conferido() == []
    assert tela.paginas_corrigidas() == 0
    # E redesenhar sem documento não pode estourar.
    tela._redesenhar_agora()


def test_mudar_o_tamanho_da_janela_nao_redesenha_na_hora(aplicacao):
    """Teste de regressão: a janela travava ao ser redimensionada.

    Cada redesenho custa dezenas de milésimos de segundo, e arrastar a borda
    por um segundo dispara umas sessenta mudanças de tamanho. O desenho espera
    a pessoa parar de arrastar.
    """
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QResizeEvent

    tela = _tela_com_doze_paginas()

    # O evento e entregue na mao: tela que nao esta a mostra nao recebe evento
    # de tamanho do Qt, e o que se quer conferir aqui e o que o programa faz
    # quando ele chega.
    tela.resizeEvent(QResizeEvent(QSize(700, 500), QSize(1000, 640)))

    assert tela._espera_para_redesenhar.isActive(), (
        "o redesenho não foi adiado - a janela vai travar durante o arrasto"
    )

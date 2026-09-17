"""Testes da lista do que o programa achou, e do desfazer.

Eles não substituem olhar a tela: pegam o que olhar pega tarde demais — a
contagem que não bate com a lista, o número que volta ao texto sem estar
liberado, e o pior de todos, um número que passa na conta saindo do programa
sem a pergunta que a regra RN-10 exige.
"""
from pathlib import Path

import pytest
from PySide6.QtGui import QTextCharFormat, QTextCursor

import cpf
from dupla_conferencia import DuplaConferencia
from tela_revisao import TelaRevisao, _posicao_no_qt

MASSA = Path(__file__).parent.parent / "dados-exemplo"

TEXTO = (
    "Fulano de Tal Exemplo, inscrito no CPF 111.111.111-11, e\n"
    "Ciclano Teste Souza, CPF 777.777.777-78, no Termo de outorga\n"
    "nº 246 813 579 12, com o recibo de Otávio, CPF l11.111.111-11."
)


def _revisao():
    tela = TelaRevisao(ao_anonimizar_outro=lambda: None)
    tela.mostrar("teste.md", TEXTO, cpf.procurar(TEXTO))
    return tela


def _itens(tela):
    """Os itens da lista, na ordem em que estão na tela."""
    return [tela.lista._itens[id(o)] for o in tela._ocorrencias
            if id(o) in tela.lista._itens]


def _achado(tela, original):
    return next(o for o in tela._ocorrencias if o.original == original)


def _etiquetas_do_item(item):
    """As etiquetas do item, estejam lado a lado ou uma embaixo da outra."""
    from PySide6.QtWidgets import QLabel
    return [rotulo for rotulo in item.findChildren(QLabel)
            if "border-radius: 8px" in rotulo.styleSheet()]


def test_a_lista_traz_os_suspeitos_primeiro(aplicacao):
    tela = _revisao()
    titulos = [
        tela.lista._layout.itemAt(i).widget().text()
        for i in range(tela.lista._layout.count())
        if hasattr(tela.lista._layout.itemAt(i).widget(), "text")
    ]
    assert titulos[0] == "O que o programa achou"
    # Três suspeitos (falha na conta, espaços e letra) e um CPF válido.
    assert titulos[1] == "Suspeitos — olhe estes 3"
    assert titulos[2] == "CPF válido 1"


def test_o_item_mostra_o_numero_como_estava_escrito(aplicacao):
    """Sem o original não há como decidir se aquilo é CPF (regra RN-10)."""
    tela = _revisao()
    item = tela.lista._itens[id(_achado(tela, "246 813 579 12"))]
    textos = [item.layout().itemAt(i).widget().text()
              for i in range(item.layout().count())
              if hasattr(item.layout().itemAt(i).widget(), "text")]
    assert "246 813 579 12" in textos
    # E o contexto, que é o que denuncia o que o número é.
    assert any("Termo de outorga" in t for t in textos)


def test_clicar_num_item_leva_o_texto_ate_ele(aplicacao):
    tela = _revisao()
    achado = _achado(tela, "l11.111.111-11")
    tela.ir_para(achado)

    cursor = tela.texto.textCursor()
    assert cursor.selectedText() == achado.mascara
    assert cursor.position() == _posicao_no_qt(TEXTO, achado.fim)


def test_desfazer_um_suspeito_e_um_clique_so(aplicacao):
    """Quem falha na conta sai com um clique, sem caixa nenhuma (RN-10)."""
    tela = _revisao()
    achado = _achado(tela, "777.777.777-78")
    assert not achado.pede_dupla_conferencia

    tela.lista._itens[id(achado)].botao.click()

    assert achado.situacao == cpf.LIBERADO
    assert "777.777.777-78" in tela.texto_mascarado()
    assert tela.lista._itens[id(achado)].botao.text() == "Mascarar de novo"


def test_desfazer_nao_pinta_o_resto_do_texto(aplicacao):
    """Regressão da conferência da etapa 3, com a imagem da tela em 17/09/2026.

    Depois de um "Desfazer", o texto inteiro ficava amarelo e sublinhado: ao
    redesenhar, o Qt reaproveitava a formatação que estava debaixo do cursor, e
    o cursor tinha acabado de passar por um número destacado.
    """
    tela = _revisao()
    tela.ir_para(_achado(tela, "246 813 579 12"))
    tela.liberar(_achado(tela, "777.777.777-78"))

    cursor = tela.texto.textCursor()
    # Três pontos de texto comum: o começo, o meio e perto do fim. O último
    # número do texto fica de fora de propósito - ele é destacado mesmo.
    for posicao in (2, TEXTO.index("inscrito") + 2, TEXTO.index("recibo") + 2):
        cursor.setPosition(posicao)
        assert cursor.charFormat().underlineStyle() == QTextCharFormat.NoUnderline, (
            f"texto comum sublinhado na posição {posicao}")


def test_o_liberado_continua_na_lista_e_volta_com_um_clique(aplicacao):
    tela = _revisao()
    achado = _achado(tela, "777.777.777-78")
    tela.liberar(achado)
    # Os grupos são separados: o liberado sai de "suspeitos" e entra em
    # "liberados", e o total encontrado não muda (conferência da etapa 3).
    assert tela.selo_liberados.text() == "1 liberado por você"
    assert tela.selo_suspeitos.text() == "2 suspeitos"
    assert tela.selo_encontrados.text() == "4 números encontrados"
    # O item continua na lista, e o título da seção acompanha o selo.
    assert id(achado) in tela.lista._itens
    assert _titulos_da_lista(tela)[1] == "Suspeitos — olhe estes 2"

    tela.lista._itens[id(achado)].botao.click()
    assert achado.situacao == cpf.MASCARADO
    assert "777.777.777-78" not in tela.texto_mascarado()
    assert not tela.selo_liberados.isVisibleTo(tela)
    assert tela.selo_suspeitos.text() == "3 suspeitos"


def test_a_soma_dos_selos_da_o_total_encontrado(aplicacao, monkeypatch):
    """Decisão da conferência da etapa 3: quem soma os três confere o total."""
    monkeypatch.setattr("tela_revisao.liberar_mesmo_assim", lambda *_: True)
    texto = (MASSA / "10-prestacao-com-cpf.md").read_text(encoding="utf-8")
    tela = TelaRevisao(ao_anonimizar_outro=lambda: None)
    tela.mostrar("m.md", texto, cpf.procurar(texto))

    def numero(selo):
        return int(selo.text().split()[0]) if selo.isVisibleTo(tela) else 0

    for ocorrencia in list(tela._ocorrencias)[::3]:
        tela.liberar(ocorrencia)
        soma = sum(numero(s) for s in (tela.selo_validos, tela.selo_suspeitos,
                                       tela.selo_liberados))
        assert soma == numero(tela.selo_encontrados) == 12


def test_a_navegacao_pelos_suspeitos_nao_passa_pelos_liberados(aplicacao):
    """Regressão da conferência da etapa 3, com a imagem da tela em 17/09/2026."""
    tela = _revisao()
    liberado = _achado(tela, "777.777.777-78")
    tela.liberar(liberado)
    tela.selo_suspeitos.mousePressEvent(_clique())

    # O clique no selo já leva ao primeiro; mais dois "próximo" dão a volta.
    vistos = [tela.texto.textCursor().selectedText()]
    for _ in range(2):
        tela.botao_proximo.click()
        vistos.append(tela.texto.textCursor().selectedText())
    assert "777.777.777-78" not in vistos
    assert vistos[0] == vistos[2]
    assert len(set(vistos)) == 2


def _titulos_da_lista(tela):
    return [
        tela.lista._layout.itemAt(i).widget().text()
        for i in range(tela.lista._layout.count())
        if hasattr(tela.lista._layout.itemAt(i).widget(), "text")
    ]


def test_numero_que_passa_na_conta_so_sai_pela_dupla_conferencia(aplicacao, monkeypatch):
    """Regra RN-10: é o que menos pode sair do programa com um clique."""
    tela = _revisao()
    for original in ("111.111.111-11", "l11.111.111-11"):
        achado = _achado(tela, original)
        assert achado.pede_dupla_conferencia
        assert tela.lista._itens[id(achado)].botao.text() == "Desfazer…"

        # A caixa apareceu e a pessoa manteve a máscara: nada muda.
        monkeypatch.setattr("tela_revisao.liberar_mesmo_assim",
                            lambda *_: False)
        tela.lista._itens[id(achado)].botao.click()
        assert achado.situacao == cpf.MASCARADO
        assert original not in tela.texto_mascarado()

        # A pessoa liberou mesmo assim: aí sim o número volta.
        monkeypatch.setattr("tela_revisao.liberar_mesmo_assim", lambda *_: True)
        tela.lista._itens[id(achado)].botao.click()
        assert achado.situacao == cpf.LIBERADO
        assert original in tela.texto_mascarado()


def test_o_quase_cpf_que_passa_na_conta_leva_as_duas_etiquetas(aplicacao):
    tela = _revisao()
    item = tela.lista._itens[id(_achado(tela, "l11.111.111-11"))]
    etiquetas = [rotulo.text() for rotulo in _etiquetas_do_item(item)]
    # A segunda etiqueta não repete o nome da seção de cima: ali é "CPF
    # válido", aqui é o número que só fecha a conta depois de corrigido.
    assert etiquetas == ["quase CPF · letra no lugar de dígito",
                         "válido se corrigido"]


# ------------------------------------------------ anterior · N de M · próximo

def test_a_navegacao_percorre_todos_os_numeros_na_ordem_do_texto(aplicacao):
    tela = _revisao()
    em_ordem = sorted(tela._ocorrencias, key=lambda o: o.inicio)
    assert tela.posicao.text() == "— de 4"

    vistos = []
    for _ in em_ordem:
        tela.botao_proximo.click()
        vistos.append(tela.texto.textCursor().selectedText())
    assert vistos == [o.mascara for o in em_ordem]
    assert tela.posicao.text() == "4 de 4"


def test_a_navegacao_da_a_volta_nas_duas_pontas(aplicacao):
    """Pedido na conferência da etapa 3: do último ao primeiro, e vice-versa."""
    tela = _revisao()
    tela.botao_anterior.click()  # sem nenhum escolhido, o "anterior" vai ao último
    assert tela.posicao.text() == "4 de 4"
    tela.botao_proximo.click()   # do último, o "próximo" volta ao primeiro
    assert tela.posicao.text() == "1 de 4"
    tela.botao_anterior.click()  # do primeiro, o "anterior" vai ao último
    assert tela.posicao.text() == "4 de 4"
    assert tela.botao_proximo.isEnabled() and tela.botao_anterior.isEnabled()


def test_a_navegacao_marca_o_item_na_lista_tambem(aplicacao):
    """Regressão da conferência da etapa 3, em 17/09/2026.

    O "próximo" selecionava o número no texto e não acendia nada na lista: a
    conta que decide qual item acender comparava do jeito errado, e dava "não
    é este" para todos - inclusive no clique na própria lista.
    """
    tela = _revisao()
    em_ordem = sorted(tela._ocorrencias, key=lambda o: o.inicio)
    for ocorrencia in em_ordem:
        tela.botao_proximo.click()
        marcados = [o.original for o in tela._ocorrencias
                    if tela.lista._itens[id(o)].marcado]
        assert marcados == [ocorrencia.original]


def test_clicar_na_lista_acerta_a_posicao_da_navegacao(aplicacao):
    tela = _revisao()
    tela.ir_para(_achado(tela, "777.777.777-78"))
    assert tela.posicao.text() == "2 de 4"
    tela.botao_proximo.click()
    assert tela.texto.textCursor().selectedText() == _achado(tela, "246 813 579 12").mascara


def test_a_navegacao_conta_tambem_o_que_foi_liberado(aplicacao):
    """M conta a lista inteira: o liberado não sai dela, nem da navegação."""
    tela = _revisao()
    tela.liberar(_achado(tela, "777.777.777-78"))
    assert tela.posicao.text() == "2 de 4"


def test_clicar_no_selo_faz_a_navegacao_andar_so_pelo_grupo(aplicacao):
    """Acréscimo de 17/09/2026: o selo filtra a navegação, e nada mais."""
    tela = _revisao()
    suspeitos = sorted((o for o in tela._ocorrencias if o.suspeito),
                       key=lambda o: o.inicio)

    tela.selo_suspeitos.mousePressEvent(_clique())
    assert tela.selo_suspeitos.aceso
    # Escolher o grupo leva direto ao primeiro dele (conferência da etapa 3).
    assert tela.posicao.text() == "1 de 3 suspeitos"

    vistos = [tela.texto.textCursor().selectedText()]
    for _ in suspeitos[1:]:
        tela.botao_proximo.click()
        vistos.append(tela.texto.textCursor().selectedText())
    assert vistos == [o.mascara for o in suspeitos]
    assert tela.posicao.text() == "3 de 3 suspeitos"
    # O texto e a lista continuam inteiros: o filtro não esconde nada.
    assert len(tela.lista._itens) == 4


def test_clicar_de_novo_no_selo_volta_a_percorrer_todos(aplicacao):
    tela = _revisao()
    tela.ir_para(_achado(tela, "246 813 579 12"))  # o terceiro número do texto
    tela.selo_validos.mousePressEvent(_clique())
    assert tela.posicao.text() == "1 de 1 CPF válido"

    # Desligar o filtro não muda de lugar: continua no CPF válido, que é o
    # primeiro do texto.
    tela.selo_validos.mousePressEvent(_clique())
    assert not tela.selo_validos.aceso
    assert tela.posicao.text() == "1 de 4"

    # Já o "encontrados" é a escolha de um grupo - o de todos - e leva ao primeiro.
    tela.ir_para(_achado(tela, "l11.111.111-11"))
    tela.selo_encontrados.mousePressEvent(_clique())
    assert tela.posicao.text() == "1 de 4"


def test_clicar_num_selo_sempre_leva_ao_primeiro_do_grupo(aplicacao):
    """Conferência da etapa 3: não ao que estiver perto de onde a pessoa estava."""
    tela = _revisao()
    tela.ir_para(_achado(tela, "l11.111.111-11"))  # o último do texto
    tela.selo_suspeitos.mousePressEvent(_clique())
    assert tela.texto.textCursor().selectedText() == _achado(tela, "777.777.777-78").mascara
    assert tela.posicao.text() == "1 de 3 suspeitos"


def test_o_proximo_segue_de_onde_a_pessoa_esta_mesmo_fora_do_grupo(aplicacao):
    """Clicou na lista num número de outro grupo: o "próximo" segue dali."""
    tela = _revisao()
    tela.selo_suspeitos.mousePressEvent(_clique())
    valido = _achado(tela, "111.111.111-11")  # o primeiro do texto, e não é suspeito
    tela.ir_para(valido)
    assert tela.posicao.text() == "— de 3 suspeitos"

    tela.botao_proximo.click()
    assert tela.texto.textCursor().selectedText() == _achado(tela, "777.777.777-78").mascara
    assert tela.posicao.text() == "1 de 3 suspeitos"


def test_o_filtro_de_liberados_desliga_quando_o_grupo_esvazia(aplicacao):
    """O selo do grupo vazio some - e sem ele não haveria como desligar o filtro."""
    tela = _revisao()
    achado = _achado(tela, "777.777.777-78")
    tela.liberar(achado)
    tela.selo_liberados.mousePressEvent(_clique())
    assert tela.posicao.text() == "1 de 1 liberado"

    tela.mascarar_de_novo(achado)
    assert not tela.selo_liberados.aceso
    assert tela.posicao.text() == "2 de 4"


def _clique():
    from PySide6.QtCore import QPointF, Qt as QtCore
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QEvent
    return QMouseEvent(QEvent.MouseButtonPress, QPointF(1, 1), QPointF(1, 1),
                       QtCore.LeftButton, QtCore.LeftButton, QtCore.NoModifier)


def test_sem_cpf_a_navegacao_nao_aparece(aplicacao):
    tela = TelaRevisao(ao_anonimizar_outro=lambda: None)
    tela.mostrar("sem.md", "Ata sem número de pessoa nenhuma.", [])
    for peca in (tela.botao_anterior, tela.posicao, tela.botao_proximo):
        assert not peca.isVisibleTo(tela)


def test_o_que_foi_liberado_fica_verde_no_selo_no_texto_e_na_lista(aplicacao):
    """Decisão da usuária em 17/09/2026: o que ela soltou se acha de relance."""
    import estilo

    tela = _revisao()
    achado = _achado(tela, "777.777.777-78")
    tela.liberar(achado)
    assert estilo.COR_SUCESSO in tela.selo_liberados.styleSheet()

    cursor = tela.texto.textCursor()
    cursor.setPosition(_posicao_no_qt(TEXTO, achado.inicio) + 1)
    formato = cursor.charFormat()
    assert formato.foreground().color().name() == estilo.COR_SUCESSO
    assert formato.underlineStyle() == QTextCharFormat.DashUnderline

    item = tela.lista._itens[id(achado)]
    liberado = next(rotulo for rotulo in _etiquetas_do_item(item)
                    if rotulo.text() == "liberado")
    assert estilo.COR_SUCESSO in liberado.styleSheet()


def test_o_conteudo_da_lista_cabe_na_largura_da_coluna(aplicacao):
    """Regressão da conferência da etapa 3, com a imagem da tela em 17/09/2026.

    O item com duas etiquetas lado a lado ("quase CPF · espaços no lugar dos
    pontos" e "CPF válido") deixava o conteúdo com 350 pontos numa coluna de
    320. A lista deslizava para o lado e cortava a primeira letra dos títulos
    ("uspeitos — olhe estes 9"). A medida é feita com a massa inteira, que tem
    as etiquetas mais compridas do programa.
    """
    texto = (MASSA / "10-prestacao-com-cpf.md").read_text(encoding="utf-8")
    tela = TelaRevisao(ao_anonimizar_outro=lambda: None)
    tela.resize(1000, 640)
    tela.show()
    tela.mostrar("10-prestacao-com-cpf.md", texto, cpf.procurar(texto))
    # Liberado, o item ganha a etiqueta "liberado" ao lado da do tipo.
    for ocorrencia in tela._ocorrencias:
        tela.liberar(ocorrencia) if not ocorrencia.pede_dupla_conferencia else None
    aplicacao.processEvents()

    lista = tela.lista
    assert lista.widget().minimumSizeHint().width() <= lista.viewport().width()
    for _ in tela._ocorrencias:
        tela.botao_proximo.click()
        assert lista.horizontalScrollBar().value() == 0


# ------------------------------------------- a caixa da dupla conferência

def test_a_caixa_vem_com_manter_a_mascara_escolhido(aplicacao):
    """Apertar Enter ou Esc mantém a máscara (regra RN-10)."""
    achado = cpf.procurar("CPF 111.111.111-11 fim")[0]
    caixa = DuplaConferencia(achado)
    assert caixa.botao_manter.isDefault()
    assert not caixa.botao_liberar.isDefault()
    assert caixa.isModal()


@pytest.mark.parametrize("texto, pedaco", [
    ("CPF 111.111.111-11 fim", "a partir dos nove primeiros"),
    ("CPF l11.111.111-11 fim", "letras trocadas de volta"),
    ("CPF 555.555.\n555-55 fim", "partido em duas linhas"),
    ("CPF 666 666 666 66 fim", "espaços pela pontuação"),
])
def test_a_caixa_explica_por_que_aquele_numero_passa(aplicacao, texto, pedaco):
    achado = cpf.procurar(texto)[0]
    caixa = DuplaConferencia(achado)
    assert pedaco in caixa.explicacao.text()
    # No "quase CPF", a caixa diz que o defeito é, quase sempre, da leitura - e
    # que no original provavelmente há um número ali.
    assert ("erro de leitura" in caixa.explicacao.text()) == (
        achado.tipo == cpf.QUASE_CPF)
    # A frase inteira precisa caber: a caixa tem largura fixa, e sem a altura
    # calculada o fim dela some para fora da borda.
    assert caixa.explicacao.minimumHeight() >= caixa.explicacao.heightForWidth(
        caixa.explicacao.width() or 460)


def test_a_massa_inteira_abre_na_lista_sem_nenhum_cpf_solto(aplicacao):
    """O documento da massa, do jeito que a pessoa vai ver."""
    texto = (MASSA / "10-prestacao-com-cpf.md").read_text(encoding="utf-8")
    tela = TelaRevisao(ao_anonimizar_outro=lambda: None)
    tela.mostrar("10-prestacao-com-cpf.md", texto, cpf.procurar(texto))

    assert cpf.procurar(tela.texto_mascarado()) == []
    assert len(tela.lista._itens) == 12
    assert tela.selo_suspeitos.text() == "9 suspeitos"

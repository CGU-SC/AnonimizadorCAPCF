"""As cores dos dois temas (emenda de 05/11/2026 da spec 001, RN-16 a RN-18 e RN-26;
rascunho mockups/janela/07-os-tons-que-faltavam.html)."""
import ast
import io
import pathlib
import re
import tokenize

from PySide6.QtWidgets import QLabel, QWidget

import estilo
import tipos_na_tela

AQUI = pathlib.Path(__file__).parent

# Cada papel com o valor que o programa usava antes da funcionalidade 10, copiado
# à mão do código daquela época, e não do estilo.py: é a prova de que quem usa o
# escuro não vê nada mudar ao atualizar (RN-16).
ESCURO_DE_ANTES = {
    "COR_FUNDO": "#1e2228",
    "COR_FUNDO_ELEVADO": "#262b33",
    "COR_BORDA": "#383e47",
    "COR_TEXTO": "#e8eaed",
    "COR_TEXTO_SECUNDARIO": "#9aa1ac",
    "COR_TEXTO_APAGADO": "#6c737d",
    "COR_DESTAQUE": "#3b6ea5",
    "COR_DESTAQUE_HOVER": "#4f86bf",
    "COR_DESTAQUE_FRACO": "rgba(59, 110, 165, 0.24)",
    "COR_PASSAR_O_MOUSE": "rgba(255, 255, 255, 0.06)",
    "COR_SUCESSO": "#4caf6d",
    "COR_ALERTA": "#d9a441",
    "COR_ALERTA_TEXTO": "#d9a441",
    # Papéis de 06/11/2026, com o amarelo que o suspeito sempre teve no escuro.
    "COR_SUSPEITO": "#d9a441",
    "COR_SUSPEITO_BARRA": "#d9a441",
    "COR_ERRO": "#d9534f",
    "COR_ERRO_TEXTO": "#f08a86",
    "COR_IA": "#b39ddb",
    "COR_ATRAS_DO_PDF": "#0f1216",
    "COR_ERRO_FUNDO": "rgba(217, 83, 79, 26)",
    "COR_ALERTA_FUNDO": "rgba(217, 164, 65, 26)",
    "COR_ALERTA_FUNDO_FORTE": "rgba(217, 164, 65, 31)",
    "COR_ALERTA_SELO": "rgba(217, 164, 65, 38)",
    "COR_DESTAQUE_AVISO": "rgba(59, 110, 165, 26)",
    "COR_DESTAQUE_NA_LISTA": "rgba(59, 110, 165, 46)",
    "COR_DESTAQUE_SELO": "rgba(59, 110, 165, 51)",
    "COR_DESTAQUE_SELO_TEXTO": "#7fb1e8",
    "COR_IA_FUNDO": "rgba(179, 157, 219, 23)",
    "COR_AREA_DE_SOLTAR": "rgba(255, 255, 255, 4)",
    "COR_TEXTO_DESLIGADO": "#5d646e",
    "COR_TEXTO_DESLIGADO_PEQUENO": "#565d66",
    "COR_BORDA_DESLIGADA": "#4a5058",
    "COR_BOLINHA_LIGADA": "#ffffff",
    "FORCA_DA_MARCA_DA_IA": 36,
    "FORCA_DO_DESTAQUE_FRACO": 0.24,
}

# Cor escrita num texto do código: #abc, #aabbcc, #aabbccdd, rgb(...) e rgba(...).
COR_ESCRITA = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3}(?:[0-9a-fA-F]{2})?)?\b|rgba?\(")
TEXTOS = (tokenize.STRING, tokenize.FSTRING_MIDDLE)


def test_o_escuro_continua_com_os_valores_de_antes():
    estilo.usar_tema(estilo.ESCURO)
    for papel, valor in ESCURO_DE_ANTES.items():
        assert getattr(estilo, papel) == valor, papel


def test_o_programa_comeca_no_escuro():
    # Ninguém escolheu tema ainda: vale o de quem nunca escolheu (RN-16).
    assert estilo.TEMA == estilo.ESCURO


def test_os_dois_temas_tem_os_mesmos_papeis():
    assert set(estilo.TEMAS[estilo.ESCURO]) == set(estilo.TEMAS[estilo.CLARO])


def test_nome_que_nao_e_tema_vale_como_escuro():
    estilo.usar_tema("azul")
    assert estilo.TEMA == estilo.ESCURO
    assert estilo.COR_FUNDO == "#1e2228"


def test_o_claro_troca_os_valores():
    estilo.usar_tema(estilo.CLARO)
    assert estilo.TEMA == estilo.CLARO
    assert estilo.COR_FUNDO == "#f2f4f7"
    assert estilo.COR_ALERTA_TEXTO == "#a85a00"
    assert estilo.COR_DESTAQUE_FRACO == "rgba(31, 78, 140, 0.1)"


def test_o_ambar_e_o_vermelho_do_claro_sao_os_escolhidos():
    # Coluna A do mockups/janela/09-o-ambar-do-suspeito-ajustado.html,
    # acréscimo de 06/11/2026 da spec 001.
    claro = estilo.TEMAS[estilo.CLARO]
    assert claro["COR_SUSPEITO"] == "#c28102"
    assert claro["COR_SUSPEITO_BARRA"] == "#ec9c01"
    assert claro["COR_ALERTA_TEXTO"] == "#a85a00"
    assert claro["COR_ERRO"] == claro["COR_ERRO_TEXTO"] == "#ae0202"


def _cores_escritas_fora_do_estilo():
    """Cada cor escrita num texto do código das telas, com o arquivo e a linha.

    Só os textos contam: o comentário que cita uma cor para explicar uma decisão
    não pinta nada.
    """
    achadas = []
    for arquivo in sorted(AQUI.glob("*.py")):
        if arquivo.name in ("estilo.py", "conftest.py") or arquivo.name.startswith(("test_", "_")):
            continue
        fonte = arquivo.read_text(encoding="utf-8")
        for pedaco in tokenize.generate_tokens(io.StringIO(fonte).readline):
            # Desde o Python 3.12, o texto de um f"..." chega em pedaços de outro
            # tipo, e não como texto comum: olhando só o comum, a varredura
            # pulava quase todas as folhas de estilo do programa, calada.
            if (pedaco.type in TEXTOS
                    and COR_ESCRITA.search(pedaco.string)):
                achadas.append(f"{arquivo.name}:{pedaco.start[0]} {pedaco.string[:60]}")
    return achadas


def test_nenhuma_tela_tem_cor_escrita_fora_do_estilo():
    # RN-26: as duas exceções (o branco da letra do botão de destaque e o do
    # símbolo) moram no próprio estilo.py, com nome.
    assert _cores_escritas_fora_do_estilo() == []


def test_a_varredura_acha_cor_escrita_de_verdade(tmp_path, monkeypatch):
    # Sem isto, uma varredura quebrada passaria calada pelo teste de cima.
    (tmp_path / "tela_de_mentira.py").write_text(
        '# um comentário com #123456 não conta\n'
        'COR = "#123456"\n'
        'FUNDO = f"background: rgba(1, 2, 3, 4);"\n', encoding="utf-8")
    monkeypatch.setattr("test_tema.AQUI", tmp_path)
    achadas = _cores_escritas_fora_do_estilo()
    assert [a.split(" ")[0] for a in achadas] == ["tela_de_mentira.py:2", "tela_de_mentira.py:3"]


def _eh_cor_do_estilo(no):
    return (isinstance(no, ast.Attribute) and isinstance(no.value, ast.Name)
            and no.value.id == "estilo" and no.attr.startswith(("COR_", "FORCA_")))


def _cores_lidas_cedo_demais():
    """Cada `estilo.COR_...` lido quando o arquivo carrega, e não quando a peça nasce.

    São três lugares: fora de qualquer função, no corpo de uma classe e no valor
    padrão de uma função - este último é lido quando a função é declarada, e foi
    o que escapou da primeira procura (lente crítica da etapa 1 da funcionalidade
    10). Lida ali, a cor fica a do escuro também no claro (RN-17).
    """
    achadas = []

    def olhar(nome, no, cedo):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            padroes = no.args.defaults + [d for d in no.args.kw_defaults if d]
            achadas.extend(f"{nome}:{d.lineno}" for padrao in padroes
                           for d in ast.walk(padrao) if _eh_cor_do_estilo(d))
            for filho in (no.body if isinstance(no.body, list) else [no.body]):
                olhar(nome, filho, False)
            return
        if cedo and _eh_cor_do_estilo(no):
            achadas.append(f"{nome}:{no.lineno}")
        for filho in ast.iter_child_nodes(no):
            olhar(nome, filho, cedo)

    for arquivo in sorted(AQUI.glob("*.py")):
        if arquivo.name in ("estilo.py", "conftest.py") or arquivo.name.startswith(("test_", "_")):
            continue
        olhar(arquivo.name, ast.parse(arquivo.read_text(encoding="utf-8")), True)
    return achadas


def test_nenhuma_tela_le_a_cor_cedo_demais():
    assert _cores_lidas_cedo_demais() == []


def test_a_procura_acha_cor_lida_cedo_demais(tmp_path, monkeypatch):
    (tmp_path / "tela_de_mentira.py").write_text(
        "import estilo\n"
        "FUNDO = estilo.COR_FUNDO\n"
        "class Peca:\n"
        "    BORDA = estilo.COR_BORDA\n"
        "    def pintar(self, cor=estilo.COR_TEXTO):\n"
        "        return estilo.COR_TEXTO\n", encoding="utf-8")
    monkeypatch.setattr("test_tema.AQUI", tmp_path)
    assert _cores_lidas_cedo_demais() == [
        "tela_de_mentira.py:2", "tela_de_mentira.py:4", "tela_de_mentira.py:5"]


def test_no_claro_o_titulo_de_secao_da_lista_sai_na_letra_do_claro():
    import lista_de_achados
    estilo.usar_tema(estilo.CLARO)
    titulo = lista_de_achados._titulo_de_secao("Suspeitos — olhe estes 3")
    assert estilo.TEMAS[estilo.CLARO]["COR_TEXTO"] in titulo.styleSheet()


def _o_que_cada_peca_pinta(janela):
    """A folha de estilo e o texto de cada peça da janela, juntos."""
    pecas = [janela, *janela.findChildren(QWidget)]
    textos = [peca.styleSheet() for peca in pecas]
    textos += [peca.text() for peca in pecas if isinstance(peca, QLabel)]
    return "\n".join(textos).lower()


def test_no_claro_nenhuma_tela_montada_tem_cor_do_escuro():
    import main
    estilo.usar_tema(estilo.CLARO)
    janela = main.JanelaPrincipal()
    pintado = _o_que_cada_peca_pinta(janela)

    claro = {str(v).lower() for v in estilo.TEMAS[estilo.CLARO].values()}
    so_do_escuro = {str(v).lower() for v in estilo.TEMAS[estilo.ESCURO].values()
                    if isinstance(v, str)} - claro - {estilo.COR_LETRA_NO_DESTAQUE}
    sobrou = sorted(cor for cor in so_do_escuro if cor in pintado)
    assert sobrou == []
    # E o claro chegou de fato às telas, e não só ao estilo.
    assert estilo.TEMAS[estilo.CLARO]["COR_FUNDO"] in pintado


def test_os_tipos_da_revisao_seguem_o_tema():
    # As cores dos tipos são lidas na hora: guardadas ao carregar, ficariam as do
    # escuro também no claro (RN-17).
    estilo.usar_tema(estilo.CLARO)
    assert tipos_na_tela.SUSPEITO.cor == "#c28102"
    assert tipos_na_tela.DA_IA.cor == "#7356c8"
    estilo.usar_tema(estilo.ESCURO)
    assert tipos_na_tela.SUSPEITO.cor == "#d9a441"


def _contraste(cor_a, cor_b):
    def luz(cor):
        def canal(v):
            v /= 255
            return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        r, g, b = (canal(int(cor[i:i + 2], 16)) for i in (1, 3, 5))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    clara, escura = sorted((luz(cor_a), luz(cor_b)), reverse=True)
    return (clara + 0.05) / (escura + 0.05)


# Os papéis que viram letra. Ficam de fora o texto apagado e as letras de peça
# desligada, apagados de propósito (exceção da RN-18); o suspeito, que no claro
# fica abaixo do mínimo de propósito (exceção da RN-30), e tem teste próprio; e o
# amarelo de alerta, que no claro só pinta fundo e borda.
LETRAS = ("COR_TEXTO", "COR_TEXTO_SECUNDARIO", "COR_DESTAQUE", "COR_DESTAQUE_HOVER",
          "COR_SUCESSO", "COR_ALERTA_TEXTO", "COR_ERRO", "COR_ERRO_TEXTO", "COR_IA",
          "COR_DESTAQUE_SELO_TEXTO")


def test_no_claro_toda_letra_tem_contraste_de_quatro_e_meio():
    claro = estilo.TEMAS[estilo.CLARO]
    for papel in LETRAS:
        for fundo in ("COR_FUNDO", "COR_FUNDO_ELEVADO"):
            medido = _contraste(claro[papel], claro[fundo])
            assert medido >= 4.5, f"{papel} sobre {fundo}: {medido:.2f}"


def test_no_claro_o_suspeito_se_separa_da_letra_do_texto():
    # A razão da exceção da RN-30: o suspeito abre mão do contraste com o fundo
    # para não se confundir com o preto do texto em volta dele.
    claro = estilo.TEMAS[estilo.CLARO]
    assert _contraste(claro["COR_SUSPEITO"], claro["COR_TEXTO"]) >= 4.5


def test_no_claro_a_revisao_pinta_o_suspeito_e_o_valido_com_as_cores_novas(aplicacao):
    import cpf
    from PySide6.QtWidgets import QLabel
    from tela_revisao import TelaRevisao

    estilo.usar_tema(estilo.CLARO)
    texto = "Bolsista no CPF 111.111.111-11 e coordenador no 777.777.777-78."
    tela = TelaRevisao(ao_anonimizar_outro=lambda: None)
    tela.mostrar("t.md", texto, cpf.procurar(texto))
    achados = {o.original: o for o in tela._ocorrencias}
    for original, letra, barra in (
            ("111.111.111-11", "#ae0202", "#ae0202"),
            ("777.777.777-78", "#c28102", "#ec9c01")):
        ocorrencia = achados[original]
        item = tela.lista._itens[id(ocorrencia)]
        assert f"border-left: 3px solid {barra}" in item.styleSheet(), original
        etiquetas = [r for r in item.findChildren(QLabel)
                     if "border-radius: 8px" in r.styleSheet()]
        assert etiquetas and all(letra in r.styleSheet() for r in etiquetas), original
        cursor = tela.texto.textCursor()
        cursor.setPosition(ocorrencia.inicio + 1)
        assert cursor.charFormat().foreground().color().name() == letra, original
    assert "#c28102" in tela.selo_suspeitos.styleSheet()


def test_no_claro_o_amarelo_de_alerta_nao_e_letra():
    import main
    estilo.usar_tema(estilo.CLARO)
    pintado = _o_que_cada_peca_pinta(main.JanelaPrincipal())
    amarelo = estilo.TEMAS[estilo.CLARO]["COR_ALERTA"]
    # "color:" sozinho é a letra; "background-color:" e "border...color:" não.
    assert not re.search(rf"(?<![-\w])color:\s*{amarelo}", pintado)
    assert not re.search(rf"color\s*=\s*['\"]?{amarelo}", pintado)

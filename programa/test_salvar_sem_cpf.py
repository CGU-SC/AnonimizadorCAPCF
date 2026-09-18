"""Testes do fim do Anonimizar: do botão de salvar ao arquivo em disco.

Aqui moram as promessas que olhar a tela não confirma: que o arquivo gravado não
tem CPF inteiro nem uma linha escrita pelo programa, que a origem continua
intacta byte a byte, e que nenhum caminho torto - arquivo que já existe, pasta
que recusa a gravação - faz a revisão se perder.
"""
import shutil
from pathlib import Path

import arquivo_md
import cpf
from painel_anonimizar import RECUSA_DA_ORIGEM, PainelAnonimizar

MASSA = Path(__file__).parent.parent / "dados-exemplo"
COM_CPF = "10-prestacao-com-cpf.md"


def _painel_com(pasta, nome=COM_CPF):
    """Um painel já na revisão, com uma cópia da massa dentro da pasta do teste.

    A cópia é de propósito: os testes gravam ao lado da origem, e a massa do
    projeto não pode ganhar arquivo nenhum por causa de um teste.
    """
    origem = pasta / nome
    shutil.copy(MASSA / nome, origem)
    painel = PainelAnonimizar()
    painel.receber_arquivo(origem)
    return painel, origem


# ------------------------------------------------------------- o caminho sugerido


def test_o_caminho_sugerido_fica_ao_lado_da_origem(tmp_path):
    sugerido = arquivo_md.caminho_sem_cpf(tmp_path / "Prestacao 2026.md")
    assert sugerido == tmp_path / "Prestacao 2026 - sem CPF.md"


def test_o_caminho_sugerido_troca_a_terminacao_do_pdf_e_do_txt(tmp_path):
    for nome in ("anexo.pdf", "anexo.txt"):
        assert arquivo_md.caminho_sem_cpf(tmp_path / nome).name == "anexo - sem CPF.md"


def test_salvar_abre_a_tela_com_o_caminho_preenchido_e_a_contagem(tmp_path, aplicacao):
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()

    assert painel.telas.currentWidget() is painel.tela_salvar
    assert painel.tela_salvar.campo.text() == str(
        origem.with_name(f"{origem.stem} - sem CPF.md"))
    # A contagem da tela de salvar conta o mesmo que os selos da revisão.
    assert painel.tela_salvar.contagem.text() == (
        "12 números mascarados: 3 CPFs válidos e 9 suspeitos."
        " Nenhum número com CPF válido foi liberado.")
    assert origem.name in painel.tela_salvar.legenda.text()


def test_o_botao_da_revisao_abre_a_tela_de_salvar(tmp_path, aplicacao):
    """Pelo clique, e não chamando a função: foi assim que o defeito passou.

    O Qt manda um argumento junto do clique, que caía no caminho de destino, e
    o botão não fazia nada - com a função chamada direto, tudo passava.
    """
    painel, origem = _painel_com(tmp_path)
    painel.tela_revisao.botao_salvar.click()

    assert painel.telas.currentWidget() is painel.tela_salvar
    assert painel.tela_salvar.campo.text().endswith(" - sem CPF.md")


def test_sem_nenhum_cpf_a_contagem_diz_isso_e_o_salvar_funciona(tmp_path, aplicacao):
    painel, origem = _painel_com(tmp_path, "11-sem-cpf.md")
    painel.abrir_o_salvar()

    assert painel.tela_salvar.contagem.text() == "Nenhum número foi mascarado neste texto."
    painel.gravar(Path(painel.tela_salvar.campo.text()))
    assert painel.telas.currentWidget() is painel.tela_gravado


# ------------------------------------------------------------------ o arquivo


def test_o_arquivo_gravado_nao_tem_nenhum_cpf_inteiro(tmp_path, aplicacao):
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    destino = Path(painel.tela_salvar.campo.text())
    painel.gravar(destino)

    gravado = destino.read_text(encoding="utf-8")
    # Passando o arquivo pelo motor de novo, não pode sobrar nada para achar.
    assert cpf.procurar(gravado) == []
    assert gravado.count("XXX") == 12


def test_o_arquivo_gravado_tem_o_texto_e_mais_nada(tmp_path, aplicacao):
    """Regra RN-12: nenhuma linha escrita pelo programa entra no arquivo."""
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    destino = Path(painel.tela_salvar.campo.text())
    painel.gravar(destino)

    gravado = destino.read_text(encoding="utf-8")
    na_tela = painel.tela_revisao.texto_mascarado()
    assert gravado == (na_tela if na_tela.endswith("\n") else na_tela + "\n")
    # Nenhuma frase que o programa escreve na tela vaza para dentro do arquivo.
    for recado in (painel.tela_revisao.resumo_do_que_sai(), "Anonimizador",
                   "CPF válido", "mascarado à mão", "Revisar antes de salvar"):
        assert recado not in gravado, recado


def test_o_arquivo_de_origem_nao_muda(tmp_path, aplicacao):
    """Regra RN-14, conferida byte a byte - e não pelo que a tela diz."""
    antes = (MASSA / COM_CPF).read_bytes()
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    painel.gravar(Path(painel.tela_salvar.campo.text()))

    assert origem.read_bytes() == antes


def test_a_tela_de_sucesso_mostra_o_caminho_e_lembra_da_origem(tmp_path, aplicacao):
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    destino = Path(painel.tela_salvar.campo.text())
    painel.gravar(destino)

    assert painel.telas.currentWidget() is painel.tela_gravado
    assert painel.tela_gravado.caminho.text() == str(destino)
    assert painel.tela_gravado.titulo.text() == "Arquivo gravado, sem CPF"
    lembrete = painel.tela_gravado.lembrete.text()
    assert origem.name in lembrete and "CPFs inteiros" in lembrete
    # A frase do lembrete muda de tamanho com o nome do arquivo: sem altura
    # calculada, o fim dela sai para fora da borda sem nada acusar.
    assert painel.tela_gravado.lembrete.minimumHeight() > 0


# --------------------------------------------------------- os caminhos tortos


def test_gravar_por_cima_da_origem_e_recusado(tmp_path, aplicacao):
    """Regra RN-14: a origem nunca é alterada, nem a pedido."""
    painel, origem = _painel_com(tmp_path)
    antes = origem.read_bytes()
    painel.abrir_o_salvar()
    painel.gravar(origem)

    assert painel.telas.currentWidget() is painel.tela_salvar
    assert RECUSA_DA_ORIGEM.format(nome=origem.name) == painel.tela_salvar.problema.text()
    assert painel.tela_salvar.problema.isVisibleTo(painel.tela_salvar)
    assert origem.read_bytes() == antes


def test_a_origem_escrita_de_outro_jeito_tambem_e_recusada(tmp_path, aplicacao):
    """O mesmo arquivo chega escrito de vários jeitos, e todos são a origem."""
    painel, origem = _painel_com(tmp_path)
    antes = origem.read_bytes()
    painel.abrir_o_salvar()
    # Com a pasta dando uma volta no caminho, e em maiúsculas: o Windows abre o
    # mesmo arquivo, e comparar só o texto do caminho deixaria passar.
    torto = origem.parent / "." / origem.name.upper()
    painel.gravar(torto)

    assert painel.telas.currentWidget() is painel.tela_salvar
    assert origem.read_bytes() == antes


def test_arquivo_que_ja_existe_pergunta_antes_de_escrever_por_cima(tmp_path, aplicacao):
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    destino = Path(painel.tela_salvar.campo.text())
    destino.write_text("texto de outro trabalho\n", encoding="utf-8")

    painel.gravar(destino)
    assert painel.telas.currentWidget() is painel.tela_sobrescrever
    # Nada foi tocado enquanto a pergunta está na tela.
    assert destino.read_text(encoding="utf-8") == "texto de outro trabalho\n"

    painel._escrever_por_cima()
    assert painel.telas.currentWidget() is painel.tela_gravado
    assert "XXX" in destino.read_text(encoding="utf-8")


def test_a_janela_do_windows_nao_pergunta_sobre_substituir(tmp_path, aplicacao,
                                                           monkeypatch):
    """Quem pergunta sobre apagar o arquivo é a nossa tela, e mais ninguém.

    A janela do Windows perguntava "deseja substituir?" e, respondido que sim,
    só devolvia o caminho - nada era gravado. Quem respondeu achava ter mandado
    salvar, e o programa parecia não fazer nada (conferência da etapa 5).
    """
    from PySide6.QtWidgets import QFileDialog

    pedidos = {}

    def falsa_janela(*args, **kwargs):
        pedidos.update(kwargs)
        return "", ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", falsa_janela)
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    painel.tela_salvar._escolher_pasta()

    assert pedidos["options"] == QFileDialog.Option.DontConfirmOverwrite


def test_o_clique_em_escrever_por_cima_grava(tmp_path, aplicacao):
    """Pelo botão de verdade: é onde o outro defeito do clique se escondeu."""
    from PySide6.QtWidgets import QPushButton

    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    destino = Path(painel.tela_salvar.campo.text())
    destino.write_text("de outro trabalho\n", encoding="utf-8")
    painel.gravar(destino)

    botao = next(b for b in painel.tela_sobrescrever.findChildren(QPushButton)
                 if b.text() == "Escrever por cima")
    botao.click()

    assert painel.telas.currentWidget() is painel.tela_gravado
    assert "XXX" in destino.read_text(encoding="utf-8")


def test_salvar_com_outro_nome_volta_com_um_nome_livre(tmp_path, aplicacao):
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    destino = Path(painel.tela_salvar.campo.text())
    destino.write_text("texto de outro trabalho\n", encoding="utf-8")

    painel.gravar(destino)
    painel._sugerir_outro_nome()

    assert painel.telas.currentWidget() is painel.tela_salvar
    assert painel.tela_salvar.campo.text() == str(
        destino.with_name(f"{destino.stem} (2).md"))
    # E o arquivo que já existia continua lá, inteiro.
    assert destino.read_text(encoding="utf-8") == "texto de outro trabalho\n"


def test_erro_ao_gravar_volta_para_o_salvar_sem_perder_a_revisao(tmp_path,
                                                                 aplicacao,
                                                                 monkeypatch):
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    destino = Path(painel.tela_salvar.campo.text())

    def recusar(caminho, conteudo, fim_de_linha="\n"):
        raise PermissionError("pasta protegida contra gravação")

    monkeypatch.setattr(arquivo_md, "gravar", recusar)
    painel.gravar(destino)

    assert painel.telas.currentWidget() is painel.tela_salvar
    assert str(destino.parent) in painel.tela_salvar.problema.text()
    assert not destino.exists()
    # A revisão continua inteira atrás: o trabalho não se perdeu.
    assert painel.tela_revisao.texto_mascarado().count("XXX") == 12


def test_a_pasta_que_nao_existe_e_avisada_antes_de_gravar(tmp_path, aplicacao):
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    painel.tela_salvar.campo.setText(str(tmp_path / "pasta que nao existe" / "x.md"))
    painel.tela_salvar._salvar()

    assert painel.telas.currentWidget() is painel.tela_salvar
    assert painel.tela_salvar.caixa_do_problema.titulo.text() == "Essa pasta não existe"


def test_so_o_nome_sem_pasta_grava_ao_lado_da_origem(tmp_path, aplicacao):
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    painel.tela_salvar.campo.setText("outro nome")
    painel.tela_salvar._salvar()

    # Sem pasta e sem terminação, o arquivo iria parar na pasta de onde o
    # programa foi aberto, e sem nome que algum programa saiba abrir.
    assert (tmp_path / "outro nome.md").exists()
    assert painel.telas.currentWidget() is painel.tela_gravado


def test_o_campo_vazio_nao_grava_nada(tmp_path, aplicacao):
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    painel.tela_salvar.campo.setText("   ")
    painel.tela_salvar._salvar()

    assert painel.telas.currentWidget() is painel.tela_salvar
    assert list(tmp_path.glob("*")) == [origem]


# --------------------------------------------------- o lembrete dos liberados


def _liberar_um_que_passa_na_conta(painel):
    ocorrencia = next(o for o in painel.tela_revisao._ocorrencias if o.passa_na_conta)
    # Direto pela situação, e não pelo botão: a dupla conferência é uma caixa
    # modal, que num teste ficaria esperando alguém clicar para sempre.
    ocorrencia.situacao = cpf.LIBERADO
    painel.tela_revisao._desenhar()
    return ocorrencia


def test_o_numero_liberado_aparece_antes_de_gravar(tmp_path, aplicacao):
    """Regra RN-11: quais foram, antes de gravar, e não depois."""
    painel, origem = _painel_com(tmp_path)
    liberado = _liberar_um_que_passa_na_conta(painel)
    painel.abrir_o_salvar()

    aviso = painel.tela_salvar.aviso_dos_liberados
    assert aviso.isVisibleTo(painel.tela_salvar)
    assert any(liberado.original in linha for linha in aviso.texto_dos_numeros())
    assert "1 número com CPF válido vai inteiro" in aviso.titulo.text()
    # Com número indo inteiro, o botão que salva deixa de ser o de destaque e
    # passa a dizer o que faz.
    assert painel.tela_salvar.botao_salvar.text() == "Salvar assim mesmo"


def test_o_quase_cpf_liberado_leva_a_etiqueta_da_lista(tmp_path, aplicacao):
    """O mesmo número não pode trocar de nome entre uma tela e outra."""
    painel, origem = _painel_com(tmp_path)
    quase = next(o for o in painel.tela_revisao._ocorrencias
                 if o.tipo == cpf.QUASE_CPF and o.passa_na_conta)
    quase.situacao = cpf.LIBERADO
    painel.tela_revisao._desenhar()
    painel.abrir_o_salvar()

    linha = painel.tela_salvar.aviso_dos_liberados.texto_dos_numeros()[0]
    assert "válido se corrigido" in linha
    # E o que vem antes no texto, que é o que deixa reconhecer qual número é.
    assert "…" in linha


def test_sem_liberado_nenhum_o_aviso_nao_aparece(tmp_path, aplicacao):
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()

    assert not painel.tela_salvar.aviso_dos_liberados.isVisibleTo(painel.tela_salvar)
    assert painel.tela_salvar.botao_salvar.text() == "Salvar"


def test_o_suspeito_que_falha_na_conta_nao_entra_no_aviso(tmp_path, aplicacao):
    """Liberar um que falha na conta é o caso comum, e não pede aviso."""
    painel, origem = _painel_com(tmp_path)
    ocorrencia = next(o for o in painel.tela_revisao._ocorrencias
                      if not o.passa_na_conta)
    ocorrencia.situacao = cpf.LIBERADO
    painel.tela_revisao._desenhar()
    painel.abrir_o_salvar()

    assert not painel.tela_salvar.aviso_dos_liberados.isVisibleTo(painel.tela_salvar)


def test_com_liberado_o_titulo_do_sucesso_nao_diz_sem_cpf(tmp_path, aplicacao):
    """O arquivo tem um CPF inteiro dentro: dizer "sem CPF" seria mentir."""
    painel, origem = _painel_com(tmp_path)
    liberado = _liberar_um_que_passa_na_conta(painel)
    painel.abrir_o_salvar()
    destino = Path(painel.tela_salvar.campo.text())
    painel.gravar(destino)

    assert painel.tela_gravado.titulo.text() == "Arquivo gravado"
    # E o número liberado está mesmo inteiro no arquivo: é o que a pessoa pediu.
    assert liberado.original in destino.read_text(encoding="utf-8")


def test_anonimizar_outro_documento_limpa_tudo(tmp_path, aplicacao):
    painel, origem = _painel_com(tmp_path)
    painel.abrir_o_salvar()
    painel.gravar(Path(painel.tela_salvar.campo.text()))
    painel.voltar_para_escolher()

    assert painel.telas.currentWidget() is painel.tela_escolher
    assert painel.tela_revisao.texto_mascarado() == ""
    # Sem origem, o salvar não tem o que salvar - e não pode gravar o texto do
    # documento anterior por engano (regra RN-19).
    painel.abrir_o_salvar()
    assert painel.telas.currentWidget() is painel.tela_escolher


def test_o_arquivo_e_o_documento_com_as_mascaras_e_nada_mais(tmp_path, aplicacao):
    """O arquivo vem do motor, e não da caixa de leitura da tela.

    A caixa é um desenho: ela troca o separador de linha U+2028, que aparece em
    texto copiado de PDF, por uma quebra comum. Saindo dali, o arquivo ficaria
    diferente do documento num ponto que ninguém mandou mudar (revisão da etapa
    5, 18/09/2026).
    """
    origem = tmp_path / "vindo-de-pdf.md"
    texto = ("Relatório de análise\n"
             "O servidor, CPF 111.111.111-11, entregou a documentação.\n"
             "Página dois\n\fSegue o anexo\n")
    origem.write_text(texto, encoding="utf-8")

    painel = PainelAnonimizar()
    painel.receber_arquivo(origem)
    painel.abrir_o_salvar()
    destino = Path(painel.tela_salvar.campo.text())
    painel.gravar(destino)

    gravado = destino.read_text(encoding="utf-8")
    assert " " in gravado, "o separador de linha do documento se perdeu"
    assert "\f" in gravado, "o avanço de página do documento se perdeu"
    # O arquivo é, letra por letra, o documento com as máscaras no lugar.
    assert gravado == cpf.aplicar(texto, cpf.procurar(texto))
    assert "111.111.111-11" not in gravado


def test_o_arquivo_sai_com_a_quebra_de_linha_do_documento(tmp_path, aplicacao):
    """Documento do Windows sai do jeito que entrou (revisão da etapa 5).

    A leitura passa tudo para a quebra simples, para o resto do programa não
    precisar saber de qual máquina o arquivo veio. Sem devolver a quebra na
    hora de gravar, todo documento escrito no Windows saía com as quebras
    trocadas - mudança que ninguém pediu, num arquivo que promete ser o texto
    do documento com as máscaras e nada mais.
    """
    for nome, quebra in (("do-windows.txt", b"\r\n"), ("simples.md", b"\n")):
        origem = tmp_path / nome
        linhas = ["Relatório de análise",
                  "O servidor, CPF 111.111.111-11, entregou a documentação.",
                  "Fim."]
        origem.write_bytes(quebra.join(linha.encode("utf-8") for linha in linhas)
                           + quebra)

        painel = PainelAnonimizar()
        painel.receber_arquivo(origem)
        painel.abrir_o_salvar()
        destino = Path(painel.tela_salvar.campo.text())
        painel.gravar(destino)

        gravado = destino.read_bytes()
        assert gravado.count(quebra) == 3, nome
        if quebra == b"\n":
            assert b"\r" not in gravado, "apareceu quebra do Windows onde não havia"
        assert b"111.111.111-11" not in gravado

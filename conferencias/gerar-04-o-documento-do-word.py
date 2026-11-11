r"""Gera a página da Conferência 04, abrindo os Words da massa com o programa.

Como as conferências 01 e 03: a página mostra o que o programa DECIDE, e cada
texto dela sai de uma chamada de verdade à leitura do Word e ao motor do CPF.
Mudou a leitura ou a massa, rode isto de novo e a página acompanha. Ela cresce
a cada etapa da funcionalidade 5, e no fim traz o roteiro da conferência na
tela, que a usuária pediu para fazer de uma vez, no fim da construção
(23/10/2026).

Lê só a massa inventada de dados-exemplo/: esta página vai para o histórico.

Rode assim, da raiz do projeto:

    .\.venv\Scripts\python.exe conferencias\gerar-04-o-documento-do-word.py
"""
import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "programa"))

import arquivo_word  # noqa: E402
from arquivo_texto import ArquivoNaoServe  # noqa: E402
from cpf import aplicar, procurar  # noqa: E402
from tela_revisao import FRASE_DAS_ALTERACOES, frase_do_que_ficou_de_fora  # noqa: E402

MASSA = RAIZ / "dados-exemplo"
PRINCIPAL = "18-documento-do-word.docx"
DATA = "26/10/2026"

# As seis etapas da construção, e o que cada uma põe no programa. A coluna da
# situação é mudada à mão a cada etapa fechada: é o registro de onde estamos.
ETAPAS = [
    ("1", "O Word abre no Anonimizar, com o corpo do texto: parágrafos, títulos e listas com marcador", "no programa"),
    ("2", "As tabelas, com barras e colunas alinhadas, a célula mesclada e a de dois parágrafos", "no programa"),
    ("3", "Cabeçalho, rodapé, notas e caixas de texto, cada um no seu lugar", "no programa"),
    ("4", "O que o Word guarda e não imprime, e a faixa azul do que ficou de fora", "no programa"),
    ("5", "As imagens, e a frase de cada Word que não abre", "no programa"),
    ("6", "A lista numerada como o Word mostra, e o roteiro da conferência na tela", "no programa"),
]

# Os outros Words da massa, que não chegam à revisão, com o que cada um testa.
QUE_NAO_ABREM = [
    ("19-nao-e-word.docx", "um arquivo de texto comum com o nome trocado para .docx"),
    ("21-word-so-com-imagens.docx", "duas páginas escaneadas coladas num Word, sem texto nenhum"),
    ("22-word-protegido.docx", "imitação de um Word protegido por senha (o formato por fora, sem o conteúdo)"),
    ("23-doc-antigo-renomeado.docx", "imitação de um .doc antigo com o nome trocado para .docx"),
    ("24-word-vazio.docx", "um Word sem texto e sem imagem"),
    ("25-word-grande-demais.docx", "53 KB compactado, mais de 50 MB de texto descompactado"),
]

# O roteiro da conferência final, para a pessoa fazer na tela: cada passo diz o
# que fazer e o que ela deve ver. Os caminhos tortos estão no meio, e não no
# fim. O número de CPFs é posto na hora, contado do Word de teste.
ROTEIRO = [
    ("Feche o programa se estiver aberto, abra de novo pelo atalho <span class='mono'>abrir\\abrir-dev.bat</span> "
     "e clique em <strong>Anonimizar</strong>.",
     "a área de arrastar dizendo <strong>\"PDF, .docx, .md ou .txt\"</strong>."),
    ("Clique em <strong>Escolher arquivo…</strong>.",
     "a janela de procurar mostra também os <span class='mono'>.docx</span>. Escolha "
     "<span class='mono'>dados-exemplo\\18-documento-do-word.docx</span>."),
    ("Olhe o alto da revisão.",
     "ela abre <strong>direto</strong>, sem leitura nem conferência; a legenda diz "
     "<strong>\"18-documento-do-word.docx — documento do Word\"</strong>; e a <strong>faixa azul</strong>, "
     "logo abaixo, com as duas linhas da tabela \"A faixa da revisão\" desta página."),
    ("Olhe os selos do alto e percorra os números com <strong>próximo ›</strong>.",
     "<strong>{n} CPFs válidos</strong>, todos mascarados, e nenhum suspeito."),
    ("Leia o texto de cima a baixo, comparando com \"O Word de teste, depois do programa\", abaixo.",
     "os dois cabeçalhos no começo; os títulos com <span class='mono'>#</span>; as tabelas com barras e as "
     "colunas retas, inclusive a do Ivo com <span class='mono'>XXX000000XX</span>; a caixa de texto logo depois de "
     "\"Observação da coordenação:\"; as listas com <span class='mono'>a)</span>, <span class='mono'>I.</span> e "
     "<span class='mono'>1.1</span>; o rodapé \"Página 1 de 3\"; e as notas <span class='mono'>[^1]</span> e "
     "<span class='mono'>[^2]</span> no fim."),
    ("<em>Caminho torto:</em> procure no texto por <span class='mono'>888</span>, <span class='mono'>999</span> e "
     "<span class='mono'>555</span>.",
     "nada: o CPF do comentário, o do texto oculto e o da pessoa excluída não aparecem em lugar nenhum. "
     "E do link aparece só \"sistema de bolsas\"."),
    ("Clique em <strong>Salvar o texto mascarado…</strong>.",
     "o caminho sugerido termina em <span class='mono'>18-documento-do-word - sem CPF.md</span>. Troque a pasta "
     "por uma sua (a Área de Trabalho, por exemplo), para o arquivo não ficar na pasta da massa, e grave."),
    ("Abra o arquivo gravado no Bloco de Notas.",
     "o mesmo texto da revisão, mascarado, <strong>sem a faixa</strong> e sem nenhuma linha escrita pelo programa."),
    ("Clique em <strong>Anonimizar outro documento</strong> e <strong>arraste</strong> o mesmo Word para a janela.",
     "a mesma revisão, com a mesma faixa: arrastar funciona como o botão."),
    ("<em>Caminho torto:</em> escolha, um de cada vez, os Words de "
     "<span class='mono'>19</span> e de <span class='mono'>21</span> a <span class='mono'>25</span>.",
     "a tela \"Não foi possível usar este arquivo\" com a frase de cada um — as da tabela \"Os Words que não "
     "abrem\" — e o botão de escolher outro. Nenhum chega à revisão."),
    ("<em>Caminho torto:</em> escolha <span class='mono'>26-documento-com-macro.docm</span> (mude o tipo da janela de "
     "procurar para \"Todos os arquivos\", ou arraste).",
     "a frase de \"outro tipo\": \"O Anonimizar abre PDF, .docx, .md e .txt\"."),
    ("Feche o programa e abra pelo atalho <span class='mono'>abrir\\abrir-sem-nenhum-motor.bat</span>.",
     "na lista do que dá para anonimizar agora, <strong>\"✓ .md, .txt e .docx\"</strong>; e o Word de teste abre "
     "a revisão normalmente, sem motor nenhum."),
    ("No <strong>Gerar OCR</strong>, tente arrastar o Word de teste.",
     "o Gerar OCR continua só com PDF: o Word não é aceito ali."),
    ("Se tiver o Word: abra o <span class='mono'>18-documento-do-word.docx</span> nele, ao lado da revisão.",
     "o que o Word mostra impresso é o que está na revisão; os comentários e o texto oculto, que o Word mostra só "
     "com as marcas ligadas, não estão. Opcional: proteja com senha um Word inventado e escolha-o no programa — a "
     "frase de \"protegido por senha\"."),
]


def e(texto):
    return html.escape(texto)


def destacado(texto, achados):
    """O texto mascarado, com cada troca sublinhada no lugar dela."""
    partes, posicao = [], 0
    for achado in achados:
        partes.append(e(texto[posicao:achado.inicio]))
        partes.append(f'<span class="d-valido">{e(achado.mascara)}</span>')
        posicao = achado.fim + achado.espacos_tirados
    partes.append(e(texto[posicao:]))
    return "".join(partes)


def main():
    word = arquivo_word.ler(MASSA / PRINCIPAL)
    texto = word.texto
    faixa = [f for f in (frase_do_que_ficou_de_fora(word),
                         FRASE_DAS_ALTERACOES if word.alteracoes else "") if f]
    achados = procurar(texto)
    sobra = len(procurar(aplicar(texto, achados)))
    roteiro = "".join(
        f"<li><div>{fazer}</div><div class='ver'>Você deve ver: {ver.format(n=len(achados))}</div></li>"
        for fazer, ver in ROTEIRO)

    linhas_etapas = "".join(
        f"<tr><td>{n}</td><td>{e(o_que)}</td>"
        f"<td class='{'feito' if situacao == 'no programa' else 'falta'}'>{e(situacao)}</td></tr>"
        for n, o_que, situacao in ETAPAS)

    linhas_erros = []
    for nome, o_que_e in QUE_NAO_ABREM:
        try:
            arquivo_word.ler(MASSA / nome)
            frase = "(abriu — e não devia)"
        except ArquivoNaoServe as problema:
            frase = str(problema)
        linhas_erros.append(
            f"<tr><td class='mono'>{e(nome)}</td><td>{e(o_que_e)}</td><td>{e(frase)}</td></tr>")

    pagina = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Conferência 04 — o documento do Word</title>
<style>
  :root {{
    --cor-fundo: #1e2228; --cor-fundo-elevado: #262b33; --cor-borda: #383e47;
    --cor-texto: #e8eaed; --cor-texto-secundario: #9aa1ac; --cor-destaque: #3b6ea5;
    --cor-sucesso: #4caf6d; --cor-erro: #d9534f; --cor-erro-texto: #f08a86;
    --fonte-texto: "Segoe UI", system-ui, sans-serif;
    --fonte-mono: "Cascadia Mono", "Consolas", monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--cor-fundo); color: var(--cor-texto);
         font-family: var(--fonte-texto); font-size: 15px; line-height: 1.55;
         padding: 32px max(16px, calc((100vw - 1040px) / 2)); }}
  h1 {{ font-size: 28px; margin: 0 0 8px; }}
  h2 {{ font-size: 20px; margin: 40px 0 8px; }}
  code {{ font-family: var(--fonte-mono); font-size: 13px; }}
  .subtitulo, .nota {{ color: var(--cor-texto-secundario); }}
  .nota {{ font-size: 13px; }}
  .selos {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }}
  .selo {{ background: var(--cor-fundo-elevado); border: 1px solid var(--cor-borda);
           border-radius: 12px; padding: 2px 12px; font-size: 13px; }}
  .caixa {{ background: var(--cor-fundo-elevado); border: 1px solid var(--cor-borda);
            border-left: 4px solid var(--cor-destaque); border-radius: 6px;
            padding: 16px 24px; margin: 16px 0; }}
  .rolar {{ overflow-x: auto; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
  th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--cor-borda); vertical-align: top; }}
  th {{ color: var(--cor-texto-secundario); font-weight: 600; font-size: 13px; }}
  .mono {{ font-family: var(--fonte-mono); white-space: nowrap; }}
  .feito {{ color: var(--cor-sucesso); font-weight: 600; }}
  .falta {{ color: var(--cor-texto-secundario); }}
  pre.documento {{ font-family: var(--fonte-mono); font-size: 12.5px; background: var(--cor-fundo-elevado);
                   border: 1px solid var(--cor-borda); border-radius: 6px; padding: 16px;
                   overflow-x: auto; white-space: pre; }}
  .d-valido {{ color: var(--cor-erro-texto); text-decoration: underline solid var(--cor-erro-texto); text-underline-offset: 3px; }}
  .faixa {{ background: rgba(59,110,165,0.10); border-left: 4px solid var(--cor-destaque);
            border-radius: 6px; padding: 8px 16px; font-size: 13px; }}
  .faixa div:first-child {{ font-weight: 600; }}
  ol.roteiro li {{ margin-bottom: 14px; }}
  ol.roteiro .ver {{ color: var(--cor-texto-secundario); font-size: 14px; margin-top: 2px; }}
  .rodape {{ margin-top: 40px; border-top: 1px solid var(--cor-borda); padding-top: 16px;
             font-size: 13px; color: var(--cor-texto-secundario); }}
</style>
</head>
<body>

<h1>Conferência 04 — o documento do Word</h1>
<p class="subtitulo">Funcionalidade 5, décima emenda da spec 003. Esta página abre os documentos do Word da
massa com o programa de verdade e mostra o que ele tirou de dentro deles — o texto que vai para a revisão e,
depois, para o <code>.md</code>. Ela cresce a cada etapa; o roteiro da sua conferência na tela entra na última.</p>

<div class="caixa">O Word de teste <code>dados-exemplo/{PRINCIPAL}</code> é inventado e gerado por script
(<code>dados-exemplo/gerar-massa-word.py</code>). Os CPFs que passam na conta são só de dígitos repetidos
(RN-22). Um deles está, de propósito, <strong>partido em três pedaços</strong> dentro do Word, como o Word faz
quando a correção ortográfica passa no meio de um número: só juntando os pedaços na ordem ele aparece inteiro
para a busca — e mascarado no texto.</div>

<h2>Onde a construção está</h2>
<div class="rolar"><table>
  <tr><th>Etapa</th><th>O que ela põe no programa</th><th>Situação</th></tr>
  {linhas_etapas}
</table></div>

<h2>A faixa da revisão</h2>
<p class="nota">Só na tela, no alto da revisão: nada disso vai para o arquivo. O comentário, o texto oculto e o
trecho apagado do Word de teste têm, cada um, um CPF — e nenhum deles aparece no texto abaixo.</p>
<div class="faixa">{"".join(f"<div>{e(f)}</div>" for f in faixa)}</div>

<h2>O Word de teste, depois do programa</h2>
<p class="nota">É este o texto que a revisão mostra, já mascarado. Sublinhado vermelho: CPF válido.</p>
<div class="selos">
  <span class="selo">{len(achados)} números mascarados</span>
  <span class="selo">{sobra} números achados de novo no texto que sai</span>
</div>
<pre class="documento">{destacado(texto, achados)}</pre>

<h2>O roteiro da sua conferência final</h2>
<p class="nota">Feche o programa e abra de novo antes de começar: a janela não troca o código com ela de pé.
Me diga o que apareceu em cada passo, principalmente se foi diferente do que está escrito.</p>
<ol class="roteiro">{roteiro}</ol>

<h2>Os Words que não abrem</h2>
<p class="nota">Cada um volta à escolha do arquivo, com a frase que a tela de erro mostra.</p>
<div class="rolar"><table>
  <tr><th>Arquivo</th><th>O que ele é</th><th>A frase</th></tr>
  {''.join(linhas_erros)}
</table></div>

<p class="rodape">Página gerada em {DATA} pela skill-07-designer-de-telas, a pedido da
skill-08-construtor-de-funcionalidades, a partir do resultado do programa sobre a massa
(<code>conferencias/gerar-04-o-documento-do-word.py</code>). Todos os nomes e números são inventados; os que
passam na conta são só de dígitos repetidos (RN-22).</p>
</body>
</html>
"""
    destino = RAIZ / "conferencias" / "04-o-documento-do-word.html"
    destino.write_text(pagina, encoding="utf-8")
    print(f"gerado: {destino.name} ({len(achados)} números mascarados, {sobra} achados de novo)")


if __name__ == "__main__":
    main()

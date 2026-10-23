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

MASSA = RAIZ / "dados-exemplo"
PRINCIPAL = "18-documento-do-word.docx"
DATA = "23/10/2026"

# As seis etapas da construção, e o que cada uma põe no programa. A coluna da
# situação é mudada à mão a cada etapa fechada: é o registro de onde estamos.
ETAPAS = [
    ("1", "O Word abre no Anonimizar, com o corpo do texto: parágrafos, títulos e listas com marcador", "no programa"),
    ("2", "As tabelas, com barras e colunas alinhadas, a célula mesclada e a de dois parágrafos", "a fazer"),
    ("3", "Cabeçalho, rodapé, notas e caixas de texto, cada um no seu lugar", "a fazer"),
    ("4", "O que o Word guarda e não imprime, e a faixa azul do que ficou de fora", "a fazer"),
    ("5", "As imagens, e a frase de cada Word que não abre", "a fazer"),
    ("6", "A lista numerada como o Word mostra, e o roteiro da conferência na tela", "a fazer"),
]

# Os outros Words da massa, que não chegam à revisão, com o que cada um testa.
QUE_NAO_ABREM = [
    ("19-nao-e-word.docx", "um arquivo de texto comum com o nome trocado para .docx"),
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
    texto = arquivo_word.ler(MASSA / PRINCIPAL)
    achados = procurar(texto)
    sobra = len(procurar(aplicar(texto, achados)))

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

<h2>O Word de teste, depois do programa</h2>
<p class="nota">É este o texto que a revisão mostra, já mascarado. Sublinhado vermelho: CPF válido.</p>
<div class="selos">
  <span class="selo">{len(achados)} números mascarados</span>
  <span class="selo">{sobra} números achados de novo no texto que sai</span>
</div>
<pre class="documento">{destacado(texto, achados)}</pre>

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

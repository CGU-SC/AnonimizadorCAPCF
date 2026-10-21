r"""Gera a página da Conferência 03, rodando o motor do CPF sobre a ficha sem o zero.

Como a Conferência 01: a página mostra o que o programa DECIDE, e cada número
dela sai de uma chamada de verdade ao motor. Mudou o motor ou a massa, rode
isto de novo e a página acompanha. Traz também o roteiro da conferência final
da funcionalidade 6, que a usuária pediu para fazer de uma vez, no fim da
construção (21/10/2026).

Lê só a massa inventada de dados-exemplo/. O formulário real do SIGPEX fica
fora daqui de propósito: esta página vai para o histórico.

Rode assim, da raiz do projeto:

    .\.venv\Scripts\python.exe conferencias\gerar-03-o-cpf-sem-o-zero.py
"""
import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "programa"))

from cpf import aplicar, procurar  # noqa: E402
from dupla_conferencia import _explicacao  # noqa: E402
import tipos_na_tela  # noqa: E402

MASSA = RAIZ / "dados-exemplo"
ARQUIVO = "17-cpf-sem-o-zero.md"
DATA = "21/10/2026"

# O que a ficha tem de propósito e o motor NÃO pode mascarar, com o motivo em
# linguagem de quem lê. Fica escrito aqui porque é decisão da spec, e não algo
# que o programa saiba explicar.
INTEIROS = [
    ("1234567891", "10 dígitos que não fecham a conta com o zero de volta — não é achado nem vira suspeito"),
    ("123456789", "9 dígitos que não fecham a conta com os zeros de volta"),
    ("0000O00000", "letra no lugar de um dígito — o curto estragado pela leitura fica de fora"),
    ("00 000 000 00", "espaços no lugar dos pontos — também fica de fora no curto"),
    ("0000000000/2026", "colado a outro número por uma barra, como num número de processo (RN-3)"),
    ("00.000.000/0000-00", "na forma de um CNPJ: o começo está ligado a mais dígitos (RN-3)"),
    ("00000000", "8 dígitos — o CPF que perdeu três zeros fica de fora"),
]

# O roteiro da conferência final, para a pessoa fazer na tela. Cada passo diz o
# que fazer e o que ela deve ver; os caminhos tortos estão no meio, e não no fim.
ROTEIRO = [
    ("Abra o programa pelo atalho <span class='mono'>abrir\\abrir-dev.bat</span>, clique em "
     "<strong>Anonimizar</strong> e escolha <span class='mono'>dados-exemplo\\17-cpf-sem-o-zero.md</span>.",
     "a revisão abre com <strong>10 números encontrados</strong> e <strong>10 CPFs válidos</strong>, e nenhum suspeito."),
    ("Olhe a tabela de bolsistas no texto.",
     "<span class='mono'>XXX000000XX</span> e <span class='mono'>XXX.000.000-XX</span> em vermelho, com traço reto, "
     "e a coluna do valor <strong>reta</strong>, igual à linha da Ana."),
    ("Olhe a lista à direita.",
     "cada curto com <strong>\"CPF válido\"</strong> e, ao lado, <strong>\"sem o zero da frente\"</strong> — ou "
     "<strong>\"sem os zeros da frente\"</strong> nos de 9 dígitos. O número aparece como está no documento."),
    ("Clique em <strong>próximo ›</strong> até dar a volta.",
     "o texto vai de número em número, o item certo acende na lista, e a contagem vai de 1 a 10."),
    ("<em>Caminho torto:</em> no curto do <strong>telefone do escritório</strong>, clique em "
     "<strong>Desfazer…</strong> e aperte <strong>Enter</strong>.",
     "a caixa vermelha mostra <span class='mono'>0000000000</span>, fala do zero perdido e do <strong>telefone com "
     "DDD</strong>, e o Enter <strong>mantém</strong> a máscara."),
    ("Desfaça de novo e clique em <strong>Liberar mesmo assim</strong>.",
     "o texto volta a <span class='mono'>0000000000 ramal 2.</span>, verde e tracejado; na lista, as três etiquetas "
     "(cinza, cinza e a verde \"liberado\") <strong>numa linha só</strong>."),
    ("Faça o mesmo no curto das <strong>parcelas</strong> (9 dígitos, com o 12 embaixo).",
     "a caixa fala do <strong>celular escrito sem o DDD</strong>; liberado, a etiqueta \"liberado\" "
     "<strong>desce</strong> para a linha de baixo — a de 9 é mais comprida."),
    ("Clique em <strong>Mascarar de novo</strong> no das parcelas.",
     "ele volta a <span class='mono'>XXX000000XX</span>, com o 12 inteiro na linha de baixo."),
    ("<em>Caminho torto:</em> marque com o mouse o <span class='mono'>1234567891</span> do fornecedor e "
     "clique em <strong>Mascarar o trecho marcado</strong>.",
     "ele vira <span class='mono'>XXX45678XX</span>, destacado no lugar certo — e não ao lado, empurrado pelos curtos de cima."),
    ("Confira a última frase, a do \"Não são CPF\".",
     "nenhum destaque: os sete números ficam inteiros (a tabela abaixo diz por quê)."),
    ("Clique em <strong>Salvar o texto mascarado…</strong>.",
     "antes de gravar, o aviso lista o telefone, que ficou liberado, como \"CPF válido\"."),
    ("Grave e abra o arquivo no Bloco de Notas.",
     "a tabela alinhada, os curtos com 11 dígitos de volta, e o telefone inteiro, porque você o liberou."),
    ("Por último, o documento de verdade: no Anonimizar, escolha "
     "<span class='mono'>dados-reais\\01 - SIGPEX.pdf</span> e aproveite o texto de dentro.",
     "os <strong>6</strong> CPFs de 10 dígitos aparecem mascarados, com a etiqueta \"sem o zero da frente\", "
     "e nenhum fica inteiro no texto."),
]


def e(texto):
    return html.escape(texto)


def mostra(texto):
    return e(texto).replace("\n", '<span class="quebra">↵</span>')


def etiquetas(achado):
    partes = ['<span class="etq valido">CPF válido</span>']
    if achado.sem_zero:
        partes.append(
            f'<span class="etq valido">{e(tipos_na_tela.SEM_ZERO[achado.sem_zero].nome)}</span>')
    return " ".join(partes)


def main():
    texto = (MASSA / ARQUIVO).read_text(encoding="utf-8")
    achados = procurar(texto)
    saida = aplicar(texto, achados)

    # O texto mascarado, com cada troca destacada no lugar dela. O curto cresce
    # na máscara e leva junto os espaços tirados depois dele, por isso o texto
    # recomeça depois desses espaços, e não no fim do número.
    partes, posicao = [], 0
    for achado in achados:
        partes.append(e(texto[posicao:achado.inicio]))
        partes.append(f'<span class="d-valido">{e(achado.mascara)}</span>')
        posicao = achado.fim + achado.espacos_tirados
    partes.append(e(texto[posicao:]))
    texto_destacado = "".join(partes)

    linhas = "".join(
        f"<tr><td class='mono'>{mostra(a.original)}</td>"
        f"<td class='mono forte'>{mostra(a.mascara)}</td>"
        f"<td>{etiquetas(a)}</td>"
        f"<td>{'sim — caixa vermelha antes de liberar' if a.pede_dupla_conferencia else 'não'}</td></tr>"
        for a in achados)
    linhas_inteiros = "".join(
        f"<tr><td class='mono'>{e(numero)}</td><td>{e(porque)}</td></tr>"
        for numero, porque in INTEIROS)
    caixas = "".join(
        f"<div class='caixa-dupla'><div class='mono forte'>{e(a.original)}</div>"
        f"<p>{e(_explicacao(a))}</p></div>"
        for a in (achados[1], achados[2]))
    roteiro = "".join(
        f"<li><div>{fazer}</div><div class='ver'>Você deve ver: {ver}</div></li>"
        for fazer, ver in ROTEIRO)

    n_curtos = sum(1 for a in achados if a.sem_zero)
    n_tirados = sum(a.espacos_tirados for a in achados)
    sobra = len(procurar(saida))

    pagina = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Conferência 03 — o CPF sem o zero da frente</title>
<style>
  :root {{
    --cor-fundo: #1e2228; --cor-fundo-elevado: #262b33; --cor-borda: #383e47;
    --cor-texto: #e8eaed; --cor-texto-secundario: #9aa1ac; --cor-destaque: #3b6ea5;
    --cor-erro: #d9534f; --cor-erro-texto: #f08a86;
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
  .caixas-duplas {{ display: flex; gap: 16px; flex-wrap: wrap; }}
  .caixa-dupla {{ flex: 1; min-width: 280px; background: rgba(217,83,79,0.10);
                  border-left: 4px solid var(--cor-erro); border-radius: 6px; padding: 12px 20px; }}
  .caixa-dupla p {{ color: var(--cor-texto-secundario); font-size: 13px; margin: 8px 0 0; }}
  .rolar {{ overflow-x: auto; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
  th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--cor-borda); vertical-align: top; }}
  th {{ color: var(--cor-texto-secundario); font-weight: 600; font-size: 13px; }}
  .mono {{ font-family: var(--fonte-mono); white-space: nowrap; }}
  .forte {{ font-weight: 600; }}
  .quebra {{ color: var(--cor-texto-secundario); padding: 0 4px; }}
  .etq {{ display: inline-block; font-size: 12px; font-weight: 600; border-radius: 10px;
          padding: 1px 8px; margin: 1px 0; }}
  .etq.valido {{ border: 1px solid var(--cor-erro-texto); color: var(--cor-erro-texto); }}
  pre.documento {{ font-family: var(--fonte-mono); font-size: 12.5px; background: var(--cor-fundo-elevado);
                   border: 1px solid var(--cor-borda); border-radius: 6px; padding: 16px;
                   overflow-x: auto; white-space: pre; }}
  .d-valido {{ color: var(--cor-erro-texto); text-decoration: underline solid var(--cor-erro-texto); text-underline-offset: 3px; }}
  ol.roteiro li {{ margin-bottom: 14px; }}
  ol.roteiro .ver {{ color: var(--cor-texto-secundario); font-size: 14px; margin-top: 2px; }}
  .rodape {{ margin-top: 40px; border-top: 1px solid var(--cor-borda); padding-top: 16px;
             font-size: 13px; color: var(--cor-texto-secundario); }}
</style>
</head>
<body>

<h1>Conferência 03 — o CPF sem o zero da frente</h1>
<p class="subtitulo">Funcionalidade 6, nona emenda da spec 003. Esta página mostra o que o programa decidiu
sobre cada número da ficha <code>dados-exemplo/{ARQUIVO}</code> — ela foi montada rodando o programa de
verdade, e não escrita à mão — e traz o roteiro da sua conferência final, na tela.</p>

<div class="caixa">Todo curto que fecha a conta nesta ficha é <strong>só de zeros</strong>: é o único jeito de
um número curto fechar a conta sem poder ser o CPF de alguém (RN-22). Na tela, o formato com outros dígitos
fica igual: os três primeiros e os dois últimos viram <code>X</code>, e os zeros da frente voltam.</div>

<h2>A ficha, depois do motor</h2>
<p class="nota">Sublinhado reto e vermelho: CPF válido. Os números sem destaque ficaram inteiros de propósito.
O ↵ marca a quebra de linha.</p>
<div class="selos">
  <span class="selo">{len(achados)} números mascarados</span>
  <span class="selo">{n_curtos} sem o zero da frente</span>
  <span class="selo">{n_tirados} espaços tirados para a coluna ficar reta</span>
  <span class="selo">{sobra} números achados de novo no texto que sai</span>
</div>
<pre class="documento">{texto_destacado}</pre>

<h2>Cada número, antes e depois</h2>
<div class="rolar"><table>
  <tr><th>Como estava</th><th>Como ficou</th><th>O que a lista diz</th><th>Desfazer pede confirmação?</th></tr>
  {linhas}
</table></div>

<h2>O que ficou inteiro, e por quê</h2>
<div class="rolar"><table>
  <tr><th>No texto</th><th>Por que não foi mascarado</th></tr>
  {linhas_inteiros}
</table></div>

<h2>A explicação da dupla conferência</h2>
<p class="nota">O texto que a caixa vermelha mostra ao desfazer um curto — com 10 dígitos e com 9. Saiu da
revisão 34: o de 9 dígitos fala do celular sem o DDD, porque telefone com DDD nunca tem 9 dígitos.</p>
<div class="caixas-duplas">{caixas}</div>

<h2>O roteiro da sua conferência final</h2>
<p class="nota">Feche o programa e abra de novo antes de começar: a janela não troca o código com ela de pé.</p>
<ol class="roteiro">{roteiro}</ol>

<p class="rodape">Página gerada em {DATA} pela skill-07-designer-de-telas, a pedido da
skill-08-construtor-de-funcionalidades, a partir do resultado do motor sobre a massa
(<code>conferencias/gerar-03-o-cpf-sem-o-zero.py</code>). Todos os nomes e números são inventados; os que
passam na conta são só de dígitos repetidos, e os curtos, só de zeros (RN-22).</p>
</body>
</html>
"""
    destino = RAIZ / "conferencias" / "03-o-cpf-sem-o-zero.html"
    destino.write_text(pagina, encoding="utf-8")
    print(f"gerado: {destino.name} ({len(achados)} números mascarados, {n_curtos} curtos, "
          f"{sobra} achados de novo no texto que sai)")


if __name__ == "__main__":
    main()

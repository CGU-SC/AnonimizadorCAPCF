r"""Gera a página da Conferência 01, rodando o motor do CPF sobre a massa.

A página mostra o que o programa DECIDE, e não o que alguém acha que ele
decide: cada número dela sai de uma chamada de verdade ao motor. Por isso ela
tem um script, e não é escrita à mão - mudou o motor ou a massa, rode isto de
novo e a página acompanha.

Rode assim, da raiz do projeto:

    .\.venv\Scripts\python.exe conferencias\gerar-01-o-motor-do-cpf-na-massa.py
"""
import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "programa"))

from cpf import FALHA_NA_CONTA, PASSA_NA_CONTA, procurar  # noqa: E402

MASSA = RAIZ / "dados-exemplo"
DATA = "16/09/2026"

# O que a massa tem de propósito e o motor NÃO pode mascarar, com o motivo em
# linguagem de quem lê. Fica escrito aqui porque é uma decisão da spec, e não
# algo que o programa saiba explicar.
INTEIROS = [
    ("12.345.678/0001-90",
     "CNPJ — os números estão ligados a outros dígitos por ponto, barra e traço (RN-3)"),
    ("23080.012345/2026-11",
     "número de processo — mais de 11 dígitos, ligados entre si (RN-3)"),
    ("34191.79001 01043.510047 91020.150008 1 89410000026000",
     "linha do boleto — nenhum pedaço tem a forma solta de um CPF (RN-3)"),
    ("9111.111.111-11", "um 9 colado antes do número — não é CPF (RN-3)"),
    ("111.111.111-119", "um 9 colado depois do número — não é CPF (RN-3)"),
    ("l234S67891O",
     "três letras e nenhuma pontuação — sem separador, a sequência tem cara de "
     "código (quarta emenda)"),
    ("lZ3.4S6.7B9-1O",
     "cinco letras, mesmo com pontuação — o limite com ponto, traço ou barra é "
     "4 das 11 posições (quarta emenda)"),
    ("SOL.IDA.DES-OS",
     "letras que não se confundem com dígito — A, E e L não estão na lista das "
     "que a leitura troca por número"),
    ("1234 5678 910",
     "não tem a forma de um CPF (grupos de 4, 4 e 3) — é o caso de mascarar à "
     "mão, na etapa 4"),
    ("R$ 1.500,00 · 03/08/2026 · 042/2026", "valores, datas e números de projeto"),
]

CONFERIR = [
    'Na coluna "como ficou", <strong>nenhum número mostra os 3 primeiros nem os 2 últimos dígitos</strong>.',
    'A pontuação de cada número ficou a mesma, menos a barra antes dos dois últimos, que virou traço '
    '(<span class="mono">333.333.333/34</span> → <span class="mono">***.333.333-**</span>).',
    'O Pedro, partido em duas linhas, aparece mascarado <strong>nas duas partes</strong>, e a quebra ficou onde estava.',
    'Na tabela de bolsistas do documento, as colunas continuam alinhadas depois da máscara.',
    'O CNPJ, o processo, o boleto e os números colados a outro dígito saíram inteiros.',
    'Os "quase CPF" que passam na conta (<span class="mono">l11.111.111-11</span>, o do Pedro e '
    '<span class="mono">666 666 666 66</span>) levam a etiqueta "CPF válido" e pedem a dupla conferência.',
    'O <span class="mono">l23.4S6.789-1O</span> e o <span class="mono">l23.4S6.7B9-1O</span>, com três e '
    'quatro letras <strong>e pontuação de CPF</strong>, aparecem mascarados (quarta emenda); o '
    '<span class="mono">l234S67891O</span>, com três letras e nenhuma pontuação, e o '
    '<span class="mono">lZ3.4S6.7B9-1O</span>, com cinco letras, continuam inteiros.',
]


def e(texto):
    return html.escape(texto)


def mostra(texto):
    return e(texto).replace("\n", '<span class="quebra">↵</span>')


def rotulo(achado):
    if achado.tipo == PASSA_NA_CONTA:
        return '<span class="etq valido">CPF válido</span>'
    if achado.tipo == FALHA_NA_CONTA:
        return '<span class="etq suspeito">suspeito · falha na conta</span>'
    extra = ' <span class="etq valido">CPF válido</span>' if achado.passa_na_conta else ""
    return f'<span class="etq suspeito">quase CPF · {e(achado.motivo)}</span>{extra}'


def main():
    texto = (MASSA / "10-prestacao-com-cpf.md").read_text(encoding="utf-8")
    achados = procurar(texto)
    bolsistas = procurar(
        (MASSA / "14-folha-com-40-bolsistas.md").read_text(encoding="utf-8"))
    anonimizado = procurar(
        (MASSA / "10-prestacao-com-cpf - sem CPF.md").read_text(encoding="utf-8"))
    sem_cpf = procurar((MASSA / "11-sem-cpf.md").read_text(encoding="utf-8"))

    linhas = []
    for achado in achados:
        dupla = ("sim — caixa vermelha antes de liberar"
                 if achado.pede_dupla_conferencia else "não — um clique")
        linhas.append(
            f"<tr><td class='mono'>{mostra(achado.original)}</td>"
            f"<td class='mono forte'>{mostra(achado.mascara)}</td>"
            f"<td>{rotulo(achado)}</td><td>{dupla}</td></tr>")

    linhas_inteiros = "".join(
        f"<tr><td class='mono'>{e(numero)}</td><td>{e(porque)}</td></tr>"
        for numero, porque in INTEIROS)

    # O texto mascarado, com cada troca destacada no lugar dela - o mesmo
    # desenho que a tela de revisão usa.
    partes, posicao = [], 0
    for achado in achados:
        partes.append(e(texto[posicao:achado.inicio]))
        classe = "d-valido" if achado.tipo == PASSA_NA_CONTA else "d-suspeito"
        partes.append(f'<span class="{classe}">{e(achado.mascara)}</span>')
        posicao = achado.fim
    partes.append(e(texto[posicao:]))
    texto_destacado = "".join(partes)

    validos_40 = sum(1 for a in bolsistas if a.tipo == PASSA_NA_CONTA)
    falha_40 = sum(1 for a in bolsistas if a.tipo == FALHA_NA_CONTA)
    n_suspeitos = sum(1 for a in achados if a.suspeito)
    n_validos = sum(1 for a in achados if a.tipo == PASSA_NA_CONTA)
    n_dupla = sum(1 for a in achados if a.pede_dupla_conferencia)
    conferir = "".join(f"<li>{item}</li>" for item in CONFERIR)

    pagina = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Conferência 01 — o motor do CPF na massa</title>
<style>
  :root {{
    --cor-fundo: #1e2228; --cor-fundo-elevado: #262b33; --cor-borda: #383e47;
    --cor-texto: #e8eaed; --cor-texto-secundario: #9aa1ac; --cor-destaque: #3b6ea5;
    --cor-alerta: #d9a441; --cor-erro-texto: #f08a86;
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
  .forte {{ font-weight: 600; }}
  .quebra {{ color: var(--cor-texto-secundario); padding: 0 4px; }}
  .etq {{ display: inline-block; font-size: 12px; font-weight: 600; border-radius: 10px;
          padding: 1px 8px; margin: 1px 0; color: var(--cor-alerta); }}
  .etq.valido {{ border: 1px solid var(--cor-erro-texto); color: var(--cor-erro-texto); }}
  .etq.suspeito {{ border: 1px dashed var(--cor-alerta); }}
  pre.documento {{ font-family: var(--fonte-mono); font-size: 12.5px; background: var(--cor-fundo-elevado);
                   border: 1px solid var(--cor-borda); border-radius: 6px; padding: 16px;
                   overflow-x: auto; white-space: pre; }}
  .d-valido {{ color: var(--cor-erro-texto); text-decoration: underline solid var(--cor-erro-texto); text-underline-offset: 3px; }}
  .d-suspeito {{ color: var(--cor-alerta); text-decoration: underline wavy var(--cor-alerta); text-underline-offset: 3px; }}
  ol li {{ margin-bottom: 8px; }}
  .rodape {{ margin-top: 40px; border-top: 1px solid var(--cor-borda); padding-top: 16px;
             font-size: 13px; color: var(--cor-texto-secundario); }}
</style>
</head>
<body>

<h1>Conferência 01 — o motor do CPF na massa</h1>
<p class="subtitulo">Anonimizador de CPF (spec 003). Esta página mostra o que a peça do programa que
acha, confere e mascara o CPF decidiu sobre cada número da massa de teste. Ela foi montada rodando o
programa de verdade sobre os arquivos de <code>dados-exemplo/</code>, e não escrita à mão.</p>

<div class="caixa"><strong>Atualizada em {DATA}, com a quarta emenda da spec.</strong> Quantas letras no
lugar de dígito um "quase CPF" aceita passa a depender da pontuação: até 4 com ponto, traço ou barra
separando os grupos, e 2 sem separador nenhum ou só com espaços.</div>

<h2>O documento principal, depois do motor</h2>
<p class="nota">É o <code>10-prestacao-com-cpf.md</code> — o mesmo documento do rascunho de tela 01.
Sublinhado reto e vermelho: CPF válido. Ondulado e amarelo: suspeito. Os números sem destaque ficaram inteiros de
propósito.</p>
<div class="selos">
  <span class="selo">{len(achados)} números mascarados</span>
  <span class="selo">{n_suspeitos} suspeitos</span>
  <span class="selo">{n_validos} com CPF válido fora dos suspeitos</span>
  <span class="selo">{n_dupla} pedem a dupla conferência para liberar</span>
</div>
<pre class="documento">{texto_destacado}</pre>

<h2>Cada número, antes e depois</h2>
<p class="nota">O "como estava" só aparece aqui e na lista da tela de revisão, para a pessoa decidir
olhando o original. O arquivo gravado leva só o "como ficou". O ↵ marca a quebra de linha.</p>
<div class="rolar"><table>
  <tr><th>Como estava</th><th>Como ficou</th><th>O que o programa decidiu</th><th>Desfazer pede confirmação?</th></tr>
  {"".join(linhas)}
</table></div>

<h2>O que ficou inteiro, e por quê</h2>
<div class="rolar"><table>
  <tr><th>No texto</th><th>Por que não foi mascarado</th></tr>
  {linhas_inteiros}
</table></div>

<h2>Os outros arquivos da massa</h2>
<div class="rolar"><table>
  <tr><th>Arquivo</th><th>O que o motor achou</th></tr>
  <tr><td class="mono">14-folha-com-40-bolsistas.md</td><td>{len(bolsistas)} números: {validos_40} com CPF válido e {falha_40} que falham na conta</td></tr>
  <tr><td class="mono">10-prestacao-com-cpf - sem CPF.md</td><td>{len(anonimizado)} números — o arquivo já anonimizado, aberto de novo, não tem CPF</td></tr>
  <tr><td class="mono">11-sem-cpf.md</td><td>{len(sem_cpf)} números — ata com CNPJ, processo e valores</td></tr>
</table></div>

<h2>O que conferir nesta página</h2>
<ol>{conferir}</ol>

<p class="rodape">Página gerada em {DATA} pela skill-07-designer-de-telas, a pedido da
skill-08-construtor-de-funcionalidades, a partir do resultado do motor sobre a massa
(<code>conferencias/gerar-01-o-motor-do-cpf-na-massa.py</code>). Todos os nomes e números são
inventados; os que passam na conta são só de dígitos repetidos (RN-22).</p>
</body>
</html>
"""
    destino = RAIZ / "conferencias" / "01-o-motor-do-cpf-na-massa.html"
    destino.write_text(pagina, encoding="utf-8")
    print(f"gerado: {destino.name} ({len(achados)} números mascarados)")


if __name__ == "__main__":
    main()

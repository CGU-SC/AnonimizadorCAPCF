r"""Gera a página da Conferência 02: os motores de leitura lado a lado.

A funcionalidade 7 põe o PaddleOCR na escolha do motor, e a solicitante decidiu
medir antes de construir: se ele não ler melhor que o Tesseract, a decisão de
ele vir marcado volta para ela. Esta página é essa medição. Cada número sai das
leituras gravadas pelo `ler-com-o-motor.py`, comparadas com o gabarito -
inclusive os do veredito, que só tem as frases escritas à mão.

Duas fontes, tratadas de jeitos diferentes:

- as páginas difíceis inventadas (`dados-exemplo/20-paginas-dificeis.pdf`), em
  que o gabarito é o texto desenhado. Aqui a página mostra o que cada motor
  leu em cada CPF, porque os números são inventados;
- o documento real desta máquina (`dados-reais/01 - SIGPEX.pdf`), em que o
  gabarito é o texto que já vem dentro do PDF. Dele a página mostra SÓ
  CONTAGENS: nenhum trecho, nenhum CPF, nenhum nome. A página entra no
  histórico, e documento real não entra.

Rode assim, da raiz do projeto, depois das leituras:

    .\.venv\Scripts\python.exe conferencias\gerar-02-os-motores-de-leitura.py
"""
import difflib
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "programa"))

import pymupdf  # noqa: E402

from cpf import LETRA_PARECIDA_COM_DIGITO, procurar  # noqa: E402

DATA = "13/10/2026"
MASSA = RAIZ / "dados-exemplo" / "20-paginas-dificeis.pdf"
GABARITO_DA_MASSA = RAIZ / "dados-exemplo" / "20-paginas-dificeis.gabarito.json"
REAL = RAIZ / "dados-reais" / "01 - SIGPEX.pdf"
LEITURAS_DA_MASSA = RAIZ / "conferencias" / "leituras-02"
LEITURAS_DO_REAL = RAIZ / "dados-reais" / "leituras-02"

MOTORES = [
    ("tesseract", "Tesseract", "o de hoje"),
    ("paddleocr", "PaddleOCR oficial", "PP-OCRv6 médio"),
    ("rapidocr", "RapidOCR pequeno", "PP-OCRv6 pequeno, vem no pacote"),
    ("rapidocr-medio", "RapidOCR médio", "PP-OCRv6 médio"),
]

# Até quantos dígitos trocados um número lido ainda é "o mesmo CPF, lido com
# erro". O programa mascara qualquer número com forma de CPF, mesmo que falhe na
# conta (RN-5 da spec 003) - então um CPF com um ou dois dígitos trocados ainda
# sai mascarado, como suspeito. Acima de três trocas já não dá para dizer que
# é o mesmo número.
TROCAS_QUE_AINDA_SAO_O_MESMO = 3

def e(texto):
    return html.escape(str(texto))


def digitos(original):
    return "".join(LETRA_PARECIDA_COM_DIGITO.get(c, c) for c in original
                   if c.isdigit() or c in LETRA_PARECIDA_COM_DIGITO)


def palavras(texto):
    return re.findall(r"\w+", texto)


def palavras_certas(gabarito, leitura):
    """De cada cem palavras do gabarito, quantas o motor leu igualzinho.

    Conta palavra, e não ordem: os motores devolvem as colunas de uma tabela
    em ordens diferentes, e a ordem não muda se o CPF sai mascarado. O que
    importa é a palavra ter sido lida.
    """
    esperadas = Counter(palavras(gabarito))
    lidas = Counter(palavras(leitura))
    total = sum(esperadas.values())
    if not total:
        return None
    return 100 * sum((esperadas & lidas).values()) / total


def destino_dos_cpfs(gabarito, leitura):
    """Para cada CPF do gabarito: lido certo, lido trocado, ou escaparia.

    "Escaparia" é o que importa para o programa existir: o número não foi
    reconhecido como CPF na leitura, e por isso sairia sem máscara.
    """
    lidos = [(o.original, digitos(o.original)) for o in procurar(leitura)]
    usados = set()
    resultado = []
    for ocorrencia in procurar(gabarito):
        esperado = digitos(ocorrencia.original)
        melhor, trocas = None, None
        for indice, (_original, achado) in enumerate(lidos):
            if indice in usados or len(achado) != len(esperado):
                continue
            diferenca = sum(a != b for a, b in zip(achado, esperado))
            if trocas is None or diferenca < trocas:
                melhor, trocas = indice, diferenca
        if melhor is not None and trocas <= TROCAS_QUE_AINDA_SAO_O_MESMO:
            usados.add(melhor)
            situacao = "certo" if trocas == 0 else "trocado"
            resultado.append((ocorrencia.original, lidos[melhor][0], situacao))
        else:
            resultado.append((ocorrencia.original, None, "escaparia"))
    return resultado


def ler_json(pasta, motor):
    caminho = pasta / f"{motor}.json"
    if not caminho.exists():
        return None
    return json.loads(caminho.read_text(encoding="utf-8"))


def medir(gabaritos, leitura, documento):
    """Junta as contas de um motor sobre um documento inteiro.

    Antes de contar, confere se a leitura é deste documento e tem as mesmas
    páginas do gabarito. Sem isso, uma leitura feita antes de a massa ganhar
    uma página era emparelhada até onde dava, e a página que faltava sumia da
    conta calada - o motor parecia melhor do que é (lente crítica, 16/10/2026).
    """
    if leitura is None:
        return None
    paginas = leitura["paginas"]
    if leitura["documento"] != documento or len(paginas) != len(gabaritos):
        return {"desatualizada": True}
    por_pagina, cpfs = [], []
    for gabarito, pagina in zip(gabaritos, paginas):
        destinos = destino_dos_cpfs(gabarito, pagina["texto"])
        cpfs.extend(destinos)
        por_pagina.append({
            "palavras": palavras_certas(gabarito, pagina["texto"]),
            "destinos": destinos,
            "segundos": pagina["segundos"],
            "falha": pagina["falha"],
        })
    contagem = Counter(situacao for _g, _l, situacao in cpfs)
    validas = [p["palavras"] for p in por_pagina if p["palavras"] is not None]
    return {
        "por_pagina": por_pagina,
        "cpfs": len(cpfs),
        "certo": contagem["certo"],
        "trocado": contagem["trocado"],
        "escaparia": contagem["escaparia"],
        "palavras": sum(validas) / len(validas) if validas else None,
        "segundos": sum(p["segundos"] for p in por_pagina) / len(por_pagina),
        "falhas": sum(1 for p in por_pagina if p["falha"]),
        "rede": len(leitura["tentativas_de_rede"]),
        "sem_rede": leitura["sem_rede"],
        "preparar": leitura["segundos_para_preparar"],
    }


def fora(medida):
    """O que a célula diz quando não há número para mostrar, ou None."""
    if medida is None:
        return "não rodou"
    if medida.get("desatualizada"):
        return "leitura desatualizada — refazer"
    return None


def tamanho_da_pasta(pasta):
    if not pasta.exists():
        return None
    return sum(f.stat().st_size for f in pasta.rglob("*") if f.is_file())


def mb(octetos):
    return "—" if octetos is None else f"{octetos / 1e6:,.0f} MB".replace(",", ".")


def porcento(valor):
    return "—" if valor is None else f"{valor:.0f}".replace(".", ",")


def segundos(valor):
    return f"{valor:.1f} s".replace(".", ",")


def celula_de_cpfs(medida):
    if fora(medida):
        return f"<td class='apagado'>{fora(medida)}</td>"
    escaparia = medida["escaparia"]
    classe = "ruim" if escaparia else "bom"
    return (f"<td><span class='forte'>{medida['certo']}</span> de {medida['cpfs']} certos"
            f"<br><span class='nota'>{medida['trocado']} com dígito trocado</span>"
            f"<br><span class='{classe}'>{escaparia} escapariam</span></td>")


def tabela_resumo(medidas, titulo_da_coluna):
    def linha(rotulo, explicacao, montar):
        celulas = "".join(f"<td class='apagado'>{fora(m)}</td>" if fora(m) else montar(m)
                          for m in medidas)
        return (f"<tr><th scope='row'>{rotulo}<br><span class='nota'>{explicacao}</span></th>"
                f"{celulas}</tr>")

    cabecalho = "".join(f"<th>{e(nome)}<br><span class='nota'>{e(detalhe)}</span></th>"
                        for _chave, nome, detalhe in MOTORES)
    linhas = [
        f"<tr><th>{titulo_da_coluna}</th>{cabecalho}</tr>",
        "<tr><th scope='row'>CPFs<br><span class='nota'>do gabarito</span></th>"
        + "".join(celula_de_cpfs(m) for m in medidas) + "</tr>",
        linha("Palavras lidas certas", "de cada cem, em média por página",
              lambda m: f"<td class='forte'>{porcento(m['palavras'])}</td>"),
        linha("Tempo por página", "média, nesta máquina",
              lambda m: f"<td>{segundos(m['segundos'])}</td>"),
        linha("Para começar", "carregar o motor, uma vez por leitura",
              lambda m: f"<td>{segundos(m['preparar'])}</td>"),
        linha("Páginas que falharam", "a leitura estourou",
              lambda m: f"<td class='{'ruim' if m['falhas'] else ''}'>{m['falhas']}</td>"),
        linha("Tentativas de conexão", "pela parte em Python, com a rede fechada",
              lambda m: f"<td class='{'ruim' if m['rede'] else 'bom'}'>{m['rede']}</td>"
              if m["sem_rede"] else "<td class='ruim'>medido com a rede aberta</td>"),
    ]
    return "<div class='rolar'><table>" + "".join(linhas) + "</table></div>"


def tabela_pagina_a_pagina(gabarito, medidas):
    linhas = ["<tr><th>Página</th>" + "".join(f"<th>{e(nome)}</th>"
                                              for _c, nome, _d in MOTORES) + "</tr>"]
    for indice, pagina in enumerate(gabarito):
        celulas = []
        for medida in medidas:
            if fora(medida):
                celulas.append(f"<td class='apagado'>{fora(medida)}</td>")
                continue
            dados = medida["por_pagina"][indice]
            contagem = Counter(s for _g, _l, s in dados["destinos"])
            total = len(dados["destinos"])
            falha = "<br><span class='ruim'>falhou</span>" if dados["falha"] else ""
            escaparam = (f"<br><span class='ruim'>{contagem['escaparia']} escapariam</span>"
                         if contagem["escaparia"] else "")
            celulas.append(
                f"<td><span class='forte'>{porcento(dados['palavras'])}</span>"
                f" <span class='nota'>palavras</span>"
                f"<br>{contagem['certo']} de {total} CPFs certos{escaparam}"
                f"<br><span class='nota'>{segundos(dados['segundos'])}</span>{falha}</td>")
        linhas.append(f"<tr><th scope='row'>{e(pagina['o_que_testa'])}</th>"
                      + "".join(celulas) + "</tr>")
    return "<div class='rolar'><table>" + "".join(linhas) + "</table></div>"


def tabela_dos_erros(gabarito, medidas):
    """O que cada motor leu em cada CPF que algum deles errou.

    Só a massa inventada aparece aqui: os números são de dígitos repetidos ou
    falham na conta, e não são de ninguém.
    """
    linhas = ["<tr><th>Página</th><th>No papel</th>"
              + "".join(f"<th>{e(nome)}</th>" for _c, nome, _d in MOTORES) + "</tr>"]
    for indice, pagina in enumerate(gabarito):
        quantos = len(procurar(pagina["texto"]))
        for posicao in range(quantos):
            leituras = []
            for medida in medidas:
                if fora(medida):
                    leituras.append(None)
                    continue
                leituras.append(medida["por_pagina"][indice]["destinos"][posicao])
            if all(l is not None and l[2] == "certo" for l in leituras):
                continue
            no_papel = next(l[0] for l in leituras if l is not None)
            celulas = []
            for leitura in leituras:
                if leitura is None:
                    celulas.append("<td class='apagado'>—</td>")
                elif leitura[2] == "certo":
                    celulas.append("<td class='bom'>certo</td>")
                elif leitura[2] == "trocado":
                    celulas.append(f"<td class='mono aviso'>{e(leitura[1])}</td>")
                else:
                    celulas.append("<td class='ruim'>escaparia</td>")
            linhas.append(f"<tr><td class='nota'>{e(pagina['pagina'])}</td>"
                          f"<td class='mono'>{e(no_papel)}</td>" + "".join(celulas) + "</tr>")
    if len(linhas) == 1:
        return "<p>Nenhum motor errou nenhum CPF das páginas inventadas.</p>"
    return "<div class='rolar'><table>" + "".join(linhas) + "</table></div>"


def tabela_do_peso():
    paddle = RAIZ / ".venv-paddleocr" / "Lib" / "site-packages"
    rapid = RAIZ / ".venv-rapidocr" / "Lib" / "site-packages"
    modelos_rapid = rapid / "rapidocr" / "models"
    medio = sum((modelos_rapid / nome).stat().st_size
                for nome in ("PP-OCRv6_det_medium.onnx", "PP-OCRv6_rec_medium.onnx")
                if (modelos_rapid / nome).exists())
    pequeno = sum((modelos_rapid / nome).stat().st_size
                  for nome in ("PP-OCRv6_det_small.onnx", "PP-OCRv6_rec_small.onnx",
                               "ch_ppocr_mobile_v2.0_cls_mobile.onnx")
                  if (modelos_rapid / nome).exists())
    tudo_rapid = tamanho_da_pasta(rapid)
    linhas = [
        ("PaddleOCR oficial", mb(tamanho_da_pasta(paddle)),
         mb(tamanho_da_pasta(RAIZ / ".modelos-medicao" / "paddlex")),
         "o PaddlePaddle sozinho é perto de 400 MB; puxa também clientes de "
         "sites de modelos (Hugging Face, ModelScope, AI Studio)"),
        ("RapidOCR pequeno", mb(tudo_rapid - medio if tudo_rapid else None), mb(pequeno),
         "os modelos pequenos já vêm dentro do pacote; o OpenCV é perto de 110 MB"),
        ("RapidOCR médio", mb(tudo_rapid), mb(medio),
         "o modelo médio é o mesmo do PaddleOCR oficial, em outro formato"),
    ]
    corpo = "".join(f"<tr><th scope='row'>{e(a)}</th><td>{b}</td><td>{c}</td><td class='nota'>{e(d)}</td></tr>"
                    for a, b, c, d in linhas)
    return ("<div class='rolar'><table><tr><th>Motor</th><th>Ocupado no ambiente de teste</th>"
            "<th>Só os modelos</th><th>De onde vem o peso</th></tr>" + corpo + "</table></div>")


def montar_veredito(gabarito, na_massa, na_real):
    """O que a medição concluiu, com cada número saindo da conta.

    As frases foram escritas depois de olhar os resultados; os números, não.
    Escritos à mão, eles envelheciam calados na primeira vez em que a medição
    fosse refeita - e a primeira versão chegou a dizer que o RapidOCR pequeno
    rodava "os mesmos modelos" do oficial, quando ele usa a versão pequena da
    mesma família (lente crítica, 16/10/2026). Faltando ou estando desatualizada
    alguma leitura, não há veredito: número de uma conta pela metade não serve.
    """
    chaves = [chave for chave, _nome, _detalhe in MOTORES]
    massa = dict(zip(chaves, na_massa))
    real = dict(zip(chaves, na_real)) if na_real else {}
    if any(fora(m) for m in list(massa.values()) + list(real.values())):
        return None
    t, o, p = massa["tesseract"], massa["paddleocr"], massa["rapidocr"]

    nomes = [pagina["pagina"] for pagina in gabarito]
    deitada = nomes.index("oficio-deitado")
    em_tabela = sum(Counter(s for _g, _l, s in t["por_pagina"][i]["destinos"])["escaparia"]
                    for i, nome in enumerate(nomes) if nome.startswith("tabela"))

    def palavras_na_deitada(medida):
        return porcento(medida["por_pagina"][deitada]["palavras"])

    escaparam_na_deitada = Counter(
        s for _g, _l, s in p["por_pagina"][deitada]["destinos"])["escaparia"]

    no_real = ""
    if real:
        no_real = (f" No documento real, o Tesseract deixaria escapar {real['tesseract']['escaparia']}"
                   f" dos {real['tesseract']['cpfs']}; o oficial, {real['paddleocr']['escaparia']};"
                   f" o RapidOCR pequeno, {real['rapidocr']['escaparia']}.")
    return f"""<strong>Os modelos do PaddleOCR ganham onde o pedido dizia, e ganham nos CPFs.</strong>
Nas páginas difíceis inventadas, o Tesseract deixaria {t['escaparia']} dos {t['cpfs']} CPFs saírem sem
máscara — {em_tabela} deles em tabela com grade, que ele pula mesmo quando a página está limpa. O
PaddleOCR oficial deixaria {o['escaparia']}, e o RapidOCR pequeno, {p['escaparia']}.{no_real}
<br><br><strong>Mas não do jeito oficial.</strong> O PaddleOCR oficial, instalado do jeito normal, não
leu nenhuma página nesta máquina (um defeito do PaddlePaddle no Windows). Com a aceleração desligada
ele lê, mas levou {segundos(o['segundos'])} por página. O RapidOCR pequeno usa a <em>versão pequena</em>
da mesma família de modelos (PP-OCRv6 — o oficial usou a média) e acertou {p['certo']} de {p['cpfs']}
CPFs, contra {o['certo']} do oficial, a {segundos(p['segundos'])} por página, com os modelos dentro do
próprio pacote.
<br><br><strong>O ponto fraco do RapidOCR:</strong> ele não endireita a página deitada. Nela, leu
{palavras_na_deitada(p)}% das palavras e deixou {escaparam_na_deitada} CPF(s) escapar; o Tesseract leu
{palavras_na_deitada(t)}% e o oficial {palavras_na_deitada(o)}%, porque endireitam."""


def gabarito_do_real():
    documento = pymupdf.open(REAL)
    try:
        return [pagina.get_text() for pagina in documento]
    finally:
        documento.close()


def main():
    gabarito = json.loads(GABARITO_DA_MASSA.read_text(encoding="utf-8"))
    textos_da_massa = [p["texto"] for p in gabarito]
    na_massa = [medir(textos_da_massa, ler_json(LEITURAS_DA_MASSA, m), MASSA.name)
                for m, _n, _d in MOTORES]

    na_real = None
    if REAL.exists():
        textos_do_real = gabarito_do_real()
        na_real = [medir(textos_do_real, ler_json(LEITURAS_DO_REAL, m), REAL.name)
                   for m, _n, _d in MOTORES]
        bloco_real = f"""
<h2>O documento real desta máquina — só contagens</h2>
<p class="nota">O formulário do SIGPEX do teste da 0.1.0, {len(textos_do_real)} páginas. Ele tem o texto
gravado por dentro, e é esse texto que serve de gabarito: os motores leram as <em>imagens</em> das
páginas, como leriam um escaneado, e a leitura foi comparada com o texto de dentro. Nenhum trecho,
nenhum CPF e nenhum nome dele aparece nesta página.</p>
{tabela_resumo(na_real, "SIGPEX")}"""
    else:
        bloco_real = ("<h2>O documento real</h2><p class='nota'>Não está nesta máquina: a página "
                      "foi gerada só com a massa inventada.</p>")

    texto_do_veredito = montar_veredito(gabarito, na_massa, na_real)
    veredito = (f"<div class='caixa'>{texto_do_veredito}</div>" if texto_do_veredito else
                "<div class='caixa'>Sem veredito: falta a leitura de algum motor, ou alguma está "
                "desatualizada. Refaça as leituras e gere a página de novo.</div>")

    pagina = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Conferência 02 — os motores de leitura lado a lado</title>
<style>
  :root {{
    --cor-fundo: #1e2228; --cor-fundo-elevado: #262b33; --cor-borda: #383e47;
    --cor-texto: #e8eaed; --cor-texto-secundario: #9aa1ac; --cor-destaque: #3b6ea5;
    --cor-sucesso: #4caf6d; --cor-alerta: #d9a441; --cor-erro-texto: #f08a86;
    --fonte-texto: "Segoe UI", system-ui, sans-serif;
    --fonte-mono: "Cascadia Mono", "Consolas", monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--cor-fundo); color: var(--cor-texto);
         font-family: var(--fonte-texto); font-size: 15px; line-height: 1.55;
         padding: 32px max(16px, calc((100vw - 1100px) / 2)); }}
  h1 {{ font-size: 28px; margin: 0 0 8px; }}
  h2 {{ font-size: 20px; margin: 40px 0 8px; }}
  code {{ font-family: var(--fonte-mono); font-size: 13px; }}
  .subtitulo, .nota {{ color: var(--cor-texto-secundario); }}
  .nota {{ font-size: 13px; font-weight: 400; }}
  .caixa {{ background: var(--cor-fundo-elevado); border: 1px solid var(--cor-borda);
            border-left: 4px solid var(--cor-destaque); border-radius: 6px;
            padding: 16px 24px; margin: 16px 0; }}
  .rolar {{ overflow-x: auto; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
  th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--cor-borda); vertical-align: top; }}
  th {{ color: var(--cor-texto-secundario); font-weight: 600; font-size: 13px; }}
  th[scope=row] {{ color: var(--cor-texto); }}
  .mono {{ font-family: var(--fonte-mono); white-space: nowrap; }}
  .forte {{ font-weight: 600; }}
  .bom {{ color: var(--cor-sucesso); }}
  .ruim {{ color: var(--cor-erro-texto); font-weight: 600; }}
  .aviso {{ color: var(--cor-alerta); }}
  .apagado {{ color: var(--cor-texto-secundario); font-style: italic; }}
  ul li {{ margin-bottom: 6px; }}
  .rodape {{ margin-top: 40px; border-top: 1px solid var(--cor-borda); padding-top: 16px;
             font-size: 13px; color: var(--cor-texto-secundario); }}
</style>
</head>
<body>

<h1>Conferência 02 — os motores de leitura lado a lado</h1>
<p class="subtitulo">Funcionalidade 7 (ler com o PaddleOCR). Antes de construir, os motores leram as
mesmas páginas, e cada leitura foi comparada com o que de fato está escrito nelas. O PaddleOCR
aparece de dois jeitos: o oficial e o RapidOCR, que roda os mesmos modelos com um motor mais leve.</p>

{veredito}

<h2>Como ler esta página</h2>
<ul>
  <li><strong>CPFs certos</strong> — o motor leu o número inteiro, igualzinho ao papel.</li>
  <li><strong>Com dígito trocado</strong> — leu com um a três dígitos errados. O programa ainda o
  mascara, como suspeito, mas a pessoa precisa corrigir na conferência.</li>
  <li><strong>Escapariam</strong> — o número não foi reconhecido como CPF na leitura, e sairia do
  programa <em>sem máscara</em>. É o número que mais importa nesta página.</li>
  <li><strong>Palavras lidas certas</strong> — de cada cem palavras escritas na página, quantas o
  motor leu igualzinho. Mede o trabalho que a conferência humana vai ter.</li>
</ul>

<h2>As páginas difíceis, inventadas</h2>
<p class="nota">{len(gabarito)} páginas feitas como imagem, como sai de um escâner, com um defeito
por página — os que motivaram o pedido: tabela com grade, poeira, página torta, desbotada com
chuvisco, gravada em baixa qualidade, e deitada. As duas primeiras são limpas, e servem de referência
(<code>dados-exemplo/20-paginas-dificeis.pdf</code>). Os nomes e os números são inventados.</p>
{tabela_resumo(na_massa, "Páginas inventadas")}

<h3>Página a página</h3>
{tabela_pagina_a_pagina(gabarito, na_massa)}

<h3>O que cada um errou nos CPFs</h3>
<p class="nota">Só os CPFs que algum motor não leu certo. Em amarelo, o que o motor leu no lugar.</p>
{tabela_dos_erros(gabarito, na_massa)}
{bloco_real}

<h2>O peso de cada um</h2>
<p class="nota">Medido nos ambientes de teste desta máquina. O programa entregue leva só a parte que
ele usa de fato, e quanto é isso só se sabe montando a pasta do programa com o motor dentro — é o
primeiro teste da construção. Para comparar: o instalador inteiro da 0.1.0, com o do Tesseract dentro,
tem 97 MB.</p>
{tabela_do_peso()}

<h2>O que esta medição não mede</h2>
<ul>
  <li>Se o motor roda de dentro da pasta montada para a entrega, e não só no ambiente de teste.</li>
  <li>Documento escaneado de verdade: o SIGPEX é um documento com texto por dentro, lido como imagem,
  e as páginas difíceis são inventadas. Um escaneado real do núcleo é o teste que falta.</li>
  <li>Outra máquina: os tempos são desta, e as do núcleo podem ser mais lentas.</li>
  <li>A prova completa de que o motor lê sem internet. Aqui foram vigiadas as conexões feitas pela
  parte do motor escrita em Python; a parte compilada passaria por fora. A prova com a máquina sem
  rede nenhuma é teste da construção.</li>
</ul>

<p class="rodape">Página gerada em {DATA} pela skill-07-designer-de-telas, a pedido da
skill-02-analista-de-requisitos, a partir das leituras gravadas
(<code>conferencias/ler-com-o-motor.py</code> e <code>conferencias/gerar-02-os-motores-de-leitura.py</code>).
Todos os nomes e números das páginas inventadas são inventados; os que passam na conta são só de
dígitos repetidos (RN-22 da spec 003). Do documento real, só contagens.</p>
</body>
</html>
"""
    destino = RAIZ / "conferencias" / "02-os-motores-de-leitura.html"
    destino.write_text(pagina, encoding="utf-8")
    print(f"gerado: {destino.name}")


if __name__ == "__main__":
    main()

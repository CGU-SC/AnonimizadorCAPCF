"""Monta a documentação de manutenção num arquivo só, a partir das partes.

A documentação é escrita em pedaços, em `documentacao/fonte/`: um HTML por
aba, a folha de estilo e as prints como arquivo comum. Este script junta tudo
em `documentacao/manutencao.html`, com as imagens dentro dele, e confere antes
de gravar:

- todo link para outra aba ou para um trecho (`#...`) leva a algo que existe;
- todo arquivo do projeto citado, num link ou entre `<code>`, existe;
- toda imagem citada existe, e nenhuma da pasta sobra sem uso;
- nenhum termo vetado aparece, se for dada a lista com `--termos`.

Achando erro, ele diz qual e não grava: a documentação velha fica como estava.

    .\\.venv\\Scripts\\python.exe documentacao\\montar.py
    .\\.venv\\Scripts\\python.exe documentacao\\montar.py --termos lista.txt

O `manutencao.html` nunca se edita direto: a próxima montagem escreve por cima.

Por que em partes, e não um HTML só escrito à mão: dentro do HTML cada print
vira um bloco enorme de texto, e mudar uma frase ao lado dela obrigava a ler e
reescrever esse bloco. Separadas, cada parte tem o tamanho de uma aba.
"""
import argparse
import base64
import html
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "documentacao"
FONTE = PASTA / "fonte"
IMAGENS = FONTE / "imagens"
SAIDA = PASTA / "manutencao.html"

# As abas, na ordem do menu e da leitura: o identificador (que é também o nome
# do arquivo em fonte/ e o endereço #...), o nome na aba e o ícone dela.
ABAS = [
    ("inicio", "Início", "⌂"),
    ("ambiente", "Ambiente", "⚙"),
    ("funcionalidades", "Funcionalidades", "▤"),
    ("regras", "Regras", "≡"),
    ("arquitetura", "Arquitetura", "⬡"),
    ("testes", "Testes", "✓"),
    ("mudancas", "Mudanças", "✎"),
    ("armadilhas", "Armadilhas", "⚠"),
    ("entrega", "Entrega", "⇪"),
    ("versoes", "Versões", "◷"),
    ("historico", "Histórico", "↺"),
]

# O que a pasta do código entregue tem. Um caminho citado fora daqui é de algo
# que quem recebe a pasta não vai ter - e por isso a conferência o recusa,
# salvo as pastas que o próprio trabalho cria, que podem ser citadas sem existir.
ENTREGUE = ["programa", "empacotar", "abrir", "dados-exemplo", "conferencias",
            "especificacoes", "mockups", "documentacao", "README.md",
            "requirements.txt", ".gitignore", ".gitattributes", ".env.example"]
CRIADAS_PELO_TRABALHO = [".venv", "builds", "instaladores", ".env", "preferencias.ini"]

SIMBOLO = ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" '
           'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
           '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/>'
           '<path d="M14 3v5h5"/><path d="M9 13h6M9 17h6"/></svg>')

# Uma aba por vez, num arquivo só. O endereço guarda a aba (#regras): o
# "voltar" do navegador e um link mandado a alguém caem nela. Um link para um
# trecho dentro de uma aba (#onde-fica-o-env) abre a aba dele e rola até lá.
# Sem script, a classe "sem-script" fica no corpo e as abas viram uma página só.
SCRIPT = """
document.body.classList.remove('sem-script');
const paineis = [...document.querySelectorAll('.painel')];
const abas = [...document.querySelectorAll('.aba')];
function mostrar() {
  const pedido = decodeURIComponent(location.hash.slice(1));
  const alvo = pedido ? document.getElementById(pedido) : null;
  const painel = (alvo && alvo.closest('.painel')) || paineis[0];
  paineis.forEach(p => p.classList.toggle('visivel', p === painel));
  abas.forEach(a => a.classList.toggle('atual', a.getAttribute('href') === '#' + painel.id));
  if (alvo && alvo !== painel) {
    const altura = document.querySelector('.alto').offsetHeight;
    window.scrollTo(0, alvo.getBoundingClientRect().top + window.scrollY - altura - 16);
  } else {
    window.scrollTo(0, 0);
  }
}
addEventListener('hashchange', mostrar);
mostrar();
"""


def versao():
    texto = (RAIZ / "programa" / "versao.py").read_text(encoding="utf-8")
    return re.search(r'^VERSAO = "([^"]+)"', texto, re.M).group(1)


def ler_partes(avisos):
    """O HTML de cada aba; a que ainda não foi escrita sai marcada, com aviso."""
    partes = {}
    for ident, rotulo, _ in ABAS:
        arquivo = FONTE / f"{ident}.html"
        if arquivo.exists():
            partes[ident] = arquivo.read_text(encoding="utf-8")
        else:
            avisos.append(f"aba ainda não escrita: {arquivo.relative_to(RAIZ)}")
            partes[ident] = (f'<div class="secao"><h2>{rotulo}</h2>'
                             '<div class="em-construcao">Em construção.</div></div>')
    return partes


def embutir_imagens(texto, erros, usadas):
    """Troca `imagens/x.png` pelo próprio arquivo, dentro do HTML."""
    def trocar(achado):
        nome = achado.group(1)
        arquivo = IMAGENS / nome
        if not arquivo.exists():
            erros.append(f"imagem que não existe: fonte/imagens/{nome}")
            return achado.group(0)
        usadas.add(nome)
        dados = base64.b64encode(arquivo.read_bytes()).decode("ascii")
        return f'src="data:image/png;base64,{dados}"'
    texto = re.sub(r'src="imagens/([^"]+\.png)"', trocar, texto)
    # O que sobrou apontando para imagens/ não foi embutido: outro formato, aspas
    # simples, ou um url() na folha de estilo. Passaria calado, e o arquivo
    # entregue abriria com a imagem quebrada, porque a pasta não vai ao lado dele.
    for sobra in re.findall(r"""(?:src|href)\s*=\s*["']?[^"'\s>]*imagens/[^"'\s>]*"""
                            r"""|url\(\s*["']?[^)]*imagens/[^)]*\)""", texto):
        erros.append(f"imagem que não foi embutida (só PNG, com src=\"imagens/...\"): {sobra}")
    return texto


def montar(partes, numero):
    abas = "\n".join(
        f'    <a class="aba" href="#{ident}"><span class="icone">{icone}</span> {rotulo}</a>'
        for ident, rotulo, icone in ABAS)
    paineis = "\n".join(
        f'<section class="painel" id="{ident}">\n{partes[ident].strip()}\n</section>'
        for ident, _, _ in ABAS)
    estilo = (FONTE / "estilo.css").read_text(encoding="utf-8")
    corpo = paineis.replace("{{VERSAO}}", numero)
    return f"""<!DOCTYPE html>
<!-- Montado pelo documentacao/montar.py a partir de documentacao/fonte/.
     Não edite este arquivo: a próxima montagem escreve por cima. -->
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Anonimizador CAPCF — documentação de manutenção</title>
<style>
{estilo}
</style>
</head>
<body class="sem-script">
<div class="alto">
  <div class="topo">
    <div class="topo-dentro">
      <a class="identidade" href="#inicio">
        <div class="simbolo">{SIMBOLO}</div>
        <div><div class="nome">Anonimizador</div><div class="casa">CAPCF · UFSC</div></div>
      </a>
      <div class="etiqueta-versao">Versão {numero}{' · teste' if numero.startswith('0.') else ''}</div>
    </div>
  </div>
  <nav class="abas">
{abas}
  </nav>
</div>
<div class="pagina-corpo">
{corpo}
</div>
<footer><div class="rodape-dentro">
  <span>Anonimizador CAPCF · documentação de manutenção da versão {numero}</span>
  <span>O programa foi desenvolvido pela CGU no âmbito da consultoria realizada à UFSC em 2026.</span>
</div></footer>
<script>{SCRIPT}</script>
</body>
</html>
"""


def conferir_ancoras(documento, erros):
    todos = re.findall(r'\bid="([^"]+)"', documento)
    ids = set(todos)
    # As abas vivem num documento só, e o navegador leva sempre ao primeiro de
    # dois identificadores iguais: uma seção com o nome de uma aba abriria a aba
    # errada, sem ninguém notar.
    for repetido in sorted({i for i in todos if todos.count(i) > 1}):
        erros.append(f"identificador repetido: #{repetido}")
    for alvo in sorted(set(re.findall(r'href="#([^"]*)"', documento))):
        if alvo not in ids:
            erros.append(f"link para #{alvo}, que não existe")


def nomes_entregues():
    """O nome de cada arquivo da pasta entregue, sem a pasta dele."""
    nomes = set()
    for item in ENTREGUE:
        caminho = RAIZ / item
        if caminho.is_file():
            nomes.add(caminho.name)
        elif caminho.is_dir():
            nomes.update(p.name for p in caminho.rglob("*")
                         if p.is_file() and "__pycache__" not in p.parts)
    return nomes


def conferir_caminhos(partes, erros):
    """Todo arquivo do projeto citado existe, e é da pasta que vai junto."""
    citados, soltos = set(), set()
    for texto in partes.values():
        for href in re.findall(r'href="\.\./([^"#]+)', texto):
            citados.add(href)
        for trecho in re.findall(r"<code>([^<]+)</code>", texto):
            caminho = html.unescape(trecho).strip().replace("\\", "/").rstrip(".,;:")
            # Só com letra: um CPF com barra (123.456.789/10) tem cara de caminho.
            parece_caminho = (re.fullmatch(r"[\w.\-]+(/[\w.\-]*)+", caminho)
                              and re.search(r"[a-zA-Z]", caminho))
            if parece_caminho or caminho in ENTREGUE:
                citados.add(caminho)
            elif re.fullmatch(r"[\w.\-]+\.(py|bat|md|html|css|spec|iss|json|txt|pdf|docx)", caminho):
                soltos.add(caminho)
    # Um nome sem pasta (`painel_ocr.py`) precisa existir em algum lugar da pasta
    # entregue. Sem isso, o arquivo renomeado numa versão futura continuaria
    # citado na documentação, e a montagem passaria limpa.
    # Os da família dos que cada máquina cria (o `.env.txt` do Bloco de Notas)
    # podem ser citados sem existir, como as pastas criadas pelo trabalho.
    existentes = nomes_entregues()
    soltos = {n for n in soltos if not n.startswith(tuple(CRIADAS_PELO_TRABALHO))}
    for nome in sorted(soltos - existentes):
        erros.append(f"arquivo citado que não existe na pasta entregue: {nome}")
    for caminho in sorted(citados):
        primeiro = caminho.split("/")[0]
        if primeiro in CRIADAS_PELO_TRABALHO:
            continue
        if primeiro not in ENTREGUE:
            erros.append(f"caminho de fora da pasta entregue: {caminho}")
        elif not (RAIZ / caminho).exists():
            erros.append(f"caminho que não existe: {caminho}")


def conferir_termos(texto, arquivo_de_termos, erros):
    """Os termos vetados: um por linha, sem diferença de maiúscula."""
    termos = [linha.strip() for linha in arquivo_de_termos.read_text(encoding="utf-8").splitlines()
              if linha.strip() and not linha.startswith("#")]
    minusculo = texto.lower()
    for termo in termos:
        if termo.lower() in minusculo:
            erros.append(f"termo vetado encontrado: {termo}")


def main():
    pedido = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    pedido.add_argument("--termos", type=Path, help="arquivo com os termos vetados, um por linha")
    argumentos = pedido.parse_args()

    erros, avisos, usadas = [], [], set()
    partes = ler_partes(avisos)
    numero = versao()
    documento = montar(partes, numero)
    conferir_ancoras(documento, erros)
    conferir_caminhos(partes, erros)
    if argumentos.termos:
        fontes = "\n".join([documento, (PASTA / "capturar_telas.py").read_text(encoding="utf-8"),
                            Path(__file__).read_text(encoding="utf-8")])
        conferir_termos(fontes, argumentos.termos, erros)
    documento = embutir_imagens(documento, erros, usadas)
    for sobra in sorted(p.name for p in IMAGENS.glob("*.png") if p.name not in usadas):
        avisos.append(f"imagem sem uso: fonte/imagens/{sobra}")

    for aviso in avisos:
        print(f"  aviso: {aviso}")
    if erros:
        for erro in erros:
            print(f"  ERRO: {erro}")
        print("Nada foi gravado.")
        sys.exit(1)
    # Quebra de linha do Linux, sempre: o arquivo é gerado, e assim ele sai
    # igual em qualquer máquina, sem o git acusar mudança onde não houve.
    SAIDA.write_text(documento, encoding="utf-8", newline="\n")
    print(f"Gravado: {SAIDA.relative_to(RAIZ)} ({SAIDA.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

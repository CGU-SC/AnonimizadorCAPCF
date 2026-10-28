r"""Gera a página da Conferência 05: o que a funcionalidade 8 já faz, o que os
testes automáticos conferem sozinhos, e o que fica para a conferência na tela.

A solicitante pediu, em 28/10/2026, que o máximo fosse conferido por teste
automático, porque ia viajar: na tela, só o que um teste não consegue ver. Esta
página separa as duas coisas, e conta quantos testes passam, rodando-os.

Rode assim, da raiz do projeto:

    .\.venv\Scripts\python.exe conferencias\gerar-05-lembrar-as-escolhas.py
"""
import html
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATA = "28/10/2026"

# As cinco etapas da construção. A situação é mudada à mão a cada etapa fechada.
ETAPAS = [
    ("1", "O Gerar OCR lembra o motor, num preferencias.ini gravado com segurança", "no programa"),
    ("2", "O Anonimizar lembra o dele, à parte, e o motor que some passa a ser lembrado como o outro", "no programa"),
    ("3", "A janela: maximizada no primeiro uso, depois o tamanho e o maximizado lembrados", "no programa"),
    ("4", "Os caminhos tortos: arquivo estragado, pasta sem gravação, o .env intacto, nada do trabalho", "no programa"),
    ("5", "O instalador (desinstalar apaga, atualizar mantém) e o roteiro da conferência", "no programa"),
]

# O que os testes automáticos conferem, em português, com o arquivo de teste.
CONFERIDO = [
    ("Marcou o Tesseract no Gerar OCR, fechou e abriu: ele vem marcado (RN-36)", "test_preferencias.py"),
    ("Quem nunca escolheu abre com o PaddleOCR, e só abrir não grava nada (RN-36)", "test_preferencias.py"),
    ("Voltar ao padrão é marcar o PaddleOCR (fora de escopo: não há botão)", "test_preferencias.py"),
    ("Marcar no Gerar OCR não muda o Anonimizar (RN-36)", "test_preferencias.py"),
    ("Um motor lembrado que não existe vale como nada lembrado", "test_preferencias.py"),
    ("Arquivo estragado, com lixo ou outra codificação: abre no padrão, sem erro, e é refeito (RN-39)", "test_preferencias.py"),
    ("Pasta que não aceita gravar: segue calado, sem travar (RN-39)", "test_preferencias.py"),
    ("Gravação cortada no meio deixa a escolha anterior inteira (RN-39)", "test_preferencias.py"),
    ("Marcou o Tesseract no Anonimizar, sem ler nada, fechou e abriu: ele vem marcado, e o Gerar OCR fica como estava (RN-36)", "test_preferencias.py"),
    ("Marcar no Anonimizar não muda o Gerar OCR, e só abrir os dois não grava nada (RN-36)", "test_preferencias.py"),
    ("O Gerar OCR não lembra pela tela de ler que ele monta e não mostra", "test_preferencias.py"),
    ("Tesseract lembrado que sumiu: abre com o PaddleOCR, a linha do Tesseract apagada, e o arquivo passa a dizer paddleocr — nos dois módulos (RN-37)", "test_preferencias.py"),
    ("O Tesseract que volta não é remarcado sozinho, com o programa aberto ou na próxima vez — nos dois módulos (RN-37)", "test_preferencias.py"),
    ("PaddleOCR lembrado que sumiu: a marca e a lembrança passam ao Tesseract (RN-37)", "test_preferencias.py"),
    ("Faltando os dois motores, nada muda no que está lembrado (RN-37)", "test_preferencias.py"),
    ("Pasta sem gravação: o Tesseract marcado lê até fechar, nos dois módulos (critério de aceite)", "test_preferencias.py"),
    ("Sem nada lembrado, a janela abre maximizada, e sai do maximizado para 1000 x 640 no meio da tela (RN-4, RN-8)", "test_janela_lembrada.py"),
    ("Fechou com 1200 x 800, abre com 1200 x 800, no meio da tela — com a janela de verdade (RN-5, RN-6)", "test_janela_lembrada.py"),
    ("Fechou maximizada, abre maximizada; saindo do maximizado, volta ao tamanho de antes — com a janela de verdade (RN-5)", "test_janela_lembrada.py"),
    ("Maximizada, minimizada pela barra de tarefas e fechada de lá: continua lembrada como maximizada (minimizada pelo próprio Windows)", "test_janela_lembrada.py"),
    ("Tamanho maior que a tela encolhe e cabe, com a barra de título; menor que 900 x 560 vira 900 x 560 (RN-7)", "test_janela_lembrada.py"),
    ("Em cinco telas (Full HD, barra de tarefas em cima, segundo monitor à direita e à esquerda, notebook) e quatro tamanhos: no meio, e nunca fora (RN-6, RN-7)", "test_janela_lembrada.py"),
    ("Numa tela menor que o mínimo, a barra de título fica à vista", "test_janela_lembrada.py"),
    ("Tamanho que não dá para ler, ou absurdo escrito à mão: primeiro uso, ou encolhe — nunca derruba o programa (RN-4, RN-39)", "test_janela_lembrada.py"),
    ("Abrir não grava; fechar que para na pergunta de descartar não grava; a janela grava no bloco dela, numa gravação só, sem mexer nos motores", "test_janela_lembrada.py"),
    ("O .env da TI, com acentos, aspas e a quebra de linha do Windows, fica idêntico byte a byte depois de marcar e fechar duas vezes", "test_preferencias_caminhos_tortos.py"),
    ("O preferencias.ini mora ao lado do .env, na pasta da instalação, e nada mais aparece nela (RN-38)", "test_preferencias_caminhos_tortos.py"),
    ("Um uso inteiro — PDF conferido, seguido para o Anonimizar e salvo — e o arquivo tem só os motores e a janela: nenhum nome, pasta, texto, CPF ou data (RN-40)", "test_preferencias_caminhos_tortos.py"),
    ("Arquivo estragado ou apagado: os dois módulos no PaddleOCR e a janela maximizada, como no primeiro uso (RN-39)", "test_preferencias_caminhos_tortos.py"),
    ("Pasta protegida: marcar e fechar seguem sem erro nem aviso, e o .env fica intacto (RN-39)", "test_preferencias_caminhos_tortos.py"),
    ("O .gitignore cobre o arquivo e o provisório", "test_preferencias_caminhos_tortos.py"),
    ("O instalador apaga o arquivo e o provisório ao desinstalar, e não o traz nem o apaga ao atualizar, nem quando ele foi esquecido na pasta montada (RN-41) — o teste lê a receita; compilá-la é à mão, e ela compilou sem erro em 28/10/2026", "test_preferencias_caminhos_tortos.py"),
    ("Arquivo salvo no Bloco de Notas em UTF-8, UTF-8 com BOM, Unicode ou ANSI é entendido (revisão 46)", "test_preferencias.py"),
    ("Antivírus segurando o arquivo por um instante: a gravação insiste e a escolha não se perde (revisão 46)", "test_preferencias.py"),
    ("Um bloco [DEFAULT] escrito à mão não vaza para os outros (revisão 46)", "test_preferencias.py"),
    ("Minimizada pelo Windows a partir do tamanho normal e fechada: lembra o tamanho, e não o do ícone (revisão 46)", "test_janela_lembrada.py"),
    ("Arquivo preso por outro programa não é reescrito, e as outras escolhas ficam (revisão 43)", "test_preferencias.py"),
    ("Arquivo salvo com BOM no Bloco de Notas, ou com \"Tesseract\" em maiúscula, é entendido (revisão 43)", "test_preferencias.py"),
    ("Duas janelas do programa não dividem o arquivo provisório (revisão 43)", "test_preferencias.py"),
    ("Nenhum teste toca o preferencias.ini desta máquina (premissa dos testes isolados)", "test_preferencias.py"),
]


# Os testes da funcionalidade, rodados para contar quantos passam.
ARQUIVOS_DE_TESTE = ["programa/test_preferencias.py", "programa/test_janela_lembrada.py",
                     "programa/test_preferencias_caminhos_tortos.py"]


# O que só a tela e a instalação de verdade mostram. Cada passo: o que fazer, o
# que deve acontecer.
ROTEIRO_NO_DESENVOLVIMENTO = [
    ("Apague o <code>preferencias.ini</code> da raiz do projeto, se houver, e abra o programa pelo "
     "<code>abrir\\abrir-dev.bat</code>.",
     "A janela abre maximizada, ocupando a tela, com a barra de tarefas do Windows à vista."),
    ("Saia do maximizado (o botão do meio, no canto de cima à direita).",
     "A janela fica com 1000 × 640, no meio da tela."),
    ("Arraste a borda até um tamanho bem diferente, leve a janela para um canto, feche e abra de novo.",
     "Ela volta com o mesmo tamanho, mas no meio da tela — e não no canto."),
    ("Maximize, feche e abra de novo. Depois, saia do maximizado.",
     "Abre maximizada; saindo, volta ao tamanho do passo anterior."),
    ("No Gerar OCR, marque o Tesseract. Feche e abra de novo. Depois, no Anonimizar, escolha o "
     "<code>dados-exemplo\\02-imprimir-para-pdf.pdf</code> e vá até a tela de ler.",
     "O Gerar OCR vem com o Tesseract marcado; o Anonimizar, com o PaddleOCR. Nada na tela diz que a escolha "
     "veio lembrada."),
    ("Ainda no Anonimizar, marque o Tesseract, sem ler. Feche e abra de novo, e volte à tela de ler.",
     "O Anonimizar vem com o Tesseract marcado."),
    ("Abra o <code>preferencias.ini</code> da raiz do projeto no Bloco de Notas.",
     "Um cabeçalho explicando o arquivo, e três blocos: <code>[gerar_ocr]</code> e <code>[anonimizar]</code> "
     "com o motor, e <code>[janela]</code> com largura, altura e maximizada. Nada de nome de documento ou "
     "pasta."),
    ("Feche e abra pelo <code>abrir\\abrir-sem-motor.bat</code>, que esconde o Tesseract. Depois feche e "
     "abra pelo <code>abrir-dev.bat</code> de novo.",
     "Pelo atalho sem motor, os dois módulos vêm com o PaddleOCR e a linha do Tesseract apagada, dizendo por "
     "quê. De volta ao normal, o Tesseract aparece aceso, mas o PaddleOCR continua marcado (RN-37)."),
]

ROTEIRO_INSTALADO = [
    ("Quando você voltar, eu monto um instalador de teste com outro nome, sem escrever por cima do da "
     "entrega 0.1.0. Instale-o, abra, marque o Tesseract no Gerar OCR, mude o tamanho da janela e feche.",
     "Abre maximizada no primeiro uso, como no desenvolvimento."),
    ("Instale o mesmo instalador de novo, por cima, e abra.",
     "O tamanho e o Tesseract continuam: atualizar mantém a escolha."),
    ("Desinstale pelo Windows (Configurações › Aplicativos) e olhe a pasta "
     "<code>%LOCALAPPDATA%\\Programs\\Anonimizador CAPCF</code>.",
     "Não sobra o <code>preferencias.ini</code>."),
    ("Instale de novo e abra.",
     "Abre maximizada e com o PaddleOCR nos dois módulos: começou do padrão."),
    ("Se você usar dois monitores: feche o programa no monitor que não é o principal e abra de novo.",
     "Ele abre no monitor principal, no meio — veja a primeira anotação abaixo."),
]

# O que as revisões 43 a 47 acharam e não era defeito claro: fica para a
# solicitante decidir.
ANOTADO = [
    ("Com dois monitores, a janela abre sempre no principal",
     "e o tamanho lembrado é cortado para caber nele. Quem trabalha num monitor grande ligado a um notebook vê "
     "o tamanho encolher toda vez. É consequência de não lembrar a posição (RN-6); lembrar o monitor seria uma "
     "emenda. (Revisão 45.)"),
    ("A troca de motor feita pelo programa também fica lembrada",
     "como a RN-37 manda. Mas \"faltar\" inclui um sumiço passageiro — o Tesseract numa pasta de rede ainda não "
     "ligada, ou sem o pacote de português —, e os atalhos de <code>abrir\\</code> que fingem um motor faltando: "
     "um dia assim, e a escolha da pessoa passa ao outro motor de vez. Se preferir que a lembrança espere o motor "
     "voltar, é uma emenda pequena na RN-37. (Revisões 43, 44 e 46.)"),
    ("Desinstalar com o programa aberto deixa a lembrança voltar",
     "o desinstalador apaga o <code>preferencias.ini</code>, e, quando a pessoa fecha a janela depois, o "
     "programa grava o tamanho de novo, na pasta que sobrou. A instalação seguinte abre com esse tamanho, e não "
     "maximizada. Fechar o programa antes de desinstalar evita; fazer o instalador recusar enquanto o programa "
     "estiver aberto é uma mudança pequena, mas muda o que a pessoa vê ao instalar e desinstalar. (Revisão 47.)"),
    ("Para a lente de manutenção",
     "a lembrança do motor está ligada à peça da tela que mostra os motores, e o caminho do PDF monta a tela de "
     "ler também no Gerar OCR, que não a mostra. Um terceiro motor (a IA local) ou um outro lugar que escolha "
     "motor precisariam repetir a ligação. (Revisões 43 e 44.)"),
]


def e(texto):
    return html.escape(texto)


def testes_que_passam():
    """Roda os testes da funcionalidade e devolve quantos passaram."""
    saida = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *ARQUIVOS_DE_TESTE],
        cwd=RAIZ, capture_output=True, text=True).stdout
    achado = re.search(r"(\d+) passed", saida)
    falhas = re.search(r"(\d+) failed", saida)
    return int(achado.group(1)) if achado else 0, int(falhas.group(1)) if falhas else 0


def main():
    passaram, falharam = testes_que_passam()
    linhas_etapas = "".join(
        f"<tr><td>{n}</td><td>{e(o_que)}</td>"
        f"<td class='{'feito' if situacao == 'no programa' else 'falta'}'>{e(situacao)}</td></tr>"
        for n, o_que, situacao in ETAPAS)
    linhas_conferido = "".join(
        f"<tr><td>{e(o_que)}</td><td class='mono'>{e(onde)}</td></tr>" for o_que, onde in CONFERIDO)

    def roteiro(passos, comeco=1):
        # Os passos são escritos aqui mesmo, com marcação: vão sem escapar.
        return "".join(
            f"<tr><td>{n}</td><td>{fazer}</td><td>{esperar}</td></tr>"
            for n, (fazer, esperar) in enumerate(passos, start=comeco))
    linhas_dev = roteiro(ROTEIRO_NO_DESENVOLVIMENTO)
    linhas_instalado = roteiro(ROTEIRO_INSTALADO, len(ROTEIRO_NO_DESENVOLVIMENTO) + 1)
    itens_anotados = "".join(f"<li><strong>{titulo}</strong>: {texto}</li>" for titulo, texto in ANOTADO)

    pagina = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Conferência 05 — lembrar as escolhas</title>
<style>
  :root {{
    --cor-fundo: #1e2228; --cor-fundo-elevado: #262b33; --cor-borda: #383e47;
    --cor-texto: #e8eaed; --cor-texto-secundario: #9aa1ac; --cor-destaque: #3b6ea5;
    --cor-sucesso: #4caf6d; --cor-erro-texto: #f08a86;
    --fonte-texto: "Segoe UI", system-ui, sans-serif;
    --fonte-mono: "Cascadia Mono", "Consolas", monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--cor-fundo); color: var(--cor-texto);
         font-family: var(--fonte-texto); font-size: 15px; line-height: 1.55;
         padding: 32px max(16px, calc((100vw - 1040px) / 2)); }}
  h1 {{ font-size: 28px; margin: 0 0 8px; }}
  h2 {{ font-size: 20px; margin: 40px 0 8px; }}
  h3 {{ font-size: 16px; margin: 24px 0 8px; }}
  .anotado li {{ margin-bottom: 8px; }}
  code {{ font-family: var(--fonte-mono); font-size: 13px; }}
  .subtitulo, .nota {{ color: var(--cor-texto-secundario); }}
  .nota {{ font-size: 13px; }}
  .selos {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }}
  .selo {{ background: var(--cor-fundo-elevado); border: 1px solid var(--cor-borda);
           border-radius: 12px; padding: 2px 12px; font-size: 13px; }}
  .selo.bom {{ border-color: var(--cor-sucesso); color: var(--cor-sucesso); }}
  .selo.ruim {{ border-color: var(--cor-erro-texto); color: var(--cor-erro-texto); }}
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
  .rodape {{ margin-top: 40px; border-top: 1px solid var(--cor-borda); padding-top: 16px;
             font-size: 13px; color: var(--cor-texto-secundario); }}
</style>
</head>
<body>

<h1>Conferência 05 — lembrar as escolhas</h1>
<p class="subtitulo">Funcionalidade 8, emendas de 28/10/2026 das specs 002 e 001. Você pediu que o máximo fosse
conferido por teste automático, porque ia viajar: esta página mostra o que os testes já conferem sozinhos e, no
fim, o pouco que só a tela mostra, e o que ficou anotado para você decidir.</p>

<div class="caixa">As escolhas ficam num arquivo <code>preferencias.ini</code>, ao lado do <code>.env</code>, na
pasta da instalação. Nesta máquina de desenvolvimento ele mora na raiz do projeto, fora do histórico — e cada teste
usa um arquivo só dele, numa pasta provisória, para nunca misturar teste com uso de verdade.</div>

<h2>Onde a construção está</h2>
<div class="rolar"><table>
  <tr><th>Etapa</th><th>O que ela põe no programa</th><th>Situação</th></tr>
  {linhas_etapas}
</table></div>

<h2>O que os testes automáticos conferem</h2>
<div class="selos">
  <span class="selo {'bom' if not falharam else 'ruim'}">{passaram} testes da funcionalidade passando</span>
  <span class="selo {'bom' if not falharam else 'ruim'}">{falharam} falhando</span>
</div>
<p class="nota">Contados agora, rodando <code>programa/test_preferencias.py</code>,
<code>programa/test_janela_lembrada.py</code> e <code>programa/test_preferencias_caminhos_tortos.py</code>. Em cada teste, "fechar e abrir o programa" é montar o painel ou a
janela de novo: o que estava só na memória vai embora, e só o que foi gravado volta. Os testes da janela de verdade
a mostram por um instante, maximizada ou não, porque só o Windows responde a que tamanho ela volta.</p>
<div class="rolar"><table>
  <tr><th>O que é conferido</th><th>Onde</th></tr>
  {linhas_conferido}
</table></div>

<h2>O que fica para você conferir na tela</h2>
<p class="nota">Só o que um teste não consegue ver: a janela no seu monitor, e o instalador instalando e desinstalando
de verdade. Nada disto foi conferido ainda — as cinco etapas foram gravadas como "não conferido na tela", por
escolha sua. A janela não recarrega o código sozinha: feche e abra a cada passo.</p>

<h3>No desenvolvimento, nesta máquina</h3>
<div class="rolar"><table>
  <tr><th>Passo</th><th>O que fazer</th><th>O que deve acontecer</th></tr>
  {linhas_dev}
</table></div>

<h3>Instalado</h3>
<div class="rolar"><table>
  <tr><th>Passo</th><th>O que fazer</th><th>O que deve acontecer</th></tr>
  {linhas_instalado}
</table></div>

<h2>Anotado para você decidir</h2>
<p class="nota">O que a lente crítica achou nas revisões 43 a 47 e não era defeito claro. Nada disto foi mudado:
como combinado, eu anoto em vez de decidir por você.</p>
<ul class="anotado">{itens_anotados}</ul>

<p class="rodape">Página gerada em {DATA} pela skill-07-designer-de-telas, a pedido da
skill-08-construtor-de-funcionalidades (<code>conferencias/gerar-05-lembrar-as-escolhas.py</code>).</p>
</body>
</html>
"""
    destino = RAIZ / "conferencias" / "05-lembrar-as-escolhas.html"
    destino.write_text(pagina, encoding="utf-8")
    print(f"gerado: {destino.name} ({passaram} passando, {falharam} falhando)")


if __name__ == "__main__":
    main()

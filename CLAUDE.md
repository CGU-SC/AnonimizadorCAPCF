# Anonimizador CAPCF

## O que é

Programa para a CAPCF (Coordenadoria de Análise de Prestações de Contas
Fundacionais da UFSC) tirar o CPF de documentos antes de eles irem para
assistentes de IA em chatbots convencionais. Roda como janela própria, uma
pessoa por vez, instalado nas máquinas do núcleo. Só CPF é anonimizado — nome
não é considerado sensível para este uso.

## Stack e por quê

**Python 3.12**, pela prática de quem mantém o projeto e pelo ecossistema mais
maduro do mercado para ler PDF, rodar OCR e achar padrão com regex.

| Peça | Escolha |
| --- | --- |
| Interface | PySide6 (Qt) — menu lateral + painel principal |
| Leitura de PDF | PyMuPDF — extrai texto, detecta ausência de texto, converte página em imagem para o OCR |
| OCR | Tesseract, via pytesseract, com pacote de português |
| Validação de CPF | Sem biblioteca — dígito verificador calculado na mão |
| Dados | Sem banco — cada documento é processado sozinho, sem estado entre usos |
| Testes | pytest |
| Distribuição | instalador do Windows (Inno Setup) com o programa numa pasta montada pelo PyInstaller — sem exigir Python nas máquinas do núcleo. Era `.exe` único até 23/09/2026: com instalador a pasta não aparece, e o `.exe` único se desempacota a cada abertura (5 a 10 s) e o antivírus desconfia dele |

Descartado: C#/.NET (sem fluência de quem mantém) e Electron (mais pesado, OCR
pior). Atenção: PyMuPDF é AGPL — ok para uso interno da UFSC, conferir se um
dia o programa sair da universidade.

## Comandos

| O quê | Comando |
| --- | --- |
| Criar/atualizar o ambiente virtual | `python -m venv .venv` |
| Instalar as dependências | `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` |
| Rodar os testes | `.\.venv\Scripts\python.exe -m pytest` |
| Rodar o programa | `abrir\abrir-dev.bat` (ou `.\.venv\Scripts\python.exe programa\main.py`) |
| Gerar a entrega | `empacotar\gerar-entrega.bat` — roda os testes, monta a pasta do programa, o instalador e a pasta `builds\entrega-<versão>\` com o instalador e o roteiro. Pede o Inno Setup (`winget install --id JRSoftware.InnoSetup --exact`) e o instalador do Tesseract em `instaladores\` |

## Onde ficam as coisas

| Pasta | O que tem |
| --- | --- |
| `programa/` | o código do programa e os testes, lado a lado (nasce na primeira etapa construída) |
| `especificacoes/` | `backlog.md` e `backlog.html` (o previsto), `specs/` (o combinado de cada funcionalidade) |
| `mockups/` | rascundos de tela, sistema de design, mapa do entendimento — tudo desenhado pela `skill-07-designer-de-telas` |
| `dados-exemplo/` | massa sintética para testar — nunca documento real |
| `conferencias/` | as páginas que mostram o que o programa decidiu sobre a massa, para conferir sem abrir código (nasce na etapa 1 do Anonimizar) |
| `abrir/` | atalho de abrir o programa em modo desenvolvimento (nasce quando houver algo para ver na tela) |
| `empacotar/` | as receitas da entrega: a do PyInstaller (`anonimizador.spec`), a do instalador (`instalador.iss`), o `.env` em branco que o instalador cria (`modelo.env`), o roteiro para quem instala (`como-instalar.html`) e o atalho que gera tudo |
| `builds/` | o que a entrega gera: a pasta do programa, o instalador e a pasta `entrega-<versão>` que vai para o núcleo — conteúdo fora do histórico |
| `instaladores/` | o instalador do Tesseract que vai dentro do nosso — programa de terceiros, fora do histórico. Vem do GitHub da UB-Mannheim; confira o código SHA256 com o do catálogo do winget (`winget show --id UB-Mannheim.TesseractOCR`) |
| `.venv/` | ambiente virtual do Python — cada máquina cria o seu, fora do histórico |

## O combinado com quem usa

- **Quem usa**: o núcleo da CAPCF, uma pessoa por vez, cada uma na própria
  máquina — não é serviço compartilhado.
- **Entrada**: PDF, às vezes com texto por dentro (gerado no sistema de
  processos), às vezes só imagem (impresso, ou anexo escaneado por terceiro).
  O programa detecta sozinho se há texto, e só roda o OCR quando não há.
- **Saída**: `.md`, com as tabelas preservadas como tabelas de texto — para a
  pessoa arrastar para dentro da conversa com o assistente.
- **Máscara do CPF**: 3 primeiros dígitos → `XXX`, 2 últimos → `XX`, mantendo a
  pontuação original (`123.456.789-10` → `XXX.456.789-XX`; barra também vira
  traço). Reconhece CPF com pontos e traço, sem pontos, sem nada, e com barra.
  Era asterisco até 18/09/2026, e ele quebrava na tela de quem abre o arquivo:
  num `.md`, `***` e `**` são a marcação de negrito e itálico (sétima emenda da
  spec 003).
- **Motor de OCR**: dois no menu — Tesseract local, e (fora do escopo desta
  primeira versão) uma IA local, na própria máquina (LM Studio) ou num servidor
  dentro da rede da universidade. Na tela ela aparece apagada, como "IA local",
  com "Funcionalidade a ser implementada" embaixo. **Nunca** um serviço de
  empresa externa — seria contradizer o motivo do programa existir.
- **Conferência humana**: parte fixa do processo quando o texto veio de OCR, e
  não etapa opcional. O dígito verificador do CPF confere o que foi lido; o
  que não fechar vira lista de suspeitos para a pessoa olhar, em vez de passar
  calado.
- **PDF grande com vários documentos**: entra como um documento só, sai como um
  `.md` só. Separar por dentro é melhoria futura.
- **Quem faz**: o programa é desenvolvido pela CGU no âmbito da consultoria
  realizada à UFSC em 2026, e será entregue à universidade depois. Em texto
  para quem usa, não diga que a UFSC o fez. No instalador, o editor é "CGU".
- **Como chega em quem usa** (forma de entrega, decidida em 23/09/2026):
  **instalador** do Windows, instalado só para a pessoa, na pasta de programas
  dela (`%LOCALAPPDATA%\Programs\Anonimizador CAPCF`), **sem pedir
  administrador** — a funcionalidade 4 vai gravar configuração ao lado do
  programa, e em `Program Files` cada gravação pediria a confirmação do
  Windows. O instalador leva o do Tesseract (na pasta `instaladores`) e cria
  um `.env` em branco; a pasta que vai para o núcleo tem o instalador e o
  roteiro `Como instalar.html`. O número da versão mora em
  `programa/versao.py`, e aparece no pé da faixa da esquerda e no instalador;
  0.x é versão de teste, 1.0.0 fica para quando o núcleo aprovar o uso.
- **Fora de escopo desta versão**: outro dado sensível além do CPF; saída em
  XLSX ou PDF (fica para um "anonimizador de documentos" futuro); construir o
  assistente de IA em si; qualquer uso oficial do arquivo gerado.

## Regras duras

Três nascem do pacote de skills, e valem sempre:

- O agente trabalha **dentro desta pasta** (`c:\Dev\AnonimizadorCAPCF`). Sair
  dela é pedido do usuário, com caminho e tarefa nomeados, e vale só para
  aquela tarefa.
- **Segredo mora no `.env`**, nunca no código, nunca no chat, nunca no
  histórico. Dado real de pessoa (CPF, nome, documento) não entra no
  repositório de jeito nenhum, nem em `dados-exemplo/`.
- **Desenvolvimento e produção não compartilham** configuração nem dado. Aqui,
  "produção" é a instalação nas máquinas do núcleo, processando documento
  real; "desenvolvimento" é esta máquina, processando só massa sintética. Não
  existe `.env.producao` porque não há configuração central compartilhada —
  cada instalação tem o próprio `.env` local, preenchido na hora, nunca
  versionado.

Duas específicas deste projeto:

- **Tarja nunca substitui remoção.** Mascarar o CPF é reescrever o texto —
  nunca desenhar algo por cima que ainda deixa o número original por baixo,
  recuperável por quem copiar o texto.
- **Nenhum caminho de código aponta para um serviço de OCR ou LLM fora da
  UFSC.** É a razão de existir do programa: documento com CPF não pode sair da
  universidade para ser processado.

## Convenções

Idioma do projeto: português. Commits e comentários também.

Comentário no código: **em português, explicando o porquê, nunca o quê.**
Comentário que repete o que a linha já diz é ruído, e no dia em que a linha
muda e ele não, passa a mentir. Comenta-se a decisão que não está escrita em
lugar nenhum: por que este número, por que este caso é tratado à parte, de
onde veio esta regra. Linguagem do dia a dia — quem lê pode não programar.

## Como cada rodada fecha

Combinado em 17/09/2026, e vale sem perguntar de novo: **etapa conferida na tela
fecha com a revisão pela lente crítica** (`skill-09-revisor-de-codigo`) **e, em
seguida, o commit** (`skill-10-controlador-de-versoes`), com a fatia e a mensagem
apresentadas antes de gravar, e o push depois do ok.

A lente crítica é a que achou defeito em todas as rodadas até aqui — CPF
escapando inteiro, arquivo de texto bom recusado, o texto inteiro sublinhado
depois de um clique. As outras lentes continuam sendo oferta, e não rotina: ao
fim da revisão, diga quais ficaram de fora e o que elas veriam.

## Decidido antes de esquecer

- **A etapa do PDF pelo Anonimizar (etapa 7) começa extraindo o caminho do PDF,
  e não o copiando.** Hoje a verificação da camada de texto, a escolha do motor,
  a leitura em segundo plano com progresso e cancelamento, a falha de leitura e
  a conferência moram dentro do `programa/painel_ocr.py` (1.246 linhas),
  amarrados às telas e ao estado dele. A spec 003 (RN-15) manda esse mesmo
  caminho rodar dentro do Anonimizar. Copiar deixaria duas cópias de umas 600
  linhas, que divergem na primeira correção — foi o que quase aconteceu em
  18/09/2026, quando a janela do Windows precisou do mesmo conserto nos dois
  módulos. Então: a primeira fatia da etapa 7 é tirar o caminho do PDF para uma
  peça própria, usada pelos dois painéis, antes de qualquer tela nova
  (revisão pela lente de manutenção, 18/09/2026).

## O que já nos mordeu

- Instalar programa em `Program Files` (como o Tesseract) exige confirmação do
  Windows que só aparece numa sessão com tela — comando rodado por controle
  remoto ou terminal sem interface trava nessa hora. Resolve rodando com
  alguém na frente da máquina para confirmar.
- O Tesseract pode estar instalado e mesmo assim o `pytesseract` dizer que não
  achou: ele procura só no caminho que o Windows conhece, e o instalador não
  põe o Tesseract lá. Antes de concluir que falta instalar, olhe em
  `C:\Program Files\Tesseract-OCR\tesseract.exe`. O programa procura nas
  pastas de sempre por conta própria (`programa/motor.py`, desde 12/09/2026),
  e numa máquina onde a TI instalou em outro lugar ela grava a pasta no `.env`,
  em `TESSERACT_CAMINHO`. Mexer no caminho do Windows resolveria só esta
  máquina, e as do núcleo continuariam quebradas.
- Para ver na tela o aviso de motor faltando sem desinstalar nada, abra pelo
  `abrir\abrir-sem-motor.bat` (ou `abrir\abrir-sem-portugues.bat`, para o
  Tesseract instalado sem o pacote de português); o
  `abrir\simular-instalacao.bat` faz o motor "aparecer" com o programa aberto.
  Instalado sem o português, o Tesseract não serve — toda leitura falharia —,
  e o programa o trata como motor faltando. No dia da entrega, o instalador do
  Tesseract vai na pasta `instaladores`, ao lado do `.exe` — sem ele, o botão
  "instalar agora" fica apagado.
- Desenhar PDF com o Qt no modo "sem tela" (`QT_QPA_PLATFORM=offscreen`) sai
  com um quadradinho preto no lugar de cada letra: nesse modo o Qt não enxerga
  as fontes instaladas no Windows. A página fica cheia de caixas, o OCR não lê
  nada, e nada no caminho acusa erro — o arquivo parece pronto. Deixe o Qt
  subir no modo normal, mesmo quando nenhuma janela vai aparecer.
- Texto com quebra de linha dentro de caixa de largura limitada (`QLabel` com
  `setWordWrap`) sai **cortado** no Qt: a caixa reserva a altura de uma linha
  só, e o resto da frase some para fora da borda, sem nenhum aviso. Aconteceu
  na caixa de erro do Módulo de OCR em 10/09/2026. Resolve dando largura fixa
  ao texto e calculando a altura a partir dela (`heightForWidth`), e
  recalculando sempre que a frase mudar. Vale para toda caixa de aviso, erro ou
  explicação que o programa vier a ter. **E a conta precisa de um
  `ensurePolished()` antes dela**: sem isso o Qt mede a frase com a fonte padrão,
  e não com a do estilo que acabou de ser posto — a diferença é a última linha,
  que some (caixa da dupla conferência, etapa 3 do Anonimizar, 16/09/2026).
- Tela do Qt criada dentro de um teste e deixada para trás faz a lista inteira
  de testes **terminar com erro mesmo passando**: todos os testes passam, e o
  comando devolve código de erro na saída, sem nenhuma mensagem. A tela só é
  desmontada quando o Python fecha, e aí o Qt já foi desligado. Resolvido em
  10/09/2026 com o `programa/conftest.py`, que desmonta as telas no fim de cada
  teste. Quem olha só o resultado do comando concluiria que a lista falhou.
- Script provisório (gerar uma página, testar uma ideia) **não roda da pasta
  temporária do sistema**: a cerca do agente bloqueia tudo fora do projeto, e
  mandar o script inteiro direto para o terminal do Bash quebrou num script
  longo, com "unexpected EOF" e nada rodado. Resolve gravando o script dentro
  do projeto, rodando e apagando em seguida (etapa 1 do Anonimizar, 15/09/2026).
- **Traço ondulado não sai por folha de estilo no Qt.** O
  `text-decoration: underline wave` é ignorado num `QLabel`: o traço sai reto,
  igual ao do outro tipo, e a tela perde justamente a diferença que ela existe
  para mostrar — e nada acusa erro. Só o texto rico faz ondulado
  (`QTextCharFormat.WaveUnderline`). Por isso a chave de cores da revisão é um
  pedacinho de texto, e não um rótulo comum (`programa/tela_revisao.py`, etapa 2
  do Anonimizar, 16/09/2026).
- **A janela não recarrega o código sozinha.** O atalho de abrir sobe o programa
  em modo de desenvolvimento, mas o Qt não troca o código com a janela de pé:
  toda conferência de tela depois de uma alteração pede fechar e abrir de novo.
  Sem isso, a pessoa confere a versão velha achando que é a nova.
- **Pôr texto novo num `QTextEdit` herda a formatação que está debaixo do
  cursor.** Se o cursor tinha acabado de passar por um trecho destacado, o texto
  inteiro sai com aquele destaque - foi o que aconteceu na revisão do Anonimizar
  depois de um "Desfazer": tudo ficou amarelo e sublinhado. Resolve devolvendo a
  formatação comum ao documento inteiro antes de pintar os destaques
  (`programa/tela_revisao.py`, etapa 3, 17/09/2026).
- **Lista com conteúdo mais largo que a coluna desliza para o lado sozinha.**
  Numa área de rolagem, quando algum item pede mais largura do que cabe, o
  programa rola para os lados ao mostrar um item - e a primeira letra de tudo
  fica cortada, sem nada acusar. Resolve de duas formas, e as duas valem: não
  deixar o conteúdo passar da largura (uma etiqueta comprida desce para a linha
  de baixo) e rolar só na vertical (`programa/lista_de_achados.py`, etapa 3 do
  Anonimizar, 17/09/2026).
- Trabalho que roda ao lado da janela (uma `QThread`) precisa ser **parado antes
  de a janela fechar**. Sem isso, fechar o programa no meio de uma leitura o faz
  estourar em vez de fechar limpo, e o Windows mostra a caixa de "o programa
  parou de funcionar" — que assusta quem usa e ainda deixa a dúvida de se o
  documento foi mexido. Reproduzido e resolvido em 10/09/2026, com o
  `closeEvent` da janela pedindo o encerramento e esperando.
- **Fileira do Qt espreme o texto em vez de descer, e ninguém avisa.** Um
  `QHBoxLayout` com mais peças do que cabe corta o texto de todos os botões
  pela metade — "Mascarar o trecho marcado" saía cortado até em janela de
  1400 px. Antes de pôr peça nova numa linha, **meça** (`sizeHint` contra a
  largura real, na janela mínima de 900 px e na de 1000 px em que ela abre),
  em vez de confiar no olho. Quando não cabe, a peça desce de linha
  (`programa/linha_que_desce.py`), vai para outro lugar, ou o texto quebra com
  `\n` escrito nele (entrega, 23/09/2026).
- **Regra de cor sem alvo vale para tudo o que está dentro.** No Qt, uma folha
  de estilo `QFrame { background: ... }` pinta também cada texto de dentro
  (todo `QLabel` é um `QFrame`), e a regra do painel em `main.py` pinta todo
  texto com o fundo da janela. O efeito são caixinhas de outro tom em volta de
  cada frase. Quadro com fundo próprio leva a regra pelo nome
  (`QFrame#quadro`) **e** `QLabel { background: transparent; }`; e um
  `QWidget` comum só pinta o próprio fundo com `WA_StyledBackground` (entrega,
  24/09/2026).
- **`.env` criado no Bloco de Notas sai `.env.txt`**, e o Windows esconde o
  `.txt`: na pasta ele parece certo, e o programa o ignora calado. Por isso o
  instalador já cria o `.env` em branco, para só ser editado (teste da
  entrega, 25/09/2026).
- **A cerca do agente bloqueia gravar fora do projeto**, até na pasta do
  programa instalado para teste e na pasta de memória. No teste da entrega, o
  `.env` da instalação foi criado pela pessoa — o que, de quebra, revelou o
  `.env.txt` acima.
- **O instalador do Tesseract 5.4.0 tem assinatura vencida**: o certificado da
  Universidade de Mannheim venceu antes de o arquivo ser assinado, e o Windows
  mostra "Editor: Desconhecido" na confirmação de administrador. O arquivo é o
  autêntico (o SHA256 bate com o do catálogo do winget); o roteiro de
  instalação avisa a pessoa antes. E ele baixa o português da internet durante
  a instalação.

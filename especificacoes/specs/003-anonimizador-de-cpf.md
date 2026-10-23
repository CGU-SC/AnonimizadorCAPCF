# Spec 003 — Módulo de Anonimizador de CPF

**Status:** aprovada
**Data:** 2026-09-13
**Aprovada em:** 2026-09-14
**Emenda:** aprovada em 2026-09-14 — o "quase CPF" que passa na conta
passa a pedir a dupla conferência para ser liberado, e entra no lembrete antes de
salvar (RN-2, RN-10 e RN-11). Veio da revisão dos rascunhos de tela 02 e 03.
**Segunda emenda, desfeita no mesmo dia:** o formato único `***.456.789-**`
para todo número mascarado chegou a ser aprovado em 2026-09-14 e foi desfeito
horas depois, a pedido da usuária. A máscara continua mantendo a pontuação
original (RN-6), por dois motivos: preserva o formato do documento, e um número
mascarado por engano como CPF continua reconhecível pelo formato que tinha — a
não ser pela barra antes dos dois últimos, que continua virando traço.
**Terceira emenda:** aprovada em 2026-09-14 — no "Anonimizar", a
escolha do motor de leitura sai da tela de escolher o arquivo e aparece só
quando o PDF vai ser lido como imagem (sem camada de texto, ou quando a pessoa
escolhe ignorar a camada e ler as imagens). Na primeira tela ela confundia:
parecia preciso escolher um motor até para anonimizar um `.md`. O aviso de motor
faltando continua na primeira tela, e a tela do "Gerar OCR" não muda.
**Quarta emenda:** aprovada em 2026-09-16 — o limite de letras no lugar de
dígito do "quase CPF" passa a depender da pontuação: até 4 letras quando ponto,
traço ou barra separam os grupos, e 2 quando não há separador nenhum ou só
espaços (premissa das letras, RN-2 e o critério de aceite correspondente). Veio
da conferência da etapa 2 da construção: `l23.4S6.789-1O` saía inteiro, e o
número continuava reconhecível. Pontuação nos lugares exatos de um CPF quase
nunca aparece em palavra ou código; sem ela, a sequência tem cara de código.
**Quinta emenda:** aprovada em 2026-09-17 — letra no fim do número, grudada numa
palavra, não conta como dígito **quando o número não tem pontuação de CPF**
(premissa das letras e critério de aceite). Veio do teste da usuária com um
documento de verdade, na própria máquina: "Número:" seguido de 9 dígitos no fim
da linha e "Situação:" na linha de baixo dava um "quase CPF partido em duas
linhas" a cada ocorrência — 18 num documento só. A ressalva da pontuação entrou
na revisão da mesma etapa, horas depois: sem ela, um CPF pontuado cuja última
letra encostava numa palavra saía inteiro e fora da lista.
**Sexta emenda:** aprovada em 2026-09-17 — na máscara feita à mão, a letra
parecida com dígito conta como posição quando o trecho marcado é só um número
(premissa da máscara à mão, RN-9 e critério de aceite). Contando só dígitos, o
`l23.4S6.789-1O` viraria `lXX.XS6.78X-XO`, com o primeiro e o último dígito do
número à vista — e é justamente esse caso que leva alguém a mascarar à mão.
**Acréscimo:** em 2026-09-17, a pedido da usuária na conferência da etapa 3 —
a navegação "‹ anterior · N de M · próximo ›" na revisão (escopo e critério de
aceite), o filtro dela pelos selos, e os selos contando grupos separados cuja
soma dá o total — o primeiro selo passa de "números mascarados" a "números
encontrados", porque, com algo liberado, nem tudo o que foi encontrado está
mascarado. Não muda regra nenhuma de máscara.
**Sétima emenda:** aprovada em 2026-09-18 — a máscara passa a ser o `X`
maiúsculo no lugar do asterisco (RN-6): `123.456.789-10` → `XXX.456.789-XX`.
Veio da conferência da etapa 5, ao abrir o arquivo gravado: num `.md`, `***` e
`**` são a marcação de negrito e itálico, e o visualizador — o próprio Bloco de
Notas do Windows abre `.md` formatado — engolia os asteriscos grudados na
pontuação e mostrava `*.222.222-` no lugar da máscara. O arquivo estava certo por
dentro, mas quem o recebesse veria a tarja quebrada. Testadas cinco formas num
arquivo aberto no Bloco de Notas: o `X` é a única que fica igual nas duas visões
— texto cru e formatado —, em qualquer posição, e não exige escrever no documento
nenhum sinal que não estava nele (RN-12). Os exemplos deste documento foram
reescritos com a máscara nova, menos o registro da segunda emenda, que fica como
foi discutido na época.
**Oitava emenda:** aprovada em 2026-09-18 — as duas decisões que faltavam para
as etapas 7 e 8 poderem ser construídas sem adivinhação. **(a) No Anonimizar, o
PDF segue o desenho do rascunho 08, sem o cartão do Gerar OCR no meio**: o PDF
sem texto por dentro abre a tela "Este documento precisa ser lido", com o nome,
as páginas e a escolha do motor logo acima do botão de ler (estado 3a); o PDF com
texto por dentro vai direto para a tela de decidir, que já mostra nome, páginas,
letras e as primeiras linhas (estado 3b); e "Ignorar e ler as imagens" leva à
mesma tela de ler, dizendo que o texto de dentro será ignorado (estado 3c). Nos
dois caminhos o tamanho do documento aparece antes de qualquer leitura. *Parte
corrigida em 21/09/2026:* a primeira versão pedia o cartão do Gerar OCR também
aqui, e foi decidida sem reler os estados 3a e 3b do rascunho aprovado, que já
respondiam a pergunta - e com um clique a menos. **(b) Depois do "Seguir para
Anonimizar", o Gerar OCR fica
exatamente como estava**: o texto conferido continua na tela de escolher a saída,
e voltando pelo menu dá para salvar o texto como está ou seguir de novo. Um
clique por engano não joga fora uma leitura de PDF, que custa minutos — e é
justamente o que a pergunta antes de descartar existe para proteger. Um segundo
"Seguir para Anonimizar", com revisão aberta e não salva do outro lado, passa por
essa pergunta.
**Nona emenda:** aprovada em 2026-10-20 — **o CPF que perdeu o zero da
frente** (funcionalidade 6 do backlog). O número solto de 10 ou de 9 dígitos que,
com os zeros de volta na frente, fecha a conta do dígito verificador passa a ser
CPF válido (RN-1), com a etiqueta "sem o zero da frente" na revisão. Na máscara,
ele volta a ter 11 dígitos, no mesmo jeito em que estava escrito (RN-6), e a
coluna da tabela é compensada com os espaços de depois dele. Isso desfaz, só para
ele, a premissa de que a máscara tem o tamanho do original. Veio do teste da
versão 0.1.0, em 25/09/2026: num formulário real do SIGPEX, o CPF de 10 dígitos
saía inteiro, sem marca na revisão. Medido no mesmo formulário (só as contagens,
nenhum número): os 6 números de 10 dígitos fecham a conta, nenhum dos 13 de 9
dígitos fecha, e nenhum dos 6 tem a palavra "CPF" logo antes, porque estão numa
coluna de tabela. Levantamento em
`mockups/requisitos/05-mapa-do-entendimento.html`, que refaz o 04 (no 04, a
máscara mantinha o tamanho, e a usuária derrubou isso). Uma premissa do mapa
mudou ao escrever esta emenda: a massa não ganha telefone que fecha a conta, e o
curto que fecha a conta é só de zeros, porque a RN-22 vale inteira.
**Acréscimo à nona emenda:** aprovado em 2026-10-22, na conferência na tela da
funcionalidade 6, em dois acordos curtos. **(a) O clique no número do texto**:
um clique simples num número destacado do texto da revisão acende o item dele na
lista, rola a lista até ele e acerta o "N de M", como o "próximo ›" - para todo
número da lista. Arrastar o mouse para marcar um trecho continua como antes. Era
preciso percorrer a lista inteira para achar o item de um número visto no texto.
**(b) As frases do CPF curto**: ele tem mais chance de ser alarme falso, e o
programa deixa de dizer que ele "quase certamente" é CPF. Na caixa da dupla
conferência, "pode ser o CPF de alguém". No aviso de antes de gravar, ele leva a
etiqueta "sem o zero da frente", e a frase do alto depende de quem foi liberado:
só CPF completo, como antes ("Eles quase certamente são o CPF de alguém."); só
curto, "Eles podem ser o CPF de alguém."; os dois, "Os válidos quase certamente
são o CPF de alguém e os sem o zero da frente podem ser CPF ou outro dado, como
um telefone." (texto da usuária). O título do aviso fica como está.
**Décima emenda:** aprovada em 2026-10-23 — **o documento do Word**
(funcionalidade 5 do backlog). O Anonimizar passa a abrir o `.docx` e leva para
a revisão tudo o que aparece no documento impresso: o corpo, as tabelas (com
barras, no formato de tabela do `.md`), o cabeçalho e o rodapé, as notas e as
caixas de texto, com as alterações controladas aceitas. O que o Word guarda e
não imprime (comentários, texto oculto) e as imagens ficam de fora, e uma faixa
na revisão diz o que ficou (RN-23 a RN-30). Só o `.docx`: o `.doc` antigo, o
`.docm` e o `.dotx` continuam de fora. O arquivo gerado continua sendo só o
`.md`, e o fora de escopo registra por que o programa não devolve o próprio
Word mascarado. A leitura usa só o que já vem no Python (o `zipfile` e o
`xml.etree.ElementTree`), sem biblioteca nova: a de PDF que o programa usa não
abre `.docx` na versão gratuita, e a python-docx não lê caixa de texto, nota nem
alteração controlada (decisão de 23/10/2026). Levantamento em
`mockups/requisitos/06-mapa-do-entendimento.html`. Pedida em 16/09/2026, na
conferência da etapa 2 do Anonimizar.
**Correções de texto na tela:** em 2026-09-16, o rótulo do tipo "passa na conta" encurtou de "forma CPF válido" para **"CPF válido"**, a pedido da usuária, e passou ao vermelho (seção Dados). Não muda regra nenhuma.
**Correções de texto:** aprovadas em 2026-09-14 — quatro trechos que se
contradiziam depois das emendas, achados na revisão dos rascunhos 04 a 07. Não
mudam o combinado: o nome na tela do tipo "passa na conta" nos critérios, o que
a caixa da dupla conferência mostra, o motor faltando num PDF com texto, e esta
nota sobre a barra.
**Origem:** levantamento detalhado de 13/09/2026, registrado em
`mockups/requisitos/02-mapa-do-entendimento.html`. Uma resposta mudou na hora de
escrever: a linha no topo do arquivo (R-11 do mapa) saiu, porque ia contra a
RN-11 da spec 002. A regra "o arquivo tem o texto e mais nada" passa a valer
para os dois arquivos que o programa gera.

## Objetivo

Entregar à pessoa um `.md` **sem nenhum CPF inteiro**, pronto para arrastar
para a conversa com o assistente de IA, partindo de um PDF, de um documento do
Word (`.docx`, décima emenda), de um `.md` ou `.txt` que já existe, ou do texto
que ela acabou de conferir no "Gerar OCR". É o
módulo que dá razão ao programa existir: documento com CPF não pode ir para um
chatbot.

## Escopo

- Ocupar o painel do item "Anonimizar" do menu lateral, no lugar do aviso de
  "ainda não construído" da spec 001.
- Escolher um arquivo da máquina, pelo botão ou arrastando: **PDF, `.md` ou
  `.txt`**.
- **PDF**: passar pelo caminho do módulo de OCR que já existe (decisão sobre a
  camada de texto, leitura, **conferência obrigatória**) e, conferido, seguir
  direto para a revisão, sem oferecer salvar o texto com CPF inteiro.
- **`.md` ou `.txt`**: ir direto para a revisão.
- **`.docx`** (décima emenda): tirar de dentro dele o texto do documento
  impresso — corpo, tabelas, cabeçalho, rodapé, notas e caixas de texto, com as
  alterações controladas aceitas —, montar o `.md` com títulos, listas e
  tabelas, e ir direto para a revisão, com a faixa do que ficou de fora quando
  houver. A escolha do arquivo passa a aceitar **PDF, `.docx`, `.md` ou
  `.txt`**, e a massa de teste ganha documentos do Word inventados, gerados por
  script.
- **Acender o botão "Seguir para Anonimizar"** no fim do "Gerar OCR", que leva o
  texto conferido para a revisão por dentro do programa, sem passar por arquivo.
- Encontrar CPF nos quatro formatos combinados e também o **"quase CPF"**: o
  número que o OCR estragou trocando dígito por letra, trocando a pontuação por
  espaço ou quebrando entre duas linhas.
- Encontrar também o **CPF que perdeu o zero da frente** (nona emenda): o
  número de 10 ou de 9 dígitos que fecha a conta com os zeros de volta, escrito
  só com dígitos ou com a pontuação do CPF. Ele é mascarado com os 11 dígitos de
  volta, e a coluna da tabela em que ele está continua reta.
- Conferir cada número encontrado pela **conta do dígito verificador**,
  separando o que passa na conta do que é **suspeito**.
- **Mascarar tudo o que foi encontrado**, suspeitos inclusive.
- **Tela de revisão**, que aparece sempre: o texto já mascarado com cada troca
  destacada, e a lista de suspeitos ao lado.
- **Navegar pelos números sem rolar a tela** (acréscimo de 17/09/2026):
  "‹ anterior · N de M · próximo ›" acima do texto, percorrendo todos os números
  da lista na ordem em que aparecem no texto. Cada passo leva o texto até o
  número e marca o item dele na lista, como o clique na lista. Clicar num selo
  do alto ("CPFs válidos", "suspeitos", "liberados por você") faz a navegação
  percorrer só aquele grupo; o texto e a lista continuam inteiros.
- Mascarar à mão o trecho que o programa não pegou.
- Desfazer uma máscara: um clique para o suspeito que falha na conta e para a
  máscara feita à mão; **dupla conferência** para todo número que passa na conta,
  inclusive o "quase CPF" que passa.
- Avisar quando **nenhum CPF** for encontrado.
- Salvar como `<nome da origem> - sem CPF.md`, na pasta da origem, com o
  caminho preenchido e editável, perguntando antes de escrever por cima.
- Na confirmação de "salvo", lembrar que o arquivo de origem continua na pasta
  com os CPFs inteiros.
- Atualizar o aviso da tela de salvar do "Gerar OCR", que hoje diz que o
  Anonimizar "ainda vai ser construído".
- Massa de teste nova em `dados-exemplo/`, com CPF que passa na conta, suspeito,
  quase CPF, CNPJ e número de processo, **nenhum deles de pessoa real**.

## Fora de escopo

- **Qualquer dado sensível além do CPF.** Nome continua não sendo sensível
  para este uso.
- **Qualquer linha escrita pelo programa dentro do arquivo de saída**, seja
  cabeçalho, aviso, contagem ou lista de suspeitos. O arquivo tem o texto do
  documento, mascarado, e mais nada (RN-11 da spec 002, que passa a valer aqui).
- **Mexer no PDF.** Nem tarja por cima, nem PDF mascarado. A máscara reescreve o
  texto e só o texto: tarja que deixa o número por baixo não é remoção.
- **Saída em qualquer formato que não seja `.md`.** Nada de XLSX, DOCX, PDF.
- **Uma caixa para colar texto direto, sem arquivo.** Foi oferecida no
  levantamento e não entrou.
- **Apagar o arquivo de origem**, mesmo o `.md` com CPF inteiro.
- **Editar livremente o texto na revisão.** Corrigir a leitura é trabalho da
  conferência do OCR. Aqui só se mascara e se desfaz máscara.
- **Mascarar número que não é CPF de propósito**, como CNPJ, número de processo,
  conta bancária, telefone ou linha de boleto.
- **CPF escrito de um jeito que não seja nenhum dos da RN-1 e da RN-2**, como
  por extenso ou com os dígitos separados por outros símbolos. Para esse, a rede
  é a revisão humana e o "mascarar à mão".
- **Do CPF sem o zero da frente** (nona emenda): o que **não fecha a conta**,
  que não é achado nem vira suspeito (no formulário do SIGPEX, seriam 13
  suspeitos novos, nenhum deles CPF); o que **a leitura estragou**, com letra no
  lugar de dígito, espaço no lugar do ponto ou partido em duas linhas, que é raro
  e encheria o texto de alarme falso; o de **8 dígitos ou menos**; e procurar
  a palavra "CPF" por perto para decidir, que perderia o CPF em coluna de tabela.
  Para esses, a rede continua sendo a revisão humana e o "mascarar à mão".
- **O aviso de "limitação conhecida" do roteiro `como-usar.html`.** Ele cai
  quando os roteiros forem refeitos para a próxima entrega, num prompt próprio.
- **Do documento do Word** (décima emenda):
  - **o `.doc` antigo**, que exigiria o Word instalado ou um programa a mais nas
    máquinas do núcleo; **o `.docm`** (documento com macros) **e o `.dotx`**
    (modelo), que recebem a frase de "outro tipo";
  - **ler o texto de dentro das imagens** coladas no documento. Quem precisar,
    salva o documento como PDF pelo Word e usa o caminho do PDF, que lê
    imagens;
  - **comentários, texto oculto, o trecho apagado das alterações controladas,
    a descrição escondida das imagens e o endereço por trás dos links**: nada
    disso vai para o arquivo;
  - **negrito, itálico, cor, fonte** e qualquer formatação além de títulos e
    listas;
  - **planilha (`.xlsx`) e apresentação (`.pptx`)**.
- **Devolver o próprio Word com os CPFs mascarados.** Perguntado em 23/10/2026,
  e decidido que não se faz, nem agora nem depois: não vai para o backlog. Os
  motivos, para ninguém refazer a conta: (1) o Word guarda o texto em pedaços
  cortados onde ele quiser — uma mudança de fonte, a correção ortográfica, uma
  edição antiga —, e `123.456` pode estar num pedaço e `.789-10` no seguinte;
  mascarar ali é trocar dígito dentro de cada pedaço sem estragar o resto. (2)
  Cada decisão da revisão — a máscara à mão, o número liberado, a coluna
  compensada do CPF curto — é tomada sobre o texto do `.md` e teria de voltar à
  posição exata dentro do Word. (3) O `.md` só leva o que o programa leu; o Word
  leva o arquivo inteiro, e o CPF teria de sair também dos comentários, do
  trecho apagado das alterações, do texto oculto, do endereço dos links, das
  propriedades do arquivo, da miniatura da primeira página e da planilha colada
  dentro do documento — o que faltasse escaparia calado. (4) O CPF numa imagem
  não se reescreve: pela regra "tarja nunca substitui remoção", a imagem teria
  de sair do arquivo, ou o arquivo ser recusado. (5) Somaria umas cinco ou seis
  etapas às do `.md`, e seria a parte com mais chance de vazar sem ninguém ver.
- **Vários arquivos de uma vez**, e separar um PDF que traz vários documentos.
- **Guardar histórico** do que foi anonimizado.
- **A leitura por IA local.** É o item 4 do backlog.

## Premissas

Inferências do levantamento que você leu e não derrubou, mais três que
apareceram ao escrever esta spec (marcadas com *nova*).

- premissa: no "quase CPF", a máscara cai nas 3 primeiras e nas 2 últimas
  posições, mesmo que haja letra ali (`l23.456.789-1O` → `XXX.456.789-XX`). O
  CPF quebrado entre duas linhas é mascarado nas duas partes, e a quebra fica
  onde estava.
- premissa: número de dígitos repetidos (`111.111.111-11`) passa na conta e é
  tratado como CPF. A Receita não os emite, mas escondê-los não custa nada.
- premissa: desfazer a máscara de um suspeito que falha na conta ou de uma
  máscara feita à mão é um clique, sem caixa de confirmação. O "quase CPF" que
  passa na conta não entra aqui: ele pede a dupla conferência (RN-10).
- premissa: a máscara troca cada dígito por um asterisco, um por um. O tamanho
  do número não muda, e a tabela de texto continua alinhada. *Emendada na nona
  emenda:* a exceção é o CPF sem o zero da frente, que cresce 1 ou 2 posições
  (RN-6), e a tabela continua alinhada pela compensação dos espaços.
- premissa: clicar num suspeito da lista leva o texto até ele.
- premissa: sair da revisão sem salvar (trocar de item do menu ou fechar a
  janela) pergunta antes de descartar, como o "Gerar OCR" já faz.
- premissa: o item marcado no menu é "Anonimizar" o caminho todo, inclusive
  enquanto o PDF passa pela leitura e pela conferência. Vindo pelo botão do
  "Gerar OCR", a revisão abre com "Anonimizar" marcado.
- premissa: um arquivo que já foi anonimizado, aberto de novo, dá "nenhum CPF
  encontrado". Os asteriscos não se parecem com dígito.
- premissa: o `.txt` abre com os acentos certos, seja qual for o jeito como o
  Bloco de Notas o gravou.
- premissa: arquivo vazio, ou que não é texto de verdade, dá uma mensagem de
  erro e volta à escolha do arquivo. PDF corrompido ou com senha usa os avisos
  que o "Gerar OCR" já tem.
- premissa: vale o que já vale no OCR. Um arquivo por vez, nada guardado entre
  um uso e outro, e o arquivo de origem nunca é alterado.
- premissa: o botão "Seguir para Anonimizar" do "Gerar OCR" acende, e o aviso da
  tela de salvar passa a apontar para o Anonimizar pronto.
- premissa (*nova*, emendada em 14/09/2026): no "Anonimizar", o aviso de motor
  faltando aparece igual ao "Gerar OCR", na primeira tela. A escolha do motor,
  não: ela aparece só quando o PDF vai ser lido como imagem — sem camada de
  texto, ou quando a pessoa escolhe ignorar a camada e ler as imagens —, com
  "Tesseract (nesta máquina)" marcado. Para `.md` e `.txt`, o motor não importa e
  o aviso não bloqueia nada.
- premissa (*nova*, emendada em 16/09/2026): para contar como "quase CPF", o
  limite de letras no lugar de dígito **depende da pontuação**. Havendo ponto,
  traço ou barra separando os grupos, cabem **até 4 das 11 posições**: sobram 7
  dígitos certos, e a pontuação exata de um CPF quase nunca aparece numa palavra
  ou num código. Sem separador nenhum, ou só com espaços, o limite é **2**: ali a
  sequência tem cara de código, protocolo ou lista de números, e marcar com mais
  letras encheria a lista de alarmes.
- premissa (*nova*, quinta emenda, 17/09/2026): **letra no fim do número,
  grudada numa palavra, é começo de palavra, e não dígito** — e a sequência não
  conta como "quase CPF". É o caso de um número de 9 dígitos no fim de uma linha
  seguido de "Situação", "Solicitante" ou "Objeto" na linha de baixo: o "Si", o
  "So" e o "Ob" fechavam as 11 posições. **Duas ressalvas, e as duas existem
  para não deixar CPF escapar:** a regra vale só quando o número **não tem
  pontuação de CPF** (com ponto, traço ou barra nas posições exatas, como em
  `111.111.111-1lAssinado`, ele continua sendo achado), e vale só para a ponta
  final — na ponta do começo, a letra grudada continua contando, porque a
  leitura cola o "CPF" no número (`CPFl11.111.111-11`).
- premissa (*nova*, emendada em 17/09/2026): a máscara feita à mão esconde as 3
  primeiras e as 2 últimas **posições** do trecho marcado. Se o trecho tiver 5
  posições ou menos, esconde todas. Trecho sem nenhum dígito não muda nada, e a
  tela diz por quê. **O que conta como posição depende do trecho:** num trecho
  que é só um número — dígitos, letras parecidas com dígito e pontuação, como
  `l23.4S6.789-1O` —, a letra conta como posição, igual à máscara automática, e
  ele vira `XXX.4S6.789-XX`; num trecho que traz palavras, contam só os dígitos,
  senão o programa mascararia o "S" e o "o" de "Sobre" e deixaria dígitos à
  vista. É justamente o número que a leitura estragou demais que a pessoa vai
  querer mascarar à mão, e contar só dígitos ali deixaria o primeiro e o último
  do número à mostra.
- premissa (*nova*): máscara desfeita pode ser refeita. O item continua na
  lista, marcado como "liberado", com a opção de mascarar de novo.

Da nona emenda, as inferências do mapa 05 que a usuária leu e não derrubou, mais
duas que apareceram ao escrever (marcadas com *nova*):

- premissa: o CPF sem o zero da frente é achado em todo caminho do Anonimizar:
  PDF com texto por dentro, PDF lido como imagem, `.md` e `.txt`. O Gerar OCR
  continua sem nenhuma linha de CPF (RN-18).
- premissa: a RN-3 vale igual para ele. Os 10 ou 9 dígitos colados a outro
  dígito, ou ligados a ele por ponto, traço ou barra, não contam.
- premissa: o CPF que perdeu três zeros ou mais (8 dígitos ou menos) fica de
  fora. Quanto menos dígitos, menos a conta separa CPF de número qualquer.
- premissa: soltá-lo pede o mesmo cuidado de qualquer CPF válido: a dupla
  conferência (RN-10), com o número como está escrito no documento, e o aviso
  antes de gravar (RN-11). Nos selos do alto, ele conta junto com os CPFs
  válidos.
- premissa: o número que não é CPF e fecha a conta por acaso (cerca de 1 em cada
  100 números curtos soltos, como um telefone com DDD) sai mascarado e aparece
  na lista com a etiqueta. A pessoa o solta pela dupla conferência. Entre um
  alarme falso e um CPF que escapa calado, fica o alarme (RN-5).
- premissa: no curto, valem as pontuações da RN-1 com o grupo da frente mais
  curto (2 dígitos, ou 1): pontos e traço, só o traço, pontos e barra, e nada.
  Qualquer outra mistura fica de fora.
- premissa: soltá-lo devolve exatamente o que estava no documento, com os 10 ou
  9 dígitos e os espaços que a compensação da coluna tinha tirado. Mascarar de
  novo refaz as duas coisas.
- premissa (*nova*): letra grudada **antes** do curto não o impede de contar
  (`CPF0000000000`), como no CPF completo: a leitura cola o "CPF" no número
  (quinta emenda). Só dígito colado o impede (RN-3).
- premissa (*nova*): com 9 dígitos, a etiqueta diz "sem os zeros da frente",
  no plural. É o mesmo tipo, com a frase certa para dois zeros.
- premissa (*nova*): o curto que fecha a conta, na massa e nos testes, é só de
  zeros (RN-22). O formato da máscara com outros dígitos é conferido direto na
  regra que mascara, com números que não fecham a conta — com tudo zero, o teste
  não veria um dígito fora do lugar. O telefone que fecha a conta não entra na
  massa: ele seria um CPF que pode existir.

Da décima emenda, as inferências do mapa 06 que a usuária leu e não derrubou,
mais quatro que apareceram ao escrever (marcadas com *nova*):

- premissa: o texto do `.docx` vai direto para a revisão, sem leitura nem
  conferência, como o `.md` e o `.txt`: é texto de verdade, e não leitura de
  imagem. A revisão, a máscara, a dupla conferência e o salvar são os de hoje.
- premissa: o `.docx` protegido por senha, o `.doc` antigo com o nome trocado
  para `.docx`, o arquivo estragado e o vazio (sem texto e sem imagem) dão erro,
  cada um com a sua frase, e voltam à escolha do arquivo.
- premissa: o Word entra só no Anonimizar. O Gerar OCR continua abrindo só PDF.
- premissa: `relatorio.docx` sugere `relatorio - sem CPF.md`, na mesma pasta
  (RN-13), e o `.docx` original nunca é alterado nem apagado (RN-14).
- premissa: num campo automático (número de página, data, mala direta), vai o
  que o Word mostra no documento, e não a fórmula por trás do campo.
- premissa: num link, vai o texto que aparece. O endereço por trás dele não vai:
  ele não aparece na impressão e pode carregar número de pessoa dentro.
- premissa: a descrição escondida da imagem (o "texto alternativo") não vai. A
  imagem conta na faixa.
- premissa: há um tamanho máximo para o Word (RN-30), bem maior que qualquer
  documento de prestação de contas: um pacote pequeno pode esconder um conteúdo
  enorme, feito para travar quem o abre.
- premissa: a massa de teste ganha documentos do Word inventados, gerados por
  script, com uma de cada coisa da RN-24 à RN-28, mais um só de imagem, um
  protegido e um `.doc` renomeado. Os CPFs seguem a RN-22.
- premissa: a tela de escolher passa a dizer "PDF, .docx, .md ou .txt", a janela
  de procurar arquivo mostra o `.docx`, e a frase de "outro tipo" passa a
  listá-lo. Sem o motor de leitura, o `.docx` aparece com ✓ na lista do que dá
  para anonimizar agora: ele não precisa de motor.
- premissa: quebra de página e de seção não deixam marca no `.md`. A lista com
  subitens sai com recuo, um nível por vez, e a lista numerada sai com o número
  (ou a letra) que o Word mostra: `1.`, `a)`, `I.`, `1.1`.
- premissa: o teste que dizia que Word "não entra nesta versão nem nas
  seguintes" passa a usar outro tipo de fora (uma planilha `.xlsx`), e o `.docx`
  ganha os testes dele.
- premissa (*nova*): gráfico, planilha colada, desenho e outros objetos
  colados no documento contam como **imagem** na faixa: o programa não lê o que
  está dentro deles.
- premissa (*nova*): as notas de rodapé vêm primeiro, numeradas de 1 em diante,
  e as notas de fim continuam a numeração. A marca no texto é a do formato de
  nota do `.md` (`[^1]`), e o texto da nota vai no fim do arquivo.
- premissa (*nova*): título é o parágrafo que o Word marca como título (os
  estilos "Título", "Título 1" a "Título 6", ou o nível de tópico do parágrafo).
  Texto só em negrito e maior não vira título.
- premissa (*nova*): quando o CPF sem o zero da frente é o texto mais largo da
  coluna, a compensação da nona emenda não acha espaço sobrando, e aquela linha
  da tabela anda 1 ou 2 posições. A tabela continua tabela para o assistente e
  para o visualizador: só o alinhamento visual daquela linha muda.

## Fluxos

### Fluxo normal — um PDF pelo "Anonimizar"

1. A pessoa clica em "Anonimizar" no menu lateral.
2. O painel mostra a área para escolher o arquivo, dizendo que aceita PDF,
   `.docx`, `.md` e `.txt`. A escolha do motor não aparece aqui.
3. Ela escolhe um PDF.
4. O programa confere o documento. Sem texto por dentro, abre a tela "Este
   documento precisa ser lido", com o nome, as páginas e a escolha do motor
   acima do botão de ler. Com texto por dentro, vai direto para a tela de
   decidir, que já mostra nome, páginas, letras e as primeiras linhas (oitava
   emenda, rascunho 08).
5. O documento segue o caminho da spec 002: a leitura roda com contagem de
   páginas e cancelar, e abre a tela de conferência. A única diferença é o
   motor: quando o PDF vai ser lido como imagem, a escolha dele aparece nessa
   hora, antes de ler, com "Tesseract (nesta máquina)" marcado.
6. Ela confere, corrige o que precisar e clica em "conferido".
7. **O programa vai direto para a revisão.** A escolha entre "salvar o texto
   como está" e "seguir para o Anonimizar" não aparece.
8. O programa procura os CPFs, confere cada um pela conta, mascara todos e abre
   a revisão: o texto mascarado, com cada troca destacada, e a lista de
   suspeitos ao lado.
9. Ela passa o olho no texto e na lista.
10. Ela clica em salvar. O caminho aparece preenchido (a pasta do PDF, o nome
    dele com `- sem CPF.md`) e pode ser trocado.
11. Ela confirma. O arquivo é gravado, e a tela diz onde, lembra que o PDF de
    origem continua na pasta com os CPFs inteiros, e traz o botão de abrir a
    pasta e o de anonimizar outro documento.

### Fluxo alternativo — um `.md` ou `.txt` pelo "Anonimizar"

3a. Ela escolhe um `.md` ou um `.txt`.
3b. O programa lê o arquivo e vai direto para o passo 7. Não há leitura nem
    conferência, porque o texto já existe.
3c. No passo 10, o lembrete fala do `.md` (ou `.txt`) de origem, que continua
    na pasta com os CPFs inteiros.

### Fluxo alternativo — um documento do Word pelo "Anonimizar" (décima emenda)

3a. Ela escolhe um `.docx`, pelo botão ou arrastando.
3b. O programa abre o documento e monta o texto: o cabeçalho no começo, o corpo
    na ordem do documento (títulos, listas, tabelas com barras, caixas de texto
    onde estão presas), o rodapé, e as notas no fim. As alterações controladas
    entram aceitas.
3c. Vai direto para o passo 7, sem leitura nem conferência.
3d. Se o documento tinha comentários, texto oculto, imagens ou alterações
    controladas, a revisão abre com a faixa no alto dizendo o que ficou de fora
    e que as alterações saíram aceitas. Sem nenhum desses, a revisão é a de
    sempre.
3e. No passo 10, o caminho sugerido é a pasta do `.docx` com `- sem CPF.md`, e o
    lembrete fala do `.docx` de origem, que continua na pasta com os CPFs
    inteiros.

### Fluxo alternativo — vindo do "Gerar OCR"

1a. No fim do "Gerar OCR", na escolha da saída, ela clica em "Seguir para
    Anonimizar".
1b. O menu passa a marcar "Anonimizar", e o texto conferido chega à revisão por
    dentro do programa (passo 7), sem arquivo no meio.
1c. O caminho sugerido ao salvar usa a pasta e o nome do PDF que foi lido.
1d. O "Gerar OCR" fica como estava: o texto conferido continua na tela de
    escolher a saída, e voltando pelo menu dá para salvar o texto como está ou
    seguir de novo — e o segundo "Seguir", com a revisão aberta e não salva,
    passa pela pergunta antes de descartar (oitava emenda).

### Caminho torto — um suspeito que não é CPF

Na lista, ela clica em "desfazer" num suspeito que falha na conta. O número
volta a aparecer como estava no texto, e o item continua na lista, marcado como
"liberado", com a opção de mascarar de novo. Nenhuma caixa de confirmação. Se o
suspeito for um "quase CPF" que passa na conta, vale o caminho seguinte.

### Caminho torto — um número que passa na conta, e ela acha que não é CPF

Ela clica em "desfazer" num número que passou na conta, seja do tipo "passa na
conta", seja um "quase CPF" que passa depois de trocadas as letras e juntadas as
partes. Abre uma caixa com o número como está escrito no texto (que é o que iria
para o arquivo) e a explicação de que ele passa na conta do CPF e por isso
quase certamente é um. O botão já escolhido é **"manter a máscara"**: apertar
Enter ou Esc não libera nada. Só clicando em "liberar mesmo assim" o número
volta. Na hora de salvar, se algum número desses foi liberado, o programa lista
quais foram e pergunta de novo: salvar assim, ou voltar à revisão.

### Caminho torto — um CPF que o programa não pegou

Ela vê no texto um número que ficou inteiro. Marca o trecho com o mouse e
escolhe "mascarar". O programa aplica a máscara (premissa da máscara à mão), e o
trecho passa a aparecer destacado, na lista, como "mascarado à mão".

### Caminho torto — um número curto que fecha a conta, e não é CPF

Um telefone com DDD, ou outro número de 10 ou 9 dígitos, fecha a conta por
acaso. Ele aparece mascarado entre os CPFs válidos, com a etiqueta "sem o zero
da frente", e o texto mostra a máscara com os 11 dígitos. Ela o reconhece pela
etiqueta e clica em "desfazer": vale a dupla conferência do caminho anterior, e
a caixa mostra o número como está no documento, com os 10 ou 9 dígitos.
Liberado, ele volta inteiro ao texto, com os espaços de antes (nona emenda).

### Caminho torto — nenhum CPF no texto

A revisão abre normalmente, com o aviso bem visível de "nenhum CPF encontrado
neste texto". A lista de suspeitos fica vazia, e o salvar funciona.

### Caminho torto — ela sai sem salvar

Ela troca de item no menu, escolhe outro arquivo ou fecha a janela com a
revisão aberta e nada salvo. O programa pergunta antes de descartar.

### Caminho torto — o arquivo não serve

Arquivo `.md` ou `.txt` vazio, ou que não é texto de verdade (algo renomeado
para `.md`), dá uma frase dizendo o que houve e volta à escolha do arquivo. PDF
corrompido, protegido por senha ou que não é PDF recebe o mesmo tratamento da
spec 002. O `.docx` protegido por senha, o `.doc` antigo com o nome trocado, o
`.docx` estragado, o vazio e o grande demais recebem cada um a sua frase (RN-30),
e também voltam à escolha. O `.docm`, o `.dotx` e o `.doc` recebem a frase de
"outro tipo".

### Caminho torto — o Word só tem imagens (décima emenda)

Ela escolhe um `.docx` com páginas escaneadas coladas, e nenhum texto. O programa
não abre a revisão: diz que o documento não tem texto, só imagens, e que o
caminho é salvá-lo como PDF pelo Word e escolher o PDF, que o programa lê e ela
confere. Volta à escolha do arquivo. Assim ela nunca chega a uma revisão vazia
dizendo "nenhum CPF encontrado", que se leria como "este documento não tem CPF".

### Caminho torto — já existe arquivo com aquele nome

No passo 10, existindo um `- sem CPF.md` com aquele nome, o programa pergunta
antes: escrever por cima ou salvar com outro nome. Nunca sobrescreve calado.

### Caminho torto — o motor de leitura falta, e ela escolhe um PDF escaneado

Igual ao "Gerar OCR" (spec 002): o aviso no alto já traz as três saídas
("instalar agora", "conferir de novo" e apontar a pasta). Um `.md`, um `.txt` ou
um PDF com camada de texto seguem normalmente. Se, num PDF com camada de texto,
ela escolher ignorar a camada e ler as imagens, vale a tela que o "Gerar OCR" já
tem para esse caso: diz que ler aquele documento como imagem precisa do motor, e
que o texto que já está por dentro dele continua podendo ser aproveitado — sem
dizer que ele "não tem texto por dentro".

### Caminho torto — ela cancela a leitura do PDF

O programa para, descarta o que leu e volta à escolha do arquivo **no
"Anonimizar"**. Nada foi gravado.

## Dados

Não há banco, e nada fica guardado entre um uso e outro. O que existe vive na
memória durante o uso:

| Informação | De onde vem | Obrigatória | Observação |
| --- | --- | --- | --- |
| arquivo de origem | a pessoa (botão ou arrastar), ou o PDF que veio do "Gerar OCR" | sim | PDF, `.docx`, `.md` ou `.txt`. Decide o caminho sugerido para salvar |
| texto de entrada | a conferência do OCR, o conteúdo do `.md`/`.txt`, ou o texto montado do `.docx` (RN-24 a RN-28) | sim | nunca é gravado como está |
| o que ficou de fora do Word | derivado, ao abrir o `.docx` (décima emenda) | não | quantos comentários e quantas imagens (objetos colados inclusive), se havia texto oculto, se havia alterações controladas. Só aparece na faixa da revisão, e nunca vai para o arquivo |
| lista de ocorrências | derivada: busca no texto + ações da pessoa | sim | cada ocorrência tem: **onde** está no texto, **o que estava escrito**, o **tipo** (passa na conta · suspeito: falha na conta · suspeito: quase CPF · mascarado à mão), a **situação** (mascarado · liberado) e, para o quase CPF, se ele **passa na conta** depois de trocadas as letras e juntadas as partes. Na tela, "passa na conta" aparece como **"CPF válido"**, em vermelho (nome encurtado e cor trocada em 16/09/2026, na conferência da construção: entre 14 e 16/09 o rótulo era "forma CPF válido", no mesmo amarelo do suspeito, e na tela de verdade a diferença entre os dois ficou sutil demais). O suspeito fica no amarelo de alerta, e a caixa da dupla conferência continua vermelha: o número que passa na conta é o mais perigoso, e o verde de antes dava a impressão de coisa boa (decidido em 14/09/2026, nos rascunhos de tela 06 e 07). Desde a nona emenda, a ocorrência do tipo "passa na conta" diz também se ele é um **CPF sem o zero da frente** — na tela, a etiqueta "sem o zero da frente" (ou "sem os zeros da frente", com 9 dígitos), em vermelho, ao lado dele na lista |
| texto de saída | derivado | sim | o texto de entrada com a máscara aplicada a toda ocorrência "mascarada". É só isto que vai para o arquivo |
| caminho de destino | sugerido pelo programa, alterável | sim, na hora de salvar | padrão: pasta da origem, nome da origem sem a terminação, mais ` - sem CPF.md` |

O `.env` não é usado neste módulo: não há segredo nenhum aqui.

## Estados da interface

- **vazio:** a área de escolher o arquivo (botão e "arraste aqui"), dizendo que
  aceita PDF, `.docx`, `.md` e `.txt`, sem a escolha do motor. É o estado de
  quando ela clica em "Anonimizar".
- **vazio, com o motor faltando:** o mesmo painel, mais o aviso no alto com as
  três saídas da spec 002. A escolha do arquivo continua funcionando.
- **PDF em andamento:** as telas da spec 002 (conferindo o arquivo, decidindo
  sobre a camada de texto, lendo, conferência), com "Anonimizar" marcado no
  menu. O fim da conferência leva à revisão.
- **procurando os CPFs:** dura um instante. A tela mostra que está trabalhando.
- **revisão, com CPF:** o texto mascarado, cada troca destacada (distinguindo
  o que passa na conta do que é suspeito e do que foi feito à mão), a lista de
  suspeitos ao lado, com o "quase CPF" que passa na conta marcado assim, a
  contagem do que foi mascarado, e o salvar liberado.
- **revisão, sem CPF:** o texto como veio, o aviso bem visível de "nenhum CPF
  encontrado neste texto", a lista vazia, e o salvar liberado.
- **revisão de um Word com algo de fora** (décima emenda): qualquer um dos dois
  estados de revisão acima, mais a faixa no alto, uma linha por aviso, à vista o
  tempo todo e sem botão de fechar (RN-29).
- **abrindo o Word:** dura um instante, como o "procurando os CPFs".
- **dupla conferência:** a caixa com o número como está escrito no texto, a explicação e "manter a
  máscara" já escolhido.
- **salvando:** o caminho preenchido e editável. Havendo número que passa na
  conta liberado, o lembrete dele vem antes de gravar.
- **sucesso:** onde o arquivo foi gravado, o lembrete de que a origem continua
  na pasta com os CPFs inteiros, o botão de abrir a pasta e o de anonimizar
  outro documento.
- **erro:** uma frase dizendo o que houve, em linguagem comum, e o caminho de
  volta.

O desenho de cada um vem no rascunho de tela (`mockups/anonimizar/`), com
aprovação própria, antes da construção.

## Regras de negócio

- RN-1: **Os quatro formatos combinados** são `123.456.789-10`,
  `123456789-10`, `12345678910` e `123.456.789/10`, escritos só com dígitos.
  Número num desses formatos que **passa na conta** é do tipo "passa na conta".
  Número num desses formatos que **falha na conta** é "suspeito: falha na
  conta".
  **O CPF sem o zero da frente** (nona emenda) é o número de **10 ou 9
  dígitos**, só com dígitos, nos mesmos formatos com o grupo da frente mais
  curto: `12.345.678-91`, `12345678-91`, `1234567891` e `12.345.678/91`, ou
  `1.234.567-89`, `1234567-89`, `123456789` e `1.234.567/89`. Posto o zero (ou os
  dois zeros) de volta na frente, se ele **passa na conta**, é do tipo "passa na
  conta", com a marca de CPF sem o zero da frente. Não precisa estar perto da
  palavra "CPF". **Se falha na conta, não é achado**: sem a conta, nada separa o
  CPF curto de um telefone ou de um número de processo. Fica fora também o curto
  com letra no lugar de dígito, com espaço no lugar do ponto ou partido em duas
  linhas: a RN-2 não vale para ele.
- RN-2: **O "quase CPF"** é a sequência com a forma de um CPF (três grupos de
  3 e um de 2, com ou sem separador) em que acontece pelo menos uma destas
  coisas: **até 4 posições** — ou **até 2**, quando não há separador nenhum ou
  só espaços, como manda a premissa das letras — trazem uma letra parecida com
  dígito no lugar dele
  (`O o D Q` por 0, `l I i |` por 1, `Z` por 2, `S s` por 5, `G b` por 6, `T`
  por 7, `B` por 8, `g q` por 9); o separador é um espaço ou uma mistura fora
  dos formatos combinados; ou o número está quebrado entre duas linhas. O
  "quase CPF" é sempre "suspeito: quase CPF", passe ou não na conta. Mas ele
  também é conferido pela conta, depois de trocadas as letras de volta por
  dígitos e juntadas as partes: o que passa leva, na lista, a marca do tipo
  "passa na conta" — na tela, a etiqueta **"válido se corrigido"**, em vermelho, ao lado da etiqueta do "quase CPF" (nome escolhido em 17/09/2026: "CPF válido" é o nome da seção dos que a leitura pegou certinho, e repeti-lo aqui confundia) — e segue a RN-10 e a RN-11 como número que passa na conta. É o CPF de
  verdade que a leitura estragou, e é o que menos pode sair com um clique.
- RN-3: **Número grudado num número maior não é CPF.** Só conta a sequência sem
  dígito colado antes ou depois, nem ligada a outro dígito por ponto, traço ou
  barra. É o que deixa inteiros o CNPJ (`12.345.678/0001-90`), o número de
  processo e a linha de boleto.
- RN-4: **A conta é a do dígito verificador do CPF**, feita pelo próprio
  programa, sem biblioteca de fora. Os dois últimos dígitos são calculados a
  partir dos nove primeiros e comparados com os que estão escritos.
- RN-5: **Tudo o que foi encontrado é mascarado**, inclusive os suspeitos. O erro
  fica do lado seguro: um CPF de verdade lido com um dígito trocado falha na
  conta, e sem máscara sairia quase inteiro.
- RN-6: **A máscara** troca por `X` as 3 primeiras e as 2 últimas posições de
  dígito (ou da letra no lugar dele), e mantém os separadores. A barra antes dos
  dois últimos vira traço (`123.456.789/10` → `XXX.456.789-XX`). Nenhum
  outro caractere muda, e o comprimento do número também não muda.
  **A exceção é o CPF sem o zero da frente** (nona emenda): ele ganha de volta o
  zero (ou os dois zeros) e é mascarado como CPF completo, no mesmo jeito em que
  estava escrito — sem pontuação continua sem, com pontuação continua com:
  `1234567891` → `XXX345678XX`, `123456789` → `XXX234567XX`,
  `12.345.678-91` → `XXX.345.678-XX`, `1.234.567-89` → `XXX.234.567-XX`. Fica à
  vista o mesmo miolo de 6 dígitos de qualquer CPF. Como ele cresce 1 ou 2
  posições, **a coluna da tabela é compensada**: logo depois do número, saem
  tantos espaços quanto ele cresceu, mas sempre sobra pelo menos um. Com um
  espaço só depois dele, ou nenhum, a linha cresce. Só espaço é tirado, e nunca
  duas colunas se juntam.
- RN-7: **A revisão aparece sempre**, com CPF ou sem, e o salvar fica liberado
  desde o começo. O suspeito que ninguém mexeu sai mascarado.
- RN-8: **O texto não é editável na revisão.** As únicas mudanças possíveis são
  mascarar e desfazer máscara. A correção da leitura acontece na conferência do
  OCR.
- RN-9: **Mascarar à mão** vale para o trecho marcado com o mouse, pela regra da
  premissa: esconde as 3 primeiras e as 2 últimas posições do trecho, ou todas
  se forem 5 ou menos. Num trecho que é só um número, a letra parecida com
  dígito conta como posição; num trecho com palavras, contam só os dígitos.
- RN-10: **Desfazer a máscara** de um suspeito que falha na conta ou de uma
  máscara feita à mão é um clique. De **todo número que passa na conta** — do
  tipo "passa na conta", ou "quase CPF" que passa (RN-2) —, pede a dupla
  conferência: a caixa com o número como está escrito no texto, a explicação, e
  **"manter a máscara" como botão já escolhido**, de modo que Enter ou Esc não
  liberam nada.
- RN-11: **Ao salvar**, se algum número que passa na conta foi liberado — do
  tipo "passa na conta", ou "quase CPF" que passa —, o programa mostra quais
  foram antes de gravar, e a pessoa escolhe entre salvar assim ou voltar à
  revisão.
- RN-12: **O arquivo de saída tem o texto e mais nada**, com as máscaras no
  lugar e as tabelas como tabelas. A RN-11 da spec 002 vale aqui: nenhuma linha
  escrita pelo programa entra no arquivo.
- RN-13: **O caminho de destino** aparece preenchido e editável antes de
  gravar: a pasta da origem, o nome da origem sem a terminação, mais
  ` - sem CPF.md`. Existindo arquivo com esse nome, o programa pergunta antes de
  escrever por cima.
- RN-14: **O arquivo de origem nunca é alterado nem apagado**, seja PDF,
  `.docx`, `.md` ou `.txt`. A tela de sucesso lembra, em uma linha, que ele continua na pasta
  com os CPFs inteiros.
- RN-15: **PDF pelo "Anonimizar"** passa pelo caminho inteiro da spec 002, com
  todas as regras dela, **conferência obrigatória inclusive**. No fim da
  conferência vai direto para a revisão, e a saída "salvar o texto como está"
  **não é oferecida** nesse caminho. A escolha do motor é a única coisa que
  muda de lugar: aparece quando o PDF vai ser lido como imagem, e não na
  primeira tela (terceira emenda).
- RN-16: **O botão "Seguir para Anonimizar"** do "Gerar OCR" funciona: leva o
  texto conferido para a revisão por dentro do programa, sem gravar arquivo, e
  marca "Anonimizar" no menu. O "Gerar OCR" **fica como estava**, com o texto
  conferido na tela de escolher a saída (oitava emenda).
- RN-17: **O aviso da tela de salvar do "Gerar OCR"** continua dizendo que o
  arquivo sai com os CPFs inteiros, e deixa de dizer que o Anonimizar "ainda
  vai ser construído": passa a dizer que, para mascarar, o caminho é "Seguir
  para Anonimizar" ou o item "Anonimizar" do menu.
- RN-18: **O módulo de OCR continua sem nada de CPF.** Procurar, conferir e
  mascarar CPF mora só no Anonimizar. O critério da spec 002 que procura CPF no
  código do OCR e não acha nada continua valendo.
- RN-19: **Um arquivo por vez, e nada guardado entre um uso e outro**, nem
  histórico, nem pasta lembrada. Sair da revisão com trabalho não salvo pergunta
  antes de descartar.
- RN-20: **Nenhum código deste módulo fala com a internet** nem com serviço
  nenhum fora da máquina.
- RN-21: **O `.txt` e o `.md` são lidos com os acentos certos** nos dois jeitos
  como o Bloco de Notas do Windows grava texto (o padrão de hoje, e o antigo, de
  quando o Bloco de Notas gravava no padrão do Windows em português). Arquivo
  vazio ou que não é texto dá erro e volta à escolha.
- RN-22: **A massa de teste nunca tem CPF que possa ser de alguém.** Os que
  passam na conta são de dígitos repetidos (`111.111.111-11`,
  `222.222.222-22`…). Os suspeitos e os "quase CPF" partem de números que falham
  na conta, como o `123.456.789-10`, ou de dígitos repetidos.
  **O CPF sem o zero da frente que passa na conta é só de zeros** (nona emenda):
  `0000000000`, `000000000`, `00.000.000-00`, cujo CPF completo é o
  `000.000.000-00`. Nenhum curto de dígitos repetidos fecha a conta, e qualquer
  outro curto que feche é um CPF que pode existir. O formato da máscara com
  outros dígitos é conferido direto na regra que mascara, com números que não
  fecham a conta.
  **O documento do Word da massa** (décima emenda) segue a mesma regra, e é
  gerado por script, como o resto: nenhum documento de verdade, nem como
  modelo.

Da décima emenda — o documento do Word:

- RN-23: **O `.docx` entra no Anonimizar** pelo botão ou arrastando, e vai
  direto para a revisão, sem leitura nem conferência. Só o `.docx`: o `.docm`,
  o `.dotx` e o `.doc` recebem a frase de "outro tipo", que passa a listar o
  `.docx` entre os aceitos. O Word não entra no Gerar OCR. A leitura usa só o
  que vem no próprio Python, nada é instalado nem baixado, e nenhuma macro é
  executada: o programa só lê o texto (RN-20 vale inteira).
- RN-24: **O que vai para o arquivo é o documento impresso**, nesta ordem: o
  cabeçalho; o corpo, na ordem do documento; o rodapé; e as notas. Cabeçalho e
  rodapé aparecem uma vez cada — e, havendo cabeçalhos (ou rodapés) diferentes
  em partes diferentes do documento, cada um diferente aparece uma vez, na
  ordem em que surge. A **caixa de texto** entra no ponto do corpo onde está
  presa, uma vez só. As **notas de rodapé** vão para o fim, numeradas de 1 em
  diante, e as **notas de fim** continuam a numeração; no ponto onde cada uma é
  chamada, o texto leva a marca de nota do `.md` (`[^1]`), e no fim vem
  `[^1]: <texto da nota>`. O programa não escreve rótulo nenhum
  ("Cabeçalho:", "Notas:"): a RN-12 vale inteira.
- RN-25: **O Word como ficaria com tudo aceito.** Nas alterações controladas, o
  trecho inserido entra e o apagado sai. Ficam de fora os **comentários**, o
  **texto oculto**, a **descrição escondida das imagens** e o **endereço por
  trás dos links** (do link, vai o texto que aparece). Num **campo automático**
  vai o que o Word mostra, e não a fórmula. Quebra de página e de seção não
  deixam marca.
- RN-26: **Imagem não vai para o arquivo**, e o programa não lê o que está
  escrito nela. Gráfico, planilha colada, desenho e outros objetos colados
  contam como imagem.
- RN-27: **Tabela do Word vira tabela do `.md`**, com barras e com as colunas
  alinhadas por espaços, e a linha de separação depois da primeira linha:

  ```
  | Nome          | CPF            | Valor       |
  | ------------- | -------------- | ----------- |
  | Fulano de Tal | XXX.111.111-XX | R$ 1.500,00 |
  ```

  A **célula mesclada** põe o texto na primeira posição que ocupa, e as outras
  ficam vazias. Os **parágrafos de uma célula** ficam na mesma linha, separados
  por ` / `, com espaço dos dois lados. A **tabela dentro de outra** vira texto
  corrido na célula dela, do mesmo jeito. A **barra vertical** escrita dentro
  de uma célula sai como `\|`, para não partir a coluna. Cada texto aparece no
  arquivo uma vez só, como no Word.
- RN-28: **Títulos e listas sim, o resto da formatação não.** O parágrafo que o
  Word marca como título ("Título" e "Título 1" a "Título 6", ou o nível de
  tópico) vira título do `.md` (`#` a `######`). A lista com marcador vira
  `- item`; a lista numerada leva o número (ou a letra) que o Word mostra
  (`1.`, `a)`, `I.`, `1.1`); o subitem sai com recuo, um nível por vez. Negrito,
  itálico, sublinhado, cor e fonte ficam de fora.
- RN-29: **A faixa do que ficou de fora.** Abrindo um `.docx` que tinha
  comentários, texto oculto, imagens ou alterações controladas, a revisão
  mostra uma faixa no alto, à vista o tempo todo, sem botão de fechar, com uma
  linha por aviso. A primeira junta o que ficou fora do arquivo, só com o que o
  documento tinha: "Ficou fora do arquivo: 3 comentários · texto oculto · 2
  imagens (o programa não lê o que está escrito nelas)." (com 1, no singular:
  "1 comentário", "1 imagem"). A segunda aparece só havendo alterações
  controladas: "As alterações controladas saíram aceitas, como o documento
  ficaria no fim." Nada disso vai para o arquivo. O `.docx` sem nenhum desses
  casos abre a revisão sem faixa. O desenho dela vem no rascunho de tela.
- RN-30: **O Word que não abre** dá uma frase e volta à escolha do arquivo,
  sem travar:
  - **protegido por senha:** "O {nome} está protegido por senha. Abra no Word,
    tire a senha e salve de novo, e escolha o arquivo outra vez.";
  - **`.doc` antigo com o nome trocado:** "O {nome} é um documento do Word
    antigo (.doc) com o nome de .docx. Abra no Word e salve como .docx.";
  - **estragado** (não é um pacote do Word, ou falta a parte do corpo): "O
    {nome} não pôde ser lido como documento do Word: ele pode estar estragado
    ou ser outro tipo de arquivo com o nome trocado.";
  - **vazio**, sem texto e sem imagem: "O {nome} está vazio: não há texto
    nele.";
  - **só imagens**, sem texto e com ao menos uma imagem: "O {nome} não tem
    texto, só imagens. Salve-o como PDF pelo Word e escolha o PDF: o programa lê
    as imagens e você confere.";
  - **grande demais:** as partes de texto do pacote, descompactadas, passam de
    **50 MB**. O texto de um documento comum, mesmo de centenas de páginas,
    fica muito abaixo disso; o limite é conferido antes de descompactar, porque um pacote
    pequeno pode esconder um conteúdo enorme, feito para travar quem o abre.
    As imagens não contam, porque não são descompactadas. A frase: "O {nome} é
    grande demais para o programa abrir com segurança."

  As frases são a proposta; o texto final sai no rascunho de tela.

## Critérios de aceite

**Encontrar e conferir**

- Dado um texto com `111.111.111-11`, `11111111111`, `111111111-11` e
  `111.111.111/11`, quando ele passa pelo Anonimizar, então os quatro aparecem
  mascarados e marcados como "CPF válido" (o nome na tela do tipo "passa na
  conta"), e nenhum está na lista de suspeitos.
- Dado um texto com `123.456.789-10`, quando ele passa pelo Anonimizar, então o
  número aparece mascarado **e** está na lista de suspeitos, como "falha na
  conta".
- Dado um texto com `l23.456.789-1O`, com `123 456 789 10` e com
  `123.456.` no fim de uma linha e `789-10` no começo da seguinte, quando ele
  passa pelo Anonimizar, então os três aparecem mascarados e na lista, como
  "quase CPF".
- Dado um texto com `l23.4S6.789-1O`, com três letras e a pontuação de um CPF,
  quando ele passa pelo Anonimizar, então ele aparece mascarado como
  `XXX.4S6.789-XX` e está na lista, como "quase CPF".
- Dado um texto com `l234S67891O`, com as mesmas três letras e **sem separador
  nenhum**, quando ele passa pelo Anonimizar, então ele não é mascarado.
- Dado um texto com um número de 9 dígitos no fim de uma linha e "Situação:" no
  começo da seguinte, quando ele passa pelo Anonimizar, então nada é mascarado
  ali. Dado `123.456.` no fim de uma linha e `789-1O,` na seguinte, então ele
  continua mascarado, como "quase CPF". Dado `111.111.111-1lAssinado`, com
  pontuação de CPF e a letra final grudada na palavra, então ele **também**
  continua mascarado, e pede a dupla conferência para ser liberado (quinta
  emenda, com a ressalva da revisão da etapa 3).
- Dado um texto com uma sequência pontuada em que 5 posições são letras
  (`SOL.IDA.DES-OS`), quando ele passa pelo Anonimizar, então ela não é
  mascarada.
- Dado um texto com o CNPJ `12.345.678/0001-90`, um número de processo com mais
  de 11 dígitos e uma linha digitável de boleto, quando ele passa pelo
  Anonimizar, então os três saem inteiros.
- Dado um texto com `111.111.111-11` colado a outro dígito (`9111.111.111-11`),
  quando ele passa pelo Anonimizar, então nada é mascarado ali.
- Dado um arquivo que já foi anonimizado, quando ele é aberto no Anonimizar,
  então a revisão diz "nenhum CPF encontrado".

**Máscara**

- Dado `111.111.111-11`, então ele vira `XXX.111.111-XX`. Dado `11111111111`,
  então ele vira `XXX111111XX`. Dado `111.111.111/11`, então ele vira
  `XXX.111.111-XX`.
- Dado `l23.456.789-1O`, então ele vira `XXX.456.789-XX`.
- Dado um CPF quebrado entre duas linhas, então as duas partes aparecem
  mascaradas e a quebra de linha continua no mesmo lugar.
- Dado um documento com um CPF dentro de uma tabela, quando o arquivo é salvo,
  então a tabela continua com as colunas no lugar.

**CPF sem o zero da frente (nona emenda)**

- Dado um texto com `0000000000`, `00.000.000-00`, `00000000-00` e
  `00.000.000/00`, quando ele passa pelo Anonimizar, então os quatro aparecem
  mascarados entre os "CPF válido", com a etiqueta "sem o zero da frente", e
  nenhum está na lista de suspeitos.
- Dado um texto com `000000000` e `0.000.000-00`, quando ele passa pelo
  Anonimizar, então os dois aparecem mascarados entre os "CPF válido", com a
  etiqueta "sem os zeros da frente".
- Dado `0000000000`, então ele vira `XXX000000XX`. Dado `00.000.000-00`, então
  ele vira `XXX.000.000-XX`. Dado `00.000.000/00`, então ele vira
  `XXX.000.000-XX`. Dado `000000000`, então ele vira `XXX000000XX`.
- Dada a regra que mascara o curto, aplicada direto, sem a busca, a
  `1234567891`, `123456789`, `12.345.678-91`, `12345678-91` e `1.234.567-89`
  (números que não fecham a conta), então eles viram `XXX345678XX`,
  `XXX234567XX`, `XXX.345.678-XX`, `XXX345678-XX` e `XXX.234.567-XX`.
- Dado um texto com `1234567891` e `123456789`, que não fecham a conta com os
  zeros de volta, quando ele passa pelo Anonimizar, então os dois saem inteiros
  e fora da lista.
- Dado um texto com `0000O00000` (letra no lugar de um dígito), com
  `00 000 000 00` e com `00.000.` no fim de uma linha e `000-00` no começo da
  seguinte, quando ele passa pelo Anonimizar, então nada é mascarado ali.
- Dado `CPF0000000000`, com o número grudado na palavra, então ele aparece
  mascarado como `CPFXXX000000XX`: a letra antes do número não o impede de
  contar, como no CPF completo (quinta emenda).
- Dado um texto com `0000000000/2026` e com `00.000.000/0000-00`, na forma de
  um CNPJ, quando ele passa pelo Anonimizar, então os dois saem inteiros.
- Dado um texto com `00000000`, de 8 dígitos, então ele sai inteiro.
- Dada a linha de tabela `| 0000000000     | R$ 1.500,00 |`, quando o arquivo é
  salvo, então ela vira `| XXX000000XX    | R$ 1.500,00 |`, do mesmo tamanho.
  Dada a linha `0000000000 R$ 10,00`, com um espaço só depois do número, então
  ela vira `XXX000000XX R$ 10,00`, uma posição maior.
- Dado `0000000000` mascarado na revisão, quando a pessoa clica em "desfazer",
  então abre a dupla conferência com `0000000000` escrito na caixa, e **apertar
  Enter mantém a máscara**. Liberado, o texto volta a ser exatamente o que era,
  com os espaços de depois dele; mascarado de novo, volta a ser `XXX000000XX`.
- Dado que a pessoa liberou um CPF sem o zero da frente, quando ela clica em
  salvar, então o programa mostra esse número antes de gravar e deixa voltar à
  revisão.
- Dado um texto com `0000000000` e `111.111.111-11`, quando a revisão abre, então
  o selo "CPFs válidos" conta 2.
- Dado `dados-exemplo/`, quando se procura por número de 10 ou 9 dígitos que,
  com os zeros de volta, passa na conta, então só aparecem os feitos de zeros.
- Dados todos os critérios das seções anteriores, então eles continuam passando
  depois desta emenda.
- Dado um texto com vários números na revisão, quando a pessoa clica no
  terceiro, no texto, então o item dele acende na lista, a lista rola até ele, a
  posição mostra "3 de N", e o botão "Mascarar o trecho marcado" não acende
  (acréscimo de 22/10/2026).
- Dado que a pessoa liberou só CPFs sem o zero da frente, quando ela clica em
  salvar, então o aviso diz "Eles podem ser o CPF de alguém." e cada um leva a
  etiqueta "sem o zero da frente". Liberados um CPF completo e um curto, então a
  frase é "Os válidos quase certamente são o CPF de alguém e os sem o zero da
  frente podem ser CPF ou outro dado, como um telefone." Liberado só CPF
  completo, a frase fica como antes. Na caixa da dupla conferência do curto, a
  frase diz "pode ser o CPF de alguém" (acréscimo de 22/10/2026).

**Documento do Word (décima emenda)**

- Dado um `.docx` com `111.111.111-11` no corpo, quando a pessoa o escolhe no
  "Anonimizar" (pelo botão ou arrastando), então a revisão abre sem passar por
  leitura nem conferência, com o número mascarado entre os "CPF válido".
- Dado um `.docx` com um CPF no cabeçalho, outro no rodapé, outro numa nota de
  rodapé, outro numa nota de fim e outro numa caixa de texto, quando a revisão
  abre, então os cinco estão mascarados; o cabeçalho é a primeira linha do
  texto, o rodapé vem depois do corpo, as notas vêm no fim como `[^1]: …` e
  `[^2]: …`, com `[^1]` e `[^2]` no ponto onde são chamadas, e o texto da caixa
  aparece uma vez só.
- Dado um `.docx` com o mesmo cabeçalho em três seções e um cabeçalho diferente
  na quarta, então o texto traz os dois cabeçalhos, uma vez cada.
- Dado um `.docx` com uma alteração controlada que inseriu `111.111.111-11` e
  outra que apagou `222.222.222-22`, quando a revisão abre, então o primeiro
  está no texto, mascarado, e o segundo não aparece em lugar nenhum — nem no
  texto, nem na lista.
- Dado um `.docx` com `333.333.333-33` num comentário e `444.444.444-44` em
  texto oculto, então nenhum dos dois aparece no texto nem na lista, e a faixa
  diz "1 comentário · texto oculto".
- Dado um `.docx` com um link cujo texto é "sistema" e cujo endereço termina em
  `555.555.555-55`, então o texto traz "sistema", e o número não aparece.
- Dado um `.docx` com uma tabela de 3 colunas, quando a revisão abre, então ela
  aparece com barras, as colunas alinhadas e a linha de separação depois da
  primeira linha; e salvo o arquivo, a tabela continua assim.
- Dado um `.docx` com uma célula mesclada em duas colunas, uma célula com dois
  parágrafos e uma tabela dentro de uma célula, então o texto da mesclada
  aparece uma vez, na primeira posição; os dois parágrafos aparecem na mesma
  célula, separados por ` / `; e o texto da tabela de dentro aparece na célula
  dela, sem partir a tabela de fora.
- Dado um `.docx` com `111.111.111-11` sozinho numa célula, então ele é achado e
  mascarado como em qualquer texto. Dado `0000000000` sozinho numa célula,
  então ele é achado como CPF sem o zero da frente.
- Dado um `.docx` com uma célula que tem `a | b` escrito, então a tabela continua
  com o mesmo número de colunas, e a célula traz `a \| b`.
- Dado um `.docx` com "Título 1", "Título 2", uma lista com marcador, uma lista
  numerada com subitens e um trecho em negrito, então o texto traz `#` e `##`,
  `- `, os números como o Word mostra, o subitem com recuo, e o trecho em negrito
  sem asterisco nenhum.
- Dado um `.docx` com duas imagens e um gráfico, então o texto não traz nada
  delas, nem a descrição escondida, e a faixa diz "3 imagens (o programa não lê
  o que está escrito nelas)".
- Dado um `.docx` com alteração controlada, então a faixa traz a linha "As
  alterações controladas saíram aceitas, como o documento ficaria no fim."
- Dado um `.docx` sem comentário, texto oculto, imagem nem alteração
  controlada, então a revisão abre sem faixa.
- Dado um `.docx` com um campo de número de página mostrando "Página 1 de 3",
  então o texto traz "Página 1 de 3", e não a fórmula do campo.
- Dado um `.docx` só com imagens, quando ele é escolhido, então a revisão não
  abre: aparece a frase de que ele não tem texto, só imagens, com o caminho do
  PDF, e a volta à escolha do arquivo.
- Dado um `.docx` protegido por senha, um `.doc` renomeado para `.docx`, um
  arquivo qualquer renomeado para `.docx` e um `.docx` vazio, quando cada um é
  escolhido, então aparece a frase dele (RN-30) e a volta à escolha, sem travar.
- Dado um `.docx` cujas partes de texto, descompactadas, passam de 50 MB,
  então ele é recusado com a frase de grande demais, sem que o programa
  descompacte o conteúdo.
- Dado um `.docm`, um `.dotx` e um `.doc`, quando cada um é escolhido, então
  aparece a frase de "outro tipo", que cita o `.docx` entre os aceitos. Dada uma
  planilha `.xlsx`, então a frase é a mesma, e não promete etapa seguinte.
- Dado `relatorio.docx`, quando a pessoa chega a salvar, então o caminho
  sugerido é a pasta dele com `relatorio - sem CPF.md`; e o `relatorio.docx`,
  comparado antes e depois, está idêntico.
- Dado que o arquivo foi gravado a partir de um `.docx`, quando ele é aberto,
  então não tem nenhuma linha escrita pelo programa — nem a faixa, nem rótulo
  de cabeçalho ou de notas.
- Dado que o motor de leitura não está instalado, quando a pessoa abre o
  "Anonimizar", então a lista do que dá para anonimizar agora traz o `.docx`
  com ✓, e um `.docx` escolhido abre a revisão normalmente.
- Dada a tela de escolher do "Anonimizar", então ela diz "PDF, .docx, .md ou
  .txt", e a janela de procurar arquivo mostra os `.docx`.
- Dado o "Gerar OCR", então ele continua aceitando só PDF.
- Dado o código que lê o Word, quando se procura por biblioteca de fora do
  Python, endereço de internet ou execução de macro, então não há nenhum; e o
  `requirements.txt` não ganhou linha nova.
- Dado `dados-exemplo/`, quando se procura nos documentos do Word por número de
  11 dígitos que passa na conta, então só aparecem números de dígitos
  repetidos (RN-22).

**Revisão**

- Dado um texto com CPFs, quando a revisão abre, então o texto aparece
  mascarado, cada troca aparece destacada, a lista de suspeitos está ao lado, e
  o salvar está liberado.
- Dado um texto sem CPF, quando a revisão abre, então aparece o aviso "nenhum
  CPF encontrado neste texto" e o salvar está liberado.
- Dado que a pessoa tenta digitar dentro do texto da revisão, então nada muda.
- Dado um suspeito na lista, quando a pessoa clica nele, então o texto rola até
  ele.
- Dado um texto com CPFs, quando a pessoa clica em "próximo", então o texto vai
  até o número seguinte na ordem do texto, o item dele se marca na lista e a
  posição "N de M" avança. A navegação dá a volta: do último número, o "próximo"
  leva ao primeiro, e do primeiro, o "anterior" leva ao último. Clicar num item
  da lista também acerta a posição. M
  conta todos os números da lista, liberados inclusive. Sem nenhum CPF, a
  navegação não aparece.
- Dado que a pessoa clica no selo "CPFs válidos" (ou "suspeitos", ou "liberados
  por você"), então o selo fica aceso, o texto vai direto ao primeiro número
  daquele grupo ("1 de 3 CPFs válidos"), e o "anterior" e o "próximo" pulam só
  entre os números do grupo, sem esconder nada do texto nem da lista. Clicar no
  "números encontrados" leva ao primeiro número de todos. Clicar de novo no selo
  aceso desliga o filtro sem sair do número em que a pessoa está. O que sai do grupo no
  meio da navegação sai da contagem, e o "próximo" segue a partir dele.
- Dado um texto com CPFs, então os selos do alto contam grupos separados, e a
  soma fecha: "N números encontrados" fica fixo; "CPFs válidos" e "suspeitos"
  contam só o que continua mascarado; "liberados por você" conta o que foi
  liberado. Liberar um suspeito tira um de "suspeitos" e põe um em "liberados";
  mascarar de novo desfaz isso. A navegação pelos suspeitos não passa pelos
  liberados, e o título da seção da lista acompanha o selo ("Suspeitos — olhe
  estes 7"), com o item liberado continuando no mesmo lugar da lista.
- Dado um suspeito que falha na conta, quando a pessoa clica em "desfazer",
  então o número volta ao original no texto, sem caixa de confirmação, e
  continua na lista como "liberado", com a opção de mascarar de novo.
- Dado um número do tipo "passa na conta", quando a pessoa clica em "desfazer",
  então abre a caixa com o número como está escrito no texto, e **apertar Enter
  mantém a máscara**.
- Dado `l11.111.111-11` e dado `555.555.` no fim de uma linha com `555-55` no
  começo da seguinte ("quase CPF" que passa na conta), quando a revisão abre,
  então os dois estão na lista de suspeitos com a etiqueta "válido se
  corrigido" ao lado da etiqueta de "quase CPF" (nome escolhido em 17/09/2026); e
  quando a pessoa clica em "desfazer" num deles, então abre a caixa da dupla
  conferência, e **apertar Enter mantém a máscara**.
- Dado que a pessoa liberou um número que passa na conta — do tipo "passa na
  conta", ou "quase CPF" que passa —, quando ela clica em salvar, então o
  programa mostra esse número antes de gravar e deixa voltar à revisão.
- Dado o trecho `1234 5678 910`, que não tem forma de CPF e por isso o programa
  não pega, quando ela o marca com o mouse e escolhe "mascarar", então ele vira
  `XXX4 5678 9XX` e aparece na lista como "mascarado à mão".
- Dado o trecho `l23.4S6.789-1O`, um número que a leitura estragou demais para o
  programa pegar, quando ela o marca e escolhe "mascarar", então ele vira
  `XXX.4S6.789-XX` — a letra conta como posição. Dado um trecho que traz
  palavras junto, então contam só os dígitos (sexta emenda).
- Dado um trecho marcado sem nenhum dígito, quando ela escolhe "mascarar",
  então nada muda, e a tela diz por quê.

**Entradas**

- Dado um PDF sem camada de texto, quando a pessoa o escolhe no "Anonimizar",
  então ele passa pela leitura e pela conferência, e depois de "conferido" vai
  **direto para a revisão**, sem aparecer a opção "salvar o texto como está".
- Dado um PDF sem texto por dentro escolhido no "Anonimizar", então antes de
  qualquer leitura aparece a tela "Este documento precisa ser lido", com o nome,
  o número de páginas e a escolha do motor acima do botão de ler. Dado um PDF com
  texto por dentro, então a tela seguinte é a de decidir sobre o texto, sem
  nenhuma tela no meio (oitava emenda, rascunho 08).
- Dado um `.md` e um `.txt`, quando a pessoa escolhe um deles no "Anonimizar",
  então a revisão abre sem passar por leitura nem conferência.
- Dado um `.txt` com acentos, gravado nos dois jeitos do Bloco de Notas, quando
  ele é aberto, então os acentos aparecem certos nos dois casos.
- Dado um `.md` vazio, ou um arquivo que não é texto renomeado para `.md`,
  quando ele é escolhido, então o programa explica em uma frase e volta à
  escolha do arquivo, sem travar.
- Dado que a pessoa está na escolha da saída do "Gerar OCR", quando ela clica em
  "Seguir para Anonimizar", então o menu passa a marcar "Anonimizar" e a
  revisão abre com o texto conferido, sem que nenhum arquivo tenha sido gravado.
- Dado que ela seguiu para o Anonimizar, quando volta ao "Gerar OCR" pelo menu,
  então — com a revisão aberta e não salva — aparece primeiro a pergunta antes
  de descartar, e, descartada a revisão, o texto conferido continua lá, na
  escolha da saída, com o salvar e o seguir de novo funcionando (oitava emenda).
  Vale também o contrário: salva a revisão, a volta é direta.
- Dado que a pessoa está lendo um PDF pelo "Anonimizar", então o item marcado no
  menu é "Anonimizar".
- Dado que a pessoa cancela a leitura de um PDF pelo "Anonimizar", então ela
  volta à escolha do arquivo do "Anonimizar", e nada foi gravado.
- Dado que o Tesseract não está instalado, quando a pessoa abre o "Anonimizar",
  então o aviso aparece com as três saídas, e um `.md` escolhido abre a revisão
  normalmente.
- Dado que a pessoa abre o "Anonimizar", então a tela de escolher o arquivo não
  mostra a escolha do motor. Dado um PDF sem camada de texto, ou um PDF com
  camada em que a pessoa escolhe ler as imagens, então a escolha do motor
  aparece antes da leitura, com "Tesseract (nesta máquina)" marcado. Dado um
  `.md`, um `.txt` ou um PDF cuja camada de texto é aproveitada, então a escolha
  do motor não aparece em momento nenhum.

**Salvar**

- Dado um PDF `relatorio.pdf`, quando a pessoa chega a salvar, então o caminho
  sugerido é a pasta dele com `relatorio - sem CPF.md`, e dá para trocar.
- Dado que já existe `relatorio - sem CPF.md` na pasta, quando ela confirma,
  então o programa pergunta antes de escrever por cima.
- Dado que o arquivo foi gravado, quando ele é aberto, então ele tem o texto com
  as máscaras e **nenhuma linha escrita pelo programa**.
- Dado que o arquivo foi gravado, quando se procura nele qualquer um dos CPFs
  que estavam no texto de entrada e continuaram mascarados, então nenhum aparece
  inteiro.
- Dado que o arquivo foi gravado, então a tela de sucesso diz onde gravou,
  lembra que a origem continua na pasta com os CPFs inteiros, e traz o botão de
  abrir a pasta.
- Dado o arquivo de origem comparado antes e depois de todo o processo, então
  ele está idêntico e continua no lugar.
- Dado que a revisão está aberta e nada foi salvo, quando a pessoa clica em
  "Gerar OCR" no menu, então o programa pergunta antes de descartar.

**Fronteiras**

- Dado o "Gerar OCR", quando a pessoa chega à tela de salvar o texto como está,
  então o aviso diz que o arquivo sai com os CPFs inteiros e aponta para o
  Anonimizar, sem dizer que ele "ainda vai ser construído".
- Dado o código do módulo de OCR, quando se procura por conta de dígito
  verificador, máscara ou lista de CPF, então não há nenhuma (o critério da spec
  002 continua passando).
- Dado o código deste módulo inteiro, quando se procura por endereço de
  internet ou chamada a serviço remoto, então não há nenhum.
- Dado `dados-exemplo/`, quando se procura por número de 11 dígitos que passa
  na conta, então só aparecem números de dígitos repetidos.
- Dado que a pessoa fecha e reabre o programa, quando ela volta ao
  "Anonimizar", então a tela está no estado inicial, sem nada lembrado.

## Questões em aberto

Nenhuma. O desenho das telas não é questão da spec: vem no rascunho de tela,
com aprovação própria, antes da construção.

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
para a conversa com o assistente de IA, partindo de um PDF, de um `.md` ou
`.txt` que já existe, ou do texto que ela acabou de conferir no "Gerar OCR". É o
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
- **Acender o botão "Seguir para Anonimizar"** no fim do "Gerar OCR", que leva o
  texto conferido para a revisão por dentro do programa, sem passar por arquivo.
- Encontrar CPF nos quatro formatos combinados e também o **"quase CPF"**: o
  número que o OCR estragou trocando dígito por letra, trocando a pontuação por
  espaço ou quebrando entre duas linhas.
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
  do número não muda, e a tabela de texto continua alinhada.
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

## Fluxos

### Fluxo normal — um PDF pelo "Anonimizar"

1. A pessoa clica em "Anonimizar" no menu lateral.
2. O painel mostra a área para escolher o arquivo, dizendo que aceita PDF,
   `.md` e `.txt`. A escolha do motor não aparece aqui.
3. Ela escolhe um PDF.
4. O documento segue o caminho da spec 002: o programa confere se há camada de
   texto, a pessoa decide sobre ela quando há, a leitura roda com contagem de
   páginas e cancelar, e abre a tela de conferência. A única diferença é o
   motor: quando o PDF vai ser lido como imagem, a escolha dele aparece nessa
   hora, antes de ler, com "Tesseract (nesta máquina)" marcado.
5. Ela confere, corrige o que precisar e clica em "conferido".
6. **O programa vai direto para a revisão.** A escolha entre "salvar o texto
   como está" e "seguir para o Anonimizar" não aparece.
7. O programa procura os CPFs, confere cada um pela conta, mascara todos e abre
   a revisão: o texto mascarado, com cada troca destacada, e a lista de
   suspeitos ao lado.
8. Ela passa o olho no texto e na lista.
9. Ela clica em salvar. O caminho aparece preenchido (a pasta do PDF, o nome
   dele com `- sem CPF.md`) e pode ser trocado.
10. Ela confirma. O arquivo é gravado, e a tela diz onde, lembra que o PDF de
    origem continua na pasta com os CPFs inteiros, e traz o botão de abrir a
    pasta e o de anonimizar outro documento.

### Fluxo alternativo — um `.md` ou `.txt` pelo "Anonimizar"

3a. Ela escolhe um `.md` ou um `.txt`.
3b. O programa lê o arquivo e vai direto para o passo 7. Não há leitura nem
    conferência, porque o texto já existe.
3c. No passo 10, o lembrete fala do `.md` (ou `.txt`) de origem, que continua
    na pasta com os CPFs inteiros.

### Fluxo alternativo — vindo do "Gerar OCR"

1a. No fim do "Gerar OCR", na escolha da saída, ela clica em "Seguir para
    Anonimizar".
1b. O menu passa a marcar "Anonimizar", e o texto conferido chega à revisão por
    dentro do programa (passo 7), sem arquivo no meio.
1c. O caminho sugerido no passo 9 usa a pasta e o nome do PDF que foi lido.

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
spec 002.

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
| arquivo de origem | a pessoa (botão ou arrastar), ou o PDF que veio do "Gerar OCR" | sim | PDF, `.md` ou `.txt`. Decide o caminho sugerido para salvar |
| texto de entrada | a conferência do OCR, ou o conteúdo do `.md`/`.txt` | sim | nunca é gravado como está |
| lista de ocorrências | derivada: busca no texto + ações da pessoa | sim | cada ocorrência tem: **onde** está no texto, **o que estava escrito**, o **tipo** (passa na conta · suspeito: falha na conta · suspeito: quase CPF · mascarado à mão), a **situação** (mascarado · liberado) e, para o quase CPF, se ele **passa na conta** depois de trocadas as letras e juntadas as partes. Na tela, "passa na conta" aparece como **"CPF válido"**, em vermelho (nome encurtado e cor trocada em 16/09/2026, na conferência da construção: entre 14 e 16/09 o rótulo era "forma CPF válido", no mesmo amarelo do suspeito, e na tela de verdade a diferença entre os dois ficou sutil demais). O suspeito fica no amarelo de alerta, e a caixa da dupla conferência continua vermelha: o número que passa na conta é o mais perigoso, e o verde de antes dava a impressão de coisa boa (decidido em 14/09/2026, nos rascunhos de tela 06 e 07) |
| texto de saída | derivado | sim | o texto de entrada com a máscara aplicada a toda ocorrência "mascarada". É só isto que vai para o arquivo |
| caminho de destino | sugerido pelo programa, alterável | sim, na hora de salvar | padrão: pasta da origem, nome da origem sem a terminação, mais ` - sem CPF.md` |

O `.env` não é usado neste módulo: não há segredo nenhum aqui.

## Estados da interface

- **vazio:** a área de escolher o arquivo (botão e "arraste aqui"), dizendo que
  aceita PDF, `.md` e `.txt`, sem a escolha do motor. É o estado de quando ela
  clica em "Anonimizar".
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
- RN-14: **O arquivo de origem nunca é alterado nem apagado**, seja PDF, `.md`
  ou `.txt`. A tela de sucesso lembra, em uma linha, que ele continua na pasta
  com os CPFs inteiros.
- RN-15: **PDF pelo "Anonimizar"** passa pelo caminho inteiro da spec 002, com
  todas as regras dela, **conferência obrigatória inclusive**. No fim da
  conferência vai direto para a revisão, e a saída "salvar o texto como está"
  **não é oferecida** nesse caminho. A escolha do motor é a única coisa que
  muda de lugar: aparece quando o PDF vai ser lido como imagem, e não na
  primeira tela (terceira emenda).
- RN-16: **O botão "Seguir para Anonimizar"** do "Gerar OCR" funciona: leva o
  texto conferido para a revisão por dentro do programa, sem gravar arquivo, e
  marca "Anonimizar" no menu.
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

## Critérios de aceite

**Encontrar e conferir**

- Dado um texto com `111.111.111-11`, `11111111111`, `111111111-11` e
  `111.111.111/11`, quando ele passa pelo Anonimizar, então os quatro aparecem
  mascarados e marcados como "forma CPF válido" (o nome na tela do tipo "passa
  na conta"), e nenhum está na lista de
  suspeitos.
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
  então os dois estão na lista de suspeitos com a marca "forma CPF válido"; e
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

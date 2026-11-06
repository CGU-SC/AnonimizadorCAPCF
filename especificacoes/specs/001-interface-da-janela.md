# Spec 001 — Interface da janela

**Status:** implementada
**Data:** 2026-09-04
**Emendada em:** 2026-10-28 (aprovada no mesmo dia) — a janela abre maximizada no
primeiro uso e depois lembra o tamanho e se estava maximizada (funcionalidade 8
do backlog, pedido da usuária no levantamento). Está na seção "Emenda de
28/10/2026", no fim; o fora de escopo e o último critério trazem a remissão. O
motor lembrado, da mesma funcionalidade, está na emenda de mesma data da spec
002.
**Emendada em:** 2026-10-31, pela spec 004 (aprovada no mesmo dia) — o menu ganha
"Configurações de IA", no fim da faixa, que troca o menu inteiro por um submenu
(RN-1 a RN-3 da spec 004). Dentro do submenu, a RN-2 daqui vale igual.
**Emendada em:** 2026-11-03 (aprovada em 04/11/2026) — a faixa da
esquerda redesenhada: cabeçalho com símbolo e a versão junto do nome, ícones em
traço nos três itens do menu e o item marcado suave (funcionalidade 9 do
backlog). Está na seção "Emenda de 03/11/2026", no fim. O acréscimo de
04/11/2026, dentro dela, leva o ícone do módulo ao título do painel
(aprovado no mesmo dia).
**Emendada em:** 2026-11-05 (aprovada no mesmo dia) — o tema claro ao lado do escuro, e
"Configurações de IA" vira "Configurações", com o Tema e a IA dentro
(funcionalidade 10 do backlog). Está na seção "Emenda de 05/11/2026", no fim; o
fora de escopo e a emenda de 03/11/2026 trazem a remissão. O tema lembrado está
na emenda de mesma data da spec 002, e o nome do menu na da spec 004.

## Objetivo
Dar ao programa uma janela própria, com a estrutura onde os dois módulos futuros
(Gerar OCR e Anonimizar) vão aparecer: um menu lateral para escolher qual
rodar, e um painel principal que muda de acordo com a escolha.

## Escopo
- Janela própria (PySide6), abre como aplicativo de mesa.
- Menu lateral fixo, com duas opções: "Gerar OCR" e "Anonimizar".
- Painel principal que muda de conteúdo conforme a opção escolhida no menu.
- Ao abrir, sem nada escolhido ainda, o painel mostra uma mensagem convidando a
  escolher um módulo.
- Escolhido um módulo — nesta primeira versão, tanto "Gerar OCR" quanto
  "Anonimizar" — o painel mostra um aviso de que aquele módulo ainda não foi
  construído. É o lugar onde o conteúdo de verdade entra quando as specs 002 e
  003 forem construídas.
- Nome do programa na janela.

## Fora de escopo
- O funcionamento real de "Gerar OCR" — spec própria, item 2 do backlog.
- O funcionamento real de "Anonimizar" — spec própria, item 3 do backlog.
- Qualquer processamento de documento.
- Redimensionar janela, temas, atalhos de teclado — nada disso foi pedido.
  *(Emendado em 28/10/2026: o tamanho da janela passa a ser lembrado — veja a
  emenda, no fim. A posição dela continua não lembrada. E, desde a emenda de
  05/11/2026, há um tema claro, escolhido pela pessoa.)*
- Ícone próprio da janela — decidido em 04/09/2026, ao fechar a funcionalidade:
  depende de alguém escolher ou desenhar a imagem, o que é decisão de
  identidade visual e não de código. Até lá a janela usa o ícone padrão.

## Premissas
- premissa: as máquinas do núcleo onde o programa roda são Windows.

## Fluxos

**Fluxo normal — abrir e navegar entre os módulos:**
1. A pessoa abre o programa.
2. A janela aparece, com o menu lateral (Gerar OCR / Anonimizar) e o painel
   principal mostrando a mensagem de boas-vindas.
3. A pessoa clica em "Gerar OCR" ou em "Anonimizar", no menu.
4. O painel principal troca para o conteúdo daquele módulo — nesta versão, o
   aviso de que o módulo ainda não foi construído.
5. A pessoa pode clicar no outro item do menu a qualquer momento, e o painel
   troca de novo.

**Caminho torto — clicar no que já está selecionado:**
A pessoa clica no item do menu que já está marcado. O item deixa de ficar
marcado e o painel volta para a mensagem de boas-vindas — o mesmo estado de
quando o programa abre.

## Dados
Não há dado persistido nesta funcionalidade — é só estrutura de tela. Nenhum
campo, nenhuma gravação, nenhuma leitura de arquivo.

## Estados da interface
- **vazio:** menu lateral visível, nenhum item marcado; painel com a mensagem
  convidando a escolher "Gerar OCR" ou "Anonimizar". É o estado de quando o
  programa abre, e o estado para onde se volta ao clicar no item já marcado.
- **com módulo selecionado:** menu lateral visível, com o item escolhido
  marcado; painel com o aviso de "este módulo ainda não foi construído".
- **carregando:** não se aplica — abrir a janela e trocar o painel é
  instantâneo, sem espera.
- **erro:** não se aplica — não há operação nesta funcionalidade que possa
  falhar.

## Regras de negócio
- RN-1: o menu lateral fica sempre visível, em qualquer estado do painel.
- RN-2: só um item do menu fica marcado como selecionado por vez.
- RN-3: clicar no item já selecionado desmarca o item e faz o painel voltar
  para a mensagem de boas-vindas. É o jeito de sair de um módulo sem precisar
  entrar no outro.

## Critérios de aceite
- Dado que a pessoa abre o programa, quando a janela aparece, então o menu
  lateral mostra "Gerar OCR" e "Anonimizar", e o painel mostra a mensagem de
  boas-vindas.
- Dado que a janela está aberta, quando a pessoa clica em "Gerar OCR", então o
  painel troca para o aviso de módulo ainda não construído, e "Gerar OCR" fica
  marcado como selecionado no menu.
- Dado que a janela está aberta, quando a pessoa clica em "Anonimizar", então o
  painel troca para o aviso de módulo ainda não construído, e "Anonimizar"
  fica marcado como selecionado no menu.
- Dado que um módulo já está selecionado, quando a pessoa clica nele de novo,
  então nenhum item fica marcado no menu e o painel volta a mostrar a mensagem
  de boas-vindas.
- Dado que a pessoa fecha a janela e abre o programa de novo, então a janela
  volta ao estado inicial, com nada selecionado. *(Desde a emenda de
  28/10/2026, o menu volta assim, e a janela volta com o tamanho lembrado.)*

## Questões em aberto
Nenhuma.

## Emenda de 28/10/2026 — a janela maximizada e o tamanho lembrado

Funcionalidade 8 do backlog. Levantamento em
`mockups/requisitos/07-mapa-do-entendimento.html` (R-2 e R-7).

### Escopo

- No primeiro uso, a janela abre maximizada, ocupando a tela.
- Depois, ela abre como a pessoa a deixou ao fechar: maximizada, ou com o
  tamanho que tinha.

### Fora de escopo

- A posição da janela: ela abre sempre no meio da tela.
- Lembrar qual item do menu estava marcado: o menu abre sempre sem nada
  marcado (RN-3).

### Regras de negócio

- RN-4: **no primeiro uso, a janela abre maximizada.** "Primeiro uso" é não
  haver tamanho lembrado que dê para ler (o arquivo do motor lembrado, o
  `preferencias.ini` da spec 002, RN-38 e RN-39, sumiu, está estragado ou nunca
  existiu).
- RN-5: **ao fechar, a janela lembra o tamanho e se estava maximizada.** Fechou
  maximizada, abre maximizada — e, saindo do maximizado, volta ao tamanho que
  tinha antes de ser maximizada. Fechou com 1200 × 800, abre com 1200 × 800.
- RN-6: **a posição não é lembrada: a janela abre no meio da tela.** Assim ela
  nunca abre fora da tela, o que aconteceria com quem fechou num segundo monitor
  que não está mais ligado.
- RN-7: **o tamanho lembrado sempre cabe.** Maior que a tela de agora (o monitor
  mudou), ele encolhe para caber; menor que o mínimo de 900 × 560, ele vira o
  mínimo.
- RN-8: o tamanho de antes desta emenda, 1000 × 640, continua sendo o tamanho da
  janela "normal" de quem saiu do maximizado sem ter tamanho lembrado.

### Critérios de aceite

- Dado que não há `preferencias.ini`, quando o programa abre, então a janela vem
  maximizada.
- Dado que a pessoa saiu do maximizado, deixou a janela com 1200 × 800 e fechou,
  quando ela abre de novo, então a janela vem com 1200 × 800, no meio da tela.
- Dado que a pessoa fechou com a janela maximizada, quando ela abre de novo,
  então a janela vem maximizada; e, saindo do maximizado, fica com o tamanho de
  antes de maximizar.
- Dado um tamanho lembrado maior que a tela de agora, quando o programa abre,
  então a janela cabe inteira na tela. Dado um tamanho lembrado menor que
  900 × 560, então ela abre com 900 × 560.
- Dado qualquer tamanho lembrado, então a janela abre no meio da tela, e nunca
  fora dela.

## Emenda de 03/11/2026 — a faixa da esquerda redesenhada

**Situação:** aprovada em 04/11/2026. O acréscimo de 04/11/2026, no fim desta
seção, foi aprovado no mesmo dia.

Funcionalidade 9 do backlog, pedida na conferência da funcionalidade 4, em
01/11/2026. Rascunho aprovado: `mockups/janela/04-tres-direcoes.html`, direção C,
em 03/11/2026. Os rascunhos 02 (ícones em emoji) e 03 (a versão à direita)
ficaram feios ao olhar e foram superados por ele.

### Objetivo

Deixar a faixa da esquerda mais fácil de ler de relance: cada módulo com um
ícone que diz o que ele faz, e o número da versão junto do nome do programa, e
não perdido no pé.

### Escopo

- O cabeçalho da faixa passa a ter um símbolo à esquerda e, ao lado,
  "Anonimizador" numa linha e "CAPCF · versão 0.1.0" embaixo, em letra menor.
- A versão sai do pé da faixa.
- "Gerar OCR" ganha uma lupa, "Anonimizar" um cadeado, e "Configurações de IA"
  troca o emoji de engrenagem por uma engrenagem do mesmo desenho dos outros
  dois. A engrenagem entra a pedido da solicitante, ao olhar o rascunho.
- O item marcado deixa de ser um bloco azul cheio e passa a ter um fundo azul
  fraco com um filete à esquerda, em todos os itens da faixa, inclusive os do
  submenu da IA.
- O `CLAUDE.md` deixa de dizer que a versão fica "no pé da faixa", e a lista da
  próxima entrega ganha os roteiros com a faixa nova.

### Fora de escopo

- **O tema claro, e "Configurações" com Tema e IA dentro**: funcionalidade 10
  do backlog, com levantamento e spec próprios. Pedidos em 03/11/2026, ao
  aprovar o rascunho; separados porque atravessam o programa inteiro.
- **Ícone nos itens do submenu** ("Voltar", "LM Studio", "Servidor de IA
  Interno", "Habilitar IA"): continuam só texto. O que muda neles é só o jeito
  de marcar. *(Revogado pela emenda de 05/11/2026: cada opção ganha o seu
  ícone, menos o "‹ Voltar" — RN-21.)*
- **O ícone da janela** (o da barra de título e da barra de tarefas): continua o
  padrão do Windows, como decidido em 04/09/2026. O símbolo do cabeçalho não
  vira ícone da janela.
- **A marca definitiva do programa**: é decisão de identidade visual. O símbolo
  desta emenda é provisório, e ela toma o lugar dele quando existir.
- **O passar do mouse** sobre um item: continua como hoje.
- O que os módulos fazem, as telas dos painéis e o desenho do painel vazio.
  *(O título das telas dos painéis entrou no acréscimo de 04/11/2026, no
  fim desta seção.)*
- Os roteiros "Como usar" e "Como instalar", que desenham a faixa com a versão
  no pé: são refeitos na próxima entrega, que é trabalho à parte.

### Premissas

- premissa: os desenhos do rascunho (o símbolo, a lupa, o cadeado e a
  engrenagem) saem iguais desenhados pelo programa. A palavra final é a
  conferência na tela.
- premissa: o filete à esquerda basta para quem distingue mal as cores
  reconhecer o item marcado, sem depender do tom do fundo.

### Fluxos

Nenhum fluxo novo. Abrir, escolher um módulo, clicar no item já marcado e entrar
e sair do submenu da IA continuam como nas RN-1 a RN-3 daqui e nas RN-1 a RN-3 da
spec 004. Muda só a aparência da faixa.

### Dados

Nenhum dado novo. O número da versão continua vindo de `programa/versao.py`, o
mesmo que o instalador lê, e nada entra no `preferencias.ini`.

### Estados da interface

- **Item normal:** ícone e texto no cinza de apoio.
- **Item com o mouse em cima:** como hoje.
- **Item marcado:** fundo azul fraco, filete à esquerda, ícone e texto claros,
  em negrito leve.
- **Carregando e erro:** não se aplicam. A faixa não carrega nada e não tem
  operação que possa falhar.

### Regras de negócio

- RN-9: **o cabeçalho tem o símbolo, o nome e a versão.** O símbolo fica à
  esquerda: um quadrado azul de cantos arredondados com uma página e uma linha
  tarjada, em branco. Ao lado, "Anonimizador" numa linha e, embaixo, em letra
  menor e cinza, "CAPCF · versão" seguido do número. Nada do cabeçalho sai
  cortado na faixa de 220 px.
- RN-10: **a versão aparece só no cabeçalho**, e não mais no pé da faixa. Ela
  continua parada quando o submenu da IA toma o lugar do menu.
- RN-11: **cada item do menu principal tem o seu ícone**: lupa em "Gerar OCR",
  cadeado em "Anonimizar", engrenagem em "Configurações de IA". Os três e o
  símbolo do cabeçalho são desenhados pelo próprio programa: sem arquivo de
  imagem, sem fonte de ícones e sem nada baixado da internet, porque o programa
  roda sem rede.
- RN-12: **o ícone acompanha a cor do texto do item**: cinza no item normal,
  claro no item marcado.
- RN-13: **o item marcado tem fundo azul fraco e um filete à esquerda**, e não
  mais o bloco azul cheio. Vale para todo item da faixa, inclusive os do submenu
  da IA. O filete é o que diz "este é o escolhido" sem depender da cor.

### Critérios de aceite

- Dado o programa aberto, então o cabeçalho mostra o símbolo, "Anonimizador" e
  "CAPCF · versão 0.1.0", com o número de `programa/versao.py`, e o pé da faixa
  não mostra versão nenhuma.
- Dado o programa aberto, quando a pessoa entra no submenu da IA, então o
  cabeçalho, com a versão, continua igual.
- Dado o programa aberto na janela mínima de 900 × 560, então nenhum texto do
  cabeçalho e dos itens do menu e do submenu sai cortado: a largura que cada um
  pede cabe na largura que ele tem.
- Dado o programa aberto, então "Gerar OCR", "Anonimizar" e "Configurações de
  IA" têm cada um o seu ícone, e o texto de "Configurações de IA" não tem mais
  o emoji de engrenagem.
- Dado um item marcado, então o ícone dele é claro; dado um item não marcado,
  então o ícone dele é cinza.
- Dado que a pessoa clica em "Anonimizar", então ele fica com o fundo azul fraco
  e o filete à esquerda, e os outros itens ficam sem fundo; e, no submenu da IA,
  o mesmo vale para o item marcado.
- Dado o programa instalado e aberto sem rede, então o símbolo e os ícones
  aparecem, e a receita do PyInstaller não ganhou nenhum arquivo de imagem.
- Dada a lista inteira de testes, então ela continua passando: o que as RN-1 a
  RN-8 daqui e as RN-1 a RN-3 da spec 004 prometem não muda.

### Questões em aberto

Nenhuma.

### Acréscimo de 04/11/2026 — o título dos módulos

**Situação:** aprovado em 04/11/2026.

Pedido pela solicitante na conferência da etapa 2, em 04/11/2026: com a faixa
nova, o título do painel ficou fraco e solto. Rascunho aprovado:
`mockups/janela/05-titulo-dos-modulos.html`, direção A, em 04/11/2026. Na mesma
conferência apareceu o desalinhamento da explicação da IA local, que entra junto.

#### Escopo

- O título das telas dos módulos ganha, à esquerda, o ícone do módulo num
  quadrado de fundo azul fraco, fica em negrito, e passa a ter uma linha fina
  embaixo, na altura da linha do cabeçalho da faixa.
- As telas que ganham esse título: a entrada do Gerar OCR e a do Anonimizar; no
  caminho do PDF, a ficha do documento, "Este documento já tem texto por dentro"
  e a tela de ler ("Este documento precisa ser lido" e "Ler as imagens deste
  documento"); depois da conferência, "Texto conferido. E agora?", "Onde salvar
  o arquivo" e "Onde salvar o texto mascarado"; e as três telas de
  Configurações de IA. As três de depois da conferência entraram na
  construção, no mesmo dia, por escolha da solicitante: tinham o título no
  alto, como as outras, e tinham ficado fora da lista.
- Na escolha do motor de leitura, a explicação embaixo de "IA local" começa
  recuada, como as do PaddleOCR e do Tesseract, e o tempo dela ganha o mesmo
  destaque claro.

#### Fora de escopo

- **O texto dos títulos e das legendas**: não muda. Encurtar a legenda do
  Anonimizar, para caber numa linha, seria mudança de texto.
- **As telas de espera** ("Conferindo o documento…" e a de "Lendo a página"):
  continuam com o título no meio. São de passagem, e um título no alto
  disputaria a atenção com a barra que corre.
- **As caixas de erro** ("Não foi possível abrir o documento", "Não foi
  possível usar este arquivo") e **as telas com o título no meio** ("Arquivo
  gravado", a pergunta antes de descartar, "Já existe um arquivo com esse
  nome"): continuam como hoje.
- **"Conferir o texto" e "Revisar antes de salvar"**: têm cabeçalho próprio,
  com selo e botões ao lado do título, e continuam como estão.
- **O painel vazio** de boas-vindas e o **tema claro** (funcionalidade 10).

#### Premissas

- premissa: o quadrado com o ícone, no mesmo azul fraco do item marcado, liga o
  painel ao menu sem depender da cor: o desenho é o mesmo nos dois lugares.

#### Estados da interface

- **Legenda numa linha:** a linha embaixo do título fica na altura da linha do
  cabeçalho da faixa.
- **Legenda em duas linhas** (a do Anonimizar, nas janelas menores, e as das
  telas do caminho do PDF, com o nome do arquivo): a linha desce junto, sem
  cortar nada.
- **Carregando e erro:** não se aplicam ao título.

#### Regras de negócio

- RN-14: **o título da tela leva o ícone do módulo em que a pessoa está**: a
  lupa no Gerar OCR, o cadeado no Anonimizar, a engrenagem nas Configurações
  de IA. Nas telas do caminho do PDF, que rodam nos dois módulos, o ícone é o do
  módulo por onde a pessoa entrou. O ícone fica num quadrado de cantos
  arredondados, no mesmo azul fraco do item marcado, e é desenhado pelo
  programa, como os da faixa (RN-11). Embaixo do título e da legenda, uma linha
  fina separa o título do resto da tela.
- RN-15: **as explicações da escolha do motor ficam alinhadas**: a da IA local
  começa recuada, debaixo do nome, como as outras duas, e o tempo dela aparece
  no mesmo destaque claro. Vale para todas as frases que aparecem nessa linha.

#### Critérios de aceite

- Dado que a pessoa escolhe "Gerar OCR", então o título da tela de entrada tem
  a lupa no quadrado azul fraco, à esquerda, e uma linha embaixo; dado
  "Anonimizar", o mesmo com o cadeado.
- Dado que a pessoa entra num documento pelo Anonimizar e chega à ficha, à
  decisão sobre o texto ou à tela de ler, então o título delas tem o cadeado;
  pelo Gerar OCR, a lupa.
- Dado que a pessoa entra em Configurações de IA, então o título de cada uma das
  três telas tem a engrenagem.
- Dada a janela aberta no tamanho em que a legenda cabe numa linha, então a
  linha embaixo do título fica na altura da linha do cabeçalho da faixa.
- Dada a janela mínima de 900 × 560, então nenhum título e nenhuma legenda sai
  cortado.
- Dado que a pessoa chega ao salvar, então "Texto conferido. E agora?" e
  "Onde salvar o arquivo" têm a lupa, e "Onde salvar o texto mascarado", o
  cadeado.
- Dada a tela "Conferindo o documento…", as caixas de erro, as telas com o
  título no meio, "Conferir o texto" e "Revisar antes de salvar", então elas
  continuam como antes.
- Dada a escolha do motor, então a explicação da IA local começa no mesmo
  recuo das do PaddleOCR e do Tesseract, com qualquer frase que estiver ali.

## Emenda de 05/11/2026 — o tema claro e o menu Configurações

**Situação:** aprovada em 05/11/2026.

Funcionalidade 10 do backlog, pedida em 03/11/2026, ao aprovar o rascunho 04 da
funcionalidade 9. Levantamento detalhado em
`mockups/requisitos/09-mapa-do-entendimento.html`. Rascunho aprovado em
05/11/2026, como está: `mockups/janela/06-tema-claro-e-configuracoes.html`, com
os quatro ícones da proposta e o filete do título de seção só à direita. As
cores do claro vêm do projeto Gerencial, papel por papel; os
valores estão em `mockups/sistema-de-design.md`, e nada mais do Gerencial entra
neste projeto. Vêm junto as emendas de mesma data na spec 002 (o tema lembrado,
RN-42) e na spec 004 (o nome "Configurações" e as frases que apontam para ele).

### Objetivo

Deixar quem prefere a tela clara usar o programa assim, sem perder nada do
desenho de hoje, e juntar num lugar só, "Configurações", o que se ajusta no
programa.

### Escopo

- Um **tema claro**, ao lado do escuro de hoje, que continua sendo o padrão.
- O item **"Configurações de IA" vira "Configurações"**, com a mesma engrenagem e
  no mesmo lugar, no fim da faixa.
- O submenu passa a ter, de cima para baixo: "‹ Voltar"; o título de seção
  **"Configurações Gerais"**, com "Tema"; e o título de seção **"Configurações de
  IA"**, com "LM Studio", "Servidor de IA Interno" e "Habilitar IA".
- **Cada opção do submenu ganha um ícone em traço**: um círculo metade cheio
  (Tema), uma tela de computador (LM Studio), caixas empilhadas (Servidor de IA
  Interno) e uma chave de ligar (Habilitar IA).
- A tela **"Tema"**, com a engrenagem no título, a legenda "As cores do programa.
  O desenho das telas é o mesmo nos dois." e, na seção "TEMA", duas opções de
  marcar, uma embaixo da outra: **"Escuro"**, com "Fundo grafite e letra clara ·
  o tema de quem nunca escolheu", e **"Claro"**, com "Fundo claro e letra
  escura".
- A frase **"O tema novo vale quando o programa abrir de novo."** e o botão
  **"Reabrir agora"**, só quando a opção marcada não é o tema que está na tela.
- A pergunta antes de reabrir, quando reabrir jogaria trabalho fora.
- **Todas as telas do programa nas cores do claro**: as do Gerar OCR, do
  Anonimizar, do caminho do PDF, da conferência, da revisão, de salvar, de
  Configurações e as perguntas e avisos dentro do painel, com o contraste
  conferido.
- No `CLAUDE.md`: a escolha do tema entra na linha do `preferencias.ini`, o menu
  passa a se chamar "Configurações", e a lista da próxima entrega ganha a linha
  do tema nos roteiros: onde se escolhe e que ele vale ao reabrir.

### Fora de escopo

- **Trocar o tema na hora**, com a janela aberta: a troca vale ao reabrir. As
  cores de cada tela são postas quando ela é montada, e repintar tudo com a
  janela de pé é um trabalho grande, com risco de uma peça ficar no tema velho.
- **Seguir sozinho** o tema claro ou escuro do Windows.
- **Mudar desenho, tamanho, espaço, fonte ou texto** de qualquer tela, além do
  nome do item e das frases da emenda da spec 004. A fonte do Gerencial não vem
  junto.
- Um terceiro tema, ou escolher cor a cor.
- A barra de título da janela, o ícone da janela e a marca definitiva do
  programa.
- O arquivo `.md` que o programa grava: ele não tem cor, e não muda.
- As páginas de documentação do projeto (specs ilustradas, mapas, conferências,
  roteiros): continuam escuras. E os rascunhos de tela de antes desta data
  continuam só no escuro, como registro do que foi aprovado.
- **Fechar a janela pelo X** com texto lido e ainda não salvo continua como
  hoje: sem pergunta. Só o "Reabrir agora" pergunta (RN-25), porque quem clica
  nele está pedindo para trocar as cores, e não para fechar.
- Fechar a funcionalidade 9 e gerar instalador na sessão da spec. O instalador
  de teste é um só, com as duas funcionalidades, no fim da construção desta.

### Premissas

Inferências do mapa 09 que a solicitante leu e não derrubou:

- premissa: o escuro é o tema de quem nunca escolheu, e também de quem tem uma
  escolha guardada que não dá para ler. Quem usa hoje não vê nada mudar ao
  atualizar.
- premissa: "LM Studio", "Servidor de IA Interno" e "Habilitar IA" mantêm os
  nomes e as telas; só passam a ficar debaixo do título "Configurações de IA".
- premissa: o "‹ Voltar" fica sem ícone: a seta escrita já é o desenho dele.
- premissa: os títulos de seção são só texto e não se clicam.
- premissa: a barra de título é a do Windows, nos dois temas.
- premissa: atrás da página do PDF, na conferência, um cinza mais escuro que o
  fundo, para a folha branca se destacar.
- premissa: daqui em diante, todo rascunho de tela nasce nos dois temas.
- premissa: desinstalar apaga a escolha do tema, e atualizar a mantém (RN-41 da
  spec 002).
- premissa: as frases do programa que mandam a pessoa a "Configurações de IA"
  passam a dizer "Configurações" (emenda de mesma data da spec 004).
- premissa: as peças que o Windows pinta, e não o programa (a barra de rolagem,
  a caixa de escolher arquivo, as mensagens do Windows), são conferidas na tela
  na primeira etapa construída; o que destoar no claro volta para a solicitante,
  como acréscimo a esta emenda (A-3 do mapa).

Inferências novas, que apareceram ao escrever esta spec e que a solicitante
leu e aprovou junto com ela, em 05/11/2026:

- premissa: depois de reabrir, a janela abre como em qualquer abertura: no
  tamanho lembrado, com o menu principal e nada marcado (RN-3 e RN-5). Quem
  quiser ver a tela do Tema de novo entra em Configurações.
- premissa: o "Reabrir agora" pergunta antes também quando há **texto lido e
  ainda não salvo**: no Gerar OCR, o texto conferido que não foi salvo; no
  Anonimizar, o texto de um PDF na conferência. Reabrir o perde do mesmo jeito
  que interromper uma leitura, e dá para chegar às Configurações com ele aberto.
- premissa: o programa só fecha depois que a janela nova começou a abrir. Não
  conseguindo abrir de novo, ele não fecha, e diz por quê na tela do Tema.

### Fluxos

**Normal: escolher o claro.**

1. A pessoa clica em "Configurações". O menu dá lugar ao submenu, com "Tema"
   marcado, e o painel mostra a tela do Tema, com "Escuro" marcado.
2. Ela marca "Claro". A escolha fica guardada nessa hora, e aparecem a frase e o
   botão "Reabrir agora".
3. Ela clica em "Reabrir agora". A janela fecha e abre de novo, inteira no
   claro, no tamanho de antes, com o menu principal e nada marcado.

**Alternativo: reabrir depois.** A pessoa marca "Claro" e segue trabalhando no
escuro. Na próxima vez que abrir o programa, ele vem no claro.

**Alternativo: mudar de ideia.** Com "Claro" marcado e o escuro na tela, a pessoa
marca "Escuro" de novo. A frase e o botão somem, porque não há nada a reabrir, e
a escolha guardada volta a ser o escuro.

**Caminho torto: uma leitura em andamento.** A pessoa mandou ler um PDF no Gerar
OCR e foi às Configurações enquanto ele lia. Ao clicar em "Reabrir agora", a
frase e o botão dão lugar à pergunta, na própria tela, sem caixa por cima: "Há
uma leitura em andamento no Gerar OCR. Reabrir agora a interrompe, e o documento
precisa ser lido de novo depois.", com **"Continuar a leitura"**, o botão forte,
e **"Reabrir mesmo assim"**. Continuar faz a pergunta sumir e a frase e o botão
voltarem, com a leitura seguindo. Reabrir mesmo assim para a leitura, como o
fechar já faz, e reabre. Com a leitura no Anonimizar, a frase diz "no
Anonimizar".

**Caminho torto: um texto lido e ainda não salvo.** O mesmo jeito de perguntar,
com "Há um texto lido e ainda não salvo no Gerar OCR. Reabrir agora o descarta,
e o documento precisa ser lido de novo depois.", e os botões **"Não reabrir"**, o
forte, e **"Reabrir mesmo assim"**. Havendo mais de uma coisa a perder, a frase
cita todas, numa pergunta só, e o botão forte é "Continuar a leitura" quando uma
delas é uma leitura.

**Caminho torto: uma revisão não salva.** O "Reabrir agora" passa pela mesma
pergunta de quando se fecha a janela, que aparece no Anonimizar, com **"Reabrir
sem salvar"** no lugar de "Fechar sem salvar". Na prática ninguém chega a ela:
sair do Anonimizar com uma revisão aberta já pergunta antes. Ela fica para o
dia em que um caminho novo levar até aqui com a revisão aberta.

**Caminho torto: não dá para guardar a escolha.** A pasta da instalação não
aceita gravação. A frase e o botão aparecem igual, e o "Reabrir agora" abre a
janela nova no tema escolhido, sem aviso. Fechando e abrindo por conta própria,
volta o tema que estava guardado.

**Caminho torto: a escolha guardada não dá para ler.** O programa abre no escuro,
sem erro e sem aviso, e a próxima escolha grava de novo.

**Caminho torto: o programa não consegue abrir de novo.** A janela não fecha, e
a tela do Tema diz, no lugar do botão: "Não foi possível reabrir agora. O tema
novo vale quando você fechar e abrir o programa."

### Dados

A escolha do tema entra no `preferencias.ini`, ao lado do motor de cada módulo e
do tamanho da janela: `escuro` ou `claro`. Sem ela, ou com qualquer outro valor,
vale o escuro. Nada mais é guardado. As regras de guardar são as da spec 002
(RN-38 a RN-42).

### Estados da interface (a tela do Tema)

- **O tema marcado é o que está na tela:** só as duas opções, nada embaixo. É o
  estado de quem entra pela primeira vez.
- **O tema marcado é outro:** embaixo das opções, a frase e o "Reabrir agora".
- **A pergunta antes de reabrir:** uma faixa de aviso no lugar da frase e do
  botão, com a frase do que se perderia e os dois botões.
- **Não deu para reabrir:** a frase do caminho torto no lugar do botão.
- **Reabrindo:** a janela some e volta. Não há tela de espera: a espera é a do
  programa abrindo, como sempre.
- **Erro ao guardar:** não aparece. A escolha vale até fechar (RN-39 da spec
  002).

### Regras de negócio

- RN-16: **dois temas, escuro e claro, e o escuro é o padrão.** Só as cores
  mudam: o desenho, os tamanhos, os espaços, as fontes e os textos de toda tela
  são os mesmos nos dois. O escuro continua com os valores de hoje. O valor de
  cada papel em cada tema está no `mockups/sistema-de-design.md`.
- RN-17: **a janela inteira nasce com um tema só**, o escolhido ao abrir. Nenhuma
  peça aparece nas cores do outro tema, e escolher outro vale ao reabrir.
- RN-18: **no claro, toda letra tem contraste de pelo menos 4,5 para 1** sobre o
  fundo em que está. A exceção é o texto apagado das opções desligadas, que é
  apagado de propósito, como no escuro. O amarelo de alerta do claro só pinta
  fundo e borda; a letra de alerta, inclusive a do suspeito, é o âmbar escuro.
- RN-19: **as marcas da revisão mantêm o sentido e o traço nos dois temas**: o
  CPF válido em vermelho com traço reto, o suspeito na cor de alerta com traço
  ondulado, o que veio da IA no lilás (no claro, violeta) com traço-ponto, o
  liberado em verde com traço tracejado, e o mascarado por você em azul com
  traço pontilhado. É o traço que separa os tipos para quem distingue mal as
  cores.
- RN-20: **o item da faixa se chama "Configurações"**, e o submenu tem as duas
  seções na ordem do escopo. O título de seção é um texto menor, no cinza de
  apoio, com um filete fino que corre à direita dele até a borda da faixa; ele
  não se clica e nunca fica marcado.
- RN-21: **cada opção do submenu tem o seu ícone**, menos o "‹ Voltar". Valem as
  regras dos ícones da faixa: desenhados pelo programa, sem nada baixado
  (RN-11), e na cor do texto do item (RN-12). Fica revogado o "continuam só
  texto" da emenda de 03/11/2026.
- RN-22: **entrar em "Configurações" abre a primeira opção, o Tema**, e não mais o
  LM Studio. O título da tela do Tema leva a engrenagem, como as três da IA: é o
  ícone do lugar em que a pessoa está (RN-14).
- RN-23: **a escolha é guardada no clique**, e a frase e o "Reabrir agora"
  aparecem só enquanto a opção marcada não é o tema que está na tela.
- RN-24: **"Reabrir agora" fecha o programa e abre de novo, no tema marcado** —
  mesmo que a escolha não tenha sido guardada. A janela nova abre como em
  qualquer abertura (RN-3 a RN-7). A velha só fecha depois que a nova começou a
  abrir; sem conseguir, ela fica, e diz por quê.
- RN-25: **reabrir pergunta antes quando jogaria trabalho fora**: uma leitura em
  andamento ou um texto lido e ainda não salvo, em qualquer dos dois módulos. A
  pergunta fica na própria tela do Tema, o botão forte é o que não perde nada, e
  uma revisão não salva leva à pergunta do fechar, com "Reabrir sem salvar". Sem
  nada a perder, reabre direto.
- RN-26: **toda cor de tela vem do tema.** Nenhuma tela tem cor escrita dentro
  dela, fora do lugar onde moram as cores dos dois temas. Ficam iguais nos dois
  temas só o branco da letra dentro do botão de destaque e o branco do desenho
  do símbolo do cabeçalho.

### Critérios de aceite

- Dado que não há `preferencias.ini`, quando o programa abre, então ele vem no
  escuro, com cada papel no valor de antes desta emenda.
- Dado um `preferencias.ini` com um tema que não é `escuro` nem `claro`, quando
  o programa abre, então ele vem no escuro, sem erro.
- Dado o programa aberto, então o último item da faixa é "Configurações", com a
  engrenagem, e nenhum item se chama "Configurações de IA".
- Dado que a pessoa clica em "Configurações", então o submenu mostra, nesta
  ordem: "‹ Voltar", "Configurações Gerais", "Tema", "Configurações de IA",
  "LM Studio", "Servidor de IA Interno" e "Habilitar IA"; "Tema" fica marcado; e
  o painel mostra a tela do Tema, com a engrenagem no título.
- Dado o submenu, quando a pessoa clica num título de seção, então nada muda: o
  título não fica marcado e o painel continua o mesmo.
- Dado o submenu, então "Tema", "LM Studio", "Servidor de IA Interno" e
  "Habilitar IA" têm cada um o seu ícone, claro no item marcado e cinza nos
  outros, e o "‹ Voltar" não tem ícone.
- Dada a janela mínima de 900 × 560, então nada sai cortado no submenu nem na
  tela do Tema, inclusive com a pergunta antes de reabrir: a largura que cada
  peça pede cabe na largura que ela tem.
- Dado o escuro na tela, quando a pessoa marca "Claro", então o
  `preferencias.ini` passa a dizer `claro` na mesma hora, e aparecem a frase e o
  "Reabrir agora"; quando ela marca "Escuro" de novo, então os dois somem e o
  arquivo volta a dizer `escuro`.
- Dado "Claro" marcado, quando a pessoa fecha pelo X e abre de novo, então o
  programa vem no claro, e a tela do Tema mostra "Claro" marcado e nada embaixo.
- Dado "Claro" marcado e nada a perder, quando a pessoa clica em "Reabrir
  agora", então a janela fecha e abre de novo no claro, sem pergunta, no tamanho
  em que estava (ou maximizada, se estava), com o menu principal e nada marcado.
- Dada a pasta da instalação sem gravação, quando a pessoa marca "Claro" e clica
  em "Reabrir agora", então o programa abre no claro; e, fechado e aberto de
  novo, abre no escuro.
- Dada uma leitura em andamento no Gerar OCR, quando a pessoa clica em "Reabrir
  agora", então aparece na tela do Tema a pergunta com "no Gerar OCR",
  "Continuar a leitura" e "Reabrir mesmo assim", sem caixa por cima; com
  "Continuar a leitura", a leitura segue até o fim e a frase e o botão voltam;
  com "Reabrir mesmo assim", a leitura para, sem a caixa de "o programa parou de
  funcionar", e o programa abre de novo no claro. O mesmo com a leitura no
  Anonimizar, com "no Anonimizar".
- Dado um texto lido e não salvo no Gerar OCR, ou um PDF na conferência do
  Anonimizar, quando a pessoa clica em "Reabrir agora", então aparece a pergunta
  com "Não reabrir" e "Reabrir mesmo assim"; com "Não reabrir", o texto continua
  lá, como estava.
- Dada uma revisão não salva, quando "Reabrir agora" é acionado, então aparece no
  Anonimizar a pergunta de quando se fecha a janela, com "Reabrir sem salvar"; e,
  voltando para salvar, nada reabre.
- Dado que abrir de novo falha, quando a pessoa clica em "Reabrir agora", então
  a janela continua aberta e a tela do Tema mostra "Não foi possível reabrir
  agora. O tema novo vale quando você fechar e abrir o programa."
- Dados os valores do claro, então cada cor de letra tem contraste de pelo menos
  4,5 para 1 sobre o fundo da janela e sobre o fundo dos quadros, menos o texto
  apagado; e o amarelo de alerta não é a cor de letra de nenhuma peça.
- Dada a revisão do Anonimizar no claro, então o CPF válido, o suspeito, o que
  veio da IA, o liberado e o mascarado por você aparecem cada um na sua cor do
  claro, com o mesmo traço do escuro.
- Dado o programa aberto no claro, então nenhuma tela montada tem um valor de cor
  do escuro; e no código das telas não há cor escrita fora do lugar das cores,
  menos as duas exceções da RN-26.
- Dado o programa no claro, quando a solicitante percorre, na conferência na
  tela, o Gerar OCR, o Anonimizar com um PDF e um Word, a revisão com cada tipo
  de marca, o salvar e as Configurações, então nada fica nas cores do escuro nem
  ilegível, e as peças que o Windows pinta foram olhadas.
- Dado o programa instalado e aberto sem rede, então o claro funciona, e a
  receita do instalador não ganhou nenhum arquivo de imagem, de fonte ou de cor.
- Dada a lista inteira de testes, então ela continua passando, com os testes que
  dizem "Configurações de IA" e o de "o submenu continua só texto" ajustados a
  esta emenda.

### Questões em aberto

Nenhuma.

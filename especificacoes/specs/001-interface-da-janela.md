# Spec 001 — Interface da janela

**Status:** implementada
**Data:** 2026-09-04
**Emendada em:** 2026-10-28 (aprovada no mesmo dia) — a janela abre maximizada no
primeiro uso e depois lembra o tamanho e se estava maximizada (funcionalidade 8
do backlog, pedido da usuária no levantamento). Está na seção "Emenda de
28/10/2026", no fim; o fora de escopo e o último critério trazem a remissão. O
motor lembrado, da mesma funcionalidade, está na emenda de mesma data da spec
002.

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
  emenda, no fim. A posição dela continua não lembrada.)*
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

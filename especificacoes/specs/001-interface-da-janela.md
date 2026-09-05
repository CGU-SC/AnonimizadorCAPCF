# Spec 001 — Interface da janela

**Status:** implementada
**Data:** 2026-09-04

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
  volta ao estado inicial, com nada selecionado.

## Questões em aberto
Nenhuma.

# Sistema de design — Anonimizador CAPCF

Decidido em 03/09/2026, com a usuária, antes da primeira tela. Toda página do
projeto (mockup de tela ou página de relatório) segue isto.

## Identidade e tom

Identidade do zero, com cara institucional/UFSC sóbria — sem copiar a marca
oficial da UFSC (exigiria autorização de identidade visual). Tom neutro de
ferramenta de trabalho: direto, sem enfeite, para uso interno repetido no
dia a dia — não é produto comercial nem site institucional formal.

## Tema

**Dois temas, escuro e claro, desde a funcionalidade 10** (rascunho
`mockups/janela/06-tema-claro-e-configuracoes.html`, aprovado em 05/11/2026).
O escuro continua o padrão. A pessoa escolhe em Configurações → Tema, e a troca
vale ao reabrir o programa (o botão "Reabrir agora" faz isso na hora).

As cores são nomeadas por **papel** (`fundo`, `texto`, `destaque`), nunca pelo
nome da cor, e cada papel tem um valor em cada tema. **Só as cores mudam**:
desenho, tamanhos, espaços, fontes e textos são os mesmos nos dois.

Os valores do claro vêm das cores do projeto Gerencial, menos os que a tabela
diz "escolhido aqui": onde o Gerencial não tem o papel, ou o valor dele não serve
como letra. Do Gerencial, só os valores de cor entram neste projeto. **Contraste se confere em cada
tema**: o mínimo para letra pequena é 4,5 para 1, e o do claro está medido contra
o fundo dos quadros (`#fbfcfd`).

Toda tela nova nasce desenhada nos dois temas.

## Paleta (valores exatos)

| Papel | Escuro | Claro | Uso |
| --- | --- | --- | --- |
| `--cor-fundo` | `#1e2228` | `#f2f4f7` | fundo da janela — no escuro, cinza-grafite, nunca preto puro |
| `--cor-fundo-elevado` | `#262b33` | `#fbfcfd` | painéis, cartões, campos, a faixa da esquerda |
| `--cor-borda` | `#383e47` | `#c9d0d8` | divisórias, contorno de campo. Um cinza mais claro sumiria no contorno de campo |
| `--cor-texto` | `#e8eaed` | `#16202b`, 16:1 | texto principal |
| `--cor-texto-secundario` | `#9aa1ac` | `#4a5868`, 7,1:1 | legenda, texto de apoio, ícone do item não marcado |
| `--cor-texto-apagado` | `#6c737d` | `#8a96a3`, 2,9:1 — o papel, escolhido aqui | opção desligada — apagada de propósito, nos dois temas (no escuro, 3,6:1) |
| `--cor-destaque` | `#3b6ea5` | `#1f4e8c`, 8,1:1 | botão principal, links. Letra branca dentro (8,3:1 no claro) |
| `--cor-destaque-hover` | `#4f86bf` | `#2a6fc9`, 4,8:1 | passar o mouse sobre o destaque, filete do item marcado, bolinha do radio, "mascarado por você" |
| `--cor-destaque-fraco` | `#3b6ea5` a 24% | `#1f4e8c` a 10% — a força, escolhida aqui | fundo do item marcado da faixa e do ícone do título dos módulos. A força do claro: o azul-marinho é mais forte que o azul do escuro |
| `--cor-passar-o-mouse` | branco a 6% | `#16202b` a 6% — escolhido aqui | fundo do item da faixa com o mouse em cima |
| `--cor-atras-do-pdf` | `#0f1216` | `#c9d0d8` | o fundo atrás da página do PDF na conferência: mais escuro que o fundo, nos dois temas, para a página branca se destacar |
| `--cor-sucesso` | `#4caf6d` | `#1f7a3a`, 5,2:1 | o que deu certo (arquivo gravado) — **não** marca CPF desde 14/09/2026. **Uma exceção, desde 17/09/2026:** o que a pessoa **liberou** na revisão é verde — o selo "N liberados por você", o número liberado no texto (com traço tracejado) e a etiqueta "liberado" na lista —, a pedido da usuária: marca uma decisão dela, e num documento com muitos liberados o cinza ficava difícil de achar depois. O traço tracejado é o que separa o liberado dos outros tipos para quem não distingue bem as cores |
| `--cor-alerta` | `#d9a441` | `#c2aa07` — **só fundo e borda, nunca letra** (2,3:1) | fundo e borda de aviso; no escuro, também o CPF **suspeito** — dígito verificador não bateu, indo para conferência humana —, que desde 06/11/2026 tem papel próprio, o `--cor-suspeito`. Traço ondulado. Entre 14 e 16/09/2026 marcou também o "forma CPF válido", que voltou ao vermelho |
| `--cor-alerta-texto` | `#d9a441`, o mesmo | `#a85a00`, 4,6:1 sobre a janela e 5,0:1 sobre os quadros; de 4,1 a 4,5:1 dentro das caixas e dos selos amarelos (exceção da RN-30) — escolhido aqui | **papel novo da funcionalidade 10**: toda letra de aviso — o título das caixas de aviso, o "não há" da ficha do PDF, o selo "LIDO PELO ...", a falta do motor. No escuro o amarelo serve de letra; no claro não. Era `#7a5c00` até 06/11/2026, e era também a cor do suspeito; a solicitante o achou perto demais do preto do texto (rascunhos 08 e 09 da janela) |
| `--cor-suspeito` | `#d9a441`, o mesmo | `#c28102`, 3,0:1 sobre a janela e 3,2:1 sobre os quadros, e 5,0:1 contra a letra do texto (exceção da RN-30) — escolhido com a solicitante | **papel novo de 06/11/2026**: o suspeito — o número no texto da revisão, com o traço ondulado; a chave de cores; o selo "N suspeitos"; e a etiqueta "falha na conta" ou "quase CPF" na lista. Abaixo do mínimo de letra de propósito: o que faz o suspeito ser achado é a diferença para o preto do texto, e o traço ondulado continua separando-o para quem distingue mal as cores |
| `--cor-suspeito-barra` | `#d9a441`, o mesmo | `#ec9c01` — não é letra | **papel novo de 06/11/2026**: a barra à esquerda do item suspeito na lista de achados, num âmbar mais vivo que o da etiqueta |
| `--cor-erro` | `#d9534f` | `#ae0202`, 6,8:1 sobre a janela e 7,3:1 sobre os quadros (era `#b3261e` até 06/11/2026) | falha (arquivo inválido, OCR não rodou), a faixa da caixa da dupla conferência de um número com forma CPF válido — o momento de risco — e, desde 16/09/2026, o **"forma CPF válido"** na revisão, com traço reto |
| `--cor-erro-texto` | `#f08a86` | `#ae0202`, o mesmo do erro: no claro ele já tem contraste de letra | letra em vermelho sobre o fundo escuro (contraste 6,6:1) — é este vermelho que marca o "forma CPF válido" no texto da revisão e o selo dele. O `#d9534f` tem 4:1 sobre o fundo e 3,6:1 sobre o fundo elevado, abaixo do mínimo de 4,5:1 para letra pequena |
| `--cor-ia` | `#b39ddb` | `#7356c8`, 5,3:1 | o que **veio da IA** na revisão: a seção "A IA pediu para olhar", o selo, a etiqueta e o número ou trecho no texto, com **traço-ponto**. Lilás porque amarelo, vermelho, azul e verde já têm dono, e traço-ponto porque reto, ondulado, tracejado e pontilhado também. Aprovado em 31/10/2026 (spec 004, rascunho 11 do Anonimizar) |

**Os tons que as telas já usavam sem nome**, aprovados em 06/11/2026 no rascunho
`mockups/janela/07-os-tons-que-faltavam.html`, onde cada um aparece na peça de
verdade, nos dois temas. O escuro de cada um é o valor que o programa já usava;
o contraste do claro está medido sobre o fundo dos quadros e o da janela, com a
letra que fica em cima.

| Papel | Escuro | Claro | Uso |
| --- | --- | --- | --- |
| `--cor-erro-fundo` | `#d9534f` a 10% (26 de 255) | `#b3261e` a 7%, do rascunho 06 | a faixa de falha, a caixa da dupla conferência, o erro de salvar |
| `--cor-alerta-fundo` | `#d9a441` a 10% (26 de 255) | `#c2aa07` a 12%, do rascunho 06 | a faixa de cuidado: o motor que falta, o aviso da conferência, os avisos da IA |
| `--cor-alerta-fundo-forte` | `#d9a441` a 12% (31 de 255) | `#c2aa07` a 15% | o aviso antes de gravar com os CPFs inteiros, e o dos números liberados |
| `--cor-alerta-selo` | `#d9a441` a 15% (38 de 255) | `#c2aa07` a 18%; a letra é o `alerta-texto`, 4,1:1 (exceção da RN-30) | o selo "LIDO PELO ..." da conferência |
| `--cor-destaque-aviso` | `#3b6ea5` a 10% (26 de 255) | `#1f4e8c` a 6% | a faixa azul de informação. Mais fraca que no escuro: a 10%, o azul-marinho pesava mais que um aviso |
| `--cor-destaque-na-lista` | `#3b6ea5` a 18% (46 de 255) | `#f2f5f8`, o azul a 4% já misturado; pior letra 4,55:1 | o item marcado na lista de achados e o selo aceso do grupo. Bem mais fraco que no escuro, de propósito: com mais fundo, a etiqueta "mascarado por você" cai abaixo de 4,5:1. No claro, quem diz "é este" é a borda azul |
| `--cor-destaque-selo` | `#3b6ea5` a 20% (51 de 255) | `#1f4e8c` a 10% | o selo "VEIO DO PRÓPRIO PDF" e o "TEXTO GRAVADO NO PRÓPRIO DOCUMENTO" |
| `--cor-destaque-selo-texto` | `#7fb1e8` | `#1f4e8c`, 6,4:1 | a letra desses dois selos |
| `--cor-ia-fundo` | `#b39ddb` a 9% (23 de 255) | `#7356c8` a 10%, do rascunho 06 | a faixa da revisão por IA. No escuro fica o 9% de sempre, e não os 14% que o rascunho 06 desenhou |
| `--cor-ia-marca` | `#b39ddb` a 14% (36 de 255) | `#7356c8` a 6%; letra lilás 4,5 a 4,9:1 | o fundo atrás do número que a IA apontou, no texto da revisão. Mais fraco que no escuro, porque a letra lilás é a própria marca |
| `--cor-area-de-soltar` | branco a 1,6% (4 de 255) | `#16202b` a 2% | o fundo da área tracejada de soltar o arquivo |
| `--cor-texto-desligado` | `#5d646e` | `#8a96a3`, 2,9:1 | a letra de botão e de campo desligados. Apagada de propósito (RN-18 da spec 001) |
| `--cor-texto-desligado-pequeno` | `#565d66` | `#8a96a3`, 2,9:1 | a letra dos botões pequenos desligados da conferência. No escuro é um cinza um pouco diferente, e por isso é papel próprio |
| `--cor-borda-desligada` | `#4a5058` | `#dde2e7` | a borda do radio desligado: mais fraca que a borda comum, nos dois temas |
| `--cor-bolinha-ligada` | `#ffffff` | `#fbfcfd`, 8,1:1 sobre o destaque | a bolinha da chave ligada. É papel com valor em cada tema, e não uma terceira exceção da RN-26 |

**Mudou em 18/09/2026** (conferência da etapa 5 do Anonimizar, sétima emenda da
spec 003): a máscara do CPF passa de `***.456.789-**` para **`XXX.456.789-XX`**,
na tela e no arquivo gravado. O asterisco é a marcação de negrito e itálico do
Markdown, e o arquivo que o programa grava é um `.md`: aberto no Bloco de Notas
do Windows, que mostra `.md` já formatado, a máscara aparecia quebrada —
`*.222.222-`, com os asteriscos engolidos. O `X` não significa nada em Markdown
em posição nenhuma, fica igual no texto cru e no formatado, e é como documento
brasileiro costuma mostrar CPF tarjado. Os rascunhos desenhados antes desta data
continuam mostrando o asterisco: eles são o registro do que foi aprovado na
época, e o que vale é esta linha.

**Mudou em 16/09/2026** (conferência da etapa 2 do Anonimizar): o "forma CPF
válido" **vira "CPF válido" e volta ao vermelho**, no tom de letra `--cor-erro-texto`, e o suspeito
fica sozinho no amarelo. Marcados os dois na mesma cor, com a diferença só no
traço, a distinção ficou sutil demais na tela de verdade — e é justamente o
número que passa na conta, o mais perigoso, que precisa saltar aos olhos. O
traço continua separando os dois: reto para o "forma CPF válido", ondulado para
o suspeito, para quem não distingue bem as cores. A caixa da dupla conferência
continua vermelha.

**Mudou em 14/09/2026** (rascunhos 06 e 07 do Anonimizar): o CPF que passa na
conta do dígito verificador deixou de ser verde. Na revisão do Anonimizar ele é
o número mais perigoso — quase certamente o CPF de alguém —, e verde dava a
impressão de coisa boa. Ele passa a ter o rótulo "forma CPF válido", no amarelo
de alerta, e o vermelho fica para a caixa da dupla conferência, que é o momento
em que ele pode escapar (decidido pela usuária). O verde fica só para "deu certo".

## Tipografia

| Papel | Valor |
| --- | --- |
| `--fonte-texto` | `"Segoe UI", system-ui, sans-serif` — a fonte nativa do Windows, sem download |
| `--fonte-mono` | `"Cascadia Mono", "Consolas", monospace` — para número de CPF e tabela |
| `--texto-pequeno` | `13px` |
| `--texto-base` | `15px` |
| `--texto-grande` | `20px` |
| `--texto-titulo` | `28px` |

## Espaçamento e densidade

Densidade **confortável**: o programa não lida com listas longas no dia a dia
(documento por vez), então prioriza espaço e clareza.

| Papel | Valor |
| --- | --- |
| `--espaco-1` | `4px` |
| `--espaco-2` | `8px` |
| `--espaco-3` | `16px` |
| `--espaco-4` | `24px` |
| `--espaco-5` | `32px` |
| `--raio` | `6px` (cantos arredondados de botão e campo) |

## Ícone e marca

A marca definitiva ainda não existe. O símbolo do cabeçalho (o quadrado azul com
a página e a linha tarjada) é provisório: o quadrado tem o azul de destaque de cada tema, e o desenho é
branco nos dois.

**Ícones em traço**, desenhados pelo próprio programa (nada baixado), numa grade
de 20 × 20, com traço de 1,6 e pontas arredondadas, em 18 px na faixa. A cor
acompanha o item: texto secundário no item normal, texto no marcado. Desde
03/11/2026: lupa (Gerar OCR), cadeado (Anonimizar), engrenagem (Configurações).
Desde a funcionalidade 10, o submenu de Configurações: **círculo metade cheio**
(Tema), **tela de computador** (LM Studio), **caixas empilhadas** (Servidor de IA
Interno) e **chave de ligar** (Habilitar IA).

## Layout de referência (janela do programa)

Faixa fixa à esquerda, com 220 px, no `--cor-fundo-elevado` e com a borda da
direita na `--cor-borda`; painel principal à direita, em `--cor-fundo`, onde
cada módulo mostra a sua tela. Os itens da faixa começam e terminam a 24 px das
bordas da janela.

**O cabeçalho da faixa** (funcionalidade 9, emenda de 03/11/2026 da spec 001). O
símbolo tem 34 px e raio 8. Ao lado dele, a 10 px, vem "Anonimizador", em 16 px,
peso 700, no `--cor-texto`, e embaixo "CAPCF · versão X", em 13 px, no texto
secundário. A versão fica aí, e não no pé, porque é o que a pessoa precisa
responder ao relatar um defeito, e no pé ninguém a achava. O cabeçalho tem 60 px
de altura, a mesma do título das telas dos módulos, para a linha de baixo de um
continuar na do outro, e não muda quando o submenu de Configurações entra. Dele
até o primeiro item há 12 px de respiro.

**Os itens.** "Gerar OCR" e "Anonimizar" ficam no alto, e "Configurações" no pé,
cada um com o ícone dele (seção "Ícone e marca"). A letra tem 15 px, no texto
secundário, com 12 px de espaço por dentro, 8 px de margem dos lados e raio 6.
Com o mouse em cima, o fundo é o `--cor-passar-o-mouse`. O item marcado tem fundo
`--cor-destaque-fraco`, filete de 3 px à esquerda no `--cor-destaque-hover` e
letra no `--cor-texto`, em seminegrito. Todo item tem o filete, transparente nos
não marcados, para o texto não pular para o lado ao ser marcado.

O submenu de Configurações (funcionalidade 10) tem "‹ Voltar" no alto e duas
seções com título: **Configurações Gerais** (Tema) e **Configurações de IA** (LM
Studio, Servidor de IA Interno, Habilitar IA). O título de seção é letra
pequena (13 px, seminegrito, sem maiúsculas), no texto secundário, com um filete
fino, na cor da borda, que corre à direita dele até a borda da faixa.

## Roteiros da entrega

Os dois roteiros que vão com o instalador, `empacotar/como-instalar.html` e
`empacotar/como-usar.html`, ganharam este desenho na entrega da 0.2.0, aprovado
pela solicitante em 10/11/2026 (commits `e84eac7` e `90f23ad`). **O roteiro de uma
versão nova nasce de uma cópia do da versão anterior**: a folha de estilo vai
inteira, a ordem das seções fica, e mudam o texto, as prints e o número da versão.
Esta seção é contra o que a cópia é conferida, para nada mudar sem querer. Peça
nova entra aqui na mesma rodada em que nasce. As regras gerais (print de verdade,
moldura por cima, imagem dentro do arquivo) estão na `skill-11-gerente-de-entrega`.

| Peça | Valor |
| --- | --- |
| Página | fundo `--cor-fundo`, letra 15 px com entrelinha 1,55, `"Segoe UI"`. Largura `max(55%, min(920px, 100%))`, centrada: 55% da tela, nunca menos de 920 px, e a largura toda num celular. Folga de 36 px no alto e 64 px embaixo |
| Faixa do alto | a faixa inteira em `#22262d`, com a linha de baixo na `--cor-borda`; por dentro, a mesma largura da página, 18 px de folga. À esquerda, o símbolo (43 px, raio 10, `--cor-destaque`, sombra `0 2px 8px` preta a 35%, a página com as linhas em branco, de 24 px e traço 2), e a 12 px dele o nome "Anonimizador" (19 px, 700) com "CAPCF · UFSC" embaixo (14 px, texto secundário). À direita, a etiqueta "Versão X · teste": 10,5 px, 600, letra `#f0c674`, fundo `--cor-alerta` a 12%, borda dele a 50%, cantos redondos de ponta a ponta, 4 × 11 px, com uma bolinha de 6 px na `--cor-alerta` antes. Da 1.0.0 em diante, sem o "· teste" |
| Capa | cartão com raio 18, folga `36px 40px 34px`, fundo `linear-gradient(120deg, #131b28 0%, #16253a 55%, #1a2f4a 100%)` ("quase noite"), borda `#5b8fc9` a 20% e sombra `0 10px 30px` preta a 35%. No canto de baixo à direita, um anel de 420 px com 36 px de branco a 4%, deslocado 120 px para a direita e 160 px para baixo. A chamada em 12,5 px, maiúsculas, espaçamento 0,12em, 700, `#8fc1f0`; o título em 44 px, 800 (34 px em tela de até 600 px); o texto em 16 px, `#d4d8de`, até 85% do cartão, com o negrito em branco. Embaixo, as fichas: 13 px, cantos redondos, borda branca a 20%, fundo branco a 5%; a ficha boa tem borda `--cor-sucesso` a 60% e letra `#8fd6a6` |
| Títulos da capa | instalar: chamada "Para quem instala", título "Instruções de instalação", fichas a 46 px do texto. Usar: chamada "Instruções de uso", título "O que é o Anonimizador", depois a ressalva (filete de 3 px na `--cor-alerta`, letra `#f0d9a8` em 15 px, negrito `#f0c674`) e o "Exemplo de saída" da máscara (`123.456.789-10` riscado → `XXX.456.789-XX`, com o `XXX` e o `XX` na `--cor-alerta`), fichas a 18 px. A frase de abertura é a mesma nos dois |
| Seções | título `h2` em 21 px, a 48 px do que vem antes; o passo obrigatório leva o número num círculo de 32 px na `--cor-destaque`. Instalar: aviso de versão de teste, aviso azul de quem atualiza, Antes de começar, O caminho inteiro, O que você recebeu, 1 Instalar o programa, Atualizar da versão anterior, 2 Tesseract, 3 IA local, 4 Para a TI, Se algo der errado, o bloco de relatar, Desinstalar. Usar: aviso de versão de teste, Antes de começar, O caminho inteiro, as partes numeradas (uma por coisa que a pessoa faz), Cuidados, Se algo der errado, o bloco de relatar |
| Prints | cada uma num bloco com a legenda em cima (12 px, maiúsculas, texto secundário, dizendo o que a tela é, e não "figura 1"). Borda `#4a5260`, raio 8, sombra `0 6px 24px` preta a 35%, nunca mais larga que a página (`.print.estreita`: até 300 px, para tela pequena). A imagem vai no próprio HTML, em PNG de 256 cores, como `data:image/png;base64` |
| Moldura do "onde clicar" | um quadro posto por cima da print, em porcentagem dela (`left`, `top`, `width`, `height`, com uma casa decimal): borda de 3 px na `--cor-alerta`, raio 4, e um contorno de 3 px preto a 45% por fora, para aparecer sobre fundo claro e escuro. Nas telas desenhadas, a peça a clicar leva um contorno de 2 px na `--cor-alerta`, a 2 px dela |
| Telas desenhadas | só as que não se capturam (o SmartScreen, a confirmação de administrador, os componentes do instalador do Tesseract): até 440 px, borda `#4a5260`, raio 8, nas cores do próprio Windows, com a legenda "a tela que aparece" |
| Rodapé | a 56 px do fim, com a linha de cima na `--cor-borda`, 13 px, texto secundário. À esquerda, "Anonimizador CAPCF · versão X"; à direita, "O programa foi desenvolvido pela CGU no âmbito da consultoria realizada à UFSC em 2026." Em tela estreita, a segunda frase desce |
| Impressão | o roteiro impresso sai claro: fundo branco, quadros `#f5f6f8`, borda `#cfd4db`, texto `#1e2228`, e nenhum quadro partido entre duas folhas |

**As peças**, com o nome que têm na folha de estilo, para o roteiro novo achar a
que já existe antes de inventar outra:

| Peça | Para quê |
| --- | --- |
| `.aviso` (amarelo), `.aviso.azul`, `.aviso.ia` (lilás) | faixa com ícone à esquerda: cuidado, informação, o que é da IA |
| `.fatos` com `.fato` | os requisitos em quadros lado a lado, com o rótulo em maiúsculas em cima |
| `.percurso` com `.etapa` e `.seta` | o caminho inteiro, da esquerda para a direita. Filete de cima azul no obrigatório; `.opcional` em âmbar e `.ti` em cinza, com a borda tracejada |
| `.arquivos` com `.arquivo` | o que veio na pasta da entrega |
| `.passos` com `.passo` | o passo a passo: número num círculo vazado, `.corpo` e `.nota` em letra pequena. `.passo.so-pdf` tem o círculo âmbar e a `.marca-pdf`; `.passo.ia`, lilás |
| `.botao`, `.botao.principal` | o nome de um botão do programa, escrito como botão |
| `.etiqueta`, `.etiqueta.boa` | o que o passo pede (internet, administrador) |
| `.dois-lados` com `.lado` e `.lado.muda` | o que fica e o que muda ao atualizar |
| `.caminhos` com `.caminho` | quando a tela pode ser uma de duas |
| `.copiar` | caminho ou comando, sozinho na linha, para copiar |
| `.chave` com `.tipo`, e as marcas `.m-valido`, `.m-suspeito`, `.m-amao`, `.m-nega`, `.m-da-ia`, `.m-liberado` | o que cada cor quer dizer, com as mesmas marcas da tela de revisão |
| `.lembra` com `.item` e `.item.nao` | o que o programa lembra e o que não lembra |
| `.problemas` com `.problema` (âmbar), `.azul` e `.ia` | se algo der errado: o que a pessoa vê, e o que fazer |
| `.relatar` com a `.faixa-mini` | onde ver a versão: a faixa da esquerda em miniatura (190 px, o símbolo de 26 px, os três ícones, o marcado com o filete `#5b8fc9`), com a versão na moldura |

**Exceções ao resto deste documento**, aprovadas com o padrão:

- **Só o tema escuro, com uma versão clara para imprimir.** O roteiro nasceu
  escuro na 0.1.0, antes de o programa ter o tema claro, e é uma página que vai
  junto, e não uma tela do programa: a regra de desenhar nos dois temas não vale
  para ele.
- **Cores próprias**, fora da paleta: `#22262d` (a faixa do alto e a miniatura,
  entre o fundo e o fundo elevado), `#f0c674` (a letra da etiqueta da versão e da
  ressalva), `#5b8fc9` (os links e o filete da miniatura, um pouco mais claro que
  o `--cor-destaque-hover`) e as da capa (o degradê, `#8fc1f0`, `#d4d8de`,
  `#f0d9a8`, `#8fd6a6`). Desenhadas com a solicitante na 0.2.0, a partir dos
  documentos de outra frente da mesma consultoria.

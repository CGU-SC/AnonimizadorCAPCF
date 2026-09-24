# Sistema de design — Anonimizador CAPCF

Decidido em 03/09/2026, com a usuária, antes da primeira tela. Toda página do
projeto (mockup de tela ou página de relatório) segue isto.

## Identidade e tom

Identidade do zero, com cara institucional/UFSC sóbria — sem copiar a marca
oficial da UFSC (exigiria autorização de identidade visual). Tom neutro de
ferramenta de trabalho: direto, sem enfeite, para uso interno repetido no
dia a dia — não é produto comercial nem site institucional formal.

## Tema

**Só escuro por enquanto.** As cores são nomeadas por **papel** (`fundo`,
`texto`, `destaque`), nunca pelo nome da cor — é isso que permite acrescentar
o tema claro depois sem redesenhar nada: basta dar um segundo valor a cada
papel.

## Paleta (valores exatos)

| Papel | Valor (escuro) | Uso |
| --- | --- | --- |
| `--cor-fundo` | `#1e2228` | fundo da janela — cinza-grafite, nunca preto puro |
| `--cor-fundo-elevado` | `#262b33` | painéis, cartões, campos |
| `--cor-borda` | `#383e47` | divisórias, contorno de campo |
| `--cor-texto` | `#e8eaed` | texto principal |
| `--cor-texto-secundario` | `#9aa1ac` | legenda, texto de apoio |
| `--cor-destaque` | `#3b6ea5` | botão principal, item ativo do menu, links |
| `--cor-destaque-hover` | `#4f86bf` | estado de passar o mouse sobre o destaque |
| `--cor-sucesso` | `#4caf6d` | o que deu certo (arquivo gravado) — **não** marca CPF desde 14/09/2026. **Uma exceção, desde 17/09/2026:** o que a pessoa **liberou** na revisão é verde — o selo "N liberados por você", o número liberado no texto (com traço tracejado) e a etiqueta "liberado" na lista —, a pedido da usuária: marca uma decisão dela, e num documento com muitos liberados o cinza ficava difícil de achar depois. O traço tracejado é o que separa o liberado dos outros tipos para quem não distingue bem as cores |
| `--cor-alerta` | `#d9a441` | CPF **suspeito** — dígito verificador não bateu, indo para conferência humana. Traço ondulado. Entre 14 e 16/09/2026 marcou também o "forma CPF válido", que voltou ao vermelho |
| `--cor-erro` | `#d9534f` | falha (arquivo inválido, OCR não rodou), a faixa da caixa da dupla conferência de um número com forma CPF válido — o momento de risco — e, desde 16/09/2026, o **"forma CPF válido"** na revisão, com traço reto |
| `--cor-erro-texto` | `#f08a86` | letra em vermelho sobre o fundo escuro (contraste 6,6:1) — é este vermelho que marca o "forma CPF válido" no texto da revisão e o selo dele. O `#d9534f` tem 4:1 sobre o fundo e 3,6:1 sobre o fundo elevado, abaixo do mínimo de 4,5:1 para letra pequena |

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

Nenhum ainda. As páginas usam só o nome do programa em texto — nada de logo
inventado como se fosse definitivo.

## Layout de referência (janela do programa)

Menu lateral fixo à esquerda (largura ~220px, `--cor-fundo-elevado`), com os
itens "Gerar OCR" e "Anonimizar"; painel principal à direita, em `--cor-fundo`,
onde cada módulo mostra sua própria tela.

# Sistema de design — AnomizadorCAPCF

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
| `--cor-sucesso` | `#4caf6d` | CPF conferido / dígito verificador bateu |
| `--cor-alerta` | `#d9a441` | CPF suspeito — dígito verificador não bateu, indo para conferência humana |
| `--cor-erro` | `#d9534f` | falha (arquivo inválido, OCR não rodou) |

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

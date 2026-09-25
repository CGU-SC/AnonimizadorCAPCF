# Anonimizador CAPCF

Programa para a CAPCF (Coordenadoria de Análise de Prestações de Contas
Fundacionais da UFSC) tirar o CPF de documentos antes de eles irem para
assistentes de IA em chatbots convencionais. É o único dado desses documentos
considerado sensível para este uso — nome não é.

## O que ele faz

Dois módulos, usados em sequência:

1. **OCR** — quando o PDF não tem texto por dentro (documento escaneado ou
   impresso), lê o conteúdo com o motor Tesseract, local, sem mandar nada para
   fora da máquina.
2. **Anonimizador de CPF** — encontra todo CPF no texto (em qualquer formato de
   pontuação) e mascara os 3 primeiros e os 2 últimos dígitos, mantendo o
   resto do documento como está.

A saída é um arquivo `.md`, pronto para a pessoa arrastar para dentro da
conversa com um assistente de IA.

Feito sob medida para os formatos de documento que a CAPCF recebe de verdade —
não para documento genérico.

## Como instalar (desenvolvimento)

Pré-requisitos já resolvidos nesta máquina: Python 3.12 e o motor Tesseract OCR
(com o pacote de português).

Criar o ambiente virtual e instalar as dependências:

```
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Copiar `.env.example` para `.env` (os valores reais ficam só na sua máquina,
nunca no histórico).

Para abrir o programa, dois cliques em:

```
abrir\abrir-dev.bat
```

## Como gerar a entrega

Dois cliques em:

```
empacotar\gerar-entrega.bat
```

Ele roda os testes, monta o instalador e deixa em `builds\entrega-<versão>\`
o que vai para o núcleo: o instalador e o roteiro `Como instalar.html`. O que
ele precisa, e onde fica cada peça, está no `CLAUDE.md`.

## Onde ficam as coisas

Ver `CLAUDE.md` — é o contrato de trabalho do projeto, com a tabela de
comandos, as regras duras e o combinado com quem usa.

## Sobre os dados

Nenhum documento real de ninguém entra neste repositório, em lugar nenhum. Ver
`dados-exemplo/README.md`.

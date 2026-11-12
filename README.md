# Anonimizador CAPCF

Programa para a CAPCF (Coordenadoria de Análise de Prestações de Contas
Fundacionais da UFSC) tirar o CPF de documentos antes de eles irem para
assistentes de IA em chatbots convencionais. Roda numa janela própria, uma
pessoa por vez, na máquina de cada uma.

Desenvolvido pela CGU no âmbito da consultoria realizada à UFSC em 2026.

## Por onde começar

Abra `documentacao/manutencao.html` no navegador. É a documentação de
manutenção, num arquivo só, que abre sem internet: o que o programa faz, como
montar o ambiente, as regras de cada funcionalidade, a arquitetura, os testes,
o caminho de uma mudança, as armadilhas já conhecidas, como gerar a entrega e o
histórico das decisões.

## Em resumo

Dois módulos:

1. **Gerar OCR** — lê o PDF que não tem texto por dentro (documento escaneado
   ou impresso) com o PaddleOCR, o motor padrão, ou o Tesseract, na própria
   máquina, sem mandar nada para fora dela.
2. **Anonimizar** — acha o CPF em `.md`, `.txt`, PDF e `.docx`, em qualquer
   formato de pontuação, e mascara os 3 primeiros e os 2 últimos dígitos
   (`123.456.789-10` → `XXX.456.789-XX`), mantendo o resto do documento.

A saída é um arquivo `.md`, pronto para a pessoa arrastar para dentro da
conversa com o assistente de IA. Uma revisão por IA local, numa IA da própria
máquina ou de um servidor da rede da instituição, vem desligada e se liga em
Configurações.

## Comandos

Pede o Python 3.12 e, para os testes, o Tesseract com o pacote de português.
O passo a passo está na aba Ambiente da documentação.

| O quê | Comando |
| --- | --- |
| Criar o ambiente virtual | `python -m venv .venv` |
| Instalar as dependências | `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` |
| Rodar os testes | `.\.venv\Scripts\python.exe -m pytest` |
| Abrir o programa | `abrir\abrir-dev.bat` |
| Gerar a entrega | `empacotar\gerar-entrega.bat` |

Copie o `.env.example` para `.env`: o `.env` fica só na sua máquina, e nunca
entra no histórico.

## Sobre os dados

A massa de `dados-exemplo/` é inventada e gerada por script. Documento de
pessoa não entra neste repositório, em lugar nenhum. Ver
`dados-exemplo/README.md`.

# A conferir na tela

O que está construído, testado e **esperando o olho de quem usa**. Teste
automático não vê tela: ele garante o que o programa decide, não o que a pessoa
entende ao olhar.

Este arquivo existe porque uma etapa foi construída num dia em que a pessoa não
estava na frente da máquina (21/09/2026, pelo controle remoto). Conferido um
item, ele sai daqui.

## Etapa 8 — "Seguir para Anonimizar" no Gerar OCR

Construída e revisada pela lente crítica em 21/09/2026; **não conferida na tela**.

1. **Gerar OCR** → `dados-exemplo\01-com-texto-e-tabela.pdf` → "Aproveitar este
   texto" → **"Conferido"**.
   O que olhar: o cartão do Anonimizar fica **à esquerda, com o botão em
   destaque**, e o de salvar à direita, dizendo "— com os CPFs inteiros".
2. **"Seguir para Anonimizar"**.
   O que olhar: o menu passa a marcar "Anonimizar", a revisão abre com os
   números mascarados, e **nenhum arquivo novo aparece** na pasta do PDF.
3. Na revisão, **"Salvar o texto mascarado…"**.
   O que olhar: o caminho sugerido é `01-com-texto-e-tabela - sem CPF.md`, na
   pasta do PDF.
4. Sem salvar, clicar em **"Gerar OCR"** no menu.
   O que olhar: aparece a pergunta antes de descartar. Respondendo "Descartar e
   seguir", o Gerar OCR está na escolha da saída, **com o texto conferido lá**.
5. Ali, **"Escolher onde salvar"**.
   O que olhar: o aviso amarelo aponta para o "Seguir para Anonimizar" e para o
   item do menu, e **não** diz mais que o Anonimizar "ainda vai ser construído".
6. Caminho torto, com os dois módulos ocupados: deixe um PDF na **conferência do
   Anonimizar**, vá ao Gerar OCR, termine outro documento e clique em "Seguir
   para Anonimizar".
   O que olhar: a pergunta fala do documento que já estava no Anonimizar, e
   traz a linha "O texto que você mandou seguir continua no Gerar OCR,
   esperando."

## Critério de aceite que só se vê na tela

Da revisão 19, ainda sem relato:

- Anonimizar um arquivo, **fechar o programa, abrir de novo** e ir em
  "Anonimizar": a tela tem que estar na escolha do arquivo, sem lembrar nada do
  uso anterior (RN-19).

## O que não fica aqui

Etapa conferida na tela sai deste arquivo no mesmo dia. Ele não é lista de
tarefas do programa — o que falta construir está no
`especificacoes/backlog.md`.

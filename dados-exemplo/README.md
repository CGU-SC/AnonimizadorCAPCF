# Dados de exemplo

Esta pasta é só para massa **sintética ou irreversivelmente anonimizada** —
nunca documento real, nunca CPF de gente que existe, nem "só para testar
rápido". Arquivo commitado aqui e depois apagado continua no histórico do git
para sempre, em todo clone já feito do projeto.

## De onde estes arquivos vêm

Todos são **inventados e gerados por script**. Nenhum veio da CAPCF, de
processo nenhum, de pessoa nenhuma. Para refazer todos do zero, da raiz do
projeto:

```
.\.venv\Scripts\python.exe dados-exemplo\gerar-massa.py
```

O único CPF que aparece nos textos é `123.456.789-10`. Ele foi escolhido de
propósito com o dígito verificador **errado**: mesmo por acidente, ele não bate
com o CPF de ninguém.

## O que é cada um

| Arquivo | O que ele é | O que ele existe para testar |
| --- | --- | --- |
| `01-com-texto-e-tabela.pdf` | 3 páginas com texto de verdade por dentro, e uma tabela de despesas na última | o caminho do PDF que já tem texto: o programa oferece aproveitar ou ignorar. E a tabela saindo como tabela |
| `02-imprimir-para-pdf.pdf` | 12 páginas em que as letras são **desenho**, não texto — sem nada legível por dentro e sem nenhuma imagem de página guardada | o caso do "Imprimir para PDF" do Windows: o programa tem que tratar como documento sem texto e rodar o OCR. As 12 páginas também servem para ver a contagem andando e para dar tempo de cancelar |
| `03-conteudo-girado.pdf` | 1 página em pé, com o conteúdo deitado 90° dentro dela, e o campo de rotação do PDF zerado | o programa não pode confiar no campo de rotação: só olhando a imagem ele descobre que está deitado e endireita antes de ler |
| `04-texto-embaralhado.pdf` | tem texto por dentro, mas o texto é lixo ilegível | o programa não julga se o texto presta: mostra as primeiras linhas e quem olha decide ignorar e ler as imagens |
| `05-corrompido.pdf` | começa como PDF e termina no meio, sem fechar | arquivo que não abre: o programa explica em uma frase e volta, sem travar |
| `06-protegido-por-senha.pdf` | PDF cifrado (a senha é `senha-de-teste`) | outro jeito de o arquivo não abrir |

## Uma observação honesta sobre o `04`

O documento de verdade que motivou esse caso tem a tabela de caracteres
quebrada por dentro — coisa que acontece quando o documento já passou por um
OCR ruim antes. O arquivo daqui não reproduz esse defeito por dentro: ele
simplesmente carrega um texto que é lixo. Para o programa dá no mesmo, porque
o que ele faz é mostrar as primeiras linhas e deixar a pessoa decidir.

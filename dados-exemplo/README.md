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

O único CPF que aparece nos PDFs é `123.456.789-10`. Ele foi escolhido de
propósito com o dígito verificador **errado**: mesmo por acidente, ele não bate
com o CPF de ninguém. A massa de texto do Anonimizar tem outros números, todos
com a mesma garantia — veja a seção dela, mais abaixo.

## O que é cada um

| Arquivo | O que ele é | O que ele existe para testar |
| --- | --- | --- |
| `01-com-texto-e-tabela.pdf` | 3 páginas com texto de verdade por dentro, e uma tabela de despesas na última | o caminho do PDF que já tem texto: o programa oferece aproveitar ou ignorar. E a tabela saindo como tabela |
| `02-imprimir-para-pdf.pdf` | 12 páginas em que as letras são **desenho**, não texto — sem nada legível por dentro e sem nenhuma imagem de página guardada | o caso do "Imprimir para PDF" do Windows: o programa tem que tratar como documento sem texto e rodar o OCR. As 12 páginas também servem para ver a contagem andando e para dar tempo de cancelar |
| `03-conteudo-girado.pdf` | 1 página em pé, com o conteúdo deitado 90° dentro dela, e o campo de rotação do PDF zerado | o programa não pode confiar no campo de rotação: só olhando a imagem ele descobre que está deitado e endireita antes de ler |
| `04-texto-embaralhado.pdf` | tem texto por dentro, mas o texto é lixo ilegível | o programa não julga se o texto presta: mostra as primeiras linhas e quem olha decide ignorar e ler as imagens |
| `05-corrompido.pdf` | começa como PDF e termina no meio, sem fechar | arquivo que não abre: o programa explica em uma frase e volta, sem travar |
| `06-protegido-por-senha.pdf` | PDF cifrado (a senha é `senha-de-teste`) | outro jeito de o arquivo não abrir |
| `07-carimbo-lateral.pdf` | 2 páginas com o número do processo **carimbado de lado** na margem, como sai de sistema de processos | o carimbo tem palavras espalhadas verticalmente, e isso já quebrou a remontagem do texto: as linhas do corpo saíam fundidas e intercaladas. Entrou na massa em 11/09/2026, depois do defeito |

## A massa de texto com CPF, do Anonimizar

Os arquivos de `10` a `16` são outra massa, gerada por outro script, para o
módulo Anonimizar (spec 003). Para refazê-los, da raiz do projeto:

```
.\.venv\Scripts\python.exe dados-exemplo\gerar-massa-cpf.py
```

Ficam num script à parte para não regravar os PDFs a cada vez (veja o fim deste
arquivo). Diferente dos PDFs, estes saem idênticos toda vez que o script roda.

**Nenhum número desta massa pode ser de alguém** (regra RN-22 da spec 003):

- os que **passam na conta** do dígito verificador são **só de dígitos
  repetidos** — `111.111.111-11`, `222.222.222-22`, `44444444444`… —, que a
  Receita não emite;
- os **suspeitos** falham na conta: `123.456.789-10`, `777.777.777-78`,
  `333.333.333/34`, `246 813 579 12`;
- os **"quase CPF"** falham na conta mesmo com as letras trocadas de volta por
  dígitos (`l23.456.789-1O`), ou partem de dígitos repetidos
  (`l11.111.111-11`, `555.555.` / `555-55` partido em duas linhas,
  `666 666 666 66`).

Cuidado com número "de sequência" inventado na hora: nem todo falha na conta,
e um que passe pode ser o CPF de alguém. Por isso nenhum número que passa na
conta é escrito nesta pasta, nem como exemplo do que evitar. Um teste automático
(`programa/test_cpf.py`) varre esta pasta inteira e falha se aparecer número
que passa na conta sem ser de dígitos repetidos.

| Arquivo | O que ele é | O que ele existe para testar |
| --- | --- | --- |
| `10-prestacao-com-cpf.md` | a prestação de contas do rascunho de tela 01 do Anonimizar, com tabela de bolsistas e observações da análise | todos os tipos de uma vez: forma CPF válido nos quatro formatos, falha na conta, os três jeitos de "quase CPF" (letra, espaços, partido em duas linhas), o "quase CPF" que passa na conta, três e quatro letras com pontuação (mascaram, quarta emenda), e as quatro que não são CPF por regra: três letras sem pontuação (`l234S67891O`), cinco letras com pontuação (`lZ3.4S6.7B9-1O`), letras que não se confundem com dígito (`SOL.IDA.DES-OS`) e o número colado a outro dígito; mais CNPJ, processo e boleto (ficam inteiros), e o `1234 5678 910` para mascarar à mão |
| `10-prestacao-com-cpf - sem CPF.md` | o mesmo documento já mascarado, com o nome que o programa dá ao arquivo que grava | um arquivo já anonimizado, aberto de novo: "nenhum CPF encontrado" |
| `11-sem-cpf.md` | ata de reunião com CNPJ, processo e valores, e nenhum CPF | a revisão sem CPF, com o aviso e o salvar liberado |
| `12-acentos-bloco-de-notas-atual.txt` | texto com acentos, gravado como o Bloco de Notas grava hoje, com a quebra de linha do Windows | os acentos certos no jeito de hoje |
| `13-acentos-bloco-de-notas-antigo.txt` | o mesmo texto, gravado no padrão antigo do Windows em português | os acentos certos no jeito antigo (RN-21) |
| `14-folha-com-40-bolsistas.md` | tabela de 40 bolsistas, metade com CPF de forma válida e metade falhando na conta | a lista ao lado da revisão com muitos itens, e a tabela alinhada depois da máscara |
| `15-vazio.md` | arquivo vazio | o erro de arquivo vazio, que volta à escolha |
| `16-planilha-renomeada.md` | bytes de planilha com o nome trocado para `.md` | o erro de arquivo que não é texto |

## Uma observação honesta sobre o `04`

O documento de verdade que motivou esse caso tem a tabela de caracteres
quebrada por dentro — coisa que acontece quando o documento já passou por um
OCR ruim antes. O arquivo daqui não reproduz esse defeito por dentro: ele
simplesmente carrega um texto que é lixo. Para o programa dá no mesmo, porque
o que ele faz é mostrar as primeiras linhas e deixar a pessoa decidir.

## Por que os PDFs "mudam" ao serem gerados de novo

Rodar o script outra vez faz o git acusar que quase todos os arquivos mudaram,
mesmo sem ninguém ter mexido em nada. É esperado, e não é defeito: todo PDF
carrega uma marca única gerada na hora de gravar, os que o Qt escreve guardam
também a data e a hora, e o protegido por senha é cifrado com uma chave nova a
cada vez.

O documento em si continua idêntico — mesmas páginas, mesmo texto, mesma
aparência. Então **não vale a pena commitar essa troca de bytes**: ela suja o
histórico sem registrar mudança nenhuma. Gerou de novo e o conteúdo é o mesmo?
Descarte as alterações dos PDFs e commite só o que mudou de verdade.

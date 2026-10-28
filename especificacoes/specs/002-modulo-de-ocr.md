# Spec 002 — Módulo de OCR

**Status:** aprovada — a emenda de 2026-10-18 (funcionalidade 7) também,
no mesmo dia
**Data:** 2026-09-09
**Emendada em:** 2026-09-11 — acrescentados os controles de tamanho da tela de
conferência (escopo, RN-23, RN-24, dois critérios de aceite e um item de
fora-de-escopo). O buraco apareceu construindo a etapa 3: a spec mandava
construir uma tela para conferência humana e não dizia que a pessoa precisa
conseguir enxergar o documento.
**Emendada em:** 2026-09-12 — a premissa do instalador ganha lugar definido
(a pasta `instaladores`, ao lado do programa), a RN-19 diz que apontar a pasta
vale só com o programa aberto e que a TI pode gravar o caminho no `.env`, e o
link de download entra no fora-de-escopo. Os três buracos apareceram ao começar
a etapa 7.
**Emendada em:** 2026-09-13 — o motor só conta como encontrado com o pacote de
português junto (RN-19 e o caminho torto do Tesseract). O buraco apareceu na
revisão da etapa 7: instalado sem o português, o aviso sumia e toda leitura de
documento escaneado falhava sem dizer por quê.
**Emendada em:** 2026-10-18 — o PaddleOCR entra na escolha do motor, primeiro e
já marcado, com o Tesseract como alternativa (funcionalidade 7 do backlog). Está
inteira na seção "Emenda de 18/10/2026", no fim; os trechos de antes que ela
muda trazem a remissão a ela. Veio da medição da conferência 02: com a mesma
massa, o Tesseract deixaria 42 de 60 CPFs saírem sem máscara, porque pula tabela
com grade, e os modelos do PaddleOCR deixariam de 1 a 5.
**Emendada em:** 2026-10-28 (aprovada no mesmo dia) — o motor marcado passa a ser lembrado
de um uso para o outro, um por módulo (funcionalidade 8 do backlog). Está
inteira na seção "Emenda de 28/10/2026", no fim; ela emenda a RN-22 e a RN-26,
que trazem a remissão. A RN-22 foi feita para o programa não lembrar o
**trabalho** (documento, texto lido, pasta), e isso continua proibido; a escolha
da pessoa é outra categoria, e passa a ser lembrada. Levantamento em
`mockups/requisitos/07-mapa-do-entendimento.html`.

## Objetivo

Transformar um PDF da CAPCF em texto conferido por uma pessoa, para que esse
texto possa seguir para o Anonimizador de CPF ou ser salvo como `.md`. É o
módulo que resolve o caso em que o documento não tem texto legível por dentro:
documento impresso, anexo escaneado por terceiro, ou documento passado pelo
"Imprimir para PDF" do Windows, que transforma as letras em desenho.

## Escopo

- Ocupar o painel do item "Gerar OCR" do menu lateral, no lugar do aviso de
  "ainda não construído" da spec 001.
- Escolher um PDF da máquina.
- Escolher o motor de leitura, entre dois itens: **"Tesseract (nesta máquina)"**,
  funcionando, e **"IA local da UFSC"**, visível e desligada, com a explicação
  de que depende de servidor que a TI ainda vai montar. *(Passam a ser três
  itens, com o PaddleOCR primeiro e marcado — emenda de 18/10/2026, RN-25.)*
- Detectar, por verificação exata, se o PDF já tem camada de texto por dentro.
- Havendo camada de texto: mostrar as primeiras linhas dela na tela e deixar a
  pessoa escolher entre aproveitar esse texto ou ignorá-lo e ler as imagens.
- Não havendo camada de texto: desenhar cada página como imagem e ler com o
  Tesseract, endireitando automaticamente a página cujo conteúdo esteja girado.
  *(Lê com o motor marcado, que por padrão é o PaddleOCR — emenda de
  18/10/2026, RN-26 e RN-28.)*
- Mostrar o andamento durante a leitura, com a contagem de páginas e a
  possibilidade de cancelar.
- Remontar como tabela de texto o que era tabela no documento, nos dois
  caminhos.
- **Tela de conferência**: o PDF de um lado, o texto do outro, andando juntos
  página a página, com o texto editável ali mesmo.
- Duas saídas depois de conferido: salvar o texto como `.md`, ou seguir para o
  módulo Anonimizar levando o texto por dentro do programa.
- Antes de salvar, mostrar o caminho de destino já preenchido, com a opção de
  trocar, e perguntar antes de escrever por cima de um arquivo existente.
- Avisar, ao abrir o módulo, quando o Tesseract não estiver instalado na
  máquina, **já oferecendo a instalação assistida no próprio aviso** — sem
  esperar a pessoa escolher um documento para descobrir que falta uma peça.
- Na tela de conferência, **controles de tamanho**: aumentar e diminuir a
  página do documento à esquerda, e aumentar e diminuir a letra do texto à
  direita. Sem eles, a página encolhida para caber em meia tela mostra o texto
  do documento com cerca de 6 pixels por letra — pequeno demais para a
  conferência que esta tela existe para permitir.

## Fora de escopo

- **Qualquer coisa a ver com CPF.** Este módulo não procura, não valida, não
  mascara e não lista CPF suspeito. Ele entrega texto; o que é CPF e o que se
  faz com ele é inteiramente do item 3 do backlog. A conferência humana que
  acontece aqui é sobre a **fidelidade da leitura**, não sobre dado sensível.
- **A leitura por IA local.** O item aparece na tela desligado. Fazer ele
  funcionar — conexão com o LM Studio ou com o servidor da TI, endereço, token,
  teste de conexão — é funcionalidade própria, item novo no backlog, com spec
  própria e decisão técnica anterior pela `skill-03-arquiteto-de-solucao`.
- **Separar um PDF que traz vários documentos dentro.** Entra um, sai um.
- **Processar vários PDFs de uma vez.** Um documento por vez.
- **Saída em qualquer formato que não seja `.md`** — nada de XLSX, DOCX ou PDF.
- **Corrigir o PDF de origem.** O programa nunca escreve no PDF que recebeu.
- **Guardar histórico do que foi processado.** Nada fica gravado entre um uso e
  outro: nem lista de documentos, nem texto, nem preferência.
- **Reconhecer letra manuscrita.** O Tesseract não faz isso de forma confiável,
  e prometer seria enganar quem usa.
- **Empacotar o instalador do Tesseract junto do programa.** A spec exige que o
  instalador esteja disponível na máquina; como ele chega lá é decisão da
  `skill-11-gerente-de-entrega`, no dia da entrega.
- **Girar a página na tela de conferência**, e qualquer edição do documento
  original. O programa nunca escreve no PDF que recebeu (RN-17).
- **Link para baixar o Tesseract dentro do programa.** O módulo não tem nenhum
  endereço de internet, e é isso que permite provar, numa busca só, que ele
  nunca fala com a internet (critério 22). O link vai para o documento de
  instalação da TI, que se atualiza sem gerar programa novo.

## Premissas

- premissa: a entrada é sempre PDF — às vezes com texto por dentro (exportado do
  sistema de processos da UFSC), às vezes só imagem (impresso, ou anexo
  escaneado por terceiro).
- premissa: o programa detecta sozinho se há texto por dentro e só roda o OCR
  quando não há — isso é verificação exata, não palpite. Julgar se esse texto
  *presta* é outra coisa, e essa fica com a pessoa (RN-4).
- premissa: o motor desta versão é o Tesseract instalado na máquina, com o
  pacote de português. A LLM/IA local aparece no menu mas está fora do escopo
  desta versão. Nunca um serviço de empresa externa. *(Desde a emenda de
  18/10/2026, o motor padrão é o PaddleOCR, que vai dentro do programa; o
  Tesseract continua como alternativa.)*
- premissa: a saída `.md` preserva as tabelas do documento original como tabelas
  de texto.
- premissa: PDF grande com vários documentos dentro entra como um documento só e
  sai como um `.md` só. Separar por dentro é melhoria futura.
- premissa: a conferência humana é parte fixa do processo quando o texto veio de
  OCR, e não etapa opcional.
- premissa: as máquinas do núcleo são Windows.
- premissa: o instalador do Tesseract estará disponível na máquina para o botão
  "instalar agora" abrir, **numa pasta chamada `instaladores`, ao lado do
  programa**. Deixá-lo ali é combinado com o dia da entrega. Não estando, o
  botão fica apagado e o passo a passo escrito diz para procurar a TI.

## Fluxos

### Fluxo normal — PDF escaneado, sem texto por dentro

1. A pessoa clica em "Gerar OCR" no menu lateral.
2. O painel mostra a área para escolher o PDF e a escolha do motor, com
   "Tesseract (nesta máquina)" já marcado.
3. Ela escolhe o PDF (pelo botão, ou arrastando o arquivo para dentro da área).
4. O programa confere se há camada de texto. Não há.
5. O programa desenha cada página como imagem, endireita a que estiver girada e
   manda para o Tesseract, mostrando "página 7 de 12" e uma barra que avança.
6. Terminada a leitura, abre a tela de conferência: o PDF à esquerda, o texto
   lido à direita, na mesma página.
7. Ela rola as duas metades, compara, e corrige no texto o que o motor errou.
8. Ela clica em "conferido".
9. O programa oferece as duas saídas: "salvar o texto como está" e "seguir para
   o Anonimizar".
10. Escolhendo salvar, o programa mostra o caminho de destino já preenchido —
    a mesma pasta do PDF, o mesmo nome, terminação `.md` — com a opção de
    trocar, e um aviso de que esse arquivo sai com os CPFs inteiros.
11. Ela confirma. O arquivo é gravado e a tela diz onde, com um botão para abrir
    a pasta.

### Fluxo alternativo — PDF que já tem texto por dentro

4a. O programa encontra camada de texto.
4b. A tela mostra o aviso "este PDF já tem texto por dentro" junto com as
    primeiras linhas desse texto, e duas saídas: **"aproveitar este texto"** ou
    **"ignorar e ler as imagens"**.
4c. Escolhendo aproveitar, o programa pula a leitura por imagem e vai direto
    para a tela de conferência (passo 6), com o texto que já estava lá.
4d. Escolhendo ignorar, segue o fluxo normal a partir do passo 5.

### Caminho torto — a camada de texto está embaralhada

O PDF tem texto por dentro, mas ele foi gravado com o mapeamento de caracteres
quebrado, e sai como lixo. Isso acontece em documento que já passou por um OCR
ruim antes. O programa não julga: ele mostra as primeiras linhas no passo 4b, a
pessoa reconhece o lixo num olhar, escolhe "ignorar e ler as imagens", e o
documento segue pelo caminho do OCR.

### Caminho torto — o Tesseract não está instalado

*Desde a emenda de 18/10/2026, o que vem abaixo vale quando **nenhum** dos dois
motores funciona. Faltando só o Tesseract, com o PaddleOCR funcionando, o aviso
do alto e a tela cheia não aparecem: a falta é dita na própria escolha do motor
(RN-30).*

- Ao abrir o módulo, o programa procura o Tesseract e não acha. Um aviso aparece
  no alto do painel dizendo que o motor de leitura não foi encontrado e que
  documentos escaneados não vão funcionar — **e esse aviso já traz o que fazer a
  respeito**: o botão **"instalar agora"** (que abre o instalador e deixa a
  pessoa clicar "Sim" na confirmação do Windows), o botão **"conferir de novo"**
  e o lugar para apontar a pasta, caso a TI já tenha instalado fora do lugar
  padrão.
- A pessoa resolve o problema ali, antes de escolher documento nenhum. Fazer
  ela arrastar um PDF para só então descobrir que falta uma peça é gastar o
  tempo dela para dar uma notícia que já se sabia ao abrir a tela.
- O módulo continua servindo para PDF que já tem texto por dentro, porque esse
  caminho não usa o motor. O aviso não bloqueia nada.
- Se ela ignorar o aviso e escolher mesmo assim um PDF sem texto, a tela cheia
  repete a explicação e as mesmas três saídas, agora sem ter o que fazer além
  disso.
- O Tesseract instalado **sem o pacote de português** conta como motor
  faltando: o aviso e a tela cheia aparecem do mesmo jeito, com as mesmas três
  saídas, mas dizendo que o que falta é o pacote — e pedindo à TI que instale
  de novo, marcando o português na lista de idiomas.

### Caminho torto — a pessoa cancela no meio

Ela clica em "cancelar" durante a leitura. O programa para na página em que
está, descarta o que leu e volta para a tela de escolher o PDF. Nada foi
gravado, porque nada é gravado antes da conferência.

### Caminho torto — o arquivo não abre

O PDF está corrompido, protegido por senha, ou não é um PDF apesar da
terminação. O programa mostra o que houve em uma frase, sem termo técnico, e
volta para a tela de escolher o arquivo.

### Caminho torto — já existe arquivo com aquele nome

No passo 11, o programa vê que o `.md` de destino já existe. Pergunta antes:
escrever por cima, ou salvar com outro nome. Nunca sobrescreve calado.

### Caminho torto — ela quer seguir para o Anonimizar, que ainda não existe

O botão "seguir para o Anonimizar" fica apagado enquanto o item 3 do backlog não
estiver construído, com a explicação de que esse módulo ainda vai ser feito. A
saída "salvar o texto como está" continua disponível.

## Dados

Não há banco e não há nada guardado entre um uso e outro — cada documento é
processado sozinho e o programa esquece tudo ao fechar. O que existe é o que
vive na memória durante o uso:

| Informação | De onde vem | Obrigatória | Observação |
| --- | --- | --- | --- |
| caminho do PDF escolhido | a pessoa (botão ou arrastar) | sim | tem que existir, ser legível e abrir como PDF |
| motor escolhido | a pessoa (escolha na tela) | sim | só "Tesseract" é escolhível nesta versão *(PaddleOCR ou Tesseract desde a emenda de 18/10/2026 — ver os Dados da emenda)* |
| tem camada de texto? | verificação no PDF | derivado | sim/não, verificação exata |
| origem do texto | derivado | sim | "camada do PDF" ou "OCR" — decide o aviso da tela de conferência |
| texto lido, página a página | PyMuPDF ou Tesseract | sim | fica separado por página, que é o que permite a rolagem casada |
| texto depois da edição | a pessoa, na conferência | sim | é este que vai para o arquivo ou para o Anonimizar |
| caminho de destino | sugerido pelo programa, alterável | sim, na hora de salvar | padrão: mesma pasta e mesmo nome do PDF, terminação `.md` |

O `.env` não é usado neste módulo: não há segredo nenhum aqui. Ele passa a ser
usado quando a IA local entrar, em spec própria.

## Estados da interface

- **vazio:** o painel mostra a área para escolher o PDF (botão e "arraste aqui")
  e a escolha do motor, com "Tesseract (nesta máquina)" marcado e "IA local da
  UFSC" apagada. É o estado de quando ela clica em "Gerar OCR".
- **vazio, com o motor faltando:** o mesmo painel, mais o aviso no alto — e o
  aviso já traz "instalar agora", "conferir de novo" e o lugar para apontar a
  pasta. A área de escolher o PDF continua funcionando.
- **conferindo o arquivo:** o programa acabou de receber o PDF e está vendo se
  há camada de texto. Dura um instante; a tela mostra que está trabalhando.
- **decidindo o que fazer com a camada de texto:** só aparece quando há texto por
  dentro. Mostra o aviso, as primeiras linhas, e as duas saídas.
- **carregando (lendo):** barra que avança, "página 7 de 12", nome do arquivo, e
  o botão de cancelar. É o estado que pode durar minutos.
- **com dados (conferência):** a tela dividida — PDF à esquerda, texto editável à
  direita, na mesma página —, um aviso dizendo se o texto veio de OCR ou da
  camada do PDF, os controles de tamanho de cada metade, e o botão "conferido".
- **escolhendo a saída:** as duas saídas lado a lado, com o botão do Anonimizar
  apagado enquanto aquele módulo não existir.
- **salvando:** o caminho de destino preenchido, editável, o aviso de que o
  arquivo sai com os CPFs inteiros, e a confirmação.
- **sucesso:** a mensagem de onde o arquivo foi gravado, com o botão de abrir a
  pasta e o de processar outro documento.
- **erro:** uma frase dizendo o que houve, em linguagem comum, e o caminho de
  volta. Vale para arquivo que não abre, motor não encontrado, e falha durante a
  leitura.

## Regras de negócio

- RN-1: o módulo trabalha um documento por vez. Escolher outro PDF descarta o
  que estava em andamento, perguntando antes quando houver texto ainda não
  salvo.
- RN-2: nada é gravado em disco antes de a pessoa escolher salvar. Cancelar,
  fechar ou trocar de documento não deixa arquivo nenhum para trás.
- RN-3: a verificação de camada de texto é exata — o programa lê o PDF e conta
  os caracteres que existem. Não há estimativa nem palpite nessa decisão.
- RN-4: havendo camada de texto, o programa **nunca decide sozinho** se ela
  presta. Ele mostra as primeiras linhas e a escolha é da pessoa. Julgar
  qualidade de texto é palpite, e palpite errado aqui produz um `.md` de lixo
  que ninguém percebe.
- RN-5: não havendo camada de texto, o programa desenha cada página como imagem
  e lê essa imagem. Vale inclusive para PDF gerado pelo "Imprimir para PDF", em
  que as letras viraram desenho vetorial e não há imagem de página nenhuma
  guardada dentro do arquivo.
- RN-6: antes de ler cada página, o programa detecta a orientação do conteúdo e
  endireita a página que estiver girada. O campo de rotação do PDF não serve
  para isso: um documento deitado dentro de uma página em pé tem esse campo
  zerado, e só a detecção em cima da imagem pega o caso. *(Com o PaddleOCR, quem
  detecta é o detector do Tesseract, quando ele está instalado — RN-28.)*
- RN-7: a página é desenhada a 300 pontos por polegada. É a densidade que o
  Tesseract recomenda para texto impresso — abaixo disso ele erra mais, acima
  fica mais lento sem ganhar precisão.
- RN-8: o texto lido fica separado por página, porque é isso que permite a
  rolagem casada da tela de conferência.
- RN-9: a rolagem casada funciona **por página**, não linha a linha. Estando na
  página 12 à esquerda, o texto da página 12 aparece à direita.
- RN-10: o que era tabela no documento sai como tabela de texto no `.md`, nos
  dois caminhos — o da camada de texto e o do OCR.
- RN-11: **nenhum aviso do programa entra dentro do arquivo de saída.** O `.md`
  tem o texto do documento e mais nada. Recado no meio do texto não é lido por
  ninguém e ainda viaja para dentro da conversa com o assistente de IA, onde
  vira ruído. O aviso de que a leitura é incerta vive na tela de conferência,
  antes de o arquivo existir.
- RN-12: a conferência humana é passo obrigatório e não tem como ser pulada. A
  tela de conferência aparece nos dois caminhos, inclusive quando a pessoa
  aproveitou a camada de texto do PDF.
- RN-13: o texto é editável na tela de conferência. A correção acontece aqui
  porque é o único momento em que ela é barata: depois, o erro já está dentro de
  um arquivo que foi para a conversa com a IA.
- RN-14: o arquivo `.md` que sai deste módulo **tem os CPFs inteiros**. A tela
  diz isso com todas as letras antes de gravar.
- RN-15: o caminho de destino aparece preenchido e editável **antes** de gravar.
  O padrão é a mesma pasta e o mesmo nome do PDF, com terminação `.md`.
- RN-16: existindo arquivo com aquele nome no destino, o programa pergunta antes
  de escrever por cima. Nunca sobrescreve calado.
- RN-17: o programa nunca escreve, altera ou apaga o PDF de origem.
- RN-18: o módulo não procura, não valida, não mascara e não lista CPF. Isso é
  inteiramente do item 3 do backlog.
- RN-19: o programa procura o Tesseract ao abrir o módulo, e o aviso de que ele
  falta **já vem com a saída junto** — instalar, conferir de novo, ou apontar a
  pasta. Quem usa não precisa escolher um documento para descobrir que falta uma
  peça: o programa já sabia disso ao abrir a tela. O aviso não bloqueia nada, e
  o caminho do PDF que já tem texto continua funcionando. Apontar a pasta vale
  enquanto o programa estiver aberto — nada é guardado entre um uso e outro
  (RN-22). Para valer sempre naquela máquina, a TI grava o caminho uma vez no
  `.env` da instalação, na variável `TESSERACT_CAMINHO`. O motor só conta
  como encontrado **com o pacote de português junto**: sem ele toda leitura
  falha, e o aviso aparece do mesmo jeito, dizendo que é o pacote que falta.
- RN-20: o programa **nunca baixa nem instala nada sozinho** e nunca manda
  documento para lugar nenhum. O botão "instalar agora" abre um instalador que
  já está na máquina, e a confirmação do Windows é clicada por uma pessoa.
- RN-21: o item "IA local da UFSC" aparece na escolha de motor, apagado, com a
  explicação de que depende de servidor que a TI ainda vai montar. Não há, neste
  módulo, nenhum código que converse com motor remoto.
- RN-22: nada é guardado entre um uso e outro — nem histórico, nem preferência
  de motor, nem última pasta usada. *(A emenda de 18/10/2026 não mexe nesta
  regra: o PaddleOCR vir marcado é o padrão escrito no programa, e não uma
  preferência guardada — RN-26.)* *(Emendada em 28/10/2026: a **preferência de
  motor** passa a ser lembrada, um por módulo — RN-36. Todo o resto continua
  proibido: nada do **trabalho** é guardado — documento, texto lido, pasta
  usada, histórico, achados, nem o tamanho de letra e de página da
  conferência — RN-40.)*
- RN-23: a página do documento, na conferência, tem controles de **−** e **+**,
  indo de 50% a 400%, mais um botão que volta ao tamanho que cabe na largura. O
  tamanho escolhido **vale para as páginas seguintes** enquanto o mesmo
  documento estiver aberto: quem aumentou para conseguir ler não quer reajustar
  a cada página.
- RN-24: a letra do texto lido também tem **−** e **+**, de 10 a 22 pixels.
  Mudar o tamanho da letra **não altera o texto** — é só como ele aparece na
  tela, e nada disso vai para o arquivo salvo. Pela RN-22, nenhum dos dois
  tamanhos sobrevive a fechar o programa.

## Critérios de aceite

- Dado um PDF sem camada de texto, quando a pessoa o escolhe e o Tesseract está
  instalado, então o programa desenha as páginas, lê, e ao fim abre a tela de
  conferência com o PDF de um lado e o texto do outro.
- Dado um PDF gerado pelo "Imprimir para PDF" do Windows (letras viradas em
  desenho vetorial, nenhum texto e nenhuma imagem de página guardada), quando
  ele é escolhido, então o programa o trata como documento sem texto e lê pelo
  OCR — não mostra a tela de "este PDF já tem texto".
- Dado um PDF com camada de texto, quando ele é escolhido, então a tela mostra o
  aviso e as primeiras linhas desse texto, com as opções "aproveitar este texto"
  e "ignorar e ler as imagens", e nenhuma leitura por imagem começou ainda.
- Dado que a pessoa escolheu "ignorar e ler as imagens", quando a leitura
  termina, então o texto exibido na conferência é o do OCR, e não o da camada
  original.
- Dado um PDF cujo conteúdo está girado 90° dentro de uma página em pé (o campo
  de rotação do PDF zerado), quando o OCR roda, então o texto sai na leitura
  correta e não como sequência de caracteres soltos.
- Dado um PDF de 12 páginas em leitura, quando o programa está na sétima, então
  a tela mostra "página 7 de 12" e a barra na proporção correspondente.
- Dado que a leitura está em andamento, quando a pessoa clica em "cancelar",
  então o programa volta para a tela de escolher o PDF e nenhum arquivo foi
  gravado em disco.
- Dado um documento com tabela, quando o texto é gerado por qualquer um dos dois
  caminhos, então a tabela aparece no `.md` como tabela de texto, com as colunas
  separadas.
- Dado o texto na tela de conferência, quando a pessoa altera uma palavra e
  clica em "conferido", então o que segue para o arquivo (ou para o Anonimizar)
  é o texto já com a alteração.
- Dado que a pessoa está na página 12 do PDF na metade esquerda, então a metade
  direita mostra o texto da página 12.
- Dado que a pessoa escolheu "salvar o texto como está", quando a tela de salvar
  aparece, então o caminho de destino já vem preenchido com a pasta e o nome do
  PDF e terminação `.md`, é editável, e há o aviso de que o arquivo sai com os
  CPFs inteiros.
- Dado que já existe um arquivo com o nome de destino, quando ela confirma o
  salvamento, então o programa pergunta antes de escrever por cima.
- Dado que o arquivo foi gravado, quando a tela de sucesso aparece, então ela
  mostra o caminho onde gravou e um botão que abre aquela pasta.
- Dado que o arquivo foi gravado, quando ele é aberto, então ele contém o texto
  do documento e nenhuma linha de aviso escrita pelo programa.
- Dado que o PDF de origem é comparado antes e depois de todo o processo, então
  ele está idêntico.
- Dado que o Tesseract não está instalado, quando a pessoa abre o módulo, então
  o aviso aparece no alto do painel **já com os botões "instalar agora" e
  "conferir de novo" e o lugar para apontar a pasta**, antes de qualquer
  documento ser escolhido, e o módulo continua aceitando um PDF.
- Dado que o Tesseract não está instalado e a pessoa ignorou o aviso do topo,
  quando ela escolhe um PDF sem camada de texto, então a tela cheia repete a
  explicação e as mesmas três saídas.
- Dado que o Tesseract não está instalado, quando a pessoa escolhe um PDF que
  tem camada de texto, então o caminho segue normalmente até a conferência.
- Dado que o Tesseract foi instalado com o programa aberto, quando ela clica em
  "conferir de novo", então o aviso some e o módulo passa a aceitar documento
  escaneado, sem precisar fechar e abrir o programa.
- Dado um arquivo corrompido, protegido por senha, ou que não é PDF, quando ele
  é escolhido, então o programa explica o que houve em uma frase e volta para a
  tela de escolher o arquivo, sem travar.
- Dado que o módulo 3 ainda não foi construído, quando a pessoa chega à escolha
  da saída, então o botão "seguir para o Anonimizar" está apagado com a
  explicação, e "salvar o texto como está" funciona.
- Dado o código deste módulo inteiro, quando se procura por endereço de internet
  ou chamada a serviço remoto, então não há nenhum.
- Dado o código deste módulo inteiro, quando se procura por validação, máscara
  ou lista de CPF, então não há nenhuma.
- Dado que a pessoa fecha e reabre o programa, quando ela volta ao módulo, então
  a tela está no estado inicial: nenhum documento, nenhuma pasta lembrada,
  nenhum histórico.
- Dado que a pessoa aumentou a página do documento e virou de página, então a
  página nova aparece no mesmo tamanho que ela escolheu.
- Dado que a pessoa mudou o tamanho da letra do texto, quando o arquivo é salvo,
  então o conteúdo dele é exatamente o mesmo — o tamanho da letra é só da tela.

## Questões em aberto

Nenhuma.

---

## Emenda de 18/10/2026 — o PaddleOCR na escolha do motor

**Funcionalidade 7 do backlog.** Levantamento detalhado fechado em 18/10/2026
(`mockups/requisitos/03-mapa-do-entendimento.html`), depois da medição
(`conferencias/02-os-motores-de-leitura.html`). Escolha técnica aprovada em
16/10/2026: os modelos do PaddleOCR rodados pelo RapidOCR, com o modelo pequeno.

### Objetivo da emenda

Ler melhor a página em que o Tesseract lê pior — tabela com grade, página torta,
contraste fraco — e, com isso, deixar escapar menos CPF. Na medição, com as
mesmas páginas, o Tesseract pulou tabelas com grade inteiras, mesmo limpas.

### Escopo da emenda

- A escolha do motor passa a ter **três itens, nesta ordem**: "PaddleOCR (nesta
  máquina)", **já marcado**; "Tesseract (nesta máquina)"; e a "IA local",
  apagada, como hoje.
- Embaixo do PaddleOCR e do Tesseract, **uma linha de resumo** com o que cada um
  faz melhor e quanto leva por página.
- **O motor marcado é o que lê.** Hoje a escolha não decide nada — o programa
  sempre chama o Tesseract. O ponto em que o programa escolhe entre motores passa
  a existir, desenhado para a IA local da funcionalidade 4 caber depois sem
  retrabalho, sem que nada dela seja construído agora.
- O PaddleOCR vai **dentro do programa**: motor e modelos na pasta da instalação.
  Nada é baixado em uso.
- Com o PaddleOCR, a página deitada é endireitada pelo **detector do Tesseract**,
  quando ele está instalado.
- A conferência diz **qual motor leu**.
- O motor faltando passa a ser dito **para cada motor**, na própria escolha; a
  tela cheia de "motor faltando" fica para quando nenhum dos dois funciona.
- A estimativa de tempo antes de ler passa a usar o tempo **do motor marcado**.
- Vale **nos dois módulos**: no Gerar OCR, na tela de escolher o documento; no
  Anonimizar, na tela de ler o PDF como imagem (RN-15 da spec 003).

### Fora de escopo da emenda

- **A IA local** (funcionalidade 4) — continua apagada na escolha.
- **Qualquer motor fora da máquina.** Nunca, por regra dura do projeto.
- **O PaddleOCR oficial** (PaddlePaddle) **e o modelo médio** — descartados na
  escolha técnica: o oficial não leu do jeito normal no Windows e leva quase um
  minuto por página; o médio é três vezes mais lento e não leu de forma
  consistentemente melhor.
- **Um modelo próprio para descobrir página deitada.** Quem endireita é o
  detector do Tesseract (RN-28).
- **Tabela no formato do Markdown, com barras.** A tabela continua saindo como
  tabela de texto (RN-10, RN-34).
- **Um botão "ler de novo com o outro motor"** na conferência.
- **Lembrar as escolhas da pessoa entre um uso e outro** — item novo do backlog,
  ligado à funcionalidade 4, que parou na mesma pergunta (onde guardar, e a
  emenda da RN-22).
- **A entrega da versão nova** e os roteiros "Como instalar" e "Como usar" — da
  `skill-11-gerente-de-entrega`, num prompt próprio.

### Premissas da emenda

- premissa: sem o Tesseract, o programa não tem como saber **qual** página
  estava deitada; por isso o aviso sai uma vez por documento, e não por página
  (RN-28).
- premissa: PDF com texto por dentro não muda nada — o PaddleOCR só entra quando
  a página é lida como imagem.
- premissa: ler em segundo plano, contar as páginas, cancelar (esperando a
  página atual terminar) e as telas de falha continuam iguais, com qualquer dos
  dois motores.
- premissa: os motores são conferidos ao abrir o módulo e de novo antes de cada
  leitura, como hoje se faz com o Tesseract.
- premissa: a página vai para o PaddleOCR na mesma densidade de hoje, 300 pontos
  por polegada (RN-7), a mesma da medição.
- premissa: os tempos do resumo foram medidos nesta máquina; nas do núcleo podem
  ser um pouco maiores.

### Fluxos da emenda

**Fluxo normal — PDF escaneado, com o PaddleOCR.**

1. A pessoa abre o módulo. A escolha mostra o PaddleOCR marcado, com o resumo
   embaixo de cada motor.
2. Ela escolhe um PDF sem texto por dentro (no Anonimizar, chega à tela de ler).
3. A estimativa antes de ler usa o tempo do PaddleOCR.
4. Para cada página: o programa desenha a imagem, o detector do Tesseract
   endireita o que estiver deitado, e o PaddleOCR lê.
5. A conferência abre como hoje, dizendo "lido pelo PaddleOCR".

**Fluxo alternativo — a pessoa escolhe o Tesseract.**

1a. Ela marca o Tesseract antes de ler. A estimativa passa a usar o tempo dele.
4a. A leitura é a de hoje, inteira. A conferência diz "lido pelo Tesseract".
1b. Com o programa aberto, o Tesseract continua marcado nos documentos seguintes
    daquele módulo, até ela trocar. Fechou e abriu o programa, volta o PaddleOCR.

**Caminho torto — falta o Tesseract, e o PaddleOCR funciona.**

- Não aparece aviso no alto nem tela cheia. Na escolha, a linha do Tesseract fica
  apagada, com "não encontrado nesta máquina — sem ele, página deitada não é
  endireitada", e as três saídas de hoje (instalar agora, conferir de novo,
  apontar a pasta) ficam ali.
- A leitura com o PaddleOCR segue, sem endireitar. A conferência mostra, uma vez,
  "a orientação das páginas não pôde ser conferida — falta o Tesseract nesta
  máquina". Nada disso vai para o arquivo (RN-11).

**Caminho torto — falta o PaddleOCR (instalação estragada).**

- A linha do PaddleOCR fica apagada, com "esta instalação está incompleta —
  reinstale o programa", e o Tesseract passa a vir marcado. A pessoa lê, mas
  sabendo com que motor. Nenhum arquivo é buscado na internet.

**Caminho torto — não funciona nenhum dos dois.**

- Como hoje: o aviso no alto com as três saídas do Tesseract, e a tela cheia
  para quem escolhe um PDF sem texto. O PDF com texto por dentro continua
  funcionando. A linha do PaddleOCR continua dizendo que a instalação está
  incompleta.

**Caminho torto — a leitura falha numa página, ou a pessoa cancela.**

- Igual a hoje, com qualquer dos dois motores: a tela de falha com "tentar de
  novo", ou a volta à escolha com nada gravado.

### Dados da emenda

| Informação | De onde vem | Observação |
| --- | --- | --- |
| motor escolhido | a pessoa | PaddleOCR ou Tesseract. Padrão: PaddleOCR. Vive na memória até ela trocar ou fechar o programa; cada módulo tem o seu (RN-26). *Desde a emenda de 28/10/2026, lembrado de um uso para o outro, no `preferencias.ini` (RN-36 a RN-39)* |
| motor que leu | derivado | vai para a linha da conferência que diz de onde o texto veio (RN-32) |
| orientação conferida? | derivado | não, quando o PaddleOCR leu sem o Tesseract na máquina; decide o aviso da conferência (RN-28) |
| PaddleOCR presente? | conferência dos arquivos na pasta do programa | os modelos e o motor estão no lugar e carregam (RN-29) |

Os modelos do PaddleOCR são arquivos do programa, e não dado: vão na instalação,
não mudam com o uso e não guardam nada de quem usa.

### Estados da interface da emenda

- **vazio:** a escolha com os três motores — PaddleOCR marcado, Tesseract, IA
  local apagada —, com a linha de resumo embaixo dos dois primeiros.
- **vazio, faltando o Tesseract:** a linha do Tesseract apagada, com o motivo e
  as três saídas; nenhum aviso no alto.
- **vazio, faltando o PaddleOCR:** a linha do PaddleOCR apagada, com "esta
  instalação está incompleta — reinstale o programa", e o Tesseract marcado.
- **vazio, sem nenhum motor:** como o "vazio, com o motor faltando" de hoje, mais
  a linha do PaddleOCR apagada.
- **com dados (conferência):** a linha de onde o texto veio diz "lido pelo
  PaddleOCR" ou "lido pelo Tesseract"; e, quando o PaddleOCR leu sem o Tesseract
  na máquina, o aviso de que a orientação não pôde ser conferida.

O desenho exato — onde ficam o resumo, a linha apagada e as três saídas, na
janela mínima de 900 px — sai no rascunho de tela, aprovado antes do código.

### Regras de negócio da emenda

- RN-25: a escolha do motor tem três itens, nesta ordem: **"PaddleOCR (nesta
  máquina)"**, "Tesseract (nesta máquina)" e "IA local" (apagada, RN-21). Ao
  abrir o programa, o PaddleOCR vem marcado.
- RN-26: **o motor marcado é o que lê.** A escolha vale até a pessoa trocar ou
  fechar o programa, e cada módulo tem a sua. Nada disso é guardado: o PaddleOCR
  vir marcado é o padrão escrito no programa, e a RN-22 continua inteira.
  *(Emendada em 28/10/2026: a escolha de cada módulo passa a ser lembrada de um
  uso para o outro — RN-36. O PaddleOCR continua sendo o padrão de quem nunca
  escolheu.)*
- RN-27: o PaddleOCR são os modelos PP-OCRv6 **pequenos**, rodados pelo RapidOCR
  (versão 3.10.0) com o onnxruntime (versão 1.31.0), dentro da pasta do
  programa. O programa confere que os arquivos dos modelos estão no lugar
  **antes** de chamar o motor, e nunca deixa a biblioteca buscar modelo na
  internet (RN-20).
- RN-28: com o PaddleOCR, a orientação é detectada pelo **detector do Tesseract**,
  quando ele está instalado (a RN-6 vale para os dois motores). Sem o Tesseract,
  a página vai como está, e a conferência diz uma vez, no alto: "a orientação das
  páginas não pôde ser conferida — falta o Tesseract nesta máquina".
- RN-29: faltando o PaddleOCR — modelo ausente, ou motor que não carrega —, a
  linha dele aparece apagada, com "esta instalação está incompleta — reinstale o
  programa", e o Tesseract passa a vir marcado. O programa **nunca troca de
  motor calado**.
- RN-30: faltando o Tesseract com o PaddleOCR funcionando, a linha do Tesseract
  aparece apagada, com "não encontrado nesta máquina — sem ele, página deitada
  não é endireitada", e as três saídas da RN-19 ficam ao lado dela. O aviso no
  alto e a tela cheia de motor faltando aparecem **só quando nenhum dos dois
  funciona**. O Tesseract sem o pacote de português conta como faltando (RN-19).
- RN-31: as linhas de resumo são: PaddleOCR — *"Melhor resultado, inclusive em
  tabela e página escaneada ruim · cerca de 2 segundos por página"*; Tesseract —
  *"Pode pular tabela com grade · cerca de 3 segundos por página"*. A estimativa
  antes de ler usa o mesmo tempo do motor marcado: 2 segundos por página com o
  PaddleOCR, 3 com o Tesseract (era 1,5, medido em 11/09/2026 só na massa
  limpa).
- RN-32: a conferência diz "lido pelo PaddleOCR" ou "lido pelo Tesseract", na
  linha que já diz de onde o texto veio. Nada disso vai para o arquivo (RN-11).
- RN-33: a escolha e as regras desta emenda valem nos dois módulos — no Gerar
  OCR, na tela de escolher o documento; no Anonimizar, na tela de ler o PDF como
  imagem.
- RN-34: com qualquer motor, a tabela sai como tabela de texto, com as colunas
  alinhadas, pela mesma remontagem de hoje (RN-10).
- RN-35: o instalador com o PaddleOCR dentro pode chegar a **cerca de 250 MB**
  (o da 0.1.0 tem 97). Passando disso, a decisão volta para a solicitante antes
  de a construção seguir.

### Critérios de aceite da emenda

- Dado qualquer dos dois módulos aberto, quando a escolha do motor aparece,
  então ela mostra, nesta ordem, "PaddleOCR (nesta máquina)" marcado, "Tesseract
  (nesta máquina)" e "IA local" apagada, com as duas linhas de resumo da RN-31.
- Dado um PDF sem texto e o PaddleOCR marcado, quando a leitura termina, então o
  texto foi lido pelo PaddleOCR (um teste confere qual motor foi chamado) e a
  conferência diz "lido pelo PaddleOCR".
- Dado o Tesseract marcado, quando a leitura termina, então o texto foi lido pelo
  Tesseract e a conferência diz "lido pelo Tesseract".
- Dadas as páginas limpas, com poeira e torta de `dados-exemplo/20-paginas-dificeis.pdf`,
  quando lidas pelo PaddleOCR, então todos os CPFs do gabarito delas aparecem
  inteiros no texto — inclusive os 12 da tabela com grade.
- Dada a página deitada (`03-conteudo-girado.pdf` e a página deitada da massa
  20), com o Tesseract instalado, quando lida pelo PaddleOCR, então o texto sai
  na leitura correta, e os CPFs da página deitada da massa 20 aparecem inteiros.
- Dado que o Tesseract não está na máquina e o PaddleOCR está, quando a pessoa
  abre o módulo, então não aparece aviso no alto, a linha do Tesseract está
  apagada com o motivo e as três saídas, e um PDF sem texto vai para a leitura
  (não para a tela cheia).
- Dado que o Tesseract não está na máquina, quando o PaddleOCR termina de ler,
  então a conferência mostra uma vez o aviso de que a orientação não pôde ser
  conferida, e o arquivo salvo não tem esse aviso.
- Dado que um arquivo de modelo do PaddleOCR foi tirado da pasta do programa,
  quando o módulo abre, então a linha do PaddleOCR está apagada com "esta
  instalação está incompleta — reinstale o programa", o Tesseract está marcado, e
  nenhuma tentativa de baixar modelo foi feita.
- Dado que nenhum dos dois motores funciona, quando a pessoa abre o módulo, então
  o aviso no alto e a tela cheia aparecem como hoje, e um PDF com texto por
  dentro segue até a conferência.
- Dado que a pessoa marcou o Tesseract e leu um documento, quando ela escolhe o
  documento seguinte no mesmo módulo, então o Tesseract continua marcado; o
  outro módulo continua com o PaddleOCR; e, fechando e abrindo o programa, os
  dois voltam ao PaddleOCR.
- Dado um PDF de 12 páginas, quando a tela mostra quanto a leitura deve levar,
  então diz "uns 24 segundos" com o PaddleOCR marcado e "uns 36 segundos" com o
  Tesseract.
- Dado que a leitura com o PaddleOCR está em andamento, quando a pessoa cancela,
  então o programa volta à escolha e nenhum arquivo foi gravado.
- Dada a pasta do programa montada para a entrega (e não o ambiente de
  desenvolvimento), quando ela lê a massa 20 com o PaddleOCR, então a leitura
  funciona.
- Dada a máquina **sem rede nenhuma**, quando o programa entregue lê um PDF
  escaneado com o PaddleOCR, então a leitura termina normalmente. *(Para a
  solicitante conferir, com a rede desligada.)*
- Dado o instalador gerado, então ele tem até cerca de 250 MB — ou a decisão da
  solicitante de seguir com mais que isso está registrada.
- Dado o código do programa inteiro, inclusive o do motor novo, quando se procura
  por endereço de internet ou chamada a serviço remoto, então não há nenhum; e o
  motor novo não usa nada de CPF (RN-18).
- Dados os testes que já existiam antes desta emenda, quando rodam, então todos
  passam — o Tesseract continua inteiro.

### Questões em aberto da emenda

Nenhuma. O desenho exato da escolha sai no rascunho de tela, com aprovação
própria; o tamanho real do instalador é medido na primeira etapa da construção e
conferido contra a RN-35.

## Emenda de 28/10/2026 — o motor lembrado de um uso para o outro

Funcionalidade 8 do backlog. Levantamento detalhado em
`mockups/requisitos/07-mapa-do-entendimento.html`. A janela que abre maximizada
e lembra o tamanho está na emenda de mesma data da spec 001; a RN-19 da spec 003
traz a remissão a esta.

### Objetivo da emenda

Quem prefere o Tesseract (ou qualquer motor que não o padrão) não precisa
marcá-lo de novo a cada vez que abre o programa: a escolha de cada módulo fica
lembrada de um uso para o outro.

### Escopo da emenda

- O motor marcado em cada módulo — o Gerar OCR e o Anonimizar, cada um o seu — é
  lembrado de um uso para o outro.
- A escolha passa a valer para a próxima vez na hora em que a pessoa marca.
- O que é lembrado mora num arquivo próprio do programa, o `preferencias.ini`, na
  pasta da instalação, ao lado do `.env`.

### Fora de escopo da emenda

- **Lembrar qualquer coisa do trabalho**: documento, texto lido, pasta usada,
  histórico, achados, e o tamanho de letra e de página da conferência
  (RN-23 e RN-24, que continuam valendo só enquanto o programa está aberto).
- **Um aviso na tela** de que a escolha veio lembrada, e **um botão de voltar ao
  padrão**: voltar ao padrão é marcar o PaddleOCR.
- **A configuração da IA local**: entra com a funcionalidade 4, no mesmo
  arquivo, com a senha dela no `.env`.
- **Escolha compartilhada** entre pessoas ou entre máquinas.
- **Escrever no `.env`**: ele continua sendo da TI, e o programa só o lê.

### Premissas da emenda

Inferências do mapa 07 que a usuária leu e não derrubou:

- premissa: a instalação é de uma pessoa só, na pasta de programas dela, e o que
  o programa lembra é dela; ninguém do núcleo herda a escolha de outra pessoa.
- premissa: nada do trabalho é lembrado (RN-40).
- premissa: o tamanho de letra e de página da conferência continua não lembrado.
- premissa: o que não dá para ler volta ao padrão, e o que não dá para gravar
  vale até fechar, os dois sem aviso: perder a lembrança não estraga nenhum
  documento (RN-39).
- premissa: a escolha desta máquina de desenvolvimento fica fora do histórico, e
  os testes usam uma escolha própria, isolada.
- premissa: a IA local entra depois, no mesmo arquivo, com a senha no `.env`.
- premissa: desinstalar leva a escolha junto; atualizar a versão a mantém
  (RN-41).

### Fluxos da emenda

**Normal — a escolha lembrada.**

1. A pessoa abre o Gerar OCR e marca o Tesseract.
2. Ela lê um documento, ou não lê nada, e fecha o programa.
3. Na próxima vez, o Gerar OCR abre com o Tesseract marcado. O Anonimizar, em
   que ela não mexeu, continua com o PaddleOCR.

**Caminho torto — o motor lembrado sumiu.** A TI desinstalou o Tesseract. Ao
abrir, a linha dele aparece apagada, dizendo por quê, e o PaddleOCR vem marcado
(RN-29 e RN-30): a troca aparece na tela. A partir daí o lembrado é o PaddleOCR;
quando o Tesseract voltar, a pessoa o marca de novo, se quiser (RN-37).

**Caminho torto — o arquivo não serve.** O `preferencias.ini` sumiu, foi apagado
ou está estragado: o programa abre com o PaddleOCR marcado nos dois módulos, como
no primeiro uso, sem erro e sem aviso. A próxima escolha grava um arquivo novo,
certo.

**Caminho torto — não dá para gravar.** A pasta ficou protegida: a escolha vale
até fechar o programa, como era antes desta emenda, sem aviso.

### Dados da emenda

O `preferencias.ini` é um arquivo de texto simples, que abre no Bloco de Notas,
com um bloco por módulo (e o bloco da janela, da spec 001). Dentro dele, só o
nome do motor de cada módulo: `paddleocr` ou `tesseract`. Nada de documento,
texto, pasta ou data.

| Informação | De onde vem | Observação |
| --- | --- | --- |
| motor lembrado do Gerar OCR | a pessoa, ao marcar | `paddleocr` ou `tesseract`; sem ele, o padrão |
| motor lembrado do Anonimizar | a pessoa, ao marcar | idem, independente do outro |

### Estados da interface da emenda

Nenhum estado novo: a escolha do motor tem o mesmo desenho, e o lembrado aparece
marcado como se a pessoa tivesse acabado de marcar. Por isso a emenda não tem
rascunho de tela.

### Regras de negócio da emenda

- RN-36: **o motor marcado é lembrado de um uso para o outro, um por módulo.** A
  escolha de cada módulo passa a valer para a próxima vez na hora em que a
  pessoa marca, leia ela um documento ou não. Quem nunca escolheu, ou não tem
  lembrança que dê para ler, abre com o PaddleOCR marcado (RN-25).
- RN-37: **o motor lembrado que falta ao abrir passa a ser lembrado como o
  outro.** A marca passa ao motor que funciona, com a troca à vista na tela
  (RN-29 e RN-30), e essa troca conta como uma escolha nova: fica lembrado o
  motor que passou a estar marcado. Faltando os dois, nada muda no que está
  lembrado.
- RN-38: **o que é lembrado mora no `preferencias.ini`, na pasta da
  instalação**, ao lado do `.env` (na pasta de programas da pessoa, gravável sem
  administrador). Nesta máquina de desenvolvimento, a pasta da instalação é a
  raiz do projeto, e o arquivo fica fora do histórico. O `.env` continua sendo
  só da TI, e o programa só o lê.
- RN-39: **lembrar nunca atrapalha usar.** Arquivo ausente, ilegível ou
  estragado vale como "nada lembrado", sem erro e sem aviso; gravação que falha
  deixa a escolha valendo até fechar, também sem aviso. A gravação é feita num
  arquivo provisório, trocado pelo de verdade só no fim: a máquina desligando no
  meio deixa a escolha anterior inteira.
- RN-40: **nada do trabalho é lembrado.** O `preferencias.ini` guarda só a
  escolha da pessoa; documento, texto lido, pasta usada, histórico, achados e o
  tamanho de letra e de página da conferência continuam proibidos de ficar
  guardados (RN-22).
- RN-41: **desinstalar apaga o `preferencias.ini`; atualizar o mantém.** Quem
  desinstala e instala de novo começa do padrão.

### Critérios de aceite da emenda

- Dado que a pessoa marca o Tesseract no Gerar OCR e fecha o programa, quando ela
  abre de novo, então o Gerar OCR vem com o Tesseract marcado, e o Anonimizar com
  o PaddleOCR.
- Dado que a pessoa marca o Tesseract no Anonimizar, sem ler documento nenhum, e
  fecha o programa, quando ela abre de novo, então o Anonimizar vem com o
  Tesseract marcado, e o Gerar OCR com o que estava.
- Dado que não há `preferencias.ini`, quando o programa abre, então os dois
  módulos vêm com o PaddleOCR marcado.
- Dado um `preferencias.ini` com conteúdo que não é de preferências (lixo, ou um
  motor que não existe), quando o programa abre, então os dois vêm com o
  PaddleOCR marcado, sem erro; e a próxima escolha grava um arquivo certo.
- Dado que o lembrado do Gerar OCR é o Tesseract e o Tesseract falta nesta
  máquina, quando o programa abre, então o Gerar OCR vem com o PaddleOCR marcado
  e a linha do Tesseract apagada, e o `preferencias.ini` passa a dizer
  `paddleocr` para o Gerar OCR; e quando o Tesseract volta, o Gerar OCR continua
  com o PaddleOCR.
- Dado que a pasta da instalação não aceita gravação, quando a pessoa marca o
  Tesseract, então o programa continua funcionando e lê com o Tesseract até
  fechar, sem aviso.
- Dado o `.env` com comentários da TI, quando a pessoa marca motores e fecha o
  programa, então o `.env` continua idêntico, byte a byte.
- Dado o `preferencias.ini` depois de um uso com documentos lidos, então ele tem
  só os motores (e a janela, da spec 001) — nenhum nome de documento, pasta,
  texto ou data.
- Dados os testes automáticos, então nenhum deles lê ou grava o
  `preferencias.ini` da raiz do projeto, e o `.gitignore` o cobre.
- Dado o instalador, então desinstalar o programa apaga o `preferencias.ini`, e
  instalar uma versão nova por cima o mantém.
- Dados todos os critérios das seções anteriores, então eles continuam passando,
  com a ressalva das RN-22 e RN-26 emendadas.

### Questões em aberto da emenda

Nenhuma.

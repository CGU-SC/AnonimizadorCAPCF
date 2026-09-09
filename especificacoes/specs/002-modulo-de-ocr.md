# Spec 002 — Módulo de OCR

**Status:** aprovada
**Data:** 2026-09-09

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
  de que depende de servidor que a TI ainda vai montar.
- Detectar, por verificação exata, se o PDF já tem camada de texto por dentro.
- Havendo camada de texto: mostrar as primeiras linhas dela na tela e deixar a
  pessoa escolher entre aproveitar esse texto ou ignorá-lo e ler as imagens.
- Não havendo camada de texto: desenhar cada página como imagem e ler com o
  Tesseract, endireitando automaticamente a página cujo conteúdo esteja girado.
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

## Premissas

- premissa: a entrada é sempre PDF — às vezes com texto por dentro (exportado do
  sistema de processos da UFSC), às vezes só imagem (impresso, ou anexo
  escaneado por terceiro).
- premissa: o programa detecta sozinho se há texto por dentro e só roda o OCR
  quando não há — isso é verificação exata, não palpite. Julgar se esse texto
  *presta* é outra coisa, e essa fica com a pessoa (RN-4).
- premissa: o motor desta versão é o Tesseract instalado na máquina, com o
  pacote de português. A LLM/IA local aparece no menu mas está fora do escopo
  desta versão. Nunca um serviço de empresa externa.
- premissa: a saída `.md` preserva as tabelas do documento original como tabelas
  de texto.
- premissa: PDF grande com vários documentos dentro entra como um documento só e
  sai como um `.md` só. Separar por dentro é melhoria futura.
- premissa: a conferência humana é parte fixa do processo quando o texto veio de
  OCR, e não etapa opcional.
- premissa: as máquinas do núcleo são Windows.
- premissa: o instalador do Tesseract estará disponível na máquina para o botão
  "instalar agora" abrir. Não estando, o programa mostra o passo a passo escrito
  e o botão fica apagado.

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
| motor escolhido | a pessoa (escolha na tela) | sim | só "Tesseract" é escolhível nesta versão |
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
  camada do PDF, e o botão "conferido".
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
  zerado, e só a detecção em cima da imagem pega o caso.
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
  o caminho do PDF que já tem texto continua funcionando.
- RN-20: o programa **nunca baixa nem instala nada sozinho** e nunca manda
  documento para lugar nenhum. O botão "instalar agora" abre um instalador que
  já está na máquina, e a confirmação do Windows é clicada por uma pessoa.
- RN-21: o item "IA local da UFSC" aparece na escolha de motor, apagado, com a
  explicação de que depende de servidor que a TI ainda vai montar. Não há, neste
  módulo, nenhum código que converse com motor remoto.
- RN-22: nada é guardado entre um uso e outro — nem histórico, nem preferência
  de motor, nem última pasta usada.

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

## Questões em aberto

Nenhuma.

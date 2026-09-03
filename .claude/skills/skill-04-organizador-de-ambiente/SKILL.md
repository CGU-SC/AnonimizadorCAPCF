---
name: skill-04-organizador-de-ambiente
description: Funda o projeto depois que os requisitos foram levantados e a stack foi aprovada — cria a ÁRVORE DE PASTAS padrão e escreve os ARQUIVOS DE RAIZ com conteúdo real (CLAUDE.md, .gitignore, .env.example, README, README dos dados de exemplo), até o commit fundador. Depois que o commit fundador existir, propõe o REPOSITÓRIO ONLINE (GitHub ou equivalente, fechado por padrão) e o envio da fundação para a branch inicial, e então escreve o BACKLOG das funcionalidades previstas antes de passar para a spec, mais o PAINEL `especificacoes/backlog.html` que o espelha em cartões por situação. É também a referência de ONDE CADA ARTEFATO MORA no projeto (spec, backlog, mockup, dados de exemplo, conferências, o atalho de abrir em `abrir/` e os artefatos gerados em `builds/`) e da regra dura de nunca versionar dado real. Use ao montar um projeto do zero, ao reorganizar um existente, quando alguém perguntar "onde coloco isso?" ou quando um arquivo aparecer em pasta que não é a dele. NÃO levanta requisitos (isso é `skill-02-analista-de-requisitos`), NÃO escolhe a stack (isso é `skill-03-arquiteto-de-solucao`) e não implementa funcionalidade. NO INÍCIO DE CADA FUNCIONALIDADE — e na primeira vez que é acionada numa sessão — oferece e RECOMENDA montar o PROMPT de uma sessão dedicada, em vez de conduzir aqui; herda o modo quando chega pelo gate de outra skill dentro da mesma funcionalidade, e volta a perguntar quando a funcionalidade é outra.
---

# Organizador de Ambiente

Projeto sem lugar certo para cada coisa faz toda sessão futura recomeçar
procurando onde as coisas estão — e inventar um caminho novo quando não acha.
Aí o mesmo assunto passa a morar em dois lugares, e nenhum deles é o certo.

Esta skill entra na hora em que o projeto ainda é uma pasta vazia, com o
histórico já ligado pela `skill-01-iniciar-projeto` e a stack já aprovada pela
`skill-03-arquiteto-de-solucao`. O trabalho dela é **dar lugar a cada coisa
antes da primeira funcionalidade** — porque depois já é mudança de endereço.

A ordem é sempre a mesma, e nenhuma etapa se antecipa:

**partida dada → requisitos levantados → stack aprovada → árvore criada →
arquivos de raiz com conteúdo real → commit fundador → repositório online →
backlog.**

Os três primeiros já aconteceram quando esta skill entra: são
**`skill-01-iniciar-projeto`** (a pasta e o histórico ligado),
**`skill-02-analista-de-requisitos`** e **`skill-03-arquiteto-de-solucao`**.

## Premissas do pacote (valem em toda skill)

Cinco premissas atravessam todas as skills. Elas não são etapa de nenhuma
delas: são o chão em que todas pisam. Quando uma instrução desta skill parecer
autorizar algo que uma premissa proíbe, **a premissa vence** — e o certo é
parar e perguntar, em vez de escolher sozinho.

### As palavras que voltam sempre

Estas oito reaparecem em toda skill do pacote. Ficam explicadas aqui, uma vez,
e são usadas sem rodeio daqui em diante: elas são o vocabulário de quem
trabalha com programa, e quem não o tem depende de tradução o tempo todo.

| A palavra | O que ela é |
| --- | --- |
| **commit** | uma foto do projeto inteiro, guardada junto com um bilhete que diz o que mudou. É o que permite voltar atrás depois |
| **branch** | uma linha de trabalho separada, em que se mexe sem estragar o que já funciona. Terminado o trabalho, ela se junta de volta |
| **diff** | a lista do que mudou desde a última foto: a linha que entrou, a linha que saiu |
| **spec** | o combinado escrito de uma funcionalidade, antes de ela ser programada — o que ela faz, o que ela não faz, e como se sabe que ficou pronta |
| **backlog** | a lista do que o programa ainda vai ter: uma linha por funcionalidade, com a situação de cada uma |
| **gate** | o ponto em que a IA para e espera uma pessoa dizer sim. É o que separa "ela fez" de "eu deixei" |
| **mockup**, ou rascunho de tela | o desenho de uma tela antes de ela existir de verdade, para você aprovar o visual olhando, e não imaginando |
| **stack** | o conjunto das escolhas técnicas do programa: em que linguagem ele é escrito, onde guarda os dados, como chega em quem usa |
| **refatorar** | arrumar o código por dentro sem mudar nada do que a pessoa vê na tela |
| **teste de regressão** | o teste que se escreve depois de consertar um defeito, para o mesmo defeito não voltar sem ninguém notar |
| **deploy**, ou publicar | pôr a versão nova no lugar onde as pessoas usam o programa |
| **standalone** | arquivo que se basta sozinho: abre sem internet, sem instalar nada e sem depender de outro arquivo do lado |
| **artefato** | qualquer coisa que o trabalho produz e fica gravada: a spec, o rascunho de tela, o mapa do banco, o instalador. Cada um tem uma pasta e uma skill dona |

### 1. O agente não sai do projeto

A **raiz do projeto** é a pasta onde o projeto inteiro mora, e ela é o mundo do
agente. Ler arquivo, escrever arquivo, listar pasta e rodar comando acontece
**dentro dela** — nunca na pasta pessoal de quem está usando, nunca em pasta de
outro projeto, nunca em `Documentos`, nunca em disco de rede.

Para sair da raiz é preciso um **pedido do usuário, com o caminho dito e a
tarefa dita** — "leia a planilha tal, naquele caminho, para importar os campos".
Essa autorização vale só para aquela tarefa. Ela não se estende à pergunta
seguinte, nem ao resto da sessão, nem à sessão de amanhã.

A barreira é **escrita, e não confiada**. O projeto nasce com um arquivo de
configuração — o `.claude/settings.json`, que o pacote chama de **a cerca do
agente** — negando o acesso a tudo que está fora da raiz; quem o escreve é a
skill que funda o ambiente. Instrução solta depende de o agente
lembrar dela; a regra gravada no arquivo continua valendo justamente quando ele
esquece.

### 2. Segredo não passa por aqui

**Senha, chave de acesso e endereço de banco com senha dentro moram em um
arquivo só — o `.env` — e em nenhum outro lugar.** Chave de acesso, também
chamada de *token* ou de *chave de API*, é a senha que um programa usa para
falar com outro: a que o seu programa usaria para entrar no serviço de e-mail,
no banco, no que for.

O `.env` fica **fora do histórico**: o nome dele entra no `.gitignore`, que é a
lista do que o histórico deve ignorar. Ao lado dele vai um `.env.example`, esse
sim gravado no histórico, com os **nomes** das senhas e nenhum valor de verdade
— ele serve para quem receber o projeto saber o que precisa preencher.

E há um segundo lugar de onde os segredos precisam ficar fora: **a conversa.**
Não peça ao usuário que cole uma senha no chat, não repita no chat uma senha
que você leu num arquivo, e não a escreva em boletim, em spec, em mensagem de
commit, em rascunho de tela nem em página HTML. Tudo o que passa pela sessão
fica gravado no registro dela, e registro de sessão não é cofre.

O mesmo corte vale para **documento pessoal e dado real de gente** — nome, CPF,
endereço, contrato, foto, planilha de cliente. Eles não entram no repositório em
lugar nenhum, nem como "só para testar": massa de teste é **inventada**.

Antes de todo commit e de todo envio, a pergunta é uma só: *se isso ficasse
público amanhã, o que vazaria?* Se a resposta não for "nada", pare e diga o que
encontrou, antes de gravar.

### 3. Desenvolvimento e produção não se misturam

**Produção** é onde estão os dados de quem usa o programa de verdade.
**Desenvolvimento** é a cópia em que se erra de graça. Os dois nunca
compartilham banco, arquivo de configuração, pasta de arquivos nem senha — e o
mínimo é um `.env` para cada um dos dois, nunca um `.env` só com uma chavinha
dentro dizendo em qual deles você está.

O ambiente é **visível**: quem abre o programa sabe em qual dos dois está sem
precisar adivinhar. Construir, testar e conferir acontece em desenvolvimento,
sempre. Nenhum comando que constrói, que muda a estrutura dos dados — o que se
chama **migração** — ou que apaga coisa aponta para produção sem uma decisão
humana tomada na hora e dita em voz alta.

Quando a diferença entre os dois puder mudar o resultado do que você está
prestes a fazer, **diga em que ambiente está antes de agir**.

### 4. Código limpo, comentado em português

O código sai **direto, enxuto e com a lógica no lugar**: sem trecho repetido por
cópia, sem passo que não serve a nada, e sem solução esperta que só quem
escreveu consegue entender depois.

E sai **comentado em português**, em linguagem simples, explicando **o porquê e
nunca o quê**: a regra que veio do usuário, o número que parece arbitrário e não
é, o caminho torto que já mordeu alguém. Comentário que repete o que a linha ao
lado já diz é ruído — e vira mentira no dia em que a linha muda e ele fica.
Termo técnico que aparecer, aparece explicado na primeira vez.

### 5. Toda etapa termina em uma página que se abre

Quem decide sobre o programa **não lê código.** Por isso o fim de cada etapa,
fase ou trecho entregue **produz ou atualiza uma página HTML local** — uma
página como as de um site, mas gravada na própria máquina, que abre no navegador
com dois cliques, sem internet e sem instalar nada. A pessoa abre e entende
sozinha, sem ninguém do lado traduzindo.

A página conta **o que ficou pronto e o que aquilo muda**, em texto direto e com
desenho: esquema, fluxo com o caminho torto ao lado do normal, antes e depois,
tabela. Linguagem objetiva e didática, sem jargão não explicado — e sem
infantilizar quem lê.

Quem **desenha** essas páginas é a skill de telas do pacote, chamada pela skill
que fechou a etapa; a skill que fecha decide **o que** a página precisa contar.

## Contrato

| | |
| --- | --- |
| **Lê** | As respostas do levantamento (`skill-02-analista-de-requisitos`) e a stack aprovada (`skill-03-arquiteto-de-solucao`); a pasta do projeto, quando já existe algo |
| **Escreve** | A árvore de pastas, `CLAUDE.md`, `.claude/settings.json` (a cerca do agente), `.gitignore`, `.env.example`, `README.md`, o `README.md` de `dados-exemplo/` e — depois do commit fundador — `especificacoes/backlog.md`, mais o painel `especificacoes/backlog.html` e o mapa do entendimento, os dois desenhados pela `skill-07-designer-de-telas` |
| **Pré-condição** | A partida dada pela `skill-01-iniciar-projeto` — pasta escolhida e histórico ligado —, requisitos levantados **e stack aprovada com "sim" expresso**. Sem os dois últimos, o `CLAUDE.md` nasce genérico e a árvore não tem como se adaptar |

Pré-condição que não se cumpre **não se contorna**: pare, diga qual artefato
falta e qual skill o produz, e pergunte em uma pergunta só. Seguir com a
entrada faltando é o jeito mais comum de produzir trabalho bem-feito sobre
premissa inventada.

## Quando entra

- Projeto novo, logo depois da stack aprovada e antes de qualquer funcionalidade.
- Projeto existente que precisa ser reorganizado, migrado por partes.
- Pergunta de destino: "onde eu coloco isso?", ou artefato que apareceu em pasta
  que não é a dele.

## O que NÃO faz

- **Não levanta requisitos** (**`skill-02-analista-de-requisitos`**) e **não escolhe a
  stack** (**`skill-03-arquiteto-de-solucao`**). Sem as duas coisas prontas, esta
  skill não começa.
- Não escreve spec (**`skill-05-redator-de-funcionalidade`**) nem desenha tela
  (**`skill-07-designer-de-telas`**). Escreve o **backlog**, que é a lista
  do que está previsto — uma linha por funcionalidade, nunca o detalhe de
  nenhuma.
- **Não liga o histórico e não escolhe a pasta do projeto** — isso é a
  **`skill-01-iniciar-projeto`**, e já aconteceu quando esta skill entra. Pasta
  sem histórico ligado é pré-condição faltando: devolva, não resolva de
  passagem.
- Não implementa funcionalidade: o projeto nasce vazio, organizado e versionado.
- Não decide sozinha: a stack precisa de "sim" expresso, e o envio para o
  repositório online também.

## Antes de tudo, e a cada funcionalidade · Aqui, ou em outra sessão?

Uma **sessão** é uma conversa com o agente, do começo ao fim dela. Pergunte — e
**recomende a sessão dedicada**, que é abrir uma conversa nova só para este
trabalho — em dois momentos: na **primeira vez** que esta skill entra numa
sessão, e **no início de cada funcionalidade**, quando a escrita ou a construção
de uma nova começa. Antes de qualquer outra coisa:

```
Antes de começar: monto o prompt para você abrir uma sessão dedicada a isto,
ou conduzo aqui mesmo?

  1) ✅ RECOMENDADA — sessão dedicada: eu escrevo o texto pronto, você abre uma
     conversa nova comigo e cola lá. Vale quase sempre: conversa nova rende
     mais, e este trabalho não fica disputando espaço com tudo o que já foi
     falado aqui
  2) aqui mesmo — quando o trabalho for pequeno, ou quando esta sessão já
     carrega o contexto de que ele precisa
  3) outra coisa que você tem em mente
```

**A recomendação é sempre a sessão dedicada**, e não é formalidade: conversa
longa perde o começo, e trabalho que entra no fim de uma sessão cheia herda o
cansaço dela — a IA passa a responder pelo que lembra em vez de pelo que está
escrito. Recomende assim mesmo quando o trabalho parecer pequeno: quem sabe se
é pequeno é quem pediu.

**Modo A — sessão dedicada.** Você escreve **um bloco de texto** — o *prompt*,
que é o texto que a pessoa vai colar na conversa nova — e para por aí. Não
executa mais nada: nem arquivo, nem comando, nem as perguntas do procedimento.
Esse texto precisa carregar o que a outra conversa não teria como saber sozinha:
o que é para fazer, em que pé o trabalho está, quais arquivos ela deve ler
antes, quais travas desta skill valem lá, e o que **não** é para fazer. Montado o
prompt, a skill que o escreve é a `skill-12-nova-sessao`.

**Modo B — aqui mesmo.** Conduz o procedimento desta skill, nesta sessão.

**A resposta vale para uma funcionalidade, não para a sessão inteira.**
Funcionalidade nova, pergunta nova — mesmo que a anterior tenha sido conduzida
aqui mesmo. É justamente a sessão que já produziu uma funcionalidade inteira que
menos serve para começar a próxima: ela entra na seguinte carregando o contexto
da anterior, e o que era memória vira suposição.

**O que conta como funcionalidade nova:** outro item do backlog, uma spec nova,
ou uma construção que começa depois de outra ter sido dada por concluída. Ajuste
dentro da funcionalidade em andamento — corrigir o que acabou de ser conferido,
refazer uma etapa, responder o que a revisão apontou — é a mesma funcionalidade,
e não repõe a pergunta.

Não pergunte de novo quando:

- **o modo já foi respondido para esta funcionalidade** — vale até ela terminar,
  e não além dela;
- **você chegou pelo gate de fim de rodada de outra skill dentro da mesma
  funcionalidade** — a passagem é continuação do mesmo trabalho e herda o modo
  que já valia. Diga em uma linha que está seguindo no modo herdado. Quando o
  gate abre uma funcionalidade nova, o modo **não** se herda: pergunte;
- **o pedido já diz qual é o modo** — um texto que já chega com fases numeradas
  e regras de execução é modo B declarado. Diga em uma linha por que entendeu
  assim, e siga;
- **o trabalho só faz sentido aqui** — porque depende do que está pendente agora
  ou do que acabou de ser feito nesta sessão. Modo A não se aplica: diga isso em
  uma linha e siga em B.

Fora desses casos, **pergunte mesmo quando parecer óbvio.** Deduzir errado custa
a sessão inteira: ou você entrega um texto quando esperavam o trabalho feito, ou
mexe no projeto quando esperavam só a instrução.

## Procedimento

### 0. A ferramenta que a stack exige

A stack acabou de ser aprovada, e é só agora que se sabe o que a máquina precisa
ter: a linguagem, o banco, o empacotador. Esse é o **segundo momento da etapa 2
da `skill-01-iniciar-projeto`** — não repita o procedimento aqui, chame-a.

O que não pode acontecer é escrever no `CLAUDE.md` um comando que ninguém
conseguiu rodar. **Cada comando que entrar na tabela de comandos foi executado
antes**, e a saída real apareceu na conversa.

Já estando tudo instalado, isto é uma linha dita e nada mais.

### 1. A árvore do projeto

Cada pasta é o destino de um artefato que alguma skill produz. Pasta sem skill
que a alimente costuma ser pasta que ninguém mantém.

```text
projeto/
├── .claude/
│   ├── skills/<nome>/SKILL.md   # os procedimentos que a IA segue
│   ├── mapa-das-skills.html     # o pacote instalado, desenhado — sempre o vigente
│   └── settings.json            # a cerca: o que o agente não pode ler nem tocar
├── programa/                    # o código do programa (+ seus testes ao lado)
├── especificacoes/
│   ├── backlog.md               # a lista do que está previsto, uma linha cada
│   ├── backlog.html             # a mesma lista em painel, sempre o vigente
│   ├── mapa-do-banco.html       # o desenho do banco, sempre o vigente
│   └── specs/                   # NNN-assunto.md — o quê construir
├── mockups/
│   ├── 00-indice.html           # a capa: toda página do projeto, com data e origem
│   ├── sistema-de-design.md     # a identidade visual, com os valores exatos
│   ├── 00-sistema-de-design.html  # a página que mostra o sistema
│   ├── marca/                   # o ícone e o logo fornecidos pela pessoa
│   ├── <area>/                  # NN-nome.html — rascunhos de tela
│   ├── requisitos/              # NN-mapa-do-entendimento.html — o que ficou combinado
│   ├── exemplos/                # NN-assunto.html — as alternativas de uma pergunta, lado a lado
│   ├── specs/                   # NNN-assunto.html — a spec desenhada
│   └── revisoes/                # NN-antes-e-depois.html — o que cada revisão mudou
├── dados-exemplo/
│   └── README.md                # origem e natureza da massa (obrigatório)
├── conferencias/                # o que prova que os números estão certos
├── abrir/                       # abrir-dev.bat — o atalho de abrir o programa
├── builds/                      # artefatos gerados — conteúdo gitignored
├── CLAUDE.md                    # contrato de trabalho do agente
├── .env.example                 # versionado: os nomes das variáveis, sem os valores
├── .env                         # gitignored: os valores reais do ambiente de desenvolvimento
├── .gitignore
└── README.md
```

| Pasta | Quem escreve nela |
| --- | --- |
| `.claude/skills/` | o pacote de skills adotado, instalado pela `skill-01-iniciar-projeto` |
| `.claude/mapa-das-skills.html` | `skill-00-mapa-skills`, a cada vez que o pacote muda |
| `.claude/settings.json` | esta skill, na fundação — e só ela |
| `especificacoes/backlog.md` | esta skill, a partir do levantamento |
| `especificacoes/backlog.html` | `skill-07-designer-de-telas`, a pedido desta skill, da `skill-05-redator-de-funcionalidade` e da `skill-08-construtor-de-funcionalidades` |
| `especificacoes/mapa-do-banco.html` | `skill-06-modelador-de-dados` |
| `especificacoes/specs/` | `skill-05-redator-de-funcionalidade` |
| `mockups/` | `skill-07-designer-de-telas` |
| `dados-exemplo/` | quem gera a massa sintética |
| `conferencias/` | quem confere os números — a pessoa, com a `skill-08-construtor-de-funcionalidades` ao lado |
| `abrir/` | `skill-08-construtor-de-funcionalidades` |
| `builds/` | `skill-11-gerente-de-entrega` |

Cinco coisas que não são óbvias e custam caro quando se erra:

- **`.claude/skills/` é o único lugar** de onde o agente carrega skills. Pasta
  `skills/` na raiz não é lida por nada, e o catálogo é lido na **abertura** da
  sessão: copiou com a sessão aberta, reinicie.
- **Teste fica ao lado do código** que ele cobre, não numa pasta `tests/` de
  raiz. Separado, o agente frequentemente não acha e escreve outro.
- **`builds/` tem o conteúdo ignorado** pelo git. Artefato gerado nunca se
  edita à mão e nunca se commita.
- **`abrir/` e `builds/` são opostas, apesar do nome parecido.** `abrir/` guarda
  o **atalho de abrir o programa em modo DEV** — um arquivo que a pessoa clica
  duas vezes para ver o programa enquanto ele está sendo construído. É escrito à
  mão, é do projeto e **é versionado**. `builds/` guarda o instalador **gerado**
  no dia da entrega, e o conteúdo dele fica fora do histórico. Uma é do dia a
  dia; a outra é do dia de entregar.
- **Página HTML mora ao lado do arquivo que ela mostra**, e não toda numa pasta
  de páginas. O `backlog.html` fica junto do `backlog.md`; o `mapa-do-banco.html`
  junto das specs. Separados, um dia mudam em separado, e aí a página passa a
  mostrar um projeto que não existe mais. Em `mockups/` ficam as páginas que não
  têm arquivo-fonte: os rascunhos de tela e os relatórios. Quem as **desenha** é
  sempre a **`skill-07-designer-de-telas`**, seja qual for a pasta — e o
  `mockups/00-indice.html` é a capa que lista todas elas, esteja cada uma onde
  estiver.

**A estrutura serve ao projeto, não o contrário.** Programa sem interface não
cria pasta de tela vazia; projeto que não gera instalador não cria `builds/`. O
`abrir/` não nasce na fundação: quem o cria é a
**`skill-08-construtor-de-funcionalidades`**, na primeira etapa que
deixa alguma coisa visível na tela — antes disso não há o que abrir. O que
**não** se adapta são as regras duras abaixo.

### 2. Regra dura: nada de dado real em `dados-exemplo/`

A massa é **sintética ou irreversivelmente anonimizada**. Nunca extrato de banco
de produção, nunca planilha de caso real, nunca CPF, nome ou documento de pessoa
que existe — nem "só para testar rápido".

O motivo é a natureza do histórico: arquivo commitado e depois apagado
**continua no histórico** de todo clone já feito. Não existe desfazer. Em
projeto que lida com dado pessoal ou sigiloso, um único commit descuidado é
vazamento permanente.

O `README.md` da pasta declara, para cada conjunto: o que é, como foi gerado e o
que ele exercita. Massa sem procedência declarada é tratada como suspeita.

### 3. Os arquivos de raiz

Criados com **conteúdo real, nunca placeholder**, antes da primeira
funcionalidade:

| Artefato | O que precisa conter |
| --- | --- |
| `CLAUDE.md` | O contrato de trabalho do agente, carregado em toda sessão. Esqueleto abaixo |
| `.claude/settings.json` | A **cerca do agente** — as regras que negam leitura e escrita fora do projeto e nos cantos onde mora segredo. Modelo abaixo |
| `.gitignore` | `.env` e todo `.env.<ambiente>`, dados reais, `builds/`, pastas de dependência e arquivos de máquina. Escrito **antes** do primeiro commit, não depois. `abrir/` **nunca** entra nesta lista: o atalho é do projeto e viaja com ele |
| `.env.example` | Os **nomes** das variáveis com um exemplo inócuo, nunca os valores. O `.env` de verdade fica fora do histórico |
| `README.md` | O que o programa faz, como instalar, como rodar e onde ficam os dados |
| `dados-exemplo/README.md` | A procedência da massa, declarando que é sintética |

Esqueleto do `CLAUDE.md`:

```markdown
# <Projeto>

## O que é
Duas a quatro linhas: o que o programa faz e para quem.

## Stack e por quê
A escolha da stack, com o motivo em uma linha e o que ficou de fora.

## Comandos
| O quê | Comando |
| --- | --- |
| Rodar o programa | `...` |
| Rodar as conferências | `...` |
| Gerar o instalador | `...` |

## Onde ficam as coisas
Um ponteiro por pasta, uma linha cada.

## O combinado com quem usa
As respostas do levantamento que valem para o projeto inteiro.

## Regras duras
O que nunca se faz neste projeto, com o motivo de cada uma. Três nascem com o
projeto, das premissas do pacote:
- O agente trabalha **dentro desta pasta**. Sair dela é pedido do usuário, com
  caminho e tarefa nomeados, e vale só para aquela tarefa.
- **Segredo mora no `.env`**, nunca no código, nunca no chat, nunca no
  histórico. Dado real de pessoa não entra no repositório de jeito nenhum.
- **Desenvolvimento e produção não compartilham** banco, configuração, pasta de
  arquivos nem credencial. Nenhum comando aponta para produção sem decisão dita
  na hora.

## Convenções
Idioma, padrão de commit, nomenclatura.

Comentário no código: **em português, explicando o porquê, nunca o quê.**
Comentário que repete o que a linha já diz é ruído, e no dia em que a linha
muda e ele não, passa a mentir. Comenta-se a decisão que não está escrita em
lugar nenhum: por que este número, por que este caso é tratado à parte, de
onde veio esta regra. Linguagem do dia a dia — quem lê pode não programar.

## O que já nos mordeu
Nasce vazia. Cada obstáculo não óbvio que aparecer entra aqui: o que
aconteceu, em uma linha, e como se resolve. Uma linha por item.
```

O `CLAUDE.md` é o arquivo que a IA lê em **toda** sessão futura: vazio ou
genérico, ele não serve para nada. E não repita nele o passo a passo que já vive
numa skill — informação duplicada envelhece em uma das cópias e passa a mentir.

**A convenção de comentário fica aqui, e não nas skills, de propósito.** Ela
precisa valer no momento em que o código é escrito: o `CLAUDE.md` é lido em toda
sessão, então o código já nasce comentado assim. Deixada só na revisão, ela vira
faxina permanente — alguém passando atrás para comentar o que já foi escrito
mudo, em todo trecho, para sempre. A **`skill-08-construtor-de-funcionalidades`**
escreve seguindo esta regra; a **`skill-09-revisor-de-codigo`** confere se
ela foi cumprida, na lente de clareza.

**Ele nasce na fundação, mas não termina aqui.** A última seção é a única que
cresce sozinha ao longo do projeto, e é a que mais paga.

O motivo: a IA abre cada sessão sem lembrar de nenhuma anterior. Sem esse
registro, a mesma parede é descoberta duas vezes — e na segunda ninguém lembra
como se saiu dela na primeira. Quem escreve ali é quem tromba no obstáculo, quase sempre a
**`skill-08-construtor-de-funcionalidades`**.

O que entra: a biblioteca que só funciona com uma versão, o formato de arquivo
que muda sem avisar, o passo de instalação que ninguém adivinha, o comando que
precisa de um jeito específico nesta máquina. O que **não** entra: preferência
de gosto, e coisa que já está escrita em outro lugar do projeto.

### 3.1 A cerca do agente: `.claude/settings.json`

A premissa 1 diz que o agente não sai do projeto. Este arquivo é o que a **faz
valer**: instrução o agente pode esquecer, regra em arquivo continua valendo.

Sem configuração nenhuma, o agente já lê sem perguntar só dentro da pasta onde a
sessão abriu, e pede autorização para sair. O que falta é a camada de baixo — os
lugares onde ele não entra **nem perguntando**:

```json
{
  "permissions": {
    "deny": [
      "Read(//**/.ssh/**)",
      "Read(//**/.aws/**)",
      "Read(//**/.gnupg/**)",
      "Read(//**/.claude/.credentials.json)",
      "Read(**/.env)",
      "Read(**/.env.producao)",
      "Edit(**/.env)",
      "Edit(**/.env.producao)",
      "Cd"
    ],
    "additionalDirectories": []
  }
}
```

Linha a linha, em português:

| Regra | O que ela impede |
| --- | --- |
| `Read(//**/.ssh/**)`, `.aws`, `.gnupg` | ler as chaves de acesso da máquina, em qualquer pasta do disco |
| `Read(//**/.claude/.credentials.json)` | ler a credencial do próprio agente |
| `Read(**/.env)` e um por ambiente | ler o segredo **do próprio projeto** — o programa lê o `.env` quando roda; o agente não precisa |
| `Edit(**/.env)` e um por ambiente | escrever dentro deles: o `.env` é da pessoa, e o que o agente escreve é o `.env.example` |
| `Cd` | mudar a pasta da sessão para outro lugar do disco |
| `additionalDirectories: []` | a lista de pastas extras nasce vazia, e só cresce por pedido |

`//` no começo do caminho quer dizer "a partir da raiz do disco"; sem ele, o
caminho conta a partir do projeto. E uma regra de `Read` que nega também barra
escrever e criar arquivo naquele caminho.

**Uma linha por ambiente, e nunca `.env.*`.** O curinga parece prático e é uma
armadilha: `.env.*` casa também com o `.env.example`, e aí o agente fica
proibido de escrever justamente o arquivo que ele precisa manter. Cada ambiente
que o projeto ganhar entra com o nome inteiro, em uma linha de `Read` e uma de
`Edit`.

**A consequência de negar o `.env` é dita na hora, não descoberta depois:**
quando uma funcionalidade precisar de uma variável nova, o agente acrescenta o
**nome** no `.env.example`, avisa, e **quem preenche o valor é a pessoa**, no
editor dela. É um passo a mais de propósito — é ele que impede a chave de
aparecer no chat.

**Uma regra a mais, só quando o projeto NÃO mora dentro da pasta pessoal**
(`C:\Users\<nome>\...` ou `/home/<nome>/...`): acrescente `"Read(~/**)"` e
`"Edit(~/**)"`, e a cerca fecha dos dois lados. Se o projeto mora lá dentro,
**não acrescente**: a regra negaria o próprio projeto, porque negar vence
permitir.

**O que esta cerca não alcança:** ela vale para as ferramentas de arquivo do
agente e para os comandos de leitura que ele reconhece no terminal. Um programa
que o agente mande rodar e que abra arquivos por conta própria passa por fora
dela. Por isso a premissa continua sendo regra de conduta, e não só de arquivo.

### 3.2 Desenvolvimento e produção, separados desde a fundação

A premissa 3 começa a valer aqui, e não no dia da entrega: ambiente que nasce
misturado não se separa depois sem susto. Na fundação isso é pouca coisa e custa
quase nada:

- **Um arquivo de configuração por ambiente**, nunca um só com um interruptor
  dentro — `.env` para desenvolvimento (é o que a pessoa copia do
  `.env.example`) e `.env.producao` no dia em que produção existir. Os dois no
  `.gitignore`.
- **Banco separado, com nome que se lê**: `<projeto>-dev` e `<projeto>-prod`.
  Nunca o mesmo arquivo de banco, nunca a mesma pasta de arquivos enviados.
- **O ambiente aparece na tela** — uma faixa, uma cor ou o título da janela
  dizendo "desenvolvimento". Quem não sabe em que ambiente está acaba apagando
  de verdade o que achava que era teste.
- **O `.env.example` declara, na primeira linha, de que ambiente ele é.**

Enquanto o programa só roda na máquina de quem o construiu, produção não existe
e a separação é barata — é por isso que ela se faz agora. Registre-a no
`CLAUDE.md`, em "Regras duras", e ela passa a valer em toda sessão futura.

### 4. O primeiro commit

Com a árvore e os arquivos de raiz prontos, esta skill para, e **não commita**:
fecha a rodada pelo gate. O histórico já está ligado desde a
**`skill-01-iniciar-projeto`** — não havendo histórico nenhum, é ela que resolve
isso, não esta. Se o usuário escolher commit, quem executa é a
**`skill-10-controlador-de-versoes`**, que apresenta o commit fundador e espera
a aprovação.

Vale ali a exceção do commit fundador, e ela é de branch, não de gate: esse
primeiro commit vai na branch inicial mesmo, e a branch de trabalho nasce depois
dele, antes da primeira funcionalidade.

Regras desta etapa:

- **Nenhum dado real e nenhum segredo entram no repositório**, nem no primeiro
  commit.
- Nada de esqueleto de funcionalidade "só para começar". O projeto nasce vazio,
  organizado e versionado; a primeira tela vem depois, pela fase própria.
- Pasta vazia sem conteúdo previsto é convite a virar depósito: crie a pasta
  quando houver o que colocar nela.

### 5. O repositório online

Enquanto o histórico só existe na máquina de quem programa, o projeto inteiro
tem um ponto único de falha: disco que queima, notebook que some, pasta apagada
sem querer. O commit fundador não protege nada se ele só existe em um lugar.

Esta etapa só começa **depois que o commit fundador existir** — não se envia o
que ainda não foi gravado. Se a árvore está pronta mas o commit não aconteceu,
esta etapa não é a próxima: o gate é.

Duas perguntas, uma de cada vez, nunca as duas na mesma mensagem:

1. **Criar o repositório online agora?** GitHub, GitLab, o que a pessoa já usa.
   Numerada, com `1) ✅ RECOMENDADA — criar agora: o projeto passa a existir em
   mais de um lugar`, depois "deixar só nesta máquina por enquanto" e "outra
   coisa que você tem em mente".
2. **Fechado ou aberto?** Só depois da primeira ter sido respondida.
   **Fechado é o padrão e a recomendação, e o silêncio nunca vale por
   "aberto".** Repositório aberto é lido pelo mundo inteiro, hoje e sempre,
   inclusive por quem varre a internet atrás de segredo esquecido. Projeto que
   toca dado pessoal, sigiloso ou de trabalho nasce fechado.

Antes de enviar, confira e mostre o que vai junto: histórico sem nada pendente,
`.gitignore` cobrindo `.env`, `builds/` e dado real, e `dados-exemplo/` só com
massa sintética. Vale aqui a mesma natureza do commit, agravada: **enviado é
permanente**. Uma vez no servidor, o histórico pode ter sido clonado, indexado
ou copiado por qualquer um com acesso, e apagar depois não desfaz nada disso.

O envio vai para a **branch inicial** (`main`), onde o commit fundador está. A
branch de trabalho nasce depois dele, antes da primeira funcionalidade.

**O envio é ato do usuário**, como o commit. Apresente o que será enviado e para
onde, e espere "sim" expresso. Sem isso, não envia. Quem executa esta etapa é
esta skill: criar o repositório e enviar a fundação é parte de fundar o projeto,
não é publicar o programa — publicar é a **`skill-11-gerente-de-entrega`**.

### 6. O backlog das funcionalidades

Com o projeto fundado e guardado, falta a única coisa que ainda não existe: a
lista do que vai ser construído. Sem ela, a próxima sessão abre perguntando "e
agora, o quê?", e a resposta muda conforme o dia e conforme quem lembra do quê.

Esta skill escreve `especificacoes/backlog.md` com as principais funcionalidades
previstas, **tiradas do que o levantamento já respondeu**. Não invente item que
ninguém pediu, e não detalhe nenhum:

```markdown
# Backlog

O que está previsto para este projeto. Uma linha por funcionalidade, sem
detalhe — o detalhe de cada uma é a spec, escrita uma de cada vez.

| # | Funcionalidade | O que ela entrega para quem usa | Situação |
| --- | --- | --- | --- |
| 1 | ... | ... | prevista |
```

A situação de cada item é **prevista → em spec → em construção → construída**, e
quem a atualiza é a skill que fez o item andar: a
**`skill-05-redator-de-funcionalidade`** ao escrever a spec, e a
**`skill-08-construtor-de-funcionalidades`** ao construir.

Duas dessas situações têm trava, e é onde o backlog costuma passar a mentir:

- **em construção** — parte existe no programa, parte não. A linha diz **qual
  parte falta**, em uma frase. "Parcial" sozinho não informa nada e não deixa
  ninguém retomar.
- **construída** — só depois que **a pessoa viu funcionando na tela**. Nunca
  porque o código parece completo. Item marcado construído sem ninguém ter
  aberto o programa some da lista e reaparece na entrega.

A diferença entre os dois artefatos é o que impede o backlog de virar spec
disfarçada:

- **Backlog** — todas as funcionalidades, uma linha cada. É índice.
- **Spec** — uma funcionalidade por inteiro, em `especificacoes/specs/`. É contrato.

Apresente a lista e espere a confirmação: item faltando, item que sobra e ordem
errada são todos correção do usuário, não sua. Backlog confirmado sem ninguém
ler é lista que ninguém segue.

**Diga uma vez, ao apresentar a lista, o que ela não mostra.** O backlog é só a
parte visível do trabalho. Quem mede projeto real encontra algo em torno de um
terço do esforço em funcionalidade nova; os outros dois terços são correção,
arrumação do que ficou torto, proteção de dado, empacotamento e registro do que
mudou — coisas que não aparecem em lista nenhuma porque não são funcionalidade.

Isso não é aviso pessimista, é calibragem: sem ele, a pessoa olha treze linhas,
faz a conta pelo tempo da primeira, e conclui na terceira semana que o projeto
travou. O projeto não travou — ele entrou na parte que a lista não mostrava.

#### 6.1 O backlog como painel

Confirmada a lista, peça à **`skill-07-designer-de-telas`** a página
`especificacoes/backlog.html`: o mesmo backlog em cartões, um por funcionalidade,
agrupados pela situação — **prevista**, **em spec**, **em construção**,
**construída** — com o que cada uma entrega para quem usa, e a frase do que falta
nas que estão em construção.

**O `backlog.md` continua sendo a fonte; a página é o espelho.** Ninguém edita a
página: ela se regenera a partir do arquivo, sempre por cima, um arquivo só.
Página que se edita à mão vira uma segunda verdade, e a partir daí as duas
discordam sem ninguém perceber qual está certa.

Ela é a página que a pessoa mais vai abrir, e é a única do projeto que responde
"como estamos?" sem obrigar ninguém a ler lista nenhuma. Quem a regenera é a
skill que fez o item andar — a **`skill-05-redator-de-funcionalidade`**
ao escrever a spec, a **`skill-08-construtor-de-funcionalidades`** ao
fechar a funcionalidade —, **no gate, junto do commit**, e nunca a cada mexida.
Painel que pisca a cada alteração deixa de ser marco e vira ruído.

#### 6.2 O mapa do entendimento, quando o projeto nasceu agora

Em projeto do zero, o levantamento da
**`skill-02-analista-de-requisitos`** aconteceu **antes de existir pasta**
— e por isso o mapa do entendimento dele ficou sem lugar para morar. Agora tem.

Gere-o aqui, pela **`skill-07-designer-de-telas`**, em
`mockups/requisitos/01-mapa-do-entendimento.html`, com as respostas do
levantamento e as inferências marcadas como inferências. É a primeira página do
projeto, e a que explica por que ele é como é.

Não houve levantamento registrado? Não invente um: diga que a página fica para
quando houver, e siga.

Confirmada a lista, proponha a passagem para a
**`skill-05-redator-de-funcionalidade`**, que pega **um** item e o
transforma em spec. Qual item vem primeiro é escolha do usuário, em lista
numerada — nunca sua.

## Como conversar

Uma coisa de cada vez. Nunca duas perguntas na mesma mensagem.

Toda escolha vai como **texto escrito no próprio chat**, em lista numerada —
**nunca como seletor, menu, caixa de escolha ou painel de opções** que a
interface abre por cima da conversa, e nunca pela ferramenta de pergunta com
opções clicáveis. O motivo é prático: o que aparece num painel some quando ele
fecha. Não volta quando a pessoa rola a conversa para cima, não pode ser relido
no dia seguinte e não fica na conversa como registro do que foi combinado.
Texto fica.

  - a **opção 1 é sempre a recomendada**, e vem marcada com `✅ RECOMENDADA`
  - o motivo da recomendação logo abaixo dela, em uma linha
  - o que cada opção ganha e o que custa, uma linha cada
  - sempre uma última opção "outra coisa que você tem em mente"

O modelo, exatamente assim:

```
<a pergunta, em uma frase>

  1) ✅ RECOMENDADA — <a opção>
     <por que esta, em uma linha>
  2) <opção> — <o que muda em relação à 1>
  3) outra coisa que você tem em mente
```

**Nenhuma pergunta aberta, e nenhuma de sim ou não.** A regra vale para *toda*
pergunta — inclusive as duas que mais escapam, que são a de confirmar o que você
entendeu e a de aprovar o que você propôs.

"O que eu entendi errado?" devolve à pessoa o trabalho de descobrir sozinha onde
está o erro, e quem não programa quase nunca consegue dizer onde ele está. Já
"está certo?" e "posso seguir?" têm uma resposta cômoda só — e o sim automático
é o começo de tudo que se constrói errado.

As duas viram lista numerada, com as correções possíveis já escritas como opção.
Quem não sabe formular o erro sabe apontar para ele.

O modelo da confirmação, logo depois de devolver um entendimento ou de propor
uma lista:

```
  1) ✅ RECOMENDADA — é isso; pode seguir
     <por que dá para escolher a 1 sem medo: o que ainda vem depois, e o que
     ainda dá para corrigir antes de virar trabalho perdido>
  2) tem coisa aí que não é assim — eu digo qual, e você refaz
  3) falta uma coisa que eu esperava e não está aí
  4) outra coisa que você tem em mente
```

As opções 2 e 3 são o que substitui o "está certo?": elas deixam a correção
barata e visível. Sem elas, discordar custa escrever um parágrafo do zero — e
quase ninguém escreve.

**Não havendo o que recomendar** — porque a resposta é um fato do projeto e não
uma preferência, ou porque a lista é de saídas e escolher por quem pediu seria
empurrar —, diga isso em uma linha antes da lista, e **nenhuma** opção leva o
`✅`. O que não pode existir é lista com a recomendação escondida no meio.

Linguagem comum. Antes de mandar a mensagem, troque cada palavra que só faz
sentido para quem programa por uma frase do dia a dia, ou descreva a cena em vez
de dar nome a ela. Precisou mesmo do termo técnico? Explique primeiro, nomeie
depois.
**Caminho de arquivo, endereço de internet e linha de comando vão em bloco de
código, em linha própria** — num trecho à parte, com fundo próprio, e nunca
soltos no meio da frase. Quem está do outro lado precisa selecionar e copiar sem
caçar onde o trecho começa e onde termina, e no meio do texto o olho perde a
borda. Um bloco por coisa: dois comandos que se digitam em momentos diferentes
são dois blocos, na ordem em que se digitam.
**Caminho citado é caminho que você oferece abrir.** Toda vez que a mensagem
trouxer uma pasta ou um arquivo da máquina — o que você acabou de criar, a pasta
do projeto, o atalho de abrir, a página gerada, o banco de dados —, **ofereça
abrir você mesmo**, na mesma mensagem em que o caminho aparece. Nunca deixe
ninguém procurando: quem não programa gasta mais tempo achando a pasta do que
fazendo o que ia fazer dentro dela, e caminho digitado à mão vira erro que a
pessoa lê como programa quebrado.

A oferta é **uma opção a mais na lista que a mensagem já tem** — nunca uma
pergunta à parte, que quebraria a regra de uma pergunta por mensagem:

```
  1) ✅ RECOMENDADA — eu abro <o arquivo, ou a pasta> para você agora
     <o que vai aparecer quando abrir, em uma linha>
  2) eu mesmo abro — o caminho está aí em cima
  3) outra coisa que você tem em mente
```

Não havendo lista naquela mensagem, o caminho vai com a oferta em uma linha, e
quem a recebe é a lista do gate seguinte. **Abra só depois da escolha** — janela
que sobe sozinha por cima do que a pessoa estava fazendo é a versão chata da
ajuda. E o que abre é sempre o programa que já é dela: `explorer` (ou `start`)
no Windows, `open` no macOS, `xdg-open` no Linux — pasta no gerenciador de
arquivos, arquivo no aplicativo de sempre.

Onde a skill já manda abrir por conta própria — as páginas HTML feitas para quem
não lê código, que você abre no navegador antes de dar o caminho —, continue
abrindo. A oferta é para todo o resto.
**Pergunta técnica não se responde no escuro: ofereça ver.** Quando a escolha
depender de imaginar como uma coisa fica — uma tela, uma lista cheia, um
gráfico, o efeito de guardar de um jeito ou de outro —, acrescente **uma opção a
mais na mesma lista**: *"me mostra os dois antes de eu escolher"*. Nunca como
pergunta à parte: pergunta empilhada quebra a regra de uma por mensagem, e a
oferta que chega sozinha vira formalidade que se aprende a recusar.

O sinal mais forte de que a página é necessária é a resposta **"tanto faz"** ou
**"o que você achar melhor"**. Quase nunca é indiferença: quase sempre é sinal
de que a pessoa não conseguiu imaginar a diferença. Aí ofereça mostrar, em vez
de anotar o que você deduziu e seguir.

Quem desenha é a **`skill-07-designer-de-telas`**, em `mockups/exemplos/`, com **as
alternativas lado a lado** — uma página que compara, e não uma que ilustra. Ela
não substitui a escolha: mostrada a página, a pergunta é feita de novo, igual.
Não explique o que não foi perguntado.

## Fim de rodada

Esta skill fecha em **dois momentos**, e o segundo só existe depois do primeiro.

**Antes do commit fundador** — árvore criada e arquivos de raiz escritos. Relate
o que foi feito e ofereça as saídas, sem recomendar nenhuma. Saída sem objeto
não entra na lista: confira o que cada uma teria antes de montar.

**A ordem do gate é revisão antes de commit, e não é decorativa.** Commit grava;
revisão é o que descobre o que não se quer gravar. Invertida a ordem, o erro
entra no histórico — e de lá ele sai caro, ou não sai.

  1) revisão → `skill-09-revisor-de-codigo` — **só se alguma lente tiver
     objeto**. Com o projeto recém-fundado, quase sempre é só a de manutenção
     sobre os arquivos de raiz; diga isso em vez de listar as cinco
  2) commit → `skill-10-controlador-de-versoes` — **só se houver
     alteração pendente**. Não havendo, diga que não há o que registrar, em uma
     linha, e não ofereça. Pendência que ainda não passou por nenhuma lente sai
     marcada: **commit ⚠ ainda não revisado**

O ⚠ **não proíbe** — quem decide continua sendo o usuário, e a fundação de um
projeto novo é justamente um caso em que gravar antes de revisar costuma ser o
certo. O que a marca impede é a pessoa **descobrir depois** que gravou sem
ninguém ter olhado.

**Nunca apresente o commit como a saída natural do trabalho pronto.** "Ficou
pronto, commito?" é a frase que treina alguém a gravar sem conferir — e, uma vez
treinado, ninguém desaprende.

**Depois que o commit fundador existir** — a fundação está gravada e não há nada
pendente. A rodada não acaba aqui: proponha, nesta ordem e uma coisa de cada
vez:

  1) o repositório online e o envio da fundação (etapa 5)
  2) o backlog das funcionalidades previstas (etapa 6)
  3) a passagem para `skill-05-redator-de-funcionalidade`, que transforma
     o primeiro item do backlog em spec

Fundação gravada só na máquina, sem lista do que vem depois, é o ponto em que
projeto novo costuma parar: parece pronto, e a sessão seguinte não tem por onde
começar. Por isso as três propostas acima são obrigatórias — recusar cada uma é
direito do usuário, deixar de oferecer não é opção sua.

Sem a escolha do usuário a rodada fica em aberto: nada é gravado, nada é
enviado, nada é revisado, e você não escolhe por ele.

**Commit é ato do usuário, e envio também.** Nenhuma skill, exceto a
`skill-10-controlador-de-versoes`, executa commit. Terminar um trabalho não
autoriza registrá-lo, e registrá-lo não autoriza enviá-lo.

## Regras que nunca mudam

- **Pergunta vai como texto no chat, nunca como seletor** — lista numerada, a
  opção 1 marcada `✅ RECOMENDADA`, e sempre a opção "outra".
- **A stack precisa estar aprovada** antes de qualquer arquivo criado; a
  aprovação é da skill anterior, e esta confere se aconteceu.
- **Segredo nunca versionado**: `.env` fora, `.env.example` dentro.
- **`dados-exemplo/` sem dado real**, sempre com procedência declarada.
- **Repositório online nasce fechado**, e aberto só com escolha expressa de quem
  é dono do projeto. Silêncio nunca vale por "aberto".
- **Nada é enviado sem "sim" expresso**, e nunca antes do commit fundador.
- **Skills só em `.claude/skills/`** — é de onde o agente carrega.
- **Artefato gerado nunca commitado nem editado à mão** (`builds/`) — e o atalho
  de `abrir/`, que não é gerado, **nunca é ignorado**.
- **Teste ao lado do código** que ele cobre.
- **Arquivo de raiz com conteúdo real**, nunca placeholder.
- **Cada pasta tem dono**: uma skill ou uma pessoa que escreve nela.

## Checklist

- [ ] Toda pergunta foi texto no chat, em lista numerada — nenhum seletor, e a
      recomendada em primeiro, marcada com `✅ RECOMENDADA`
- [ ] Nenhuma pergunta aberta e nenhuma de sim ou não — nem para confirmar
      entendimento, nem para aprovar o que eu propus
- [ ] Todo caminho de pasta ou arquivo citado veio com a oferta de eu abrir, na
      mesma mensagem
- [ ] Requisitos levantados e stack aprovada antes do primeiro arquivo
- [ ] Árvore criada, adaptada ao projeto, sem pasta vazia sem destino
- [ ] `CLAUDE.md` com conteúdo real, incluindo o combinado do levantamento
- [ ] Convenção de comentário no `CLAUDE.md`: português, o porquê e não o quê
- [ ] `.gitignore` escrito **antes** do primeiro commit, cobrindo `.env` e todo `.env.<ambiente>`
- [ ] `.env.example` só com nomes, declarando o ambiente na primeira linha; `.env` fora do histórico
- [ ] `.claude/settings.json` escrito com as regras de negação, e a consequência de negar o `.env` dita ao usuário na hora
- [ ] Separação de desenvolvimento e produção decidida na fundação: arquivo de configuração por ambiente, banco separado e ambiente visível na tela
- [ ] As três regras duras das premissas transcritas no `CLAUDE.md`
- [ ] `README.md` de `dados-exemplo/` declarando a procedência sintética
- [ ] Nenhum dado real, nenhum segredo, nenhum esqueleto de funcionalidade
- [ ] Commit fundador deixado para a `skill-10-controlador-de-versoes`, apresentado e aprovado lá
- [ ] Modo perguntado na primeira vez desta skill na sessão — ou herdado, declarado ou inaplicável, dito em uma linha
- [ ] Pergunta que dependia de imaginar ofereceu ver antes de escolher, como opção na mesma lista
- [ ] Rodada fechada pelo gate, oferecendo só as saídas que têm objeto, sem escolher pelo usuário
- [ ] Repositório online proposto **depois** do commit fundador, com fechado/aberto perguntado à parte e fechado por padrão
- [ ] O que vai ser enviado conferido e mostrado, e envio só com "sim" expresso, para a branch inicial
- [ ] `especificacoes/backlog.md` escrito a partir do levantamento, uma linha por funcionalidade, sem detalhe
- [ ] `especificacoes/backlog.html` gerado pela `skill-07-designer-de-telas`, espelhando o `.md` e sem edição à mão
- [ ] Mapa do entendimento do levantamento gerado, quando o projeto nasceu do zero
- [ ] Backlog apresentado e confirmado, e a passagem para a `skill-05-redator-de-funcionalidade` proposta com o usuário escolhendo o primeiro item

## O pacote inteiro

Estas skills são um ciclo, e **qualquer uma pode chamar qualquer outra** quando o
trabalho pedir. Saber que as outras existem é o que evita refazer do zero um
procedimento que já está escrito em outro lugar — e o que permite devolver o
assunto para a dona dele, em vez de improvisar.

| # | Skill | Para quando |
| --- | --- | --- |
|  | `skill-00-mapa-skills` | desenhar o mapa do pacote instalado, e conferir o que nele não fecha |
|  | `skill-01-iniciar-projeto` | dar a partida: skills instaladas, máquina pronta, lugar do projeto |
|  | `skill-02-analista-de-requisitos` | abrir trabalho novo e levantar o que ele precisa |
|  | `skill-03-arquiteto-de-solucao` | escolher com o que o programa vai ser feito |
|  | `skill-04-organizador-de-ambiente` | fundar o projeto, e saber onde cada arquivo mora |
|  | `skill-05-redator-de-funcionalidade` | fechar o escopo de uma funcionalidade |
|  | `skill-06-modelador-de-dados` | propor como os dados se organizam, e desenhar o banco |
|  | `skill-07-designer-de-telas` | decidir o visual antes de escrever a tela |
|  | `skill-08-construtor-de-funcionalidades` | escrever o programa, etapa por etapa |
|  | `skill-09-revisor-de-codigo` | conferir o que foi construído, por uma lente |
|  | `skill-10-controlador-de-versoes` | registrar o trabalho em commit |
|  | `skill-11-gerente-de-entrega` | pôr a versão nova nas mãos de quem usa |
|  | `skill-12-nova-sessao` | montar o prompt de uma sessão dedicada, ou conduzir a atividade aqui |

A ordem é a do ciclo comum, não uma obrigação: trabalho pequeno pula etapas, e
trabalho que dá errado volta. O que não se pula é o gate — o ponto em que se
para e uma pessoa decide.

**Apareceu no caminho assunto que é de outra skill, nomeie a skill e devolva** em
vez de resolver por conta própria. Duas skills fazendo a mesma coisa de jeitos
diferentes é como um projeto começa a se contradizer.

Nada aqui presume um tipo de projeto, uma área ou um jeito de trabalhar: serve
para programa de uso pessoal, ferramenta de trabalho, ou o que mais a pessoa
resolver construir.

## Relação com outras skills

- A pasta do projeto, o histórico ligado e o pacote de skills instalado →
  **`skill-01-iniciar-projeto`**, que roda antes de todas. A ferramenta que a
  stack exige volta para a etapa 2 dela, chamada aqui na etapa 0.
- Os requisitos → **`skill-02-analista-de-requisitos`**; a stack aprovada →
  **`skill-03-arquiteto-de-solucao`**, cuja escolha e motivo esta skill registra no
  `CLAUDE.md`.
- O primeiro commit → **`skill-10-controlador-de-versoes`** (exceção do commit fundador, que é de branch e não de gate).
- O `especificacoes/backlog.md` é escrito **aqui** e lido pela
  **`skill-05-redator-de-funcionalidade`**, que consome um item por vez.
  A lista é desta skill; o detalhe de cada item nunca é.
- A spec que vai morar em `especificacoes/specs/` → **`skill-05-redator-de-funcionalidade`**.
- Os rascunhos de `mockups/` → **`skill-07-designer-de-telas`**, que usa
  uma pasta por área. A área `revisoes` guarda as páginas de antes e depois
  pedidas pela **`skill-09-revisor-de-codigo`**.
- O artefato de `builds/` → **`skill-11-gerente-de-entrega`**. O atalho
  de `abrir/`, que é o oposto dele — versionado, escrito à mão, do dia a dia —
  → **`skill-08-construtor-de-funcionalidades`**, na primeira etapa que
  dá o que ver.
- A convenção de comentário registrada aqui é seguida pela
  **`skill-08-construtor-de-funcionalidades`** ao escrever e conferida pela
  **`skill-09-revisor-de-codigo`** na lente de clareza.

## Manutenção da skill

Atualizar quando:
- Uma pasta da árvore se mostrar sem uso real (sai) ou faltar destino para um
  artefato que o projeto passou a produzir (entra).
- Surgir arquivo de raiz que todo projeto novo passe a precisar.
- O agente passar a carregar skills de outro caminho.

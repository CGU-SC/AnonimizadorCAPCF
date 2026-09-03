---
name: skill-01-iniciar-projeto
description: A PARTIDA — a primeira organização, antes de existir projeto, requisito ou linha de código. Faz três coisas e só elas, nesta ordem, cada uma com aprovação expressa. (1) CONFERE SE O PACOTE DE SKILLS ESTÁ EM `.claude/skills/`, o único lugar de onde o agente carrega skill, e PROPÕE A INSTALAÇÃO quando não está — passando calada quando está tudo lá. (2) CONFERE O QUE A MÁQUINA PRECISA TER para o trabalho começar (o histórico, o editor, o terminal), conduzindo a instalação do que faltar um passo por vez, com o comando de versão como prova; a ferramenta que a STACK exige não é aqui, é a volta que a `skill-04-organizador-de-ambiente` pede depois da stack aprovada. (3) DECIDE ONDE O PROJETO VAI MORAR — a pasta, que a partir dali é a raiz e o mundo do agente — e LIGA O HISTÓRICO com `git init`, conferindo a identidade do git antes que ela derrube o primeiro commit. Fecha entregando para a `skill-02-analista-de-requisitos`. NÃO levanta requisitos, NÃO escolhe a stack, NÃO cria a árvore de pastas nem arquivo de raiz (isso é `skill-04-organizador-de-ambiente`) e NÃO commita. Use na primeira sessão de um projeto novo, quando o agente não estiver enxergando as skills, quando o pacote entrar num projeto que já existe, ou em máquina nova. É uma das TRÊS skills sem gate de sessão dedicada — as outras são a `skill-00-mapa-skills`, que lê e desenha sem nada a distribuir, e a `skill-10-controlador-de-versoes`, porque commit só existe onde o pendente está. Esta roda sempre aqui, porque é ela que deixa a próxima sessão possível.
---

# Iniciar Projeto

Antes de existir projeto, existe uma máquina, uma pasta e um agente que ainda
não sabe nada. Esta skill é a **partida**: a meia hora que se gasta uma vez para
que todas as sessões seguintes comecem em pé.

Ela faz **três coisas, e só elas**, nesta ordem:

1. **As skills instaladas** — o agente enxerga o pacote, ou está trabalhando de
   memória?
2. **A máquina pronta** — o que precisa estar instalado para o trabalho começar.
3. **O lugar do projeto** — em que pasta ele vai morar, com o histórico ligado.
   Histórico, aqui, é o **git**: o caderno que guarda cada versão do projeto e
   permite voltar a qualquer uma delas.

E então **entrega para a `skill-02-analista-de-requisitos`**, que é quem pergunta
o que o programa vai fazer. Aqui não se pergunta isso, nem se decide nada sobre
o programa: esta skill prepara o chão, não constrói em cima dele.

**Esta é uma das três skills do pacote sem o gate de "aqui, ou em outra
sessão?"** — as outras são a do mapa das skills, que lê e desenha sem nada a
distribuir, e a do commit, que só existe onde o trabalho pendente está. O motivo aqui é simples: não dá para preparar o texto de uma sessão
dedicada quando o agente ainda não enxerga as skills que essa sessão deveria
seguir. Ela roda **sempre aqui**, e é curta de propósito.

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

## A exceção que esta skill carrega

A premissa 1 fala da raiz do projeto — e esta é a única skill que trabalha
**antes de a raiz existir**. Enquanto ela não existir, o mundo do agente é
**a pasta onde a sessão abriu**, e mais nada.

Ir buscar arquivo em outro lugar — o pacote de skills que ficou em `Downloads`,
uma pasta na Área de Trabalho, um pen drive — continua exigindo o que a premissa
exige: **o caminho dito pelo usuário e a tarefa dita**, uma vez, para aquela
tarefa. Escolhida a pasta do projeto na etapa 3, ela vira a raiz, e a premissa
passa a valer inteira daí em diante.

A cerca escrita — o arquivo `.claude/settings.json` — não é desta skill:
quem a escreve é a **`skill-04-organizador-de-ambiente`**, na fundação.

## Contrato

| | |
| --- | --- |
| **Lê** | A pasta onde a sessão abriu; o `.claude/skills/`, se existir; o que a máquina tem instalado, pelos comandos de versão |
| **Escreve** | O pacote de skills em `.claude/skills/`, com aprovação; o histórico iniciado (`git init`) na pasta escolhida; a identidade do git, quando faltar. **Nada mais** — nem pasta do projeto por dentro, nem arquivo de raiz, nem uma linha de código |
| **Pré-condição** | Nenhuma. Esta é a porta antes da porta: quando falta contexto, ela pergunta |

## Quando entra

- **Primeira sessão de um projeto novo**, antes de qualquer pergunta sobre o que
  o programa vai fazer.
- **O agente não está enxergando as skills** — o nome de uma skill é citado e
  nada acontece, ou o agente responde do jeito dele em vez do jeito do pacote.
- **Este pacote entra num projeto que já existe**, pela primeira vez.
- **Máquina nova, ou pessoa nova**, com o projeto já baixado do repositório e
  nada instalado ainda.

## O que NÃO faz

- **Não levanta requisitos** — isso é **`skill-02-analista-de-requisitos`**.
  Aqui não se pergunta o que o programa vai fazer, nem para quem.
- **Não escolhe a stack** — isso é **`skill-03-arquiteto-de-solucao`**. E é por
  isso que a etapa 2 não instala linguagem nem banco: antes da stack, não se
  sabe o que instalar.
- **Não cria a árvore de pastas nem os arquivos de raiz** — isso é
  **`skill-04-organizador-de-ambiente`**. Esta skill escolhe **onde** o projeto
  mora e liga o histórico; o que vai **dentro** é da outra.
- **Não commita.** `git init` cria o histórico vazio, e isso não é commit. O
  primeiro é o **commit fundador**, da
  **`skill-10-controlador-de-versoes`**, depois da árvore.
- Não escreve código, não desenha tela, não propõe funcionalidade.

## Procedimento

As três etapas são **na ordem**, e cada uma espera o "sim" antes de mexer em
qualquer coisa. Nenhuma delas se pula em silêncio: quando uma já está resolvida,
diga em uma linha e siga para a próxima.

### 1. As skills estão onde o agente as enxerga?

Um pacote de skills baixado e deixado numa pasta qualquer **não é lido pelo
agente** — ele nem fica sabendo que aquilo existe. O pacote só entra em cena
quando mora em um destes dois lugares:

- **`.claude/skills/` na raiz do projeto** — o recomendado: viaja com o projeto,
  vale para quem clonar depois e entra no histórico junto com o código.
- **`.claude/skills/` da pasta pessoal** — `~/.claude/skills/` no Mac e no
  Linux, `%USERPROFILE%\.claude\skills\` no Windows: vale para todos os
  projetos daquela máquina, e não viaja com o repositório.

Então a primeira coisa a fazer é **listar `.claude/skills/`** e ver se as treze
pastas `skill-*` estão lá:

```
ls .claude/skills/
```

Um atalho ajuda a descobrir isso: se esta skill foi acionada **pelo nome**, é
porque ela já está instalada em um dos dois lugares — o que falta conferir é se **as outras doze** estão
junto. Se ela foi acionada porque alguém apontou o arquivo na mão, nada está
instalado ainda.

**Se estiver tudo lá, não faça cerimônia**: diga em uma linha que o pacote está
instalado e siga para a etapa 2. Checagem que passa é checagem silenciosa.

**Se não estiver**, pare aqui e **proponha** a instalação — não a execute
sozinho:

```
Uma coisa antes: as skills ainda não estão em `.claude/skills/`. Sem isso o
agente não as enxerga sozinho, e o roteiro só vale enquanto alguém aponta o
arquivo na mão, uma skill de cada vez.

  1) ✅ RECOMENDADA — instalar no projeto: copio as treze pastas para
     `.claude/skills/` daqui; passam a valer para quem abrir este projeto e
     entram no histórico junto com ele
  2) instalar na sua pasta pessoal — valem para todos os seus projetos nesta
     máquina, mas não viajam com o repositório
  3) seguir assim mesmo — eu continuo, e você aponta o arquivo da skill toda
     vez que uma for necessária
  4) outra coisa que você tem em mente
```

O que costuma aparecer, e o que fazer em cada caso:

| O que você encontra | O que fazer |
| --- | --- |
| As pastas soltas na raiz (`skills/`, uma pasta descompactada, um nome qualquer) | Propor **mover** para `.claude/skills/`, dizendo o que sai de onde e chega aonde |
| Um `.zip` ainda fechado | Propor descompactar e instalar — e nunca descompactar por cima de pasta com conteúdo sem dizer antes o que seria substituído |
| Só algumas das treze | Dizer **quais faltam, pelo nome**, e propor completar: pacote pela metade quebra no meio do caminho, na hora em que uma skill chama outra que não está lá |
| `.claude/skills/` já existe, com versão anterior das mesmas skills | Não sobrescrever calado — diga que já existe e pergunte se substitui |
| As skills estão fora da pasta onde a sessão abriu (Downloads, Área de Trabalho, pen drive) | Vale a **exceção** desta skill: peça o **caminho** e a autorização, em uma pergunta só — e então **copie, nunca mova**: o original fica onde está |

Instalado, **avise em uma linha**: o agente carrega as skills **quando a sessão
abre**, e skill copiada no meio da conversa pode não ser reconhecida até a
sessão ser fechada e aberta de novo. Ofereça retomar daqui quando isso
acontecer.

### 2. A máquina tem o que o trabalho exige

Esta etapa tem **dois momentos**, e aqui acontece só o primeiro.

**Agora, o que independe da stack** — o que todo projeto precisa, seja ele qual
for:

| O que | Para que serve | Como se confere |
| --- | --- | --- |
| O **histórico** (`git`) | Registra cada alteração e permite voltar atrás | `git --version` |
| Um **editor de código** | Ver e abrir os arquivos do projeto sem depender do chat | abrir a pasta nele |
| O **terminal** onde a sessão roda | É por ele que tudo acontece | já está em uso |

**Depois, o que a stack exigir** — a linguagem, o banco, e o programa que
transforma o projeto no arquivo que se instala. Esse
momento **não é aqui**: ele acontece quando a stack já foi aprovada pela
**`skill-03-arquiteto-de-solucao`**, e quem chama esta etapa de volta é a
**`skill-04-organizador-de-ambiente`**, antes de escrever os comandos do
`CLAUDE.md`. Instalar linguagem antes da stack é apostar em uma decisão que
ainda não foi tomada.

Regras da etapa, valendo nos dois momentos:

- **Um passo por vez.** Instale uma coisa, confirme que funcionou, e só então a
  próxima. Três instalações em paralelo viram três erros misturados.
- **Diga antes o que é e para que serve**, em uma frase do dia a dia. Ninguém
  aprova o que não entendeu.
- **A prova é o comando de versão**, com a saída real colada na conversa. "Deve
  estar instalado" não é conferência.
- **Nada é instalado calado**, e nada é instalado "de brinde" porque costuma ser
  útil.
- **Já instalado é assunto encerrado**: diga a versão que apareceu e siga. Não
  proponha atualizar o que já funciona.

### 3. Onde o projeto vai morar

A pasta escolhida aqui é a **raiz** — o mundo do agente daí em diante. Pergunte,
com o caminho completo em bloco próprio, e espere a escolha:

```
Onde este projeto vai morar? A pasta que você escolher vira a casa dele: é
dentro dela que eu leio, escrevo e rodo qualquer coisa, e de fora dela eu não
saio sem você pedir.

  1) ✅ RECOMENDADA — uma pasta nova só para ele: nada dentro se confunde com
     outro trabalho, e o dia de copiar, apagar ou levar para outra máquina é
     um arrastar de pasta
  2) esta pasta mesmo, onde a sessão abriu
  3) outra coisa que você tem em mente
```

Quatro coisas que se conferem antes de aceitar a pasta, e que custam caro
depois:

- **Pasta sincronizada com nuvem** — OneDrive, Dropbox, Google Drive — é o lugar
  mais comum de histórico corrompido: dois programas mexendo nos mesmos arquivos
  ao mesmo tempo. Se for o caso, **diga o risco e recomende outra pasta**; a
  decisão continua sendo do usuário.
- **Caminho com espaço, acento ou emoji** funciona quase sempre, e quebra
  justamente no comando que ninguém esperava. Recomende um nome curto, sem
  acento e sem espaço.
- **Pasta que já tem coisa dentro** — liste o que tem **antes** de seguir. Pode
  ser o projeto certo, e pode ser a pasta errada.
- **Disco de rede ou pen drive** não é lugar de projeto em construção.

Escolhida a pasta, diga em uma linha que ela é a raiz a partir de agora.

### 4. O histórico ligado

O histórico é o que separa "mexi e não sei mais como estava" de "volto ao que
funcionava ontem". Explique em três linhas o que ele faz — **registra cada
alteração, mostra o que mudou e quando, e permite voltar atrás** — e nada além
disso. Aula de git não é aqui.

Antes de ligar, confira se já está ligado:

```
git status
```

**Se já existir histórico, não reinicie nada** — diga que já existe e siga.
`git init` em pasta que já tem histórico é o tipo de comando que parece
inofensivo e não é.

Não existindo, ligue:

```
git init
```

E confira, na mesma etapa, a **identidade do git** — o nome e o e-mail que vão
assinar cada alteração:

```
git config user.name
```

```
git config user.email
```

Se os dois vierem vazios, guarde: esse é o motivo mais comum de o **primeiro
commit falhar** horas depois, no meio da fundação, sem ninguém entender por quê. Configure agora, e
diga uma coisa antes de pedir o e-mail: **ele fica gravado no histórico**, e
histórico enviado para um repositório público é lido por qualquer um. Quem não
quiser o e-mail pessoal exposto usa o endereço sem resposta que o próprio
serviço oferece.

**E para aqui.** Nenhum commit: o primeiro é o **fundador**, e ele vem depois da
árvore de pastas, pela **`skill-10-controlador-de-versoes`**.

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
soltos no meio da frase. Nesta skill a regra pesa mais do que em qualquer outra:
quase tudo que o usuário faz aqui é copiar um caminho ou colar um comando, e no
meio do texto o olho perde a borda. Um bloco por coisa: dois comandos que se
digitam em momentos diferentes são dois blocos, na ordem em que se digitam.
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
**Instalação que dá errado não se contorna sozinha.** Erro de instalação é onde
quem não programa desiste. Mostre a mensagem de erro inteira, diga em uma frase
o que ela significa, e proponha **um** próximo passo — nunca três de uma vez, e
nunca "tente de novo".
Não explique o que não foi perguntado.

## Fim de rodada

Esta skill fecha com a partida dada e nada construído. Relate em três linhas o
que ficou de pé — pacote instalado, ferramentas conferidas com as versões que
apareceram, pasta escolhida e histórico ligado — e ofereça a saída:

  1) o levantamento do que o programa precisa fazer →
     **`skill-02-analista-de-requisitos`**

**Não há commit a oferecer** quando o projeto nasceu agora: o histórico acabou
de ser criado e a fundação ainda não existe. Dizer isso em uma linha vale mais
do que oferecer uma saída vazia.

**Há uma exceção:** quando o pacote foi instalado dentro de um projeto que **já
tinha histórico**, o `.claude/skills/` é alteração pendente de verdade. Aí a
saída inclui o commit, pela **`skill-10-controlador-de-versoes`**, e ele sai
marcado como o que é: **commit ⚠ ainda não revisado**.

E se as skills foram copiadas **com esta sessão aberta**, a última frase é a
mais importante de todas: **feche e abra a sessão** antes de seguir para a
`skill-02-analista-de-requisitos`. Sem isso, o agente continua sem enxergar o
pacote que acabou de ser instalado, e a próxima skill não vai ser encontrada
pelo nome.

## Regras que nunca mudam

- **Pergunta vai como texto no chat, nunca como seletor** — lista numerada, a
  opção 1 marcada `✅ RECOMENDADA`, e sempre a opção "outra".
- **A ordem é skills → máquina → lugar.** Instalar ferramenta antes de saber se
  o agente enxerga as skills é gastar tempo no escuro.
- **Nada é instalado sem o "sim"** — nem skill, nem ferramenta, nem pasta criada.
- **O comando de versão é a prova.** Sem a saída real na conversa, a ferramenta
  não está conferida.
- **`git init` não é commit**, e esta skill não commita.
- **Linguagem, banco e empacotador não se instalam aqui** — a stack ainda não
  foi escolhida, e instalar antes é apostar numa decisão que ninguém tomou.
- **Escolhida a raiz, o agente não sai dela** sem caminho e tarefa nomeados.

## Checklist

- [ ] Toda pergunta foi texto no chat, em lista numerada — nenhum seletor, e a
      recomendada em primeiro, marcada com `✅ RECOMENDADA`
- [ ] Nenhuma pergunta aberta e nenhuma de sim ou não — nem para confirmar
      entendimento, nem para aprovar o que eu propus
- [ ] Todo caminho de pasta ou arquivo citado veio com a oferta de eu abrir, na
      mesma mensagem
- [ ] Conferi `.claude/skills/` antes de qualquer outra coisa
- [ ] Faltando skill, propus a instalação e esperei o "sim" — não copiei nada por
      conta própria
- [ ] Disse quais faltavam, pelo nome, em vez de dizer só "faltam algumas"
- [ ] Avisei que skill copiada com a sessão aberta só vale depois de reabrir
- [ ] Conferi o histórico e o editor, com o comando de versão e a saída real
- [ ] Não instalei nada da stack — nem "para adiantar"
- [ ] Instalei um passo por vez, dizendo antes o que era e para que servia
- [ ] A pasta do projeto foi escolhida pelo usuário, e eu disse os riscos que vi
      (nuvem, acento, pasta com coisa dentro)
- [ ] Não rodei `git init` em pasta que já tinha histórico
- [ ] Conferi nome e e-mail do git, e avisei que o e-mail fica gravado
- [ ] Não commitei
- [ ] Fechei entregando para a `skill-02-analista-de-requisitos`

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

- A saída desta skill é sempre a **`skill-02-analista-de-requisitos`**: partida
  dada, a próxima pergunta é o que o programa precisa fazer.
- A **ferramenta que a stack exige** volta para a etapa 2 desta skill, chamada
  pela **`skill-04-organizador-de-ambiente`** depois que a
  **`skill-03-arquiteto-de-solucao`** teve o "sim".
- A **árvore de pastas**, os **arquivos de raiz** e a **cerca do agente**
  (`.claude/settings.json`) são da **`skill-04-organizador-de-ambiente`**. Esta
  skill entrega a pasta e o histórico; o que vai dentro é lá.
- O **commit fundador** é da **`skill-10-controlador-de-versoes`**, depois da
  fundação — nunca aqui.
- O **repositório online** é da **`skill-04-organizador-de-ambiente`**, e só
  depois do commit fundador: não se envia o que ainda não foi gravado.

## Manutenção da skill

Atualizar quando:
- O pacote ganhar ou perder skill — a etapa 1 confere **treze**.
- O agente passar a carregar skills de outro caminho.
- Aparecer ferramenta que todo projeto novo passe a precisar, seja qual for a
  stack.
- A etapa 3 começar a receber sempre a mesma resposta — sinal de que a pergunta
  virou formalidade e o critério precisa ser revisto.

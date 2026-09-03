---
name: skill-12-nova-sessao
description: Abre um trabalho novo com o agente (feature, revisão, checagem técnica, correção de bug) em um de dois modos, SEMPRE perguntando qual antes de começar — MODO A, montar o PROMPT INICIAL de uma sessão dedicada; MODO B, executar a atividade aqui mesmo. Nos dois casos valida o entendimento ANTES de qualquer código, faz reconhecimento dirigido do repositório e propõe formas de solução quando o pedido chega como solução pronta; depois entrega o prompt autossuficiente (A) ou conduz a atividade (B), na ordem análise → especificação proporcional → fases pequenas → testes → commits aprovados um a um. Use ao COMEÇAR um trabalho novo. NO INÍCIO DE CADA FUNCIONALIDADE — e na primeira vez que é acionada numa sessão — oferece e RECOMENDA montar o PROMPT de uma sessão dedicada, em vez de conduzir aqui; herda o modo quando chega pelo gate de outra skill dentro da mesma funcionalidade, e volta a perguntar quando a funcionalidade é outra. O PROMPT que ela monta manda a sessão dedicada FECHAR com revisão pela `skill-09-revisor-de-codigo`, uma lente por rodada, e não no último commit. NÃO levanta requisitos por dimensão (isso é `skill-02-analista-de-requisitos`, que também abre trabalho novo e é a porta padrão do ciclo): esta entra quando o que se quer é o PROMPT de uma sessão dedicada, ou a condução de uma atividade avulsa que não começa por levantamento.
---

# Nova Sessão

A falha mais cara de programar conversando com uma IA — o que se chama de *vibe
coding* — não é código errado. É **código certo para o problema errado**,
produzido rápido e com toda a confiança do mundo. Ele funciona, passa nos
testes, e resolve uma coisa que ninguém pediu.

Esta skill existe para gastar quinze minutos entendendo o pedido antes de gastar
horas construindo.

A skill tem **dois modos**, e a primeira coisa que faz é perguntar qual:

- **MODO A — prompt.** Entrega um bloco de texto: a primeira mensagem de uma
  conversa NOVA com o agente. Ela tem que se bastar sozinha — quem abre a
  conversa nova não viu nada do que foi falado aqui —, ser específica, e citar
  os arquivos de verdade do projeto. Nesse modo a skill não constrói nada, não
  escreve a spec final, não abre branch e não commita: isso é trabalho da
  sessão que receber o texto.
- **MODO B — execução aqui.** Conduz a própria atividade nesta conversa mesmo,
  seguindo o roteiro que o modo A escreveria.

A sequência é obrigatória e **igual nos dois modos**: **modo escolhido →
entendimento confirmado → reconhecimento do que já existe →** o texto do prompt
(A) ou a execução (B). Pular o entendimento produz trabalho que resolve o
problema errado com precisão.

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
| **Lê** | O pedido; o repositório, quando já existe; o `CLAUDE.md` do projeto; o catálogo de skills disponíveis |
| **Escreve** | **Modo A:** nada em disco — só o texto do prompt, no chat. **Modo B:** o entendimento validado, no chat, e arquivo do projeto só o que a atividade pedir, fase a fase |
| **Pré-condição** | Nenhuma. Esta é a porta de entrada: quando falta contexto, ela pergunta, não pressupõe |

Pré-condição que não se cumpre **não se contorna**: pare, diga qual artefato
falta e qual skill o produz, e pergunte em uma pergunta só. Seguir com a
entrada faltando é o jeito mais comum de produzir trabalho bem-feito sobre
premissa inventada.

## Quando entra

- **Trabalho novo de qualquer tamanho** — projeto do zero, funcionalidade,
  revisão de algo que já existe, checagem técnica, correção de bug.
- Quando o pedido chega **como solução pronta** ("põe um botão de exportar
  aqui") e ninguém disse qual é o problema por trás.
- Quando a conversa atual já está longa e o trabalho novo merece contexto limpo.

É uma **porta de entrada do pacote**, ao lado da
`skill-02-analista-de-requisitos`, e o corte entre as duas é o que o trabalho
pede primeiro: quando ele começa por **levantar o que precisa**, dimensão por
dimensão, a porta é a 02; quando o que se quer é o **prompt de uma sessão
dedicada**, ou conduzir uma atividade que já chega entendida, a porta é esta.
Nenhuma outra skill a oferece no **gate de fim de rodada** — mas as que têm o gate de
modo a nomeiam ali, quando a resposta é a sessão dedicada e o prompt precisa ser
escrito por alguém.

## O que NÃO faz

- **Não levanta os requisitos dimensão por dimensão** — valida o entendimento e
  devolve para a **`skill-02-analista-de-requisitos`**, que é quem pergunta
  por escopo, dados, fluxos, estados e regras.
- **Não escolhe a stack** — isso é **`skill-03-arquiteto-de-solucao`**.
- **Não cria pasta nem arquivo** — isso é
  **`skill-04-organizador-de-ambiente`**.
- **Não escreve spec** e **não implementa**. No MODO A ela não executa nada:
  entrega o prompt e para.

## 0. Modo de trabalho (pergunta obrigatória, SEMPRE)

Antes de qualquer outra coisa — antes até de reformular o pedido — pergunte:

> **Monto o prompt para uma sessão nova, ou executo a atividade aqui nesta
> sessão?**

| Resposta | Modo | Caminho |
| --- | --- | --- |
| "monta o prompt", "prepara pra outra sessão" | **A** | passos 1 → 2 → 3 → 4 → 5 |
| "executa aqui", "faz agora", "pode ir fazendo" | **B** | passos 1 → 2 → 3 → 6 |

**Pergunte sempre, mesmo quando parecer óbvio.** "Vamos implementar X" tanto
pode ser pedido de execução imediata quanto de preparação do prompt de uma
sessão dedicada — e deduzir errado custa a sessão inteira: ou você entrega um
texto quando esperavam código pronto, ou começa a mexer no repositório quando
esperavam só a instrução.

Resposta ambígua ("tanto faz") **não é escolha do modo B**: é o caso em que a
recomendação vale mais. Diga que vai montar o prompt, e siga pelo modo A.

**A pergunta volta no início de cada funcionalidade**, quando a escrita ou a
construção de uma nova começa — não só na primeira vez que a skill entra na
sessão. Funcionalidade nova, pergunta nova: outro item do backlog, uma spec
nova, ou uma construção que começa depois de outra ter sido dada por concluída.
Ajuste dentro da funcionalidade em andamento não repõe a pergunta.

## 1. Loop de entendimento (bloqueante — vale nos DOIS modos)

Antes de abrir QUALQUER arquivo de código, reformule o pedido **com suas
próprias palavras** — nunca repetindo as do solicitante, porque repetir não
prova compreensão. Quatro blocos curtos:

- **Objetivo** — o que se quer alcançar, em uma frase.
- **Problema** — o que está errado, faltando ou custando caro hoje.
- **Resultado esperado** — como se reconhece que terminou, do ponto de vista de
  quem usa.
- **Limites e requisitos** — o que está fora de escopo, o que não pode quebrar,
  restrições de prazo/dado/permissão/compatibilidade.

Marque explicitamente o que você **inferiu** (não foi dito) e o que ficou
**ambíguo** — é aí que o erro mora.

Termine perguntando, de forma direta: **"O entendimento está correto?"**

- **"Não" / correção** → peça o esclarecimento específico que falta e
  **reformule de novo, do zero**, com as próprias palavras. Pergunte outra vez.
  Repita quantas vezes forem necessárias.
- **"Sim"** (confirmação expressa) → só então siga para o passo 2.

Silêncio, "acho que sim" ou uma resposta que muda o escopo **não são
confirmação**. Sem "sim" explícito, o loop continua.

**Confirmação parcial também não é confirmação.** Quando você fez várias
perguntas e a resposta cobre só algumas, o resto NÃO está aprovado por tabela:
volte e pergunte de novo, nomeando item por item o que ficou sem resposta. É a
falha mais comum na prática — quem responde a última pergunta acredita ter
respondido todas, e quem perguntou acredita ter sido respondido.

Proibido nesta etapa: propor solução, listar arquivos que "provavelmente"
mudam, estimar esforço, começar a redigir o prompt.

## 2. Reconhecimento dirigido (depois do "sim" — vale nos DOIS modos)

Objetivo: ancorar o prompt em **nomes reais**, não em suposições. Levantamento
raso e rápido — a análise profunda é tarefa da sessão dedicada.

Levante só o suficiente para citar caminhos verdadeiros:

- os módulos/camadas envolvidos e como se chamam de verdade;
- os testes que já cobrem a área;
- specs, ADRs e documentação existentes sobre o assunto;
- **a skill específica que já cobre o procedimento** — se existir, o prompt
  manda segui-la, não reinventá-la.

Use busca por padrão (`Grep`/`Glob`) e, quando a varredura for ampla, um agente
de exploração. Não leia arquivos inteiros aqui: confirme que existem, o que
fazem e como se chamam.

Se o reconhecimento **contradisser** o entendimento confirmado ("isso já existe
e funciona", "o caminho passa por outro módulo"), **volte ao passo 1** e
reconfirme — o entendimento validado era sobre uma premissa que caiu.

## 3. Formas de solução (condicional — vale nos DOIS modos)

Um especialista de domínio quase sempre descreve a **solução que imaginou**, não
o problema que tem: "faz um botão que exporta isso" no lugar de "preciso
conferir esses dados rápido". Um agente obediente constrói o botão e ninguém
descobre que havia caminho melhor. Esta etapa existe para essa hora — e só
para ela.

**Entra quando** (basta um):
- o pedido chegou descrito como solução pronta, não como problema;
- o reconhecimento revelou caminho mais simples ou mais barato que o pedido;
- há mais de uma forma plausível, com custos claramente diferentes.

**Pula direto para o passo 4 quando**:
- o pedido já veio como problema bem posto e existe uma forma óbvia;
- é correção de bug (a forma é consertar a causa);
- o procedimento já é coberto por uma skill específica, que decide a forma.

**O que apresentar:** duas ou três formas **distintas** — não variações da
mesma. Cada uma com o que é em uma frase, o que custa (esforço, risco,
manutenção futura) e o que deixa de fora. Recomende uma, com o critério
explícito. Uma pergunta só, opções numeradas, e espere a escolha.

Três tamanhos do mesmo botão não são três alternativas: é a mesma forma três
vezes. Se você não consegue descrever em que as opções *discordam*, ainda não
há alternativas para apresentar.

**Se a forma escolhida for diferente da pedida, o entendimento do passo 1
mudou.** Registre a forma escolhida no bloco "Entendimento validado" do prompt,
com uma linha sobre o que foi descartado e por quê — senão a sessão nova recebe
um objetivo que já não é o combinado.

Não confundir com ADR: aqui se escolhe a **forma do produto**. Escolha técnica
com efeito duradouro que apareça no caminho vira **`skill-03-arquiteto-de-solucao`** na
sessão de execução, não aqui.

## 4. Montar o prompt — MODO A

Em pt-BR, segunda pessoa, endereçado à sessão nova. Precisa se sustentar
sozinho: quem o receber não terá acesso a esta conversa. O esqueleto:

```markdown
# <Título curto da atividade>

## Contexto do projeto
<stack, arquitetura em 3-4 linhas, regras duras e onde lê-las>

## Entendimento validado com o solicitante
- Objetivo / Problema / Resultado esperado / Limites / Fora de escopo

Este entendimento JÁ FOI confirmado — não o renegocie, mas avise se a análise
do código o contradisser.

## Pontos de partida no repositório
<caminhos reais, com uma linha do porquê de cada um>
<skill aplicável, quando houver: "siga .claude/skills/<nome>/SKILL.md">

## Como conduzir a sessão

### Fase 0 — análise (antes de qualquer alteração)
Estado atual frente ao pedido: o que já existe, implementações parciais,
dependências, convenções adotadas, impactos, riscos de regressão,
oportunidades de reúso, necessidade de testes/migração/documentação e
alternativas com trade-offs.

NÃO parta do princípio de que a solução sugerida é a certa. Se o código
mostrar caminho melhor (ou que nada precisa ser feito), diga isso com
evidência — arquivo e linha — antes de propor código.

### Fase 1 — especificação PROPORCIONAL ao tamanho
Escolha o artefato pelo tamanho e declare qual escolheu:
- **Uma fase, sem contrato público, migração ou decisão arquitetural novos**
  → acordo curto: duas a quatro linhas, com o critério de aceite.
- **Várias fases, ou contrato/migração/ADR envolvidos** → spec formal:
  problema, escopo e não-escopo, requisitos, critérios de aceitação
  verificáveis, casos de exceção, riscos, etapas e testes por etapa.

Pare e peça aprovação NOS DOIS CAMINHOS. Nenhuma linha de código antes
disso — encolhe o texto, nunca o gate. Se o escopo crescer no meio da
implementação, PARE e suba para a spec formal.

### Fase 2+ — implementação em fases pequenas
Cada fase cumpre o ciclo, sem pular etapa: analisar o trecho → detalhar a
alteração → implementar SÓ o escopo da fase → rodar testes → revisar →
corrigir → confirmar os critérios → oferecer as saídas de fim de rodada que
tiverem objeto (revisão antes de commit) e esperar a escolha. Escolhido o
commit, APRESENTAR o commit proposto (mensagem completa + o que entra e por
quê) e só com "sim" expresso, commitar. Sem escolha, a rodada fica em aberto.
Fase que cresce no meio do caminho vira duas fases.

### Fase final — fechar a sessão com revisão
Terminado o trabalho, a sessão NÃO se encerra no último commit: ela fecha
rodando a skill `skill-09-revisor-de-codigo`: UMA lente por rodada, escolhida
por quem pediu, e o conserto só do que for aprovado achado a achado. A lente
padrão do dia a dia é a crítica; quando a sessão vai terminar em entrega, ou
quando alguma coisa cheirou errado no caminho, a lente é a que cobre o que
cheirou — e nunca todas de uma vez, que é o mesmo que nenhuma.

## Regras invioláveis
<branch de trabalho; commit nunca automático, sempre por escolha minha; toda
rodada fecha oferecendo revisão antes de commit; a sessão fecha com a skill
de revisão, e não no último commit; commit apresentado um a um antes de
executar; um commit por etapa lógica; nada de `--no-verify` nem pular gate;
nada de editar artefato gerado; idioma e convenções do projeto>

## Verificação
<os comandos reais de teste/gate do projeto>

## Antes de começar
Reformule o pedido com suas palavras (objetivo, problema, resultado esperado,
limites) e confirme comigo. Só depois abra o código.
```

O bloco final é deliberado: a sessão nova **revalida** o entendimento com quem
a estiver conduzindo, mesmo já vindo com ele escrito. Duas barreiras contra o
problema errado custam menos que uma implementação inteira.

## 5. Entregar — MODO A

Entrega SEMPRE no chat, em bloco de código markdown, pronto para copiar.
**Nunca criar arquivo com o prompt** — o solicitante copia do próprio chat.

Feche dizendo, em duas linhas, o que ficou de fora do prompt de propósito e o
que a sessão nova provavelmente vai precisar perguntar.

## 6. Conduzir a atividade aqui — MODO B

**Não escreva o texto do prompt.** Conduza a sessão seguindo o mesmo roteiro
que o modo A escreveria — as seções "Como conduzir a sessão" e "Regras
invioláveis" do modelo do passo 4, aplicadas a você mesmo.

A ordem é a mesma, e os gates são os mesmos: análise antes de qualquer alteração,
especificação proporcional aprovada antes do código, fases pequenas, e cada
commit apresentado e aprovado antes de executar.

Se existir skill específica para o procedimento, **siga-a** — no modo B ela se
aplica a você diretamente, não vira citação num texto.

### O filtro que se perde no modo B (e como compensar)

No modo A há **duas** barreiras contra o problema errado: o entendimento
confirmado aqui, e o bloco "Antes de começar" que faz a sessão nova reformular
tudo ao receber o prompt. **No modo B a segunda barreira não existe** — quem
entendeu é quem executa, e não há um agente com contexto limpo para questionar
a premissa.

Compensações obrigatórias:

- Rigor redobrado no passo 1: nada de encurtar o loop porque "já está claro".
- Contradição encontrada na análise **volta ao solicitante**, em vez de ser
  resolvida por conta própria — é onde o modo A teria feito a pergunta.
- Depois da especificação aprovada, **pare de verdade**: é o último ponto em
  que o escopo ainda se corrige barato.

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
antes, quais travas desta skill valem lá, e o que **não** é para fazer. Quem escreve
esse texto é esta skill mesma — é para isso que ela existe.

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

Terminou a rodada, relate o que foi feito e ofereça as saídas, sem recomendar
nenhuma.

**No modo A não há gate a montar.** A rodada fecha na entrega do prompt: nada foi
alterado, não há o que revisar nem o que gravar, e oferecer as duas coisas
ensinaria que o gate é formalidade. Diga em uma linha que a sessão dedicada é o
próximo passo, e pare.

**Antes de montar a lista, confira o que cada saída teria de objeto.** Saída sem
objeto não entra na lista.

Oferecer commit quando não há nada alterado obriga a pessoa a escolher entre uma
opção real e uma vazia. Ela aprende, em uma rodada, que o gate é formalidade — e
a partir daí passa por ele sem ler.

**A ordem do gate é revisão antes de commit, e não é decorativa.** Commit grava;
revisão é o que descobre o que não se quer gravar. Invertida a ordem, o erro
entra no histórico — e de lá ele sai caro, ou não sai.

  1) revisão → `skill-09-revisor-de-codigo` — **só se alguma lente tiver
     objeto**. Não havendo, diga o que ainda falta existir para ela ter, e não
     ofereça
  2) commit → `skill-10-controlador-de-versoes` — **só se houver
     alteração pendente**. Não havendo, diga que não há o que registrar, em uma
     linha, e não ofereça. Pendência que ainda não passou por nenhuma lente sai
     marcada: **commit ⚠ ainda não revisado**
  3) levantar o que o trabalho precisa → `skill-02-analista-de-requisitos` —
     o caminho normal quando ainda há requisito a descobrir dimensão por
     dimensão. Fechado o entendimento aqui, o passo seguinte é direto: em
     projeto do zero, a stack, com a `skill-03-arquiteto-de-solucao`; em
     projeto que já existe, o escopo da funcionalidade, com a
     `skill-05-redator-de-funcionalidade`

O ⚠ **não proíbe**: quem decide continua sendo o usuário, e há caso legítimo de
gravar antes de revisar. O que a marca impede é a pessoa **descobrir depois** que
gravou sem ninguém ter olhado.

**Nunca apresente o commit como a saída natural do trabalho pronto.** "Ficou
pronto, commito?" é a frase que treina alguém a gravar sem conferir — e, uma vez
treinado, ninguém desaprende.

Sobrou uma saída só, ofereça uma. Não sobrou nenhuma, não invente gate: diga que
a rodada fechou sem pendência e qual é o próximo passo previsto.

Sem a escolha do usuário a rodada fica em aberto: nada é gravado, nada é
revisado, e você não escolhe por ele.

**Commit é ato do usuário.** Nenhuma skill, exceto a
`skill-10-controlador-de-versoes`, executa commit. Terminar um trabalho não
autoriza registrá-lo.

## Regras que nunca mudam

- **Perguntar o modo antes de tudo** — nunca deduzir pelo tom do pedido.
- Nenhum código, nenhuma proposta de solução antes do "sim" expresso.
- Todo caminho citado no prompt existe de verdade (foi conferido no passo 2).
- O prompt manda **analisar antes de propor** e **especificar antes de codar**.
- O prompt exige aprovação explícita de cada commit — nunca commit direto.

## Checklist

**Os dois modos:**

- [ ] Perguntei o modo ANTES de tudo — não deduzi pelo tom do pedido
- [ ] Reformulei com minhas palavras, marcando inferências e ambiguidades
- [ ] Perguntei explicitamente se o entendimento estava correto
- [ ] Repeti o loop até a confirmação expressa
- [ ] Reconhecimento feito: todo caminho citado existe
- [ ] Avaliei se o pedido veio como solução pronta — e, se veio, apresentei formas distintas
- [ ] Forma escolhida diferente da pedida foi registrada no entendimento
- [ ] Skill específica do procedimento referenciada, quando existe

**Modo A (prompt):**

- [ ] O prompt se sustenta sozinho, sem esta conversa
- [ ] Entreguei no chat, em bloco de código — nenhum arquivo criado
- [ ] O prompt traz a especificação proporcional e a regra de subir para spec formal se o escopo crescer

**Modo B (execução aqui):**

- [ ] Não escrevi o texto do prompt — segui o roteiro diretamente
- [ ] Análise veio antes de qualquer alteração, com evidência
- [ ] Artefato de escopo declarado e **aprovado** antes da primeira linha de código
- [ ] Escopo que cresceu no meio parou a implementação e subiu para spec formal
- [ ] Cada commit apresentado e aprovado antes de executar
- [ ] Contradição encontrada na análise foi levada ao solicitante
- [ ] Pergunta que dependia de imaginar ofereceu ver antes de escolher, como opção na mesma lista
- [ ] Rodada fechada pelo gate de fim de rodada, oferecendo só as saídas que tinham objeto, sem escolher pelo usuário
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

- Dimensões de requisito a perguntar → **`skill-02-analista-de-requisitos`**.
- A spec que a sessão nova vai escrever na Fase 1 → **`skill-05-redator-de-funcionalidade`**.
- Quebra em etapas depois da spec aprovada → **`skill-08-construtor-de-funcionalidades`**, que corta em cinco a oito etapas e conduz uma por vez.
- Escolha técnica com efeito duradouro que surgir no passo 3 → **`skill-03-arquiteto-de-solucao`**.
- Se o trabalho é correção de bug → o prompt manda reproduzir antes de corrigir, e fechar pela lente crítica da **`skill-09-revisor-de-codigo`**.
- Se já existe skill do procedimento (migração, tela nova, deploy) → o prompt
  manda segui-la em vez de reinventar.

## Origem

O loop de entendimento e a etapa de formas de solução correspondem ao
*brainstorming* da metodologia **Superpowers**, de Jesse Vincent
(https://github.com/obra/superpowers): refinar a ideia bruta com perguntas
antes de qualquer código. A condicionalidade da etapa 3 é adaptação deste
acervo, para não pesar o fluxo quando o pedido já chega bem posto.

## Manutenção da skill

Atualizar quando:
- A branch de trabalho ou a política de commit/push do projeto mudar.
- Surgir skill nova que a Fase 0/1 deva referenciar.
- Os comandos de verificação do projeto mudarem.
- A etapa 3 (formas de solução) começar a disparar sempre ou nunca — os dois
  extremos indicam que o critério de condicionalidade está errado.

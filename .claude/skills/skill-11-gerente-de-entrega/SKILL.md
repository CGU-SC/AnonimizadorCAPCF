---
name: skill-11-gerente-de-entrega
description: Coloca a versão nova nas mãos de quem usa, seja qual for a forma de entrega — instalador na máquina, publicação na web, atualização do lugar onde o programa já roda, ou arquivo entregue direto. Pergunta a forma antes de agir, diagnostica o que a versão nova faz com quem já está usando a anterior COM DADOS DENTRO, numera a versão, gera o artefato e faz o teste obrigatório da versão nova SOBRE dados que já existem. Gate humano explícito antes de qualquer liberação, porque entrega não se desfaz. Use ao preparar entrega, gerar instalador, publicar versão nova, subir atualização. Triggers, "gera o instalador", "empacota", "publica", "coloca no ar", "manda pro colega", "libera a versão". NÃO implementa nem corrige — só entrega. Na primeira vez que é acionada numa sessão, oferece e RECOMENDA montar o PROMPT de uma sessão dedicada, em vez de conduzir aqui — herdando o modo quando chega pelo gate de outra skill.
---

# Gerente de Entrega

Enquanto o programa roda só onde foi construído, ele não tem usuários, tem um. A
partir da primeira entrega, toda versão nova carrega uma pergunta que não existia
antes: **isso quebra quem já está usando?**

Essa pergunta é a mesma em qualquer forma de entrega. Muda o verbo, não o risco.

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
| **Lê** | O programa na versão a entregar; a versão anterior já em uso, quando existe; o `CLAUDE.md` |
| **Escreve** | O artefato ou a publicação, o número de versão e a nota do que mudou |
| **Pré-condição** | Programa revisado e funcionando, e o teste da versão nova **sobre dados que já existem** feito antes de qualquer liberação |

Pré-condição que não se cumpre **não se contorna**: pare, diga qual artefato
falta e qual skill o produz, e pergunte em uma pergunta só. Seguir com a
entrada faltando é o jeito mais comum de produzir trabalho bem-feito sobre
premissa inventada.

## Quando entra

- Primeira entrega do programa para outra pessoa.
- Versão nova de um programa que já está em uso em algum lugar.
- Usuário pede instalador, empacotamento, publicação ou atualização.

## O que NÃO faz

- Não implementa nem corrige nada. Entregar é registrar um estado, não
  melhorá-lo.
- Não substitui a revisão — **`skill-09-revisor-de-codigo`** vem antes,
  sempre. Aqui isso é **trava, não recomendação**: commit se desfaz com trabalho,
  entrega não se desfaz de jeito nenhum — o arquivo já está na máquina de outra
  pessoa. Não conseguindo **nomear** qual lente rodou sobre esta versão, trate
  como não revisada: pare antes de gerar qualquer artefato, diga isso em uma
  linha e ofereça a revisão.
- Não escreve o texto do que mudou para quem usa — isso é redação em linguagem
  de efeito, não de código.
- Não escolhe a forma de entrega sozinha: pergunta.

## Antes de tudo · Aqui, ou em outra sessão?

Uma **sessão** é uma conversa com o agente, do começo ao fim dela. Na
**primeira vez** que esta skill entra numa sessão, antes de qualquer outra
coisa, pergunte — e **recomende a sessão dedicada**, que é abrir uma conversa
nova só para este trabalho:

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

Não pergunte de novo quando:

- **o modo já foi respondido para esta skill nesta sessão** — vale até o fim dela;
- **você chegou pelo gate de fim de rodada de outra skill** — a passagem é
  continuação do mesmo trabalho e herda o modo que já valia. Diga em uma linha
  que está seguindo no modo herdado;
- **o pedido já diz qual é o modo** — um texto que já chega com fases numeradas
  e regras de execução é modo B declarado. Diga em uma linha por que entendeu
  assim, e siga;
- **o trabalho só faz sentido aqui** — porque depende do que está pendente agora
  ou do que acabou de ser feito nesta sessão. Modo A não se aplica: diga isso em
  uma linha e siga em B.

Fora desses casos, **pergunte mesmo quando parecer óbvio.** Deduzir errado custa
a sessão inteira: ou você entrega um texto quando esperavam o trabalho feito, ou
mexe no projeto quando esperavam só a instrução.

## 0. Qual é a forma de entrega (pergunta obrigatória, SEMPRE)

Antes de gerar qualquer coisa, pergunte **em uma mensagem só**, com opções
numeradas:

```
Como este programa chega em quem vai usar?

  1) INSTALADOR — a pessoa instala na máquina dela
  2) PUBLICAÇÃO NA WEB — o programa fica num endereço que as pessoas abrem
  3) ATUALIZAÇÃO DO LUGAR ONDE JÁ RODA — o programa já está de pé e recebe
     a versão nova por cima
  4) ARQUIVO ENTREGUE DIRETO — planilha, relatório ou pasta que alguém recebe
     e usa como está
  5) outra forma que você tem em mente
```

**É a única pergunta obrigatória do pacote sem a opção `✅ RECOMENDADA`, e é de
propósito:** a forma de entrega é um **fato** do projeto, não uma preferência.
Recomendar aqui seria sugerir a resposta de algo que só quem vai entregar sabe —
e a sugestão errada vira a forma adotada, porque veio recomendada.

Já está registrado no `CLAUDE.md` de entregas anteriores? Diga qual entendeu e
siga, sem repetir a pergunta. Forma nova, ou primeira entrega, registre a
resposta lá ao fim.

**A forma muda o vocabulário e os comandos. Não muda nenhuma regra desta skill.**

## Procedimento

### 1. Diagnóstico de compatibilidade, antes de gerar qualquer coisa

A pergunta é uma só: **se eu liberar agora, o que acontece com quem já tem a
versão anterior, com dados dentro?**

Classifique cada mudança desta entrega:

| Sinal | Significa | O que fazer |
| --- | --- | --- |
| ✅ | Não toca dados nem formato; quem já usa segue funcionando | seguir |
| ⚠️ | Muda estrutura de dados, mas com conversão testada | seguir, com o teste do passo 4 obrigatório |
| ❌ | Muda estrutura sem conversão, apaga dado, ou exige ação manual de quem usa | **parar** — resolver antes de liberar |

Mudança de formato de dados sem conversão testada **bloqueia a liberação**, em
qualquer forma de entrega.

### 2. Verificações que precisam estar verdes

Antes de gerar, e nesta ordem:

- o programa conferido funcionando, inclusive sem nenhum dado;
- nenhum defeito grave em aberto (**`skill-09-revisor-de-codigo`**);
- os critérios de aceite da spec percorridos, um a um;
- nenhum segredo, credencial ou caminho pessoal dentro do que será entregue.

Qualquer uma vermelha: **reportar e parar**. Nunca "libera assim mesmo e corrige
depois" — depois da entrega, o problema mora do lado de lá.

### 3. Numerar a versão

Um número por entrega, e **o mesmo número nunca designa duas coisas
diferentes**. Essa é a invariante que torna possível perguntar "qual versão você
está usando?" e confiar na resposta.

Regerar e reliberar conteúdo diferente sob o mesmo número transforma todo relato
de defeito em adivinhação. Vale para instalador, para o que está no ar e para o
arquivo que você mandou por mensagem.

### 4. Gerar e testar SOBRE dados que já existem

O artefato gerado vai para `builds/`, pasta cujo **conteúdo nunca é versionado**
e cujo produto **nunca se edita à mão**. Entrega que não gera arquivo (publicação
direta) pula a pasta, não pula o teste.

**O teste que realmente importa, e que quase ninguém faz:** provar que a versão
nova encontra dados antigos e não os estraga. O princípio é sempre o mesmo, e o
que muda é só como se faz:

| Forma | Como fazer o teste |
| --- | --- |
| Instalador | Instale a versão **anterior** em máquina, perfil ou pasta limpa; use o programa de verdade; instale a nova **por cima**, sem desinstalar |
| Publicação na web | Suba a versão nova num endereço de teste apontando para uma **cópia dos dados reais**, nunca para os dados de verdade |
| Atualização do lugar onde já roda | Faça a atualização primeiro numa cópia do ambiente, com uma cópia dos dados, e só depois no que está em uso |
| Arquivo entregue direto | Abra o arquivo novo com a ferramenta e a versão que a pessoa realmente usa, com o arquivo anterior dela ao lado |

Em qualquer uma delas, o roteiro é este:

1. Ponha a versão **anterior** para funcionar, no lugar de teste.
2. Use o programa: crie registros de verdade, alguns de cada tipo.
3. Ponha a versão **nova** por cima, sem apagar o que existia.
4. Abra e confira: os dados continuam lá, legíveis e corretos; o que era novo
   funciona; nada pediu intervenção manual.
5. Abra uma segunda vez, para provar que a conversão não roda de novo nem
   duplica nada.

Começar do zero testa o caminho que sempre funciona. É o caminho de cima que
quebra.

**Nunca teste sobre os dados de verdade de quem usa.** Cópia, sempre.

Ao passar esse roteiro para alguém executar, **todo caminho de pasta, endereço e
linha de comando vai em bloco próprio, sozinho na linha** — onde o instalador
ficou, onde os dados moram, o que digitar. É o momento em que mais se copia e
cola, e é onde a pessoa está mais insegura:

```
C:\Users\<você>\AppData\Roaming\<Programa>
```

Caminho embutido na frase, aqui, custa uma ligação pedindo ajuda.

### 5. Gate humano antes de liberar

Entrega é irreversível na prática: não existe recolher o que já foi instalado,
nem desver o que já foi publicado. Portanto, **apresente e espere aprovação
expressa** antes de liberar, mostrando:

- o que muda nesta versão, em linguagem de quem usa;
- o resultado do diagnóstico de compatibilidade;
- o resultado do teste sobre dados existentes;
- o que fazer se der errado, ou seja, como voltar à versão anterior.

Sem "sim" expresso, o artefato fica em `builds/` e a publicação não acontece.

### 6. Depois de liberar

- Registrar o que mudou, para quem usa, em linguagem de efeito e não de código.
- Guardar a versão anterior: ela é o insumo do teste da próxima, e o caminho de
  volta se a nova der errado.
- Conferir uma utilização real, feita por outra pessoa, antes de considerar a
  entrega encerrada.
- Registrar a forma de entrega no `CLAUDE.md`, se ainda não estiver lá.

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
  3) próxima funcionalidade → `skill-08-construtor-de-funcionalidades` —
     **só se sobrar item previsto no backlog**. Entrega feita não fecha o
     projeto; fecha a versão

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

- **Pergunta vai como texto no chat, nunca como seletor** — lista numerada, a
  opção 1 marcada `✅ RECOMENDADA`, e sempre a opção "outra".
- **A forma de entrega é perguntada, nunca suposta.**
- **Revisão antes de entrega, sem exceção.** Não sabendo nomear qual lente rodou
  sobre esta versão, ela não foi revisada — e nada é gerado antes disso.
- **Verificação vermelha bloqueia** — reportar e parar, nunca contornar.
- **Mesmo número, mesma coisa entregue.** Sempre.
- **Testar a versão nova sobre dados que já existem** antes de liberar, seja
  qual for a forma.
- **Nunca testar sobre os dados de verdade de quem usa** — cópia, sempre.
- **Conteúdo de `builds/` nunca versionado**; artefato gerado nunca editado à mão.
- **Nenhum segredo dentro do que é entregue.**
- **Liberação exige aprovação humana expressa**, sempre — é o ponto sem volta.
- **Falha no meio do processo interrompe o processo.** Nada de seguir "porque só
  faltava o último passo".

## Checklist

- [ ] Toda pergunta foi texto no chat, em lista numerada — nenhum seletor, e a
      recomendada em primeiro, marcada com `✅ RECOMENDADA`
- [ ] Nenhuma pergunta aberta e nenhuma de sim ou não — nem para confirmar
      entendimento, nem para aprovar o que eu propus
- [ ] Todo caminho de pasta ou arquivo citado veio com a oferta de eu abrir, na
      mesma mensagem
- [ ] Forma de entrega perguntada e registrada
- [ ] Revisão desta versão nomeada (o que foi revisado, por qual lente) antes de gerar qualquer artefato
- [ ] Diagnóstico de compatibilidade feito, com cada mudança classificada
- [ ] Programa conferido funcionando, sem defeito grave em aberto
- [ ] Nenhum segredo nem caminho pessoal no que vai ser entregue
- [ ] Ambiente de destino dito em voz alta antes de agir, e a configuração de produção separada da de desenvolvimento no artefato
- [ ] Versão numerada, e o número não reaproveita outra entrega
- [ ] Artefato em `builds/`, com conteúdo fora do versionamento (quando gera arquivo)
- [ ] Versão nova testada **sobre dados que já existem**, numa cópia
- [ ] Segunda abertura conferida
- [ ] Aprovação humana expressa antes de liberar
- [ ] Caminho de volta documentado
- [ ] Modo perguntado na primeira vez desta skill na sessão — ou herdado, declarado ou inaplicável, dito em uma linha
- [ ] Pergunta que dependia de imaginar ofereceu ver antes de escolher, como opção na mesma lista
- [ ] Rodada fechada pelo gate, oferecendo só as saídas que têm objeto, sem escolher pelo usuário

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

- A forma de entrega nasce da escolha de stack → **`skill-03-arquiteto-de-solucao`**.
- Mudança de estrutura de dados → o desenho é da **`skill-06-modelador-de-dados`**
  e a mudança em si é da **`skill-08-construtor-de-funcionalidades`**; aqui, a
  conversão testada sobre dados que já existem é pré-requisito da entrega.
- Antes de entregar → **`skill-09-revisor-de-codigo`**.
- O combinado que a entrega precisa cumprir → **`skill-05-redator-de-funcionalidade`**.
- O registro do trabalho → **`skill-10-controlador-de-versoes`**.

## Manutenção da skill

Atualizar quando:
- Surgir forma de entrega que não caiba nas quatro da pergunta inicial.
- O projeto ganhar canais distintos (teste × produção) e a graduação de risco
  entre eles precisar ser descrita.
- A ferramenta de empacotamento ou de publicação mudar.
- Uma falha real de entrega render regra nova — que entra aqui com o incidente
  que a originou.

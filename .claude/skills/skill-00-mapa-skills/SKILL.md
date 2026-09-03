---
name: skill-00-mapa-skills
description: DESENHA O MAPA DAS SKILLS INSTALADAS — uma página HTML local em `.claude/mapa-das-skills.html`, um arquivo só, sempre o vigente, que mostra o pacote inteiro para quem NÃO programa. Cada skill numa caixa do anel, e o clique nela abre o que ela LÊ, o que ela ESCREVE, o GATE dela e o que ela NÃO FAZ, mais as três ligações entre elas — FLUXO, o bastão passando adiante; CHAMADA, uma skill acionando outra para produzir um artefato; DEVOLUÇÃO, o assunto de outra skill sendo nomeado e devolvido. SEMPRE RELÊ A PASTA DAS SKILLS INTEIRA antes de desenhar, uma `SKILL.md` por vez, porque skill nova pode ter entrado no meio do projeto e mapa copiado do anterior envelhece em silêncio — a pasta manda, e o mapa antigo, o README e a memória da sessão não valem como fonte. Na leitura CONFERE O PACOTE e RELATA o que não fecha (número repetido ou faltando, skill sem Contrato, ligação apontando para skill que não existe), sem consertar nada. Ao fim ESCREVE a página a partir do modelo que vem junto e A ABRE. Use quando alguém pedir "o mapa das skills", "o que cada skill faz", "quem chama quem", "atualiza o mapa"; quando uma skill for criada, renomeada ou removida; e ao mostrar o pacote para alguém. NÃO edita skill, NÃO cria skill, NÃO conserta o que encontrou torto, NÃO commita e NÃO SE DESENHA na própria página — ela é lida e conferida como as outras, mas o mapa mostra o trabalho, não a lente. É uma das TRÊS skills sem gate de sessão dedicada — junto da `skill-01-iniciar-projeto` e da `skill-10-controlador-de-versoes` —, porque ela lê, desenha e para.
---

# Mapa das Skills

Um pacote de skills é um monte de arquivo de texto numa pasta. Quem o escreveu
sabe de cor o que cada um faz; qualquer outra pessoa — inclusive quem o escreveu,
três meses depois — abre a pasta e vê nomes.

Esta skill transforma a pasta em **uma página**: cada skill numa caixa, as
ligações entre elas desenhadas, e o clique mostrando o que a skill lê, o que
escreve, onde ela para para esperar uma pessoa, e o que ela **não** faz.

Ela faz **quatro coisas, e só elas**, nesta ordem:

1. **Relê a pasta inteira** — uma `SKILL.md` por vez, do começo ao fim.
2. **Confere o pacote** e relata o que não fecha — sem consertar nada.
3. **Escreve a página** a partir do modelo que vem junto.
4. **Abre a página.**

**A releitura não é opcional, e é o motivo desta skill existir.** Um projeto de
verdade ganha skill no meio do caminho: alguém cria uma, renomeia outra, apaga a
que não usa mais. Mapa montado a partir do mapa anterior fica bonito e passa a
mentir — e mapa que mente é pior que mapa nenhum, porque ninguém desconfia dele.
Por isso a **pasta manda**: nem o mapa de ontem, nem o README, nem o que você
lembra de ter lido nesta sessão valem como fonte.

**Esta é uma das três skills do pacote sem o gate de "aqui, ou em outra
sessão?"** — as outras são a da partida e a do commit. O motivo aqui é simples:
ela lê, desenha e para. Não há trabalho para distribuir, nem decisão que uma
sessão dedicada tomasse melhor. Chamou, ela roda.

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
| **Lê** | A pasta das skills instaladas, `.claude/skills/`, **inteira** — toda `SKILL.md`, do começo ao fim, na mesma rodada. E, se existir, o mapa anterior, **só** para dizer o que mudou |
| **Escreve** | `.claude/mapa-das-skills.html`, um arquivo só, sempre o vigente, gerado a partir do modelo em `modelo/mapa-das-skills.modelo.html`. **Nada mais** — nenhuma `SKILL.md` é tocada |
| **Pré-condição** | Existe uma pasta de skills com pelo menos uma `SKILL.md`. Não existindo, o passo anterior é a `skill-01-iniciar-projeto`, que instala o pacote |

Pré-condição que não se cumpre **não se contorna**: pare, diga qual artefato
falta e qual skill o produz, e pergunte em uma pergunta só.

## Quando entra

- **Pedido direto** — "mostra o mapa das skills", "o que cada skill faz",
  "quem chama quem", "atualiza o mapa".
- **O pacote mudou** — skill criada, renomeada, removida, ou com o gate alterado.
  O mapa que não acompanha vira desenho de um pacote que não existe mais.
- **Alguém de fora vai ver o trabalho** — mostrar a pasta é mostrar nomes de
  arquivo; mostrar o mapa é mostrar o método.
- **Você mesmo perdeu o fio** — não lembra qual skill é dona de um assunto, ou
  duas parecem fazer a mesma coisa. O mapa é onde a sobreposição aparece.
- **Primeira vez neste projeto** — não existe mapa nenhum ainda.

## O que NÃO faz

- **Não edita skill.** Encontrou uma `SKILL.md` torta, ela é relatada e fica
  como está. Quem mexe em skill é quem a mantém, com o texto na frente.
- **Não cria skill.** Faltou uma etapa no ciclo, isso é achado do relatório, não
  arquivo novo.
- **Não conserta o que encontrou.** Número repetido, ligação apontando para
  skill que não existe, seção faltando — tudo isso **sai no relatório**, e
  nenhum deles vira correção silenciosa. Mapa que arruma o que retrata deixa de
  ser retrato.
- **Não inventa ligação.** Aresta só entra quando **está escrita** em alguma
  `SKILL.md`. Duas skills que "deviam" se falar e não se falam é achado, não é
  seta.
- **Não desenha o projeto.** As telas, o banco e o backlog do programa que está
  sendo construído são de outras skills. Aqui o assunto é o **pacote**.
- **Não commita.** O arquivo fica gravado em disco e a decisão de registrar é do
  usuário, pela `skill-10-controlador-de-versoes`.

## Procedimento

### 0. Achar a pasta das skills

`.claude/skills/` é o **único** lugar de onde o agente carrega skill, e é ela
que se lê. Liste a pasta antes de qualquer coisa.

| O que você encontra | O que fazer |
| --- | --- |
| A pasta existe, com subpastas contendo `SKILL.md` | Siga para o passo 1 |
| A pasta não existe, ou está vazia | Pare. Diga que não há pacote instalado e que quem instala é a **`skill-01-iniciar-projeto`** |
| A pasta é um atalho para outro lugar | Siga normalmente, e **diga no relatório** para onde ela aponta — quem lê o mapa precisa saber qual pasta ele retrata |
| Existem subpastas sem `SKILL.md` dentro | Ignore no desenho, e **liste no relatório**. Pasta que não tem `SKILL.md` não é skill, e costuma ser sobra de renomeação |

### 1. Reler tudo, uma por vez

**Leia toda `SKILL.md` da pasta, inteira, nesta rodada.** Não amostre, não pule
a que "não deve ter mudado", não aproveite o que ficou na memória da sessão.

**Esta skill é lida como as outras, e não vira entrada.** O mapa mostra o
trabalho — as skills que levantam, decidem, constroem, conferem e entregam. Esta
aqui é a lente, não a paisagem: desenhá-la na própria página é o retrato em que o
fotógrafo aparece, e ela ocupa um cartão que a pessoa nunca vai precisar abrir.
Ela continua sendo **lida e conferida**, e o que estiver torto nela sai no
relatório como o de qualquer outra.

De cada uma, colha nove coisas:

| Campo | Onde ele está | Como ele fica |
| --- | --- | --- |
| **número** | os dois dígitos do nome da pasta | `"07"` — texto, com o zero à esquerda |
| **arquivo** | o nome da pasta, exato | `skill-07-designer-de-telas` |
| **nome** | o título `#` de dentro da skill | Designer de Telas |
| **curto** | o rótulo da caixa, escrito por você | até doze letras. É o que a pessoa lê de longe |
| **frase** | a abertura da skill, condensada | uma linha, na língua de quem não programa |
| **lê** | a linha **Lê** do Contrato | 2 a 4 itens curtos, não a frase inteira |
| **escreve** | a linha **Escreve** do Contrato | 2 a 4 itens, com o caminho do artefato quando houver |
| **gate** | o gate declarado na skill | onde ela para e espera uma pessoa dizer sim. Aparece no painel, ao clicar na caixa |
| **não faz** | a seção **O que NÃO faz** | uma linha, os três ou quatro verbos negados |

**O `curto` e a `frase` são escritos, não copiados.** A descrição da skill é
densa de propósito, para o agente; o mapa é para uma pessoa olhar. Se a frase
não couber em uma linha lida em voz alta, ela ainda não está pronta.

**Skill sem `Contrato`, sem gate ou sem `O que NÃO faz` entra assim mesmo**, com
o campo vazio marcado como não declarado — e vira item do relatório. Buraco no
mapa é informação; buraco preenchido de cabeça é invenção.

### 2. Levantar as ligações

Três tipos, e a diferença entre eles é o que o mapa tem de melhor a ensinar:

| Tipo | O que é | Onde está escrito |
| --- | --- | --- |
| **fluxo** | o bastão passa adiante, pelo gate de fim de rodada | "a saída desta skill é", "entrega para", as saídas do **Fim de rodada** |
| **chamada** | uma skill aciona outra para produzir um artefato, com o conteúdo já pronto | "desenhada pela", "aciona a", "gerado pela", "a pedido desta skill" |
| **devolução** | apareceu assunto de outra skill, nomeia e devolve em vez de improvisar | "isso é da", "devolva para", "o passo anterior é outro", quase sempre em **Relação com outras skills** |

Regras da colheita:

- **Aresta só existe se estiver escrita.** A frase que a sustenta tem de estar
  em alguma `SKILL.md`. Na dúvida, não desenhe e relate.
- **A legenda é a frase da skill, encurtada** — não um rótulo genérico. "o
  rascunho de tela vem antes do código da interface" ensina; "próxima etapa" não.
- **Ligação repetida entre o mesmo par continua sendo duas.** Duas skills podem
  se ligar por fluxo, por chamada e por devolução ao mesmo tempo — cada uma é
  uma aresta, e o desenho as separa sozinho.
- **A que todas têm não entra.** Quase toda skill oferece revisão e commit no
  fim da rodada, e quase toda skill com gate de modo aciona a do prompt.
  Desenhar isso são dezenas de setas que viram teia e escondem o resto — e
  explicá-las em texto ao lado do desenho é a mesma informação cobrada duas
  vezes de quem só queria olhar. Ficam de fora, e ponto: quem precisa do detalhe
  abre a `SKILL.md`.
- **Aresta de fluxo que é atalho leva `fora: true`** — ela aparece no desenho,
  mas fica de fora do ciclo tocado pelo botão.

### 3. Separar quem está fora do ciclo

Skill que **não recebe e não passa o bastão** — nenhuma aresta de fluxo — não
entra no anel. Ela ganha `avulsa: true` e vira cartão embaixo do diagrama.

É o caso das transversais — as que entram em qualquer ponto do trabalho. Pô-las
no anel é inventar uma ordem que elas não têm, e a ordem inventada é justamente
o que a pessoa vai acreditar.

Não havendo nenhuma, a seção não aparece: o modelo a esconde sozinho.

### 4. Conferir o pacote

Antes de desenhar, passe a colheita por seis perguntas. **Nenhuma delas vira
correção** — todas viram linha do relatório.

1. **Falta número?** As pastas numeram uma sequência. Buraco no meio quase
   sempre é skill removida sem renumerar.
2. **Número repetido?** Duas pastas com o mesmo número é o agente carregando
   uma e ignorando a outra.
3. **Alguma skill cita skill que não existe?** Nome entre crases apontando para
   pasta ausente é ligação morta — o agente simplesmente não invoca nada.
4. **Alguma skill ficou sem nenhuma ligação?** Ou ela é avulsa de verdade, ou
   ninguém a conhece e ela nunca vai ser chamada.
5. **Duas skills declaram o mesmo dono?** Dois donos do mesmo artefato é como um
   projeto começa a se contradizer.
6. **Alguma ficou sem gate declarado?** Skill sem ponto de parada é skill que
   decide sozinha.

### 5. Desenhar um glifo por skill

Cada skill tem **um desenho seu**, em traço, que a representa no diagrama e ao
lado do nome dela em todo lugar da página. Botão de ligar para a partida, balão
com pergunta para a entrevista, cilindro para o banco, chave para a construção.

- `<symbol id="ic-NN" viewBox="0 0 24 24">`, com o `NN` batendo com o número.
- Só `path`, `circle` e `rect`. **Sem `fill` e sem `stroke`** — a cor e a
  espessura vêm do CSS, e é assim que o glifo acompanha o tema claro e escuro.
- **Nunca emoji.** Emoji muda de forma em cada máquina, não obedece à cor do
  tema e some quando a fonte não o tem.
- O glifo diz **o que a skill faz**, não a inicial do nome dela.

### 6. Escrever a página

O arquivo `modelo/mapa-das-skills.modelo.html`, que vem junto desta skill, é a
página inteira — estilo, diagrama, painel, seções — com **dois lugares para
preencher** e mais nada:

| Onde | O que entra |
| --- | --- |
| o bloco `GLIFOS`, dentro do `<defs>` | um `<symbol>` por skill |
| `NOME_DO_PACOTE`, `SKILLS` e `ARESTAS`, no início do `<script>` | a colheita dos passos 1 a 3, mais o nome do pacote, que vai na aba do navegador. O título da página é fixo, **Mapa de Skills**, e a página não tem texto de explicação — o desenho é a explicação |

**Copie o modelo e preencha. Não reescreva a página.** O anel, os raios, o
tamanho do desenho, as contagens e os títulos saem sozinhos do que está nas
listas — inclusive quando o pacote cresce, porque o anel se abre em dois raios
alternados para as caixas não se encostarem. Mexer no que está abaixo de
`geometria` é a maneira mais rápida de quebrar isso.

Grave em **`.claude/mapa-das-skills.html`** — ao lado da pasta que ele retrata,
como toda página do pacote fica ao lado do que ela mostra. Um arquivo só, sempre
o vigente. Não versione o mapa por data, não guarde o anterior: o histórico do
projeto já guarda.

### 7. Abrir

Abra o arquivo no navegador padrão, e diga que abriu.

| Sistema | Comando |
| --- | --- |
| Windows | `start "" ".claude\mapa-das-skills.html"` |
| macOS | `open .claude/mapa-das-skills.html` |
| Linux | `xdg-open .claude/mapa-das-skills.html` |

Não abriu — não force. Diga o caminho completo, ofereça abrir de novo, e siga
para o relatório: a página está gravada de qualquer jeito.

**Depois de aberta, confira você mesmo, no arquivo, três coisas** antes de
relatar: toda skill lida virou entrada — menos esta —, todo `ic-NN` tem símbolo, e nenhuma
aresta ficou apontando para número que não está na lista — o modelo descarta
essas com aviso no console, e aresta descartada em silêncio é ligação que
sumiu do mapa sem ninguém saber.

### 8. Relatar

Em texto no chat, curto:

- **quantas skills** foram lidas, e de qual pasta;
- **o que mudou** desde o mapa anterior — entrou, saiu, mudou de nome, mudou de
  gate. Não havia mapa anterior, diga que este é o primeiro;
- **os achados da conferência**, um por linha, ou "nada fora do lugar";
- **o caminho do arquivo**, com a oferta de abrir.

## Como conversar

Esta skill quase não pergunta — ela lê, desenha e mostra. As poucas perguntas
que ela tem seguem a regra do pacote: **texto no chat, nunca seletor**, lista
numerada, a opção 1 marcada `✅ RECOMENDADA`, e sempre uma opção "outra".

**Ela pergunta em três situações, e só nelas:**

1. **Não achou a pasta das skills** — ou achou mais de uma candidata.
2. **O pacote está grande demais para um anel** — acima de mais ou menos
   quarenta skills, o desenho fica apertado mesmo com o anel aberto. Diga isso e
   pergunte se ela desenha assim mesmo ou se separa por grupo.
3. **A colheita ficou com buraco grande** — várias skills sem Contrato, por
   exemplo. Pergunte se ela desenha com os campos vazios marcados, ou se para
   aqui e devolve o relatório sozinho.

Fora dessas, **não pergunte, faça**. Foi chamada justamente para não dar
trabalho: o gate desta skill é a página aberta na frente da pessoa.

**Todo caminho de pasta ou arquivo citado vai com a oferta de eu abrir**, na
mesma mensagem.

**Não descreva a página em vez de mostrá-la.** Parágrafo contando o que o mapa
mostra é o que esta skill existe para substituir.

## Fim de rodada

Terminou, relate e ofereça as saídas, sem recomendar nenhuma.

**Antes de montar a lista, confira o que cada saída teria de objeto.** Saída sem
objeto não entra na lista.

  1) commit do mapa → `skill-10-controlador-de-versoes` — **só se o arquivo
     tiver mudado**. Mapa idêntico ao anterior não é pendência
  2) arrumar um achado da conferência → a skill dona do arquivo torto, nomeada —
     **só se houve achado**. Esta skill não conserta nada
  3) voltar ao trabalho — esta skill nunca é destino final. Diga qual era a
     skill que conduzia quando o mapa foi pedido, e devolva a condução para ela

Sobrou uma saída só, ofereça uma. Não sobrou nenhuma, não invente gate: diga que
a rodada fechou sem pendência e qual é o próximo passo previsto.

**Commit é ato do usuário.** Nenhuma skill, exceto a
`skill-10-controlador-de-versoes`, executa commit. Ter gerado o mapa não
autoriza registrá-lo.

## Regras que nunca mudam

- **A pasta manda.** Toda rodada relê `.claude/skills/` inteira. O mapa anterior,
  o README e a memória da sessão **não** são fonte.
- **Aresta só existe se estiver escrita** em alguma `SKILL.md`.
- **Nada de skill é editado aqui** — o que está torto é relatado, e fica.
- **Um arquivo só, sempre o vigente**, em `.claude/mapa-das-skills.html`.
- **Página local e autossuficiente** — abre com dois cliques, sem internet e sem
  instalar nada. Nada de link para fora, nada de biblioteca baixada.
- **Nunca emoji no diagrama** — um glifo em traço por skill.
- **A página se abre no fim.** Mapa gerado e não aberto é arquivo, não é mapa.
- **Pergunta vai como texto no chat, nunca como seletor** — lista numerada, a
  opção 1 marcada `✅ RECOMENDADA`, e sempre a opção "outra".
- **Não commita.**

## Checklist

- [ ] A pasta das skills foi listada, e a que foi lida está dita no relatório
- [ ] **Toda** `SKILL.md` foi lida nesta rodada, inteira — nenhuma pulada por já ser conhecida
- [ ] Esta skill foi lida e conferida, e **não** entrou na página
- [ ] Os nove campos colhidos de cada skill, e o que faltou marcado como não declarado
- [ ] `curto` e `frase` escritos para uma pessoa ler, não copiados da descrição
- [ ] Toda aresta desenhada tem frase que a sustenta em alguma `SKILL.md`
- [ ] As ligações que todas as skills têm ficaram fora do diagrama e ditas em texto
- [ ] Skill sem aresta de fluxo marcada como `avulsa`, fora do anel
- [ ] As seis perguntas da conferência respondidas, e os achados no relatório
- [ ] Nenhum achado foi consertado — nenhuma `SKILL.md` tocada
- [ ] Um `<symbol id="ic-NN">` por skill, em traço, sem `fill` e sem `stroke`, sem emoji
- [ ] A página saiu do modelo, com só os dois blocos preenchidos — nada abaixo de `geometria` alterado
- [ ] Gravada em `.claude/mapa-das-skills.html`, um arquivo só
- [ ] Aberta no navegador, e conferida — toda skill virou entrada, todo `ic-NN` tem símbolo, nenhuma aresta descartada
- [ ] Relatório com a contagem, o que mudou desde o mapa anterior, os achados e o caminho
- [ ] Todo caminho de pasta ou arquivo citado veio com a oferta de eu abrir, na mesma mensagem
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

- **Quem instala o pacote** é a **`skill-01-iniciar-projeto`**. Sem pasta de
  skills não há o que mapear, e é para ela que esta devolve quando a pasta não
  existe.
- **Escrever, renomear ou apagar skill não é assunto daqui.** Esta skill percebe
  a mudança e redesenha; quem mexe no texto é quem mantém a skill, com o arquivo
  na frente.
- **A página sai do modelo que vem junto, e não da
  `skill-07-designer-de-telas`.** Aquela desenha as páginas do **projeto** — as
  telas, a spec ilustrada, o painel do backlog, o mapa do entendimento. Esta
  desenha o **pacote**, que é outro assunto e tem forma fixa. Por isso o mapa
  também não entra no `mockups/00-indice.html`, que é a capa das páginas do
  projeto.
- **Onde o arquivo mora** segue a regra da
  **`skill-04-organizador-de-ambiente`** — página fica ao lado do que ela
  mostra. O mapa mostra `.claude/skills/`, então ele mora em `.claude/`.
- **O commit do mapa** é da **`skill-10-controlador-de-versoes`**, oferecido no
  gate — nunca aqui.
- **Achado que vira conserto** volta para a skill dona do arquivo torto,
  nomeada no relatório.

## Manutenção da skill

Atualizar quando:
- O modelo da página ganhar seção nova, ou as ligações deixarem de ser três.
- O agente passar a carregar skills de outro caminho, e o passo 0 deixar de
  achar a pasta.
- O pacote passar de mais ou menos quarenta skills, e o anel deixar de caber num
  desenho só.
- As seis perguntas da conferência começarem a não achar nada nunca — sinal de
  que viraram formalidade, e não de que o pacote está perfeito.

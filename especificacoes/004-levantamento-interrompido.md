# Funcionalidade 4 — Revisão por IA local: levantamento interrompido

**Isto não é uma spec.** É o que foi levantado antes de o trabalho ser parado,
para que quem retomar não recomece do zero.

- **Parado em** 23/09/2026, no meio do levantamento, antes de qualquer linha de
  código e antes da spec 004.
- **Por que parou**: a solicitante decidiu entregar antes uma versão de teste
  para o núcleo da CAPCF, com o que já está construído (funcionalidades 1, 2 e
  3). A funcionalidade 4 volta depois da entrega.
- **Onde estava**: a Fase 0 (análise do código) foi feita e está inteira aqui
  embaixo. O levantamento tinha acabado de começar — uma pergunta feita e
  respondida, uma pergunta no ar.
- **O que existe em código**: nada. Nenhuma linha da funcionalidade 4 foi
  escrita. Esta anotação é o único arquivo dela.

---

## 1. Entendimento validado com a solicitante

Confirmado por ela em 23/09/2026. Não renegociar — mas avisar se o código
contradisser.

**Objetivo** — dar a quem confere um segundo par de olhos automático antes do
olho humano: uma IA rodando na máquina dela, ou na rede da universidade, que
diga onde vale olhar com mais cuidado.

**Problema** — hoje o único filtro entre o que o Tesseract leu e a pessoa é a
conta do dígito verificador e o formato do número. Disso saem duas falhas:

1. Texto estragado em outro lugar passa sem marca. Se o OCR errou no meio de
   uma palavra, de uma tabela ou de um número sem cara de CPF, nada levanta a
   mão.
2. Número que só o contexto denuncia — ou inocenta — não é visto. Um número
   solto depois de "CPF:" merece suspeita mesmo torto; um número de empenho com
   onze dígitos que passa na conta merece ser inocentado.

O efeito: a pessoa lê o documento inteiro sem saber onde a leitura é mais
frágil, e a atenção é finita.

**Resultado esperado** — com a camada ligada, a revisão chega com apontamentos
a mais, cada um sabendo dizer de onde veio. Desligada, o programa se comporta
exatamente como hoje.

**Limites** — a IA não escreve o texto do documento; ele continua sendo o do
Tesseract. Nada sai da UFSC.

### As duas frentes, e o peso de cada uma

| Frente | Peso |
| --- | --- |
| **IA revisora** — segundo par de olhos sobre o que já foi lido | é a razão de a funcionalidade existir |
| **IA como motor de OCR** — alternativa ao Tesseract na leitura | entra preparada e habilitada, não escondida, com aviso na spec e na tela de que os modelos locais pequenos de hoje leem bem pior que o Tesseract. A solicitante mediu isso |

## 2. Premissas

Valem como respondidas até alguém as derrubar. Caindo uma, o entendimento
reabre no ponto em que ela sustentava.

- premissa: a camada de revisão por IA vem **desligada** por padrão;
- premissa: os apontamentos da IA **somam** à lista que já existe, e nunca
  reduzem o que a pessoa precisa ler;
- premissa: vale nos **dois módulos** (Gerar OCR e Anonimizar), já que a escolha
  do motor hoje é montada num lugar só;
- premissa: IA indisponível, fora do ar ou lenta demais **não trava a
  conferência** — o programa avisa e segue com o que já tem;
- premissa: "desligada se comporta como hoje" significa **nenhuma chamada de
  rede e nenhum caminho novo executado**, e não apenas "a tela fica igual".

## 3. Decidido pela solicitante em 23/09/2026

- A IA vem **sem configurar** por padrão.
- O menu lateral ganha um item **"Configurações de IA"**, na **parte inferior**,
  longe das demais funcionalidades.
- Dentro dele, dois submenus: **"LM Studio"** (na própria máquina) e
  **"Servidor de IA Interno"** (na rede da universidade).
- Mesmo vindo desligada, **quem usa só o Tesseract precisa saber que existe** a
  possibilidade de ligar uma IA para revisar. Forma do aviso: em aberto.
- A configuração de IA **deve ser guardada entre um uso e outro**. Sem banco de
  dados. Ver a contradição na seção 5.

## 4. Fase 0 — o que o código mostra

Análise feita em 23/09/2026 sobre o commit `3271a31`. Nada foi alterado.

### 4.1 O rádio da IA não está só apagado; ele não está ligado a nada

`programa/caminho_do_pdf.py`, linhas 783-823, monta a escolha e devolve os dois
botões. Quem os recebe: `programa/painel_ocr.py:257` e
`programa/caminho_do_pdf.py:853` — os dois guardam a referência e **nunca
consultam** qual está marcado. O único lugar que lê o estado é um teste
(`programa/test_painel_anonimizar.py:182-183`), conferindo que o Tesseract vem
marcado. `programa/leitura.py:113` chama o Tesseract direto.

**Consequência**: desapagar o rádio não liga nada. O ponto onde o programa
escolhe entre dois motores **não existe e precisa ser construído**. É etapa, não
ajuste de uma linha.

### 4.2 O programa sabe ler o `.env` e não sabe escrever nele

`programa/configuracao.py` tem 81 linhas: `valor_do_env` (linha 26) lê um valor,
e `_texto_do_env` (linha 52) aceita os três formatos em que o Bloco de Notas do
Windows grava texto. **Não há escrita em lugar nenhum.**

`pasta_do_programa()` (linha 12) devolve, na entrega, a pasta do próprio `.exe`
— que pode ser `Program Files`, onde gravar exige a confirmação do Windows. É o
mesmo tropeço já anotado no `CLAUDE.md` a respeito do Tesseract.

### 4.3 As duas variáveis de IA existem e ninguém as lê

`LLM_REMOTA_URL` e `LLM_REMOTA_API_KEY` estão no `.env.example` com explicação
escrita. Nenhuma linha do programa as consulta. Aparecem uma vez, como enfeite,
dentro de um `.env` de mentira em `programa/test_motor.py:51`.

### 4.4 O menu já tem o lugar pedido — e não tem submenu

`programa/main.py:52-56` monta os dois itens e logo depois um espaçador que
empurra tudo para cima. Item acrescentado **depois** do espaçador nasce colado
embaixo — exatamente "na parte inferior, longe das demais". Esse pedaço é
barato.

O que não existe é submenu: hoje todo item é um botão que troca o painel
inteiro, e só um fica marcado por vez (RN-2 da spec 001, em
`programa/main.py:236-239`). Menu com dois níveis é forma nova, e precisa passar
pelo desenho de tela.

### 4.5 Um detalhe do menu que vai morder na conferência

`programa/main.py:219-224`: sair do Anonimizar com revisão não salva dispara a
pergunta "descartar?". Um item novo no menu **cai nessa mesma regra** — clicar
em "Configurações de IA" no meio de uma revisão vai perguntar antes. Está certo,
mas precisa estar escrito na spec: sem isso, na conferência de tela isso aparece
como defeito.

### 4.6 A lista de achados tem onde caber, mas não como mais um "tipo"

`programa/lista_de_achados.py:74-90` monta as seções a partir do **tipo** da
ocorrência, e o tipo vem de `programa/cpf.py:16-19` — quatro valores, decididos
só por formato e pela conta do dígito. Apontamento de IA não é um tipo de CPF: é
**outra origem de suspeita**. Enfiá-lo em `POR_TIPO`
(`programa/tipos_na_tela.py:34`) misturaria duas coisas diferentes no mesmo
lugar. Decisão de spec.

### 4.7 O molde do trabalho em segundo plano já está pronto

`programa/leitura_em_segundo_plano.py` tem progresso, cancelamento e quatro
caminhos de falha, com o "seja o que for, a tela precisa sair da espera" já
escrito (linha 57). Uma revisão por IA precisa exatamente disso. Reúso quase de
graça — só o `run()` é que chama o Tesseract direto.

### 4.8 O backlog descreve a funcionalidade na forma antiga

`especificacoes/backlog.md`, item 4, diz "alternativa ao Tesseract". A
solicitante quer **revisão**, e a leitura por IA é a frente secundária. A linha
precisa ser reescrita quando a spec 004 for aprovada.

## 5. A contradição que precisa ser resolvida antes da spec

> **RN-22 (spec 002)**: nada é guardado entre um uso e outro — nem histórico,
> **nem preferência de motor**, nem última pasta usada.

> **RN-19 (spec 003)**: Um arquivo por vez, e nada guardado entre um uso e
> outro, nem histórico, nem pasta lembrada.

A solicitante pediu que a configuração de IA seja guardada entre usos. "Nem
preferência de motor" está escrito com todas as letras, e é justamente isso.

**Não é impedimento — é uma emenda a escrever de olhos abertos.** A regra foi
feita para proibir o programa de *lembrar do trabalho*: que documento foi
aberto, que texto foi lido, que pasta foi usada. Isso continua proibido. O que
ela pediu é outra categoria: **configuração da instalação**, que é o que o
`TESSERACT_CAMINHO` já é hoje — ninguém nunca considerou que ele violasse a
RN-22, porque ele não é memória do uso.

A emenda separa as duas coisas: fica escrito o que **pode** ser guardado
(endereço, credencial, qual destino, ligado ou desligado) e o que **continua
proibido** (documento, texto lido, pasta, histórico, achado).

## 6. A pergunta que ficou no ar

**Onde a configuração de IA vai morar?** Quatro saídas, nenhuma precisa de
banco. Elas não diferem em dificuldade: diferem em **quem configura** e **onde o
segredo mora**.

1. *(era a recomendada)* **O programa escreve no `.env` da instalação.** Um
   lugar só para tudo, segredo onde a regra dura manda, e tanto a TI quanto a
   pessoa podem preencher. **Custo**: `configuracao.py` só sabe ler, e precisa
   aprender a escrever sem destruir os comentários da TI nem trocar a
   acentuação do arquivo; e instalado em `Program Files` esbarra na confirmação
   do Windows, o que obriga a decidir, na entrega, instalar fora de lá.
2. **O programa não escreve nada.** A tela de configuração vira tela de *ver e
   testar*: mostra o que está configurado, diz se a conexão responde, e explica
   o que escrever. Guardar entre usos sai de graça. **Custo**: a pessoa do
   núcleo não configura sozinha pelo programa — é menos do que ela pediu.
3. **Arquivo próprio na pasta do usuário do Windows**, separado do `.env`.
   Sempre gravável, sem administrador, um por pessoa. **Custo**: configuração
   passa a morar em dois lugares, e o token sai do `.env` — o que obriga a
   reescrever a regra dura do projeto.
4. **No registro do Windows**, pelo recurso que o Qt já traz. Nenhum arquivo.
   **Custo**: invisível para quem não programa, a TI não consegue preparar a
   máquina antes, e segredo lá é o mais difícil de conferir. Desaconselhado.

## 7. O que ainda nem foi perguntado

A fila do levantamento, na ordem de consequência. Nada disto está decidido, e a
solicitante pediu expressamente que nada chegasse decidido.

- **O que a IA revisora enxerga**: a imagem da página, o texto lido, ou os dois.
  É o que mais muda o tamanho do trabalho, e a única ambiguidade que ela deixou
  explicitamente em aberto.
- **Como a IA infere por contexto** que um número é CPF — ideia dela, e
  capacidade que o programa hoje não tem.
- **Como o apontamento da IA aparece** na lista ao lado do texto, sabendo dizer
  de onde veio, sem se confundir com os quatro tipos que já existem (ver 4.6).
- **O rótulo do motor na tela** — hoje é "IA local da UFSC".
- **Quantos destinos de IA existem**, e quais.
- **Se há teste de conexão**, e o que ele promete.
- **Se o programa restringe o endereço** que pode ser digitado.
- **Como quem usa só o Tesseract descobre** que a revisão por IA existe.
- **Se a conferência humana muda** quando a IA participa.
- **O que acontece quando a IA falha** no meio — e como a tela diz isso.
- **Fora de escopo** da funcionalidade 4: ainda não foi delimitado.

## 8. Como retomar

1. Voltar a esta branch (`spec-004-revisao-por-ia-local`).
2. Reler este arquivo — ele substitui a Fase 0, que não precisa ser refeita,
   desde que o código não tenha mudado nas linhas citadas na seção 4.
3. Retomar o levantamento pela pergunta da seção 6, seguindo
   `.claude/skills/skill-02-analista-de-requisitos/SKILL.md`, passo 7, nível
   detalhado — uma pergunta por mensagem, em lista numerada.
4. Esgotada a fila da seção 7, fechar com o mapa do entendimento e só então
   escrever a spec 004.

**Regra que vale em toda a funcionalidade**: nenhum endereço de serviço fora da
UFSC entra no código, em teste, em comentário ou como exemplo — nem neste
arquivo.

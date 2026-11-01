# Spec 004 — Revisão por IA local

**Status:** aprovada; construída, à espera da conferência na tela
**Data:** 2026-10-31
**Aprovada em:** 2026-10-31
**Levantamento:** `mockups/requisitos/08-mapa-do-entendimento.html`, começado em
23/09/2026 e fechado em 31/10/2026. A anotação de setembro está em
`especificacoes/004-levantamento-interrompido.md`, e vale o que está aqui quando
as duas divergem.

## Objetivo

Dar a quem confere um segundo par de olhos automático antes do olho humano: uma
IA na própria máquina ou num servidor interno aponta, na revisão do Anonimizar,
onde vale olhar com mais cuidado. Secundariamente, deixar a IA disponível como
motor de leitura, atrás de uma chave e com ressalva.

## Escopo

- O item **"Configurações de IA"**, no fim da faixa da esquerda, logo acima da
  versão. O clique troca o menu inteiro pelo submenu **"LM Studio"**, **"Servidor
  de IA Interno"** e **"Habilitar IA"**, com um **"voltar"**.
- A tela **LM Studio**: switch, porta, situação da conexão, seletores de modelo e
  botão de testar.
- A tela **Servidor de IA Interno**: switch, endereço, token, situação da
  conexão, seletores de modelo e botão de testar.
- A tela **Habilitar IA**: os switches "Habilitar IA", "IA revisora" e "IA como
  motor de leitura", a opção de como a revisão inicia e a ressalva do motor.
- O **aviso de endereço não reconhecido**, ao salvar e no primeiro uso a cada
  abertura do programa, e a lista de endereços locais no `.env`.
- A **revisão por IA**, só no Anonimizar, para toda entrada dele (PDF, `.docx`,
  `.md` e `.txt`): a seção "A IA pediu para olhar", a etiqueta nos números já
  listados, a máscara nos números apontados, o andamento, o cancelar e o
  retomar.
- A **"IA local" como motor de leitura**, nos dois módulos, quando a chave
  estiver ligada.
- A **separação da lembrança do motor** da peça de tela que mostra os motores,
  antes de o terceiro motor entrar (`CLAUDE.md`, "Decidido antes de esquecer").
- As **emendas** às specs 001, 002 e 003 e ao `CLAUDE.md`, descritas no fim.

## Fora de escopo

- **Ligar o servidor, baixar e carregar modelo pelo programa.** Ficam no próprio
  LM Studio, e a tela diz para a pessoa abri-lo.
- **Motor próprio dentro do programa, e download direto do Hugging Face.** O
  programa continua sem baixar nada (RN-20 da spec 002).
- **Revisora no Gerar OCR**, e **revisora olhando a imagem da página**.
- **Dois destinos ligados ao mesmo tempo.**
- **Editar pela tela as instruções** que o programa manda para a IA: vêm fixas.
- **Guardar apontamentos** de um uso para o outro, ou escrevê-los no `.md`.
- **Apontar outros dados sensíveis além do CPF.** A IA aponta só número suspeito
  e trecho estragado.
- **Lista de modelos recomendados.** A pessoa escolhe entre os instalados.
- **Bloquear endereço.** O programa avisa, e quem decide é a pessoa (RN-16).
- **Medir a qualidade da revisão.** O teste de conexão só diz que o modelo
  respondeu.

## Premissas

Lidas no mapa 08 e não derrubadas. Caindo uma, a spec reabre no ponto que ela
sustenta.

- premissa: como revisora, a IA nunca escreve o texto; como motor, o texto é dela,
  só com a chave ligada e esse motor marcado.
- premissa: como motor, a IA recebe a imagem da página com os CPFs inteiros.
- premissa: a ressalva vai datada, como avaliação de quem fez o programa, porque
  o medido é o Tesseract contra o PaddleOCR.
- premissa: o aviso de troca de destino vem ao ligar o switch; abrir a tela do
  outro destino e preencher os campos não desliga nada.
- premissa: endereço e modelos ficam no `preferencias.ini`; o token, nunca.
- premissa: redirecionamento não é seguido.
- premissa: o aviso de endereço aparece uma vez por abertura, para os dois usos;
  trocar o endereço com o programa aberto faz perguntar de novo.
- premissa: endereço em `http://` é aceito.
- premissa: quem nunca escolheu começa em "ao clicar no botão".
- premissa: trecho citado pela IA que não existe no texto é descartado.
- premissa: servidor que não lista os modelos pede o nome digitado.
- premissa: a conferência humana não muda, e nenhum apontamento marca algo como
  conferido.
- premissa: sem a IA ligada, nenhuma chamada de rede e nenhum caminho novo.
- premissa: o LM Studio não tem campo de token nesta versão.
- premissa: o endereço do LM Studio é sempre esta máquina, e só a porta se
  troca; LM Studio em outra máquina se configura como servidor interno.
- premissa: sair de uma revisão pelo menu da IA faz a pergunta de descartar.
- premissa: o token salvo aparece só como "token salvo", com substituir e apagar.
- premissa: desinstalar leva o token junto; atualizar o mantém.

Novas, surgidas ao escrever esta spec, e ditas na apresentação dela:

- premissa: número apontado é o trecho com **8 dígitos ou mais**, contando letra
  parecida com dígito; menos que isso, ele é só apontado, sem máscara (RN-30).
- premissa: número que a pessoa já liberou não é mascarado de novo pela IA; ele
  só recebe a etiqueta (RN-31).
- premissa: resposta da IA que o programa não consegue entender conta como falha
  daquele pedaço, e entra no "o que faltou" (RN-37).
- premissa: a leitura pela IA segue a orientação da página como o PaddleOCR, e
  não mostra estimativa de tempo antes de começar, porque ela depende do modelo.

## Fluxos

### Configurar o LM Studio

1. A pessoa clica em "Configurações de IA"; o menu vira o submenu.
2. Em "LM Studio", ela já tem o servidor do LM Studio ligado e liga o switch.
3. O programa testa a conexão, lista os modelos e mostra "respondendo".
4. Ela escolhe o modelo da revisora, o teste roda com ele, e o destino passa a
   contar como configurado.

**Torto — o LM Studio está fechado.** O teste falha, o switch volta para
desligado, a escolha fica guardada, e a tela diz: "Abra o LM Studio e ligue o
servidor local". Ao tentar de novo, tudo volta como estava.

### Configurar o Servidor de IA Interno

1. Em "Servidor de IA Interno", a pessoa digita o endereço e o token que a TI
   entregou, e salva.
2. O token vai para o `.env`, e o campo passa a mostrar "token salvo".
3. Ela liga o switch; o programa testa e lista os modelos. Sem lista, o seletor
   vira um campo para digitar o nome.

**Torto — endereço não reconhecido.** Ao salvar, abre o aviso de risco (RN-20). Sem
confirmar, o endereço não é salvo.

**Torto — o outro destino está ligado.** Ao ligar o switch, um aviso diz que o
outro será desligado. Confirmando, ele desliga e as configurações dele ficam
guardadas. Sem confirmar, nada muda.

**Torto — o servidor está fora do ar.** O teste falha, o switch volta para
desligado, e endereço e token ficam salvos.

### Habilitar a IA

1. Em "Habilitar IA", a pessoa liga o switch geral, que só responde com um
   destino configurado.
2. "IA revisora" liga junto, e "IA como motor de leitura" fica desligada.
3. Ela escolhe se a revisão inicia ao abrir ou ao clicar no botão.

**Torto — nenhum destino configurado.** O switch não liga, e uma frase diz onde
configurar.

**Torto — a pessoa desliga o destino em uso.** O switch geral desliga junto, e a
tela diz por quê. As posições dos outros ficam guardadas. Se o motor marcado era
a IA, a marca passa a outro, e a linha da "IA local" diz o motivo.

### Revisar com IA

1. No Anonimizar, com a revisão aberta, a IA começa sozinha ou pelo clique em
   "Revisar com IA", conforme a escolha da pessoa.
2. Se o endereço não for reconhecido e for o primeiro uso desta abertura, vem o
   aviso de risco.
3. O texto vai em pedaços, com os CPFs inteiros, sem travar a tela: uma linha
   mostra o andamento, com cancelar, e a pessoa já pode trabalhar.
4. Cada apontamento entra na lista conforme chega. Número novo entra mascarado.
5. A pessoa olha, solta o que não for CPF, e salva. O `.md` sai como hoje, sem
   nenhuma marca da IA.

**Torto — a pessoa não confirma o aviso.** Nada é enviado, e a revisão segue sem
IA.

**Torto — a IA cai no meio.** O que chegou fica, e uma linha fixa diz: "A IA revisou
até a página 12 de 30. O resto não teve segundo par de olhos", com o motivo e
"Tentar de novo", que retoma só o que faltou.

**Torto — a pessoa cancela.** A mesma linha diz o que faltou, e dá para retomar.

**Torto — salvar com a IA rodando.** O programa pergunta: "A IA ainda está
revisando. Salvar mesmo assim?". Voltando à revisão, ela continua. Salvando, ela
é parada.

**Torto — a IA aponta algo que não está no texto.** O apontamento é descartado.

### Ler com a IA como motor

1. Com a chave ligada e um modelo que lê imagem escolhido, "IA local" acende na
   escolha do motor, nos dois módulos.
2. A pessoa a marca e lê: cada página vai como imagem, e o texto volta. A
   conferência é a de sempre, e obrigatória.

**Torto — a IA falha numa página.** Vale a falha de leitura que os outros motores
já têm: a tela sai da espera e diz o que fazer, com nada gravado.

**Torto — chave desligada com a IA lembrada.** A marca passa a outro motor, e a
linha apagada diz o motivo (RN-37 da spec 002).

## Dados

| Informação | Origem | Onde mora | Observação |
| --- | --- | --- | --- |
| destino ligado | a pessoa | `preferencias.ini` | nenhum, LM Studio ou servidor |
| porta do LM Studio | a pessoa | `preferencias.ini` | padrão 1234 |
| endereço do servidor | a pessoa | `preferencias.ini` | vazio até ser preenchido |
| modelo da revisora e modelo do motor | a pessoa | `preferencias.ini` | um par por destino |
| switches da IA e como a revisão inicia | a pessoa | `preferencias.ini` | tudo desligado, e "ao clicar no botão" |
| token do servidor | a pessoa ou a TI | `.env`, em `IA_SERVIDOR_TOKEN` | nunca volta à tela |
| endereços locais | a TI | `.env`, em `IA_ENDERECOS_LOCAIS` | o programa só lê |
| apontamentos | a IA | só na memória, com a revisão aberta | nada é guardado (RN-40 da spec 002) |
| confirmação do aviso de endereço | a pessoa | só na memória, até fechar | nunca é gravada |

As variáveis `LLM_REMOTA_URL` e `LLM_REMOTA_API_KEY` do `.env.example`, que
nenhuma linha lê, saem. O `modelo.env` do instalador ganha as duas novas, em
branco.

## Estados da interface

**Telas de configuração**

- **vazio:** switches desligados e campos vazios. A única exceção é a porta do LM
  Studio.
- **carregando:** "Testando a conexão...", sem travar a janela.
- **com dados:** "respondendo", os modelos escolhidos e, no servidor, "token salvo".
- **erro:** o switch desligado, o motivo e o que fazer.

**Revisão**

- **IA nunca ligada:** "Revisar com IA" apagado, e uma frase dizendo onde ligar.
- **pronta:** o botão aceso, com a escolha de iniciar pelo clique.
- **revisando:** a linha de andamento com cancelar, e a lista recebendo itens.
- **terminada:** "Revisar de novo com IA", e a seção com o que chegou. Sem
  apontamentos, a linha diz que a IA não apontou nada, e lembra que isso não
  dispensa a leitura.
- **parcial:** a linha fixa com o que faltou, e "Tentar de novo".
- **sempre que a IA rodou:** o aviso das limitações (RN-26).

**Escolha do motor**

- **chave desligada:** "IA local" apagada, com a frase dizendo onde ligar, no lugar
  de "Funcionalidade a ser implementada".
- **chave ligada sem modelo:** continua apagada, com a frase pedindo o modelo.
- **chave ligada com modelo:** acesa, com uma linha resumindo a ressalva.

## Regras de negócio

### O menu

- RN-1: "Configurações de IA" fica no fim da faixa da esquerda, logo acima da
  versão, longe dos módulos.
- RN-2: o clique troca o menu inteiro pelo submenu, com o "voltar". Quando a saída
  descartaria uma revisão aberta e não salva, vale a mesma pergunta dos outros
  itens (RN-19 da spec 003).
- RN-3: dentro do submenu, só um item fica marcado por vez, como no menu de sempre
  (RN-2 da spec 001). Voltar não desliga nem muda nada.

### Os destinos

- RN-4: só um destino fica ligado por vez. Ligar um pede confirmação e desliga o
  outro. As configurações do desligado ficam guardadas e voltam ao religá-lo.
- RN-5: o endereço do LM Studio é sempre esta máquina, e só a porta pode mudar.
- RN-6: **um destino só conta como configurado depois de um teste que passou.** O
  teste roda ao ligar o switch e ao trocar o modelo, e há um botão para repetir.
  Se falhar, o switch volta para desligado, as escolhas ficam guardadas, e a tela
  diz o que fazer.
- RN-7: **o teste nunca envia documento.** A revisora recebe uma frase inventada,
  sem número nenhum; o motor, uma imagem pequena inventada. Passar só promete que
  aquele modelo respondeu naquela hora.
- RN-8: o teste não se repete a cada abertura. Com a IA ligada, abrir o programa
  não abre conexão nenhuma. Se o destino cair depois, vale a RN-36.
- RN-9: a lista de modelos do LM Studio traz o nome e o que estiver disponível
  sobre cada um. Modelo escolhido que não está carregado faz o teste falhar ou
  demorar conforme o LM Studio se comportar, e a frase da tela diz para carregá-lo
  lá.

### O token

- RN-10: a pessoa digita o token no programa, e ele fica no `.env`. Quem preencher
  a linha à mão tem o mesmo resultado.
- RN-11: **o programa grava só a linha do token**, preservando os comentários, a
  acentuação, o formato e as outras linhas. Não havendo a linha, ela é
  acrescentada. Nenhuma outra escolha da pessoa vai para o `.env`.
- RN-12: **depois de salvo, o token nunca volta à tela**, nem em mensagem de erro.
  O campo mostra "token salvo", com substituir e apagar.
- RN-13: não dando para gravar, a tela diz isso, e o token não fica em outro lugar.
- RN-14: atualizar a versão mantém o token. Desinstalar não o deixa para trás.

### O endereço

- RN-15: nenhum endereço de fora é escrito no programa, e o do servidor nasce
  vazio.
- RN-16: **o programa não bloqueia endereço nenhum.** O endereço de cada instituição
  varia, e a decisão é de quem usa, depois de avisada.
- RN-17: passam sem aviso: a própria máquina; os nomes terminados em `.ufsc.br`; o
  que for número interno ou der em número interno, perguntado à rede; e o que
  estiver em `IA_ENDERECOS_LOCAIS`, exato ou por terminação.
- RN-18: **número interno não prova que é a UFSC.** Isso fica escrito na tela do
  servidor, porque na rede de casa ele também aparece. *(Corrigida em 31/10/2026: dizia
  também "no aviso", que só abre para endereço não reconhecido, e ali a frase não faria
  sentido.)*
- RN-19: os demais abrem o aviso de risco: o endereço digitado pode ser externo, e
  há risco em enviar dados pessoais, como CPF, para servidores externos. O botão já
  escolhido é o que não envia, de modo que Enter ou Esc não confirmam nada.
- RN-20: o aviso abre ao salvar o endereço, e no primeiro uso da IA a cada abertura
  do programa, valendo para a revisora e o motor juntos. Trocar o endereço com o
  programa aberto faz perguntar de novo. A confirmação nunca é gravada.
- RN-21: a cada uso, o programa confere de novo o endereço. Se um nome que dava em
  número interno passar a dar em número externo, o aviso abre antes de enviar.
- RN-22: em `http://` e não reconhecido, o aviso diz também que o texto e o token
  viajam sem cifra.
- RN-23: **redirecionamento não é seguido.** O destino final é sempre o que a pessoa
  viu.

### A revisora

- RN-24: "Habilitar IA" só liga com um destino configurado. Ao ligar, liga a revisora
  e deixa o motor desligado. Desligar o destino em uso desliga o geral, e a tela
  diz por quê; as posições dos outros ficam guardadas.
- RN-25: a revisão inicia sozinha, ao abrir a revisão, ou pelo botão, conforme a
  escolha da pessoa. Com a revisora desligada, o botão fica apagado, com a frase
  dizendo onde ligar.
- RN-26: **a revisora vê só o texto**, com os CPFs inteiros e nos dois destinos. A
  tela avisa que ela não compara com a página original, e que um dígito lido errado
  num número que parece normal pode passar.
- RN-27: **a conferência não muda.** Nenhum apontamento marca algo como conferido,
  e não ter apontamento não dispensa a leitura.
- RN-28: **a IA nunca escreve o texto.** A resposta dela só pode apontar: quem faz a
  máscara é o programa. O que vier escrito dentro do documento, mesmo em forma de
  ordem à IA, não pode soltar máscara nem mudar o texto, porque nenhuma resposta
  tem esse poder.
- RN-29: cada apontamento diz de onde veio, com a IA, o destino e o modelo, e o
  motivo dela. Ele aparece na seção **"A IA pediu para olhar"**, abaixo dos
  suspeitos e com cor própria, separada dos tipos de CPF (`programa/cpf.py`). *(Corrigida
  em 31/10/2026: o comentário num número já listado diz só "IA: ...", como no rascunho
  aprovado. O destino e o modelo aparecem nos itens da seção.)*
- RN-30: **número apontado que o programa não tinha achado entra mascarado**, pela
  regra da máscara à mão (RN-9 da spec 003), e a pessoa solta se não for CPF. Soltar
  segue a RN-10 da spec 003: o que passa na conta pede a dupla conferência. Ao
  salvar, vale a RN-11 da spec 003. Com menos de 8 dígitos ele é só apontado, e
  trecho estragado sem número também.
- RN-31: **comentário sobre um número já listado vira etiqueta nele**, e nunca muda
  a seção, a contagem nem a máscara. Isso vale também para o que a pessoa já liberou
  e o que ela mascarou à mão.
- RN-32: trecho citado que não existe no texto é descartado. Revisar de novo não
  repete o que já está na lista.
- RN-33: os apontamentos valem só na revisão aberta, e nada deles entra no `.md`
  (RN-12 da spec 003).
- RN-34: salvar com a IA rodando pergunta antes. Sair da revisão, para outro item do
  menu ou outro documento, ou fechar o programa, para a IA antes, sem o programa
  estourar (`CLAUDE.md`, sobre o trabalho ao lado da janela). Minimizar a janela não
  para. Voltando à revisão, a faixa diz o que faltou, e dá para retomar.
- RN-35: os pedidos vão por um caminho em que cada um vale sozinho, sem pedir ao
  destino que guarde a conversa.

### As falhas

- RN-36: **a IA nunca trava a conferência.** Destino fora do ar, lento demais ou
  com erro leva à linha fixa, e a revisão segue.
- RN-37: **falha no meio guarda o que chegou.** Os números mascarados continuam
  mascarados. A linha diz até onde a IA foi, com o motivo, e "Tentar de novo" retoma
  só o que faltou. Em `.docx`, `.md` e `.txt`, ela fala em partes do texto. Resposta
  que o programa não entende conta como falha daquele pedaço.

### O motor

- RN-38: com "IA como motor de leitura" desligada, "IA local" fica apagada nos dois
  módulos, com a frase dizendo onde ligar. Com a chave ligada e sem modelo, a frase
  pede o modelo.
- RN-39: o switch do motor traz a ressalva, datada: até a criação do programa, os
  modelos locais eram muito inferiores ao PaddleOCR e ao Tesseract na leitura, e o
  uso indicado é como revisora. Junto, o aviso de que a página vai com os CPFs
  inteiros.
- RN-40: o seletor do motor só aparece com a chave ligada, vem vazio e oferece só
  modelos que leem imagem. Se o destino não disser quais leem, ele oferece todos, e
  o teste com imagem (RN-7) decide.
- RN-41: a conferência continua obrigatória, e o texto segue o mesmo caminho dos
  outros motores (RN-15 da spec 003).
- RN-42: a marca "IA local" é lembrada por módulo, como as outras (RN-36 da spec
  002). Sem chave ou sem destino, a marca passa a outro motor, e a troca aparece na
  tela (RN-29 e RN-37 da spec 002).

### O que não pode mudar

- RN-43: **sem a IA ligada, o programa é o de hoje:** nenhuma chamada de rede e
  nenhum caminho novo executado, além da tela de configuração em si.
- RN-44: **um arquivo só fala com a rede.** Os testes de guarda (`test_cpf.py`,
  `test_leitura.py` e `test_motor.py`) continuam barrando sinais de rede em todo o
  resto, com esse arquivo nomeado como a única exceção. Ele não faz download.
- RN-45: os testes nunca dependem de um LM Studio ou servidor de verdade, e não tocam
  o `.env` nem o `preferencias.ini` da raiz.

## Critérios de aceite

### Menu e destinos

- Dado o programa aberto, então "Configurações de IA" está no fim da faixa, acima
  da versão, e o clique troca o menu por "LM Studio", "Servidor de IA Interno" e
  "Habilitar IA", com o "voltar".
- Dada uma revisão não salva, quando a pessoa clica em "Configurações de IA", então
  vem a pergunta de descartar.
- Dado o LM Studio ligado, quando a pessoa liga o switch do servidor e confirma,
  então o LM Studio desliga; e, ao religá-lo, a porta e os modelos voltam como
  estavam.
- Dado o aviso de troca, quando a pessoa não confirma, então nada muda.
- Dado um destino fora do ar, quando a pessoa liga o switch, então ele volta para
  desligado, as escolhas continuam, e a tela diz o que fazer.
- Dado um destino simulado, quando o teste roda, então o que foi enviado não tem
  número nenhum.
- Dada a IA ligada, quando o programa abre, então nenhuma conexão é aberta.
- Dado um servidor que não lista modelos, então o seletor vira um campo de digitar.

### Token

- Dado um `.env` com comentários, acentos e `TESSERACT_CAMINHO`, salvo nos três
  formatos do Bloco de Notas, quando a pessoa salva o token, então só a linha dele
  muda, e o resto do arquivo fica idêntico byte a byte.
- Dado um `.env` sem a linha, quando a pessoa salva, então a linha é acrescentada.
- Dado um token salvo, então a tela mostra só "token salvo", e nenhuma tela ou
  mensagem de erro traz o valor, mesmo com o servidor devolvendo um erro que o cite.
- Dado um token salvo, então o `preferencias.ini` não o contém.
- Dado um `.env` que não aceita gravação, quando a pessoa salva, então a tela diz
  isso, e o token não vai para outro lugar.
- Dada uma instalação com token, quando se atualiza a versão, então ele continua;
  quando se desinstala, então ele não fica na pasta.

### Endereço

- Dados a própria máquina, um nome `.ufsc.br`, um número interno, um nome que dá em
  número interno e um endereço de `IA_ENDERECOS_LOCAIS` (exato e por terminação),
  quando a pessoa salva, então não há aviso.
- Dado um endereço não reconhecido, quando a pessoa salva, então vem o aviso; sem
  confirmar, ele não é salvo.
- Dado o aviso aberto, quando a pessoa aperta Enter ou Esc, então nada é confirmado.
- Dado um endereço não reconhecido e salvo, quando o programa abre e a IA é usada
  pela primeira vez, então vem o aviso; no segundo uso, revisora ou motor, não vem;
  ao fechar e abrir, vem de novo.
- Dado o aviso, quando a pessoa não confirma, então nada é enviado, e a revisão ou
  leitura segue sem IA.
- Dado um nome que passou a dar em número externo, quando a IA vai ser usada, então
  vem o aviso antes de enviar.
- Dado um endereço em `http://` não reconhecido, então o aviso fala da falta de cifra.
- Dado um servidor simulado que redireciona, então o programa não segue, e a linha
  de falha aparece.

### Revisão

- Dada a revisora desligada, então "Revisar com IA" está apagado, com a frase dizendo
  onde ligar.
- Dada a opção "ao clicar no botão", quando a revisão abre, então nada é enviado até
  o clique. Dada "ao abrir a revisão", então a IA começa, sem clique.
- Dada a IA revisando, então a pessoa consegue navegar, liberar e mascarar, e o
  andamento e o cancelar estão à vista.
- Dado um documento com CPF válido, então o texto recebido pelo destino simulado traz
  o CPF inteiro.
- Dado um número novo de 11 dígitos apontado, então ele aparece na seção "A IA pediu
  para olhar", mascarado, com o motivo e a origem, e pode ser solto; passando na
  conta, soltar pede a dupla conferência.
- Dado um número apontado com menos de 8 dígitos, ou um trecho estragado, então ele é
  apontado, e o texto não muda.
- Dado um comentário sobre um número já listado, inclusive liberado, então ele ganha a
  etiqueta, e a seção, a contagem e a máscara não mudam.
- Dado um trecho citado que não está no texto, então nada aparece.
- Dada uma resposta que tente soltar uma máscara ou reescrever o texto, então nada
  disso acontece.
- Dado um documento cujo texto traga uma ordem à IA, então o texto e as máscaras
  continuam dependendo só do que ela apontar.
- Dada a IA terminada sem apontamento, então a tela diz isso e lembra que não dispensa
  a leitura.
- Dada a revisão salva, então o `.md` não tem nada escrito pela IA, nem etiqueta nem
  motivo, além das máscaras.
- Dada a IA rodando, quando a pessoa salva, então vem a pergunta; voltando, a IA
  continua.
- Dada a IA rodando, quando a pessoa fecha o programa, então ele fecha limpo.
- Dada uma revisão reaberta, então nenhum apontamento anterior aparece.

### Falhas

- Dado um destino que cai no pedaço 3 de 5, então os apontamentos dos pedaços 1 e 2
  ficam, e a linha diz o que faltou; "Tentar de novo" envia só os pedaços 3 a 5.
- Dada uma resposta que o programa não entende, então aquele pedaço entra no que
  faltou.
- Dado um `.docx` que falha no meio, então a linha fala em partes do texto.
- Dado um destino que não responde, então a tela sai da espera dentro do tempo limite,
  e a revisão segue.

### Motor

- Dada a chave desligada, então "IA local" está apagada nos dois módulos, com a frase
  dizendo onde ligar.
- Dada a chave ligada, então a ressalva e o aviso dos CPFs estão junto do switch, com
  a data.
- Dado um modelo que lê imagem escolhido, então "IA local" acende, e, marcada, é ela
  que lê, com a conferência de sempre.
- Dada "IA local" lembrada e a chave desligada, quando o módulo abre, então a marca
  passa a outro motor, e a linha diz o motivo.
- Dada uma falha numa página, então vale a tela de falha de leitura, com nada gravado.

### O que não pode mudar

- Dada a IA desligada, quando um documento passa por todo o caminho, então nenhuma
  conexão de rede é aberta, e o arquivo da rede nem é carregado.
- Dado qualquer arquivo do programa além do da rede, então os testes de guarda não
  encontram sinal de rede, e o da rede não tem download.
- Dada a lista de testes rodando sem LM Studio nem servidor, então todos passam, e o
  `.env` e o `preferencias.ini` da raiz ficam intactos.
- Dada a separação da lembrança do motor feita, então as RN-36 a RN-41 da spec 002
  continuam passando nos dois módulos, sem a tela precisar saber do arquivo.

## Verificações durante a construção

Não mudam o que está combinado acima, mas precisam de resultado registrado na
conferência. O que mudar algo que se vê na tela volta à solicitante.

- O que o LM Studio faz com o modelo não carregado (RN-9), medido nesta máquina.
- O que uma versão antiga do LM Studio responde, e se o seletor do motor cai no caso
  da RN-40.
- Que nada do documento fica guardado no LM Studio depois de uma revisão (RN-35).
- Que o token sai ao desinstalar (RN-14), e a forma: apagar a linha, ou o `.env`.
- O limite de cada pedaço de texto, medido, e o tempo limite de cada pedido.

**Limite conhecido:** sem o servidor da TI disponível, a conferência da tela do
servidor usa um servidor simulado nesta máquina. Isso prova o caminho, e não que o
servidor real fala do mesmo jeito. Se ele guarda o texto recebido, só a TI pode
responder, e isso entra nos roteiros da entrega.

## Emendas que esta spec traz

Escritas nas specs de origem na aprovação, em 31/10/2026, valendo quando a
funcionalidade estiver construída.

- **`CLAUDE.md`, regra dura "nenhum caminho de código aponta para fora da UFSC":** o
  programa continua sem nenhum endereço de fora escrito nele. Quem digita pode apontar
  para fora, depois de avisado, e o teste prova o aviso.
- **`CLAUDE.md`, no combinado:** o `.env` deixa de ser só lido, por uma linha, e o
  motor "IA local" deixa de estar fora de escopo.
- **Spec 001, RN-2:** ganha o submenu (RN-1 a RN-3 daqui).
- **Spec 002, RN-20:** "nunca manda documento para lugar nenhum" passa a valer com a
  IA desligada. "Nunca baixa nem instala nada" fica inteira.
- **Spec 002, RN-21 e RN-25:** "IA local" passa a acender com a chave.
- **Spec 002, emenda de 28/10/2026 ("escrever no `.env`" fora de escopo):** passa a
  valer a exceção da RN-11 daqui. O critério byte a byte continua para as escolhas
  de motor e de janela.
- **Spec 003, RN-20:** "nenhum código deste módulo fala com a internet" passa a ter a
  exceção da RN-44 daqui, só com a IA ligada.
- **Backlog, item 4:** reescrito na aprovação desta spec.

## Acréscimos da lente crítica (31/10/2026)

Vieram da revisão da construção, antes da conferência na tela. Nenhum muda o que foi
combinado: fecham buracos que deixariam dígito à vista ou o token sair sem aviso.

- RN-46: **número apontado com mais de 14 dígitos não vira máscara**, e fica só
  apontado. A máscara esconde as pontas do que recebe, e uma citação com dois números
  deixaria o miolo à vista, com a lista dizendo "mascarado".
- RN-47: **citação que vai além de um número já listado** comenta o número e aponta o
  resto dela, para um segundo número ali não passar sem ninguém ver.
- RN-48: **a IA diz se o número parece CPF.** Dito claramente que não, ele fica só
  apontado, sem máscara: um CEP não vira máscara por causa da opinião de que não é
  CPF. Sem resposta clara, vale como se parecesse.
- RN-49: **ligar e testar também passam pelo aviso de endereço**, porque mandam o
  token. Abrir a tela não pergunta nem envia nada sem o endereço reconhecido ou já
  confirmado.
- RN-50: **endereço novo com token salvo pergunta** se o token fica ou sai, porque ele
  é daquele servidor. O botão já escolhido é o que apaga.
- RN-51: **o teste que falha ao trocar de destino devolve o destino de antes.** A falha
  não deixa a pessoa sem nenhum dos dois.
- RN-52: **a leitura pela IA fixa o destino e o modelo ao começar.** Trocar o destino
  no meio não manda as páginas seguintes para outro lugar.
- RN-53: **resposta cortada pelo limite do modelo é falha**, e não página pela metade.
  O raciocínio que alguns modelos escrevem antes da resposta não entra no texto.

## Acréscimos da revisão de segurança (31/10/2026)

- RN-54: **todo pedido que leva o token confere o endereço antes**, inclusive o teste do
  motor, ao ligar a chave em "Habilitar IA", e o teste ao trocar de modelo.
- RN-55: **não dando para apagar o token ao trocar de endereço, o endereço novo não é
  salvo**, e a tela diz por quê.
- RN-56: **a citação da IA é procurada sem ligar para a diferença de espaços.** Um número
  de verdade não é descartado como inventado por um espaço a mais.

## Questões em aberto

Nenhuma.

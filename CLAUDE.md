# AnomizadorCAPCF

## O que é

Programa para a CAPCF (Coordenadoria de Análise de Prestações de Contas
Fundacionais da UFSC) tirar o CPF de documentos antes de eles irem para
assistentes de IA em chatbots convencionais. Roda como janela própria, uma
pessoa por vez, instalado nas máquinas do núcleo. Só CPF é anonimizado — nome
não é considerado sensível para este uso.

## Stack e por quê

**Python 3.12**, pela prática de quem mantém o projeto e pelo ecossistema mais
maduro do mercado para ler PDF, rodar OCR e achar padrão com regex.

| Peça | Escolha |
| --- | --- |
| Interface | PySide6 (Qt) — menu lateral + painel principal |
| Leitura de PDF | PyMuPDF — extrai texto, detecta ausência de texto, converte página em imagem para o OCR |
| OCR | Tesseract, via pytesseract, com pacote de português |
| Validação de CPF | Sem biblioteca — dígito verificador calculado na mão |
| Dados | Sem banco — cada documento é processado sozinho, sem estado entre usos |
| Testes | pytest |
| Distribuição | `.exe` único via PyInstaller — sem exigir instalação de Python nas máquinas do núcleo |

Descartado: C#/.NET (sem fluência de quem mantém) e Electron (mais pesado, OCR
pior). Atenção: PyMuPDF é AGPL — ok para uso interno da UFSC, conferir se um
dia o programa sair da universidade.

## Comandos

| O quê | Comando |
| --- | --- |
| Criar/atualizar o ambiente virtual | `python -m venv .venv` |
| Instalar as dependências | `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` |
| Rodar os testes | `.\.venv\Scripts\python.exe -m pytest` |
| Rodar o programa | `abrir\abrir-dev.bat` (ou `.\.venv\Scripts\python.exe programa\main.py`) |
| Gerar o instalador | *(ainda não existe — entra com a `skill-11-gerente-de-entrega`)* |

## Onde ficam as coisas

| Pasta | O que tem |
| --- | --- |
| `programa/` | o código do programa e os testes, lado a lado (nasce na primeira etapa construída) |
| `especificacoes/` | `backlog.md` e `backlog.html` (o previsto), `specs/` (o combinado de cada funcionalidade) |
| `mockups/` | rascundos de tela, sistema de design, mapa do entendimento — tudo desenhado pela `skill-07-designer-de-telas` |
| `dados-exemplo/` | massa sintética para testar — nunca documento real |
| `abrir/` | atalho de abrir o programa em modo desenvolvimento (nasce quando houver algo para ver na tela) |
| `builds/` | o `.exe` gerado no dia da entrega — conteúdo fora do histórico |
| `.venv/` | ambiente virtual do Python — cada máquina cria o seu, fora do histórico |

## O combinado com quem usa

- **Quem usa**: o núcleo da CAPCF, uma pessoa por vez, cada uma na própria
  máquina — não é serviço compartilhado.
- **Entrada**: PDF, às vezes com texto por dentro (gerado no sistema de
  processos), às vezes só imagem (impresso, ou anexo escaneado por terceiro).
  O programa detecta sozinho se há texto, e só roda o OCR quando não há.
- **Saída**: `.md`, com as tabelas preservadas como tabelas de texto — para a
  pessoa arrastar para dentro da conversa com o assistente.
- **Máscara do CPF**: 3 primeiros dígitos → `***`, 2 últimos → `**`, mantendo a
  pontuação original (`123.456.789-10` → `***.456.789-**`; barra também vira
  traço). Reconhece CPF com pontos e traço, sem pontos, sem nada, e com barra.
- **Motor de OCR**: dois no menu — Tesseract local, e (fora do escopo desta
  primeira versão) uma LLM remota, apontando para um servidor que a TI da UFSC
  pretende montar dentro da rede da universidade. **Nunca** um serviço de
  empresa externa — seria contradizer o motivo do programa existir.
- **Conferência humana**: parte fixa do processo quando o texto veio de OCR, e
  não etapa opcional. O dígito verificador do CPF confere o que foi lido; o
  que não fechar vira lista de suspeitos para a pessoa olhar, em vez de passar
  calado.
- **PDF grande com vários documentos**: entra como um documento só, sai como um
  `.md` só. Separar por dentro é melhoria futura.
- **Fora de escopo desta versão**: outro dado sensível além do CPF; saída em
  XLSX ou PDF (fica para um "anonimizador de documentos" futuro); construir o
  assistente de IA em si; qualquer uso oficial do arquivo gerado.

## Regras duras

Três nascem do pacote de skills, e valem sempre:

- O agente trabalha **dentro desta pasta** (`c:\Dev\AnomizadorCAPCF`). Sair
  dela é pedido do usuário, com caminho e tarefa nomeados, e vale só para
  aquela tarefa.
- **Segredo mora no `.env`**, nunca no código, nunca no chat, nunca no
  histórico. Dado real de pessoa (CPF, nome, documento) não entra no
  repositório de jeito nenhum, nem em `dados-exemplo/`.
- **Desenvolvimento e produção não compartilham** configuração nem dado. Aqui,
  "produção" é a instalação nas máquinas do núcleo, processando documento
  real; "desenvolvimento" é esta máquina, processando só massa sintética. Não
  existe `.env.producao` porque não há configuração central compartilhada —
  cada instalação tem o próprio `.env` local, preenchido na hora, nunca
  versionado.

Duas específicas deste projeto:

- **Tarja nunca substitui remoção.** Mascarar o CPF é reescrever o texto —
  nunca desenhar algo por cima que ainda deixa o número original por baixo,
  recuperável por quem copiar o texto.
- **Nenhum caminho de código aponta para um serviço de OCR ou LLM fora da
  UFSC.** É a razão de existir do programa: documento com CPF não pode sair da
  universidade para ser processado.

## Convenções

Idioma do projeto: português. Commits e comentários também.

Comentário no código: **em português, explicando o porquê, nunca o quê.**
Comentário que repete o que a linha já diz é ruído, e no dia em que a linha
muda e ele não, passa a mentir. Comenta-se a decisão que não está escrita em
lugar nenhum: por que este número, por que este caso é tratado à parte, de
onde veio esta regra. Linguagem do dia a dia — quem lê pode não programar.

## O que já nos mordeu

- Instalar programa em `Program Files` (como o Tesseract) exige confirmação do
  Windows que só aparece numa sessão com tela — comando rodado por controle
  remoto ou terminal sem interface trava nessa hora. Resolve rodando com
  alguém na frente da máquina para confirmar.

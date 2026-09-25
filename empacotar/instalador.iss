; Receita do instalador, para o Inno Setup.
;
; Gera-se pelo empacotar\gerar-entrega.bat, que passa o número da versão lido
; de programa\versao.py - ele não se escreve aqui, para o instalador e a tela
; nunca dizerem versões diferentes. Rodado sem ele, o instalador nem é gerado.

#ifndef Versao
  #error Gere pelo empacotar\gerar-entrega.bat: ele passa o numero da versao.
#endif

#define Nome "Anonimizador CAPCF"
#define Executavel "Anonimizador CAPCF.exe"

[Setup]
; A identidade do programa para o Windows. NUNCA mude este número: é por ele
; que a versão seguinte se reconhece como atualização desta, e não como um
; segundo programa instalado ao lado.
AppId={{3825E2BD-0F1E-4D71-9CAB-F8994F19CC8F}
AppName={#Nome}
AppVersion={#Versao}
AppVerName={#Nome} {#Versao}
; Curto, porque o Windows mostra o editor numa coluna estreita da lista de
; aplicativos; a frase inteira vai no comentário, que aparece nos detalhes.
AppPublisher=CGU
AppComments=O programa foi desenvolvido pela CGU no âmbito da consultoria realizada à UFSC em 2026.
VersionInfoVersion={#Versao}

; Instala só para quem está usando, na pasta de programas pessoal, sem pedir
; administrador (plano de entrega, 23/09/2026). A funcionalidade 4 vai gravar
; configuração ao lado do programa, e em Program Files cada gravação pediria
; a confirmação do Windows. Mudar de lugar depois custaria uma volta em cada
; máquina do núcleo.
PrivilegesRequired=lowest
DefaultDirName={autopf}\{#Nome}
DisableProgramGroupPage=yes
DisableDirPage=yes

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

OutputDir=..\builds\instalador
OutputBaseFilename=Anonimizador-CAPCF-{#Versao}-instalador
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#Nome}
UninstallDisplayIcon={app}\{#Executavel}

[Languages]
Name: "portugues"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "atalho_na_area_de_trabalho"; Description: "Criar um atalho na área de trabalho"; Flags: unchecked

[Files]
Source: "..\builds\programa\{#Nome}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; O instalador do Tesseract vai na pasta "instaladores", ao lado do programa: é
; lá que o botão "instalar agora" o procura (spec 002). Sem ele, o botão nasce
; apagado e a pessoa fica sem saída na primeira leitura.
Source: "..\instaladores\tesseract-ocr-w64-setup-*.exe"; DestDir: "{app}\instaladores"; Flags: ignoreversion
; O .env desta instalação já nasce com o nome certo, em branco, para a TI só
; abrir e preencher. Criado à mão no Bloco de Notas, ele sai ".env.txt" - o
; Windows esconde o ".txt", e o programa ignora o arquivo em silêncio (teste
; da entrega, 25/09/2026). Nunca é o .env desta máquina de desenvolvimento: é
; o modelo em branco de empacotar\. Numa instalação por cima, o que a TI já
; preencheu fica como está.
Source: "modelo.env"; DestDir: "{app}"; DestName: ".env"; Flags: onlyifdoesntexist

[Icons]
Name: "{autoprograms}\{#Nome}"; Filename: "{app}\{#Executavel}"
Name: "{autodesktop}\{#Nome}"; Filename: "{app}\{#Executavel}"; Tasks: atalho_na_area_de_trabalho

[Run]
Filename: "{app}\{#Executavel}"; Description: "Abrir o {#Nome} agora"; Flags: nowait postinstall skipifsilent

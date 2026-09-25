@echo off
title Anonimizador CAPCF - gerar a entrega
echo.
echo   Gerando o instalador do Anonimizador CAPCF...
echo.

cd /d "%~dp0.."

REM Cada passo para tudo se der errado: entrega gerada com um passo falho no
REM meio parece pronta e nao esta. Os testes vem primeiro - verificacao
REM vermelha bloqueia a entrega, e nunca "gera assim mesmo".
echo   [1/4] Rodando os testes...
".venv\Scripts\python.exe" -m pytest -q
if errorlevel 1 goto erro

REM O numero sai de programa\versao.py, o mesmo que a janela mostra.
REM O "call" na frente e de proposito: comando que comeca com aspas perde as
REM aspas de fora dentro do for, e o caminho do Python quebraria.
for /f "delims=" %%v in ('call ".venv\Scripts\python.exe" -c "import sys; sys.path.insert(0, 'programa'); from versao import VERSAO; print(VERSAO)"') do set VERSAO=%%v
if "%VERSAO%"=="" goto erro
echo   Versao: %VERSAO%

REM Sem o instalador do Tesseract, o botao "instalar agora" nasceria apagado
REM nas maquinas do nucleo. Ele e baixado a parte (fora do historico), e o
REM roteiro de entrega diz de onde.
if not exist "instaladores\tesseract-ocr-w64-setup-*.exe" (
    echo.
    echo   Falta o instalador do Tesseract na pasta "instaladores".
    goto erro
)

echo   [2/4] Montando a pasta do programa...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --distpath builds\programa --workpath builds\trabalho empacotar\anonimizador.spec
if errorlevel 1 goto erro

REM O Inno Setup pode estar na pasta de programas pessoal (como o winget o
REM instala) ou na de todos os usuarios.
echo   [3/4] Procurando o Inno Setup...
set ISCC=
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe
if "%ISCC%"=="" (
    echo   Inno Setup nao encontrado. Instale com:
    echo   winget install --id JRSoftware.InnoSetup --exact
    goto erro
)

echo   [4/4] Montando o instalador...
"%ISCC%" /Qp /DVersao=%VERSAO% empacotar\instalador.iss
if errorlevel 1 goto erro

REM A pasta que vai para o nucleo: o instalador e o roteiro, e nada mais. E
REM refeita do zero a cada vez, para nunca levar sobra de uma geracao anterior.
set ENTREGA=builds\entrega-%VERSAO%
if exist "%ENTREGA%" rmdir /s /q "%ENTREGA%"
mkdir "%ENTREGA%"
copy /y "builds\instalador\Anonimizador-CAPCF-%VERSAO%-instalador.exe" "%ENTREGA%\" >nul
if errorlevel 1 goto erro
copy /y "empacotar\como-instalar.html" "%ENTREGA%\Como instalar.html" >nul
if errorlevel 1 goto erro

echo.
echo   Pronto: %ENTREGA%
echo.
pause
exit /b 0

:erro
echo.
echo   Alguma coisa deu errado nas linhas acima. Nada foi entregue.
echo   Copie a mensagem e me mande - nao feche antes de copiar.
echo.
pause
exit /b 1

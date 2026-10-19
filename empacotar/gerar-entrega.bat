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

REM Os roteiros sao refeitos a mao a cada versao, num prompt proprio (decisao
REM de 09/10/2026, no CLAUDE.md), e daqui so sao copiados. Roteiro que nao
REM cita a versao que esta saindo e roteiro que ninguem refez - e ele iria
REM para o nucleo com o numero e as regras da versao anterior.
for %%r in (como-instalar como-usar) do (
    findstr /c:"%VERSAO%" "empacotar\%%r.html" >nul
    if errorlevel 1 (
        echo.
        echo   O roteiro empacotar\%%r.html nao fala da versao %VERSAO%.
        echo   Refaca os dois roteiros para esta versao antes de gerar a entrega.
        goto erro
    )
)

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

REM O PyInstaller termina sem erro mesmo sem os modelos do PaddleOCR, que
REM entram por fora (anonimizador.spec). Sem eles, o motor padrao chegaria ao
REM nucleo como "instalacao incompleta", e reinstalar nao resolveria. Os nomes
REM vem do proprio programa, para a conferencia nunca divergir do que ele abre
REM (lente critica da etapa 2 da funcionalidade 7, 19/10/2026).
echo   Conferindo os modelos do PaddleOCR na pasta montada...
".venv\Scripts\python.exe" -c "import sys; sys.path.insert(0, 'programa'); from pathlib import Path; from motor_paddleocr import MODELOS; pasta = Path(r'builds\programa\Anonimizador CAPCF\_internal\rapidocr\models'); faltam = [m for m in MODELOS if not (pasta / m).is_file()]; print('   Faltam na pasta montada: ' + ', '.join(faltam)) if faltam else None; sys.exit(1 if faltam else 0)"
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

REM A pasta que vai para o nucleo: o instalador e os dois roteiros, e nada
REM mais. E refeita do zero a cada vez, para nunca levar sobra de uma geracao
REM anterior - e, pelo mesmo motivo, nada entra nela copiado a mao: o que
REM nao esta aqui fica de fora da proxima entrega sem ninguem perceber.
set ENTREGA=builds\entrega-%VERSAO%
if exist "%ENTREGA%" rmdir /s /q "%ENTREGA%"
mkdir "%ENTREGA%"
copy /y "builds\instalador\Anonimizador-CAPCF-%VERSAO%-instalador.exe" "%ENTREGA%\" >nul
if errorlevel 1 goto erro
copy /y "empacotar\como-instalar.html" "%ENTREGA%\Como instalar.html" >nul
if errorlevel 1 goto erro
copy /y "empacotar\como-usar.html" "%ENTREGA%\Como usar.html" >nul
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

@echo off
title Anonimizador CAPCF - modo DEV
echo.
echo   Abrindo o Anonimizador CAPCF em modo de desenvolvimento...
echo.

cd /d "%~dp0.."

echo   [1/2] Conferindo o ambiente...
if not exist ".venv\Scripts\python.exe" (
    echo   Ambiente virtual nao encontrado - criando...
    python -m venv .venv
    if errorlevel 1 goto erro
)

REM A instalacao roda sempre, e nao so quando o ambiente e criado: uma
REM instalacao interrompida no meio deixa a pasta .venv de pe mas incompleta, e
REM quem so clica no atalho ficaria preso nesse estado para sempre. Estando tudo
REM instalado, este passo confere e sai em poucos segundos.
echo   Conferindo as dependencias, pode levar um minuto na primeira vez...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto erro

echo   [2/2] Abrindo o programa...
echo.
".venv\Scripts\python.exe" programa\main.py
if errorlevel 1 goto erro
goto fim

:erro
echo.
echo   Alguma coisa deu errado nas linhas acima.
echo   Copie a mensagem e me mande - nao feche antes de copiar.
echo.
pause
exit /b 1

:fim
echo.
echo   O programa fechou. Pode fechar esta janela.
pause

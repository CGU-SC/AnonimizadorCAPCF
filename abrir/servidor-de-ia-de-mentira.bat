@echo off
title Servidor de IA de mentira
echo.
echo   Sobe um servidor de IA de mentira nesta maquina, na porta 1234: a mesma do
echo   LM Studio. Ele nao pensa nada: lista dois modelos inventados e aponta o que
echo   estiver no documento de exemplo. Serve para conferir as telas sem um modelo.
echo   Para parar, feche esta janela.
echo.

cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    echo   Ambiente virtual nao encontrado. Abra primeiro o abrir-dev.bat,
    echo   que prepara o ambiente, e depois volte a este.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" abrir\servidor_de_ia_de_mentira.py %*
if errorlevel 1 goto erro
goto fim

:erro
echo.
echo   Alguma coisa deu errado nas linhas acima. Se a porta 1234 ja estiver em uso,
echo   feche o LM Studio e abra este atalho de novo.
echo.
pause
exit /b 1

:fim
pause

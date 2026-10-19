@echo off
title Anonimizador CAPCF - modo DEV, sem nenhum motor
echo.
echo   Abrindo o Anonimizador CAPCF como se NENHUM motor funcionasse: nem o
echo   PaddleOCR nem o Tesseract. Nada foi desinstalado: o programa so finge.
echo.
echo   Para simular a TI instalando o Tesseract com o programa aberto,
echo   de dois cliques em simular-instalacao.bat, nesta mesma pasta.
echo.

cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    echo   Ambiente virtual nao encontrado. Abra primeiro o abrir-dev.bat,
    echo   que prepara o ambiente, e depois volte a este.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" abrir\sem_motor.py sem-nenhum
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

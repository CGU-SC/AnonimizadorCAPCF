@echo off
title AnomizadorCAPCF - modo DEV, sem o motor de leitura
echo.
echo   Abrindo o AnomizadorCAPCF como se o Tesseract NAO estivesse instalado.
echo   Nada foi desinstalado: o programa so finge que nao encontrou o motor.
echo.
echo   Para simular a TI terminando a instalacao com o programa aberto,
echo   de dois cliques em simular-instalacao.bat, nesta mesma pasta.
echo.

cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    echo   Ambiente virtual nao encontrado. Abra primeiro o abrir-dev.bat,
    echo   que prepara o ambiente, e depois volte a este.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" abrir\sem_motor.py
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

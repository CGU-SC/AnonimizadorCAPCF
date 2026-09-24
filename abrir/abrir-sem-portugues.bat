@echo off
title Anonimizador CAPCF - modo DEV, Tesseract sem o portugues
echo.
echo   Abrindo o Anonimizador CAPCF como se o Tesseract estivesse instalado
echo   SEM o pacote de portugues. Nada foi mexido na instalacao: o programa
echo   so finge que o pacote nao esta la.
echo.
echo   Para simular a TI instalando o pacote com o programa aberto,
echo   de dois cliques em simular-instalacao.bat, nesta mesma pasta.
echo.

cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    echo   Ambiente virtual nao encontrado. Abra primeiro o abrir-dev.bat,
    echo   que prepara o ambiente, e depois volte a este.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" abrir\sem_motor.py sem-portugues
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

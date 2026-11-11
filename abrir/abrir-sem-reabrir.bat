@echo off
title Anonimizador CAPCF - modo DEV, sem conseguir reabrir
echo.
echo   Abrindo o Anonimizador CAPCF como se ele NAO conseguisse abrir de novo:
echo   o "Reabrir agora" da tela do Tema vai falhar de proposito, para conferir
echo   a frase do caminho torto. Nada foi bloqueado de verdade.
echo.

cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    echo   Ambiente virtual nao encontrado. Abra primeiro o abrir-dev.bat,
    echo   que prepara o ambiente, e depois volte a este.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" abrir\sem_reabrir.py
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

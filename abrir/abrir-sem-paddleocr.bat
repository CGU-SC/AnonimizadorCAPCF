@echo off
title Anonimizador CAPCF - modo DEV, sem o PaddleOCR
echo.
echo   Abrindo o Anonimizador CAPCF como se a instalacao estivesse SEM os modelos
echo   do PaddleOCR - a instalacao estragada da RN-29. Nada foi apagado: o
echo   programa so finge que os modelos nao estao la. O Tesseract funciona.
echo.

cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    echo   Ambiente virtual nao encontrado. Abra primeiro o abrir-dev.bat,
    echo   que prepara o ambiente, e depois volte a este.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" abrir\sem_motor.py sem-paddleocr
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

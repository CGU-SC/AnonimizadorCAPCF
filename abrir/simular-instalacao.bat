@echo off
title Anonimizador CAPCF - simular a instalacao do motor
echo.
if exist "%~dp0.motor-escondido" (
    del "%~dp0.motor-escondido"
    echo   Pronto: para o programa aberto por um dos atalhos abrir-sem-...,
    echo   o Tesseract agora "foi instalado". Volte ao programa e clique em
    echo   "Conferir de novo".
    echo.
    echo   O PaddleOCR escondido pelo abrir-sem-paddleocr.bat ou pelo
    echo   abrir-sem-nenhum-motor.bat NAO volta: como na vida real, instalacao
    echo   estragada so se resolve reinstalando - aqui, fechando o programa.
) else (
    echo   Nada a fazer: o Tesseract ja nao estava escondido. Esta simulacao
    echo   so vale para o programa aberto por um dos atalhos abrir-sem-...
)
echo.
pause

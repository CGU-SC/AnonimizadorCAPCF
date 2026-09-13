@echo off
title AnomizadorCAPCF - simular a instalacao do motor
echo.
if exist "%~dp0.motor-escondido" (
    del "%~dp0.motor-escondido"
    echo   Pronto: para o programa aberto pelo abrir-sem-motor.bat ou pelo
    echo   abrir-sem-portugues.bat, o motor de leitura agora "foi instalado".
    echo   Volte ao programa e clique em "Conferir de novo".
) else (
    echo   Nada a fazer: o motor ja nao estava escondido. Esta simulacao so
    echo   vale para o programa aberto pelo abrir-sem-motor.bat ou pelo
    echo   abrir-sem-portugues.bat.
)
echo.
pause

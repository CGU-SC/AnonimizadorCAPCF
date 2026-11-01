@echo off
title Servidor de IA de mentira - cai no segundo pedido
echo.
echo   O mesmo servidor de mentira, que responde o teste de ligar e cai no terceiro
echo   pedido, com uma demora de 2 segundos: serve para ver a revisao parar no meio,
echo   cancelar e tentar de novo. Para parar, feche esta janela.
echo.
call "%~dp0servidor-de-ia-de-mentira.bat" --cair-no-pedido 3 --demora 2

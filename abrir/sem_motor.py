"""Abre o programa como se o Tesseract não estivesse pronto nesta máquina.

Só para conferir na tela o aviso do motor faltando (etapa 7 da spec 002) sem
desinstalar nada. O Tesseract continua onde está; o programa é que finge não
encontrá-lo enquanto o arquivo abrir/.motor-escondido existir. Apagar esse
arquivo - é o que o simular-instalacao.bat faz - equivale à TI terminar a
instalação com o programa aberto.

Chamado com "sem-portugues", finge outra coisa: que o Tesseract está
instalado, só que sem o pacote de português.

A pasta apontada pela pessoa continua valendo, porque é justamente uma das
coisas que se quer conferir.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "programa"))

import main  # noqa: E402
import motor  # noqa: E402

MARCA = Path(__file__).resolve().parent / ".motor-escondido"

if "sem-portugues" in sys.argv[1:]:
    _conferir_de_verdade = motor.tem_o_portugues

    def _portugues_so_depois_da_instalacao(executavel):
        return not MARCA.exists() and _conferir_de_verdade(executavel)

    motor.tem_o_portugues = _portugues_so_depois_da_instalacao
else:
    _procurar_de_verdade = motor._onde_procurar_sem_ajuda

    def _procurar_so_depois_da_instalacao():
        if MARCA.exists():
            return iter(())
        return _procurar_de_verdade()

    motor._onde_procurar_sem_ajuda = _procurar_so_depois_da_instalacao

MARCA.write_text(
    "Enquanto este arquivo existir, a simulação esconde o motor de leitura.\n",
    encoding="utf-8",
)
main.main()

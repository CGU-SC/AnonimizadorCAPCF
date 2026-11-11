"""Abre o programa como se ele não conseguisse abrir de novo.

Só para conferir na tela o caminho torto do "Reabrir agora" (RN-24 da spec 001):
o botão é clicado, a cópia nova não abre, e a tela do Tema diz por quê. Nada é
bloqueado de verdade; o programa só finge que o Windows recusou abrir a cópia.
Fechar e abrir pelo atalho de sempre traz o tema novo, como a frase diz.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "programa"))

import main  # noqa: E402

main.abrir_de_novo = lambda tema: False
main.main()

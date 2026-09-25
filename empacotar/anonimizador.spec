# Receita do PyInstaller: como o programa vira uma pasta que roda sem Python.
#
# Gera-se pelo empacotar\gerar-entrega.bat, e nunca à mão: o resultado vai
# para builds\, fora do histórico, e ninguém o edita.
#
# Uma pasta, e não um .exe único (plano de entrega aprovado em 23/09/2026): o
# instalador esconde a pasta de quem usa, e o .exe único se desempacota numa
# pasta temporária a cada vez que abre - 5 a 10 segundos de espera com o Qt
# dentro, e o antivírus costuma desconfiar desse tipo de programa.
import sys
from pathlib import Path

RAIZ = Path(SPECPATH).parent
PROGRAMA = RAIZ / "programa"

sys.path.insert(0, str(PROGRAMA))
from main import NOME_PROGRAMA  # noqa: E402

analise = Analysis(
    [str(PROGRAMA / "main.py")],
    pathex=[str(PROGRAMA)],
    # Só o que o programa importa entra: os testes, a massa de exemplo e o
    # .env ficam de fora por não estarem nesta lista. Nenhum arquivo de dados
    # entra por fora, de propósito - a conferência da pasta gerada confirma.
    datas=[],
    # O pytest está no ambiente de desenvolvimento para os testes, e não tem
    # o que fazer no programa entregue.
    excludes=["pytest", "_pytest", "tkinter"],
    noarchive=False,
)

pacote = PYZ(analise.pure)

executavel = EXE(
    pacote,
    analise.scripts,
    [],
    exclude_binaries=True,
    name=NOME_PROGRAMA,
    # Sem a janela preta de terminal atrás do programa: quem usa não programa,
    # e uma janela de terminal aberta parece erro.
    console=False,
    upx=False,
)

COLLECT(
    executavel,
    analise.binaries,
    analise.datas,
    name=NOME_PROGRAMA,
    upx=False,
)

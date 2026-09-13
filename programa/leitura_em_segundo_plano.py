"""Faz a leitura acontecer sem congelar a janela.

Ler um documento de doze páginas leva quase vinte segundos. Se isso rodasse no
mesmo lugar que desenha a tela, a janela pararia de responder o tempo todo: não
daria para mover, nem minimizar, nem clicar em cancelar - e o Windows ainda
escreveria "Não Responde" na barra de título. Quem vê isso encerra o programa à
força, achando que travou.

Por isso a leitura roda "ao lado", e vai avisando a tela do que está
acontecendo.
"""
from PySide6.QtCore import QThread, Signal

from leitura import (
    LeituraCancelada,
    LeituraFalhou,
    MotorNaoEncontrado,
    ler_documento,
)


class LeituraEmSegundoPlano(QThread):
    avancou = Signal(int, int)      # página atual, total de páginas
    terminou = Signal(list)         # o texto de cada página, em ordem
    cancelou = Signal(int)          # em que página parou
    falhou = Signal(int, str)       # em que página (0 quando a falha não foi
                                    # numa página), e o que dizer na tela

    def __init__(self, caminho):
        super().__init__()
        self._caminho = caminho
        self._pediram_para_cancelar = False

    def cancelar(self):
        """Marca o pedido; quem para de fato é a leitura, na página seguinte.

        Não se interrompe a leitura no meio de uma página: o Tesseract está
        trabalhando naquela imagem, e cortá-lo pela metade é o tipo de coisa que
        deixa o programa num estado que ninguém sabe descrever. A espera é de no
        máximo uma página - cerca de um segundo e meio.
        """
        self._pediram_para_cancelar = True

    def run(self):
        try:
            paginas = ler_documento(
                self._caminho,
                ao_avancar=self.avancou.emit,
                foi_cancelado=lambda: self._pediram_para_cancelar,
            )
        except LeituraCancelada as parada:
            self.cancelou.emit(parada.pagina)
        except LeituraFalhou as problema:
            self.falhou.emit(problema.pagina, str(problema))
        except MotorNaoEncontrado as problema:
            self.falhou.emit(0, str(problema))
        except Exception:
            # Rede caindo, memória acabando, defeito não previsto: seja o que
            # for, a tela precisa sair do estado de espera e ter um botão.
            self.falhou.emit(
                0,
                "A leitura não pôde ser concluída. Nada foi gravado, e o "
                "documento original não foi tocado.",
            )
        else:
            self.terminou.emit(paginas)

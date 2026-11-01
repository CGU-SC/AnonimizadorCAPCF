"""O que fala com a IA roda ao lado da janela, e a janela nunca espera.

Um destino fora do ar leva segundos para dizer isso, e um modelo pode levar minutos
para responder: no mesmo lugar que desenha a tela, a janela ficaria "Não Responde".
"""
from PySide6.QtCore import QThread, Signal

FRASE_GERAL = "A conversa com a IA não pôde ser concluída."


def frase_da_falha(problema):
    """A frase de uma falha conhecida; a de uma desconhecida nunca vai para a tela,
    porque poderia trazer o token ou o texto do documento."""
    return str(problema) if getattr(problema, "para_a_tela", False) else FRASE_GERAL


class _Tarefa(QThread):
    pronto = Signal(object)
    falhou = Signal(str)

    def __init__(self, funcao):
        super().__init__()
        self._funcao = funcao

    def run(self):
        try:
            resultado = self._funcao()
        except Exception as problema:
            # Cancelar ao fechar o programa não é falha do destino: tratado como falha,
            # o teste cortado desligaria a IA para a próxima abertura.
            if not getattr(problema, "e_cancelamento", False):
                self.falhou.emit(frase_da_falha(problema))
        else:
            self.pronto.emit(resultado)


def rodar(dono, funcao, ao_pronto, ao_falhar):
    """Roda ao lado, e chama de volta na janela. `dono` guarda a tarefa enquanto
    ela roda: sem isso o Python a recolheria no meio, e o programa estouraria."""
    tarefas = dono.__dict__.setdefault("_tarefas_da_ia", [])
    tarefa = _Tarefa(funcao)
    tarefas.append(tarefa)
    tarefa.pronto.connect(ao_pronto)
    tarefa.falhou.connect(ao_falhar)
    tarefa.finished.connect(lambda: tarefas.remove(tarefa))
    tarefa.start()


def esperar_terminar(dono, milissegundos=8000):
    """Espera as tarefas antes de fechar, porque trabalho que sobra ao lado da
    janela fechada faz o programa estourar ("O que já nos mordeu")."""
    for tarefa in list(dono.__dict__.get("_tarefas_da_ia", [])):
        tarefa.wait(milissegundos)

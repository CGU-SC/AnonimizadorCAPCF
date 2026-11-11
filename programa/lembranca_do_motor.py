"""O motor que cada módulo lembra de um uso para o outro (RN-36 da spec 002).

Morava dentro da peça da tela que mostra os motores, e ali cada motor novo teria
que repetir a mesma ligação. Tirada para cá antes de a IA local entrar como
terceiro motor (revisões 43 e 44, `CLAUDE.md`). A tela diz o que foi marcado, e
quem sabe guardar é esta peça.
"""
import preferencias


class LembrancaDoMotor:
    """A lembrança de um módulo, com o nome do bloco dele no `preferencias.ini`."""

    def __init__(self, modulo):
        self._modulo = modulo

    def motor(self):
        """O motor lembrado, ou None quando não há nada lembrado que dê para ler."""
        return preferencias.ler(self._modulo, "motor")

    def lembrar(self, motor):
        preferencias.gravar(self._modulo, "motor", motor)

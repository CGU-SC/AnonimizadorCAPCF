"""Um servidor de IA de mentira, nesta máquina, para testar e conferir sem modelo.

Fala do mesmo jeito que o LM Studio e não pensa nada: lista dois modelos inventados
e aponta o que está escrito nas regras abaixo. Não faz parte do programa, e o
instalador não o leva. Escuta só na própria máquina.

    python abrir/servidor_de_ia_de_mentira.py --porta 1234
"""
import argparse
import json
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODELOS_PADRAO = [
    {"type": "llm", "key": "modelo-exemplo-texto-8b", "display_name": "Texto",
     "size_bytes": 5476083302, "max_context_length": 8192,
     "capabilities": {"vision": False}, "loaded_instances": [{"id": "a"}]},
    {"type": "llm", "key": "modelo-exemplo-visao-13b", "display_name": "Visão",
     "size_bytes": 8589934592, "max_context_length": 8192,
     "capabilities": {"vision": True}, "loaded_instances": []},
    {"type": "embedding", "key": "modelo-exemplo-busca", "display_name": "Busca"},
]


def apontar(texto):
    """As regras da mentira: o bastante para a revisão ter o que mostrar."""
    apontamentos = []
    for achado in re.finditer(r"Inscrição do bolsista:\s*(\S+)", texto):
        apontamentos.append({
            "tipo": "numero", "citacao": achado.group(1),
            "motivo": '"Inscrição do bolsista" costuma ser um CPF, e aqui está em '
                      "grupos estranhos."})
    for achado in re.finditer(r"Termo de outorga nº\s*(\S+)", texto):
        apontamentos.append({
            "tipo": "numero", "citacao": achado.group(1), "parece_cpf": False,
            "motivo": "Parece o número de um termo, e não um CPF."})
    for achado in re.finditer(r"\b[A-Za-z]+[0-9][A-Za-z0-9]*\b.{0,30}", texto):
        trecho = achado.group(0).strip()
        if sum(c.isalpha() for c in trecho) > 6:
            apontamentos.append({
                "tipo": "trecho", "citacao": trecho,
                "motivo": "Há números no lugar de letras: a leitura desta parte "
                          "parece frágil."})
    return {"apontamentos": apontamentos}


class Comportamento:
    """O que o servidor faz, mudado à vontade pelos testes."""

    def __init__(self):
        self.modelos = MODELOS_PADRAO
        self.so_lista_comum = False
        self.sem_lista = False
        self.token = None
        self.cair_no_pedido = None
        self.resposta_estranha_no_pedido = None
        self.redirecionar = False
        self.demora = 0
        self.resposta = None
        self.pedidos = []
        self.pedidos_de_conversa = 0
        self.corpo_cru = []


def _criar_tratador(comportamento):
    class Tratador(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *_):
            pass

        def _responder(self, estado, corpo, cabecalhos=None):
            dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
            self.send_response(estado)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(dados)))
            for chave, valor in (cabecalhos or {}).items():
                self.send_header(chave, valor)
            self.end_headers()
            self.wfile.write(dados)

        def _autorizado(self):
            if comportamento.token is None:
                return True
            return self.headers.get("Authorization") == f"Bearer {comportamento.token}"

        def do_GET(self):
            comportamento.pedidos.append(("GET", self.path))
            if not self._autorizado():
                self._responder(401, {"error": "token recusado"})
            elif comportamento.redirecionar:
                self._responder(302, {}, {"Location": "http://127.0.0.1:9/outro"})
            elif comportamento.sem_lista:
                self._responder(404, {"error": "nao ha"})
            elif self.path == "/api/v1/models" and not comportamento.so_lista_comum:
                self._responder(200, {"models": comportamento.modelos})
            elif self.path == "/v1/models":
                self._responder(200, {"data": [{"id": m["key"]}
                                               for m in comportamento.modelos]})
            else:
                self._responder(404, {"error": "nao ha"})

        def do_POST(self):
            comportamento.pedidos.append(("POST", self.path))
            tamanho = int(self.headers.get("Content-Length", 0))
            cru = self.rfile.read(tamanho).decode("utf-8")
            comportamento.corpo_cru.append(cru)
            if not self._autorizado():
                self._responder(401, {"error": "token recusado"})
                return
            if comportamento.redirecionar:
                self._responder(307, {}, {"Location": "http://127.0.0.1:9/outro"})
                return
            corpo = json.loads(cru)
            comportamento.pedidos_de_conversa += 1
            numero = comportamento.pedidos_de_conversa
            time.sleep(comportamento.demora)
            if numero == comportamento.cair_no_pedido:
                self._responder(500, {"error": "caiu"})
                return
            conteudo = corpo["messages"][-1]["content"]
            if isinstance(conteudo, list):
                texto = "Texto lido pela IA de mentira.\nCPF 111.111.111-11"
            elif "Responda apenas" in conteudo:
                texto = "ok"
            elif numero == comportamento.resposta_estranha_no_pedido:
                texto = "isto nao e o que foi pedido"
            elif comportamento.resposta is not None:
                texto = comportamento.resposta
            else:
                texto = json.dumps(apontar(conteudo), ensure_ascii=False)
            self._responder(200, {"choices": [{"message": {"content": texto}}]})

    return Tratador


class ServidorDeMentira:
    """Sobe numa porta livre da própria máquina, numa linha à parte."""

    def __init__(self, porta=0):
        self.comportamento = Comportamento()
        self._parado = False
        self._servidor = ThreadingHTTPServer(
            ("127.0.0.1", porta), _criar_tratador(self.comportamento))
        self._servidor.daemon_threads = True
        self.porta = self._servidor.server_address[1]
        self.base = f"http://127.0.0.1:{self.porta}"
        threading.Thread(target=self._servidor.serve_forever, daemon=True).start()

    def parar(self):
        """Pode ser chamado duas vezes: um teste que derruba o servidor no meio e o fim
        do teste, que sempre derruba."""
        if self._parado:
            return
        self._parado = True
        self._servidor.shutdown()
        self._servidor.server_close()


def main():
    leitor = argparse.ArgumentParser(description=__doc__)
    leitor.add_argument("--porta", type=int, default=1234)
    leitor.add_argument("--cair-no-pedido", type=int)
    leitor.add_argument("--demora", type=float, default=0)
    leitor.add_argument("--sem-lista", action="store_true")
    leitor.add_argument("--token")
    argumentos = leitor.parse_args()
    servidor = ServidorDeMentira(argumentos.porta)
    servidor.comportamento.cair_no_pedido = argumentos.cair_no_pedido
    servidor.comportamento.demora = argumentos.demora
    servidor.comportamento.sem_lista = argumentos.sem_lista
    servidor.comportamento.token = argumentos.token
    print(f"Servidor de mentira no ar: {servidor.base}. Feche esta janela para parar.")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()

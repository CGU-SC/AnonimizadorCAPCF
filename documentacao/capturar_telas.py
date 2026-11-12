"""Tira as prints da documentação de manutenção do programa de verdade.

Abre a janela do programa, leva cada tela ao estado que a documentação mostra,
com os documentos inventados de `dados-exemplo/`, e grava a imagem em
`documentacao/fonte/imagens/`. A cada versão nova, rodar de novo deixa as prints
iguais à tela de hoje, sem ninguém precisar clicar e recortar à mão:

    .\\.venv\\Scripts\\python.exe documentacao\\capturar_telas.py

A janela aparece e some algumas vezes enquanto ele roda: o Qt precisa subir no
modo normal, com a tela, porque no modo "sem tela" ele não enxerga as fontes do
Windows e cada letra sai como um quadradinho preto.

Nada desta máquina é lido nem gravado: as escolhas lembradas e o `.env` vão
para uma pasta provisória em `builds/`, que fica fora do histórico.
"""
import sys
import time
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "programa"))

from PySide6.QtCore import QSize, Qt  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402
from PySide6.QtWidgets import QApplication, QPushButton  # noqa: E402

import configuracao  # noqa: E402
import estilo  # noqa: E402
import preferencias  # noqa: E402

MASSA = RAIZ / "dados-exemplo"
DESTINO = RAIZ / "documentacao" / "fonte" / "imagens"
PROVISORIA = RAIZ / "builds" / "capturas"

# A largura das prints que já estão nos roteiros da entrega: com ela, a tela
# cabe na largura da página sem encolher a letra até ficar ilegível.
TAMANHO_DA_JANELA = QSize(1200, 760)


def isolar_esta_maquina():
    """Aponta o `preferencias.ini` e o `.env` para a pasta provisória.

    Sem isto, a captura gravaria o motor marcado e o tamanho da janela no
    `preferencias.ini` de quem roda, e leria o token do `.env` dele.
    """
    PROVISORIA.mkdir(parents=True, exist_ok=True)
    for sobra in PROVISORIA.iterdir():
        sobra.unlink()
    preferencias.caminho = lambda: PROVISORIA / "preferencias.ini"
    configuracao.caminho_do_env = lambda: PROVISORIA / ".env"


def esperar(condicao, segundos=90):
    """Deixa o programa trabalhar até a condição valer, ou desiste com erro.

    A leitura do OCR roda ao lado da janela: sem dar a vez ao Qt, ela nunca
    andaria, e a print sairia da tela de antes.
    """
    limite = time.monotonic() + segundos
    while not condicao():
        if time.monotonic() > limite:
            raise TimeoutError("a tela esperada não apareceu")
        QApplication.processEvents()
        time.sleep(0.05)
    # Uma última volta, para a tela terminar de se desenhar.
    for _ in range(10):
        QApplication.processEvents()
        time.sleep(0.02)


def botao_visivel(raiz, comeco):
    """O botão visível e ligado cujo texto começa assim, ou None."""
    for botao in raiz.findChildren(QPushButton):
        if botao.isVisible() and botao.isEnabled() and botao.text().startswith(comeco):
            return botao
    return None


def em_256_cores(imagem):
    """A imagem com as 256 cores que mais aparecem nela.

    Sem a lista de cores, o Qt reduz para uma tabela fixa, e o fundo #1e2228 da
    janela virava um cinza #333333: as prints saíam sem o tom do programa, e a
    borda dos botões, de um tom vizinho do fundo, sumia. Numa tela de programa,
    as cores que mais aparecem são as do sistema de design, e o resto é a borda
    suavizada das letras, que vai para a cor mais próxima.
    """
    imagem = imagem.convertToFormat(QImage.Format_RGB32)
    pontos = memoryview(imagem.constBits()).cast("I")
    mais_comuns = [cor for cor, _ in Counter(pontos).most_common(256)]
    return imagem.convertToFormat(QImage.Format_Indexed8, mais_comuns,
                                  Qt.ThresholdDither | Qt.AvoidDither)


def gravar(janela, nome):
    """Grava a janela como PNG de 256 cores, o formato das prints dos roteiros.

    256 cores bastam para uma tela de programa, e deixam o arquivo umas três
    vezes menor - o que pesa, porque a imagem vai dentro do HTML.
    """
    imagem = janela.grab().toImage()
    if imagem.width() > TAMANHO_DA_JANELA.width():
        # Com a escala do Windows acima de 100%, a captura sai maior que a janela.
        imagem = imagem.scaledToWidth(TAMANHO_DA_JANELA.width(), Qt.SmoothTransformation)
    imagem = em_256_cores(imagem)
    DESTINO.mkdir(parents=True, exist_ok=True)
    arquivo = DESTINO / f"{nome}.png"
    imagem.save(str(arquivo))
    print(f"  {arquivo.relative_to(RAIZ)}  ({arquivo.stat().st_size // 1024} KB)")


def nova_janela():
    import main
    janela = main.JanelaPrincipal()
    janela.setMinimumSize(TAMANHO_DA_JANELA)
    janela.resize(TAMANHO_DA_JANELA)
    janela.show()
    esperar(janela.isVisible)
    return janela


def capturar_com_os_motores(janela):
    gravar(janela, "janela-ao-abrir")

    # O Gerar OCR com um PDF sem texto, lido pelo PaddleOCR, até a conferência.
    janela.menu.botao_ocr.click()
    # O 02 é o "Imprimir para PDF": nenhum texto por dentro, e por isso o caminho
    # vai direto à leitura. O cartão do que o programa descobriu vem antes.
    janela.painel_ocr.receber_documento(MASSA / "02-imprimir-para-pdf.pdf")
    esperar(lambda: botao_visivel(janela.painel_ocr, "Ler") is not None)
    gravar(janela, "gerar-ocr-antes-de-ler")
    botao_visivel(janela.painel_ocr, "Ler").click()
    # Do cartão, o "Ler" leva à escolha do motor, que tem o próprio "Ler".
    esperar(lambda: True)
    segundo = botao_visivel(janela.painel_ocr, "Ler")
    if segundo is not None:
        segundo.click()
    from tela_conferencia import TelaConferencia
    esperar(lambda: any(t.isVisible() for t in janela.painel_ocr.findChildren(TelaConferencia)))
    gravar(janela, "gerar-ocr-conferencia")

    # O Anonimizar com o documento do Word: a revisão e a faixa do que ficou de fora.
    janela.menu.botao_anonimizar.click()
    janela.painel_anonimizar.receber_arquivo(MASSA / "18-documento-do-word.docx")
    from tela_revisao import TelaRevisao
    esperar(lambda: any(t.isVisible() for t in janela.painel_anonimizar.findChildren(TelaRevisao)))
    gravar(janela, "anonimizar-word")

    # As Configurações entram pelo Tema. A revisão aberta faz o programa
    # perguntar antes de sair dela; esquecida, ele vai direto.
    janela.painel_anonimizar.tela_revisao.esquecer()
    janela.painel_anonimizar._salvo = True
    janela.menu.botao_config_ia.click()
    esperar(lambda: janela.painel.currentWidget() is janela.painel_ia)
    gravar(janela, "configuracoes-tema")


def capturar_sem_os_motores():
    """Os dois motores escondidos: o único caso do aviso no alto (RN-29 e RN-30
    da spec 002). Do mesmo jeito que o `abrir/sem_motor.py` finge."""
    import motor
    import motor_paddleocr
    motor._onde_procurar_sem_ajuda = lambda: iter(())
    motor_paddleocr.presente = lambda: False
    janela = nova_janela()
    janela.menu.botao_ocr.click()
    esperar(lambda: janela.painel.currentWidget() is janela.painel_ocr)
    gravar(janela, "motor-faltando")
    return janela


def main():
    aplicacao = QApplication(sys.argv)
    isolar_esta_maquina()
    # O escuro, o tema de sempre: a documentação mostra o programa como ele abre.
    estilo.usar_tema(estilo.ESCURO)
    print("Gravando as prints:")
    janela = nova_janela()
    capturar_com_os_motores(janela)
    janela.close()
    capturar_sem_os_motores().close()
    aplicacao.processEvents()


if __name__ == "__main__":
    main()

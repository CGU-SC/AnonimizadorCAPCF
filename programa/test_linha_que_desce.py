"""Testes da fileira que desce para a linha de baixo quando não cabe."""
from PySide6.QtWidgets import QLabel, QWidget

from linha_que_desce import LinhaQueDesce


def _fileira(textos):
    dono = QWidget()
    fileira = LinhaQueDesce(espaco=8)
    dono.setLayout(fileira)
    rotulos = [QLabel(t) for t in textos]
    for rotulo in rotulos:
        fileira.addWidget(rotulo)
    return dono, fileira, rotulos


def test_a_peca_que_nao_cabe_desce_inteira_em_vez_de_ser_espremida(aplicacao):
    """É a razão de existir dela: as fileiras do Qt cortam o texto, calado."""
    dono, fileira, rotulos = _fileira(["um selo comprido", "outro selo comprido"])
    largura_de_um = max(r.sizeHint().width() for r in rotulos)

    fileira.setGeometry(dono.rect().adjusted(0, 0, largura_de_um - dono.width(), 0))

    for rotulo in rotulos:
        assert rotulo.width() == rotulo.sizeHint().width()
    assert rotulos[1].y() > rotulos[0].y()
    assert fileira.heightForWidth(largura_de_um) > fileira.heightForWidth(10_000)


def test_peca_escondida_nao_deixa_buraco(aplicacao):
    """O selo de um grupo sem números some de vez da fileira."""
    dono, fileira, rotulos = _fileira(["primeiro", "escondido", "terceiro"])
    rotulos[1].setVisible(False)

    fileira.setGeometry(dono.rect().adjusted(0, 0, 10_000 - dono.width(), 0))

    esperado = rotulos[0].x() + rotulos[0].sizeHint().width() + 8
    assert rotulos[2].x() == esperado

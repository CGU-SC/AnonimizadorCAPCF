"""O painel de Configurações de IA: três telas, uma por item do submenu.

Segue o rascunho aprovado mockups/ia/01-configuracoes-de-ia.html.

O arquivo que fala com a rede só é carregado quando a pessoa aciona algo aqui: sem
ninguém mexer nestas telas, o programa nem o abre (RN-43 da spec 004).
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import avisos_da_ia
import config_ia
import estilo
import trabalho_da_ia
from pecas_da_ia import (
    LARGURA_DO_CONTEUDO,
    Faixa,
    Frase,
    Interruptor,
    campo_de_texto,
    linha_do_switch,
    rotulo_de_campo,
    titulo_de_tela,
)

LM_STUDIO = config_ia.LM_STUDIO
SERVIDOR = config_ia.SERVIDOR
HABILITAR = "habilitar"

RESPONDENDO = "Respondendo agora. Isso diz que o modelo respondeu, e não como ele revisa."
ESCOLHA_UM_MODELO = "Respondendo agora. Escolha um modelo."
NENHUM_MODELO = ("O destino respondeu, mas não tem nenhum modelo para oferecer. "
                 "Instale um modelo e ligue este switch de novo.")
# A data é parte da frase: modelo local melhora, e o programa não tem como saber
# disso. Escrita como avaliação de quem fez o programa, porque o que está medido é o
# Tesseract contra o PaddleOCR (conferência 02).
RESSALVA_DO_MOTOR = (
    "Ressalva, de 31/10/2026. Até a criação deste programa, os modelos de IA locais "
    "eram muito inferiores ao PaddleOCR e ao Tesseract na leitura. O uso indicado da IA "
    "é como revisora. Como motor, a IA recebe a imagem da página com os CPFs inteiros, "
    "e o texto do documento passa a ser o que ela escrever."
)
TESTANDO = "Testando a conexão... O teste manda uma frase inventada, sem nada do documento."


def _rede():
    """Só aqui o arquivo da rede é carregado, e só quando há o que fazer com ele."""
    import rede_da_ia
    return rede_da_ia


def _recuado(peca, recuo):
    fora = QWidget()
    linha = QHBoxLayout(fora)
    linha.setContentsMargins(recuo, 0, 0, 0)
    linha.setSpacing(0)
    linha.addWidget(peca)
    linha.addStretch()
    return fora


def _rolavel(tela):
    """Rola só na vertical: rolando para o lado, a primeira letra de tudo fica
    cortada, sem nada acusar ("O que já nos mordeu")."""
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setFrameShape(QFrame.NoFrame)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    area.setWidget(tela)
    return area


def _seletor():
    seletor = QComboBox()
    seletor.setFixedWidth(LARGURA_DO_CONTEUDO)
    seletor.setStyleSheet(
        f"""
        QComboBox, QComboBox QAbstractItemView {{
            background-color: {estilo.COR_FUNDO_ELEVADO};
            border: 1px solid {estilo.COR_BORDA};
            border-radius: {estilo.RAIO}px;
            padding: 6px 10px;
            color: {estilo.COR_TEXTO};
            font-size: {estilo.TEXTO_PEQUENO}px;
        }}
        """
    )
    return seletor


def _botao_pequeno(texto, ao_clicar, principal=False):
    botao = QPushButton(texto)
    botao.setCursor(Qt.PointingHandCursor)
    botao.setStyleSheet(estilo.estilo_botao(principal=principal, pequeno=True))
    botao.clicked.connect(lambda _=False: ao_clicar())
    return botao


class _TelaBasica(QWidget):
    def __init__(self, titulo, legenda):
        super().__init__()
        self.corpo = QVBoxLayout(self)
        self.corpo.setContentsMargins(0, 0, 0, 0)
        self.corpo.setSpacing(estilo.ESPACO_3)
        self.corpo.addWidget(titulo_de_tela(titulo))
        self.legenda = Frase(legenda)
        self.corpo.addWidget(self.legenda)


class _TelaDoDestino(_TelaBasica):
    """O que as telas do LM Studio e do servidor têm em comum.

    Ligar o switch testa, e só um teste que passou faz o destino contar como
    configurado (RN-6). Se falhar, o switch volta para desligado, e o que a pessoa
    escolheu fica guardado.
    """

    nome = None
    rotulo_do_switch = ""
    FRASE_DE_FALHA = ""

    def __init__(self, titulo, legenda, ao_mudar):
        super().__init__(titulo, legenda)
        self._ao_mudar = ao_mudar
        self._cancelador = None
        # None: ainda não perguntou. O destino que não sabe listar pede o nome digitado.
        self._lista_conhecida = False
        self._sem_lista = False
        # Ligando por cima do outro destino: ele só desliga depois do teste, para a
        # falha não deixar a pessoa sem nenhum dos dois.
        self.interruptor = Interruptor()
        self.interruptor.clicked.connect(self._switch_clicado)
        self.corpo.addWidget(linha_do_switch(self.interruptor, self.rotulo_do_switch))
        self.situacao = Frase()
        self.corpo.addWidget(self.situacao)
        self.faixa_erro = Faixa("erro")
        self.faixa_erro.setVisible(False)
        self.corpo.addWidget(self.faixa_erro)
        self._montar_campos()

        self.rotulo_revisora = rotulo_de_campo("Modelo da revisora")
        self.seletor_revisora = _seletor()
        self.seletor_revisora.activated.connect(lambda _: self._escolheu_revisora())
        self.campo_revisora = campo_de_texto()
        self.campo_revisora.setPlaceholderText("O nome do modelo, que a TI informa")
        self.campo_revisora.editingFinished.connect(self._digitou_revisora)
        self.rotulo_motor = rotulo_de_campo("Modelo do motor de leitura (só os que leem imagem)")
        self.seletor_motor = _seletor()
        self.seletor_motor.activated.connect(lambda _: self._escolheu_motor())
        self.campo_motor = campo_de_texto()
        self.campo_motor.setPlaceholderText("O nome do modelo, que a TI informa")
        self.campo_motor.editingFinished.connect(self._digitou_motor)
        self.botao_testar = QPushButton("Testar de novo")
        self.botao_testar.setCursor(Qt.PointingHandCursor)
        self.botao_testar.setStyleSheet(estilo.estilo_botao(principal=False, pequeno=True))
        self.botao_testar.clicked.connect(self._testar_de_novo)
        for peca in (self.rotulo_revisora, self.seletor_revisora, self.campo_revisora,
                     self.rotulo_motor, self.seletor_motor, self.campo_motor):
            self.corpo.addWidget(peca)
        linha = QHBoxLayout()
        linha.addWidget(self.botao_testar)
        linha.addStretch()
        self.corpo.addLayout(linha)
        self.corpo.addStretch()
        self.atualizar()

    def _montar_campos(self):
        """Os campos próprios de cada destino, entre a situação e os modelos."""

    def base(self):
        raise NotImplementedError

    def pode_ligar(self):
        return True

    def _token(self):
        return config_ia.token_do_destino(self.nome)

    def esta_ligado(self):
        return config_ia.destino_ligado() == self.nome

    def atualizar(self):
        """Põe a tela de acordo com o que está guardado."""
        ligado = self.esta_ligado()
        self.interruptor.setChecked(ligado)
        self.interruptor.setEnabled(self.pode_ligar())
        self.situacao.setText(self._frase_da_situacao() if ligado else "")
        self._mostrar_modelos(ligado)

    def _frase_da_situacao(self):
        if config_ia.testado(self.nome) and config_ia.modelo_da_revisora(self.nome):
            return RESPONDENDO
        return ESCOLHA_UM_MODELO

    def _mostrar_modelos(self, ligado):
        tem_lista = self.seletor_revisora.count() > 0
        digita = ligado and self._sem_lista
        self.rotulo_revisora.setVisible(ligado)
        self.seletor_revisora.setVisible(ligado and tem_lista)
        self.campo_revisora.setVisible(digita)
        com_motor = ligado and config_ia.motor_marcado()
        self.rotulo_motor.setVisible(com_motor)
        self.seletor_motor.setVisible(com_motor and tem_lista)
        self.campo_motor.setVisible(com_motor and self._sem_lista)
        self.botao_testar.setVisible(ligado)
        if digita:
            self.campo_revisora.setText(config_ia.modelo_da_revisora(self.nome))
            self.campo_motor.setText(config_ia.modelo_do_motor(self.nome))

    def _ocupado(self, ocupado):
        for peca in (self.interruptor, self.seletor_revisora, self.seletor_motor,
                     self.campo_revisora, self.campo_motor, self.botao_testar):
            peca.setEnabled(not ocupado)
        if ocupado:
            self.situacao.setText(TESTANDO)
            self.faixa_erro.setVisible(False)
        else:
            self.interruptor.setEnabled(self.pode_ligar())

    # ---------------------------------------------------------- ligar e desligar

    def _switch_clicado(self, ligado):
        if ligado:
            self._ligar()
        else:
            config_ia.desligar_destino()
            self.faixa_erro.setVisible(False)
            self.atualizar()
            self._ao_mudar()

    def _ligar(self):
        outro = config_ia.destino_ligado()
        if outro and outro != self.nome and not avisos_da_ia.confirmar_troca_de_destino(outro, self):
            self.interruptor.setChecked(False)
            return
        self._listar_e_testar()

    def _listar_e_testar(self):
        self._ocupado(True)
        self._cancelador = _rede().Cancelador()
        base, token, cancelador = self.base(), self._token(), self._cancelador
        trabalho_da_ia.rodar(
            self, lambda: _rede().listar_modelos(base, token, cancelador),
            self._chegou_a_lista, self._falhou_ao_ligar)

    def _testar_de_novo(self):
        self._listar_e_testar()

    def _chegou_a_lista(self, modelos):
        self._ocupado(False)
        config_ia.ligar_destino(self.nome)
        if modelos == []:
            self._desligar_com_falha(NENHUM_MODELO)
            return
        self._sem_lista = modelos is None
        self._lista_conhecida = True
        self._encher_seletores(modelos or [])
        self.atualizar()
        self._ao_mudar()
        self._testar_o_que_esta_escolhido()

    def _encher_seletores(self, modelos):
        self.seletor_revisora.clear()
        self.seletor_motor.clear()
        if not modelos:
            return
        self.seletor_revisora.addItem("Escolha um modelo", "")
        self.seletor_motor.addItem("Escolha um modelo", "")
        # O destino que não diz quais leem imagem oferece todos, e o teste com imagem
        # decide (RN-40).
        para_o_motor = [m for m in modelos if m.le_imagem is not False]
        for modelo in modelos:
            self.seletor_revisora.addItem(modelo.descricao(), modelo.nome)
        for modelo in para_o_motor:
            self.seletor_motor.addItem(modelo.descricao(), modelo.nome)
        for seletor, guardado in ((self.seletor_revisora, config_ia.modelo_da_revisora(self.nome)),
                                  (self.seletor_motor, config_ia.modelo_do_motor(self.nome))):
            indice = seletor.findData(guardado) if guardado else 0
            seletor.setCurrentIndex(max(indice, 0))

    def _testar_o_que_esta_escolhido(self):
        modelo = config_ia.modelo_da_revisora(self.nome)
        if not modelo:
            config_ia.marcar_testado(self.nome, False)
            self.atualizar()
            self._ao_mudar()
            return
        if self.seletor_revisora.count() and self.seletor_revisora.findData(modelo) < 0:
            # O modelo guardado não existe mais naquele destino.
            config_ia.marcar_testado(self.nome, False)
            self.atualizar()
            self._ao_mudar()
            return
        self._testar_modelo(modelo)

    def _testar_modelo(self, modelo):
        self._ocupado(True)
        self._cancelador = _rede().Cancelador()
        base, token, cancelador = self.base(), self._token(), self._cancelador
        trabalho_da_ia.rodar(
            self, lambda: _rede().testar_modelo(base, token, modelo, cancelador=cancelador),
            self._modelo_respondeu, self._falhou_ao_ligar)

    def _modelo_respondeu(self, _resultado):
        self._ocupado(False)
        config_ia.marcar_testado(self.nome, True)
        self.atualizar()
        self._ao_mudar()
        self._testar_o_motor_escolhido()

    def _falhou_ao_ligar(self, frase):
        self._ocupado(False)
        self._desligar_com_falha(f"{frase} {self.FRASE_DE_FALHA}")

    def _desligar_com_falha(self, frase):
        """O switch volta para desligado, com o que fazer, e as escolhas ficam (RN-6)."""
        config_ia.marcar_testado(self.nome, False)
        if self.esta_ligado():
            config_ia.desligar_destino()
        self.atualizar()
        self._ao_mudar()
        self.faixa_erro.mostrar(frase)

    # -------------------------------------------------------------- os modelos

    def _escolheu_revisora(self):
        modelo = self.seletor_revisora.currentData() or ""
        self._modelo_da_revisora_mudou(modelo)

    def _digitou_revisora(self):
        modelo = " ".join(self.campo_revisora.text().split())
        if modelo != config_ia.modelo_da_revisora(self.nome):
            self._modelo_da_revisora_mudou(modelo)

    def _modelo_da_revisora_mudou(self, modelo):
        config_ia.guardar_do_destino(self.nome, modelo_revisora=modelo)
        config_ia.marcar_testado(self.nome, False)
        if modelo:
            self._testar_modelo(modelo)
        else:
            self.atualizar()
            self._ao_mudar()

    def _escolheu_motor(self):
        self._modelo_do_motor_mudou(self.seletor_motor.currentData() or "")

    def _digitou_motor(self):
        modelo = " ".join(self.campo_motor.text().split())
        if modelo != config_ia.modelo_do_motor(self.nome):
            self._modelo_do_motor_mudou(modelo)

    def _modelo_do_motor_mudou(self, modelo):
        config_ia.guardar_do_destino(self.nome, modelo_motor=modelo)
        config_ia.marcar_motor_testado(self.nome, False)
        self._testar_o_motor_escolhido()

    def _testar_o_motor_escolhido(self):
        """Com o motor ligado, o modelo dele é testado com uma imagem inventada."""
        modelo = config_ia.modelo_do_motor(self.nome)
        if not modelo or not config_ia.motor_marcado():
            self._ao_mudar()
            return
        self._ocupado(True)
        self._cancelador = _rede().Cancelador()
        base, token, cancelador = self.base(), self._token(), self._cancelador
        imagem = _rede().imagem_de_teste()
        trabalho_da_ia.rodar(
            self,
            lambda: _rede().testar_modelo(base, token, modelo, imagem, cancelador),
            self._motor_respondeu, self._motor_falhou)

    def _motor_respondeu(self, _resultado):
        self._ocupado(False)
        config_ia.marcar_motor_testado(self.nome, True)
        self.atualizar()
        self._ao_mudar()

    def _motor_falhou(self, frase):
        # O destino continua valendo para a revisora: só este modelo não lê imagem.
        self._ocupado(False)
        config_ia.marcar_motor_testado(self.nome, False)
        self.atualizar()
        self._ao_mudar()
        self.faixa_erro.mostrar(f"O modelo do motor não leu a imagem de teste. {frase}")

    def showEvent(self, evento):
        """Abrindo a tela com o destino já ligado, busca a lista de modelos.

        Só aqui, e não ao abrir o programa: quem não entra nesta tela não abre
        conexão nenhuma (RN-8). Sem resposta, nada desliga: a falha só desliga no
        teste, e aqui a pessoa só veio olhar.
        """
        super().showEvent(evento)
        if self.esta_ligado() and not self._lista_conhecida:
            self._lista_conhecida = True
            base, token = self.base(), self._token()
            trabalho_da_ia.rodar(self, lambda: _rede().listar_modelos(base, token),
                                 self._lista_ao_abrir, self._sem_lista_ao_abrir)

    def _lista_ao_abrir(self, modelos):
        self._sem_lista = modelos is None
        self._encher_seletores(modelos or [])
        self.atualizar()

    def _sem_lista_ao_abrir(self, frase):
        self._lista_conhecida = False
        self.situacao.setText(f"{frase} Clique em \"Testar de novo\" para conferir.")

    def encerrar(self):
        """Corta o teste em andamento antes de o programa fechar: sem isso, a janela
        esperaria a resposta do modelo para fechar."""
        if self._cancelador is not None:
            self._cancelador.cancelar()
        trabalho_da_ia.esperar_terminar(self)


class _TelaLmStudio(_TelaDoDestino):
    nome = LM_STUDIO
    rotulo_do_switch = "Habilitar LM Studio"
    FRASE_DE_FALHA = ("Abra o LM Studio, carregue um modelo e ligue o servidor local, "
                      "e ligue este switch de novo. A porta e o modelo ficaram guardados.")

    def __init__(self, ao_mudar):
        super().__init__("LM Studio", "A IA roda nesta máquina, e o documento não sai dela.",
                         ao_mudar)

    def _montar_campos(self):
        self.antes_de_ligar = Faixa("info")
        self.antes_de_ligar.mostrar(
            "Antes de ligar: abra o LM Studio, carregue um modelo e ligue o servidor "
            "local dele.")
        self.corpo.addWidget(self.antes_de_ligar)
        self.corpo.addWidget(rotulo_de_campo("Porta"))
        self.campo_porta = campo_de_texto(140)
        self.campo_porta.setText(str(config_ia.porta_do_lm_studio()))
        self.campo_porta.editingFinished.connect(self._porta_mudou)
        self.corpo.addWidget(self.campo_porta)

    def _porta_mudou(self):
        texto = self.campo_porta.text().strip()
        if texto.isdigit() and 0 < int(texto) < 65536:
            if int(texto) != config_ia.porta_do_lm_studio():
                config_ia.guardar_do_destino(LM_STUDIO, porta=int(texto))
                # Com a porta nova, o teste que passou não vale mais.
                config_ia.marcar_testado(LM_STUDIO, False)
                if self.esta_ligado():
                    config_ia.desligar_destino()
                self.atualizar()
                self._ao_mudar()
        else:
            self.campo_porta.setText(str(config_ia.porta_do_lm_studio()))

    def base(self):
        return _rede().base_do_lm_studio(config_ia.porta_do_lm_studio())

    def atualizar(self):
        super().atualizar()
        self.antes_de_ligar.setVisible(not self.esta_ligado())


class _TelaServidor(_TelaDoDestino):
    nome = SERVIDOR
    rotulo_do_switch = "Habilitar Servidor de IA Interno"
    FRASE_DE_FALHA = ("Confira o endereço, ou veja com a TI se ele está no ar. O "
                      "endereço e o token ficaram guardados.")

    def __init__(self, ao_mudar):
        super().__init__(
            "Servidor de IA Interno",
            "A IA roda num servidor da instituição. O texto do documento viaja até "
            "lá, com os CPFs inteiros.", ao_mudar)

    def _montar_campos(self):
        self.frase_salve = Frase("Salve o endereço para poder ligar.")
        self.corpo.addWidget(self.frase_salve)
        self.corpo.addWidget(rotulo_de_campo("Endereço, que a TI informa"))
        self.campo_endereco = campo_de_texto()
        self.campo_endereco.setText(config_ia.endereco_do_servidor())
        self.corpo.addWidget(self.campo_endereco)
        self.por_que = Frase()
        self.corpo.addWidget(self.por_que)

        self.corpo.addWidget(rotulo_de_campo(
            "Token, que a TI informa (deixe em branco se o servidor não pedir)"))
        self.campo_token = campo_de_texto()
        # Com bolinhas enquanto se digita, para não ficar à vista de quem passa.
        self.campo_token.setEchoMode(QLineEdit.Password)
        self.corpo.addWidget(self.campo_token)
        self.token_salvo = QWidget()
        linha = QHBoxLayout(self.token_salvo)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(estilo.ESPACO_2)
        aviso = rotulo_de_campo("token salvo")
        aviso.setStyleSheet(f"font-size: {estilo.TEXTO_PEQUENO}px; color: {estilo.COR_SUCESSO};")
        self.botao_substituir = _botao_pequeno("Substituir", self._substituir_token)
        self.botao_apagar = _botao_pequeno("Apagar", self._apagar_token)
        linha.addWidget(aviso)
        linha.addStretch()
        linha.addWidget(self.botao_substituir)
        linha.addWidget(self.botao_apagar)
        self.token_salvo.setFixedWidth(LARGURA_DO_CONTEUDO)
        self.corpo.addWidget(self.token_salvo)
        self._trocando_token = False

        self.botao_salvar = _botao_pequeno("Salvar", self.salvar, principal=True)
        linha_salvar = QHBoxLayout()
        linha_salvar.addWidget(self.botao_salvar)
        linha_salvar.addStretch()
        self.corpo.addLayout(linha_salvar)

    def base(self):
        return _rede().base_do_endereco(config_ia.endereco_do_servidor())

    def pode_ligar(self):
        return bool(config_ia.endereco_do_servidor())

    def atualizar(self):
        super().atualizar()
        self.frase_salve.setVisible(not self.pode_ligar())
        salvo = config_ia.token_salvo() and not self._trocando_token
        self.token_salvo.setVisible(salvo)
        self.campo_token.setVisible(not salvo)

    def showEvent(self, evento):
        super().showEvent(evento)
        endereco = config_ia.endereco_do_servidor()
        if endereco:
            self._mostrar_por_que(_rede().avaliar_endereco(endereco, config_ia.enderecos_locais()))

    def _mostrar_por_que(self, avaliacao):
        self.por_que.setText(avaliacao.por_que)

    def salvar(self):
        """Grava o endereço e o token, com o aviso antes, quando ele cabe (RN-19)."""
        self.faixa_erro.setVisible(False)
        endereco = self.campo_endereco.text().strip()
        if not endereco:
            self.faixa_erro.mostrar("Escreva o endereço que a TI informou.")
            return
        avaliacao = _rede().avaliar_endereco(endereco, config_ia.enderecos_locais())
        if not avaliacao.valido:
            self.faixa_erro.mostrar(avaliacao.problema)
            return
        mudou_o_endereco = endereco != config_ia.endereco_do_servidor()
        if mudou_o_endereco:
            # Endereço novo: a confirmação do antigo não vale para ele (RN-20).
            avisos_da_ia.esquecer_confirmado()
        if not avaliacao.reconhecido and not avisos_da_ia.confirmar_endereco(endereco, avaliacao, self):
            self.campo_endereco.setText(config_ia.endereco_do_servidor())
            return

        token = self.campo_token.text().strip()
        if token and not config_ia.salvar_token(token):
            # Nem o endereço fica: a pessoa veria "salvo" e o teste falharia sem dizer
            # por quê. E o token não vai para nenhum outro lugar (RN-13).
            self.faixa_erro.mostrar(
                "Não foi possível guardar o token: a pasta do programa não aceitou. "
                "Nada foi salvo.")
            return
        self.campo_token.clear()
        self._trocando_token = False
        config_ia.guardar_do_destino(SERVIDOR, endereco=endereco)
        self._mostrar_por_que(avaliacao)
        if mudou_o_endereco or token:
            self._o_teste_nao_vale_mais()
        self.atualizar()
        self._ao_mudar()

    def _o_teste_nao_vale_mais(self):
        config_ia.marcar_testado(SERVIDOR, False)
        config_ia.marcar_motor_testado(SERVIDOR, False)
        if self.esta_ligado():
            config_ia.desligar_destino()

    def _substituir_token(self):
        self._trocando_token = True
        self.atualizar()
        self.campo_token.setFocus()

    def _apagar_token(self):
        if not config_ia.apagar_token():
            self.faixa_erro.mostrar("Não foi possível apagar o token: a pasta do "
                                    "programa não aceitou.")
            return
        self._o_teste_nao_vale_mais()
        self.atualizar()
        self._ao_mudar()


class _TelaHabilitar(_TelaBasica):
    """Os três switches (RN-24, RN-25, RN-38 e RN-39 da spec 004)."""

    RECUO = 44

    def __init__(self, ao_mudar, ao_ligar_o_motor):
        super().__init__("Habilitar IA", "")
        self._ao_mudar = ao_mudar
        self._ao_ligar_o_motor = ao_ligar_o_motor

        self.geral = Interruptor()
        self.geral.clicked.connect(self._geral_clicado)
        self.corpo.addWidget(linha_do_switch(self.geral, "Habilitar IA"))
        self.configure_primeiro = Faixa("info")
        self.configure_primeiro.mostrar(
            "Configure primeiro o LM Studio ou o Servidor de IA Interno, nos itens "
            "ao lado.")
        self.corpo.addWidget(self.configure_primeiro)
        self.foi_desligada = Faixa("alerta")
        self.foi_desligada.mostrar(
            "A IA foi desligada porque nenhum destino está habilitado. Ao religar um "
            "destino e este switch, tudo volta como estava.")
        self.corpo.addWidget(self.foi_desligada)

        self.revisora = Interruptor()
        self.revisora.clicked.connect(self._revisora_clicada)
        self.corpo.addWidget(linha_do_switch(self.revisora, "IA revisora", self.RECUO))
        self.sobre_a_revisora = Frase(
            "Um segundo par de olhos na revisão do Anonimizar. Ela lê só o texto, e não "
            "compara com a página original.", largura=LARGURA_DO_CONTEUDO - 2 * self.RECUO)
        self.corpo.addWidget(_recuado(self.sobre_a_revisora, 2 * self.RECUO))
        self.corpo.addWidget(_recuado(rotulo_de_campo("A revisão por IA começa"), 2 * self.RECUO))
        self.inicio_clique = QRadioButton('ao clicar no botão "Revisar com IA"')
        self.inicio_abrir = QRadioButton("sozinha, ao abrir a revisão")
        for botao, inicio in ((self.inicio_clique, config_ia.INICIO_NO_CLIQUE),
                              (self.inicio_abrir, config_ia.INICIO_AO_ABRIR)):
            botao.setStyleSheet(f"color: {estilo.COR_TEXTO}; font-size: {estilo.TEXTO_PEQUENO}px;")
            botao.clicked.connect(lambda _=False, i=inicio: config_ia.escolher_inicio(i))
            self.corpo.addWidget(_recuado(botao, 2 * self.RECUO))

        self.motor = Interruptor()
        self.motor.clicked.connect(self._motor_clicado)
        self.corpo.addWidget(linha_do_switch(self.motor, "IA como motor de leitura", self.RECUO))
        self.ressalva = Faixa("alerta", largura=LARGURA_DO_CONTEUDO - 2 * self.RECUO)
        self.ressalva.mostrar(RESSALVA_DO_MOTOR)
        self.corpo.addWidget(_recuado(self.ressalva, 2 * self.RECUO))
        self.falta_modelo = Frase(largura=LARGURA_DO_CONTEUDO - 2 * self.RECUO,
                                  cor=estilo.COR_ALERTA)
        self.corpo.addWidget(_recuado(self.falta_modelo, 2 * self.RECUO))
        self.corpo.addStretch()
        self.atualizar()

    def atualizar(self):
        pode = config_ia.destino_configurado()
        ligada = config_ia.geral_ligada() and pode
        destino = config_ia.destino_ligado()
        self.legenda.setText(
            f"Destino em uso: {config_ia.NOME_NA_TELA[destino]}, "
            f"{config_ia.modelo_da_revisora(destino)}" if pode else "")
        self.geral.setEnabled(pode)
        self.geral.setChecked(ligada)
        desligada_pelo_destino = config_ia.desligada_pelo_destino()
        self.configure_primeiro.setVisible(not pode and not desligada_pelo_destino)
        self.foi_desligada.setVisible(desligada_pelo_destino and not ligada)
        self.revisora.setEnabled(ligada)
        self.revisora.setChecked(ligada and config_ia.revisora_marcada())
        for botao in (self.inicio_clique, self.inicio_abrir):
            botao.setEnabled(self.revisora.isChecked())
        marcado = (self.inicio_abrir if config_ia.inicio_da_revisao() == config_ia.INICIO_AO_ABRIR
                   else self.inicio_clique)
        marcado.setChecked(True)
        self.motor.setEnabled(ligada)
        self.motor.setChecked(ligada and config_ia.motor_marcado())
        sem_modelo = config_ia.motor_ligado() and not config_ia.modelo_do_motor(destino)
        self.falta_modelo.setText(
            f"Escolha o modelo do motor na tela do {config_ia.NOME_NA_TELA[destino]}."
            if sem_modelo else "")

    def showEvent(self, evento):
        self.atualizar()
        super().showEvent(evento)

    def _geral_clicado(self, ligada):
        if ligada:
            config_ia.ligar_geral()
        else:
            config_ia.desligar_geral()
        self._ao_mudar()

    def _revisora_clicada(self, ligada):
        config_ia.marcar_revisora(ligada)
        self._ao_mudar()

    def _motor_clicado(self, ligado):
        config_ia.marcar_motor(ligado)
        self._ao_mudar()
        if ligado:
            self._ao_ligar_o_motor()


class PainelIa(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(estilo.ESPACO_4, estilo.ESPACO_4,
                                  estilo.ESPACO_5, estilo.ESPACO_5)
        self.telas = QStackedWidget()
        layout.addWidget(self.telas)

        self.tela_lm_studio = _TelaLmStudio(self._mudou)
        self.tela_servidor = _TelaServidor(self._mudou)
        self.tela_habilitar = _TelaHabilitar(self._mudou, self._testar_o_motor)
        self._areas = {}
        for nome, tela in ((LM_STUDIO, self.tela_lm_studio),
                           (SERVIDOR, self.tela_servidor),
                           (HABILITAR, self.tela_habilitar)):
            area = _rolavel(tela)
            self._areas[nome] = area
            self.telas.addWidget(area)

    def _mudou(self):
        """Uma tela mudou algo que as outras mostram: ligar um destino desliga o outro,
        e o "Habilitar IA" depende dos dois."""
        self.tela_lm_studio.atualizar()
        self.tela_servidor.atualizar()
        self.tela_habilitar.atualizar()

    def _testar_o_motor(self):
        """Ligada a chave com um modelo já guardado, ele é testado com a imagem."""
        destino = config_ia.destino_ligado()
        if destino:
            tela = self.tela_lm_studio if destino == LM_STUDIO else self.tela_servidor
            tela._testar_o_motor_escolhido()

    def mostrar(self, nome):
        self.telas.setCurrentWidget(self._areas[nome])

    def tela_atual(self):
        for nome, area in self._areas.items():
            if area is self.telas.currentWidget():
                return nome
        return None

    def encerrar(self):
        self.tela_lm_studio.encerrar()
        self.tela_servidor.encerrar()

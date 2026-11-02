"""O painel de Configurações de IA: três telas, uma por item do submenu.

Segue o rascunho aprovado mockups/ia/01-configuracoes-de-ia.html.

O arquivo que fala com a rede só é carregado quando a pessoa aciona algo aqui: sem
ninguém mexer nestas telas, o programa nem o abre (RN-43 da spec 004).
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
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
    etiqueta_nao_encontrado,
    estilo_do_radio,
    etiqueta_online,
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
LM_STUDIO_NESTA_MAQUINA = "A IA roda nesta máquina, e o documento não sai dela."
LM_STUDIO_EM_OUTRA_MAQUINA = ("A IA roda no endereço abaixo, fora desta máquina. O texto do "
                              "documento viaja até lá, com os CPFs inteiros.")
ENDERECO_NAO_CONFIRMADO = "O endereço não foi confirmado, e nada foi enviado."
ONLINE = "online"
NAO_ENCONTRADO = "nao_encontrado"
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
        # Todos os pedidos abertos: guardando só o último, um pedido anterior não
        # seria cortado ao fechar, e a janela fecharia com ele rodando (lente crítica).
        self._canceladores = []
        # O destino que estava ligado antes de este ser testado, para voltar a ele se
        # o teste falhar: a falha não pode deixar a pessoa sem nenhum dos dois.
        self._destino_de_antes = None
        self.ao_motor_falhar = lambda frase: None
        # Quantos pedidos estão abertos. Enquanto houver um, nada do que ele usou pode
        # mudar: a resposta antiga religaria o destino, com o endereço já trocado.
        self._pedidos_abertos = 0
        # Já perguntou ao destino quais modelos ele tem? Ao abrir o programa, não: a
        # pergunta só vai quando a pessoa abre a tela. E o destino que respondeu que não
        # sabe listar pede o nome digitado.
        self._lista_conhecida = False
        self._sem_lista = False
        self._base_ao_abrir = None
        self.interruptor = Interruptor()
        self.interruptor.clicked.connect(self._switch_clicado)
        # Só depois de o destino responder nesta abertura: é a prova de que ele está no
        # ar, e o "testado" guardado de outro dia não prova isso.
        self.online = etiqueta_online()
        self.online.setVisible(False)
        self.nao_encontrado = etiqueta_nao_encontrado()
        self.nao_encontrado.setVisible(False)
        # Um campo só, para as duas etiquetas nunca aparecerem juntas (revisão 54).
        self._conexao = None
        self.corpo.addWidget(linha_do_switch(self.interruptor, self.rotulo_do_switch,
                                             ao_lado=(self.online, self.nao_encontrado)))
        self.situacao = Frase()
        self.corpo.addWidget(self.situacao)
        self.faixa_erro = Faixa("erro")
        self.faixa_erro.setVisible(False)
        self.corpo.addWidget(self.faixa_erro)
        # Fora da troca do switch, e sempre à vista: a pessoa confere o endereço primeiro,
        # e liga só se quiser (RN-64).
        self.botao_testar = QPushButton("Testar conexão")
        self.botao_testar.setCursor(Qt.PointingHandCursor)
        self.botao_testar.setStyleSheet(estilo.estilo_botao(principal=False, pequeno=True))
        self.botao_testar.clicked.connect(self._testar_conexao)
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
        for peca in (self.rotulo_revisora, self.seletor_revisora, self.campo_revisora,
                     self.rotulo_motor, self.seletor_motor, self.campo_motor):
            self.corpo.addWidget(peca)
        self.corpo.addStretch()
        self.atualizar()

    def _montar_campos(self):
        """Os campos próprios de cada destino, entre a situação e os modelos."""

    def base(self):
        raise NotImplementedError

    def pode_ligar(self):
        return True

    def pode_falar(self, perguntando=True):
        """Pode mandar um pedido a este destino? Quem tem aviso de endereço diz aqui."""
        return True

    def _novo_cancelador(self):
        cancelador = _rede().Cancelador()
        self._canceladores.append(cancelador)
        return cancelador

    def _token(self):
        return config_ia.token_do_destino(self.nome)

    def esta_ligado(self):
        return config_ia.destino_ligado() == self.nome

    def atualizar(self):
        """Põe a tela de acordo com o que está guardado."""
        ligado = self.esta_ligado()
        self.interruptor.setChecked(ligado)
        self.interruptor.setEnabled(self.pode_ligar() and not self._pedidos_abertos)
        self._mostrar_etiquetas()
        if not self._pedidos_abertos:
            self.situacao.setText(self._frase_da_situacao() if ligado else "")
        self._mostrar_modelos(ligado)

    def _mostrar_etiquetas(self):
        livre = not self._pedidos_abertos
        self.online.setVisible(livre and self._conexao == ONLINE)
        self.nao_encontrado.setVisible(livre and self._conexao == NAO_ENCONTRADO)

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
        if digita:
            self.campo_revisora.setText(config_ia.modelo_da_revisora(self.nome))
            self.campo_motor.setText(config_ia.modelo_do_motor(self.nome))

    def _campos_do_destino(self):
        """O que muda para onde o pedido vai: fica travado enquanto ele está aberto."""
        return ()

    def _ocupado(self, ocupado):
        self._pedidos_abertos += 1 if ocupado else -1
        livre = not self._pedidos_abertos
        for peca in (self.interruptor, self.seletor_revisora, self.seletor_motor,
                     self.campo_revisora, self.campo_motor, self.botao_testar,
                     *self._campos_do_destino()):
            peca.setEnabled(livre)
        if ocupado:
            # O "Online" só se esconde durante o teste, e volta se o modelo responder: quem
            # testa o modelo já sabe que o destino está no ar.
            if self._conexao == NAO_ENCONTRADO:
                self._conexao = None
            self.situacao.setText(TESTANDO)
            self.faixa_erro.setVisible(False)
        elif livre:
            self.interruptor.setEnabled(self.pode_ligar())
        self._mostrar_etiquetas()

    # ---------------------------------------------------------- ligar e desligar

    def _switch_clicado(self, ligado):
        if ligado:
            self._ligar()
        else:
            self._conexao = None
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
        if not self.pode_falar():
            self.interruptor.setChecked(self.esta_ligado())
            return
        self._ocupado(True)
        base, token, cancelador = self.base(), self._token(), self._novo_cancelador()
        trabalho_da_ia.rodar(
            self, lambda: _rede().listar_modelos(base, token, cancelador),
            self._chegou_a_lista, self._lista_falhou)

    def _lista_falhou(self, frase):
        self._falhou_ao_ligar(frase)
        self._conexao = self._conexao_depois_da_falha(frase)
        self._mostrar_etiquetas()

    def _conexao_depois_da_falha(self, frase):
        """Só isto é "não encontrado". Recusar o token, por exemplo, é sinal de que ele foi
        encontrado, e a etiqueta mandaria a pessoa procurar o defeito no lugar errado."""
        return NAO_ENCONTRADO if frase in (_rede().NAO_RESPONDEU, _rede().DEMOROU) else None

    def _endereco_pronto(self):
        """O endereço que está escrito é o guardado? Sem isto, o teste diria "Online" sobre
        o endereço de antes, com o novo à vista no campo."""
        return True

    def _testar_conexao(self):
        if not self._endereco_pronto():
            return
        if self.esta_ligado():
            self._listar_e_testar()
            return
        # Desligado, o teste só diz se o destino responde: não liga nada, e não mexe no
        # destino que estiver em uso (RN-64).
        if not self.pode_falar():
            self.faixa_erro.mostrar(ENDERECO_NAO_CONFIRMADO)
            return
        self._ocupado(True)
        base, token, cancelador = self.base(), self._token(), self._novo_cancelador()
        trabalho_da_ia.rodar(
            self, lambda: _rede().listar_modelos(base, token, cancelador),
            self._conexao_respondeu, self._conexao_falhou)

    def _conexao_respondeu(self, modelos):
        self._ocupado(False)
        self._conexao = ONLINE
        self.atualizar()
        if modelos == []:
            self.faixa_erro.mostrar(NENHUM_MODELO)

    def _conexao_falhou(self, frase):
        self._ocupado(False)
        self._conexao = self._conexao_depois_da_falha(frase)
        self.atualizar()
        self.faixa_erro.mostrar(f"{frase} {self.FRASE_DO_TESTE}")

    def _chegou_a_lista(self, modelos):
        self._ocupado(False)
        antes = config_ia.destino_ligado()
        self._destino_de_antes = antes if antes != self.nome else None
        config_ia.ligar_destino(self.nome)
        if modelos == []:
            self._desligar_com_falha(NENHUM_MODELO)
            return
        self._conexao = ONLINE
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

    def _modelo_do_motor_sumiu(self):
        """O modelo guardado saiu do destino: o teste antigo não vale mais."""
        guardado = config_ia.modelo_do_motor(self.nome)
        if guardado and self.seletor_motor.count() and self.seletor_motor.findData(guardado) < 0:
            config_ia.marcar_motor_testado(self.nome, False)

    def _testar_o_que_esta_escolhido(self):
        self._modelo_do_motor_sumiu()
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
        # Enquanto não responde, não conta como configurado: um "testado" que sobrou de
        # outra vez deixaria a revisora ativa durante o teste (lente crítica).
        config_ia.marcar_testado(self.nome, False)
        # O teste manda o token: sem o endereço confirmado, ele não sai (RN-49).
        if not self.pode_falar():
            self.atualizar()
            self._ao_mudar()
            self.faixa_erro.mostrar(ENDERECO_NAO_CONFIRMADO)
            return
        self._ocupado(True)
        base, token, cancelador = self.base(), self._token(), self._novo_cancelador()
        trabalho_da_ia.rodar(
            self, lambda: _rede().testar_modelo(base, token, modelo, cancelador=cancelador),
            self._modelo_respondeu, self._falhou_ao_ligar)

    def _modelo_respondeu(self, _resultado):
        self._ocupado(False)
        self._destino_de_antes = None
        config_ia.marcar_testado(self.nome, True)
        self.atualizar()
        self._ao_mudar()
        self._testar_o_motor_escolhido()

    def _falhou_ao_ligar(self, frase):
        self._ocupado(False)
        self._desligar_com_falha(f"{frase} {self.FRASE_DE_FALHA}")

    def _desligar_com_falha(self, frase):
        """O switch volta para desligado, com o que fazer, e as escolhas ficam (RN-6)."""
        self._conexao = None
        config_ia.marcar_testado(self.nome, False)
        if self.esta_ligado():
            if self._destino_de_antes:
                config_ia.ligar_destino(self._destino_de_antes)
            else:
                config_ia.desligar_destino()
        self._destino_de_antes = None
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
        # Enquanto não responde, não vale: um "testado" que sobrou de outra vez deixaria a
        # IA ler de verdade, com os CPFs inteiros, durante o teste.
        config_ia.marcar_motor_testado(self.nome, False)
        # Ligar a chave do motor chega aqui sem ter passado por nenhuma outra tela, e
        # este teste também manda o token (revisão de segurança, RN-49).
        if not self.pode_falar():
            self.atualizar()
            self._ao_mudar()
            self.faixa_erro.mostrar(ENDERECO_NAO_CONFIRMADO)
            self.ao_motor_falhar(ENDERECO_NAO_CONFIRMADO)
            return
        self._ocupado(True)
        base, token, cancelador = self.base(), self._token(), self._novo_cancelador()
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
        mensagem = f"O modelo do motor não leu a imagem de teste. {frase}"
        self.faixa_erro.mostrar(mensagem)
        # Quem ligou a chave está na outra tela, e não veria esta faixa (lente crítica).
        self.ao_motor_falhar(mensagem)

    def showEvent(self, evento):
        """Abrindo a tela com o destino já ligado, busca a lista de modelos.

        Só aqui, e não ao abrir o programa: quem não entra nesta tela não abre
        conexão nenhuma (RN-8). Sem resposta, nada desliga: a falha só desliga no
        teste, e aqui a pessoa só veio olhar.
        """
        super().showEvent(evento)
        if self.esta_ligado() and not self._lista_conhecida:
            # Sem perguntar: quem só abriu a tela não pediu nada, e sem o endereço
            # confirmado nesta abertura o token não sai (RN-21).
            if not self.pode_falar(perguntando=False):
                self.situacao.setText('Clique em "Testar conexão" para conferir.')
                return
            self._lista_conhecida = True
            base, token, cancelador = self.base(), self._token(), self._novo_cancelador()
            self._base_ao_abrir = base
            trabalho_da_ia.rodar(self, lambda: _rede().listar_modelos(base, token, cancelador),
                                 self._lista_ao_abrir, self._sem_lista_ao_abrir)

    def _resposta_ao_abrir_vale(self):
        """Este pedido não trava a tela, porque a pessoa só veio olhar. Então, até a resposta
        chegar, ela pode ter trocado o endereço ou desligado, e a resposta seria sobre outro
        endereço. Ignorada, a pergunta volta na próxima vez que a tela abrir."""
        if self.esta_ligado() and self.base() == self._base_ao_abrir:
            return True
        self._lista_conhecida = False
        return False

    def _lista_ao_abrir(self, modelos):
        if not self._resposta_ao_abrir_vale():
            return
        self._conexao = ONLINE
        self._sem_lista = modelos is None
        self._encher_seletores(modelos or [])
        guardado = config_ia.modelo_da_revisora(self.nome)
        # A tela diria "Respondendo agora", e cada revisão falharia sem explicar.
        if guardado and self.seletor_revisora.count() and self.seletor_revisora.findData(guardado) < 0:
            config_ia.marcar_testado(self.nome, False)
        self._modelo_do_motor_sumiu()
        self.atualizar()
        self._ao_mudar()

    def _sem_lista_ao_abrir(self, frase):
        if not self._resposta_ao_abrir_vale():
            return
        self._conexao = self._conexao_depois_da_falha(frase)
        self._mostrar_etiquetas()
        self._lista_conhecida = False
        self.situacao.setText(f"{frase} Clique em \"Testar conexão\" para conferir.")

    def encerrar(self):
        """Corta o teste em andamento antes de o programa fechar: sem isso, a janela
        esperaria a resposta do modelo para fechar."""
        for cancelador in self._canceladores:
            cancelador.cancelar()
        trabalho_da_ia.esperar_terminar(self)


class _TelaLmStudio(_TelaDoDestino):
    nome = LM_STUDIO
    rotulo_do_switch = "Habilitar LM Studio"
    FRASE_DE_FALHA = ("Abra o LM Studio, carregue um modelo e ligue o servidor local, "
                      "e ligue este switch de novo. O endereço e o modelo ficaram guardados.")
    FRASE_DO_TESTE = "Confira o endereço e veja se o servidor local do LM Studio está ligado."

    def __init__(self, ao_mudar):
        super().__init__("LM Studio", LM_STUDIO_NESTA_MAQUINA, ao_mudar)

    def _montar_campos(self):
        self.antes_de_ligar = Faixa("info")
        self.antes_de_ligar.mostrar(
            "Antes de ligar: abra o LM Studio, carregue um modelo e ligue o servidor "
            "local dele.")
        self.corpo.addWidget(self.antes_de_ligar)
        self.corpo.addWidget(rotulo_de_campo("Endereço, como o LM Studio mostra"))
        self.campo_endereco = campo_de_texto()
        self.campo_endereco.editingFinished.connect(self._endereco_mudou)
        self.corpo.addWidget(self.campo_endereco)
        linha = QHBoxLayout()
        linha.addWidget(self.botao_testar)
        linha.addStretch()
        self.corpo.addLayout(linha)
        self._conferindo_o_endereco = False
        self._recusado_neste_clique = False
        # Voltou a digitar: aquele clique já passou, e não pode engolir o próximo.
        self.campo_endereco.textEdited.connect(self._esquecer_a_recusa)

    def showEvent(self, evento):
        # Só aqui: o de costume é escrito pelo arquivo da rede, que não abre sem precisar.
        self.campo_endereco.setText(config_ia.endereco_do_lm_studio())
        self._dizer_onde_a_ia_roda()
        super().showEvent(evento)

    def _dizer_onde_a_ia_roda(self):
        self.legenda.setText(LM_STUDIO_NESTA_MAQUINA if config_ia.lm_studio_nesta_maquina()
                             else LM_STUDIO_EM_OUTRA_MAQUINA)

    def _endereco_mudou(self):
        """Cola-se o endereço inteiro, porque é assim que o LM Studio o mostra.

        A trava é porque a caixa do aviso tira o foco do campo, e isso dispara este
        mesmo aviso de novo: sem ela, abriria uma caixa em cima da outra.
        """
        if self._conferindo_o_endereco:
            return False
        self._conferindo_o_endereco = True
        try:
            return self._conferir_o_endereco()
        finally:
            self._conferindo_o_endereco = False

    def _esquecer_a_recusa(self, _texto):
        self._recusado_neste_clique = False

    def _mouse_no_botao_de_testar(self):
        return self.botao_testar.underMouse()

    def _endereco_pronto(self):
        recusado, self._recusado_neste_clique = self._recusado_neste_clique, False
        if recusado:
            return False
        pronto = self._endereco_mudou()
        # Recusado agora, por este mesmo clique: não sobra nada para o próximo.
        self._recusado_neste_clique = False
        return pronto

    def _conferir_o_endereco(self):
        """Diz se o que está no campo é o que vale agora."""
        atual = config_ia.endereco_do_lm_studio()
        texto = self.campo_endereco.text().strip()
        novo = _rede().base_do_endereco(texto) if texto else atual
        if novo == _rede().base_do_endereco(atual):
            self.campo_endereco.setText(atual)
            return True
        avaliacao = _rede().avaliar_endereco(novo, config_ia.enderecos_locais())
        if not avaliacao.valido:
            self.campo_endereco.setText(atual)
            self.faixa_erro.mostrar(avaliacao.problema)
            # O campo já voltou ao endereço antigo: o clique que tirou o foco dele, ao
            # terminar, testaria esse, e o "Online" apagaria o erro.
            self._recusado_neste_clique = self._mouse_no_botao_de_testar()
            return False
        if not avaliacao.reconhecido and not avisos_da_ia.confirmar_endereco(novo, avaliacao, self):
            self.campo_endereco.setText(atual)
            return False
        self.faixa_erro.setVisible(False)
        config_ia.guardar_do_destino(LM_STUDIO, endereco=novo)
        self.campo_endereco.setText(novo)
        self._dizer_onde_a_ia_roda()
        # Com o endereço novo, os testes que passaram não valem mais.
        self._conexao = None
        config_ia.marcar_testado(LM_STUDIO, False)
        config_ia.marcar_motor_testado(LM_STUDIO, False)
        if self.esta_ligado():
            config_ia.desligar_destino()
        self.atualizar()
        self._ao_mudar()
        return True

    def base(self):
        return config_ia.base_do_destino(LM_STUDIO)

    def pode_falar(self, perguntando=True):
        return avisos_da_ia.pode_usar_o_endereco(config_ia.endereco_do_lm_studio(), self,
                                                 perguntando)

    def _campos_do_destino(self):
        return (self.campo_endereco,)

    def atualizar(self):
        super().atualizar()
        self.antes_de_ligar.setVisible(not self.esta_ligado())


class _TelaServidor(_TelaDoDestino):
    nome = SERVIDOR
    rotulo_do_switch = "Habilitar Servidor de IA Interno"
    FRASE_DE_FALHA = ("Confira o endereço, ou veja com a TI se ele está no ar. O "
                      "endereço e o token ficaram guardados.")
    FRASE_DO_TESTE = "Confira o endereço, ou veja com a TI se ele está no ar."

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
        linha_salvar.addWidget(self.botao_testar)
        linha_salvar.addStretch()
        self.corpo.addLayout(linha_salvar)

    def base(self):
        return _rede().base_do_endereco(config_ia.endereco_do_servidor())

    def _endereco_pronto(self):
        # Só salva o que mudou: salvar de novo um endereço de fora abriria o aviso à toa.
        if (self.campo_endereco.text().strip() == config_ia.endereco_do_servidor()
                and not self.campo_token.text().strip() and self.pode_ligar()):
            return True
        return self.salvar()

    def _campos_do_destino(self):
        return (self.campo_endereco, self.campo_token, self.botao_salvar,
                self.botao_substituir, self.botao_apagar)

    def pode_ligar(self):
        return bool(config_ia.endereco_do_servidor())

    def pode_falar(self, perguntando=True):
        return avisos_da_ia.pode_usar_o_servidor(self, perguntando)

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
        """Grava o endereço e o token, com o aviso antes, quando ele cabe (RN-19). Diz se
        gravou: o teste de conexão salva antes, e não pode seguir sem isso."""
        self.faixa_erro.setVisible(False)
        endereco = self.campo_endereco.text().strip()
        if not endereco:
            self.faixa_erro.mostrar("Escreva o endereço que a TI informou.")
            return False
        avaliacao = _rede().avaliar_endereco(endereco, config_ia.enderecos_locais())
        if not avaliacao.valido:
            self.faixa_erro.mostrar(avaliacao.problema)
            return False
        mudou_o_endereco = endereco != config_ia.endereco_do_servidor()
        if mudou_o_endereco:
            # Endereço novo: a confirmação do antigo não vale para ele (RN-20).
            avisos_da_ia.esquecer_confirmado()
        if not avaliacao.reconhecido and not avisos_da_ia.confirmar_endereco(endereco, avaliacao, self):
            self.campo_endereco.setText(config_ia.endereco_do_servidor())
            return False

        token = self.campo_token.text().strip()
        if token and not config_ia.salvar_token(token):
            # Nem o endereço fica: a pessoa veria "salvo" e o teste falharia sem dizer
            # por quê. E o token não vai para nenhum outro lugar (RN-13).
            self.faixa_erro.mostrar(
                "Não foi possível guardar o token: a pasta do programa não aceitou. "
                "Nada foi salvo.")
            return False
        anterior = config_ia.endereco_do_servidor()
        if (mudou_o_endereco and anterior and not token and config_ia.token_salvo()
                and not avisos_da_ia.manter_o_token_no_endereco_novo(self)
                and not config_ia.apagar_token()):
            # A pessoa recusou mandar o token para lá, e ele continua no arquivo: salvar
            # o endereço mandaria o token justamente para onde ela disse que não
            # (revisão de segurança, RN-50).
            self.campo_endereco.setText(anterior)
            self.faixa_erro.mostrar("Não foi possível apagar o token: a pasta do programa "
                                    "não aceitou. O endereço novo não foi salvo.")
            return False
        self.campo_token.clear()
        self._trocando_token = False
        config_ia.guardar_do_destino(SERVIDOR, endereco=endereco)
        self._mostrar_por_que(avaliacao)
        if mudou_o_endereco or token:
            self._o_teste_nao_vale_mais()
        self.atualizar()
        self._ao_mudar()
        return True

    def _o_teste_nao_vale_mais(self):
        self._conexao = None
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
        # O grupo é preciso: cada radio mora no próprio recuo, e o Qt só faz um desmarcar o
        # outro entre vizinhos da mesma caixa. Sem ele, os dois ficavam marcados.
        self.grupo_do_inicio = QButtonGroup(self)
        for botao, inicio in ((self.inicio_clique, config_ia.INICIO_NO_CLIQUE),
                              (self.inicio_abrir, config_ia.INICIO_AO_ABRIR)):
            self.grupo_do_inicio.addButton(botao)
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
            botao.setStyleSheet(estilo_do_radio(apagado=not botao.isEnabled()))
        marcado = (self.inicio_abrir if config_ia.inicio_da_revisao() == config_ia.INICIO_AO_ABRIR
                   else self.inicio_clique)
        marcado.setChecked(True)
        self.motor.setEnabled(ligada)
        self.motor.setChecked(ligada and config_ia.motor_marcado())
        sem_modelo = config_ia.motor_ligado() and not config_ia.modelo_do_motor(destino)
        self.falta_modelo.setText(
            f"Escolha o modelo do motor na tela do {config_ia.NOME_NA_TELA[destino]}."
            if sem_modelo else "")

    def mostrar_falha_do_motor(self, frase):
        self.falta_modelo.setText(frase)

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
        self.tela_lm_studio.ao_motor_falhar = self.tela_habilitar.mostrar_falha_do_motor
        self.tela_servidor.ao_motor_falhar = self.tela_habilitar.mostrar_falha_do_motor
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


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from app.adapters.inbound.qt.widgets.parameter_card import ParameterCard


class HelpPage(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(16, 16, 16, 16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 10, 24, 20)
        layout.setSpacing(16)

        title = QLabel("Manual Rápido do Usuário")
        title.setProperty("class", "heading-1")
        layout.addWidget(title)

        subtitle = QLabel("Comece em poucos minutos e saiba o que observar em cada experimento.")
        subtitle.setProperty("class", "text-secondary")
        layout.addWidget(subtitle)

        card_1 = ParameterCard("Interferência e difração — passo a passo")
        text_1 = QLabel(
            "<b>1.</b> Abra <b>Fendas</b> e escolha <b>1 Fenda</b> ou <b>2 Fendas</b>.<br>"
            "<b>2.</b> Ajuste λ, I₀, largura <i>a</i> e incidência <i>α</i>. Em duas fendas, mantenha <i>d &gt; a</i>.<br>"
            "<b>3.</b> Mova <i>θ</i> pelo controle, gráfico, mapa angular ou bancada. A linha pontilhada indica a direção consultada.<br>"
            "<b>4.</b> Use <b>Ampliar padrão</b> para enquadrar automaticamente o envelope central; o mesmo intervalo aparece nas três visualizações.<br>"
            "<b>5.</b> Leia I/I₀ e I atual na barra inferior. Use <b>CSV</b> para os dados e <b>Imagem</b> para o gráfico PNG."
        )
        text_1.setTextFormat(Qt.TextFormat.RichText)
        text_1.setWordWrap(True)
        text_1.setProperty("class", "text-secondary")
        card_1.add_widget(text_1)
        layout.addWidget(card_1)

        card_2 = ParameterCard("Polarização — passo a passo")
        text_2 = QLabel(
            "<b>1.</b> Abra <b>Polarização</b> e escolha luz <b>Não Polarizada</b> ou <b>Polarizada</b>.<br>"
            "<b>2.</b> Se a luz já for polarizada, ajuste o ângulo inicial φ₀.<br>"
            "<b>3.</b> Escolha de 1 a 3 polarizadores e ajuste os eixos φ₁, φ₂ e φ₃ entre 0° e 180°.<br>"
            "<b>4.</b> Compare a intensidade após cada etapa na tabela e observe a direção do campo elétrico no desenho.<br>"
            "<b>5.</b> Leia a intensidade final, transmissão total e direção resultante nos cartões. Use <b>CSV</b> para exportar as etapas."
        )
        text_2.setTextFormat(Qt.TextFormat.RichText)
        text_2.setWordWrap(True)
        text_2.setProperty("class", "text-secondary")
        card_2.add_widget(text_2)
        layout.addWidget(card_2)

        card_3 = ParameterCard("Como interpretar as visualizações")
        text_3 = QLabel(
            "• <b>Bancada vetorial:</b> esquema angular do experimento; não representa distâncias em escala.<br>"
            "• <b>Perfil de intensidade:</b> gráfico de I(θ)/I₀. Em duas fendas, as franjas aparecem dentro do envelope de difração.<br>"
            "• <b>Mapa angular:</b> brilho calculado por direção, com escala em graus — não é posição em centímetros no anteparo.<br>"
            "• <b>Cor:</b> representa aproximadamente λ entre 400 e 700 nm; o brilho representa intensidade.<br>"
            "• <b>Ângulos:</b> α é incidência, θ é observação e φ identifica eixos de polarização."
        )
        text_3.setTextFormat(Qt.TextFormat.RichText)
        text_3.setWordWrap(True)
        text_3.setProperty("class", "text-secondary")
        card_3.add_widget(text_3)
        layout.addWidget(card_3)

        card_4 = ParameterCard("Se algo parecer errado")
        text_4 = QLabel(
            "• Em duas fendas, verifique se <i>d &gt; a</i>.<br>"
            "• Com parâmetros inválidos em Fendas, o gráfico é o anterior e a exportação fica bloqueada.<br>"
            "• Se o marcador desaparecer no detalhe ampliado, θ está fora da área exibida; volte à visão completa ou ajuste θ.<br>"
            "• Use <b>Restaurar</b> para recuperar os parâmetros padrão; a escolha de zoom é preservada.<br>"
            "• <b>I₀ = 0:</b> fonte sem luz. Em Fendas, o gráfico conserva apenas o perfil teórico normalizado.<br>"
            "• <b>Abaixo da escala visual:</b> campo positivo muito pequeno, apresentado em notação científica.<br>"
            "• Os botões +/− aplicam o passo indicado pelo controle; o slider e o valor numérico permanecem sincronizados.<br>"
            "• Consulte <b>Teoria</b> para as equações e hipóteses dos modelos. O LumenLab funciona totalmente offline."
        )
        text_4.setTextFormat(Qt.TextFormat.RichText)
        text_4.setWordWrap(True)
        text_4.setProperty("class", "text-secondary")
        card_4.add_widget(text_4)
        layout.addWidget(card_4)

        files = ParameterCard("Salvar, reabrir e comparar")
        text = QLabel(
            "<b>Arquivo → Salvar experimento</b> (Ctrl+S) grava os parâmetros do módulo ativo em JSON. "
            "<b>Abrir experimento</b> (Ctrl+O) valida os parâmetros e recalcula os resultados.<br>"
            "Em Fendas, use <b>Fixar referência</b> e altere λ, a ou outro parâmetro: a curva tracejada fica fixa. "
            "<b>Remover referência</b> encerra a comparação. Cada curva é normalizada pelo seu próprio I₀. "
            "O PNG inclui as duas curvas; CSV e JSON salvam somente a configuração atual.<br>"
            "Em telas menores ou com escala ampliada, use as barras de rolagem da área de trabalho e do painel de parâmetros."
        )
        text.setWordWrap(True)
        files.add_widget(text)
        layout.addWidget(files)

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)

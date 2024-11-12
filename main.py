from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Ellipse, Line, PushMatrix, PopMatrix, Rotate
from kivy.animation import Animation
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.config import Config
from roleta import Roleta

# Configuração para iniciar em tela cheia
Config.set('graphics', 'fullscreen', 'auto')

# KV Design para a interface da aplicação com fundo cinza
kv = '''
BoxLayout:
    orientation: 'horizontal'
    canvas.before:
        Color:
            rgba: 0.9, 0.9, 0.9, 1  # Fundo cinza
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.7

        RoletaWidget:
            id: roleta_widget
            size_hint: (1, 0.7)

        MDRaisedButton:
            text: "Sortear"
            pos_hint: {"center_x": 0.5}
            on_release: app.sortear_nome()
            size_hint_y: None
            height: dp(40)

        MDLabel:
            id: output_label
            text: ""
            halign: "center"
            theme_text_color: "Primary"
            size_hint_y: None
            height: self.texture_size[1]

    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.3

        MDTextField:
            id: nome_input
            hint_text: "Insira um nome"
            pos_hint: {"center_x": 0.5}
            size_hint_x: 0.9

        MDRaisedButton:
            text: "Adicionar Nome"
            pos_hint: {"center_x": 0.5}
            on_release: app.adicionar_nome(nome_input.text)
            size_hint_y: None
            height: dp(40)

        RecycleView:
            id: nome_list
            viewclass: 'NomeListItem'
            scroll_type: ['bars', 'content']
            bar_width: 10
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'

<NomeListItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(56)

    # Se o item não estiver sendo editado, exibe o nome e o botão "Editar"
    Label:
        id: name_label
        text: root.text if not root.is_editing else ""
        size_hint_x: 0.4
        color: 0, 0, 0, 1  # Cor do texto definida como preto
        opacity: 1 if not root.is_editing else 0

    # Se o item estiver sendo editado, exibe um campo TextInput para alterar o nome
    TextInput:
        id: edit_input
        text: root.text
        multiline: False
        size_hint_x: 0.4
        opacity: 1 if root.is_editing else 0
        disabled: not root.is_editing

    Widget:
        size_hint_x: 0.1
        canvas.before:
            Color:
                rgba: root.cor
            Rectangle:
                pos: self.pos
                size: self.size

    Button:
        text: "Editar"
        size_hint_x: 0.15
        on_release: root.on_edit()
        opacity: 1 if not root.is_editing else 0

    Button:
        text: "Salvar"
        size_hint_x: 0.15
        on_release: root.on_save()
        opacity: 1 if root.is_editing else 0

    Button:
        text: "X"
        size_hint_x: 0.15
        on_release: root.on_delete()
'''

class RoletaWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rota = Rotate(angle=0)
        self.segments = []
        self.colors = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), (1, 1, 0, 1), (1, 0, 1, 1), (0, 1, 1, 1)]
        self.selected_segment = None
        with self.canvas:
            self.canvas.add(self.rota)

    def atualizar_nomes(self, nomes):
        """Atualiza a lista de nomes e recria os segmentos da roleta"""
        self.segments = nomes
        self.desenhar_roleta()

    def desenhar_roleta(self):
        """Desenha a roleta com segmentos coloridos e numerados"""
        self.canvas.clear()
        total = len(self.segments)
        angle = 360 / total if total > 0 else 0
        
        with self.canvas:
            PushMatrix()
            self.rota = Rotate(angle=0, origin=self.center)
            for i, nome in enumerate(self.segments):
                Color(*self.colors[i % len(self.colors)])
                Ellipse(pos=(self.center_x - 150, self.center_y - 150), size=(300, 300), angle_start=i * angle, angle_end=(i + 1) * angle)
                
                # Coloca o nome no segmento
                label = Label(text=nome, font_size=12, color=(0, 0, 0, 1))
                label.center_x = self.center_x + 100 * (self.width / 300) * (angle / 360) * self.width / 2
                label.center_y = self.center_y + 100 * (self.height / 300) * (angle / 360) * self.height / 2
                self.add_widget(label)
                
            PopMatrix()

        # Adiciona o indicador para o segmento sorteado
        with self.canvas.after:
            Color(1, 0, 0, 1)
            Line(points=[self.center_x, self.center_y + 160, self.center_x, self.center_y + 190], width=4)

    def girar_roleta(self, resultado, callback):
        """Anima a roleta para simular um giro no sentido horário e parar no segmento escolhido"""
        if resultado not in self.segments:
            return
        total_segments = len(self.segments)
        segment_angle = 360 / total_segments
        segment_index = self.segments.index(resultado)
        
        # Resetar o ângulo inicial da rotação para garantir o giro completo
        self.rota.angle = 0
        
        # Adiciona três voltas completas (1080 graus) no sentido horário antes de parar no centro do segmento
        angulo_final = (360 * 3) + (segment_index * segment_angle) + (segment_angle / 2)
        
        anim = Animation(angle=angulo_final, duration=3, t='out_cubic')
        anim.bind(on_complete=lambda *x: callback(resultado))
        anim.start(self.rota)

class NomeListItem(RecycleDataViewBehavior, BoxLayout):
    """Item da lista de nomes, com botões para editar e excluir."""
    text = StringProperty("")
    cor = ListProperty([1, 1, 1, 1])  # Cor padrão (branco)
    is_editing = BooleanProperty(False)

    def refresh_view_attrs(self, rv, index, data):
        """Atualiza os atributos do item da lista."""
        self.text = data['text']
        self.cor = data['cor']
        return super(NomeListItem, self).refresh_view_attrs(rv, index, data)

    def on_edit(self):
        """Callback para iniciar a edição do nome."""
        self.is_editing = True

    def on_save(self):
        """Callback para salvar o novo nome após a edição."""
        novo_nome = self.ids.edit_input.text
        if novo_nome and novo_nome != self.text:
            app = MDApp.get_running_app()
            app.editar_nome(self.text, novo_nome)
        self.is_editing = False

    def on_delete(self):
        """Callback para deletar o nome."""
        app = MDApp.get_running_app()
        app.remover_nome(self.text)

class RoletaApp(MDApp):
    def build(self):
        self.roleta = Roleta()
        self.root = Builder.load_string(kv)
        return self.root

    def adicionar_nome(self, nome):
        if nome:
            self.roleta.adicionar_nome(nome)
            self.atualizar_roleta_widget()
            self.atualizar_lista_nomes()
            self.root.ids.nome_input.text = ""  # Limpa o campo de entrada após adicionar

    def remover_nome(self, nome):
        """Remove o nome da roleta."""
        self.roleta.remover_nome(nome)
        self.atualizar_roleta_widget()
        self.atualizar_lista_nomes()

    def editar_nome(self, nome_atual, novo_nome):
        """Permite a edição de um nome na lista."""
        if novo_nome and novo_nome != nome_atual:
            self.roleta.remover_nome(nome_atual)
            self.roleta.adicionar_nome(novo_nome)
            self.atualizar_roleta_widget()
            self.atualizar_lista_nomes()

    def atualizar_roleta_widget(self):
        """Atualiza a roleta visual com os nomes atuais."""
        self.root.ids.roleta_widget.atualizar_nomes(list(self.roleta.nomes.keys()))

    def atualizar_lista_nomes(self):
        """Atualiza a lista de nomes na interface."""
        nomes = list(self.roleta.nomes.keys())
        cores = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), (1, 1, 0, 1), (1, 0, 1, 1), (0, 1, 1, 1)]  # As cores devem ser iguais às da roleta

        self.root.ids.nome_list.data = [
            {'text': nome, 'cor': cores[i % len(cores)]} for i, nome in enumerate(nomes)
        ]

    def sortear_nome(self):
        resultado = self.roleta.sortear()
        # Esvaziar o texto do resultado antes de girar a roleta
        self.root.ids.output_label.text = ""
        # Iniciar o giro e mostrar o resultado ao final
        self.root.ids.roleta_widget.girar_roleta(resultado, self.exibir_resultado)

    def exibir_resultado(self, resultado):
        """Exibe o resultado do sorteio."""
        self.root.ids.output_label.text = f"Resultado do sorteio: {resultado}"

if __name__ == '__main__':
    RoletaApp().run()

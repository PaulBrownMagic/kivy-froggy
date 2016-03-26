from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from random import randint


class Sprite(Image):
    """
    Sprite: A base class for a sprite, which is an image with a position.
    """

    def __init__(self, **kwargs):
        super(Sprite, self).__init__(**kwargs)
        self.size = self.texture_size


class Frog(Sprite):
    """
    Frog inherits from Sprite. Animated game character.
    """

    def __init__(self):
        super(Frog, self).__init__(source="atlas://images/froggy_atlas/frog1", pos=(randint(0, 400), 0))
        self.place()
        self.frame = 1
        self.atlas = "atlas://images/froggy_atlas/frog"
        self.alive = True

    def update(self, dt):
        if self.alive:
            self.y += 500 * dt
            self.frame = self.frame + 1 if self.frame < 17 else 1
            src = self.atlas + str(int(self.frame/2))
            self.source = src
            if self.y > Window.size[1]:
                self.place()
                FroggyApp.score -= 1
        else:
            src = self.atlas + "_dead"
            self.source = src

    def place(self):
        self.x = randint(0, Window.size[0] - self.size[0])
        self.y = randint(Window.size[1] * -1, self.size[1] * -1)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.alive:
            dead_animation = Animation(size=(0, 0), center=touch.pos, t='in_quint')
            dead_animation.bind(on_complete=self.revive)
            dead_animation.start(self)
            self.alive = False
            FroggyApp.score += 1
            return True

    def revive(self, *_):
        self.size = (116, 172)
        self.alive = True
        self.place()


class Ripple(Sprite):

    def __init__(self, touch):
        super(Ripple, self).__init__(source="images/ripple.png", pos=touch.pos)
        self.size = (10, 10)
        self.animation = Animation(size=(80, 80), center=touch.pos, opacity=0, t='out_sine')


class FroggyGame(Widget):
    frogs = []

    def __init__(self):
        super(FroggyGame, self).__init__()
        for frog in range(4):
            frog = Frog()
            self.frogs.append(frog)
            self.add_widget(frog)

    def update(self, dt):
        for frog in self.frogs:
            frog.update(dt)

    def on_touch_down(self, touch):
        if Widget.on_touch_down(self, touch):
            return
        ripple = Ripple(touch)
        self.add_widget(ripple)
        ripple.animation.start(ripple)


class FroggyApp(App):
    """
    Kivy base App class.
    """
    score = 0

    def on_build(self):
        self.game = FroggyGame()
        return self.game

    def on_start(self):
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def update(self, dt):
        self.root.score_lbl.text = str(self.score)
        self.root.update(dt)


if __name__ == "__main__":
    LabelBase.register(name='d-puntillas',
                       fn_regular='fonts/d-puntillas-B-to-tiptoe.ttf'
                       )
    Window.clearcolor = get_color_from_hex('#00BCD4')
    FroggyApp().run()

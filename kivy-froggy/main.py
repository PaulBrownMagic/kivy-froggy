from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from random import randint

Builder.load_file('froggy.kv')

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
    caught = SoundLoader.load('sounds/catch.wav')

    def __init__(self):
        super(Frog, self).__init__(source="atlas://images/froggy_atlas/frog1", allow_stretch=True, pos=(randint(0, 400), 0))
        self.place()
        self.frame = 1
        self.atlas = "atlas://images/froggy_atlas/frog"
        self.alive = True
        self.size = ('116dp', '174dp')

    def update(self, dt):
        if self.alive:
            self.y += Window.height * dt * (1.63 + FroggyApp.score//10/100)
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
            FroggyApp.total_frogs += 1
            self.caught.play()
            return True

    def revive(self, *_):
        self.size = ('116dp', '174dp')
        self.alive = True
        self.place()


class Ripple(Sprite):
    splash = SoundLoader.load('sounds/splash.wav')

    def __init__(self, touch):
        super(Ripple, self).__init__(source="images/ripple.png", pos=touch.pos)
        self.size = (10, 10)
        self.animation = Animation(size=(150, 150), center=touch.pos, opacity=0, t='out_sine')
        self.splash.play()


class FroggyGame(Widget):
    frogs = []

    def get_frogs(self, _):
        self.frogs = []
        for frog in range(4):
            frog = Frog()
            self.frogs.append(frog)
            self.add_widget(frog)

    def update(self, dt):
        for frog in self.frogs:
            frog.update(dt)
        if FroggyApp.score >= 0:
            self.score_lbl.text = str(FroggyApp.score)
            FroggyApp.max_score = max(FroggyApp.score, FroggyApp.max_score)
        else:
            self.score_lbl.txt = "X"

    def on_touch_down(self, touch):
        if Widget.on_touch_down(self, touch):
            return
        ripple = Ripple(touch)
        self.add_widget(ripple)
        ripple.animation.start(ripple)


class FroggyScreen(Screen):
    frog_music_loop = SoundLoader.load('sounds/16167__visual__industrial-wack8.wav')
    frog_music_loop.loop = True
    to_level_sfx = SoundLoader.load('sounds/going_up.wav')
    game_over = True

    def on_pre_enter(self, *args):
        FroggyScreen.to_level_sfx.play()

    def on_enter(self, *args):
        super(FroggyScreen, self).on_enter(*args)
        Clock.schedule_once(self.game_start, 0.2)
        FroggyApp.music_loop.stop()

    def game_start(self, _):
        if self.game_over:
            FroggyApp.score = 0
            self.game = FroggyGame()
            self.add_widget(self.game)
            self.game_over = False
            Clock.schedule_once(self.game.get_frogs, 1)
            Clock.schedule_interval(self.update, 1.0 / 60.0)
            FroggyScreen.frog_music_loop.play()

    def update(self, dt):
        self.game.update(dt)
        if FroggyApp.score < 0:
            self.manager.current = 'summary'

    def on_pre_leave(self, *args):
        FroggyScreen.frog_music_loop.stop()
        if self.game:
            self.game.clear_widgets(children=self.game.frogs)

    def on_leave(self, *args):
        self.game_over = True
        if self.game:
            self.game.clear_widgets()
            Clock.unschedule(self.update)


class HomeScreen(Screen):

    def on_enter(self, *args):
        FroggyApp.music_loop.play()

    def on_pre_leave(self, *args):
        FroggyApp.button_pop_wav.play()


class SummaryScreen(Screen):

    def on_pre_enter(self, *args):
        self.ids.captured.text = "Total Captured: " + str(FroggyApp.total_frogs)
        self.ids.max_score.text = "Max Score: " + str(FroggyApp.max_score)
        FroggyApp.music_loop.play()

    def on_pre_leave(self, *args):
        FroggyApp.button_pop_wav.play()

    def on_leave(self, *args):
        FroggyApp.total_frogs = 0
        FroggyApp.max_score = 0


class FroggyApp(App):
    """
    Kivy base App class.
    """
    score = 0
    total_frogs = 0
    max_score = 0
    music_loop = SoundLoader.load('sounds/170255__dublie__trumpet.wav')
    music_loop.loop = True
    button_pop_wav = SoundLoader.load('sounds/262301__boulderbuff64__tongue-click.wav')

    def build(self):
        root = ScreenManager(transition=WipeTransition(duration=1))
        root.add_widget(HomeScreen(name='home'))
        root.add_widget(FroggyScreen(name='froggy'))
        root.add_widget(SummaryScreen(name='summary'))
        return root


if __name__ == "__main__":
    LabelBase.register(name='d-puntillas',
                       fn_regular='fonts/d-puntillas-B-to-tiptoe.ttf'
                       )
    Window.clearcolor = get_color_from_hex('#00BCD4')
    FroggyApp().run()

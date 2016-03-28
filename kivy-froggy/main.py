from __future__ import division
from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from random import randint
from settingsjson import settings_json

__version__ = "1.0"
__author__ = "Paul Brown"

class FroggySounds:
    """
    Namespace class for accessing sounds and applying settings
    """
    is_sound_on = True
    music_library = {
        'splash': SoundLoader.load('sounds/splash.wav'),
        'frog_caught': SoundLoader.load('sounds/catch.wav'),
        'frog_music_loop': SoundLoader.load('sounds/16167__visual__industrial-wack8.wav'),
        'to_level_sfx': SoundLoader.load('sounds/going_up.wav'),
        'music_loop': SoundLoader.load('sounds/170255__dublie__trumpet.wav'),
        'button_pop': SoundLoader.load('sounds/262301__boulderbuff64__tongue-click.wav')
    }
    music_library['frog_music_loop'].loop = True
    music_library['music_loop'].loop = True

    @classmethod
    def play(cls, sound):
        if cls.is_sound_on:
            cls.music_library[sound].play()

    @classmethod
    def stop(cls, sound):
        if cls.music_library[sound].state == 'play' and cls.is_sound_on:
            cls.music_library[sound].stop()

    @classmethod
    def sound_settings(cls, value):
        if int(value) == 0 and cls.is_sound_on:
            for sound in cls.music_library:
                cls.stop(sound)
            cls.is_sound_on = False
        else:
            cls.is_sound_on = True
            cls.play('music_loop')


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
    speeds = {
        'Easy': 0.7,
        'Medium': 1.1,
        'Hard': 1.4,
        'Impossible': 1.7
    }
    frog_size = ('116dp', '174dp')

    def __init__(self):
        super(Frog, self).__init__(source="atlas://images/froggy_atlas/frog1",
                                   allow_stretch=True,
                                   pos=(randint(0, 400), 0))
        self.place()
        self.frame = 1
        self.atlas = "atlas://images/froggy_atlas/frog"
        self.alive = True
        self.size = self.frog_size
        self.speed = self.get_speed()

    def update(self, dt):
        if self.alive:
            self.speed = max(self.speed, self.get_speed())
            self.y += self.speed * dt
            self.frame = self.frame + 1 if self.frame < 17 else 1
            self.source = self.atlas + str(self.frame//2)
            if self.y > Window.size[1]:
                self.place()
                FroggyApp.score -= 1
        else:
            self.source = self.atlas + "_dead"

    def place(self):
        self.x = randint(0, Window.size[0] - self.size[0])
        self.y = randint(-Window.size[1], -self.size[1])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.alive:
            dead_animation = Animation(size=(0, 0),
                                       center=touch.pos,
                                       t='in_quint')
            dead_animation.bind(on_complete=self.revive)
            dead_animation.start(self)
            self.alive = False
            FroggyApp.score += 1
            FroggyApp.total_frogs += 1
            FroggySounds.play('frog_caught')
            return True
        else:
            return False

    def get_speed(self):
        return Window.height * (self.speeds[FroggyGame.difficulty] + FroggyApp.score // 5 / 40)

    def revive(self, *_):
        self.size = self.frog_size
        self.alive = True
        self.place()


class Ripple(Sprite):
    """
    Ripple inherits from Sprite, special effect placed when user misses frog to show touch.
    """

    def __init__(self, touch):
        super(Ripple, self).__init__(source="images/ripple.png", pos=touch.pos)
        self.size = (50, 50)
        self.animation = Animation(size=(300, 300),
                                   center=touch.pos,
                                   opacity=0,
                                   t='out_sine')
        FroggySounds.play('splash')


class FroggyGame(Widget):
    """
    Widget that contains most of the game play. Allows elements to be added/removed separately.
    Gives more reliable positioning than the Screen class.
    """
    frogs = []
    difficulty = 'Medium'

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
    """
    Screen to hold game and control game flow.
    """
    game = None

    def on_pre_enter(self, *args):
        FroggySounds.play('to_level_sfx')

    def on_enter(self, *args):
        Clock.schedule_once(self.game_start, 0.2)
        FroggySounds.stop('music_loop')

    def game_start(self, _):
        FroggyApp.score = 0
        self.game = FroggyGame()
        self.add_widget(self.game)
        Clock.schedule_once(self.game.get_frogs, 1)
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        FroggySounds.play('frog_music_loop')

    def update(self, dt):
        self.game.update(dt)
        if FroggyApp.score < 0 or FroggyApp.score >= 101:
            self.manager.current = 'summary'

    def on_pre_leave(self, *args):
        FroggySounds.stop('frog_music_loop')
        self.game.clear_widgets(children=self.game.frogs)

    def on_leave(self, *args):
        self.game.clear_widgets()
        Clock.unschedule(self.update)
        self.clear_widgets()


class HomeScreen(Screen):
    """
    Home Screen with splash image, settings, and play button.
    """

    def on_enter(self, *args):
        FroggySounds.play('music_loop')

    def on_pre_leave(self, *args):
        FroggySounds.play('button_pop')


class SummaryScreen(Screen):
    """
    Screen shown to player after the level. Shows game play stats. No buttons in
    top majority to avoid click through in game play frenzy.
    """

    def on_pre_enter(self, *args):
        if FroggyApp.score >= 101:
            self.ids.title.text = "Well DONE!"
            self.ids.max_score.text = "Your TIME: " + str(FroggyApp.max_score)
        else:
            self.ids.title.text = "Game OVER!"
            self.ids.max_score.text = "Max SCORE: " + str(FroggyApp.max_score)
        self.ids.captured.text = "Total FROGS: " + str(FroggyApp.total_frogs)
        FroggySounds.play('music_loop')

    def on_pre_leave(self, *args):
        FroggySounds.play('button_pop')

    def on_leave(self, *args):
        FroggyApp.total_frogs = 0
        FroggyApp.max_score = 0


class FroggyScreenManager(ScreenManager):
    """
    Holds all the screens and settings for transitions.
    """
    def key_press_handler(self, window, key, *_):
        if key == 27:
            if self.current == 'home':
                return False
            elif self.current == 'froggy':
                self.current = 'summary'
                return True
            else:
                self.current = 'home'
                return True


class FroggyApp(App):
    """
    Kivy base App class.
    """
    score = 0
    total_frogs = 0
    max_score = 0

    def build(self):
        if self.config:
            FroggyGame.difficulty = self.config.get('settings', 'difficulty')
            FroggySounds.is_sound_on = self.config.getint('settings', 'sound_on') == 1
        root = FroggyScreenManager()
        Window.bind(on_keyboard=root.key_press_handler)
        return root

    def build_config(self, config):
        config.setdefaults('settings', {
            'sound_on': 1,
            'difficulty': 'Medium'
                           })

    def build_settings(self, settings):
        settings.add_json_panel('Froggit Settings',
                                self.config,
                                data=settings_json)

    def on_config_change(self, config, section, key, value):
        if key == 'sound_on':
            FroggySounds.sound_settings(value)
        elif key == 'difficulty':
            FroggyGame.difficulty = value


if __name__ == "__main__":
    LabelBase.register(name='d-puntillas',
                       fn_regular='fonts/d-puntillas-B-to-tiptoe.ttf')
    LabelBase.register(name='heydings',
                       fn_regular='fonts/heydings_icons.ttf')
    Window.clearcolor = get_color_from_hex('#00BCD4')
    FroggyApp().run()
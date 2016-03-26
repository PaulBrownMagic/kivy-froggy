# TODO: KV Score Label is cleared, need to find out how to add it back in.
# TODO: Register fonts needed ala KivyBlueprints Clock App, see bottom of code
# TODO: Colour palette: Google Material Design: 500 Colours, adapt all!
# TODO: Frogs need depth, dead frogs go under any living frogs. Higher frogs have softer shadow and are a bit bigger.
# TODO: Dead frogs exit, shrink to center.
# TODO: Add touch ripple on hit spot
# TODO: Transition to game play, maybe exit image up and enter frogs from below. Only 1 screen. But should cross-fade

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty
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
        self.y = randint(Window.size[1] * -1, self.height * -1)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.alive:
            self.alive = False
            Clock.schedule_once(self.revive, 1)
            FroggyApp.score += 1

    def revive(self, _):
        self.alive = True
        self.place()


class FroggyGame(Widget):

    def __init__(self):
        super(FroggyGame, self).__init__()
        self.frogs = []
        for frog in range(4):
            frog = Frog()
            self.frogs.append(frog)
            self.add_widget(frog)

    def update(self, dt):
        for frog in self.frogs:
            frog.update(dt)


class FroggyApp(App):
    """
    Kivy base App class.
    """
    score = 0
    game = None

    def build(self):
        self.game = FroggyGame()
        return self.game

    def on_start(self):
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)

if __name__ == "__main__":
    Window.clearcolor = get_color_from_hex('#00bcd4')
    FroggyApp().run()

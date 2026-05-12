from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


class ShimmerBox(Widget):
    def __init__(self, width=200, height=20, radius=4, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.width = dp(width)
        self.height = dp(height)
        with self.canvas:
            self._color = Color(0.9, 0.9, 0.9, 1)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
        self.bind(pos=self._update_pos, size=self._update_size)
        self._animate()

    def _update_pos(self, *args):
        self._rect.pos = self.pos

    def _update_size(self, *args):
        self._rect.size = self.size

    def _animate(self):
        anim = Animation(rgb=(0.85, 0.85, 0.85), duration=0.8) + Animation(rgb=(0.95, 0.95, 0.95), duration=0.8)
        anim.repeat = True
        anim.start(self._color)

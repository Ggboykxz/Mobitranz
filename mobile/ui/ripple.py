from kivy.animation import Animation
from kivy.graphics import Color, Ellipse
from kivy.metrics import dp
from kivymd.uix.button import MDRaisedButton


class RippleButton(MDRaisedButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ripple_color = [1, 1, 1, 0.3]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._create_ripple(touch.pos)
        return super().on_touch_down(touch)

    def _create_ripple(self, pos):
        with self.canvas.after:
            Color(*self._ripple_color)
            ellipse = Ellipse(pos=(pos[0] - dp(20), pos[1] - dp(20)), size=(dp(40), dp(40)))
        anim = Animation(
            size=(self.width * 2, self.height * 2),
            pos=(pos[0] - self.width, pos[1] - self.height),
            duration=0.5
        )
        anim.bind(on_complete=lambda *a: self.canvas.after.remove(ellipse))
        anim.start(ellipse)

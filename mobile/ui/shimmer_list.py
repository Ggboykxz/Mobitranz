from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from mobile.ui.shimmer import ShimmerBox


class ShimmerContainer(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=[16, 8],
            spacing=8,
            size_hint_y=None,
            **kwargs
        )
        self.bind(minimum_height=self.setter("height"))


class ShimmerTripCard(MDCard):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(90),
            padding=[12, 8],
            spacing=4,
            md_bg_color=[0.97, 0.97, 0.97, 1],
            radius=[8],
            **kwargs
        )
        row1 = MDBoxLayout(size_hint_y=None, height=dp(24))
        row1.add_widget(ShimmerBox(width=100, height=14))
        row1.add_widget(MDBoxLayout())
        row1.add_widget(ShimmerBox(width=60, height=14))
        self.add_widget(row1)
        self.add_widget(ShimmerBox(width=180, height=16))
        self.add_widget(ShimmerBox(width=80, height=14))


class ShimmerProfileRow(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            padding=[12, 8],
            spacing=12,
            **kwargs
        )
        self.add_widget(ShimmerBox(width=24, height=24, radius=12))
        self.add_widget(ShimmerBox(width=160, height=18))


class ShimmerEarningsCard(MDCard):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(130),
            padding=dp(20),
            spacing=dp(8),
            radius=[dp(16)],
            elevation=3,
            **kwargs
        )
        self.add_widget(MDBoxLayout())
        self.add_widget(ShimmerBox(width=120, height=18, pos_hint={"center_x": 0.5}))
        self.add_widget(ShimmerBox(width=180, height=40, pos_hint={"center_x": 0.5}))
        self.add_widget(MDBoxLayout())


class ShimmerStatsRow(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            spacing=dp(12),
            adaptive_height=True,
            **kwargs
        )
        for _ in range(3):
            card = MDCard(
                orientation="vertical",
                size_hint=(0.3, None),
                height=dp(80),
                padding=dp(8),
                spacing=dp(4),
                radius=[dp(8)],
                elevation=1
            )
            card.add_widget(ShimmerBox(width=32, height=24, pos_hint={"center_x": 0.5}))
            card.add_widget(ShimmerBox(width=60, height=16, pos_hint={"center_x": 0.5}))
            card.add_widget(ShimmerBox(width=40, height=12, pos_hint={"center_x": 0.5}))
            self.add_widget(card)


class ShimmerTransactionList(MDBoxLayout):
    def __init__(self, count=3, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(6),
            adaptive_height=True,
            **kwargs
        )
        for _ in range(count):
            txn = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(60),
                padding=[dp(12), dp(8)],
                spacing=dp(4),
                radius=[dp(8)],
                elevation=1
            )
            row = MDBoxLayout(adaptive_height=True, spacing=dp(8))
            row.add_widget(ShimmerBox(width=140, height=16, size_hint_x=0.6))
            row.add_widget(MDBoxLayout())
            row.add_widget(ShimmerBox(width=80, height=16, size_hint_x=0.4))
            txn.add_widget(row)
            txn.add_widget(ShimmerBox(width=100, height=12))
            self.add_widget(txn)

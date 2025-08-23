from ignis import widgets
from .widgets import NotificationCenter, QuickToggle
from .widgets.quicktogglecenter import QuickToggleCenter
from scripts import Wallpaper

class QuickCenter(widgets.Window):
    def __init__(self):
        super().__init__(
            css_classes=["quickcenter"],
            hide_on_close=True,
            visible=False,
            namespace="QuickCenter",
            popup=True,
            layer="overlay",
            anchor=["top", "bottom", "right"],
            margin_top=5,
            margin_bottom=5,
            margin_left=5,
            margin_right=5,
            width_request=400,
            child=widgets.Box(
                vertical=True,
                spacing=0,
                child=[
                    QuickToggleCenter(),
                    NotificationCenter()
                ]
            )
        )
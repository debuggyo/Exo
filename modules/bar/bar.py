# bar.py
import os
from ignis import widgets, utils
from user_settings import user_settings
from .widgets import Clock, WindowInfo, Workspaces, Tray, Media
from modules.m3components import Button
from modules.corners import Corners
from ignis.css_manager import CssManager
from ignis.window_manager import WindowManager

css_manager = CssManager.get_default()
window_manager = WindowManager.get_default()

class Bar:
    def __init__(self, monitor: int = 0):
        self.monitor = monitor
        self.__win = None
        self.time_date = Clock()
        self.media = Media()
        self.window_info = WindowInfo()
        self.workspaces = Workspaces()

    def _compute_margins(self, side: str):
        top, left, right, bottom = 5, 5, 5, 5
        if side == "top":
            bottom = 0
        elif side == "bottom":
            top = 0
        elif side == "left":
            right = 0
        elif side == "right":
            left = 0
        return top, left, right, bottom

    def build(self):
        side = user_settings.appearance.bar_side
        vertical = user_settings.appearance.vertical
        barfloating = user_settings.appearance.bar_floating
        compact_mode = user_settings.appearance.compact

        topmargin, leftmargin, rightmargin, bottommargin = self._compute_margins(side)

        if not barfloating:
            topmargin = leftmargin = rightmargin = bottommargin = 0

        height = 40
        if compact_mode == 1:
            height = 35
        elif compact_mode == 2:
            height = 30
        elif compact_mode == 3:
            height = 25

        anchors = [side] if user_settings.appearance.bar_centered else (["top", "bottom", side] if vertical else ["left", "right", side])

        self.__win = widgets.Window(
            namespace="Bar",
            monitor=self.monitor,
            anchor=anchors,
            css_classes=["bar"],
            exclusivity="exclusive",
            height_request=height,
            margin_top=topmargin,
            margin_left=leftmargin,
            margin_right=rightmargin,
            margin_bottom=bottommargin,
            child=widgets.CenterBox(
                vertical=vertical,
                css_classes=["bar-widgets"],
                start_widget=widgets.Box(
                    vertical=vertical,
                    spacing=2,
                    css_classes=["left-widgets"],
                    halign="fill",
                    child=[self.window_info.widget()],
                ),
                center_widget=widgets.Box(
                    vertical=vertical,
                    spacing=2,
                    css_classes=["center-widgets"],
                    halign="center",
                    child=[self.media.widget(), self.workspaces.widget()],
                ),
                end_widget=widgets.Box(
                    vertical=False,
                    spacing=2,
                    css_classes=["right-widgets"],
                    halign="end",
                    child=[
                        # widgets.Box(child=[widgets.Label(label="Goon Corner")], style="padding: 0px 15px;"),
                        Tray(),
                        widgets.Button(child=widgets.Label(label="tune"), css_classes=["quickcenter-button"], on_click=lambda x: window_manager.toggle_window("QuickCenter")),
                        self.time_date.widget()
                    ],
                ),
            ),
        )
        return self.__win

    def get_window(self):
        return self.__win
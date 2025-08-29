import os
from ignis import widgets, utils
from user_settings import user_settings
from .widgets import Clock, WindowInfo, Workspaces, Tray, Media
from modules.m3components import Button
from modules.corners import Corners
from ignis.css_manager import CssManager
from ignis.window_manager import WindowManager
from scripts import BarStyles

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

    def build(self):
        side = user_settings.interface.bar.side
        vertical = user_settings.interface.bar.vertical
        compact_mode = user_settings.interface.bar.density

        height = 40
        width = 40
        if compact_mode == 1:
            height = 35
            width = 35
        elif compact_mode == 2:
            height = 30
            width = 30
        elif compact_mode == 3:
            height = 25
            width = 25

        anchors = [side] if user_settings.interface.bar.centered else (["top", "bottom", side] if vertical else ["left", "right", side])
        
        if vertical:
            size_request = {"width_request": width}
        else:
            size_request = {"height_request": height}

        self.__win = widgets.Window(
            namespace="Bar",
            monitor=self.monitor,
            anchor=anchors,
            css_classes=["bar"],
            exclusivity="exclusive",
            **size_request,
            child=widgets.CenterBox(
                vertical=vertical,
                css_classes=["bar-widgets"],
                start_widget=widgets.Box(
                    vertical=vertical,
                    spacing=2,
                    css_classes=["left-widgets"],
                    child=[self.window_info.widget(), self.media.widget()],
                ),
                center_widget=widgets.Box(
                    vertical=vertical,
                    spacing=2,
                    css_classes=["center-widgets"],
                    child=[self.workspaces.widget()],
                ),
                end_widget=widgets.Box(
                    vertical=vertical,
                    spacing=2,
                    css_classes=["right-widgets"],
                    child=[
                        Tray(),
                        widgets.Button(child=widgets.Label(label="tune"), css_classes=["quickcenter-button"], on_click=lambda x: window_manager.toggle_window("QuickCenter")),
                        self.time_date.widget()
                    ],
                ),
            ),
        )
        
        BarStyles.setFloating(user_settings.interface.bar.floating)

        return self.__win

    def get_window(self):
        return self.__win
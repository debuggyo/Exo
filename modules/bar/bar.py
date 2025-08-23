import os
from ignis import widgets, utils
from user_settings import user_settings
from .widgets import Clock, WindowInfo, Workspaces, Tray
from modules.m3components import Button
from ignis.css_manager import CssManager, CssInfoPath
from ignis.window_manager import WindowManager
from scripts.set_bar_styles import BarStyles  # only import class, no instance

css_manager = CssManager.get_default()
window_manager = WindowManager.get_default()

class Bar:
    def __init__(self, monitor: int = 0):
        self.monitor = monitor
        self.__win = None
        self.time_date = Clock()
        self.window_info = WindowInfo()
        self.workspaces = Workspaces()
        BarStyles.set_bar_instance(self)  # register this Bar instance

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
        return top, left, right, bottom  # return margins

    def build(self):
        side = user_settings.appearance.bar_side
        vertical = user_settings.appearance.vertical
        barstyle = user_settings.appearance.style
        compact_mode = user_settings.appearance.compact

        topmargin, leftmargin, rightmargin, bottommargin = self._compute_margins(side)  # compute margins

        # apply style CSS
        if barstyle == "connected":
            topmargin = leftmargin = rightmargin = bottommargin = 0
            css_manager.apply_css(CssInfoPath(
                name="connected",
                path=os.path.expanduser("~/.config/ignis/styles/barstyles/connected.scss"),
                compiler_function=lambda path: utils.sass_compile(path=path),
            ))
        elif barstyle in ("floating", "island"):
            css_manager.apply_css(CssInfoPath(
                name="floating",
                path=os.path.expanduser("~/.config/ignis/styles/barstyles/floating.scss"),
                compiler_function=lambda path: utils.sass_compile(path=path),
            ))
        elif barstyle == "trislands":
            css_manager.apply_css(CssInfoPath(
                name="trislands",
                path=os.path.expanduser("~/.config/ignis/styles/barstyles/trislands.scss"),
                compiler_function=lambda path: utils.sass_compile(path=path),
            ))

        # determine height
        if compact_mode == 0:
            height = 40
        elif compact_mode == 1:
            height = 35
            css_manager.apply_css(CssInfoPath(
                name="compact",
                path=os.path.expanduser("~/.config/ignis/styles/compactmodes/compact.scss"),
                compiler_function=lambda path: utils.sass_compile(path=path),
            ))
        elif compact_mode in (2, 3):
            height = 30
            css_manager.apply_css(CssInfoPath(
                name="compactplus",
                path=os.path.expanduser("~/.config/ignis/styles/compactmodes/compactplus.scss"),
                compiler_function=lambda path: utils.sass_compile(path=path),
            ))
            if compact_mode == 3:
                height = 25
                css_manager.apply_css(CssInfoPath(
                    name="ultracompact",
                    path=os.path.expanduser("~/.config/ignis/styles/compactmodes/ultracompact.scss"),
                    compiler_function=lambda path: utils.sass_compile(path=path),
                ))

        # vertical CSS
        if vertical:
            css_manager.apply_css(CssInfoPath(
                name="vertical",
                path=os.path.expanduser("~/.config/ignis/styles/barstyles/vertical.scss"),
                compiler_function=lambda path: utils.sass_compile(path=path),
            ))

        # compute initial anchors
        anchors = [side] if barstyle == "island" else (["top", "bottom", side] if vertical else ["left", "right", side])

        # build Window
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
                    child=[Workspaces(), self.time_date.widget()],
                ),
                end_widget=widgets.Box(
                    vertical=False,
                    spacing=2,
                    css_classes=["right-widgets"],
                    halign="end",
                    child=[
                        widgets.Box(child=[widgets.Label(label="Goon Corner")], style="padding: 0px 15px;"),
                        widgets.Button(child=widgets.Label(label="tune"), css_classes=["quickcenter-button"], on_click=lambda x: window_manager.toggle_window("QuickCenter")),
                        Tray(),
                    ],
                ),
            ),
        )
        return self.__win

    def get_window(self):
        return self.__win  # safe accessor

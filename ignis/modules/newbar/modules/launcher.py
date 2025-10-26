from ignis import widgets
from ignis.window_manager import WindowManager
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
import modules.m3components as m3

class LauncherButton(widgets.EventBox, BaseWidget):
    __gtype_name__ = "ExoLauncherButton"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        widgets.EventBox.__init__(self)
        self._icon_name: str = "apps"
        self.window_manager = WindowManager.get_default()

        self.icon = m3.Icon(self._icon_name, 16, halign="center", valign="center")
        self.append(self.icon)

        self.on_click = lambda _: self.window_manager.toggle_window("Launcher")

        self.add_css_class("exo-launcher-button")
        BaseWidget.__init__(self, **kwargs)

    @IgnisProperty
    def icon_name(self) -> str:
        return self._icon_name

    @icon_name.setter
    def icon_name(self, value: str) -> None:
        if value == self._icon_name:
            return
        self._icon_name = value
        self.icon.set_icon(value)
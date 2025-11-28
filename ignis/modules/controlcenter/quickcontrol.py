from typing import Callable
from ignis import widgets, utils
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
from modules.m3components import Button, Icon

class QuickControl(Button, BaseWidget):
    __gtype_name__ = "QuickControl"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self,
        on_activate: Callable | None = None,
        on_deactivate: Callable | None = None,
        **kwargs
    ):
        Button.__init__(self, **kwargs)
        self._active: bool = False
        self._on_activate = on_activate
        self._on_deactivate = on_deactivate

        self.add_css_class("quick-control")

        self.on_click = self.do_toggle

        BaseWidget.__init__(self, **kwargs)

    @IgnisProperty
    def on_activate(self) -> Callable:
        return self._on_activate

    @on_activate.setter
    def on_activate(self, value: Callable):
        self._on_activate = value

    @IgnisProperty
    def on_deactivate(self) -> Callable:
        return self._on_deactivate

    @on_deactivate.setter
    def on_deactivate(self, value: Callable):
        self._on_deactivate = value

    @IgnisProperty
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        self._active = value
        if value:
            self.add_css_class("active")
        else:
            self.remove_css_class("active")

    def do_toggle(self, *args):
        print("Toggling")
        if self.active:
            if self._on_deactivate:
                self._on_deactivate(self)
        else:
            if self._on_activate:
                self._on_activate(self)
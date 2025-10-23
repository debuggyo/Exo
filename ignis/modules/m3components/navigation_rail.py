from gi.repository import Gtk
from ignis import widgets
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
from modules.m3components import Button

class NavigationRail(widgets.Box, BaseWidget):
    __gtype_name__ = "M3NavigationRail"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        widgets.Box.__init__(self)
        self.add_css_class("navigation-rail")
        
        self._tabs = {}
        self._selected_tab = None
        self._vertical = True
        self.buttons = {}
        
        BaseWidget.__init__(self, **kwargs)

        self.set_orientation(Gtk.Orientation.VERTICAL if self._vertical else Gtk.Orientation.HORIZONTAL)
        self.set_spacing(5)
        if not self.buttons:
             self._update_buttons()

    @IgnisProperty
    def vertical(self) -> bool:
        return self._vertical

    @vertical.setter
    def vertical(self, value: bool):
        self._vertical = value
        self.set_orientation(Gtk.Orientation.VERTICAL if value else Gtk.Orientation.HORIZONTAL)

    @IgnisProperty
    def tabs(self) -> dict:
        return self._tabs

    @tabs.setter
    def tabs(self, value: dict):
        self._tabs = value
        self._update_buttons()

    @IgnisProperty
    def selected_tab(self) -> str:
        return self._selected_tab

    @selected_tab.setter
    def selected_tab(self, key: str):
        if self._selected_tab == key:
            return

        if self._selected_tab and self._selected_tab in self.buttons:
            self.buttons[self._selected_tab].remove_css_class("selected")

        self._selected_tab = key
        if key in self.buttons:
            self.buttons[key].add_css_class("selected")

    def _update_buttons(self):
        child = self.get_first_child()
        while child:
            self.remove(child)
            child = self.get_first_child()
        self.buttons.clear()

        if not self._tabs:
            return

        for key, (icon, label) in self._tabs.items():
            btn = Button(
                icon=icon,
                label=label,
                ialign="center",
                valign="center",
                css_classes=["rail-button"],
                vertical=True,
                on_click=lambda *_, key=key: self.set_property("selected-tab", key),
            )
            self.buttons[key] = btn
            self.append(btn)
        
        if self._selected_tab and self._selected_tab in self.buttons:
            self.buttons[self._selected_tab].add_css_class("selected")

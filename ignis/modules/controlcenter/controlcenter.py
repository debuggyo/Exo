from ignis import widgets, utils
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
from .quick_toggles import *
from .sliders import QuickSliders

class ControlCenter(widgets.Window, BaseWidget):
    __gtype_name__ = "ControlCenter"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        unique_namespace = f"ControlCenter{kwargs.get('monitor', 0)}"
        widgets.Window.__init__(self, namespace=unique_namespace)
        self._position: list = ["top", "right"]

        self.quick_controls_container = widgets.Box(
            spacing=8,
            child=[
                NetworkToggle(),
                DarkModeToggle()
            ],
            css_classes=["quick-controls-container"]
        )
        self.bottom_buttons_container = widgets.Box(spacing=8)
        self.container = widgets.Box(
            vertical=True,
            spacing=8,
            child=[self.quick_controls_container, QuickSliders(), self.bottom_buttons_container],
            vexpand=False,
            hexpand=False,
        )

        close_button = widgets.Button(
            vexpand=True,
            hexpand=True,
            can_focus=False,
            on_click=lambda x: self.close()
        )
        main_overlay = widgets.Overlay(
            css_classes=["popup-close"],
            child=close_button,
            overlays=[self.container]
        )

        self.child = main_overlay
        self.popup = False
        self.layer = "overlay"
        self.kb_mode = "exclusive"
        self.anchor = ["top", "left", "right", "bottom"]
        self.container.add_css_class("exo-control-center")
        self.margin_top = 5
        self.margin_left = 5
        self.margin_right = 5
        self.margin_bottom = 5

        BaseWidget.__init__(self, **kwargs)

        self.set_visible(False)
        self.set_position(["top", "right"])

        self.connect("notify::visible", self.on_visibility_change)

    @IgnisProperty
    def position(self) -> list:
        return self._position

    @position.setter
    def position(self, value: list) -> None:
        self._position = value

        self.container.set_halign("center")
        self.container.set_valign("center")
        for side in value:
            if side == "top":
                self.container.set_valign("start")
            elif side == "bottom":
                self.container.set_valign("end")
            elif side == "left":
                self.container.set_halign("start")
            elif side == "right":
                self.container.set_halign("end")
    
    def on_visibility_change(self, *args):
        if self.visible:
            self.container.add_css_class("open")

    def close(self, *args):
        self.container.remove_css_class("open")
        def set_invisible():
            self.set_visible(False)
        utils.Timeout(300, set_invisible)

    def toggle_window(self, *args):
        if self.visible:
            self.close()
        else:
            self.set_visible(True)
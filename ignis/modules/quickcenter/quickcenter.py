from ignis import widgets
from ignis.window_manager import WindowManager
from .widgets import NotificationCenter
from modules.m3components import NavigationRail
from user_settings import user_settings
from ignis.services.niri import NiriService
import os


class QuickCenter(widgets.RevealerWindow):
    def __init__(self):
        window_manager = WindowManager.get_default()

        content_stack = widgets.Stack(vexpand=True)
        notification_center = NotificationCenter()
        content_stack.add_named(notification_center, "notifications")

        tabs = {
            "notifications": ("notifications", "Notifications"),
        }

        def toggle_view_local(key):
            content_stack.visible_child_name = key

        navigation_rail = NavigationRail(
            tabs=tabs,
            on_select=toggle_view_local,
            default="notifications",
            vertical=False,
        )
        navigation_rail.halign = "center"

        self.content_box = widgets.Box(
            vertical=True,
            spacing=0,
            hexpand=False,
            css_classes=["quick-center"],
            child=[navigation_rail, content_stack],
        )
        self.content_box.width_request = 400

        revealer = widgets.Revealer(
            child=self.content_box,
            transition_duration=300,
        )

        close_button = widgets.Button(
            vexpand=True,
            hexpand=True,
            can_focus=False,
            on_click=lambda x: window_manager.close_window("QuickCenter"),
        )

        main_overlay = widgets.Overlay(
            css_classes=["popup-close"],
            child=close_button,
            overlays=[revealer],
        )

        super().__init__(
            revealer=revealer,
            child=main_overlay,
            css_classes=["popup-close"],
            hide_on_close=True,
            visible=False,
            namespace="QuickCenter",
            popup=True,
            layer="overlay",
            kb_mode="exclusive",
            anchor=["left", "right", "top", "bottom"],
        )

        self.window_manager = window_manager
        self.content_stack = content_stack
        self.notification_center = notification_center
        self.tabs = tabs
        self.navigation_rail = navigation_rail
        self.revealer = revealer
        self.actual_content_box = revealer

        self.niri = NiriService.get_default()
        self.connect("notify::visible", self._toggle_revealer)
        self.update_side()

    def _toggle_revealer(self, *_):
        self.revealer.reveal_child = self.visible

    def update_side(self):
        side = user_settings.interface.bar.side
        self.revealer.transition_type = "none"
        if self.niri and self.niri.is_available:
            if side == "left":
                self.revealer.transition_type = "slide_right"
                self.content_box.set_halign("end")
            else:
                self.revealer.transition_type = "slide_left"
                self.content_box.set_halign("start")

        if side == "left":
            self.actual_content_box.set_halign("start")
            self.actual_content_box.anchor = ["top", "bottom", "left"]
        else:
            self.actual_content_box.set_halign("end")
            self.actual_content_box.anchor = ["top", "bottom", "right"]

        self.actual_content_box.queue_resize()

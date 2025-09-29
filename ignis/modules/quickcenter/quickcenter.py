from ignis import widgets
from ignis.window_manager import WindowManager
from ignis.services.notifications import NotificationService
from modules.m3components import Button
from .widgets import NotificationCenter, QuickSliders
from user_settings import user_settings
from ignis.services.niri import NiriService

window_manager = WindowManager.get_default()
notifications = NotificationService.get_default()


class QuickCenter(widgets.RevealerWindow):
    def open_window(self, window):
        window_manager.close_window("QuickCenter")
        window_manager.open_window(window)

    def __init__(self):
        notification_center = NotificationCenter()
        quick_sliders = QuickSliders()
        bottom_controls = widgets.Box(
            css_classes=["bottom-controls"],
            hexpand=True,
            halign="fill",
            homogeneous=False,
            spacing=5,
            child=[
                Button.button(
                    icon="power_settings_new",
                    halign="start",
                    hexpand=False,
                    on_click=lambda x: self.open_window("PowerMenu"),
                    vexpand=False,
                    valign="center",
                    size="xs",
                ),
                Button.button(
                    icon="settings",
                    halign="start",
                    hexpand=False,
                    on_click=lambda x: self.open_window("Settings"),
                    vexpand=False,
                    valign="center",
                    size="xs",
                ),
                Button.button(
                    icon="clear_all",
                    label="Clear all",
                    halign="end",
                    hexpand=True,
                    on_click=lambda x: notifications.clear_all(),
                    css_classes=["notification-clear-all"],
                    vexpand=True,
                    valign="center",
                    size="xs",
                    visible=notifications.bind(
                        "notifications", lambda value: len(value) != 0
                    ),
                ),
            ],
        )

        self.content_box = widgets.Box(
            vertical=True,
            spacing=0,
            hexpand=False,
            css_classes=["quick-center"],
            child=[notification_center, quick_sliders, bottom_controls],
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
        self.notification_center = notification_center
        self.revealer = revealer
        self.actual_content_box = revealer

        self.niri = NiriService.get_default()
        self.connect("notify::visible", self._toggle_revealer)
        self.update_side()

    def _toggle_revealer(self, *_):
        self.revealer.reveal_child = self.visible

    def update_side(self):
        position = user_settings.interface.modules
        location = position.location.systeminfotray
        bar = (
            user_settings.interface.bar
            if position.bar_id.systeminfotray == 0
            else user_settings.interface.bar
        )
        side = bar.side
        if side in ["left", "right"]:
            self.actual_content_box.set_halign("start" if side == "left" else "end")
            self.actual_content_box.anchor = ["top", "bottom", side]
        else:
            if location == "center":
                self.actual_content_box.set_halign("center")
                self.actual_content_box.anchor = ["top", "bottom"]
            else:
                self.actual_content_box.set_halign("start" if location == 0 else "end")
                self.actual_content_box.anchor = [
                    "top",
                    "bottom",
                    "left" if location == 0 else "end",
                ]

        self.revealer.transition_type = "none"
        if self.niri and self.niri.is_available:
            self.revealer.transition_type = (
                "slide_right"
                if self.actual_content_box.halign == "start"
                else "slide_left"
            )
            self.content_box.set_halign(
                "end" if self.actual_content_box.halign == "start" else "end"
            )

        self.actual_content_box.queue_resize()

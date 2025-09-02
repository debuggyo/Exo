from ignis import widgets
from ignis.window_manager import WindowManager
from .widgets import NotificationCenter
from modules.m3components import NavigationRail
from user_settings import user_settings
import os

class QuickCenter(widgets.Window):
    def __init__(self):
        self.window_manager = WindowManager.get_default()

        self.content_stack = widgets.Stack(vexpand=True)
        self.notification_center = NotificationCenter()
        self.content_stack.add_named(self.notification_center, "notifications")

        self.tabs = {
            "notifications": ("notifications", "Notifications"),
        }

        self.navigation_rail = NavigationRail(
            tabs=self.tabs,
            on_select=self.toggle_view,
            default="notifications",
            vertical=False
        )
        self.navigation_rail.halign = "center"


        self.actual_content_box = widgets.Box(
            vertical=True,
            spacing=0,
            hexpand=False,
            halign="end",
            css_classes=["quick-center"],
            child=[
                self.navigation_rail,
                self.content_stack
            ]
        )

        

        self.actual_content_box.anchor = ["top", "bottom", "right"]
        self.actual_content_box.margin_top = 5
        self.actual_content_box.margin_bottom = 5
        self.actual_content_box.margin_left = 5
        self.actual_content_box.margin_right = 5
        self.actual_content_box.width_request = 400

        close_button = widgets.Button(
            vexpand=True,
            hexpand=True,
            can_focus=False,
            on_click=lambda x: self.window_manager.close_window("QuickCenter")
        )

        main_overlay = widgets.Overlay(
            css_classes=["popup-close"],
            child=close_button,
            overlays=[self.actual_content_box]
        )
        
        super().__init__(
            css_classes=["popup-close"],
            hide_on_close=True,
            visible=False,
            namespace="QuickCenter",
            popup=True,
            layer="overlay",
            kb_mode="exclusive",
            anchor=["left", "right", "top", "bottom"],
            child=main_overlay
        )

    def toggle_view(self, key):
        self.content_stack.visible_child_name = key

    def update_side(self):
        if user_settings.interface.bar.side == "right":
            self.actual_content_box.set_halign("start")
        else:
            self.actual_content_box.set_halign("end")

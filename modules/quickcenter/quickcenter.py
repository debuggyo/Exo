from ignis import widgets
from .widgets import NotificationCenter
from modules.m3components import NavigationRail
import os

class QuickCenter(widgets.Window):
    def __init__(self):
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

        super().__init__(
            css_classes=["quickcenter"],
            hide_on_close=True,
            visible=False,
            namespace="QuickCenter",
            popup=True,
            layer="overlay",
            anchor=["top", "bottom", "right"],
            margin_top=5,
            margin_bottom=5,
            margin_left=5,
            margin_right=5,
            width_request=400,
            child=widgets.Box(
                vertical=True,
                spacing=0,
                child=[
                    self.navigation_rail,
                    self.content_stack
                ]
            )
        )

    def toggle_view(self, key):
        self.content_stack.visible_child_name = key
from ignis import widgets
from .widgets import NotificationCenter
from modules.m3components import NavigationRail
from .networkbox import NetworkBox
from .bluetoothbox import BluetoothBox
import os

class QuickCenter(widgets.Window):
    def __init__(self):
        self.content_stack = widgets.Stack(vexpand=True)
        self.notification_center = NotificationCenter()
        self.network_box = NetworkBox()
        self.bluetooth_box = BluetoothBox()
        self.content_stack.add_named(self.notification_center, "notifications")
        self.content_stack.add_named(self.network_box, "network")
        self.content_stack.add_named(self.bluetooth_box, "bluetooth")

        self.tabs = {
            "notifications": ("notifications", "Notifications"),
            "network": ("network_wifi", "Network"),
            "bluetooth": ("bluetooth", "Bluetooth"),
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
import asyncio
from ignis import widgets
from ignis.services.upower import UPowerService, UPowerDevice
from ignis import utils
from gi.repository import Gtk
from user_settings import user_settings

class Battery:
    def __init__(self):
        self.upowerservice = UPowerService.get_default()
        self.battery = None
        self.connected_signals = False

        self.battery_percent = widgets.Label(css_classes=["battery-percent-label"])
        self.battery_status = widgets.Label(css_classes=["battery-status"])
        self.battery_fill = widgets.Box(css_classes=["battery-fill"])

        self.text_container = widgets.Box(spacing=2, halign="center", valign="center", homogeneous=False)
        self.text_container.append(self.battery_status)
        self.text_container.append(self.battery_percent)

        self.battery_box = widgets.Overlay(
            child=self.battery_fill,
            overlays=[self.text_container],
            css_classes=["battery-box"],
            halign="center",
            valign="center"
        )
        self.battery_box.set_overflow(Gtk.Overflow.HIDDEN)

        self.container = widgets.Box(spacing=5, css_classes=["battery-widget"])
        self.container.append(self.battery_box)
        self.container.set_visible(False)

        self.upowerservice.connect("notify::batteries", self._on_batteries_changed)

        asyncio.create_task(self._initial_setup())
        self.update_layout()

    async def _initial_setup(self):
        await asyncio.sleep(0.1)
        self._on_batteries_changed(None, None)

    def _on_batteries_changed(self, service, prop):
        if self.upowerservice.batteries:
            self.battery = self.upowerservice.batteries[0]
            if not self.connected_signals:
                self.battery.connect("notify::percent", self._update_ui)
                self.battery.connect("notify::charging", self._update_ui)
                self.battery.connect("notify::icon-name", self._update_ui)
                self.connected_signals = True

            self._update_ui()
        else:
            self.battery = None
            self.connected_signals = False
            self._update_ui()

    def update_layout(self):
        is_vertical = user_settings.interface.bar.vertical
        self.container.set_vertical(is_vertical)
        self.text_container.set_vertical(is_vertical)

        if is_vertical:
            self.container.set_halign("fill")
            self.container.set_valign("center")
            self.container.set_hexpand(False)
            self.container.set_vexpand(False)
            self.battery_status.set_halign("center")
            self.battery_status.set_valign("end")
            self.battery_percent.set_valign("start")
            self.battery_percent.set_halign("center")

            self.battery_box.set_size_request(26, 40)
        else:
            self.container.set_halign("center")
            self.container.set_valign("center")
            self.container.set_hexpand(False)
            self.container.set_vexpand(False)
            self.battery_status.set_halign("end")
            self.battery_status.set_valign("center")
            self.battery_percent.set_valign("center")
            self.battery_percent.set_halign("center")

            self.battery_box.set_size_request(50, 26)

        self._update_ui()

    def _update_ui(self, *args):
        if self.battery and self.battery.available:
            percentage = int(self.battery.percent)

            if self.battery.charging:
                status = "bolt"
            elif self.battery.percent == 100:
                status = "battery_android_full"
            elif self.battery.percent >= 96:
                status = "battery_android_6"
            elif self.battery.percent >= 81:
                status = "battery_android_5"
            elif self.battery.percent >= 61:
                status = "battery_android_4"
            elif self.battery.percent >= 41:
                status = "battery_android_3"
            elif self.battery.percent >= 26:
                status = "battery_android_2"
            elif self.battery.percent >= 11:
                status = "battery_android_1"
            elif self.battery.percent >= 0:
                status = "battery_android_0"
            else:
                status = "battery_android_question"

            if user_settings.interface.bar.vertical:
                format_string = f"{percentage}"
                self.battery_fill.set_vexpand(True)
                self.battery_fill.set_valign("end")
                self.battery_fill.set_height_request(int(40 * percentage / 100))
                self.battery_fill.set_width_request(26)
            else:
                format_string = f"{percentage}%"
                self.battery_fill.set_hexpand(True)
                self.battery_fill.set_halign("start")
                self.battery_fill.set_height_request(26)
                self.battery_fill.set_width_request(int(50 * percentage / 100))

            self.battery_percent.set_label(f"{format_string}")
            self.battery_status.set_label(status)
            self.container.set_visible(True)

            if self.battery.charging:
                self.container.add_css_class("charging")
            else:
                self.container.remove_css_class("charging")

            if percentage <= 20:
                self.container.add_css_class("low")
            else:
                self.container.remove_css_class("low")
        else:
            self.container.set_visible(False)

    def widget(self):
        return self.container

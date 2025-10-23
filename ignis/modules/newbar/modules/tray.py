from ignis import utils, widgets
from ignis.gobject import IgnisProperty
from ignis.services.network import NetworkService
from ignis.services.bluetooth import BluetoothService
from ignis.services.audio import AudioService
from ignis.services.upower import UPowerService
from ignis.base_widget import BaseWidget
from gi.repository import Gtk
import modules.m3components as m3

class Battery(widgets.Box, BaseWidget):
    __gtype_name__ = "ExoBattery"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        widgets.Box.__init__(self, spacing=5, css_classes=["battery"], hexpand=False, halign="center", vexpand=False, valign="center")
        self._vertical: bool = False
        self.upowerservice = UPowerService.get_default()
        self.battery = None
        self.connected_signals = False

        self.battery_percent = widgets.Label(css_classes=["percent"])
        self.battery_status = m3.Icon(size=12, css_classes=["status"])
        self.battery_fill = widgets.Box(css_classes=["fill"])

        self.text_container = widgets.Box(
            spacing=2, halign="center", valign="center", homogeneous=False
        )
        self.text_container.append(self.battery_status)
        self.text_container.append(self.battery_percent)

        self.battery_box = widgets.Overlay(
            child=self.battery_fill,
            overlays=[self.text_container],
            css_classes=["battery-box"],
            hexpand=False,
            vexpand=False,
            halign="center",
            valign="center"
        )
        self.set_overflow(Gtk.Overflow.HIDDEN)

        self.append(self.battery_box)

        self.upowerservice.connect("notify::batteries", self.on_batteries_changed)
        self.upowerservice.connect("notify::devices", self.on_batteries_changed)
        BaseWidget.__init__(self, **kwargs)

    @IgnisProperty
    def vertical(self) -> bool:
        return self._vertical

    @vertical.setter
    def vertical(self, value: bool) -> None:
        self._vertical = value
        self.update_layout()

    def on_batteries_changed(self, service, prop):
        if self.upowerservice.batteries:
            self.battery = self.upowerservice.batteries[0]
            if not self.connected_signals:
                self.battery.connect("notify::percent", self.update_info)
                self.battery.connect("notify::charging", self.update_info)
                self.battery.connect("notify::icon-name", self.update_info)
                self.connected_signals = True

            self.update_info()
        else:
            self.battery = None
            self.connected_signals = False
            self.update_info()

    def update_layout(self):
        if self._vertical:
            self.battery_box.set_size_request(24, 40)
        else:
            self.battery_box.set_size_request(40, 20)

        self.update_info()

    def update_info(self, *args):
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

            if self._vertical:
                format_string = f"{percentage}"
                self.battery_status.set_visible(True)
                self.text_container.set_vertical(True)
                self.battery_fill.set_vexpand(True)
                self.battery_fill.set_hexpand(False)
                self.battery_fill.set_valign("end")
                self.battery_fill.set_halign("fill")
                self.battery_fill.set_height_request(int(40 * percentage / 100))
                self.battery_fill.set_width_request(24)
            else:
                format_string = f"{percentage}%"
                self.battery_status.set_visible(True if self.battery.charging else False)
                self.text_container.set_vertical(False)
                self.battery_fill.set_hexpand(True)
                self.battery_fill.set_vexpand(False)
                self.battery_fill.set_halign("start")
                self.battery_fill.set_valign("fill")
                self.battery_fill.set_height_request(20)
                self.battery_fill.set_width_request(int(40 * percentage / 100))

            self.battery_percent.set_label(format_string)
            self.battery_status.set_icon(status)
            self.set_visible(True)

            if percentage == 100:
                self.add_css_class("full")
            else:
                self.remove_css_class("full")

            if self.battery.charging:
                self.add_css_class("charging")
            else:
                self.remove_css_class("charging")

            if percentage <= 20:
                self.add_css_class("low")
            else:
                self.remove_css_class("low")
        else:
            self.set_visible(False)

class Tray(Gtk.Box, BaseWidget):
    __gtype_name__ = "ExoTray"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, spacing=10)
        self._vertical: bool = False
        self.network = NetworkService.get_default()
        self.bluetooth = BluetoothService.get_default()
        self.audio = AudioService.get_default()

        self.network_icon = m3.Icon(size=14, visible=False)
        self.bluetooth_icon = m3.Icon(size=14, visible=False)
        self.audio_icon = m3.Icon(size=14, visible=False)
        self.battery = Battery(vertical=self._vertical)

        scroll_controller = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.VERTICAL)
        scroll_controller.connect("scroll", self.audio_scroll)
        self.audio_icon.add_controller(scroll_controller)

        self.append(self.network_icon)
        self.append(self.bluetooth_icon)
        self.append(self.audio_icon)
        self.append(self.battery)

        self.network.wifi.connect("notify::is-connected", self.update_network_icon)
        self.network.ethernet.connect("notify::is-connected", self.update_network_icon)

        self.bluetooth.connect("notify::powered", self.update_bluetooth_icon)
        self.bluetooth.connect("notify::connected_devices", self.update_bluetooth_icon)
        self.bluetooth.connect("notify::devices", self.update_bluetooth_icon)

        if self.audio.speaker:
            self.audio.speaker.connect("notify::volume", self.update_audio_icon)
            self.audio.speaker.connect("notify::is-muted", self.update_audio_icon)

        self.add_css_class("exo-tray")
        BaseWidget.__init__(self, **kwargs)

    @IgnisProperty
    def vertical(self) -> bool:
        return self._vertical

    @vertical.setter
    def vertical(self, value: bool) -> None:
        if self._vertical == value:
            return
        self._vertical = value
        self.set_orientation(Gtk.Orientation.VERTICAL if value else Gtk.Orientation.HORIZONTAL)
        self.battery.set_vertical(value)

    def update_network_icon(self, *args):
        wifi = self.network.wifi
        ethernet = self.network.ethernet
        if ethernet.is_connected:
            self.network_icon.set_visible(True)
            self.network_icon.set_icon("settings_ethernet")
        elif wifi.enabled:
            self.network_icon.set_visible(True)
            if wifi.devices and wifi.devices[0].ap:
                strength = wifi.devices[0].ap.strength
                if strength >= 75:
                    icon = "signal_wifi_4_bar"
                elif strength >= 50:
                    icon = "network_wifi_3_bar"
                elif strength >= 25:
                    icon = "network_wifi_2_bar"
                elif strength > 0:
                    icon = "network_wifi_1_bar"
                else:
                    icon = "signal_wifi_0_bar"
                self.network_icon.set_icon(icon)
            else:
                self.network_icon.set_icon("signal_wifi_off")
        else:
            self.wifi.set_visible(False)

    def update_bluetooth_icon(self, *args):
        found_devices = self.bluetooth.devices
        if found_devices:
            self.bluetooth_icon.set_visible(True)
            if self.bluetooth.powered:
                if len(self.bluetooth.connected_devices) > 0:
                    self.bluetooth_icon.set_icon("bluetooth_connected")
                else:
                    self.bluetooth_icon.set_icon("bluetooth")
            else:
                self.bluetooth_icon.set_icon("bluetooth_disabled")
        else:
            self.bluetooth_icon.set_visible(False)

    def update_audio_icon(self, *args):
        if self.audio.speaker:
            self.audio_icon.set_visible(True)
            if self.audio.speaker.is_muted:
                self.audio_icon.set_icon("volume_off")
            else:
                if self.audio.speaker.volume < 33:
                    self.audio_icon.set_icon("volume_mute")
                elif self.audio.speaker.volume < 67:
                    self.audio_icon.set_icon("volume_down")
                else:
                    self.audio_icon.set_icon("volume_up")

    def audio_scroll(self, _, _dx, dy):
        if self.audio.speaker:
            current_volume = self.audio.speaker.volume
            new_volume = current_volume - (2 * dy)
            new_volume = max(0, min(100, new_volume))
            self.audio.speaker.volume = new_volume
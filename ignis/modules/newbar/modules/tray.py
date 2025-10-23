from ignis import utils, widgets
from ignis.services.network import NetworkService
from ignis.services.bluetooth import BluetoothService
from ignis.services.audio import AudioService
from ignis.base_widget import BaseWidget
from gi.repository import Gtk
import modules.m3components as m3

class Tray(widgets.Box, BaseWidget):
    __gtype_name__ = "ExoTray"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        widgets.Box.__init__(self, spacing=10)
        self.network = NetworkService.get_default()
        self.bluetooth = BluetoothService.get_default()
        self.audio = AudioService.get_default()

        self.network_icon = m3.Icon(size=14, visible=False)
        self.bluetooth_icon = m3.Icon(size=14, visible=False)
        self.audio_icon = m3.Icon(size=14, visible=False)

        scroll_controller = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.VERTICAL)
        scroll_controller.connect("scroll", self.audio_scroll)
        self.audio_icon.add_controller(scroll_controller)

        self.set_child([
            self.network_icon, self.bluetooth_icon, self.audio_icon
        ])

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
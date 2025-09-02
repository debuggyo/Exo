import asyncio
from ignis import widgets
from ignis.services.network import NetworkService
from ignis.services.bluetooth import BluetoothService
from ignis.services.audio import AudioService
from ignis.window_manager import WindowManager
from ignis import utils
from gi.repository import Gtk
from user_settings import user_settings
from .battery import Battery

window_manager = WindowManager.get_default()

class SystemInfoTray:
    def __init__(self):
        self.network_service = NetworkService.get_default()
        self.bluetooth_service = BluetoothService.get_default()
        self.audio_service = AudioService.get_default()

        self.battery_widget = Battery()

        self.container = widgets.Box(spacing=5, css_classes=["system-info-tray"])
        self.button = widgets.Button(child=self.container, css_classes=["system-info-tray-container"], on_click=lambda x: window_manager.toggle_window("QuickCenter"))

        self.wifi = widgets.Label(label=None, css_classes=["icon"])
        self.bluetooth = widgets.Label(label=None, css_classes=["icon"])

        self.audio_container = widgets.EventBox(
            on_right_click=self._toggle_audio_mute,
            on_middle_click=self._toggle_audio_mute,
            on_scroll_up=self._on_audio_scroll_up,
            on_scroll_down=self._on_audio_scroll_down,
            halign="center",
            valign="center"
        )
        self.audio = widgets.Label(label=None, halign="center", valign="fill", css_classes=["icon"])

        self.container.append(self.wifi)
        self.container.append(self.bluetooth)
        self.container.append(self.audio_container)
        self.audio_container.append(self.audio)

        self.container.append(self.battery_widget.widget())

        self.network_service.wifi.connect("notify::is-connected", self._update_ui)
        self.network_service.ethernet.connect("notify::is-connected", self._update_ui)
        self.network_service.vpn.connect("notify::is-connected", self._update_ui)

        self.bluetooth_service.connect("notify::powered", self._update_ui)
        self.bluetooth_service.connect("notify::connected-devices", self._update_ui)
        self.bluetooth_service.connect("notify::devices", self._update_ui)

        self.audio_service.speaker.connect("notify::is-muted", self._update_ui)
        self.audio_service.speaker.connect("notify::volume", self._update_ui)

        self.update_layout()

    def _toggle_audio_mute(self, widget=None):
        self.audio_service.speaker.is_muted = not self.audio_service.speaker.is_muted

    def _on_audio_scroll_up(self, widget):
        current_volume = self.audio_service.speaker.volume
        new_volume = current_volume + 5
        new_volume = max(0, min(100, new_volume))
        self.audio_service.speaker.volume = new_volume

    def _on_audio_scroll_down(self, widget):
        current_volume = self.audio_service.speaker.volume
        new_volume = current_volume - 5
        new_volume = max(0, min(100, new_volume))
        self.audio_service.speaker.volume = new_volume

    def update_layout(self):
        is_vertical = user_settings.interface.bar.vertical

        if is_vertical:
            self.container.set_halign("fill")
            self.container.set_valign("center")
            self.container.set_hexpand(True)
            self.container.set_vexpand(False)
            self.container.set_vertical(True)
        else:
            self.container.set_halign("center")
            self.container.set_valign("fill")
            self.container.set_hexpand(False)
            self.container.set_vexpand(True)
            self.container.set_vertical(False)

        self.battery_widget.update_layout()
        self._update_ui()

    def _update_ui(self, *args):
        network = self.network_service.wifi
        ethernet = self.network_service.ethernet
        if ethernet.is_connected:
            self.wifi.set_visible(True)
            self.wifi.set_label("settings_ethernet")
        elif network.enabled:
            self.wifi.set_visible(True)
            if network.is_connected and network.devices and network.devices[0].ap:
                strength = network.devices[0].ap.strength
                if strength >= 75:
                    self.wifi.set_label("signal_wifi_4_bar")
                elif strength >= 50:
                    self.wifi.set_label("network_wifi_3_bar")
                elif strength >= 25:
                    self.wifi.set_label("network_wifi_2_bar")
                elif strength > 0:
                    self.wifi.set_label("network_wifi_1_bar")
                else:
                    self.wifi.set_label("network_wifi_0_bar")
            else:
                self.wifi.set_label("signal_wifi_off")
        else:
            self.wifi.set_visible(False)

        found_devices = self.bluetooth_service.devices
        if found_devices:
            self.bluetooth.set_visible(True)
            if self.bluetooth_service.powered:
                if len(self.bluetooth_service.connected_devices) > 0:
                    self.bluetooth.set_label("bluetooth_connected")
                else:
                    self.bluetooth.set_label("bluetooth")
            else:
                self.bluetooth.set_label("bluetooth_disabled")
        else:
            self.bluetooth.set_visible(False)

        if self.audio_service.speaker.is_muted:
            self.audio.set_label("volume_off")
        else:
            if self.audio_service.speaker.volume < 33:
                self.audio.set_label("volume_mute")
            elif self.audio_service.speaker.volume < 67:
                self.audio.set_label("volume_down")
            else:
                self.audio.set_label("volume_up")

    def widget(self):
        return self.button

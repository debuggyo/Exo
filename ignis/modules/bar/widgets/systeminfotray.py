import asyncio
import datetime
from ignis import widgets, utils
from ignis.services.system_tray import SystemTrayService, SystemTrayItem
from ignis.services.network import NetworkService
from ignis.services.bluetooth import BluetoothService
from ignis.services.audio import AudioService
from ignis.window_manager import WindowManager
from gi.repository import Gtk
from user_settings import user_settings
from .battery import Battery

window_manager = WindowManager.get_default()
system_tray = SystemTrayService.get_default()


class TrayItem(widgets.Button):
    __gtype_name__ = "TrayItem"

    def __init__(self, item: SystemTrayItem, on_removed_callback=None):
        menu = None
        if item.menu:
            menu = item.menu.copy()
            menu.add_css_class("tray-menu")

        icon_box_children = [
            widgets.Icon(image=item.bind("icon"), pixel_size=16, css_classes=["tray-icon"])
        ]

        def on_item_removed(x):
            if on_removed_callback:
                on_removed_callback()
            self.unparent()

        super().__init__(
            child=widgets.Box(child=icon_box_children),
            tooltip_text=item.bind("tooltip"),
            on_click=lambda _: asyncio.create_task(item.activate_async()),
            setup=lambda self: item.connect("removed", on_item_removed),
            on_right_click=menu.popup if menu else None,
            css_classes=["tray-item", "unset"],
            halign="center",
            valign="center",
        )


class Tray(widgets.Box):
    __gtype_name__ = "Tray"

    def __init__(self):
        self.container = widgets.Box(
            css_classes=["tray"],
        )

        self.__setup()

    def __setup(self):
        self.update_layout()
        self.update_visibility()

        system_tray.connect("added", self.handle_added)

        for item in system_tray.items:
            self.container.append(TrayItem(item, on_removed_callback=self.handle_item_removed))

    def update_layout(self):
        is_vertical = user_settings.interface.bar.vertical

        self.container.set_vertical(is_vertical)

        if is_vertical:
            self.container.set_hexpand(False)
            self.container.set_vexpand(True)
            self.container.set_spacing(0)
        else:
            self.container.set_hexpand(True)
            self.container.set_vexpand(False)
            self.container.set_spacing(10)

    def update_visibility(self):
        self.container.set_visible(len(system_tray.items) > 0)

    def handle_added(self, _, item):
        self.container.append(TrayItem(item, on_removed_callback=self.handle_item_removed))
        self.update_visibility()

    def handle_item_removed(self):
        self.update_visibility()

    def widget(self):
        return self.container

class Clock:
    def __init__(self):
        self.container = widgets.Box(css_classes=["timedate"])
        self.time_label = widgets.Label(css_classes=["time"])
        self.date_label = widgets.Label(css_classes=["date"])

        self.container.append(self.time_label)
        self.container.append(self.date_label)

        utils.Poll(1000, lambda _: self.update_labels())

        self.update_layout()

    def update_labels(self):
        now = datetime.datetime.now()
        is_vertical = user_settings.interface.bar.vertical
        military_time = user_settings.interface.bar.modules.military_time

        if is_vertical:
            time_format = "%H" if military_time else "%I"
            date_format = "%M"
        else:
            if military_time:
                time_format = "%H:%M"
            else:
                time_format = "%I:%M %p"
            date_format = "%a %d %b"

        self.time_label.set_label(now.strftime(time_format))
        self.date_label.set_label(now.strftime(date_format))

    def update_layout(self):
        is_vertical = user_settings.interface.bar.vertical
        compact_mode = user_settings.interface.bar.density

        self.container.set_halign("fill")
        self.container.set_valign("fill")

        self.container.set_vertical(is_vertical)
        if is_vertical:
            self.container.set_hexpand(True)
            self.container.set_vexpand(True)
        else:
            self.container.set_hexpand(True)
            self.container.set_vexpand(True)

        if is_vertical:
            self.date_label.set_visible(True)
            self.container.set_spacing(0)
            self.container.set_homogeneous(True)
            self.time_label.set_valign("center")

        elif compact_mode == 0:
            self.date_label.set_visible(True)
            self.container.set_spacing(0)
            self.container.set_homogeneous(True)
            self.time_label.set_valign("end")
            self.date_label.set_valign("start")
            self.container.set_vertical(True)

        elif compact_mode == 1:
            self.date_label.set_visible(True)
            self.container.set_spacing(10)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")
            self.date_label.set_valign("center")
            self.container.set_vertical(False)

        elif compact_mode == 2:
            self.date_label.set_visible(True)
            self.container.set_spacing(6)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")
            self.date_label.set_valign("center")
            self.container.set_vertical(False)

        elif compact_mode == 3:
            self.date_label.set_visible(False)
            self.container.set_spacing(0)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")
            self.container.set_vertical(False)

    def widget(self):
        return self.container

class SystemInfoTray:
    def __init__(self):
        self.tray_widget = Tray()
        self.clock_widget = Clock()
        self.battery_widget = Battery()

        self.network_service = NetworkService.get_default()
        self.bluetooth_service = BluetoothService.get_default()
        self.audio_service = AudioService.get_default()

        self.container = widgets.Box(css_classes=["system-info-tray"])
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
        self.audio_container.append(self.audio)

        self.container.append(self.tray_widget.widget())
        self.container.append(self.wifi)
        self.container.append(self.bluetooth)
        self.container.append(self.audio_container)
        self.container.append(self.battery_widget.widget())
        self.container.append(self.clock_widget.widget())

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
            self.container.set_spacing(5)
            self.container.set_halign("fill")
            self.container.set_valign("center")
            self.container.set_hexpand(True)
            self.container.set_vexpand(False)
            self.container.set_vertical(True)
        else:
            self.container.set_spacing(10)
            self.container.set_halign("center")
            self.container.set_valign("fill")
            self.container.set_hexpand(False)
            self.container.set_vexpand(True)
            self.container.set_vertical(False)

        self.tray_widget.update_layout()
        self.clock_widget.update_layout()
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

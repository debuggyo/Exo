import asyncio
import subprocess
import os
from ignis import widgets
from ignis.services.network import NetworkService
from modules.m3components import Button
from modules.settings.widgets import CategoryLabel, SettingsRow, SwitchRow
from scripts import send_notification

class NetworkTab(widgets.Box):
    def __init__(self):
        super().__init__(
            vertical=True,
            spacing=20,
            css_classes=["settings-body"],
            hexpand=False,
            halign="center",
            width_request=800
        )

        self.network_service = NetworkService.get_default()

        self.network_category = self.create_network_category()

        self.append(self.network_category)

        self.append(SettingsRow(
            title="Open Network Settings",
            description="Open the network panel in the GNOME Settings application for advanced configuration.",
            child=[Button.button(
                icon="barefoot",
                label="Open Settings",
                on_click=lambda x: self._open_gnome_settings(),
            )]
        ))

        self.append(SettingsRow(
            title="Refresh Network Status",
            description="Manually refresh the status of all network connections.",
            child=[Button.button(
                icon="refresh",
                label="Refresh",
                on_click=lambda x: asyncio.create_task(self.update_ui()),
            )]
        ))

        self.network_service.wifi.connect("notify::enabled", self._on_property_changed)
        self.network_service.ethernet.connect("notify::is-connected", self._on_property_changed)

        asyncio.create_task(self.update_ui())

    def _on_property_changed(self, service, prop):
        asyncio.create_task(self.update_ui())

    async def update_ui(self):
        self.wifi_switch_row.active = self.network_service.wifi.enabled

        eth_connected = self.network_service.ethernet.is_connected
        self.ethernet_status_label.label = "Connected" if eth_connected else "Disconnected"
        self.ethernet_status_label.set_css_classes(["status-label", "connected" if eth_connected else "disconnected"])

        wifi_service = self.network_service.wifi

        for child in list(self.wifi_list_box.child):
            self.wifi_list_box.remove(child)

        if wifi_service.enabled:
            found_aps = []
            for device in wifi_service.devices:
                await device.scan()
                found_aps.extend(device.access_points)

            if not found_aps:
                self.wifi_list_box.append(widgets.Label(label="No networks found.", halign="center", vexpand=True, css_classes=["no-networks-label"]))
            else:
                for ap in found_aps:
                    self.wifi_list_box.append(self.create_access_point_row(ap))
        else:
            self.wifi_list_box.append(widgets.Label(label="Wi-Fi is disabled.", halign="center", vexpand=True))

    def _open_gnome_settings(self):
        try:
            env = os.environ.copy()
            env["XDG_CURRENT_DESKTOP"] = "GNOME"
            subprocess.Popen(["gnome-control-center", "network"], env=env)
        except FileNotFoundError:
            send_notification("Error", "GNOME Control Center not found.")

    def _get_wifi_icon_name(self, ap):
        is_secured = ap.security != ''
        strength = ap.strength

        if strength > 75:
            base_name = "network_wifi_3_bar"
        elif strength > 50:
            base_name = "network_wifi_2_bar"
        elif strength > 25:
            base_name = "network_wifi_1_bar"
        else:
            base_name = "network_wifi"

        if is_secured:
            return f"{base_name}_locked"
        else:
            return base_name

    async def _connect_wifi_and_refresh(self, ap):
        await ap.connect_to_graphical()
        await self.update_ui()

    async def _disconnect_wifi_and_refresh(self, ap):
        await ap.disconnect_from()
        await self.update_ui()

    def create_access_point_row(self, ap):
        row_content = widgets.Box(spacing=10, halign="fill", hexpand=True)

        icon_name = self._get_wifi_icon_name(ap)

        icon = widgets.Label(
            label=icon_name,
            css_classes=["material-symbols", "icon-label"],
            margin_start=10
        )
        ssid_label = widgets.Label(label=ap.ssid, hexpand=True, halign="start")
        row_content.append(icon)
        row_content.append(ssid_label)

        if ap.is_connected:
            row_content.append(widgets.Label(label="Connected", css_classes=["connected-status-label"]))
            row_button = widgets.Button(
                on_click=lambda *_: asyncio.create_task(self._disconnect_wifi_and_refresh(ap)),
                child=row_content,
                css_classes=["network-row"],
            )
        else:
            row_button = widgets.Button(
                on_click=lambda *_: asyncio.create_task(self._connect_wifi_and_refresh(ap)),
                child=row_content,
                css_classes=["network-row"],
            )

        return row_button

    def create_network_category(self):
        box = widgets.Box(css_classes=["settings-category"], vertical=True, spacing=2)
        box.append(CategoryLabel("Wi-Fi & Ethernet"))

        self.wifi_switch_row = SwitchRow(
            label="Wi-Fi",
            description="Toggle Wi-Fi on or off.",
            active=self.network_service.wifi.enabled,
            on_change=lambda x, active: setattr(self.network_service.wifi, 'enabled', active)
        )
        box.append(self.wifi_switch_row)

        self.wifi_list_box = widgets.Box(vertical=True, spacing=5, css_classes=["network-list-container"])
        box.append(SettingsRow(
            title="Available Networks",
            description="Select a network to connect.",
            child=[self.wifi_list_box]
        ))

        self.ethernet_status_label = widgets.Label(label="", css_classes=["status-label"])
        box.append(SettingsRow(
            title="Ethernet Status",
            description="Status of your Ethernet connection.",
            child=[self.ethernet_status_label]
        ))

        return box

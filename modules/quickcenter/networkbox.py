import asyncio
from ignis import widgets
from ignis.services.network import NetworkService
from modules.m3components import Button

class NetworkBox(widgets.Box):
    def __init__(self):
        self.wifi_list_box = widgets.Box(vertical=True, spacing=2, css_classes=["network-row-container"])
        self.ethernet_status_label = widgets.Label(label="", css_classes=["status-label"])
        
        super().__init__(
            css_classes=["network-box"],
            vertical=True,
            spacing=10,
            margin_top=10,
            margin_bottom=10,
            child=[
                self.create_network_section("Wi-Fi", self.wifi_list_box),
                self.create_network_section("Ethernet", self.ethernet_status_label),
                widgets.Box(vexpand=True),
                Button.button(
                    label="Refresh",
                    on_click=lambda x: asyncio.create_task(self.update_network_status()),
                    css_classes=["refresh-button"],
                )
            ]
        )
        
        asyncio.create_task(self.update_network_status())

    def create_network_section(self, title, child_widget):
        box = widgets.Box(vertical=True, spacing=5, css_classes=["network-section"])
        header = widgets.Label(label=title, halign="start", css_classes=["section-header"])
        box.append(header)
        box.append(child_widget)
        return box

    async def update_network_status(self):
        network_service = NetworkService.get_default()
        wifi_service = network_service.wifi
        ethernet_service = network_service.ethernet
        
        for child in list(self.wifi_list_box.child):
            self.wifi_list_box.remove(child)
            
        if wifi_service.enabled:
            found_aps = []
            for device in wifi_service.devices:
                await device.scan()
                found_aps.extend(device.access_points)
            
            if not found_aps:
                self.wifi_list_box.append(widgets.Label(label="No networks found.", halign="center", valign="center", vexpand=True, css_classes=["no-networks-label"]))
            else:
                for ap in found_aps:
                    self.wifi_list_box.append(self.create_access_point_row(ap))
        else:
            self.wifi_list_box.append(widgets.Label(label="Wi-Fi is disabled.", halign="center", valign="center", vexpand=True))

        eth_connected = ethernet_service.is_connected
        self.ethernet_status_label.label = "Connected" if eth_connected else "Disconnected"
        self.ethernet_status_label.set_css_classes(["status-label", "connected" if eth_connected else "disconnected"])

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
        await self.update_network_status()

    async def _disconnect_wifi_and_refresh(self, ap):
        await ap.disconnect_from()
        await self.update_network_status()

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
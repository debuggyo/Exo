import asyncio
from ignis import widgets
from ignis.services.bluetooth import BluetoothService
from modules.m3components import Button

class BluetoothBox(widgets.Box):
    def __init__(self):
        self.bluetooth_service = BluetoothService.get_default()
        
        # Check if the Bluetooth adapter is absent
        if self.bluetooth_service.state == "absent":
            super().__init__(
                css_classes=["network-box"],
                vertical=True,
                spacing=10,
                margin_top=10,
                margin_bottom=10,
                child=[
                    widgets.Label(label="No Bluetooth Found", halign="center", vexpand=True)
                ]
            )
            return

        # If Bluetooth is found, proceed with normal setup
        self.adapter_box = widgets.Box(spacing=10)
        self.device_list_box = widgets.Box(vertical=True, spacing=2, css_classes=["network-row-container"])

        super().__init__(
            css_classes=["network-box"],
            vertical=True,
            spacing=10,
            margin_top=10,
            margin_bottom=10,
            child=[
                self.create_adapter_section("Bluetooth", self.adapter_box),
                self.create_device_section("Devices", self.device_list_box),
                widgets.Box(vexpand=True),
                Button.button(
                    label="Refresh",
                    on_click=lambda x: asyncio.create_task(self.update_ui()),
                    css_classes=["refresh-button"],
                )
            ]
        )
        
        # Connect to service signals
        self.bluetooth_service.connect("notify::powered", self._on_property_changed)
        self.bluetooth_service.connect("device-added", self._on_device_changed)
        
        asyncio.create_task(self.update_ui())

    def create_adapter_section(self, title, child_widget):
        box = widgets.Box(vertical=True, spacing=5, css_classes=["network-section"])
        header = widgets.Label(label=title, halign="start", css_classes=["section-header"])
        box.append(header)
        
        self.bluetooth_switch = widgets.Switch(active=self.bluetooth_service.powered, margin_end=10, halign="end")
        self.bluetooth_switch.connect("state-set", self._on_switch_toggled)

        row = widgets.Box(spacing=10)
        row.append(widgets.Label(label="Bluetooth", halign="start", hexpand=True))
        row.append(self.bluetooth_switch)
        box.append(row)
        
        return box
    
    def create_device_section(self, title, child_widget):
        box = widgets.Box(vertical=True, spacing=5, css_classes=["network-section"])
        header = widgets.Label(label=title, halign="start", css_classes=["section-header"])
        box.append(header)
        box.append(child_widget)
        return box

    def _on_property_changed(self, service, prop):
        self.bluetooth_switch.set_state(self.bluetooth_service.powered)
        asyncio.create_task(self.update_ui())
        
    def _on_device_changed(self, service, device):
        asyncio.create_task(self.update_ui())

    def _on_switch_toggled(self, switch, state):
        self.bluetooth_service.powered = state
        asyncio.create_task(self.update_ui())
        return False

    async def update_ui(self):
        self.bluetooth_switch.set_state(self.bluetooth_service.powered)
        
        for child in list(self.device_list_box.child):
            self.device_list_box.remove(child)

        if self.bluetooth_service.powered:
            found_devices = self.bluetooth_service.devices
            if not found_devices:
                self.device_list_box.append(widgets.Label(label="No devices found.", halign="center", vexpand=True, css_classes=["no-devices-label"]))
            else:
                for device in found_devices:
                    device_row = self.create_device_row(device)
                    self.device_list_box.append(device_row)
                    device.connect("removed", self._on_device_changed)
        else:
            self.device_list_box.append(widgets.Label(label="Bluetooth is off.", halign="center", vexpand=True))

    def create_device_row(self, device):
        row_content = widgets.Box(spacing=10, halign="fill", hexpand=True)
        
        icon = widgets.Label(
            label=device.icon_name,
            css_classes=["material-symbols", "icon-label"],
            margin_start=10
        )
        alias_label = widgets.Label(label=device.alias, hexpand=True, halign="start")
        
        row_content.append(icon)
        row_content.append(alias_label)
        
        if device.connected:
            row_content.append(widgets.Label(label="Connected", css_classes=["connected-status-label"]))
            button_handler = lambda *_: asyncio.create_task(device.disconnect_from())
        else:
            row_content.append(widgets.Label(label="Not Connected", css_classes=["status-label"]))
            button_handler = lambda *_: asyncio.create_task(device.connect_to())

        row_button = widgets.Button(
            on_click=button_handler,
            child=row_content,
            css_classes=["network-row"],
        )
        return row_button
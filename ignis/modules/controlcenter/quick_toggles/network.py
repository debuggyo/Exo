from ..quickcontrol import QuickControl
from ignis.services.network import NetworkService

class NetworkToggle(QuickControl):
    __gtype_name__ = "NetworkToggle"

    def __init__(self):
        self.network = NetworkService.get_default()
        self.wifi = self.network.wifi
        self.ethernet = self.network.ethernet

        super().__init__(
            icon="signal_wifi_4_bar",
            on_activate=lambda: self.wifi.set_enabled(True),
            on_deactivate=lambda: self.wifi.set_enabled(False),
            active=True
        )

        self.network.wifi.connect("notify::is-connected", self.do_update)
        self.network.ethernet.connect("notify::is-connected", self.do_update)

    def do_update(self, *args):
        if self.ethernet.is_connected:
            self.set_icon("settings_ethernet")
        elif self.wifi.enabled:
            if self.wifi.devices and self.wifi.devices[0].ap:
                strength = self.wifi.devices[0].ap.strength
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
                if icon:
                    self.set_icon(icon)
            else:
                self.set_icon("signal_wifi_off")
        else:
            self.set_icon("signal_wifi_off")

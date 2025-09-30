from ignis import widgets
from modules.m3components import Button
from .tabs import (
    QuickTab,
    AppearanceTab,
    InterfaceTab,
    NetworkTab,
    BluetoothTab,
    AboutTab,
    ServicesTab,
)
from modules.m3components import NavigationRail
from ignis.app import IgnisApp


class Settings(widgets.RegularWindow):
    def __init__(self):
        self.reload_button = Button.button(
            icon="restart_alt",
            type="tonal",
            visible=True,
            shape="square",
            on_click=lambda x: IgnisApp.get_initialized().reload(),
            css_classes=["reload-button"],
            tooltip_text="Reload Exo",
        )

        self.content_scroll = widgets.Scroll(
            hexpand=True,
            halign="fill",
            child=QuickTab(),
        )

        self.tabs = {
            "quick": ("bolt", "Quick"),
            "appearance": ("palette", "Appearance"),
            "interface": ("tune", "Interface"),
            "services": ("api", "Services"),
            "network": ("network_wifi", "Network"),
            "bluetooth": ("bluetooth", "Bluetooth"),
            "about": ("info", "System"),
        }

        self.active_tab_label = widgets.Label(
            label="", css_classes=["active-tab-label"]
        )

        rail = NavigationRail(self.tabs, on_select=self.switch_tab, default="quick")
        rail.vexpand = True

        rail.append(widgets.Box(vexpand=True))
        rail.append(self.reload_button)

        super().__init__(
            css_classes=["settings-window"],
            default_width=1200,
            default_height=900,
            hide_on_close=True,
            visible=False,
            title="Exo Settings",
            namespace="Settings",
            child=widgets.Box(
                vertical=True,
                vexpand=True,
                valign="fill",
                child=[
                    widgets.Box(
                        css_classes=["header-bar"],
                        spacing=5,
                        child=[
                            widgets.Label(
                                label="settings", css_classes=["header-title-icon"]
                            ),
                            widgets.Label(
                                label="Exo Settings", css_classes=["header-title"]
                            ),
                            widgets.Label(
                                label=">", css_classes=["breadcrumb-separator"]
                            ),
                            self.active_tab_label,
                        ],
                    ),
                    widgets.Box(
                        vexpand=True,
                        child=[
                            rail,
                            self.content_scroll,
                        ],
                    ),
                ],
            ),
        )

    def switch_tab(self, key):
        self.active_tab_label.label = self.tabs[key][1]

        if key == "quick":
            self.content_scroll.set_child(QuickTab())
        elif key == "appearance":
            self.content_scroll.set_child(AppearanceTab())
        elif key == "interface":
            self.content_scroll.set_child(InterfaceTab())
        elif key == "services":
            self.content_scroll.set_child(ServicesTab())
        elif key == "network":
            self.content_scroll.set_child(NetworkTab())
        elif key == "bluetooth":
            self.content_scroll.set_child(BluetoothTab())
        elif key == "about":
            self.content_scroll.set_child(AboutTab())

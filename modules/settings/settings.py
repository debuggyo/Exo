from ignis import widgets
from modules.m3components import Button
from user_settings import user_settings
from .tabs import (
    AppearanceTab,
    InterfaceTab,
    NiriTab,
    HyprlandTab,
    AboutTab,
)
from ignis.app import IgnisApp


class NavigationRail(widgets.Box):
    def __init__(self, tabs, on_select, default="appearance"):
        super().__init__(css_classes=["navigation-rail"], vertical=True, spacing=5)
        self.on_select = on_select
        self.buttons = {}

        for key, (icon, label) in tabs.items():
            btn = Button.button(
                icon=icon,
                label=label,
                ialign="center",
                valign="center",
                css_classes=["rail-button"],
                vertical=True,
                on_click=lambda *_, key=key: self.select(key),
            )
            self.buttons[key] = btn
            self.append(btn)

        self.select(default)

    def select(self, key):
        for name, btn in self.buttons.items():
            if name == key:
                btn.add_css_class("selected")
            else:
                btn.remove_css_class("selected")
        self.on_select(key)


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
            child=AppearanceTab(),
        )

        self.tabs = {
            "appearance": ("palette", "Appearance"),
            "interface": ("tune", "Interface"),
            "niri": ("settings", "Niri"),
            "hyprland": ("settings", "Hyprland"),
            "about": ("info", "System"),
        }

        self.active_tab_label = widgets.Label(
            label="",
            css_classes=["active-tab-label"]
        )

        rail = NavigationRail(self.tabs, on_select=self.switch_tab, default="appearance")
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
                            widgets.Label(label="settings", css_classes=["header-title-icon"]),
                            widgets.Label(label="Exo Settings", css_classes=["header-title"]),
                            widgets.Label(label=">", css_classes=["breadcrumb-separator"]),
                            self.active_tab_label,
                        ]
                    ),
                    widgets.Box(
                        vexpand=True,
                        child=[
                            rail,
                            self.content_scroll,
                        ]
                    )
                ]
            ),
        )

    def switch_tab(self, key):
        self.active_tab_label.label = self.tabs[key][1]
        
        if key == "appearance":
            self.content_scroll.set_child(AppearanceTab())
        elif key == "interface":
            self.content_scroll.set_child(InterfaceTab())
        elif key == "niri":
            self.content_scroll.set_child(NiriTab())
        elif key == "hyprland":
            self.content_scroll.set_child(HyprlandTab())
        elif key == "about":
            self.content_scroll.set_child(AboutTab())
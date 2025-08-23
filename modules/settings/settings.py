# settings.py
from ignis import widgets
from modules.m3components import Button
from user_settings import user_settings
from .tabs import (
    AppearanceTab,
    NiriTab,
    HyprlandTab,
    AboutTab,
)
from ignis.app import IgnisApp


class NavigationRail(widgets.Box):
    def __init__(self, tabs, on_select, default="appearance", show_reload_button=None):
        super().__init__(css_classes=["navigation-rail"], vertical=True, spacing=5)
        self.on_select = on_select
        self.buttons = {}
        self.show_reload_button = show_reload_button

        # Add the "Settings" label to the top of the rail
        settings_label = widgets.Label(
            label="settings",
            css_classes=["settings-icon"],
            margin_top=10,
            margin_bottom=10,
            halign="center",
        )
        self.prepend(settings_label)

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
        # Create reload button in settings window
        self.reload_button = Button.button(
            css_classes=["reload-button"],
            icon="restart_alt",
            type="filled",
            visible=False,
            shape="square",
            on_click=lambda x: IgnisApp.get_initialized().reload()
        )

        def show_reload_button():
            self.reload_button.set_visible(True)

        # Create content area (default to appearance)
        self.content_scroll = widgets.Scroll(
            hexpand=True,
            halign="fill",
            child=AppearanceTab(show_reload_button),
        )

        # Define available tabs
        tabs = {
            "appearance": ("palette", "Appearance"),
            "niri": ("settings", "Niri"),
            "hyprland": ("settings", "Hyprland"),
            "about": ("info", "About"),
        }

        # Create rail
        rail = NavigationRail(tabs, on_select=self.switch_tab, default="appearance")

        # Append reload button to the rail
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
            resizable=False,
            child=widgets.Box(
                child=[
                    rail,
                    self.content_scroll,
                ]
            ),
        )

    def switch_tab(self, key):
        # Reset reload button visibility when switching tabs
        self.reload_button.set_visible(False)
        if key == "appearance":
            # Pass the show_reload_button callback to AppearanceTab
            self.content_scroll.set_child(AppearanceTab(lambda: self.reload_button.set_visible(True)))
        elif key == "niri":
            self.content_scroll.set_child(NiriTab())
        elif key == "hyprland":
            self.content_scroll.set_child(HyprlandTab())
        elif key == "about":
            self.content_scroll.set_child(AboutTab())
# quicktogglecenter.py
import os
import asyncio
from ignis import widgets, utils
from .quicktoggles import QuickToggle
from ignis.window_manager import WindowManager
from scripts import Wallpaper
from user_settings import user_settings
window_manager = WindowManager.get_default()

class QuickToggleCenter(widgets.Box):
    def open_gnome_settings(self):
        asyncio.create_task(utils.exec_sh_async("env XDG_CURRENT_DESKTOP=GNOME gnome-control-center"))
        window_manager.close_window("QuickCenter")

    def __init__(self, on_view_toggled):
        self.on_view_toggled = on_view_toggled
        super().__init__(
            css_classes=["quick-toggles-container"],
            halign="center",
            spacing=2,
            child=[
                QuickToggle("contrast", active=user_settings.appearance.wallcolors.dark_mode, on_click=lambda x: Wallpaper.setDarkMode(not user_settings.appearance.wallcolors.dark_mode), tooltip_text="Dark Mode"),
                # Add the new QuickToggle for the network view
                QuickToggle("network", on_click=lambda x: self.on_view_toggled(), tooltip_text="Network"),
                QuickToggle("more_horiz", on_click=lambda x: self.open_gnome_settings(), tooltip_text="Open GNOME Settings", label="Misc")
            ]
        )
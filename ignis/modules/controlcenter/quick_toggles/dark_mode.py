from ..quickcontrol import QuickControl
from scripts.wallpaper import Wallpaper
from user_settings import user_settings

class DarkModeToggle(QuickControl):
    __gtype_name__ = "DarkModeToggle"

    def __init__(self):
        super().__init__(
            icon="dark_mode",
            on_activate=lambda _: Wallpaper.setDarkMode(True),
            on_deactivate=lambda _: Wallpaper.setDarkMode(False),
            active=user_settings.appearance.wallcolors.bind("dark_mode")
        )

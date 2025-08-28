import os
from ignis import utils
from ignis.app import IgnisApp
from ignis.options_manager import OptionsGroup, OptionsManager, TrackedList
from ignis.window_manager import WindowManager
window_manager = WindowManager.get_default()
app = IgnisApp.get_initialized()

class UserSettings(OptionsManager):
    def __init__(self):
        super().__init__(file=os.path.expanduser("~/.config/ignis/user_settings.json"))

    class Appearance(OptionsGroup):
        # Wallpaper / Colours
        wallpaper_path: str = ""
        color_scheme: str = "tonal_spot"
        dark_mode: bool = True

        # Bar Styles
        bar_side: str = "top"
        vertical: bool = False
        compact: int = 0
        bar_corners: bool = True
        bar_floating: bool = False
        bar_separation: bool = False
        bar_centered: bool = False

        # Misc
        screen_corners: bool = True
        media_widget: bool = True

    appearance = Appearance()
    # appearance.connect_option("bar_side", app.reload)

user_settings = UserSettings()

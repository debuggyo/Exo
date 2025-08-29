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
        class WallpaperColors(OptionsGroup):
            # Wallpaper / Colours
            quickselect_path: str = ""
            wallpaper_path: str = ""
            color_scheme: str = "tonal_spot"
            dark_mode: bool = True

        wallcolors = WallpaperColors()

    class Interface(OptionsGroup):
        class Bar(OptionsGroup):
            side: str = "top"
            vertical: bool = False
            density: int = 0
            corners: bool = True
            floating: bool = False
            separation: bool = False
            centered: bool = False

            class Modules(OptionsGroup):
                media_widget: bool = True
                military_time: bool = False

            modules = Modules()

        class Notifications(OptionsGroup):
            anchor: list = []

        class Misc(OptionsGroup):
            screen_corners: bool = True

        bar = Bar()
        notifications = Notifications()
        misc = Misc()
    appearance = Appearance()
    interface = Interface()
user_settings = UserSettings()

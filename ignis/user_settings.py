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
            floating: bool = False
            separation: bool = False
            centered: bool = False

            class Modules(OptionsGroup):
                media_widget: bool = True
                military_time: bool = False
                recording_indicator: str = "recording"
                workspaces_style: str = "numbers"

            modules = Modules()

        class Dock(OptionsGroup):
            enabled: bool = False
            side: str = "bottom"
            vertical: bool = False
            floating: bool = True
            centered: bool = True
            size: int = 24

        class Notifications(OptionsGroup):
            anchor: list = ["top", "right"]

        class Misc(OptionsGroup):
            shell_corners: bool = True
            screen_corners: bool = True

        bar = Bar()
        dock = Dock()
        notifications = Notifications()
        misc = Misc()
    appearance = Appearance()
    interface = Interface()
user_settings = UserSettings()

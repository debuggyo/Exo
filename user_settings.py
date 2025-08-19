from ignis.app import IgnisApp
from ignis.options_manager import OptionsGroup, OptionsManager, TrackedList
from ignis.window_manager import WindowManager
window_manager = WindowManager.get_default()
app = IgnisApp.get_initialized()

class UserSettings(OptionsManager):
    def __init__(self):
        super().__init__(file="/home/debuggy/.config/ignis/user_settings.json")

    class Appearance(OptionsGroup):
        # Wallpaper / Colours
        wallpaper_path: str = "/home/debuggy/Pictures/Wallpapers/debuggycloud.png"
        color_scheme: str = "tonal_spot"
        dark_mode: bool = True

        # Bar Styles
        bar_side: str = "top"
        bar_anchors: TrackedList = TrackedList()
        bar_margins: TrackedList[int] = TrackedList([10, 10, 10, 10])  # top, left, right, bottom
        vertical: bool = False
        style: str = "floating"
        transparent: bool = False
        compact: int = 0

    appearance = Appearance()
    # appearance.connect_option("bar_side", app.reload)

user_settings = UserSettings()

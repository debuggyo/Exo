import os
from modules import (
    Bar,
    Corners,
    Settings,
    Launcher,
    PowerMenu,
    QuickCenter,
    M3Test,
    NotificationPopup,
    Dock
)
from ignis.css_manager import CssInfoPath, CssManager
from ignis import utils
from scripts import BarStyles, DockStyles, Wallpaper
from user_settings import user_settings

css_manager = CssManager.get_default()
css_manager.apply_css(
    CssInfoPath(
        name="main",
        path=os.path.expanduser("~/.config/ignis/styles/main.scss"),
        compiler_function=lambda path: utils.sass_compile(path=path)
    )
)
css_manager.apply_css(
    CssInfoPath(
        name="colors",
        path=os.path.expanduser("~/.config/ignis/colors.scss"),
        compiler_function=lambda path: utils.sass_compile(path=path)
    )
)

QuickCenter()
bar = Bar()
BarStyles.set_bar_instance(bar)
BarStyles._apply_css(bar.build())

dock = Dock()
DockStyles.set_dock_instance(dock)

DockStyles._apply_dock_css(dock.build())
if not user_settings.appearance.wallcolors.wallpaper_path:
    default_wallpaper_path = os.path.expanduser("~/Pictures/Wallpapers/default.png")
    if os.path.exists(default_wallpaper_path):
        print("No wallpaper set in user_settings, setting default wallpaper.")
        Wallpaper.setWall(default_wallpaper_path)
    else:
        print("No wallpaper set and default wallpaper file not found.")

if user_settings.interface.misc.screen_corners or user_settings.interface.bar.corners:
    Corners.build()
Settings()
Launcher()
PowerMenu()
M3Test()

for monitor in range(utils.get_n_monitors()):
    NotificationPopup(monitor)

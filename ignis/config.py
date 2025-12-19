import os

from ignis.command_manager import CommandManager
from ignis.css_manager import CssInfoPath, CssManager
from modules import (
    OSD,
    Bar,
    Corners,
    Launcher,
    M3Test,
    NotificationPopup,
    PowerMenu,
    QuickCenter,
    Settings,
)
from scripts import BarStyles, Wallpaper, auto_dark
from user_settings import user_settings

from ignis import utils

command_manager = CommandManager.get_default()

Wallpaper.generatePreviews()

css_manager = CssManager.get_default()
css_manager.widgets_style_priority = "user"
css_manager.apply_css(
    CssInfoPath(
        name="main",
        path=os.path.expanduser("~/.config/ignis/styles/main.scss"),
        compiler_function=lambda path: utils.sass_compile(path=path),
        priority="user",
    )
)
css_manager.apply_css(
    CssInfoPath(
        name="colors",
        path=os.path.expanduser("~/.config/ignis/colors.scss"),
        compiler_function=lambda path: utils.sass_compile(path=path),
        priority="user",
    )
)
if not user_settings.appearance.wallcolors.dark_mode:
    css_manager.apply_css(
        CssInfoPath(
            name="lightthemeoverrides",
            path=os.path.expanduser("~/.config/ignis/styles/lightthemeoverrides.scss"),
            compiler_function=lambda path: utils.sass_compile(path=path),
            priority="user",
        )
    )

QuickCenter()
bar = Bar()
BarStyles.set_bar_instance(bar)
BarStyles._apply_css(bar.build(), bar_id=0)
BarStyles._apply_css(bar.build2(), bar_id=1)

BarStyles.setFloating(user_settings.interface.bar.floating, bar_id=0)
BarStyles.setFloating(user_settings.interface.bar2.floating, bar_id=1)

if not user_settings.appearance.wallcolors.wallpaper_path:
    default_wallpaper_path = os.path.expanduser("~/Pictures/Wallpapers/default.png")
    if os.path.exists(default_wallpaper_path):
        print("No wallpaper set in user_settings, setting default wallpaper.")
        Wallpaper.setWall(default_wallpaper_path)
    else:
        print("No wallpaper set and default wallpaper file not found.")

if (
    user_settings.interface.misc.screen_corners
    or user_settings.interface.misc.shell_corners
):
    Corners.build()
Settings()
launcher = Launcher()
PowerMenu()
OSD()
M3Test()

NotificationPopup(0)

command_manager.add_command("toggle-launcher", lambda: launcher.toggle_window())

# Auto Dark Mode
utils.Poll(60000, lambda _: auto_dark())

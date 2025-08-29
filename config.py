import os
from modules import (
    Bar, 
    Corners, 
    Settings, 
    Launcher, 
    PowerMenu, 
    QuickCenter, 
    M3Test, 
    NotificationPopup
)
from ignis.css_manager import CssInfoPath, CssManager
from ignis import utils
from scripts import BarStyles
from scripts.apply_bar_css import apply_bar_css
from user_settings import user_settings

css_manager = CssManager.get_default()
css_manager.apply_css(
    CssInfoPath(
        name="main",
        path=os.path.expanduser("~/.config/ignis/style.scss"),
        compiler_function=lambda path: utils.sass_compile(path=path)
    )
)
css_manager.apply_css(
    CssInfoPath(
        name="bar",
        path=os.path.expanduser("~/.config/ignis/styles/bar.scss"),
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

bar = Bar()
BarStyles.set_bar_instance(bar)

apply_bar_css(bar.build())

if user_settings.interface.misc.screen_corners or user_settings.interface.bar.corners:
    Corners.build()
Settings()
Launcher()
PowerMenu()
QuickCenter()
M3Test()

for monitor in range(utils.get_n_monitors()):
    NotificationPopup(monitor)
import os
from modules import Bar, Settings, Launcher, PowerMenu, M3Test, NotificationPopup
from ignis.css_manager import CssInfoPath, CssManager
from ignis import utils
from scripts import set_bar_styles  # import the whole module

css_manager = CssManager.get_default()
css_manager.apply_css(
    CssInfoPath(
        name="main",
        path=os.path.expanduser("~/.config/ignis/style.scss"),
        compiler_function=lambda path: utils.sass_compile(path=path)
    )
)

# Create one global Bar and assign it to set_bar_styles.bar_instance
bar = Bar()  # removed monitor=0
set_bar_styles.bar_instance = bar
bar.build()

Settings()
Launcher()
PowerMenu()
M3Test()

for monitor in range(utils.get_n_monitors()):
    NotificationPopup(monitor)

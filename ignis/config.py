import os
from modules import (
    Bar,
    Corners,
    Settings,
    Launcher,
    PowerMenu,
    QuickCenter,
    OSD,
    M3Test,
    NotificationPopup,
)
from modules.newbar import Bar as NewBar
from ignis.css_manager import CssInfoPath, CssManager
from ignis import utils, widgets
from scripts import BarStyles, Wallpaper, auto_dark
from user_settings import user_settings

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
# bar = Bar()
# BarStyles.set_bar_instance(bar)
# BarStyles._apply_css(bar.build(), bar_id=0)
# BarStyles._apply_css(bar.build2(), bar_id=1)

# BarStyles.setFloating(user_settings.interface.bar.floating, bar_id=0)
# BarStyles.setFloating(user_settings.interface.bar2.floating, bar_id=1)

# if not user_settings.appearance.wallcolors.wallpaper_path:
#     default_wallpaper_path = os.path.expanduser("~/Pictures/Wallpapers/default.png")
#     if os.path.exists(default_wallpaper_path):
#         print("No wallpaper set in user_settings, setting default wallpaper.")
#         Wallpaper.setWall(default_wallpaper_path)
#     else:
#         print("No wallpaper set and default wallpaper file not found.")

if (
    user_settings.interface.misc.screen_corners
    or user_settings.interface.misc.shell_corners
):
    Corners.build()
Settings()
Launcher()
PowerMenu()
OSD()
M3Test()

NotificationPopup(0)


# Auto Dark Mode
utils.Poll(60000, lambda _: auto_dark())


newbar = NewBar(
    bar_options={
        "side": "bottom",
        "floating": False,
    },
    modules={
        "start": [
            {"ExampleLabel": {"label": "Start 1"}},
            {"ExampleLabel": {"label": "Start 2"}},
        ],
        "center": [
            {"ExampleLabel": {"label": "Center 3"}},
            {"ExampleLabel": {"label": "Center 4"}},
            {"ExampleButton": {"child": widgets.Label(label="Button")}},
        ],
        "end": [
            {"ExampleLabel": {"label": "End 5"}},
            {"ExampleLabel": {"label": "End 6"}},
        ],
    },
)
newbar.build()
newbar.bar_options = {
    "side": "top",
    "floating": False,
    "density": 0,
    "background": "gradient",
}
newbar.modules = {
    "center": [
        {"ExampleLabel": {"label": "Gradient Background!"}},
    ]
}

utils.Timeout(10000, newbar.rebuild)

newbar2 = NewBar(
    bar_id=1,
    bar_options={
        "side": "bottom",
        "floating": False,
    },
    modules={
        "start": [
            {"ExampleLabel": {"label": "Start 1"}},
        ],
        "center": [
            {"ExampleLabel": {"label": "Full"}},
        ],
        "end": [
            {"ExampleLabel": {"label": "Label"}},
            {"ExampleLabel": {"label": "Label"}},
            {"ExampleLabel": {"label": "Label"}},
            {"ExampleLabel": {"label": "Label"}},
            {"ExampleLabel": {"label": "Label"}},
        ],
    },
)
newbar2.build()

newbar3 = NewBar(
    bar_id=2,
    bar_options={"side": "bottom", "floating": True, "centered": True},
    modules={
        "start": [
            {"ExampleLabel": {"label": "Floating"}},
        ],
        "center": [
            {"ExampleLabel": {"label": "and"}},
        ],
        "end": [
            {"ExampleLabel": {"label": "Centered"}},
        ],
    },
)
newbar3.build()

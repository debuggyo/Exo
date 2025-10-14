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
from modules.newbar.modules import *
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
        path=os.path.join(utils.get_current_dir(), "styles/main.scss"),
        compiler_function=lambda path: utils.sass_compile(path=path),
        priority="user",
    )
)
css_manager.apply_css(
    CssInfoPath(
        name="colors",
        path=os.path.join(utils.get_current_dir(), "colors.scss"),
        compiler_function=lambda path: utils.sass_compile(path=path),
        priority="user",
    )
)
if not user_settings.appearance.wallcolors.dark_mode:
    css_manager.apply_css(
        CssInfoPath(
            name="lightthemeoverrides",
            path=os.path.join(utils.get_current_dir(), "styles/lightthemeoverrides.scss"),
            compiler_function=lambda path: utils.sass_compile(path=path),
            priority="user",
        )
    )

QuickCenter()
# bar = Bar()
# BarStyles.set_bar_instance(bar)
# BarStyles._apply_css(bar.build(), bar_id=0)
# BarStyles._apply_css(bar.build2(), bar_id=1)
# 
# BarStyles.setFloating(user_settings.interface.bar.floating, bar_id=0)
# BarStyles.setFloating(user_settings.interface.bar2.floating, bar_id=1)

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
Launcher()
PowerMenu()
OSD()
M3Test()

NotificationPopup(0)


# Auto Dark Mode
utils.Poll(60000, lambda _: auto_dark())

newbar = NewBar(
    start_modules=[
        Clock(),
        Clock(show_date=False)
    ],
    center_modules=[
        Clock()
    ]
)

# newbar.bar_options = {
#     "side": "left",
#     "floating": False,
#     "density": 0,
#     "background": "gradient",
# }
# newbar.modules = {
#     "start": [
#         {"ExampleLabel": {"label": "Start 1"}},
#         {"ExampleLabel": {"label": "Start 2"}},
#     ],
#     "center": [
#         {"ExampleLabel": {"label": "Gradient Background!"}},
#     ],
#     "end": [
#         {"ExampleLabel": {"label": "End 1"}},
#         {"ExampleLabel": {"label": "End 2"}},
#     ],
# }
# newbar.area_options = {"center": {"module_backgrounds": "none"}}
#
# utils.Timeout(10000, newbar.rebuild)
#
# newbar2 = NewBar(
#     bar_id=1,
#     bar_options={
#         "side": "bottom",
#         "floating": False,
#     },
#     area_options={
#         "start": {"module_backgrounds": "none"},
#         "center": {"module_backgrounds": "connected"},
#         "end": {"module_backgrounds": "separated"},
#     },
#     modules={
#         "start": [
#             {"ExampleLabel": {"label": "No Module Background"}},
#         ],
#         "center": [
#             {"ExampleLabel": {"label": "Connected"}},
#             {"ExampleLabel": {"label": "Module"}},
#             {"ExampleLabel": {"label": "Backgrounds"}},
#         ],
#         "end": [
#             {"ExampleLabel": {"label": "Separated"}},
#             {"ExampleLabel": {"label": "Module"}},
#             {"ExampleLabel": {"label": "Backgrounds"}},
#         ],
#     },
# )
#
# newbar4 = NewBar(
#     bar_id=3,
#     bar_options={
#         "side": "bottom",
#         "floating": False,
#         "centered": False,
#         "background": "areas",
#     },
#     area_options={
#         "start": {"module_backgrounds": "none", "area_background": False},
#         "center": {"module_backgrounds": "none"},
#         "end": {"module_backgrounds": True, "area_background": False},
#     },
#     modules={
#         "start": [
#             {"ExampleLabel": {"label": "This area should have no background"}},
#         ],
#         "center": [
#             {"ExampleLabel": {"label": "This one should"}},
#         ],
#         "end": [
#             {
#                 "ExampleLabel": {
#                     "label": "This one should only have a module background"
#                 }
#             },
#         ],
#     },
# )
#
# newbar3 = NewBar(
#     bar_id=2,
#     bar_options={
#         "side": "bottom",
#         "floating": True,
#         "centered": True,
#     },
#     area_options={
#         "center": {"module_backgrounds": "none"},
#     },
#     modules={
#         "start": [
#             {"ExampleLabel": {"label": "Floating"}},
#         ],
#         "center": [
#             {"ExampleLabel": {"label": "and"}},
#         ],
#         "end": [
#             {"ExampleLabel": {"label": "Centered"}},
#         ],
#     },
# )

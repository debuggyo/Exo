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
            path=os.path.join(
                utils.get_current_dir(), "styles/lightthemeoverrides.scss"
            ),
            compiler_function=lambda path: utils.sass_compile(path=path),
            priority="user",
        )
    )
if user_settings.appearance.wallcolors.transparency:
    css_manager.apply_css(
        CssInfoPath(
            name="transparency",
            path=os.path.join(utils.get_current_dir(), "styles/transparency.scss"),
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
    autohide=False,
    autohide_fullscreen=True,
    side="bottom",
    floating=True,
    centered=False,
    background="full",
    density=0,
    start_background=True,
    center_background=True,
    end_background=True,
    start_module_bg="none",
    center_module_bg="none",
    end_module_bg="none",
    start_modules=[Window(), Media(show_when_no_player=False)],
    center_modules=[
        Workspaces(
            workspace_style="impulse",
            fixed_workspaces=True,
            fixed_workspace_amount=5,
            icons=True,
            names=False,
            bigger_active=True,
        ),
    ],
    end_modules=[Layout(), Clock(), Tray()],
)

# workspaces = NewBar(
#     bar_id=1,
#     centered=True,
#     start_modules=[
#         Workspaces(
#             workspace_style="impulse"
#         ),
#         Workspaces(
#             numbers=True,
#         ),
#         Workspaces(
#             numbers=True,
#             names=False,
#         )
#     ],
#     center_modules=[
#         Workspaces(
#             icons=False,
#             numbers=True,
#         ),
#         Workspaces(
#             icons=False,
#             names=False,
#             numbers=True,
#         )
#     ],
#     end_modules=[
#         Workspaces(
#             workspace_style="dots"
#         )
#     ]
# )

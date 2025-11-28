import os
from modules import *
from modules.newbar import Bar as NewBar
from modules.newbar.modules import *
from ignis.css_manager import CssInfoPath, CssManager
from ignis import utils, widgets
from ignis.command_manager import CommandManager
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


# QuickCenter()
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

Settings()
background = Background()
launcher = Launcher()
control_center = ControlCenter()
PowerMenu()
OSD()

NotificationPopup(0)

# Auto Dark Mode
utils.Poll(60000, lambda _: auto_dark())

# Custom Commands
command_manager = CommandManager.get_default()
command_manager.add_command("toggle-launcher", lambda: launcher.toggle_window())
command_manager.add_command("toggle-control-center", lambda: control_center.toggle_window())

bar = NewBar(
    autohide=False,
    autohide_fullscreen=True,
    side="top",
    floating=False,
    centered=False,
    background="full",
    density=0,
    start_background=True,
    center_background=True,
    end_background=True,
    start_module_bg="none",
    center_module_bg="none",
    end_module_bg="none",
    start_modules=[Window(show_on_empty=False), Media(show_when_no_player=False)],
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
    end_modules=[
        Layout(show_on_single=False),
        RecordingIndicator(show_always=True),
        Clock(),
        Tray(),
    ],
)

if user_settings.interface.misc.screen_corners or user_settings.interface.misc.shell_corners:
    Corners.build()
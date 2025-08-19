from ignis import widgets
from ignis.app import IgnisApp
from modules.m3components import Button
from scripts import Wallpaper, BarStyles
from user_settings import user_settings
app = IgnisApp.get_initialized()

class CategoryLabel(widgets.Label):
    def __init__(self, title):
        super().__init__(
            css_classes=["settings-category-label"],
            label=title,
            justify="left",
            halign="start"
        )

def make_toggle_buttons(items, get_value, set_value):
    buttons = []

    def update_active():
        for btn, value in buttons:
            if get_value() == value:
                btn.add_css_class("active")
                btn.add_css_class("filled")
            else:
                btn.remove_css_class("active")
                btn.remove_css_class("filled")

    for item in items:
        if len(item) == 3:
            label, value, icon = item
        else:
            label, value = item
            icon = None

        btn = Button.button(
            label=label,
            icon=icon,
            on_click=lambda _, v=value: (set_value(v), update_active()),
            shape="square",
            hexpand=True,
            halign="fill"
        )
        buttons.append((btn, value))

    update_active()
    return Button.connected_group([b for b, _ in buttons], homogeneous=True)

class WallpaperCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=5,
            child=[
                CategoryLabel("󰸉  Wallpaper"),
                widgets.Picture(
                    height=400,
                    vexpand=False,
                    content_fit="cover",
                    css_classes=["wallpaper-preview"],
                    image=user_settings.appearance.bind("wallpaper_path")
                ),
                widgets.FileChooserButton(
                    css_classes=["file-chooser-button"],
                    dialog=widgets.FileDialog(
                        on_file_set=lambda self, file: Wallpaper.setWall(file.get_path()),
                        initial_path=user_settings.appearance.wallpaper_path,
                        filters=[
                            widgets.FileFilter(
                                mime_types=["image/jpeg", "image/png", "image/webp", "image/gif"],
                                default=True,
                                name="Images (PNG, JPG, WebP, GIF)",
                            )
                        ]
                    ),
                    label=widgets.Label(label='Select', ellipsize="end", max_width_chars=20)
                ),
                # Color schemes with icon
                make_toggle_buttons(
                    [
                        ("Content", "content", "palette"),
                        ("Expressive", "expressive", "auto_awesome"),
                        ("Fruit Salad", "fruit-salad", "grocery"),
                        ("Monochrome", "monochrome", "tonality"),
                        ("Neutral", "neutral", "gradient"),
                        ("Rainbow", "rainbow", "looks"),
                        ("Tonal Spot", "tonal-spot", "flare"),
                    ],
                    lambda: user_settings.appearance.color_scheme,
                    Wallpaper.setColors
                ),
                # Dark mode
                make_toggle_buttons(
                    [
                        ("Light", False, "light_mode"),
                        ("Dark", True, "dark_mode"),
                    ],
                    lambda: user_settings.appearance.dark_mode,
                    Wallpaper.setDarkMode
                )
            ]
        )

class BarStylesCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=5,
            child=[
                CategoryLabel("󰉼  Bar Styles"),
                # Bar side buttons
                make_toggle_buttons(
                    [
                        ("Top", "top", "align_vertical_top"),
                        ("Bottom", "bottom", "align_vertical_bottom"),
                        # Disabled temporarily.
                        # ("Left", "left", "align_horizontal_left"),
                        # ("Right", "right", "align_horizontal_right"),
                    ],
                    lambda: user_settings.appearance.bar_side,
                    BarStyles.setSide
                ),
                # Bar style buttons
                make_toggle_buttons(
                    [
                        ("Connected", "connected", "toolbar"),
                        ("Floating", "floating", "sliders"),
                        ("Trislands", "trislands", "more_horiz"),
                        ("Island", "island", "commit"),
                    ],
                    lambda: user_settings.appearance.style,  # change property if needed
                    BarStyles.setStyle
                ),
                make_toggle_buttons(
                    [
                        ("Default", 0, "expand"),
                        ("Compact", 1, "background_dot_large"),
                        ("Compact+", 2, "background_dot_small"),
                        ("Ultra Compact", 3, "background_grid_small"),
                    ],
                    lambda: user_settings.appearance.compact,
                    BarStyles.setCompact
                ),
                Button.button(
                    label="Reload",
                    on_click=lambda x: app.reload(),
                    type="filled",
                    halign="end"
                )
            ]
        )

class Settings(widgets.RegularWindow):
    def __init__(self):
        super().__init__(
            css_classes=["settings-window"],
            default_width=1200,
            default_height=900,
            hide_on_close=True,
            visible=False,
            title="Exo Settings",
            namespace="Settings",
            resizable=False,
            child=widgets.Scroll(
                child=widgets.Box(
                    vertical=True,
                    spacing=2,
                    child=[
                        WallpaperCategory(),
                        BarStylesCategory(),
                    ]
                )
            )
        )

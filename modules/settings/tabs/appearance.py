import os

from ignis import widgets
from modules.m3components import Button
from scripts import Wallpaper, BarStyles
from user_settings import user_settings
from ..widgets import CategoryLabel, make_toggle_buttons, SwitchRow, SettingsRow
from ignis.app import IgnisApp

app = IgnisApp.get_initialized()


class ColorCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=2,
            child=[
                CategoryLabel("Colors & Wallpaper"),
            ]
        )

        wallpaper_picture = widgets.Picture(
            height=400,
            vexpand=False,
            content_fit="cover",
            css_classes=["wallpaper-preview"],
            image=user_settings.appearance.bind("wallpaper_path")
        )

        wallpaper_filename_label = widgets.Label(
            label=os.path.basename(user_settings.appearance.wallpaper_path) or "Click to set wallpaper",
            halign="start",
            valign="end",
            margin_start=10,
            margin_bottom=10,
            css_classes=["wallpaper-filename-label"],
        )

        def on_file_set_handler(dialog, file):
            path = file.get_path()
            Wallpaper.setWall(path)
            wallpaper_filename_label.label = os.path.basename(path)

        file_chooser_button = widgets.FileChooserButton(
            label=widgets.Label(label=''),  # Keep this empty label to avoid an error
            css_classes=["wallpaper-button-overlay"],
            dialog=widgets.FileDialog(
                on_file_set=on_file_set_handler,
                initial_path=user_settings.appearance.wallpaper_path,
                filters=[
                    widgets.FileFilter(
                        mime_types=["image/jpeg", "image/png", "image/webp", "image/gif"],
                        default=True,
                        name="Images (PNG, JPG, WebP, GIF)",
                    )
                ]
            )
        )

        wallpaper_overlay = widgets.Overlay(
            css_classes=["wallpaper-overlay"],
            child=wallpaper_picture,
        )

        wallpaper_overlay.add_overlay(file_chooser_button)
        wallpaper_overlay.add_overlay(wallpaper_filename_label)

        self.append(SettingsRow(
            title="Wallpaper",
            child=[wallpaper_overlay]
        ))

        self.append(SettingsRow(
            title="Color Scheme",
            child=[
                make_toggle_buttons(
                    [
                        ("Content", "content"),
                        ("Expressive", "expressive"),
                        ("Fidelity", "fidelity"),
                        ("Fruit Salad", "fruit-salad"),
                        ("Monochrome", "monochrome"),
                        ("Neutral", "neutral"),
                        ("Rainbow", "rainbow"),
                        ("Tonal Spot", "tonal-spot"),
                    ],
                    lambda: user_settings.appearance.color_scheme,
                    Wallpaper.setColors
                )
            ]
        ))

        self.append(SettingsRow(
            title="Theme",
            child=[
                make_toggle_buttons(
                    [
                        ("Light", False, "light_mode"),
                        ("Dark", True, "dark_mode"),
                    ],
                    lambda: user_settings.appearance.dark_mode,
                    Wallpaper.setDarkMode
                )
            ]
        ))


class BarStylesCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=2,
        )

        self.append(CategoryLabel("Bar"))

        self.append(SettingsRow(
            title="Position",
            child=[
                make_toggle_buttons(
                    [
                        ("Top", "top", "align_vertical_top"),
                        ("Bottom", "bottom", "align_vertical_bottom"),
                        ("Left", "left", "align_horizontal_left"),
                        ("Right", "right", "align_horizontal_right"),
                    ],
                    lambda: user_settings.appearance.bar_side,
                    BarStyles.setSide,
                    on_any_click=None
                )
            ]
        ))

        # Bar compactness
        self.append(SettingsRow(
            title="Density",
            child=[
                make_toggle_buttons(
                    [
                        ("Default", 0, "expand"),
                        ("Compact", 1, "background_dot_large"),
                        ("Compact+", 2, "background_dot_small"),
                        ("Ultra Compact", 3, "background_grid_small"),
                    ],
                    lambda: user_settings.appearance.compact,
                    BarStyles.setCompact,
                    on_any_click=None
                )
            ]
        ))

        self.append(SwitchRow(
                label="Floating Bar",
                description="Make the bar float away from the edges of the screen.",
                active=user_settings.appearance.bar_floating,
                on_change=lambda x, active: BarStyles.setFloating(active)
            ))

        self.append(SwitchRow(
                label="Separated Islands",
                description="Seperate the bar into 3 separate 'islands'.",
                active=user_settings.appearance.bar_separation,
                on_change=lambda x, active: BarStyles.setSeparation(active)
            ))

        self.append(SwitchRow(
                label="Extend to Edges",
                description="Make the bar span the full width of the screen.",
                active=(not user_settings.appearance.bar_centered),
                on_change=lambda x, active: BarStyles.setBarCenter(not active)
            ))

        self.append(SwitchRow(
                label="Rounded Bar Corners",
                description="Add a curve outside the bar that warps around the screen.",
                active=user_settings.appearance.bar_corners,
                on_change=lambda x, active: BarStyles.setBarCorners(active)
            ))


class MiscCategory(widgets.Box):
    screen_corners = user_settings.appearance.screen_corners

    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=2,
            child=[
                CategoryLabel("Miscellaneous"),
                SwitchRow(
                    label="Rounded Screen Corners",
                    description="Add rounded corners to the screen.",
                    active=self.screen_corners,
                    on_change=lambda x, active: BarStyles.setScreenCorners(active)
                )
            ]
        )


class AppearanceTab(widgets.Box):

    def __init__(self):
        super().__init__(vertical=True, spacing=20, css_classes=["settings-body"], hexpand=False, halign="center", width_request=800)
        self.append(ColorCategory())
        self.append(BarStylesCategory())
        self.append(MiscCategory())
        self.hexpand = True
        self.vexpand = True
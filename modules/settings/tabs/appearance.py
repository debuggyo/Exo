# appearance.py
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
            spacing=5,
            child=[
                CategoryLabel("Colors"),
            ]
        )

        # Create the main image widget for the wallpaper preview
        wallpaper_picture = widgets.Picture(
            height=400,
            vexpand=False,
            content_fit="cover",
            css_classes=["wallpaper-preview"],
            image=user_settings.appearance.bind("wallpaper_path")
        )

        # Create a new, custom label to display the filename
        # This label will be positioned at the bottom-left of the image
        wallpaper_filename_label = widgets.Label(
            label=os.path.basename(user_settings.appearance.wallpaper_path) or "Click to set wallpaper",
            halign="start",  # Align to the left side of the overlay
            valign="end",    # Align to the bottom of the overlay
            margin_start=10,
            margin_bottom=10,
            css_classes=["wallpaper-filename-label"],
        )

        # This is the function that will be called when a file is selected
        def on_file_set_handler(dialog, file):
            path = file.get_path()
            Wallpaper.setWall(path)
            # Update our custom label with the new filename
            wallpaper_filename_label.label = os.path.basename(path)

        # Create the FileChooserButton with the dialog argument
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

        # The main Overlay widget that holds everything
        wallpaper_overlay = widgets.Overlay(
            css_classes=["wallpaper-overlay"],
            child=wallpaper_picture,
        )
        
        # Add the transparent button first, then add the label on top of it.
        wallpaper_overlay.add_overlay(file_chooser_button)
        wallpaper_overlay.add_overlay(wallpaper_filename_label)

        # Add the fully constructed wallpaper row to the settings category
        self.append(SettingsRow(
            title="Wallpaper",
            description="Choose your own wallpaper.",
            child=[wallpaper_overlay]
        ))

        self.append(SettingsRow(
            title="Color Schemes",
            description="Choose from 8 Material color schemes, in Light or Dark mode.",
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
                ),
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
    def __init__(self, show_reload_button):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=5,
        )

        self.append(CategoryLabel("Bar Styles"))

        # Bar side
        self.append(SettingsRow(
            title="Bar Side",
            description="Choose where the bar is anchored on screen.",
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
                    on_any_click=show_reload_button
                )
            ]
        ))

        # Bar style
        self.append(SettingsRow(
            title="Bar Style",
            description="Switch between different bar layouts.",
            child=[
                make_toggle_buttons(
                    [
                        ("Connected", "connected", "toolbar"),
                        ("Floating", "floating", "sliders"),
                        ("Trislands", "trislands", "more_horiz"),
                        ("Island", "island", "commit"),
                    ],
                    lambda: user_settings.appearance.style,
                    BarStyles.setStyle,
                    on_any_click=show_reload_button
                )
            ]
        ))

        # Bar compactness
        self.append(SettingsRow(
            title="Bar Size",
            description="Adjust how compact the bar looks.",
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
                    on_any_click=show_reload_button
                )
            ]
        ))

        # Bar corners (only if style is connected)
        if user_settings.appearance.style == "connected":
            self.append(SwitchRow(
                label="Bar Corners",
                description="Enable rounded corners coming out of the bar.",
                active=user_settings.appearance.bar_corners,
                on_change=lambda x, active: user_settings.appearance.set_bar_corners(active)
            ))


class MiscCategory(widgets.Box):
    screen_corners = user_settings.appearance.screen_corners

    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=5,
            child=[
                CategoryLabel("Miscellaneous"),
                SwitchRow(
                    label="Screen Corners",
                    description="Enable rounded corners for the screen.",
                    active=self.screen_corners,
                    on_change=lambda x, active: user_settings.appearance.set_screen_corners(active)
                )
            ]
        )


class AppearanceTab(widgets.Box):
    """Main tab with scrollable content."""
    def __init__(self, show_reload_button):
        super().__init__(vertical=True, spacing=2, css_classes=["settings-body"])
        self.append(ColorCategory())
        self.append(BarStylesCategory(show_reload_button))
        self.append(MiscCategory())
        self.hexpand = True
        self.vexpand = True
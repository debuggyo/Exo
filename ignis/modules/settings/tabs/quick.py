import os
import threading
from gi.repository import GLib, Gtk

from ignis import widgets
from scripts import Wallpaper, BarStyles
from user_settings import user_settings
from ..widgets import (
    CategoryLabel,
    SettingsRow,
    SwitchRow,
    make_toggle_buttons,
    make_independent_toggle_buttons,
)
from ignis.app import IgnisApp

app = IgnisApp.get_initialized()


class WallColorCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
            child=[
                CategoryLabel("Appearance", "palette"),
            ],
        )

        self.wallpaper_picture = widgets.Picture(
            height=300,
            width=560,
            halign="fill",
            hexpand=True,
            content_fit="cover",
            css_classes=["wallpaper-preview"],
            image=user_settings.appearance.wallcolors.bind("wallpaper_path"),
        )

        self.wallpaper_filename_label = widgets.Label(
            label=os.path.basename(user_settings.appearance.wallcolors.wallpaper_path)
            or "Click to set wallpaper",
            halign="start",
            valign="end",
            margin_start=10,
            margin_bottom=10,
            css_classes=["wallpaper-filename-label"],
        )

        def on_file_set_handler(dialog, file):
            path = file.get_path()
            self._set_and_update_wallpaper(path)

        file_chooser_button = widgets.FileChooserButton(
            label=widgets.Label(label=""),
            css_classes=["wallpaper-button-overlay"],
            dialog=widgets.FileDialog(
                on_file_set=on_file_set_handler,
                initial_path=user_settings.appearance.wallcolors.wallpaper_path,
                filters=[
                    widgets.FileFilter(
                        mime_types=[
                            "image/jpeg",
                            "image/png",
                            "image/webp",
                            "image/gif",
                        ],
                        default=True,
                        name="Images (PNG, JPG, WebP, GIF)",
                    )
                ],
            ),
        )

        wallpaper_overlay = widgets.Overlay(
            css_classes=["wallpaper-overlay"],
            child=self.wallpaper_picture,
            halign="fill",
            hexpand=True,
        )

        wallpaper_overlay.add_overlay(file_chooser_button)
        wallpaper_overlay.add_overlay(self.wallpaper_filename_label)

        self.palettes = [
            "content",
            "expressive",
            "fidelity",
            "fruit-salad",
            "monochrome",
            "neutral",
            "rainbow",
            "tonal-spot",
        ]

        palette_selector_row = widgets.Grid(
            column_spacing=5, row_spacing=5, css_classes=["palette-selector-row"]
        )

        self.palette_buttons = []

        def on_palette_selected(btn, palette_name):
            Wallpaper.setColors(palette_name)
            user_settings.appearance.wallcolors.color_scheme = palette_name
            self._update_palette_selection()

        def make_palette_button(palette_name):
            css_class = f"{palette_name}-preview"
            preview = widgets.Box(
                css_classes=["preview", css_class],
                vertical=True,
                height_request=50,
                width_request=50,
                halign="center",
                hexpand=False,
                valign="center",
                vexpand=False,
                tooltip_text=palette_name,
                child=[
                    widgets.Box(
                        css_classes=["primary"],
                        height_request=25,
                        width_request=50,
                        hexpand=False,
                        halign="start",
                    ),
                    widgets.Box(
                        vertical=False,
                        child=[
                            widgets.Box(
                                css_classes=["secondary"],
                                height_request=25,
                                width_request=25,
                            ),
                            widgets.Box(
                                css_classes=["tertiary"],
                                height_request=25,
                                width_request=25,
                            ),
                        ],
                    ),
                ],
            )

            btn = widgets.Button(
                on_click=lambda btn, p=palette_name: on_palette_selected(btn, p),
                css_classes=["palette-preview-btn"],
                hexpand=True,
                halign="fill",
                child=preview,
            )
            btn.palette_name = palette_name
            preview.set_overflow(Gtk.Overflow.HIDDEN)
            return btn

        for i, palette in enumerate(self.palettes):
            btn = make_palette_button(palette)
            self.palette_buttons.append(btn)
            palette_selector_row.attach(btn, i % 3, i // 3, 1, 1)

        theme_selector_row = widgets.Box(
            vertical=False,
            spacing=10,
            vexpand=True,
            valign="fill",
            css_classes=["theme-selector-row"],
        )

        self.theme_buttons = []

        def on_theme_selected(btn, is_dark):
            Wallpaper.setDarkMode(is_dark)
            user_settings.appearance.wallcolors.dark_mode = is_dark
            self._update_theme_selection()

        def make_theme_button(label, is_dark, css_class):
            icon = "dark_mode" if is_dark else "light_mode"
            btn = widgets.Button(
                on_click=lambda btn, val=is_dark: on_theme_selected(btn, val),
                hexpand=True,
                halign="fill",
                vexpand=True,
                valign="fill",
                child=widgets.Box(
                    vertical=True,
                    css_classes=[css_class],
                    hexpand=True,
                    halign="fill",
                    vexpand=True,
                    valign="fill",
                    child=[
                        widgets.Box(
                            vertical=True,
                            css_classes=["container"],
                            hexpand=True,
                            halign="fill",
                            vexpand=True,
                            valign="fill",
                            spacing=5,
                            child=[
                                widgets.Box(
                                    css_classes=["surface"],
                                    width_request=40,
                                    vexpand=True,
                                    valign="fill",
                                    child=[
                                        widgets.Box(
                                            halign="center",
                                            hexpand=True,
                                            valign="center",
                                            vexpand=True,
                                            spacing=2,
                                            child=[
                                                widgets.Label(
                                                    label=icon, css_classes=["icon"]
                                                ),
                                                widgets.Label(label=label),
                                            ],
                                        )
                                    ],
                                ),
                                widgets.Box(
                                    vertical=False,
                                    spacing=5,
                                    child=[
                                        widgets.Box(
                                            css_classes=["btn-1"],
                                            width_request=30,
                                            hexpand=True,
                                            halign="fill",
                                            height_request=30,
                                        ),
                                        widgets.Box(
                                            css_classes=["btn-2"],
                                            width_request=30,
                                            height_request=30,
                                        ),
                                        widgets.Box(
                                            css_classes=["btn-3"],
                                            width_request=30,
                                            height_request=30,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                css_classes=["theme-preview-btn"],
            )
            btn.is_dark = is_dark
            btn.set_overflow(Gtk.Overflow.HIDDEN)
            return btn

        light_btn = make_theme_button("Light", False, "light-preview")
        dark_btn = make_theme_button("Dark", True, "dark-preview")
        self.theme_buttons.extend([light_btn, dark_btn])
        theme_selector_row.append(light_btn)
        theme_selector_row.append(dark_btn)

        right_column = widgets.Box(vertical=True, spacing=10)
        right_column.append(theme_selector_row)
        right_column.append(palette_selector_row)

        top_section = widgets.Box(
            vertical=False, spacing=10, valign="center", halign="center"
        )
        top_section.append(wallpaper_overlay)
        top_section.append(right_column)

        self.append(top_section)

        self._update_palette_selection()
        self._update_theme_selection()

    def _update_palette_selection(self):
        selected_palette = user_settings.appearance.wallcolors.color_scheme
        for btn in self.palette_buttons:
            if btn.palette_name == selected_palette:
                btn.add_css_class("selected")
            else:
                btn.remove_css_class("selected")

    def _update_theme_selection(self):
        selected_dark = user_settings.appearance.wallcolors.dark_mode
        for btn in self.theme_buttons:
            if btn.is_dark == selected_dark:
                btn.add_css_class("selected")
            else:
                btn.remove_css_class("selected")

    def _set_and_update_wallpaper(self, path):
        if path:
            Wallpaper.setWall(path)
            self.wallpaper_picture.image = path
            self.wallpaper_filename_label.label = os.path.basename(path)

    def _on_thumbnail_clicked(self, path):
        self._set_and_update_wallpaper(path)
        self._update_selected_icons()


class BarCategory(widgets.Box):
    def __init__(self):
        bar = user_settings.interface.bar
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
        )

        self.append(CategoryLabel("Bar", "toolbar"))

        self.append(
            SettingsRow(
                title="Position",
                description="Pick a side for the bar to be located.",
                child=[
                    make_toggle_buttons(
                        [
                            ("Top", "top", "align_vertical_top"),
                            ("Bottom", "bottom", "align_vertical_bottom"),
                            ("Left", "left", "align_horizontal_left"),
                            ("Right", "right", "align_horizontal_right"),
                        ],
                        lambda: bar.side,
                        BarStyles.setSide,
                        on_any_click=None,
                    )
                ],
            )
        )
        self.append(widgets.Separator())

        self.append(
            SettingsRow(
                title="Density",
                description="Pick between 4 different density options.",
                child=[
                    make_toggle_buttons(
                        [
                            ("Cozy", 0, "density_large"),
                            ("Comfortable", 1, "density_medium"),
                            ("Compact", 2, "density_small"),
                            ("Condensed", 3, "list"),
                        ],
                        lambda: bar.density,
                        BarStyles.setCompact,
                        on_any_click=None,
                    )
                ],
            )
        )
        self.append(widgets.Separator())

        self.append(
            SettingsRow(
                title="Extra Modifiers",
                description="Add extra modifiers to the bar (You can select multiple).",
                child=[
                    make_independent_toggle_buttons(
                        [
                            (
                                "Floating",
                                bar.get_floating,
                                BarStyles.setFloating,
                                "page_header",
                            ),
                            (
                                "Separated",
                                bar.get_separation,
                                BarStyles.setSeparation,
                                "more_horiz",
                            ),
                            (
                                "Centered",
                                bar.get_centered,
                                BarStyles.setBarCenter,
                                "code",
                            ),
                        ]
                    )
                ],
            )
        )
        self.append(widgets.Separator())

        self.append(
            SettingsRow(
                title="Backgrounds",
                description="Add or remove the backgrounds of the Bar/Modules.",
                child=[
                    make_independent_toggle_buttons(
                        [
                            (
                                "Bar",
                                bar.get_bar_background,
                                BarStyles.setBarBackground,
                                "toolbar",
                            ),
                            (
                                "Modules",
                                bar.get_module_backgrounds,
                                BarStyles.setModuleBackgrounds,
                                "more_horiz",
                            ),
                        ]
                    )
                ],
            )
        )


class MiscCategory(widgets.Box):
    screen_corners = user_settings.interface.misc.screen_corners

    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
            child=[
                CategoryLabel("Miscellaneous", "more_horiz"),
                SwitchRow(
                    title="Rounded Shell Corners",
                    description="Add a curve outside the shell that warps around the screen.",
                    active=user_settings.interface.misc.shell_corners,
                    on_change=lambda x, active: BarStyles.setShellCorners(active),
                ),
                widgets.Separator(),
                SettingsRow(
                    title="Rounded Screen Corners",
                    description="Round the corners of the screen.",
                    child=[
                        make_toggle_buttons(
                            [
                                ("Disabled", "disabled", "close"),
                                (
                                    "When not fullscreen",
                                    "not_fullscreen",
                                    "fullscreen_exit",
                                ),
                                ("Always", "always", "check"),
                            ],
                            lambda: user_settings.interface.misc.screen_corners,
                            BarStyles.setScreenCorners,
                            on_any_click=None,
                        ),
                    ],
                ),
            ],
        )


class QuickTab(widgets.Box):
    def __init__(self):
        super().__init__(
            vertical=True,
            spacing=8,
            css_classes=["settings-body"],
            hexpand=False,
            halign="center",
            width_request=800,
        )
        self.append(WallColorCategory())
        self.append(BarCategory())
        self.append(MiscCategory())

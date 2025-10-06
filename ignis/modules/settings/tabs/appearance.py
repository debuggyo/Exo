import os
import threading
from gi.repository import GLib, Gtk, Pango

from ignis import widgets
from scripts import Wallpaper
from scripts.auto_dark import setAutoDark
from user_settings import user_settings
from ..widgets import CategoryLabel, SettingsRow, SwitchRow
from ignis.app import IgnisApp

app = IgnisApp.get_initialized()


class WallpaperCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
            child=[
                CategoryLabel("Wallpaper", "image"),
            ],
        )

        self.wallpaper_picture = widgets.Picture(
            height=300,
            width=560,
            vexpand=False,
            hexpand=False,
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
        )

        wallpaper_overlay.add_overlay(file_chooser_button)
        wallpaper_overlay.add_overlay(self.wallpaper_filename_label)

        self.append(wallpaper_overlay)

    def _set_and_update_wallpaper(self, path):
        if path:
            Wallpaper.setWall(path)
            self.wallpaper_picture.image = path
            self.wallpaper_filename_label.label = os.path.basename(path)


class ColorCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
            child=[
                CategoryLabel("Colors", "palette"),
            ],
        )

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

        palette_selector_row = widgets.Box(
            spacing=2, vertical=False, css_classes=["palette-selector-row"]
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

        for _, palette_name in enumerate(self.palettes):
            btn = make_palette_button(palette_name)
            self.palette_buttons.append(btn)
            palette_selector_row.append(btn)

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
                    height_request=100,
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

        self.append(
            SettingsRow(
                title="Themes",
                description="Set your theme.",
                vertical=True,
                child=[theme_selector_row],
                css_classes=["colors-row"],
            )
        )
        self.append(widgets.Separator())
        self.append(
            SwitchRow(
                title="Auto Dark",
                description="Automatically set the dark theme based on the time of day.",
                active=user_settings.appearance.wallcolors.auto_dark.enabled,
                on_change=lambda x, active: setAutoDark(active),
            )
        )
        self.append(widgets.Separator())
        self.append(
            SettingsRow(
                title="Start Time",
                description="Time of day to enable dark mode when Auto Dark is enabled.",
                child=[
                    widgets.SpinButton(
                        min=0,
                        max=24,
                        step=1,
                        value=user_settings.appearance.wallcolors.auto_dark.start_hour,
                        on_change=lambda _,
                        value: user_settings.appearance.wallcolors.auto_dark.set_start_hour(
                            value
                        ),
                    ),
                    widgets.SpinButton(
                        min=0,
                        max=60,
                        step=1,
                        value=user_settings.appearance.wallcolors.auto_dark.start_min,
                        on_change=lambda _,
                        value: user_settings.appearance.wallcolors.auto_dark.set_start_min(
                            value
                        ),
                    ),
                ],
            )
        )
        self.append(widgets.Separator())
        self.append(
            SettingsRow(
                title="End Time",
                description="Time of day to disable dark mode when Auto Dark is enabled.",
                child=[
                    widgets.SpinButton(
                        min=0,
                        max=24,
                        step=1,
                        value=user_settings.appearance.wallcolors.auto_dark.end_hour,
                        on_change=lambda _,
                        value: user_settings.appearance.wallcolors.auto_dark.set_end_hour(
                            int(value)
                        ),
                    ),
                    widgets.SpinButton(
                        min=0,
                        max=60,
                        step=1,
                        value=user_settings.appearance.wallcolors.auto_dark.end_min,
                        on_change=lambda _,
                        value: user_settings.appearance.wallcolors.auto_dark.set_end_min(
                            int(value)
                        ),
                    ),
                ],
            )
        )
        self.append(widgets.Separator())
        self.append(
            SettingsRow(
                title="Color Schemes",
                description="Set your color scheme.",
                vertical=True,
                child=[palette_selector_row],
                css_classes=["colors-row"],
            )
        )

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


class QuickSelectCategory(widgets.Box):
    def __init__(self, wallpaper_category_ref):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
            child=[
                CategoryLabel("Quick Select", "image"),
            ],
        )
        self.wallpaper_category_ref = wallpaper_category_ref

        self.thumbnail_overlays = []

        quick_select_container = widgets.Box(
            vertical=True, spacing=5, vexpand=True, valign="fill"
        )

        folder_chooser_button = widgets.FileChooserButton(
            label=widgets.Label(label="Select a Folder"),
            css_classes=["folder-chooser-button"],
            dialog=widgets.FileDialog(
                select_folder=True,
                initial_path=user_settings.appearance.wallcolors.quickselect_path,
                on_file_set=self._on_quickselect_folder_selected,
            ),
        )
        quick_select_container.append(folder_chooser_button)

        self.gallery_content_container = widgets.Box(
            vertical=True,
            halign="fill",
            hexpand=True,
            valign="fill",
            vexpand=True,
            css_classes=["wallpaper-gallery-container"],
        )
        quick_select_container.append(self.gallery_content_container)

        loading_label = widgets.Label(label="Loading wallpapers...")
        self.gallery_content_container.append(loading_label)

        self._find_and_create_gallery_async()

        self.append(quick_select_container)

    def _on_quickselect_folder_selected(self, dialog, file):
        path = file.get_path()
        if path:
            user_settings.appearance.wallcolors.set_quickselect_path(path)
            self._find_and_create_gallery_async()

    def _find_and_create_gallery_async(self):
        def do_find_and_build():
            wallpaper_dir = user_settings.appearance.wallcolors.quickselect_path
            if not wallpaper_dir or not os.path.isdir(
                os.path.expanduser(wallpaper_dir)
            ):
                wallpaper_dir = os.path.expanduser("~/Pictures/Wallpapers")

            if not os.path.isdir(wallpaper_dir):
                GLib.idle_add(self._replace_gallery_content, None)
                return

            supported_extensions = (".png", ".jpg", ".jpeg", ".gif")
            image_files = []
            try:
                with os.scandir(wallpaper_dir) as entries:
                    for entry in entries:
                        if entry.is_file() and entry.name.lower().endswith(
                            supported_extensions
                        ):
                            image_files.append(entry.path)
            except Exception:
                GLib.idle_add(self._replace_gallery_content, None)
                return

            image_files.sort()
            if not image_files:
                GLib.idle_add(self._replace_gallery_content, None)
                return

            gallery_grid = widgets.Grid(
                halign="fill",
                hexpand=True,
                column_spacing=5,
                row_spacing=5,
            )
            columns = 4
            temp_thumbnails = []
            current_path = user_settings.appearance.wallcolors.wallpaper_path

            for idx, file_path in enumerate(image_files):
                is_selected = file_path == current_path
                btn = widgets.Button(
                    on_click=lambda btn, path=file_path: (
                        self.wallpaper_category_ref._set_and_update_wallpaper(path),
                        self._update_selected_icons(),
                    ),
                    child=widgets.Picture(
                        image=file_path,
                        content_fit="cover",
                        height=100,
                        width=196,
                        hexpand=True,
                        halign="fill",
                        css_classes=["wallpaper-thumbnail-image"]
                        + (["selected"] if is_selected else []),
                    ),
                    hexpand=True,
                    halign="fill",
                    css_classes=["wallpaper-thumbnail"]
                    + (["selected"] if is_selected else []),
                )
                btn.wallpaper_path = file_path
                gallery_grid.attach(btn, idx % columns, idx // columns, 1, 1)
                temp_thumbnails.append(btn)

            gallery_scroll = widgets.Scroll(
                width_request=600,
                height_request=300,
            )
            gallery_scroll.set_child(gallery_grid)
            GLib.idle_add(
                self._replace_gallery_content, gallery_scroll, temp_thumbnails
            )

        loader_thread = threading.Thread(target=do_find_and_build)
        loader_thread.daemon = True
        loader_thread.start()

    def _update_selected_icons(self):
        current_path = user_settings.appearance.wallcolors.wallpaper_path
        for btn in self.thumbnail_overlays:
            if btn.wallpaper_path == current_path:
                btn.add_css_class("selected")
                btn.get_child().add_css_class("selected")
            else:
                btn.remove_css_class("selected")
                btn.get_child().remove_css_class("selected")

    def _replace_gallery_content(self, new_child, thumbnail_buttons=None):
        while self.gallery_content_container.get_last_child():
            self.gallery_content_container.remove(
                self.gallery_content_container.get_last_child()
            )

        if new_child:
            self.gallery_content_container.append(new_child)
            if thumbnail_buttons is not None:
                self.thumbnail_overlays = thumbnail_buttons
        else:
            self.gallery_content_container.append(
                widgets.Label(
                    label="No wallpapers found in the directory.",
                    css_classes=["message"],
                )
            )


class FontCategory(widgets.Box):
    def __init__(self):
        super().__init__(css_classes=["settings-category"], vertical=True, spacing=0)
        self.append(CategoryLabel("Fonts", "custom_typography"))

        font_dialog = Gtk.FontDialog()
        font_button = Gtk.FontDialogButton(dialog=font_dialog)

        settings = Gtk.Settings.get_default()
        font_name = settings.get_property("gtk-font-name")
        font_button.set_font_desc(Pango.FontDescription.from_string(font_name))
        self.append(
            SettingsRow(
                title="Font", description="Select a system font.", child=[font_button]
            )
        )

        font_button.connect("notify::font-desc", self.on_font_set)

        self.append(font_button)

    def on_font_set(self, button, _):
        font_desc = button.get_font_desc()
        if not font_desc:
            return

        font_name = font_desc.to_string()

        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-font-name", font_name)

        os.system(f"gsettings set org.gnome.desktop.interface font-name '{font_name}'")


class AppearanceTab(widgets.Box):
    def __init__(self):
        super().__init__(
            vertical=True,
            spacing=8,
            css_classes=["settings-body"],
            hexpand=False,
            halign="center",
            width_request=800,
        )
        wallpaper_category = WallpaperCategory()
        self.append(wallpaper_category)
        self.append(ColorCategory())
        self.append(FontCategory())
        self.append(QuickSelectCategory(wallpaper_category_ref=wallpaper_category))

import os
import threading
from gi.repository import GLib, Gtk 

from ignis import widgets
from modules.m3components import Button
from scripts import Wallpaper
from user_settings import user_settings
from ..widgets import CategoryLabel, make_toggle_buttons, SwitchRow, SettingsRow
from ignis.app import IgnisApp

app = IgnisApp.get_initialized()


class WallColorCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=2,
            child=[
                CategoryLabel("Wallpaper & Colors"),
            ]
        )

        self.wallpaper_picture = widgets.Picture(
            height=450,
            width=800,
            vexpand=False,
            content_fit="cover",
            css_classes=["wallpaper-preview"],
            image=user_settings.appearance.wallcolors.bind("wallpaper_path")
        )

        self.wallpaper_filename_label = widgets.Label(
            label=os.path.basename(user_settings.appearance.wallcolors.wallpaper_path) or "Click to set wallpaper",
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
            label=widgets.Label(label=''),
            css_classes=["wallpaper-button-overlay"],
            dialog=widgets.FileDialog(
                on_file_set=on_file_set_handler,
                initial_path=user_settings.appearance.wallcolors.wallpaper_path,
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
            child=self.wallpaper_picture,
        )

        wallpaper_overlay.add_overlay(file_chooser_button)
        wallpaper_overlay.add_overlay(self.wallpaper_filename_label)

        self.append(SettingsRow(
            title="Wallpaper",
            description="Interface colors automatically match your wallpaper.",
            child=[wallpaper_overlay]
        ))
        
        self.thumbnail_overlays = []
        
        quick_select_container = widgets.Box(
            vertical=True,
            spacing=10,
        )

        folder_chooser_button = widgets.FileChooserButton(
            label=widgets.Label(label="Select a Folder"),
            css_classes=["folder-chooser-button"],
            dialog=widgets.FileDialog(
                select_folder=True,
                initial_path=user_settings.appearance.wallcolors.quickselect_path,
                on_file_set=self._on_quickselect_folder_selected,
            )
        )
        quick_select_container.append(folder_chooser_button)

        self.gallery_content_container = widgets.Box(
            vertical=True,
            halign="center",
            valign="center",
            css_classes=["wallpaper-gallery-container"],
            width_request=800,
        )
        quick_select_container.append(self.gallery_content_container)
        
        loading_label = widgets.Label(label="Loading wallpapers...")
        self.gallery_content_container.append(loading_label)

        loader_thread = threading.Thread(target=self._find_and_create_gallery_async)
        loader_thread.daemon = True
        loader_thread.start()

        self.append(SettingsRow(
            title="Color Scheme",
            description="Pick between a variety of palettes.",
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
                    lambda: user_settings.appearance.wallcolors.color_scheme,
                    Wallpaper.setColors
                )
            ]
        ))

        self.append(SettingsRow(
            title="Theme",
            description="Pick between a light and a dark theme for the interface.",
            child=[
                make_toggle_buttons(
                    [
                        ("Light", False, "light_mode"),
                        ("Dark", True, "dark_mode"),
                    ],
                    lambda: user_settings.appearance.wallcolors.dark_mode,
                    Wallpaper.setDarkMode
                )
            ]
        ))
        
        self.append(SettingsRow(
            title="Quick Select",
            description="Browse local wallpapers for a quick change.",
            child=[quick_select_container]
        ))

    def _set_and_update_wallpaper(self, path):
        if path:
            Wallpaper.setWall(path)
            self.wallpaper_picture.image = path
            self.wallpaper_filename_label.label = os.path.basename(path)

    def _on_thumbnail_clicked(self, path):
        self._set_and_update_wallpaper(path)
        self._update_selected_icons()

    def _on_quickselect_folder_selected(self, dialog, file):
        path = file.get_path()
        if path:
            user_settings.appearance.wallcolors.set_quickselect_path(path)
            self._find_and_create_gallery_async()

    def _find_and_create_gallery_async(self):
        wallpaper_dir = user_settings.appearance.wallcolors.quickselect_path
        if not wallpaper_dir or not os.path.isdir(os.path.expanduser(wallpaper_dir)):
            wallpaper_dir = os.path.expanduser("~/Pictures/Wallpapers")
            
        if not os.path.isdir(wallpaper_dir) or not os.listdir(wallpaper_dir):
            GLib.idle_add(self._replace_gallery_content, None)
            return

        supported_extensions = ('.png', '.jpg', '.jpeg', '.gif')
        image_files = [os.path.join(wallpaper_dir, f) for f in os.listdir(wallpaper_dir) if f.lower().endswith(supported_extensions)]
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
        
        temp_thumbnails = []
        for i, file_path in enumerate(image_files):
            thumbnail_button = widgets.Button(
                on_click=lambda btn, path=file_path: self._on_thumbnail_clicked(path),
                child=widgets.Picture(
                    image=file_path,
                    content_fit="cover",
                    height=100,
                    hexpand=True,
                    halign="fill",
                    css_classes=["wallpaper-thumbnail-image"]
                ),
                hexpand=True,
                halign="fill",
                css_classes=["wallpaper-thumbnail"]
            )
            
            selected_icon = widgets.Label(
                label="check",
                style="font-family: 'Material Symbols Outlined';", 
                css_classes=["selected-icon"],
                visible=False,
            )

            thumbnail_overlay = widgets.Overlay(
                css_classes=["wallpaper-thumbnail-overlay"],
                child=thumbnail_button,
            )
            thumbnail_overlay.wallpaper_path = file_path
            thumbnail_overlay.selected_icon = selected_icon

            thumbnail_overlay.add_overlay(selected_icon)

            gallery_grid.attach(thumbnail_overlay, i % 4, i // 4, 1, 1)
            temp_thumbnails.append(thumbnail_overlay)

        gallery_scroll = widgets.Scroll(
            width_request=800,
            height_request=300,
        )
        gallery_scroll.set_child(gallery_grid)
        
        GLib.idle_add(self._replace_gallery_content, gallery_scroll, temp_thumbnails)

    def _update_selected_icons(self):
        current_path = user_settings.appearance.wallcolors.wallpaper_path
        for overlay in self.thumbnail_overlays:
            is_selected = overlay.wallpaper_path == current_path
            selected_icon = overlay.selected_icon
            selected_icon.visible = is_selected

    def _replace_gallery_content(self, new_child, thumbnail_overlays=None):
        if self.gallery_content_container.get_last_child():
             self.gallery_content_container.remove(self.gallery_content_container.get_last_child())
        
        if new_child:
            self.gallery_content_container.append(new_child)
            if thumbnail_overlays:
                self.thumbnail_overlays = thumbnail_overlays
            self._update_selected_icons()
        else:
            self.gallery_content_container.append(widgets.Label(label="No wallpapers found in the directory.", css_classes=["message"]))


class AppearanceTab(widgets.Box):

    def __init__(self):
        super().__init__(vertical=True, spacing=20, css_classes=["settings-body"], hexpand=False, halign="center", width_request=800)
        self.append(WallColorCategory())
import os
from gi.repository import Gtk
from ignis.base_widget import BaseWidget
from ignis.services.niri import NiriService
from user_settings import user_settings
from scripts.extra_niri import ExtraNiri
from ignis import widgets

class Background(widgets.Window, BaseWidget):
    __gtype_name__ = "ExoBackground"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        unique_namespace = f"ExoBackground{kwargs.get('monitor', 0)}"
        widgets.Window.__init__(
            self,
            namespace=unique_namespace,
            layer="background",
            exclusivity="ignore",
            anchor=["top", "left", "right", "bottom"],
            css_classes=["exo-background"],
        )
        self.niri = NiriService.get_default()
        self.extra_niri = ExtraNiri()
        self.image = widgets.Picture(
            image=user_settings.appearance.wallcolors.bind("wallpaper_path"),
            hexpand=True,
            vexpand=True,
            halign="fill",
            valign="fill",
            content_fit="cover",
            css_classes=["exo-background-image"],
        )
        self.child = self.image

        BaseWidget.__init__(self, **kwargs)

        self.niri.connect("notify::workspaces", self.update)
        self.niri.connect("notify::windows", self.update)
        self.niri.connect("notify::overview-opened", self.update)

        user_settings.appearance.wallcolors.connect("notify::wallpaper-path", self.update)
        user_settings.appearance.wallcolors.background.connect("notify::overview-zoom", self.update)
        user_settings.appearance.wallcolors.background.connect("notify::darken-with-windows", self.update)

    def update(self, *args):
        self.image.set_visible(os.path.exists(user_settings.appearance.wallcolors.wallpaper_path))

        if not self.extra_niri.workspace_is_empty(self.extra_niri.active_workspace()) and user_settings.appearance.wallcolors.background.darken_with_windows:
            self.add_css_class("windows")
        else:
            self.remove_css_class("windows")

        if self.niri.overview_opened and user_settings.appearance.wallcolors.background.overview_zoom:
            self.add_css_class("overview-open")
        else:
            self.remove_css_class("overview-open")

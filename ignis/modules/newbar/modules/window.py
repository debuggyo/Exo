from ignis import widgets, utils
from gi.repository import Gtk
from ignis.base_widget import BaseWidget
from ignis.services.niri import NiriService
from ignis.services.hyprland import HyprlandService
from ignis.services.applications import ApplicationsService
from ignis.gobject import IgnisProperty

class Window(Gtk.Box, BaseWidget):
    __gtype_name__ = "ExoWindow"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, spacing=8)
        self._vertical: bool = False
        self._density: int = 0

        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()
        self.applications = ApplicationsService.get_default()

        self.icon = widgets.Icon(image="application-x-executable-symbolic", pixel_size=16, halign="center", valign="center")
        self.info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.title_label = Gtk.Label(label="Title", justify=Gtk.Justification.CENTER, vexpand=True, halign=Gtk.Align.START)
        self.app_id_label = Gtk.Label(label="AppID", justify=Gtk.Justification.CENTER, vexpand=True, halign=Gtk.Align.START)

        self.append(self.icon)
        self.append(self.info)
        self.info.append(self.title_label)
        self.info.append(self.app_id_label)

        self.icon.add_css_class("icon")
        self.title_label.add_css_class("title")
        self.app_id_label.add_css_class("app-id")
        self.add_css_class("exo-window")
        self.set_overflow(Gtk.Overflow.HIDDEN)

        self.update_layout()
        if self.niri.is_available:
            self.niri.active_window.connect("notify::title", self.update_info)
        elif self.hyprland.is_available:
            self.hyprland.active_window.connect("notify::title", self.update_info)

        BaseWidget.__init__(self, **kwargs)

    @IgnisProperty
    def vertical(self) -> bool:
        return self._vertical

    @vertical.setter
    def vertical(self, value: bool) -> None:
        self._vertical = value
        self.update_layout()

    def update_layout(self):
        self.info.set_visible(True if not self._vertical else False)

        # CSS Classes
        if self._vertical:
            self.add_css_class("window-vertical")
        else:
            self.remove_css_class("window-vertical")

    def update_info(self, *args):
        if self.niri.is_available:
            app_id = self.niri.active_window.app_id
            title = self.niri.active_window.title
            icon = utils.get_app_icon_name(app_id) or "application-x-executable-symbolic"
        elif self.hyprland.is_available:
            title = self.hyprland.active_window.title
            app_id = self.hyprland.active_window.class_name
            icon = utils.get_app_icon_name(app_id) or "application-x-executable-symbolic"
        else:
            title = "Title"
            app_id = "AppID"
            icon = "application-x-executable-symbolic"

        self.icon.set_image(icon)
        self.title_label.set_label(title)
        self.app_id_label.set_label(app_id)
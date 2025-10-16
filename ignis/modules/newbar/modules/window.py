from ignis import widgets, utils
from gi.repository import Gtk, Pango
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
        self._show_app_id: bool = True
        self._show_title: bool = True
        self._show_icon: bool = True
        self._fixed_width: bool = True

        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()
        self.applications = ApplicationsService.get_default()

        self.icon = widgets.Icon(image="application-x-executable-symbolic", pixel_size=16, halign="center", valign="center", hexpand="center", vexpand="center")
        self.info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.title_label = Gtk.Label(
            label="Empty",
            vexpand=True,
            justify=Gtk.Justification.LEFT,
            halign=Gtk.Align.START,
            ellipsize=Pango.EllipsizeMode.END,
            max_width_chars=24,
            xalign=0,
        )
        self.app_id_label = Gtk.Label(
            label="placeholder",
            vexpand=True,
            justify=Gtk.Justification.LEFT,
            halign=Gtk.Align.START,
            ellipsize=Pango.EllipsizeMode.END,
            max_width_chars=30,
            xalign=0,
        )

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

    @IgnisProperty
    def density(self) -> bool:
        return self._density

    @density.setter
    def density(self, value: bool) -> None:
        self._density = value
        self.update_layout()

    @IgnisProperty
    def show_icon(self) -> bool:
        return self._show_icon

    @show_icon.setter
    def show_icon(self, value: bool) -> None:
        self._show_icon = value
        self.update_layout()

    @IgnisProperty
    def show_title(self) -> bool:
        return self._show_title

    @show_title.setter
    def show_title(self, value: bool) -> None:
        self._show_title = value
        self.update_layout()

    @IgnisProperty
    def show_app_id(self) -> bool:
        return self._show_app_id

    @show_app_id.setter
    def show_app_id(self, value: bool) -> None:
        self._show_app_id = value
        self.update_layout()

    @IgnisProperty
    def fixed_width(self) -> bool:
        return self._fixed_width

    @fixed_width.setter
    def fixed_width(self, value: bool) -> None:
        self._fixed_width = value
        self.update_layout()

    def update_layout(self):
        info_visible = not self._vertical and (self._show_title or self._show_app_id)
        app_id_visible = self._show_app_id and self._density == 0

        self.info.set_visible(info_visible)
        self.icon.set_visible(True if self._show_icon or self._vertical else False)
        self.title_label.set_visible(True if self._show_title else False)
        self.app_id_label.set_visible(app_id_visible)
        self.title_label.set_width_chars(24 if self._fixed_width else -1)

        # CSS Classes
        if self._vertical:
            self.add_css_class("window-vertical")
        else:
            self.remove_css_class("window-vertical")
        if not info_visible and not self._vertical:
            self.add_css_class("no-labels")
        else:
            self.remove_css_class("no-labels")

    def update_info(self, *args):
        if self.niri.is_available:
            title = self.niri.active_window.title or "Empty"
            app_id = self.niri.active_window.app_id or "niri"
            icon = utils.get_app_icon_name(app_id) or "application-x-executable-symbolic"
        elif self.hyprland.is_available:
            title = self.hyprland.active_window.title or "Empty"
            app_id = self.hyprland.active_window.class_name or "hyprland"
            icon = utils.get_app_icon_name(app_id) or "application-x-executable-symbolic"
        else:
            title = "Title"
            app_id = "AppID"
            icon = "application-x-executable-symbolic"

        self.icon.set_image(icon)
        self.title_label.set_label(title)
        self.app_id_label.set_label(app_id)
from ignis import widgets, utils
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
from ignis.services.niri import NiriService
from ignis.services.hyprland import HyprlandService
from gi.repository import Gtk
from modules.shared_modules import AppIcon


class LayoutWindow(widgets.EventBox, BaseWidget):
    __gtype_name__ = "LayoutWindow"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, window, amount_in_column, **kwargs):
        widgets.EventBox.__init__(
            self,
            css_classes=["window"],
            on_click=lambda _: window.focus(),
        )
        self._show_icons: bool = True
        self.window = window
        self.width = window.layout.window_size[0] / 50
        self.height = (25 / amount_in_column) - 4

        self.icon = AppIcon(app_id=self.window.app_id, name=self.window.title, halign="center", hexpand=True)
        self.append(self.icon)

        self.set_width_request(self.width)
        self.update_icons()

        BaseWidget.__init__(self, **kwargs)

    @IgnisProperty
    def show_icons(self) -> bool:
        return self._show_icons

    @show_icons.setter
    def show_icons(self, value) -> None:
        if value == self._show_icons:
            return
        self._show_icons = value
        self.update_icons()

    def update_icons(self):
        if self._show_icons:
            if self.width > 17 and self.height > 17:
                self.icon.set_pixel_size(16)
                self.icon.set_visible(True)
            elif self.width > 9 and self.height > 9:
                self.icon.set_pixel_size(8)
                self.icon.set_visible(True)
            else:
                self.icon.set_visible(False)
        else:
            self.icon.set_visible(False)


class Layout(Gtk.Box, BaseWidget):
    __gtype_name__ = "ExoLayout"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, visible=False)
        self._vertical: bool = False
        self._show_on_single: bool = True
        self._show_icons: bool = True
        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()

        self.add_css_class("exo-layout")
        self.update_layout()

        self.niri.connect("notify::workspaces", self.update_layout)
        self.niri.connect("notify::windows", self.update_layout)

        BaseWidget.__init__(self, **kwargs)

    @IgnisProperty
    def vertical(self) -> bool:
        return self._vertical

    @vertical.setter
    def vertical(self, value) -> None:
        if value == self._vertical:
            return
        self._vertical = value
        self.update_layout()

    @IgnisProperty
    def show_on_single(self) -> bool:
        return self._show_on_single

    @show_on_single.setter
    def show_on_single(self, value) -> None:
        if value == self._show_on_single:
            return
        self._show_on_single = value
        self.update_layout()

    @IgnisProperty
    def show_icons(self) -> bool:
        return self._show_icons

    @show_icons.setter
    def show_icons(self, value) -> None:
        if value == self._show_icons:
            return
        self._show_icons = value
        self.update_layout()

    def update_layout(self, *args):
        self.set_visible(False)
        while True:
            child = self.get_first_child()
            if not child:
                break
            self.remove(child)
        if self.niri.is_available:
            for i in self.niri.workspaces:
                if i.is_active:
                    active_workspace = i
            windows_in_workspaces = [w for w in self.niri.windows if w.workspace_id == active_workspace.id]
            columns = {}
            for window in windows_in_workspaces:
                if not window.is_floating:
                    column = window.layout.pos_in_scrolling_layout[0]
                    if column not in columns:
                        columns[column] = []
                    columns[column].append(window)
                    columns = dict(sorted(columns.items()))

            for column, windows in columns.items():
                column_box = widgets.Box(vertical=True, vexpand=False, valign="center", height_request=25)
                windows = sorted(windows, key=lambda w: w.layout.pos_in_scrolling_layout[1])
                for win in windows:
                    window_box = LayoutWindow(
                        win,
                        len(windows),
                        show_icons=self._show_icons,
                        vexpand=True,
                        valign="fill",
                    )
                    if win.id == active_workspace.active_window_id:
                        window_box.add_css_class("active")
                    column_box.append(window_box)
                self.append(column_box)

            if not self._vertical:
                if len(windows_in_workspaces) == 0 or len(windows_in_workspaces) == 1 and not self._show_on_single:
                    self.set_visible(False)
                else:
                    self.set_visible(True)
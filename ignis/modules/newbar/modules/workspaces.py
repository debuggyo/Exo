import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GObject, Gtk
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
from ignis import widgets, utils
from ignis.services.niri import NiriService
from ignis.services.hyprland import HyprlandService

class WorkspaceStyle(GObject.GEnum):
    IMPULSE = 0
    NUMBERS = 1
    DOTS = 2

class Workspace(widgets.Button, BaseWidget):
    __gtype_name__ = "ExoWorkspace"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, index, **kwargs):
        widgets.Button.__init__(self, hexpand=False, vexpand=False)
        self._index: int = index
        self._workspace_style: WorkspaceStyle = WorkspaceStyle.IMPULSE

        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()

        if self.niri.is_available:
            self.on_click = lambda _: self.niri.switch_to_workspace(self._index)
            self.niri.connect("notify::workspaces", self._update_info)
            self.niri.connect("notify::windows", self._update_info)
        elif self.hyprland.is_available:
            self.on_click = lambda _: self.hyprland.switch_to_workspace(self._index)
            self.hyprland.connect("notify::active-workspace", self._update_info)
            self.hyprland.connect("notify::windows", self._update_info)

        self.container = Gtk.Box()
        self.icon = widgets.Icon(pixel_size=16, halign="center", valign="center", hexpand=True, vexpand=True)
        self.number = widgets.Label(halign="center", valign="center", hexpand=True, vexpand=True)

        self.container.append(self.icon)
        self.container.append(self.number)
        self.set_child(self.container)

        self.add_css_class("workspace")
        self.icon.add_css_class("icon")
        self.number.add_css_class("label")

        BaseWidget.__init__(self, **kwargs)
        self._update_info()

    @IgnisProperty(type=WorkspaceStyle, default=WorkspaceStyle.IMPULSE)
    def workspace_style(self) -> WorkspaceStyle:
        return self._workspace_style

    @workspace_style.setter
    def workspace_style(self, value: WorkspaceStyle):
        if self._workspace_style == value:
            return
        self._workspace_style = value
        self._update_info()

    def _update_info(self, *args):
        active = False
        windows_in_workspace = []
        icon_name = "application-x-executable-symbolic"

        if self.niri.is_available:
            ws = self.niri.get_workspace_by_id(self._index)
            if ws:
                active = ws.is_active
            windows_in_workspace = [w for w in self.niri.windows if w.workspace_id == self._index]
            if windows_in_workspace:
                icon_name = utils.get_app_icon_name(windows_in_workspace[0].app_id) or icon_name
        elif self.hyprland.is_available:
            active_ws = self.hyprland.active_workspace
            if active_ws:
                active = active_ws.id == self._index
            windows_in_workspace = self.hyprland.get_windows_on_workspace(self._index)
            if windows_in_workspace:
                icon_name = utils.get_app_icon_name(windows_in_workspace[0].class_name) or icon_name

        empty = not windows_in_workspace

        self.icon.set_visible(False)
        self.number.set_visible(False)

        style_map = {
            WorkspaceStyle.DOTS: "dots",
            WorkspaceStyle.NUMBERS: "numbers",
            WorkspaceStyle.IMPULSE: "impulse",
        }
        for s in style_map.values():
            self.remove_css_class(s)
        if self._workspace_style in style_map:
            self.add_css_class(style_map[self._workspace_style])

        if self._workspace_style == WorkspaceStyle.DOTS:
            self.set_hexpand(False)
            self.set_vexpand(False)
            self.set_halign("center")
            self.set_valign("center")
        elif self._workspace_style == WorkspaceStyle.NUMBERS:
            self.number.set_label(str(self._index))
            self.number.set_visible(True)
            self.set_hexpand(True)
            self.set_vexpand(True)
            self.set_halign("fill")
            self.set_valign("fill")
        elif self._workspace_style == WorkspaceStyle.IMPULSE:
            if not empty:
                self.icon.set_image(icon_name)
                self.icon.set_visible(True)
            else:
                self.number.set_label("•")
                self.number.set_visible(True)
            self.set_hexpand(True)
            self.set_vexpand(True)
            self.set_halign("fill")
            self.set_valign("fill")

        if active:
            self.add_css_class("active")
        else:
            self.remove_css_class("active")

        if empty:
            self.add_css_class("empty")
        else:
            self.remove_css_class("empty")


class Workspaces(widgets.Box, BaseWidget):
    __gtype_name__ = "ExoWorkspaces"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        widgets.Box.__init__(self, spacing=2)
        self._workspace_style: WorkspaceStyle = WorkspaceStyle.IMPULSE
        self._vertical: bool = False

        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()
        BaseWidget.__init__(self, **kwargs)

        self.set_vertical(self._vertical)
        self.add_css_class("exo-workspaces")

        if self.niri.is_available:
            self.niri.connect("notify::workspaces", self._update_workspaces)
        elif self.hyprland.is_available:
            self.hyprland.connect("notify::workspaces", self._update_workspaces)

        self._update_workspaces()

    @IgnisProperty
    def vertical(self) -> bool:
        return self._vertical

    @vertical.setter
    def vertical(self, value: bool) -> None:
        self._vertical = value
        self.set_orientation(Gtk.Orientation.VERTICAL if value else Gtk.Orientation.HORIZONTAL)

    @IgnisProperty(type=WorkspaceStyle, default=WorkspaceStyle.IMPULSE)
    def workspace_style(self) -> WorkspaceStyle:
        return self._workspace_style

    @workspace_style.setter
    def workspace_style(self, value: WorkspaceStyle):
        if self._workspace_style == value:
            return
        self._workspace_style = value
        self._update_workspaces()

    def _update_workspaces(self, *args):
        # Clear any existing workspace widgets
        while child := self.get_first_child():
            self.remove(child)

        workspace_ids = []
        if self.niri.is_available:
            workspace_ids = sorted([ws.idx for ws in self.niri.workspaces])
        elif self.hyprland.is_available:
            workspace_ids = sorted([ws.id for ws in self.hyprland.workspaces])
        else:
            return

        # Re-create widgets in the correct order
        for i in workspace_ids:
            new_workspace = Workspace(index=i, workspace_style=self._workspace_style)
            self.append(new_workspace)

        self.set_spacing(4 if self._workspace_style == WorkspaceStyle.DOTS else 2)
        style_map = {
            WorkspaceStyle.DOTS: "dots",
            WorkspaceStyle.NUMBERS: "numbers",
            WorkspaceStyle.IMPULSE: "impulse",
        }
        for s in style_map.values():
            self.remove_css_class(s)
        if self._workspace_style in style_map:
            self.add_css_class(style_map[self._workspace_style])
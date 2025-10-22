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

    def __init__(self, workspace, **kwargs):
        widgets.Button.__init__(self, hexpand=False, vexpand=False)
        self._workspace = workspace
        self._workspace_style: WorkspaceStyle = WorkspaceStyle.IMPULSE
        self._impulse_numbers: bool = False

        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()

        if self.niri.is_available:
            self.on_click = lambda _: self.niri.switch_to_workspace(self._workspace.idx)
            self.niri.connect("notify::workspaces", self._update_info)
        elif self.hyprland.is_available:
            self.on_click = lambda _: self.hyprland.switch_to_workspace(self._workspace.id)
            self.hyprland.connect("notify::active-workspace", self._update_info)
            self.hyprland.connect("notify::workspaces", self._update_info)

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

    @IgnisProperty
    def impulse_numbers(self) -> bool:
        return self._impulse_numbers

    @impulse_numbers.setter
    def impulse_numbers(self, value: bool):
        if self._impulse_numbers == value:
            return
        self._impulse_numbers = value
        self._update_info()

    def _update_info(self, *args):
        active = False
        windows_in_workspace = []
        icon_name = "application-x-executable-symbolic"

        if self.niri.is_available:
            ws = self._workspace
            if ws:
                active = ws.is_active
            windows_in_workspace = [w for w in self.niri.windows if w.workspace_id == self._workspace.id]
            if windows_in_workspace:
                icon_name = utils.get_app_icon_name(windows_in_workspace[0].app_id) or icon_name
        elif self.hyprland.is_available:
            updated_ws = next((w for w in self.hyprland.workspaces if w.id == self._workspace.id), None)
            if updated_ws:
                self._workspace = updated_ws

            active_ws = self.hyprland.active_workspace
            if active_ws:
                active = active_ws.id == self._workspace.id
            windows_in_workspace = self.hyprland.get_windows_on_workspace(self._workspace.id)
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
            if self.niri.is_available or hasattr(self._workspace, "dummy"):
                label = str(self._workspace.idx)
                if self._workspace.name:
                    label = self._workspace.name[0]
            else:
                label = str(self._workspace.id)
            self.number.set_label(label)
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
                if self._impulse_numbers:
                    if self.niri.is_available or hasattr(self._workspace, "dummy"):
                        label = str(self._workspace.idx)
                        if self._workspace.name:
                            label = self._workspace.name[0]
                    else:
                        label = str(self._workspace.id)
                else:
                    label = "•"
                self.number.set_label(label)
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
        self._impulse_numbers: bool = False
        self._vertical: bool = False
        self._fixed_workspaces: bool = False
        self._fixed_workspace_amount: int = 5

        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()
        BaseWidget.__init__(self, **kwargs)

        self.set_vertical(self._vertical)
        self.add_css_class("exo-workspaces")

        if self.niri.is_available:
            self.niri.connect("notify::workspaces", self._update_workspaces)
            self.niri.connect("notify::windows", self._update_workspaces)
        elif self.hyprland.is_available:
            self.hyprland.connect("notify::workspaces", self._update_workspaces)
            self.hyprland.connect("notify::active-workspace", self._update_workspaces)
            self.hyprland.connect("notify::windows", self._update_workspaces)

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

    @IgnisProperty
    def impulse_numbers(self) -> bool:
        return self._impulse_numbers

    @impulse_numbers.setter
    def impulse_numbers(self, value: bool):
        if self._impulse_numbers == value:
            return
        self._impulse_numbers = value
        self._update_workspaces()

    @IgnisProperty(type=bool, default=False)
    def fixed_workspaces(self) -> bool:
        return self._fixed_workspaces

    @fixed_workspaces.setter
    def fixed_workspaces(self, value: bool):
        if self._fixed_workspaces == value:
            return
        self._fixed_workspaces = value
        self._update_workspaces()

    @IgnisProperty(type=int, default=5)
    def fixed_workspace_amount(self) -> int:
        return self._fixed_workspace_amount

    @fixed_workspace_amount.setter
    def fixed_workspace_amount(self, value: int):
        if self._fixed_workspace_amount == value:
            return
        self._fixed_workspace_amount = value
        self._update_workspaces()

    def _get_dummy_workspace(self, ws_id):
        class DummyWorkspace:
            def __init__(self, id, idx, name, is_active, is_urgent):
                self.id = id
                self.idx = idx
                self.name = name
                self.is_active = is_active
                self.is_urgent = is_urgent
                self.dummy = True

        return DummyWorkspace(id=9999, idx=ws_id, name=None, is_active=False, is_urgent=False)

    def _update_workspaces(self, *args):
        while child := self.get_first_child():
            self.remove(child)

        all_workspaces_map = {}
        workspaces = []
        if self.niri.is_available:
            workspaces = self.niri.workspaces
        elif self.hyprland.is_available:
            workspaces = self.hyprland.workspaces
        else:
            return

        for ws in workspaces:
            if self.niri.is_available:
                all_workspaces_map[ws.idx] = ws
            elif self.hyprland.is_available:
                all_workspaces_map[ws.id] = ws

        workspaces_to_display = []

        if self._fixed_workspaces and self._fixed_workspace_amount > 0:
            active_workspace_id = None
            if self.niri.is_available:
                active_ws = next((w for w in workspaces if w.is_active), None)
                if active_ws:
                    active_workspace_id = active_ws.id
            elif self.hyprland.is_available:
                active_ws = self.hyprland.active_workspace
                if active_ws:
                    active_workspace_id = active_ws.id

            workspace_ids_to_display_range = []
            if active_workspace_id is not None:
                if self._fixed_workspace_amount == 1:
                    page_base_id = active_workspace_id
                else:
                    page_base_id = ((active_workspace_id - 1) // self._fixed_workspace_amount) * self._fixed_workspace_amount + 1

                start_id = page_base_id
                end_id = page_base_id + self._fixed_workspace_amount - 1
                workspace_ids_to_display_range = range(start_id, end_id + 1)
            else:
                workspace_ids_to_display_range = range(1, self._fixed_workspace_amount + 1)

            for i in workspace_ids_to_display_range:
                ws = all_workspaces_map.get(i)
                if not ws:
                    ws = self._get_dummy_workspace(i)
                if ws:
                    workspaces_to_display.append(ws)
        else:
            if self.niri.is_available:
                workspaces_to_display = sorted(workspaces, key=lambda ws: ws.idx)
            else:
                workspaces_to_display = sorted(workspaces, key=lambda ws: ws.id)

        for ws in workspaces_to_display:
            new_workspace = Workspace(workspace=ws, workspace_style=self._workspace_style, impulse_numbers=self._impulse_numbers)
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

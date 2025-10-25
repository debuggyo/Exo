import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GObject, Gtk
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
from ignis import widgets
from ignis.services.niri import NiriService
from ignis.services.hyprland import HyprlandService
from modules.shared_modules import AppIcon

class WorkspaceStyle(GObject.GEnum):
    IMPULSE = 0
    DOTS = 1

class Workspace(widgets.Button, BaseWidget):
    __gtype_name__ = "ExoWorkspace"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, workspace, **kwargs):
        widgets.Button.__init__(self, hexpand=False, vexpand=False, halign="center", valign="center")
        self._workspace = workspace
        self._workspace_style: WorkspaceStyle = WorkspaceStyle.IMPULSE
        self._icons: bool = True
        self._names: bool = True
        self._numbers: bool = False
        self._bigger_active: bool = False

        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()

        if self.niri.is_available:
            self.on_click = lambda _: self.niri.switch_to_workspace(self._workspace.idx)
            self.niri.connect("notify::workspaces", self._update_info)
            if not hasattr(self._workspace, "dummy"):
                self._workspace.connect("destroyed", self._on_workspace_destroyed)
        elif self.hyprland.is_available:
            self.on_click = lambda _: self.hyprland.switch_to_workspace(self._workspace.id)
            self.hyprland.connect("notify::active-workspace", self._update_info)
            self.hyprland.connect("notify::workspaces", self._update_info)

        self.container = Gtk.Box()
        self.icon = AppIcon(pixel_size=16, halign="center", valign="center", hexpand=True, vexpand=True)
        self.number = widgets.Label(halign="center", valign="center", hexpand=True, vexpand=True)

        self.container.append(self.icon)
        self.container.append(self.number)
        self.set_child(self.container)

        self.add_css_class("workspace")
        self.icon.add_css_class("icon")
        self.number.add_css_class("label")

        BaseWidget.__init__(self, **kwargs)
        self._update_info()

    def _on_workspace_destroyed(self, *args):
        parent = self.get_parent()
        if parent:
            parent._update_workspaces()

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
    def icons(self) -> bool:
        return self._icons

    @icons.setter
    def icons(self, value: bool):
        if self._icons == value:
            return
        self._icons = value
        self._update_info()

    @IgnisProperty
    def names(self) -> bool:
        return self._names

    @names.setter
    def names(self, value: bool):
        if self._names == value:
            return
        self._names = value
        self._update_info()

    @IgnisProperty
    def numbers(self) -> bool:
        return self._numbers

    @numbers.setter
    def numbers(self, value: bool):
        if self._numbers == value:
            return
        self._numbers = value
        self._update_info()

    @IgnisProperty
    def bigger_active(self) -> bool:
        return self._bigger_active

    @bigger_active.setter
    def bigger_active(self, value: bool):
        if self._bigger_active == value:
            return
        self._bigger_active = value
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
            all_window_ids = {}
            for w in self.niri.windows:
                all_window_ids[w.id] = w
            if windows_in_workspace:
                app = all_window_ids[ws.active_window_id].app_id
                name = all_window_ids[ws.active_window_id].title
            ws_name = f"{ws.name} - {ws.idx}" if ws.name else f"Workspace {ws.idx}"
            titles_in_workspace = [w.title for w in windows_in_workspace] or ["No windows"]
            tooltip = f"<b>{ws_name}</b>\n" + '\n'.join(titles_in_workspace)
            self.set_tooltip_markup(tooltip)

        elif self.hyprland.is_available:
            ws = self._workspace
            updated_ws = next((w for w in self.hyprland.workspaces if w.id == self._workspace.id), None)
            if updated_ws:
                self._workspace = updated_ws

            active_ws = self.hyprland.active_workspace
            if active_ws:
                active = active_ws.id == self._workspace.id
            windows_in_workspace = self.hyprland.get_windows_on_workspace(self._workspace.id)
            if windows_in_workspace:
                app = windows_in_workspace[0].class_name
                name = windows_in_workspace[0].title
            ws_name = f"{ws.name if ws.name else ws.idx}"
            titles_in_workspace = [w.title for w in windows_in_workspace] or ["No windows"]
            tooltip = f"<b>{ws_name}</b>\n" + '\n'.join(titles_in_workspace)
            self.set_tooltip_markup(tooltip)

        empty = not windows_in_workspace

        self.icon.set_visible(False)
        self.number.set_visible(False)

        style_map = {
            WorkspaceStyle.IMPULSE: "impulse",
            WorkspaceStyle.DOTS: "dots",
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
        elif self._workspace_style == WorkspaceStyle.IMPULSE:
            if not empty and self._icons:
                self.icon.set_app_id(app)
                self.icon.set_name(name)
                self.icon.set_visible(True)
            else:
                label = "•"
                if self._numbers:
                    if self.niri.is_available or hasattr(self._workspace, "dummy"):
                        label = str(self._workspace.idx)
                    else:
                        label = str(self._workspace.id)
                if self._workspace.name and self._names:
                    label = self._workspace.name[0]
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

        if self._bigger_active:
            self.add_css_class("bigger-active")
        else:
            self.remove_css_class("bigger-active")


class Workspaces(widgets.Box, BaseWidget):
    __gtype_name__ = "ExoWorkspaces"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        widgets.Box.__init__(self, spacing=2)
        self._workspace_style: WorkspaceStyle = WorkspaceStyle.IMPULSE
        self._icons: bool = True
        self._names: bool = True
        self._numbers: bool = False
        self._bigger_active: bool = False
        self._vertical: bool = False
        self._fixed_workspaces: bool = False
        self._fixed_workspace_amount: int = 5

        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()

        scroll_controller = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.VERTICAL)
        scroll_controller.connect("scroll", self.on_scroll)
        self.add_controller(scroll_controller)

        self.set_vertical(self._vertical)
        self.add_css_class("exo-workspaces")

        if self.niri.is_available:
            self.niri.connect("notify::workspaces", self._update_workspaces)
            self.niri.connect("notify::windows", self._update_workspaces)
        elif self.hyprland.is_available:
            self.hyprland.connect("notify::workspaces", self._update_workspaces)
            self.hyprland.connect("notify::active-workspace", self._update_workspaces)
            self.hyprland.connect("notify::windows", self._update_workspaces)

        BaseWidget.__init__(self, **kwargs)
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
    def icons(self) -> bool:
        return self._icons

    @icons.setter
    def icons(self, value: bool):
        if self._icons == value:
            return
        self._icons = value
        self._update_workspaces()

    @IgnisProperty
    def names(self) -> bool:
        return self._names

    @names.setter
    def names(self, value: bool):
        if self._names == value:
            return
        self._names = value
        self._update_workspaces()

    @IgnisProperty
    def numbers(self) -> bool:
        return self._numbers

    @numbers.setter
    def numbers(self, value: bool):
        if self._numbers == value:
            return
        self._numbers = value
        self._update_workspaces()

    @IgnisProperty
    def bigger_active(self) -> bool:
        return self._bigger_active

    @bigger_active.setter
    def bigger_active(self, value: bool):
        if self._bigger_active == value:
            return
        self._bigger_active = value
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

    def on_scroll(self, _, _dx, dy):
        if self.niri.is_available:
            l = [i.idx for i in self.niri.workspaces if i.is_active]
            active_ws = l[0]
            desktop = self.niri
        elif self.hyprland.is_available:
            active_ws = self.hyprland.active_workspace.id
            desktop = self.hyprland
        if desktop:
            if dy > 0:
                new_ws = active_ws + 1
                if new_ws > len(desktop.workspaces) and desktop == self.niri:
                    new_ws = len(desktop.workspaces)
            else:
                new_ws = active_ws - 1
                if new_ws < 0:
                    new_ws = 0
            desktop.switch_to_workspace(new_ws)

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
                    active_workspace_id = active_ws.idx
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

        existing_widgets = {}
        existing_ws_ids = set()
        child = self.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            ws_id = child._workspace.idx if hasattr(child._workspace, "dummy") or self.niri.is_available else child._workspace.id
            if ws_id in existing_ws_ids:
                self.remove(child)
            else:
                existing_ws_ids.add(ws_id)
                existing_widgets[ws_id] = child
            child = next_child

        new_ws_ids = set()
        for ws in workspaces_to_display:
            ws_id = ws.idx if hasattr(ws, "dummy") or self.niri.is_available else ws.id
            new_ws_ids.add(ws_id)

            if ws_id in existing_widgets:
                widget = existing_widgets[ws_id]
                widget._workspace = ws
                widget.workspace_style = self._workspace_style
                widget.icons = self._icons
                widget.names = self._names
                widget.numbers = self._numbers
                widget.bigger_active = self._bigger_active
                widget._update_info()
            else:
                new_widget = Workspace(
                    workspace=ws,
                    workspace_style=self._workspace_style,
                    icons=self._icons,
                    names=self._names,
                    numbers=self._numbers,
                    bigger_active=self._bigger_active,
                )
                self.append(new_widget)
                existing_widgets[ws_id] = new_widget

        for ws_id, widget in list(existing_widgets.items()):
            if ws_id not in new_ws_ids:
                self.remove(widget)
                del existing_widgets[ws_id]

        sibling = None
        for ws in workspaces_to_display:
            ws_id = ws.idx if hasattr(ws, "dummy") or self.niri.is_available else ws.id
            widget = existing_widgets.get(ws_id)
            if widget:
                self.reorder_child_after(widget, sibling)
                sibling = widget

        self.set_spacing(4 if self._workspace_style == WorkspaceStyle.DOTS else 2)
        style_map = {
            WorkspaceStyle.DOTS: "dots",
            WorkspaceStyle.IMPULSE: "impulse",
        }
        for s in style_map.values():
            self.remove_css_class(s)
        if self._workspace_style in style_map:
            self.add_css_class(style_map[self._workspace_style])

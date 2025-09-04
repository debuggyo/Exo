from ignis import widgets
from ignis.services.niri import NiriService, NiriWorkspace, NiriWindow
from ignis.services.hyprland import HyprlandService, HyprlandWorkspace, HyprlandWindow
from ignis.services.applications import ApplicationsService
from user_settings import user_settings

SERVICE = None
if NiriService.get_default().is_available:
    SERVICE = NiriService.get_default()
elif HyprlandService.get_default().is_available:
    SERVICE = HyprlandService.get_default()

APPLICATIONS = ApplicationsService.get_default()

def get_active_workspace():
    if not SERVICE:
        return None
    if isinstance(SERVICE, NiriService):
        for workspace in SERVICE.workspaces:
            if workspace.is_active:
                return workspace
        return None
    elif isinstance(SERVICE, HyprlandService):
        return SERVICE.active_workspace
    return None

class WorkspaceButton(widgets.Button):
    def __init__(self, workspace) -> None:
        style = user_settings.interface.bar.modules.workspaces_style

        if isinstance(workspace, NiriWorkspace):
            label_text = str(workspace.idx)
        else:
            label_text = str(workspace.id)

        self.workspace = workspace
        self._label = widgets.Label(label=label_text, halign="center", valign="center")
        
        children = [self._label]
        self._icons_box = None

        if style == "windows":
            self._icons_box = widgets.Box(spacing=2, css_classes=["workspace-icons"])
            children.append(self._icons_box)
        
        self._main_content_box = widgets.Box(
            halign="fill",
            valign="fill",
            spacing=4,
            child=children  
        )

        super().__init__(
            css_classes=["workspace"],
            on_click=lambda x: self.workspace.switch_to(),
            child=self._main_content_box,
        )

        def update_css_classes(*args):
            active_workspace = get_active_workspace()
            if active_workspace and self.workspace.id == active_workspace.id:
                self.add_css_class("active")
            else:
                self.remove_css_class("active")

        if SERVICE:
            SERVICE.connect("notify::workspaces", update_css_classes)
            if isinstance(SERVICE, HyprlandService):
                SERVICE.connect("notify::active-workspace", update_css_classes)
            update_css_classes()
        
        self.update_layout()
        if style == "windows":
            self._update_icons()

        if SERVICE:
            SERVICE.connect("notify::windows", lambda *args: self._update_icons())

    def _get_windows_for_workspace(self):
        if isinstance(SERVICE, NiriService):
            return [w for w in SERVICE.windows if w.workspace_id == self.workspace.id]
        elif isinstance(SERVICE, HyprlandService):
            return SERVICE.get_windows_on_workspace(self.workspace.id)
        return []

    def _update_icons(self):
        if not self._icons_box:
            return

        last_child = self._icons_box.get_last_child()
        while last_child:
            self._icons_box.remove(last_child)
            last_child = self._icons_box.get_last_child()

        windows = self._get_windows_for_workspace()
        
        for window in windows:
            app_id = None
            if isinstance(window, NiriWindow):
                app_id = window.app_id
            elif isinstance(window, HyprlandWindow):
                app_id = window.class_name
            
            if app_id:
                apps = APPLICATIONS.search(APPLICATIONS.apps, app_id)
                if apps and apps[0].icon:
                    icon_widget = widgets.Icon(
                        icon_name=apps[0].icon,
                        pixel_size=16
                    )
                    self._icons_box.append(icon_widget)
        
        self._main_content_box.queue_resize()


    def update_layout(self):
        vertical = user_settings.interface.bar.vertical
        compact_mode = user_settings.interface.bar.density
        style = user_settings.interface.bar.modules.workspaces_style

        if self._icons_box:
            self._icons_box.set_vertical(vertical)
        
        if vertical:
            self._main_content_box.set_vertical(True)
            self.set_halign("center")
            if compact_mode == 3:
                self.set_valign("center")
            else:
                self.set_valign("fill")
        else:
            self._main_content_box.set_vertical(False)
            self.set_valign("center")
            if compact_mode == 3:
                self.set_halign("center")
            else:
                self.set_halign("fill")

        if style == "dots":
            self._main_content_box.set_spacing(0)

class Workspaces(widgets.Box):
    def __init__(self):
        self._workspace_box = widgets.Box(
            css_classes=["workspaces"]
        )
        
        super().__init__(child=[self._workspace_box])

        def update_workspaces(*args):
            # Get the current style from user settings
            style = user_settings.interface.bar.modules.workspaces_style
            
            # Explicitly manage CSS classes to avoid conflicts and invalid properties
            self.remove_css_class("dots")
            self.remove_css_class("windows")
            self.remove_css_class("numbers")

            if style == "dots":
                self.add_css_class("dots")
            elif style == "windows":
                self.add_css_class("windows")
            elif style == "numbers":
                self.add_css_class("numbers")

            if SERVICE:
                workspaces = SERVICE.workspaces

                last_child = self._workspace_box.get_last_child()
                while last_child:
                    self._workspace_box.remove(last_child)
                    last_child = self._workspace_box.get_last_child()

                for workspace in workspaces:
                    self._workspace_box.append(WorkspaceButton(workspace))
            else:
                pass

        if SERVICE:
            SERVICE.connect("notify::workspaces", update_workspaces)
            update_workspaces()

        self.update_layout()

    def update_layout(self):
        vertical = user_settings.interface.bar.vertical
        compact_mode = user_settings.interface.bar.density
        
        style = user_settings.interface.bar.modules.workspaces_style

        if compact_mode == 3:
            spacing = 5
        else:
            spacing = 2
        
        if style == "dots":
            spacing = 0

        self._workspace_box.set_vertical(vertical)
        self._workspace_box.set_spacing(spacing)

        for child in self._workspace_box:
            if isinstance(child, WorkspaceButton):
                child.update_layout()

    def widget(self):
        return self
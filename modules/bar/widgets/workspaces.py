# workspaces.py
from ignis import widgets
from ignis.services.niri import NiriService, NiriWorkspace
from ignis.services.hyprland import HyprlandService, HyprlandWorkspace
from user_settings import user_settings

SERVICE = None
if NiriService.get_default().is_available:
    SERVICE = NiriService.get_default()
elif HyprlandService.get_default().is_available:
    SERVICE = HyprlandService.get_default()

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
        if isinstance(workspace, NiriWorkspace):
            label_text = str(workspace.idx)
        else:
            label_text = str(workspace.id)

        self.workspace = workspace
        
        super().__init__(
            css_classes=["workspace"],
            on_click=lambda x: self.workspace.switch_to(),
            child=widgets.Label(label=label_text, halign="center", valign="center"),
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

    def update_layout(self):
        if user_settings.appearance.compact == 3:
            self.set_valign("center")
        else:
            self.set_valign("fill")

class Workspaces(widgets.Box):
    def __init__(self):
        self._workspace_box = widgets.Box(
            css_classes=["workspaces"]
        )
        
        def update_workspaces(*args):
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
            
        super().__init__(child=[self._workspace_box])
        self.update_layout()

    def update_layout(self):
        vertical = user_settings.appearance.vertical    
        compact_mode = user_settings.appearance.compact
        
        if compact_mode == 3:
            spacing = 5
        else:
            spacing = 2
        
        self._workspace_box.set_vertical(vertical)
        self._workspace_box.set_spacing(spacing)
        
        for child in self._workspace_box:
            if isinstance(child, WorkspaceButton):
                child.update_layout()
                
    def widget(self):
        return self
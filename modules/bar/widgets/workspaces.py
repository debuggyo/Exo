from ignis import widgets
from ignis.services.niri import NiriService, NiriWorkspace
from ignis.services.hyprland import HyprlandService, HyprlandWorkspace
from user_settings import user_settings

# Determine the active service and assign it to a single variable
SERVICE = None
if NiriService.get_default().is_available:
    SERVICE = NiriService.get_default()
elif HyprlandService.get_default().is_available:
    SERVICE = HyprlandService.get_default()

compact_mode = user_settings.appearance.compact

# Helper function to get the active workspace, abstracting the difference
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
        if compact_mode == 3:
            valign = "center"
        else:
            valign = "fill"

        # Determine the workspace ID property based on the service type
        if isinstance(workspace, NiriWorkspace):
            label_text = str(workspace.idx)
        else:
            # Assuming HyprlandWorkspace
            label_text = str(workspace.id)

        super().__init__(
            css_classes=["workspace"],
            on_click=lambda x: workspace.switch_to(),
            child=widgets.Label(label=label_text, halign="center", valign="center"),
            valign=valign
        )
        
        # Use a single, unified binding mechanism
        def update_css_classes(*args):
            active_workspace = get_active_workspace()
            if active_workspace and workspace.id == active_workspace.id:
                self.add_css_class("active")
            else:
                self.remove_css_class("active")

        if SERVICE:
            # This handles both niri and hyprland updates.
            # niri.workspaces changes when active workspace changes, so this works for both.
            SERVICE.connect("notify::workspaces", update_css_classes)
            if isinstance(SERVICE, HyprlandService):
                SERVICE.connect("notify::active-workspace", update_css_classes)
            update_css_classes() # Call once for initial state

class Workspaces(widgets.Box):
    def __init__(self):
        vertical = user_settings.appearance.vertical    
        if compact_mode == 3:
            spacing = 5
        else:
            spacing = 2
        
        self._workspace_box = widgets.Box(
            vertical=vertical,
            css_classes=["workspaces"],
            spacing=spacing
        )
        
        def update_workspaces(*args):
            if SERVICE:
                workspaces = SERVICE.workspaces
                self._workspace_box.child = [WorkspaceButton(workspace) for workspace in workspaces]
            else:
                self._workspace_box.child = []

        if SERVICE:
            SERVICE.connect("notify::workspaces", update_workspaces)
            update_workspaces() # initial state
            
        super().__init__(child=[self._workspace_box])
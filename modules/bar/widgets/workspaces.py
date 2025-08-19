from ignis import widgets
from ignis.services.niri import NiriService, NiriWorkspace
from ignis.services.hyprland import HyprlandService, HyprlandWorkspace
niri = NiriService.get_default()
hyprland = HyprlandService.get_default()
from user_settings import user_settings
compact_mode = user_settings.appearance.compact

class WorkspaceButton(widgets.Button):
    if niri.is_available:
        def __init__(self, workspace: NiriWorkspace) -> None:
            if compact_mode == 3:
                valign = "center"
            else:
                valign = "fill"

            super().__init__(
                css_classes=["workspace"],
                on_click=lambda x: workspace.switch_to(),
                child=widgets.Label(label=str(workspace.idx)),
                valign=valign
            )
            if workspace.is_active:
                self.add_css_class("active")
    elif hyprland.is_available:
        def __init__(self, workspace: HyprlandWorkspace) -> None:
            if compact_mode == 3:
                valign = "center"
            else:
                valign = "fill"

            super().__init__(
                css_classes=["workspace"],
                on_click=lambda x: workspace.switch_to(),
                child=widgets.Label(label=str(workspace.id)),
                valign=valign
            )
            if workspace.id == hyprland.active_workspace.id:
                self.add_css_class("active")

class Workspaces(widgets.Box):
    def __init__(self):
        if compact_mode == 3:
            spacing = 5
        else:
            spacing = 2
        if niri.is_available:
            child = [
                widgets.Box(
                    css_classes=["workspaces"],
                    spacing=spacing,
                    child=niri.bind_many(
                        ["workspaces"],
                        transform=lambda workspaces, *_: [
                            WorkspaceButton(i) for i in workspaces
                        ]
                    )
                )
            ]
        elif hyprland.is_available:
            child = [
                widgets.Box(
                    css_classes=["workspaces"],
                    spacing=spacing,
                    child=hyprland.bind_many(
                        ["workspaces"],
                        transform=lambda workspaces, *_: [
                            WorkspaceButton(i) for i in workspaces
                        ]
                    )
                )
            ]
        else:
            child = []
        super().__init__(child=child)

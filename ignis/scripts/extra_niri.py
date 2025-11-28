from ignis.services.niri import NiriService

class ExtraNiri:
    def __init__(self):
        self.niri = NiriService.get_default()

    def windows_in_workspace(self, workspace):
        return [w for w in self.niri.windows if w.workspace_id == workspace.id]

    def active_workspace(self):
        return next((w for w in self.niri.workspaces if w.is_active), None)

    def workspace_is_empty(self, workspace):
        return len(self.windows_in_workspace(workspace)) == 0
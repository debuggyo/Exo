from ignis import widgets
from ..widgets import CategoryLabel

class NiriTab(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-body"],
            vertical=True,
            spacing=2,
            child=[
                CategoryLabel("Niri Settings")
            ]
        )

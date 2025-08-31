from ignis import widgets
from modules.m3components import Button

class NavigationRail(widgets.Box):
    def __init__(self, tabs, on_select, default=None, vertical=True):
        super().__init__(
            css_classes=["navigation-rail"],
            vertical=vertical,
            spacing=5,
        )
        self.on_select = on_select
        self.buttons = {}

        for key, (icon, label) in tabs.items():
            btn = Button.button(
                icon=icon,
                label=label,
                ialign="center",
                valign="center",
                css_classes=["rail-button"],
                vertical=True,
                on_click=lambda *_, key=key: self.select(key),
            )
            self.buttons[key] = btn
            self.append(btn)
        
        # Set the default selected tab if one is provided
        if default:
            self.select(default)

    def select(self, key):
        for name, btn in self.buttons.items():
            if name == key:
                btn.add_css_class("selected")
            else:
                btn.remove_css_class("selected")
        self.on_select(key)
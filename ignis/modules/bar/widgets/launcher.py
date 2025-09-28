from ignis import widgets
from ignis.window_manager import WindowManager

window_manager = WindowManager.get_default()


class Launcher:
    def __init__(self):
        self.button = widgets.Button(
            label="apps",
            css_classes=["m3-icon", "launcher-button"],
            on_click=lambda x: self.launch(),
            hexpand=True,
            vexpand=True,
            halign="fill",
            valign="fill",
        )

    def launch(self):
        window_manager.toggle_window("Launcher")

    def widget(self):
        return self.button

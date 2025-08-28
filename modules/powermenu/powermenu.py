import asyncio
from ignis import widgets
from ignis import utils
from ignis.window_manager import WindowManager
from typing import Callable

window_manager = WindowManager.get_default()

def create_exec_task(cmd: str) -> None:
    asyncio.create_task(utils.exec_sh_async(cmd))

class PowerMenuButton(widgets.Button):
    def __init__(self, icon_name: str, command) -> None:
        super().__init__(
            label=icon_name,
            on_click=lambda *args: create_exec_task(command),
            css_classes=["power-option"],
        )

class PowerMenu(widgets.Window):
    def __init__(self):
        main_box = widgets.Box(
            vertical=False,
            valign="center",
            halign="center",
            css_classes=["powermenu"],
            child=[
                PowerMenuButton("power_settings_new", "shutdown"),
                PowerMenuButton("restart_alt", "reboot now"),
                PowerMenuButton("lock", "hyprlock"),
                PowerMenuButton("logout", "niri msg action quit || loginctl terminate-user ''"),
            ],
        )
        super().__init__(
            popup=True,
            kb_mode="exclusive",
            namespace="PowerMenu",
            exclusivity="ignore",
            visible=False,
            child=main_box,
            css_classes=["unset"],
        )

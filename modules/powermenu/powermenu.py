import asyncio
from ignis import widgets
from ignis import utils
from ignis.window_manager import WindowManager
from typing import Callable

window_manager = WindowManager.get_default()

def create_exec_task(cmd: str) -> None:
    asyncio.create_task(utils.exec_sh_async(cmd))

class PowerMenuButton(widgets.Button):
    def __init__(self, icon: str, command: str) -> None:
        super().__init__(
            label=icon,
            on_click=lambda x: create_exec_task(f'{command}'),
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
                PowerMenuButton(icon="power_settings_new", command="shutdown now"),
                PowerMenuButton(icon="restart_alt", command="reboot"),
                PowerMenuButton(icon="lock", command="hyprlock"),
                PowerMenuButton(icon="logout", command="niri msg action quit || loginctl terminate-user ''"),
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

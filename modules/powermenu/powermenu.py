import asyncio
from ignis import widgets
from ignis import utils
from ignis.window_manager import WindowManager
from typing import Callable

window_manager = WindowManager.get_default()

def create_exec_task(cmd: str) -> None:
    asyncio.create_task(utils.exec_sh_async(cmd))

class PowermenuButton(widgets.Button):
    def __init__(self, icon_name: str, on_click: Callable) -> None:
        super().__init__(
            label=icon_name,
            on_click=on_click,
            css_classes=["power-option", "unset"],
        )


class PowerOffButton(PowermenuButton):
    def __init__(self):
        super().__init__(
            icon_name="󰐥",
            on_click=lambda *args: create_exec_task("poweroff"),
        )


class RebootButton(PowermenuButton):
    def __init__(self):
        super().__init__(
            icon_name="󰜉",
            on_click=lambda *args: create_exec_task("reboot"),
        )


class LockButton(PowermenuButton):
    def __init__(self):
        super().__init__(
            icon_name="󰌾", on_click=lambda *args: create_exec_task("hyprlock")
        )

class HyprlandExitButton(PowermenuButton):
    def __init__(self):
        super().__init__(
            icon_name="󰗽",
            on_click=lambda *args: create_exec_task("niri msg action quit || loginctl terminate-user ''"),
        )


class PowerMenu(widgets.Window):
    def __init__(self):
        main_box = widgets.Box(
            vertical=False,
            valign="center",
            halign="center",
            css_classes=["powermenu"],
            child=[
                PowerOffButton(),
                RebootButton(),
                LockButton(),
                HyprlandExitButton(),
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

import asyncio
from ignis import widgets
from ignis import utils
from ignis.window_manager import WindowManager
from typing import Callable

window_manager = WindowManager.get_default()

def create_exec_task(cmd: str) -> None:
    asyncio.create_task(utils.exec_sh_async(cmd))

class PowerMenuButton(widgets.Button):
    def __init__(self, icon: str, label: str, command: str) -> None:
        button_content = widgets.Box(
            child=[
                widgets.Label(label=icon, css_classes=["power-menu-icon"]),
                widgets.Label(label=label, css_classes=["power-menu-label"])
            ],
            spacing=10,
            vertical=True,
            halign="center",
            valign="center"
        )

        super().__init__(
            child=button_content,
            on_click=lambda x: create_exec_task(f'{command}'),
            css_classes=["power-option"],
            height_request=150,
            width_request=150,
        )

class PowerMenu(widgets.Window):
    def __init__(self):
        main_box = widgets.Grid(
            valign="center",
            halign="center",
            css_classes=["powermenu"],
            row_num=2,
            child=[
                PowerMenuButton(icon="power_settings_new", label="Power Off", command="shutdown now"),
                PowerMenuButton(icon="restart_alt", label="Reboot", command="reboot"),
                PowerMenuButton(icon="lock", label="Lock Screen", command="hyprlock"),
                PowerMenuButton(icon="logout", label="Log Out", command="niri msg action quit || loginctl terminate-user ''"),
                PowerMenuButton(icon="dark_mode", label="Sleep", command="systemctl suspend"),
                PowerMenuButton(icon="frame_reload", label="Restart Exo", command="ignis reload"),
            ],
        )
        
        close_button = widgets.Button(
            vexpand=True,
            hexpand=True,
            can_focus=False,
            css_classes=["popup-close"],
            on_click=lambda x: window_manager.close_window("PowerMenu")
        )

        main_overlay = widgets.Overlay(
            css_classes=["popup-close"],
            child=close_button,
            overlays=[main_box]
        )

        super().__init__(
            popup=True,
            kb_mode="exclusive",
            namespace="PowerMenu",
            exclusivity="ignore",
            visible=False,
            child=main_overlay,
            css_classes=["popup-close"],
            anchor=["left", "right", "top", "bottom"],
        )
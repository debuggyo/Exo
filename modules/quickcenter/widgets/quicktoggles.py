from ignis import widgets
from ignis.services.network import Wifi
from modules.m3components import Button
from user_settings import user_settings

def QuickToggle(icon, on_click=None, active=False, size="s", **kwargs):
    classes = ["quick-toggle"]
    if active:
        classes.append("active")

    btn = Button.button(
        css_classes=classes,
        on_click=lambda v: _handle_click(btn, on_click, v),
        icon=icon,
        size=size,
        valign="center",
        vexpand=False,
        **kwargs
    )

    def set_active(value: bool):
        if value and "active" not in btn.css_classes:
            btn.css_classes.append("active")
        elif not value and "active" in btn.css_classes:
            btn.css_classes.remove("active")

    btn.set_active = set_active
    btn.is_active = lambda: "active" in btn.css_classes

    btn.set_active(active)

    return btn

def _handle_click(btn, external_handler, value):
    currently_active = btn.is_active()
    btn.set_active(not currently_active)

    if external_handler:
        external_handler(not currently_active)
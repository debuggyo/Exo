from ignis import widgets
from modules.m3components import Button

class CategoryLabel(widgets.Label):
    def __init__(self, title):
        super().__init__(
            css_classes=["settings-category-label"],
            label=title,
            justify="left",
            halign="start"
        )

def make_toggle_buttons(items, get_value, set_value, on_any_click=None):
    buttons = []

    def update_active():
        for btn, value in buttons:
            if get_value() == value:
                btn.add_css_class("active")
                btn.add_css_class("filled")
            else:
                btn.remove_css_class("active")
                btn.remove_css_class("filled")

    for item in items:
        if len(item) == 3:
            label, value, icon = item
        else:
            label, value = item
            icon = None

        def click_handler(_, v=value, btn=None):
            set_value(v)
            update_active()
            if on_any_click:
                on_any_click()

        btn = Button.button(
            label=label,
            icon=icon,
            on_click=click_handler,
            shape="square",
            hexpand=True,
            halign="fill"
        )
        buttons.append((btn, value))

    update_active()
    return Button.connected_group([b for b, _ in buttons], homogeneous=False, halign="start", hexpand=False)

class SettingsRow(widgets.Box):
    def __init__(self, icon: str = None, title: str = None, description: str = None, child: list = None, vertical: bool = True, css_classes: list = [], **kwargs):
        header = []
        if icon:
            header.append(widgets.Label(label=icon, css_classes=["settings-row-icon"], halign="start"))
        if title:
            header.append(widgets.Label(label=title, css_classes=["settings-row-title"], halign="start"))
        if description:
            header.append( widgets.Label(label=description, css_classes=["settings-row-description"], halign="start") )

        children = child or []

        classes=["settings-row"]
        classes.extend(css_classes)

        super().__init__(
            css_classes=classes,
            vertical=vertical,
            hexpand=True,
            halign="fill",
            spacing=5,
            child=[
                widgets.Box(
                    vertical=True,
                    css_classes=["settings-row-header"],
                    valign="center",
                    halign="fill",
                    hexpand=True,
                    child=header,
                ),
                *children,
            ],
            **kwargs
        )

def SwitchRow(label: str, active, on_change, **kwargs):
    switch = widgets.Switch(
        active=active,
        valign="center",
        halign="end",
    )

    row_content = SettingsRow(
        title=label,
        vertical=False,
        css_classes=["switch-row"],
        child=[
            switch
        ],
        **kwargs
    )

    def on_button_click(_):
        new_active_state = not switch.active
        on_change(switch, new_active_state)
        switch.set_active(new_active_state)

    return widgets.Button(
        child=row_content,
        on_click=on_button_click,
        hexpand=True,
        halign="fill",
        css_classes=["row-button"]
    )
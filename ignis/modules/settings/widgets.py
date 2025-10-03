from ignis import widgets
from modules.m3components import Button


class CategoryLabel(widgets.Box):
    def __init__(self, title: str = None, icon: str = None):
        super().__init__(
            css_classes=["settings-category-label"],
            spacing=5,
            child=[
                widgets.Label(
                    css_classes=["m3-icon"],
                    label=icon,
                    justify="left",
                    halign="start",
                )
                if icon
                else None,
                widgets.Label(
                    label=title,
                    justify="left",
                    halign="start",
                ),
            ],
        )


def make_toggle_buttons(
    items, get_value, set_value, on_any_click=None, widget=None, bar_id=None
):
    buttons = []

    def update_active():
        for btn, value in buttons:
            if widget:  # if widget exists
                if get_value() == value and widget:
                    btn.add_css_class("active")
                    btn.add_css_class("filled")
                else:
                    btn.remove_css_class("active")
                    btn.remove_css_class("filled")
            else:  # otherwise, behave as before
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
            if bar_id:
                set_value(v, bar_id)
            elif widget:
                set_value(widget, v)
            else:
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
            halign="fill",
            size="xs",
        )
        buttons.append((btn, value))

    update_active()
    return Button.connected_group(
        [b for b, _ in buttons],
        homogeneous=False,
        halign="start",
        hexpand=False,
    )


def make_independent_toggle_buttons(items, on_any_click=None, bar_id=None):
    buttons = []

    def update_active():
        for btn, get_bool in buttons:
            is_active = get_bool()
            if is_active:
                btn.add_css_class("active")
                btn.add_css_class("filled")
            else:
                btn.remove_css_class("active")
                btn.remove_css_class("filled")

    for item in items:
        if len(item) == 4:
            label, get_bool, set_bool, icon = item
        else:
            label, get_bool, set_bool = item
            icon = None

        def click_handler(_, g=get_bool, s=set_bool):
            current_value = g()
            new_value = not current_value

            if bar_id:
                s(new_value, bar_id)
            else:
                s(new_value)

            update_active()
            if on_any_click:
                on_any_click()

        btn = Button.button(
            label=label,
            icon=icon,
            on_click=click_handler,
            shape="square",
            hexpand=True,
            halign="fill",
            size="xs",
        )
        buttons.append((btn, get_bool))

    update_active()

    return Button.connected_group(
        [b for b, _ in buttons],
        homogeneous=False,
        halign="start",
        hexpand=False,
    )


class SettingsRow(widgets.Box):
    def __init__(
        self,
        icon: str = None,
        title: str = None,
        description: str = None,
        child: list = None,
        vertical: bool = False,
        css_classes: list = [],
        **kwargs,
    ):
        header = []
        if icon:
            header.append(
                widgets.Label(
                    label=icon, css_classes=["settings-row-icon"], halign="start"
                )
            )
        if title:
            header.append(
                widgets.Label(
                    label=title, css_classes=["settings-row-title"], halign="start"
                )
            )
        if description:
            header.append(
                widgets.Label(
                    label=description,
                    css_classes=["settings-row-description"],
                    halign="start",
                )
            )

        children = child or []

        classes = ["settings-row"]
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
            **kwargs,
        )


def SwitchRow(active, on_change, **kwargs):
    switch = widgets.Switch(
        active=active,
        valign="center",
        halign="end",
    )

    row_content = SettingsRow(
        vertical=False,
        css_classes=["switch-row"],
        child=[switch],
        **kwargs,
    )

    row_content.remove_css_class("settings-row")

    def on_button_click(_):
        new_active_state = not switch.active
        on_change(switch, new_active_state)
        switch.set_active(new_active_state)

    return widgets.Button(
        child=row_content,
        on_click=on_button_click,
        hexpand=True,
        halign="fill",
        css_classes=["settings-row", "row-button"],
    )

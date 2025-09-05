from ignis import widgets

class Button(widgets.Button):
    @staticmethod
    def button(
        icon: str = None,
        label: str = None,
        on_click=None,
        type="tonal",
        size="s",
        shape="round",
        css_classes: list = None,
        ialign: str = "center",
        vertical: bool = False,  # NEW
        **kwargs  # catch-all for extra args
    ):
        if on_click is None:
            on_click = lambda *_: None

        classes = ["m3-button", type, size, shape]
        if css_classes:
            classes.extend(css_classes)

        children = []
        if icon:
            children.append(widgets.Label(label=icon, css_classes=["m3-button-icon"], halign="center", hexpand=False))
            if not label:
                classes.append("icon-only")
        if label:
            children.append(widgets.Label(label=label, css_classes=["m3-button-label"]))

        # spacing between icon + label depends on size
        gap = {
            "xs": 8,
            "s": 8,
            "m": 8,
            "l": 12,
            "xl": 16
        }.get(size, 8)

        return widgets.Button(
            css_classes=classes,
            on_click=on_click,
            child=widgets.Box(
                vertical=vertical,     # 👈 stack vertically when requested
                spacing=gap,
                child=children,
                halign=ialign,
            ),
            **kwargs
        )

    @staticmethod
    def connected_group(child, **kwargs):
        return widgets.Box(
            vertical=False,
            spacing=2,
            css_classes=["connected-button-group"],
            child=child,
            **kwargs
        )

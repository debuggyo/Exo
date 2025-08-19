from ignis import widgets

class Button(widgets.Button):
    @staticmethod

    # Button
    def button(icon: str = None, label: str = None, on_click=None, type="tonal", size="s", shape="round", hexpand: bool = False, halign: str = "start", valign: str = "start", css_classes: list = []):

        if on_click is None:
            on_click = lambda _: None

        classes = ["m3-button"]
        classes.append(type)
        classes.append(size)
        classes.append(shape)
        classes.extend(css_classes)

        children = []
        if icon:
            children.append(widgets.Label(label=icon, css_classes=["m3-button-icon"]))
            if not label:
                classes.append("icon-only")
        if label:
            children.append(widgets.Label(label=label, css_classes=["m3-button-label"]))

        # Change gap between icon and label based on size
        if size == "xs" or size == "s" or size == "m":
            gap = 8
        elif size == "l":
            gap = 12
        elif size == "xl":
            gap = 16
        else:
            gap = 8

        return widgets.Button(
            css_classes=classes,
            on_click=on_click,
            hexpand=hexpand,
            halign=halign,
            child=widgets.Box(
                vertical=False,
                spacing=gap,
                child=children,
                halign="center",
            )
        )

    # Toggle Button


    # Icon Button


    # Split Button


    # Connected Button Group
    def connected_group(child, homogeneous: bool = False):
        return widgets.Box(
            vertical=False,
            spacing=2,
            homogeneous=homogeneous,
            css_classes=["connected-button-group"],
            child=child
        )

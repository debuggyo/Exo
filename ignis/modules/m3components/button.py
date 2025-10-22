from ignis import widgets
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty


class Button(widgets.Button, BaseWidget):
    __gtype_name__ = "M3Button"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        widgets.Button.__init__(self)
        self._icon = ""
        self._label = ""
        self._type = "tonal"
        self._size = "s"
        self._shape = "round"
        self._ialign = "center"
        self._vertical = False

        self.button_icon = widgets.Label(label=self._icon, css_classes=["m3-button-icon"], halign="center", hexpand=False, visible=False)
        self.button_label = widgets.Label(label=self._label, css_classes=["m3-button-label"], visible=False)

        gap = {"xs": 8, "s": 8, "m": 8, "l": 12, "xl": 16}.get(self._size, 8)

        self.container = widgets.Box(
            vertical=self._vertical,
            spacing=gap,
            halign=self._ialign,
            valign="center",
            child=[self.button_icon, self.button_label]
        )

        BaseWidget.__init__(self, **kwargs)
        self.set_child(self.container)
        self.update()


    @IgnisProperty
    def icon(self) -> str:
        return self._icon

    @icon.setter
    def icon(self, value: str) -> None:
        self._icon = value
        self.button_icon.set_label(value)

    @IgnisProperty
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = value
        self.button_label.set_label(value)

    @IgnisProperty
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        self._type = value
        self.update()

    @IgnisProperty
    def size(self) -> str:
        return self._size

    @size.setter
    def size(self, value: str) -> None:
        self._size = value
        self.update()

    @IgnisProperty
    def shape(self) -> str:
        return self._shape

    @shape.setter
    def shape(self, value: str) -> None:
        self._shape = value
        self.update()

    @IgnisProperty
    def ialign(self) -> str:
        return self._ialign

    @ialign.setter
    def ialign(self, value: str) -> None:
        self._ialign = value
        self.container.set_halign(value)

    @IgnisProperty
    def vertical(self) -> bool:
        return self._vertical

    @vertical.setter
    def vertical(self, value: bool) -> None:
        self._vertical = value
        self.container.set_vertical(value)

    def update(self):
        classes = [
            "elevated", "filled", "tonal", "outlined", "text",
            "xs", "s", "m", "l", "xl",
            "round", "square"
        ]
        for style in classes:
            self.remove_css_class(style)

        self.add_css_class("m3-button")
        self.add_css_class(self._type)
        self.add_css_class(self._size)
        self.add_css_class(self._shape)

        self.button_icon.set_visible(True if self._icon else False)
        self.button_label.set_visible(True if self._label else False)

class ConnectedButtonGroup(widgets.Box, BaseWidget):
    __gtype_name__ = "M3ConnectedButtonGroup"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, children, **kwargs):
        widgets.Box.__init__(self, vertical=False, vexpand=False, spacing=2)
        self.add_css_class("connected-button-group")
        for child in children:
            self.append(child)
        BaseWidget.__init__(self, **kwargs)

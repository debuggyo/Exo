import asyncio
from ignis import widgets, utils
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
import modules.m3components as m3


class Action(widgets.EventBox, BaseWidget):
    __gtype_name__ = "ExoAction"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        self._icon_name: str = "edit"
        self._label: str = ""
        self._left_click: str = "notify-send 'Example' 'Exo Action Module'"
        self._right_click: str = "notify-send 'Example' 'Exo Action Module'"
        self._middle_click: str = "notify-send 'Example' 'Exo Action Module'"
        self._scroll_up: str = "notify-send 'Example' 'Exo Action Module'"
        self._scroll_down: str = "notify-send 'Example' 'Exo Action Module'"

        widgets.EventBox.__init__(
            self,
            spacing=8,
            on_click=self._on_click,
            on_right_click=self._on_right_click,
            on_middle_click=self._on_middle_click,
            on_scroll_up=self._on_scroll_up,
            on_scroll_down=self._on_scroll_down,
        )

        self.icon = m3.Icon(self._icon_name, 16, halign="center", valign="center")
        self.text = widgets.Label(label=self._label, halign="center", valign="center")
        self.append(self.icon)
        self.append(self.text)

        self.connect("notify::vertical", self.update_layout)

        self.add_css_class("exo-action")
        self.update_layout()
        BaseWidget.__init__(self, **kwargs)

    def _on_click(self, *args):
        asyncio.create_task(utils.exec_sh_async(self._left_click))

    def _on_right_click(self, *args):
        asyncio.create_task(utils.exec_sh_async(self._right_click))

    def _on_middle_click(self, *args):
        asyncio.create_task(utils.exec_sh_async(self._middle_click))

    def _on_scroll_up(self, *args):
        asyncio.create_task(utils.exec_sh_async(self._scroll_up))

    def _on_scroll_down(self, *args):
        asyncio.create_task(utils.exec_sh_async(self._scroll_down))

    @IgnisProperty
    def icon_name(self) -> str:
        return self._icon_name

    @icon_name.setter
    def icon_name(self, value: str) -> None:
        if value == self._icon_name:
            return
        self._icon_name = value
        self.icon.set_icon(value)

    @IgnisProperty
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        if value == self._label:
            return
        self._label = value
        self.text.set_label(value)
        self.update_layout()

    @IgnisProperty
    def left_click(self) -> str:
        return self._left_click

    @left_click.setter
    def left_click(self, value: str) -> None:
        if value == self._left_click:
            return
        self._left_click = value

    @IgnisProperty
    def right_click(self) -> str:
        return self._right_click

    @right_click.setter
    def right_click(self, value: str) -> None:
        if value == self._right_click:
            return
        self._right_click = value

    @IgnisProperty
    def middle_click(self) -> str:
        return self._middle_click

    @middle_click.setter
    def middle_click(self, value: str) -> None:
        if value == self._middle_click:
            return
        self._middle_click = value

    @IgnisProperty
    def scroll_up(self) -> str:
        return self._scroll_up

    @scroll_up.setter
    def scroll_up(self, value: str) -> None:
        if value == self._scroll_up:
            return
        self._scroll_up = value

    @IgnisProperty
    def scroll_down(self) -> str:
        return self._scroll_down

    @scroll_down.setter
    def scroll_down(self, value: str) -> None:
        if value == self._scroll_down:
            return
        self._scroll_down = value

    def update_layout(self, *args):
        if self._label and not self.vertical:
            self.text.set_visible(True)
            self.add_css_class("has-label")
        else:
            self.text.set_visible(False)
            self.remove_css_class("has-label")

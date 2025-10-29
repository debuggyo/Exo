from ignis import widgets, utils
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
from gi.repository import Gtk, GObject
import modules.m3components as m3

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

        btn = m3.Button(
            label=label,
            icon=icon,
            on_click=click_handler,
            shape="square",
            vexpand=False,
            hexpand=True,
            halign="fill",
            valign="center",
            size="xs",
        )
        buttons.append((btn, value))

    update_active()

    button_group = m3.ConnectedButtonGroup(
        [b for b, _ in buttons],
        homogeneous=False,
        halign="start",
        hexpand=False,
    )
    button_group.buttons = buttons
    button_group.update_active = update_active
    return button_group


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

        btn = m3.Button(
            label=label,
            icon=icon,
            on_click=click_handler,
            shape="square",
            hexpand=True,
            vexpand=False,
            halign="fill",
            valign="center",
            size="xs",
        )
        buttons.append((btn, get_bool))

    update_active()

    button_group = m3.ConnectedButtonGroup(
        [b for b, _ in buttons],
        homogeneous=False,
        halign="start",
        hexpand=False,
    )
    button_group.buttons = buttons
    button_group.update_active = update_active
    return button_group

class Row(Gtk.Box, BaseWidget):
    __gtype_name__ = "SettingsRow"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, spacing=8)
        self._icon_name: str = None
        self._title: str = None
        self._description: str = None
        self._child = None

        self.icon = m3.Icon(self._icon_name, 16, visible=False)
        self.info_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=0, hexpand=True, valign="center"
        )
        self.title_label = Gtk.Label(halign="start", valign="center", vexpand=True)
        self.description_label = Gtk.Label(halign="start", valign="center", vexpand=True)

        self.info_box.append(self.title_label)
        self.info_box.append(self.description_label)

        self.append(self.icon)
        self.append(self.info_box)
        if self._child:
            self.append(self._child)
            self._child.set_vexpand(False)
            self._child.set_valign(Gtk.Align.Center)

        self.title_label.set_visible(True if self._title else False)
        self.description_label.set_visible(True if self._description else False)

        self.add_css_class("exo-settings-row")
        self.title_label.add_css_class("title")
        self.description_label.add_css_class("description")
        BaseWidget.__init__(self, **kwargs)

    @IgnisProperty
    def icon_name(self) -> str:
        return self._icon_name

    @icon_name.setter
    def icon_name(self, value: str) -> None:
        if value == self._icon_name:
            return
        self._icon_name = value
        self.icon.set_icon(value)
        self.icon.set_visible(True if self._icon_name else False)

    @IgnisProperty
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if value == self._title:
            return
        self._title = value
        self.title_label.set_text(value)
        self.title_label.set_visible(True if self._title else False)

    @IgnisProperty
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        if value == self._description:
            return
        self._description = value
        self.description_label.set_text(value)
        self.description_label.set_visible(True if self._description else False)

    @IgnisProperty
    def child(self):
        return self._child

    @child.setter
    def child(self, value) -> None:
        if value == self._child:
            return
        self._child = value
        if self._child:
            self.append(self._child)
            self._child.set_vexpand(False)


class SwitchRow(Row):
    __gtype_name__ = "SwitchRow"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        self._option = False
        self._option_target = None
        self._option_property = None
        self.switch = widgets.Switch(active=self._option, vexpand=False, valign="center", sensitive=False)
        Row.__init__(self, **kwargs)

        self.set_child(self.switch)

        click_controller = Gtk.GestureClick.new()
        click_controller.connect("pressed", self.toggle_option)
        self.add_controller(click_controller)

        self.switch.connect("notify::active", self._on_switch_toggled)
        self.add_css_class("switch-row")

    def bind_option(self, target_object, property_name: str):
        """Binds the switch's option to a property on a target object."""
        self._option_target = target_object
        self._option_property = property_name

        initial_value = getattr(target_object, property_name, False)
        self.option = initial_value

        self.connect("notify::option", self._update_bound_property)

    def _update_bound_property(self, *args):
        """Handler to update the bound property."""
        if self._option_target and self._option_property:
            current_value = getattr(self._option_target, self._option_property)
            if current_value != self.option:
                setattr(self._option_target, self._option_property, self.option)

    @IgnisProperty
    def option(self) -> bool:
        return self._option

    @option.setter
    def option(self, value: bool) -> None:
        value = bool(value)
        if self._option == value:
            return
        self._option = value
        self.switch.set_active(value)
        self.notify("option")

    def toggle_option(self, *args):
        self.option = not self.option

    def _on_switch_toggled(self, switch, _):
        self.option = switch.get_active()


class SingleSelectRow(Row):
    __gtype_name__ = "SingleSelectRow"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        self._option = ""
        self._option_target = None
        self._option_property = None
        self._items = []
        self.buttons = None
        Row.__init__(self, **kwargs)

    def bind_option(self, target_object, property_name: str):
        """Binds the switch's option to a property on a target object."""
        self._option_target = target_object
        self._option_property = property_name

        initial_value = getattr(target_object, property_name, "")
        self.option = initial_value

        self.connect("notify::option", self._update_bound_property)

    def _update_bound_property(self, *args):
        """Handler to update the bound property."""
        if self._option_target and self._option_property:
            current_value = getattr(self._option_target, self._option_property)
            if current_value != self.option:
                setattr(self._option_target, self._option_property, self.option)

    @IgnisProperty
    def items(self) -> list:
        return self._items

    @items.setter
    def items(self, value: list) -> None:
        self._items = value
        self.buttons = make_toggle_buttons(
            self._items,
            lambda: self.option,
            lambda v: setattr(self, "option", v),
        )
        self.set_child(self.buttons)

    @GObject.Property
    def option(self) -> str:
        return self._option

    @option.setter
    def option(self, value: str) -> None:
        if self._option == value:
            return
        self._option = value
        if self.buttons:
            self.buttons.update_active()
        self.notify("option")


class MultiSelectRow(Row):
    __gtype_name__ = "MultiSelectRow"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        self._items = []
        self.buttons = None
        Row.__init__(self, **kwargs)

    @IgnisProperty
    def items(self) -> list:
        return self._items

    @items.setter
    def items(self, value: list) -> None:
        self._items = value
        self.buttons = make_independent_toggle_buttons(
            self._items,
        )
        self.set_child(self.buttons)


class Window(widgets.Window, BaseWidget):
    __gtype_name__ = "SettingsWindow"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        self.title_label = Gtk.Label(label=self.title, halign=Gtk.Align.START)
        self.title_label.add_css_class("options-window-title")
        self.title_bar = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=5,
            hexpand=True,
            halign=Gtk.Align.FILL,
        )
        self.title_bar.add_css_class("options-window-title-bar")
        self.title_bar.append(self.title_label)

        self.scrollable_content = widgets.Box(vertical=True, spacing=0, css_classes=["scrollable"])
        scrolled_window = widgets.Scroll(
            child=self.scrollable_content,
            vexpand=True,
        )

        self.container = widgets.Box(
            vertical=True,
            child=[self.title_bar, scrolled_window],
        )
        self.container.add_css_class("exo-options-window")

        self._build_content()

        self.actual_settings_content_box = widgets.Box(
            vertical=True,
            spacing=0,
            hexpand=False,
            halign="center",
            valign="center",
            css_classes=["settings-window-content"],
            child=[self.container],
        )
        self.actual_settings_content_box.set_width_request(800)
        self.actual_settings_content_box.set_height_request(600)

        background_close_button = widgets.Button(
            vexpand=True,
            hexpand=True,
            can_focus=False,
            on_click=self.close,
        )

        main_overlay = widgets.Overlay(
            child=background_close_button,
            overlays=[self.actual_settings_content_box],
            css_classes=["popup-close"],
        )

        namespace = kwargs.get("namespace", f'{kwargs.get("title", "").replace(" ", "")}SettingsWindow')

        widgets.Window.__init__(
            self,
            namespace=namespace,
            visible=False,
            child=main_overlay,
            popup=True,
            layer="overlay",
            exclusivity="ignore",
            kb_mode="exclusive",
            anchor=["left", "right", "top", "bottom"],
        )
        self.add_css_class("popup-close")

        BaseWidget.__init__(self, **kwargs)

    def _build_content(self):
        child = self.scrollable_content.get_first_child()
        while child:
            self.scrollable_content.remove(child)
            child = self.scrollable_content.get_first_child()

        if self.content:
            for c in self.content:
                self.scrollable_content.append(c)

    def close(self, *args):
        self.set_visible(False)

    @IgnisProperty
    def title(self) -> str:
        return getattr(self, "_title", "Settings")

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        if hasattr(self, "title_label"):
            self.title_label.set_text(value)

    @IgnisProperty
    def content(self) -> list:
        return getattr(self, "_content", [])

    @content.setter
    def content(self, value) -> None:
        self._content = value
        if hasattr(self, "container"):
            self._build_content()

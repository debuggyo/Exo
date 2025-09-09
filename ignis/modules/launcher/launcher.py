import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from ignis.services.applications.application import Application
from ignis import widgets
from ignis.window_manager import WindowManager
from ignis.services.applications import ApplicationsService
from modules.m3components import Button
applications = ApplicationsService.get_default()
window_manager = WindowManager.get_default()

GRID_COLUMNS = 5

class AppItem(widgets.Button):
    def __init__(self, application: Application, launcher_instance: 'Launcher') -> None:
        self._application = application
        self._launcher = launcher_instance
        super().__init__(
            on_click=lambda x: self.launch(),
            css_classes=["app-item"],
            halign="fill",
            hexpand=True,
            child=widgets.Box(
                vertical=True,
                spacing=5,
                halign="center",
                valign="center",
                child=[
                    widgets.Icon(image=application.icon, pixel_size=32, halign="center"),
                    widgets.Label(label=application.name, halign="center", css_classes=["app-label"], ellipsize="end", max_width_chars=15)
                ]
            )
        )
        self.set_size_request(100, 100)

        self._gesture = Gtk.GestureClick.new()
        self._gesture.set_button(3)
        self._gesture.connect("released", self.__on_right_click_released)
        self.add_controller(self._gesture)

        self._application.connect("pinned", self.__on_app_state_change)
        self._application.connect("unpinned", self.__on_app_state_change)

    def __on_right_click_released(self, gesture, n_press, x, y):
        popover = Gtk.Popover.new()
        popover.set_parent(self)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        if self._application.is_pinned:
            action_button = Gtk.Button.new_with_label("Unpin")
            action_button.connect("clicked", lambda b: self.__unpin_app(popover))
        else:
            action_button = Gtk.Button.new_with_label("Pin")
            action_button.connect("clicked", lambda b: self.__pin_app(popover))

        box.append(action_button)

        popover.set_child(box)
        popover.popup()

    def __pin_app(self, popover):
        self._application.pin()
        popover.popdown()

    def __unpin_app(self, popover):
        self._application.unpin()
        popover.popdown()

    def __on_app_state_change(self, app):
        self._launcher.refresh_pinned_apps_list()

    def launch(self) -> None:
        self._application.launch(terminal_format="kitty %command%")
        window_manager.close_window("Launcher")

class FeaturedAppItem(widgets.Button):
    def __init__(self, application: Application, launcher_instance: 'Launcher') -> None:
        self._application = application
        self._launcher = launcher_instance
        super().__init__(
            on_click=lambda x: self.launch(),
            css_classes=["app-item"],
            halign="fill",
            hexpand=True,
            child=widgets.Box(
                vertical=False,
                spacing=10,
                halign="start",
                valign="center",
                child=[
                    widgets.Icon(image=application.icon, pixel_size=32, halign="center"),
                    widgets.Label(label=application.name, halign="start", css_classes=["app-label"], ellipsize="end")
                ]
            )
        )
        self.set_size_request(-1, 80)

        self._gesture = Gtk.GestureClick.new()
        self._gesture.set_button(3)
        self._gesture.connect("released", self.__on_right_click_released)
        self.add_controller(self._gesture)

        self._application.connect("pinned", self.__on_app_state_change)
        self._application.connect("unpinned", self.__on_app_state_change)

    def __on_right_click_released(self, gesture, n_press, x, y):
        popover = Gtk.Popover.new()
        popover.set_parent(self)
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        if self._application.is_pinned:
            action_button = Gtk.Button.new_with_label("Unpin")
            action_button.connect("clicked", lambda b: self.__unpin_app(popover))
        else:
            action_button = Gtk.Button.new_with_label("Pin")
            action_button.connect("clicked", lambda b: self.__pin_app(popover))

        box.append(action_button)
        popover.set_child(box)
        popover.popup()

    def __pin_app(self, popover):
        self._application.pin()
        popover.popdown()

    def __unpin_app(self, popover):
        self._application.unpin()
        popover.popdown()

    def __on_app_state_change(self, app):
        self._launcher.refresh_pinned_apps_list()

    def launch(self) -> None:
        self._application.launch(terminal_format="kitty %command%")
        window_manager.close_window("Launcher")


class PinnedAppItem(widgets.Button):
    def __init__(self, application: Application, launcher_instance: 'Launcher') -> None:
        self._application = application
        self._launcher = launcher_instance
        super().__init__(
            on_click=lambda x: self.launch(),
            css_classes=["pinned-item"],
            child=widgets.Icon(image=application.icon, pixel_size=32, halign="center")
        )
        self.set_size_request(64, 64)

        self._gesture = Gtk.GestureClick.new()
        self._gesture.set_button(3)
        self._gesture.connect("released", self.__on_right_click_released)
        self.add_controller(self._gesture)

        self._application.connect("pinned", self.__on_app_state_change)
        self._application.connect("unpinned", self.__on_app_state_change)

    def __on_right_click_released(self, gesture, n_press, x, y):
        popover = Gtk.Popover.new()
        popover.set_parent(self)
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        if self._application.is_pinned:
            action_button = Gtk.Button.new_with_label("Unpin")
            action_button.connect("clicked", lambda b: self.__unpin_app(popover))
        else:
            action_button = Gtk.Button.new_with_label("Pin")
            action_button.connect("clicked", lambda b: self.__pin_app(popover))

        box.append(action_button)
        popover.set_child(box)
        popover.popup()

    def __pin_app(self, popover):
        self._application.pin()
        popover.popdown()

    def __unpin_app(self, popover):
        self._application.unpin()
        popover.popdown()

    def __on_app_state_change(self, app):
        self._launcher.refresh_pinned_apps_list()

    def launch(self) -> None:
        self._application.launch(terminal_format="kitty %command%")
        window_manager.close_window("Launcher")


class Launcher(widgets.Window):
    def __init__(self):
        self._main_content_container = widgets.Box(
            vertical=True,
            spacing=0,
            css_classes=["main-content-container"],
            halign="fill",
            hexpand=True
        )

        self._pinned_apps_container = widgets.Box(
            spacing=10,
            css_classes=["pinned-apps-container"],
            height_request=64,
            vexpand=True,
        )

        self._pin_icon = widgets.Label(
            label="push_pin",
            css_classes=["icon", "pin-icon"],
            valign="end",
            vexpand=True
        )
        self._pin_hint_label = widgets.Label(
            label="Right click on an item to pin it.",
            css_classes=["pin-hint-label"],
            valign="start",
            vexpand=True
        )

        self._app_grid_container = widgets.Box(
            vertical=True,
            spacing=5,
            css_classes=["inner-box"],
            halign="fill",
            hexpand=True,
        )
        self._first_row = None

        search_icon = widgets.Label(
            label="search",
            css_classes=["icon", "search-icon"]
        )

        self._entry = widgets.Entry(
            placeholder_text="Search",
            css_classes=["launcher-search"],
            on_change=self.__search,
            on_accept=self.__on_accept,
            hexpand=True
        )

        self._clear_button = Button.button(
            on_click=self.__clear_search,
            icon="close",
            visible=False,
            size="xs",
            vexpand=False,
            css_classes=["clear-button"]
        )

        search_bar_container = widgets.Box(
            child=[search_icon, self._entry, self._clear_button],
            spacing=5,
            css_classes=["search-bar-container"]
        )

        self._entry.text = ""
        self.__populate_pinned_apps_list()
        self.__populate_grid([])

        self._main_content_container.append(search_bar_container)

        self._pinned_revealer = widgets.Revealer(
            transition_type='slide_down',
            reveal_child=True
        )
        self._pinned_revealer.set_child(self._pinned_apps_container)
        self._main_content_container.append(self._pinned_revealer)

        self._scroll_container = widgets.Scroll(
            vexpand=True,
            valign="fill",
            css_classes=["outer-box"],
            child=self._app_grid_container,
            height_request=550
        )
        self._scroll_container.set_overflow(Gtk.Overflow.HIDDEN)
        
        self._scroll_revealer = widgets.Revealer(
            transition_type='slide_down',
            reveal_child=False
        )
        self._scroll_revealer.set_child(self._scroll_container)
        self._main_content_container.append(self._scroll_revealer)

        actual_launcher_content_box = widgets.Box(
            vertical=True,
            spacing=0,
            hexpand=False,
            halign="center",
            valign="center",
            css_classes=["launcher-window"],
            child=[
                self._main_content_container
            ]
        )
        actual_launcher_content_box.width_request = 600

        close_button = widgets.Button(
            vexpand=True,
            hexpand=True,
            can_focus=False,
            on_click=lambda x: window_manager.close_window("Launcher")
        )

        main_overlay = widgets.Overlay(
            css_classes=["popup-close"],
            child=close_button,
            overlays=[actual_launcher_content_box]
        )

        super().__init__(
            css_classes=["popup-close"],
            hide_on_close=True,
            visible=False,
            namespace="Launcher",
            popup=True,
            layer="overlay",
            kb_mode="exclusive",
            anchor=["left", "right", "top", "bottom"],
            default_width=600,
            setup=lambda self: self.connect("notify::visible", self.__on_open),
            child=main_overlay
        )

    def refresh_pinned_apps_list(self):
        self.__populate_pinned_apps_list()

    def __populate_pinned_apps_list(self):
        while self._pinned_apps_container.get_last_child():
            self._pinned_apps_container.remove(self._pinned_apps_container.get_last_child())

        pinned_apps = applications.pinned

        if not pinned_apps:
            self._pinned_apps_container.set_orientation('vertical')
            self._pinned_apps_container.set_halign('center')
            self._pinned_apps_container.set_spacing(5)
            self._pinned_apps_container.append(self._pin_icon)
            self._pinned_apps_container.append(self._pin_hint_label)
            self._pinned_apps_container.visible = True
        else:
            self._pinned_apps_container.set_orientation('horizontal')
            self._pinned_apps_container.set_halign('start')
            self._pinned_apps_container.set_spacing(10)
            self._pinned_apps_container.visible = True
            for app in pinned_apps:
                item = PinnedAppItem(app, self)
                self._pinned_apps_container.append(item)


    def __populate_grid(self, apps: list[Application], featured_app: Application | None = None) -> None:
        last_child = self._app_grid_container.get_last_child()
        while last_child:
            self._app_grid_container.remove(last_child)
            last_child = self._app_grid_container.get_last_child()

        self._first_row = None

        if not apps and not featured_app:
            return

        if featured_app:
            first_item = FeaturedAppItem(featured_app, self)
            first_item.hexpand = True

            self._first_row = widgets.Box(spacing=5, css_classes=["app-row"], child=[first_item])
            self._first_row.add_css_class("featured-app-row")
            self._app_grid_container.append(self._first_row)

        app_grid = widgets.Grid(
            column_spacing=0,
            row_spacing=0,
            halign="fill",
            hexpand=True,
        )
        self._app_grid_container.append(app_grid)

        remaining_apps = apps

        for i, app in enumerate(remaining_apps):
            row = i // GRID_COLUMNS
            col = i % GRID_COLUMNS

            app_grid.attach(AppItem(app, self), col, row, 1, 1)

    def __search(self, *args) -> None:
        query = self._entry.text

        self._clear_button.visible = bool(query)

        if query:
            self._pinned_revealer.set_reveal_child(False)
            self._scroll_revealer.set_reveal_child(True)

            apps = applications.search(applications.apps, query)
            featured_app = apps[0] if apps else None
            remaining_apps = apps[1:] if apps else []
            self.__populate_grid(remaining_apps, featured_app)
        else:
            self._pinned_revealer.set_reveal_child(True)
            self._scroll_revealer.set_reveal_child(False)

    def __clear_search(self, *args) -> None:
        self._entry.text = ""
        self._entry.grab_focus()
        self.__search()

    def __on_open(self, *args) -> None:
        if not self.visible:
            return

        self._entry.text = ""
        self._entry.grab_focus()
        self._entry.set_position(-1)
        self.__populate_pinned_apps_list()
        self.__search()

    def __on_accept(self, *args) -> None:
        if self._first_row and self._first_row.child:
            self._first_row.child[0].launch()
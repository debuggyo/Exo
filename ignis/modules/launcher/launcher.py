import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from ignis.services.applications.application import Application
from ignis import widgets
from ignis.window_manager import WindowManager
from ignis.services.applications import ApplicationsService
from modules.m3components import Button
from ignis.menu_model import IgnisMenuModel, IgnisMenuItem, IgnisMenuSeparator
from user_settings import user_settings

applications = ApplicationsService.get_default()
window_manager = WindowManager.get_default()

GRID_COLUMNS = 5


class AppItem(widgets.Button):
    def __init__(
        self,
        application: Application,
        launcher_instance: "Launcher",
        is_featured: bool = False,
        layout: str = "grid",
    ) -> None:
        self._application = application
        self._launcher = launcher_instance

        if is_featured or layout == "list":
            child_widget = widgets.Box(
                vertical=False,
                spacing=10,
                halign="start",
                valign="center",
                child=[
                    widgets.Icon(
                        image=application.icon, pixel_size=32, halign="center"
                    ),
                    widgets.Box(
                        vertical=True,
                        halign="start",
                        valign="center",
                        child=[
                            widgets.Label(
                                label=application.name,
                                halign="start",
                                css_classes=["app-label"],
                                ellipsize="end",
                            ),
                            widgets.Label(
                                label=application.description,
                                halign="start",
                                css_classes=["app-description"],
                                ellipsize="end",
                            )
                            if application.description
                            else None,
                        ],
                    ),
                ],
            )
        else:  # grid layout
            child_widget = widgets.Box(
                vertical=True,
                spacing=5,
                halign="center",
                valign="center",
                child=[
                    widgets.Icon(
                        image=application.icon, pixel_size=32, halign="center"
                    ),
                    widgets.Label(
                        label=application.name,
                        halign="center",
                        css_classes=["app-label"],
                        ellipsize="end",
                    ),
                ],
            )

        super().__init__(
            on_click=lambda x: self.launch(),
            css_classes=["app-item"],
            halign="fill",
            hexpand=True,
            child=child_widget,
        )

        if is_featured or layout == "list":
            self.set_size_request(100, 50)
        else:
            self.set_size_request(100, 100)

        self._gesture = Gtk.GestureClick.new()
        self._gesture.set_button(3)
        self._gesture.connect("released", self.__on_right_click_released)
        self.add_controller(self._gesture)

        self._application.connect("pinned", self.__on_app_state_change)
        self._application.connect("unpinned", self.__on_app_state_change)

    def __on_right_click_released(self, gesture, n_press, x, y):
        menu_items = [
            IgnisMenuItem(label=self._application.name, enabled=False),
            IgnisMenuSeparator(),
            IgnisMenuItem(
                label="Unpin App" if self._application.is_pinned else "Pin App",
                on_activate=lambda item, app=self._application: (
                    self.__unpin_app() if app.is_pinned else self.__pin_app()
                ),
            ),
        ]

        if self._application.actions:
            menu_items.append(IgnisMenuSeparator())
            for action in self._application.actions:
                menu_items.append(
                    IgnisMenuItem(
                        label=action.name,
                        on_activate=lambda item, act=action: (
                            act.launch(),
                            window_manager.close_window("Launcher"),
                        ),
                    )
                )

        popover = widgets.PopoverMenu(model=IgnisMenuModel(*menu_items))
        if self.get_child():
            self.get_child().append(popover)
        popover.popup()

    def __pin_app(self):
        self._application.pin()

    def __unpin_app(self):
        self._application.unpin()

    def __on_app_state_change(self, app):
        self._launcher.refresh_pinned_apps_list()

    def launch(self) -> None:
        self._application.launch(terminal_format="kitty %command%")
        window_manager.close_window("Launcher")


class PinnedAppItem(widgets.Button):
    def __init__(self, application: Application, launcher_instance: "Launcher") -> None:
        self._application = application
        self._launcher = launcher_instance
        super().__init__(
            on_click=lambda x: self.launch(),
            css_classes=["pinned-item"],
            child=widgets.Box(
                halign="center",
                valign="center",
                child=[
                    widgets.Icon(image=application.icon, pixel_size=32, halign="center")
                ],
            ),
        )
        self.set_size_request(64, 64)

        self._gesture = Gtk.GestureClick.new()
        self._gesture.set_button(3)
        self._gesture.connect("released", self.__on_right_click_released)
        self.add_controller(self._gesture)

        self._application.connect("pinned", self.__on_app_state_change)
        self._application.connect("unpinned", self.__on_app_state_change)

    def __on_right_click_released(self, gesture, n_press, x, y):
        menu_items = [
            IgnisMenuItem(label=self._application.name, enabled=False),
            IgnisMenuSeparator(),
            IgnisMenuItem(
                label="Unpin App" if self._application.is_pinned else "Pin App",
                on_activate=lambda item, app=self._application: (
                    self.__unpin_app() if app.is_pinned else self.__pin_app()
                ),
            ),
        ]

        if self._application.actions:
            menu_items.append(IgnisMenuSeparator())
            for action in self._application.actions:
                menu_items.append(
                    IgnisMenuItem(
                        label=action.name,
                        on_activate=lambda item, act=action: (
                            act.launch(),
                            window_manager.close_window("Launcher"),
                        ),
                    )
                )

        popover = widgets.PopoverMenu(model=IgnisMenuModel(*menu_items))
        if self.get_child():
            self.get_child().append(popover)
        popover.popup()

    def __pin_app(self):
        self._application.pin()

    def __unpin_app(self):
        self._application.unpin()

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
            hexpand=True,
        )

        self._pinned_apps_container = widgets.Grid(
            css_classes=["pinned-apps-container"],
            height_request=64,
            vexpand=True,
        )
        self._pinned_apps_container.set_column_spacing(10)
        self._pinned_apps_container.set_row_spacing(10)

        self._pin_icon = widgets.Label(
            label="push_pin",
            css_classes=["icon", "pin-icon"],
            valign="end",
            vexpand=True,
        )
        self._pin_hint_label = widgets.Label(
            label="Right click on an item to pin it.",
            css_classes=["pin-hint-label"],
            valign="start",
            vexpand=True,
        )

        self._app_container = widgets.Box(
            vertical=True,
            spacing=5,
            css_classes=["inner-box"],
            halign="fill",
            hexpand=True,
        )

        search_icon = widgets.Label(label="search", css_classes=["icon", "search-icon"])

        self._entry = widgets.Entry(
            placeholder_text="Search",
            css_classes=["launcher-search"],
            on_change=self.__search,
            on_accept=self.__on_accept,
            hexpand=True,
        )

        self._clear_button = Button.button(
            on_click=self.__clear_search,
            icon="close",
            visible=False,
            size="xs",
            type="text",
            vexpand=False,
            css_classes=["clear-button"],
        )

        self._layout_button = Button.button(
            on_click=self.__toggle_layout,
            icon="",
            visible=False,
            size="xs",
            type="text",
            vexpand=False,
            css_classes=["layout-toggle-button"],
        )

        self._search_bar_container = widgets.Box(
            child=[search_icon, self._entry, self._clear_button, self._layout_button],
            spacing=5,
            css_classes=["search-bar-container"],
            hexpand=True,
        )

        self.__update_layout_button_icon()
        self.__populate_pinned_apps_list()

        self._main_content_container.append(self._search_bar_container)

        self._pinned_revealer = widgets.Revealer(
            transition_type="slide_down", reveal_child=True
        )
        self._pinned_revealer.set_child(self._pinned_apps_container)
        self._main_content_container.append(self._pinned_revealer)

        self._scroll_container = widgets.Scroll(
            vexpand=True,
            valign="fill",
            css_classes=["outer-box"],
            child=self._app_container,
            height_request=550,
        )
        self._scroll_container.set_overflow(Gtk.Overflow.HIDDEN)

        self._scroll_revealer = widgets.Revealer(
            transition_type="slide_down", reveal_child=False
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
            child=[self._main_content_container],
        )
        actual_launcher_content_box.width_request = 600

        close_button = widgets.Button(
            vexpand=True,
            hexpand=True,
            can_focus=False,
            on_click=lambda x: window_manager.close_window("Launcher"),
        )

        main_overlay = widgets.Overlay(
            css_classes=["popup-close"],
            child=close_button,
            overlays=[actual_launcher_content_box],
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
            setup=lambda self: self.connect(
                "notify::visible", self.__on_visibility_change
            ),
            child=main_overlay,
        )

    def __update_layout_button_icon(self):
        current_layout = user_settings.interface.launcher.layout
        if current_layout == "grid":
            new_icon = "view_list"
        else:
            new_icon = "grid_view"

        # Remove the old button
        if self._layout_button.get_parent():
            self._layout_button.get_parent().remove(self._layout_button)

        # Rebuild the button with the new icon
        self._layout_button = Button.button(
            on_click=self.__toggle_layout,
            icon=new_icon,
            size="xs",
            type="text",
            vexpand=False,
            css_classes=["layout-toggle-button"],
        )

        # Re-add the button to the search container
        self._search_bar_container.append(self._layout_button)

    def __toggle_layout(self, *args):
        current_layout = user_settings.interface.launcher.layout
        if current_layout == "grid":
            user_settings.interface.launcher.layout = "list"
        else:
            user_settings.interface.launcher.layout = "grid"

        self.__update_layout_button_icon()
        self.__search()

    def _get_layout(self):
        return user_settings.interface.launcher.layout

    def refresh_pinned_apps_list(self):
        self.__populate_pinned_apps_list()

    def __populate_pinned_apps_list(self):
        while self._pinned_apps_container.get_last_child():
            self._pinned_apps_container.remove(
                self._pinned_apps_container.get_last_child()
            )

        pinned_apps = applications.pinned

        if not pinned_apps:
            self._pinned_apps_container.set_halign("center")
            self._pinned_apps_container.attach(self._pin_icon, 0, 0, 1, 1)
            self._pinned_apps_container.attach(self._pin_hint_label, 0, 1, 1, 1)
            self._pinned_apps_container.visible = True
        else:
            self._pinned_apps_container.set_halign("start")
            self._pinned_apps_container.remove(self._pin_icon)
            self._pinned_apps_container.remove(self._pin_hint_label)
            self._pinned_apps_container.visible = True
            for i, app in enumerate(pinned_apps):
                item = PinnedAppItem(app, self)
                col = i % 8
                row = i // 8
                self._pinned_apps_container.attach(item, col, row, 1, 1)

    def __populate_apps(
        self, apps: list[Application], featured_app: Application | None = None
    ) -> None:
        while self._app_container.get_last_child():
            self._app_container.remove(self._app_container.get_last_child())

        if not apps and not featured_app:
            return

        layout = self._get_layout()

        if featured_app:
            self._app_container.append(
                AppItem(featured_app, self, is_featured=True, layout=layout)
            )

        if layout == "list":
            for app in apps:
                self._app_container.append(AppItem(app, self, layout="list"))
        else:  # grid layout
            app_grid = widgets.Grid(
                column_spacing=0,
                row_spacing=0,
                halign="fill",
                hexpand=True,
            )
            self._app_container.append(app_grid)

            for i, app in enumerate(apps):
                row = i // GRID_COLUMNS
                col = i % GRID_COLUMNS
                app_grid.attach(AppItem(app, self, layout="grid"), col, row, 1, 1)

    def __search(self, *args) -> None:
        query = self._entry.text

        # Update visibility of the clear button and layout button based on query
        self._clear_button.visible = bool(query)
        self._layout_button.visible = bool(query)

        if query:
            self._pinned_revealer.set_reveal_child(False)
            self._scroll_revealer.set_reveal_child(True)

            apps = applications.search(applications.apps, query)
            featured_app = apps[0] if apps else None
            remaining_apps = apps[1:] if apps else []
            self.__populate_apps(remaining_apps, featured_app)
        else:
            self._pinned_revealer.set_reveal_child(True)
            self._scroll_revealer.set_reveal_child(False)
            # Revert to the default state by populating the list with no apps
            self.__populate_apps([], None)

    def __clear_search(self, *args) -> None:
        self._entry.text = ""
        self._entry.grab_focus()
        self.__search()

    def __on_visibility_change(self, *args) -> None:
        if self.visible:
            self._entry.grab_focus()
            self._entry.set_position(-1)
        else:
            self._entry.text = ""
            self.__populate_pinned_apps_list()
            self.__search()

    def __on_accept(self, *args) -> None:
        first_child = self._app_container.get_first_child()
        if isinstance(first_child, AppItem):
            first_child.launch()
        elif isinstance(first_child, widgets.Grid):
            first_item_in_grid = first_child.get_child_at(0, 0)
            if isinstance(first_item_in_grid, AppItem):
                first_item_in_grid.launch()

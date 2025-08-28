# launcher.py
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from ignis.services.applications.application import Application
from ignis import widgets
from ignis.window_manager import WindowManager
from ignis.services.applications import ApplicationsService
applications = ApplicationsService.get_default()
window_manager = WindowManager.get_default()

GRID_COLUMNS = 3

class AppItem(widgets.Button):
    def __init__(self, application: Application) -> None:
        self._application = application
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
        self.set_size_request(150, 80)

    def launch(self) -> None:
        self._application.launch(terminal_format="kitty %command%")
        window_manager.close_window("Launcher")


class Launcher(widgets.Window):
    def __init__(self):
        self._app_grid_container = widgets.Box(
            vertical=True,
            spacing=5,
            css_classes=["inner-box"],
            halign="fill",
            hexpand=True,
        )
        self._first_row = None

        self._entry = widgets.Entry(
            placeholder_text="Search",
            css_classes=["launcher-search"],
            on_change=self.__search,
            on_accept=self.__on_accept
        )

        self._entry.text = ""
        self.__search()

        # Create the scroll container and set its overflow property
        scroll_container = widgets.Scroll(
            vexpand=True,
            css_classes=["outer-box"],
            child=self._app_grid_container
        )
        scroll_container.set_overflow(Gtk.Overflow.HIDDEN)

        super().__init__(
            css_classes=["launcher-window"],
            default_width=500,
            default_height=600,
            resizable=False,
            hide_on_close=True,
            visible=False,
            setup=lambda self: self.connect("notify::visible", self.__on_open),
            namespace="Launcher",
            kb_mode="exclusive",
            popup=True,
            child=widgets.Box(
                vertical=True,
                spacing=5,
                child=[
                    self._entry,
                    scroll_container
                ]
            )
        )
        
    def __populate_grid(self, apps: list[Application]) -> None:
        last_child = self._app_grid_container.get_last_child()
        while last_child:
            self._app_grid_container.remove(last_child)
            last_child = self._app_grid_container.get_last_child()
        
        self._first_row = None

        if not apps:
            return

        first_item = AppItem(apps[0])
        first_item.set_size_request(-1, 80)
        first_item.hexpand = True
        
        self._first_row = widgets.Box(spacing=5, css_classes=["app-row"], child=[first_item])
        self._first_row.add_css_class("featured-app-row")
        self._app_grid_container.append(self._first_row)
        
        remaining_apps = apps[1:]
        current_row = widgets.Box(spacing=5, css_classes=["app-row"])
        
        for i, app in enumerate(remaining_apps):
            if i % GRID_COLUMNS == 0 and i != 0:
                self._app_grid_container.append(current_row)
                current_row = widgets.Box(spacing=5, css_classes=["app-row"])
            
            current_row.append(AppItem(app))
            
        if current_row.child:
            self._app_grid_container.append(current_row)

    def __search(self, *args) -> None:
        query = self._entry.text

        if query == "":
            apps = applications.apps
        else:
            apps = applications.search(applications.apps, query)

        self.__populate_grid(apps)

    def __on_open(self, *args) -> None:
        if not self.visible:
            return

        self._entry.text = ""
        self._entry.grab_focus()
        self._entry.set_position(-1)

    def __on_accept(self, *args) -> None:
        if self._first_row and self._first_row.child:
            self._first_row.child[0].launch()
from ignis.services.applications.application import Application
from ignis import widgets
from ignis.window_manager import WindowManager
from ignis.services.applications import ApplicationsService
applications = ApplicationsService.get_default()
window_manager = WindowManager.get_default()

class AppItem(widgets.Button):
    def __init__(self, application: Application) -> None:
        self._application = application
        super().__init__(
            on_click=lambda x: self.launch(),
            css_classes=["app-item"],
            child=widgets.Box(
                spacing=5,
                child=[
                    widgets.Icon(image=application.icon, pixel_size=24),
                    widgets.Label(label=application.name, css_classes=["app-label"])
                ]
            )
        )

    def launch(self) -> None:
        self._application.launch(terminal_format="kitty %command%")
        window_manager.close_window("Launcher")


class Launcher(widgets.Window):
    def __init__(self):
        self._app_list = widgets.Box(
            vertical=True,
            spacing=2,
            css_classes=["inner-box"],
        )

        self._entry = widgets.Entry(
            placeholder_text="Search",
            css_classes=["launcher-search"],
            on_change=self.__search,
            on_accept=self.__on_accept
        )

        self._entry.text = ""
        self.__search()

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
                spacing=2,
                child=[
                    self._entry,
                    widgets.Scroll(
                        vexpand=True,
                        css_classes=["outer-box"],
                        child=self._app_list
                    )
                ]
            )
        )

    def __search(self, *args) -> None:
        query = self._entry.text

        if query == "":
            apps = applications.apps
        else:
            apps = applications.search(applications.apps, query)

        self._app_list.child = [AppItem(i) for i in apps]

    def __on_open(self, *args) -> None:
        if not self.visible:
            return

        self._entry.text = ""
        self._entry.grab_focus()

    def __on_accept(self, *args) -> None:
            if len(self._app_list.child) > 0:
                self._app_list.child[0].launch()

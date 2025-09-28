from ignis import widgets
from user_settings import user_settings
from ignis.services.applications import ApplicationsService
from ignis.window_manager import WindowManager
from modules.m3components import Button
from gi.repository import Gtk, GLib
from ignis.menu_model import IgnisMenuModel, IgnisMenuItem, IgnisMenuSeparator

window_manager = WindowManager.get_default()

try:
    from ignis.services.niri import NiriService
except ImportError:
    NiriService = None

try:
    from ignis.services.hyprland import HyprlandService
except ImportError:
    HyprlandService = None

SERVICE = None
if NiriService and NiriService.get_default().is_available:
    SERVICE = NiriService.get_default()
elif HyprlandService and HyprlandService.get_default().is_available:
    SERVICE = HyprlandService.get_default()


class Tasks(widgets.Box):
    def __init__(self, **kwargs):
        super().__init__(css_classes=["tasks"], **kwargs)
        self.applications_service = ApplicationsService.get_default()

        bar = (
            user_settings.interface.bar
            if user_settings.interface.modules.bar_id.tasks == 0
            else user_settings.interface.bar2
        )
        side = bar.side

        vertical = side in ("left", "right")
        self.set_vertical(vertical)

        if side == "left":
            self.set_halign("start")
            self.set_valign("fill")
        elif side == "right":
            self.set_halign("end")
            self.set_valign("fill")
        elif side == "top":
            self.set_halign("fill")
            self.set_valign("start")
        elif side == "bottom":
            self.set_halign("fill")
            self.set_valign("end")

        self.set_spacing(4)

        self.applications_service.connect(
            "notify::pinned", lambda *args: self._update_dock()
        )
        if SERVICE:
            SERVICE.connect("notify::windows", lambda *args: self._update_dock())
            SERVICE.connect("notify::active-window", lambda *args: self._update_dock())

        self._update_dock()

    def _is_same_app(self, id1: str, id2: str):
        if not id1 or not id2:
            return False
        id1_lower = id1.lower()
        id2_lower = id2.lower()
        return id1_lower in id2_lower or id2_lower in id1_lower

    def _get_app_from_window(self, window):
        app_id = None
        if isinstance(SERVICE, NiriService):
            app_id = window.app_id
        elif isinstance(SERVICE, HyprlandService):
            app_id = window.class_name

        if app_id:
            for app in self.applications_service.apps:
                if self._is_same_app(app.id, app_id):
                    return app
        return None

    def _handle_app_click(self, app, widget):
        if not SERVICE:
            app.launch()
            return

        app_windows = []
        for window in SERVICE.windows:
            window_id = None
            if isinstance(SERVICE, NiriService):
                window_id = window.app_id
            elif isinstance(SERVICE, HyprlandService):
                window_id = window.class_name

            if self._is_same_app(app.id, window_id):
                app_windows.append(window)

        if not app_windows:
            app.launch()
        elif len(app_windows) == 1:
            self._focus_window(app_windows[0])
        else:
            self._show_window_list_popover(app_windows, widget)

    def _focus_window(self, window):
        if isinstance(SERVICE, NiriService):
            GLib.idle_add(window.focus)
        elif isinstance(SERVICE, HyprlandService):
            SERVICE.send_command(f"dispatch focuswindow address:{window.address}")

    def _show_window_list_popover(self, windows, parent_widget):
        menu_items = []
        for window in windows:
            window_title = "Untitled Window"
            if hasattr(window, "title") and window.title:
                window_title = window.title

            menu_items.append(
                IgnisMenuItem(
                    label=window_title,
                    on_activate=lambda item, w=window: (
                        print(f"Focusing window: {w}"),
                        self._focus_window(w),
                    ),
                )
            )

        popover = widgets.PopoverMenu(model=IgnisMenuModel(*menu_items))
        container = parent_widget.get_child()
        if container and isinstance(container, Gtk.Overlay):
            container.add_overlay(popover)
            popover.popup()

    def _create_app_button(self, app, is_open: bool, is_active: bool = False):
        bar = (
            user_settings.interface.bar
            if user_settings.interface.modules.bar_id.tasks == 0
            else user_settings.interface.bar2
        )
        if bar.density in [0, 1]:
            icon_size = 20
        else:
            icon_size = 16

        icon = widgets.Icon(image=app.icon, pixel_size=icon_size)

        overlay = Gtk.Overlay()
        overlay.set_child(icon)

        if is_open:
            indicator = widgets.Box(css_classes=["app-indicator"])
            if not bar.vertical:
                indicator.set_halign("center")
            elif bar.side == "left":
                indicator.set_halign("start")
            elif bar.side == "right":
                indicator.set_halign("end")
            if bar.side in ["left", "right"]:
                indicator.set_valign("center")
            elif bar.side == "top":
                indicator.set_valign("start")
            elif bar.side == "bottom":
                indicator.set_valign("end")

            overlay.add_overlay(indicator)

        app_button = Button(
            child=overlay,
            on_click=lambda btn: self._handle_app_click(app, btn),
            css_classes=["app-button"],
        )

        if is_open:
            app_button.add_css_class("open-app")

        if is_active:
            app_button.add_css_class("active-app")

        menu_items = []

        menu_items.append(IgnisMenuItem(label=app.get_name(), enabled=False))
        menu_items.append(IgnisMenuSeparator())

        menu_items.append(
            IgnisMenuItem(
                label="Unpin from Dock" if app.is_pinned else "Pin to Dock",
                on_activate=lambda item, app=app: (
                    print(f"Pin/Unpin clicked for app: {app.get_name()}"),
                    app.unpin() if app.is_pinned else app.pin(),
                ),
            )
        )

        has_extra_actions = is_open or app.actions
        if has_extra_actions:
            menu_items.append(IgnisMenuSeparator())

        if is_open:
            menu_items.append(
                IgnisMenuItem(
                    label="New Window",
                    on_activate=lambda item, app=app: (
                        print(f"New Window clicked for app: {app.get_name()}"),
                        app.launch(),
                    ),
                )
            )

        if app.actions:
            for action in app.actions:
                menu_items.append(
                    IgnisMenuItem(
                        label=action.name,
                        on_activate=lambda item, act=action: (
                            print(
                                f"Action clicked: {action.name} for app: {app.get_name()}"
                            ),
                            act.launch(),
                        ),
                    )
                )

        def show_menu(widget):
            popover = widgets.PopoverMenu(model=IgnisMenuModel(*menu_items))
            container = widget.get_child()
            if container and isinstance(container, Gtk.Overlay):
                container.add_overlay(popover)
                popover.popup()

        app_button.on_right_click = show_menu
        return app_button

    def _update_dock(self, *args):
        bar = (
            user_settings.interface.bar
            if user_settings.interface.modules.bar_id.tasks == 0
            else user_settings.interface.bar2
        )
        self.set_vertical(bar.vertical)
        self.set_child([])
        active_app = None
        if SERVICE and hasattr(SERVICE, "active_window"):
            active_window = SERVICE.active_window
            if active_window:
                active_app = self._get_app_from_window(active_window)

        pinned_apps = self.applications_service.pinned

        open_unpinned_apps = []
        open_app_ids = set()
        if SERVICE:
            for window in SERVICE.windows:
                app = self._get_app_from_window(window)
                if app:
                    open_app_ids.add(app.id)

        pinned_app_ids = {app.id for app in pinned_apps}

        for app in pinned_apps:
            is_open = app.id in open_app_ids
            is_active = app and active_app and app.id == active_app.id
            self.append(self._create_app_button(app, is_open, is_active))

        if SERVICE:
            for window in SERVICE.windows:
                app = self._get_app_from_window(window)
                if app and app.id not in pinned_app_ids:
                    if app not in open_unpinned_apps:
                        open_unpinned_apps.append(app)

        if open_unpinned_apps:
            orientation = True if bar.vertical else False
            separator = widgets.Separator(vertical=orientation)

            self.append(separator)

        for app in open_unpinned_apps:
            is_active = app and active_app and app.id == active_app.id
            self.append(self._create_app_button(app, True, is_active))

    def widget(self):
        return self

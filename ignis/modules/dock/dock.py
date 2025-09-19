import os
from ignis import widgets, utils

from user_settings import user_settings
from ignis.services.applications import ApplicationsService
from ignis.window_manager import WindowManager
from modules.m3components import Button
from modules import Corners
from gi.repository import Gtk, Gdk, GLib

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

from scripts.set_dock_styles import DockStyles

class Dock:
    def __init__(self, monitor: int = 0):
        self.monitor = monitor
        self.applications_service = ApplicationsService.get_default()
        self.dock_box = widgets.Box(css_classes=["dock-apps"])
        self.__win = None
        self.icon_size = user_settings.interface.dock.size

    def build(self):
        side = user_settings.interface.dock.side
        vertical = user_settings.interface.dock.vertical
        size = user_settings.interface.dock.size
        enabled = user_settings.interface.dock.enabled

        self.dock_box.set_vertical(vertical)
        self.dock_box.set_spacing(4)

        height = size + 10

        if vertical:
            size_request = {"width_request": height}
        else:
            size_request = {"height_request": height}

        anchors = [side] if user_settings.interface.dock.centered else (["top", "bottom", side] if vertical else ["left", "right", side])

        self.__win = widgets.Window(
            namespace="Dock",
            monitor=self.monitor,
            anchor=anchors,
            css_classes=["dock"],
            visible=enabled,
            **size_request,
            child=widgets.CenterBox(
                vertical=vertical,
                css_classes=["dock-container"],
                center_widget=self.dock_box
            )
        )

        if enabled:
            self.__win.set_exclusivity("exclusive")

        DockStyles.setSide(user_settings.interface.dock.side)
        DockStyles.setFloating(user_settings.interface.dock.floating)

        self.applications_service.connect("notify::pinned", lambda *args: self._update_dock())
        if SERVICE:
            SERVICE.connect("notify::windows", lambda *args: self._update_dock())
            SERVICE.connect("notify::active-window", lambda *args: self._update_dock())

        return self.__win

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
        popover = Gtk.Popover.new()
        popover.set_parent(parent_widget)

        menu_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        popover.set_child(menu_box)

        for window in windows:
            window_title = "Untitled Window"
            if hasattr(window, 'title') and window.title:
                window_title = window.title

            button = widgets.Button(label=window_title, css_classes=["menu-button"])
            button.connect("clicked", lambda _, w=window, p=popover: self._focus_and_close_popover(w, p))
            menu_box.append(button)

        popover.popup()

    def _focus_and_close_popover(self, window, popover):
        self._focus_window(window)
        popover.popdown()

    def _create_app_button(self, app, is_open: bool, is_active: bool = False):
        icon = widgets.Icon(image=app.icon, pixel_size=self.icon_size)

        overlay = Gtk.Overlay()
        overlay.set_child(icon)

        if is_open:
            indicator = widgets.Box(css_classes=["app-indicator"])
            side = user_settings.interface.dock.side
            vertical = user_settings.interface.dock.vertical

            if vertical:
                indicator.set_valign("center")
                if side == "left":
                    indicator.set_halign("start")
                else:
                    indicator.set_halign("end")
            else:  # horizontal
                indicator.set_halign("center")
                if side == "top":
                    indicator.set_valign("start")
                else:
                    indicator.set_valign("end")

            overlay.add_overlay(indicator)

        app_button = Button(
            child=overlay,
            on_click=lambda btn: self._handle_app_click(app, btn),
            css_classes=["app-button"]
        )

        if is_open:
            app_button.add_css_class("open-app")

        if is_active:
            app_button.add_css_class("active-app")

        popover = Gtk.Popover.new()
        menu_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        popover.set_child(menu_box)

        app_name_label = Gtk.Label(label=app.get_name())
        app_name_label.add_css_class("menu-label")
        menu_box.append(app_name_label)

        separator = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        menu_box.append(separator)

        is_pinned = app.is_pinned
        label = "Unpin from Dock" if is_pinned else "Pin to Dock"
        pin_button = widgets.Button(label=label, css_classes=["menu-button"])

        def on_pin_clicked(btn):
            if app.is_pinned:
                app.unpin()
            else:
                app.pin()
            popover.popdown()

        pin_button.connect("clicked", on_pin_clicked)
        menu_box.append(pin_button)

        has_extra_actions = is_open or app.actions
        if has_extra_actions:
            separator = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
            menu_box.append(separator)

        if is_open:
            new_window_button = widgets.Button(label="New Window", css_classes=["menu-button"])
            def on_new_window_clicked(btn):
                app.launch()
                popover.popdown()
            new_window_button.connect("clicked", on_new_window_clicked)
            menu_box.append(new_window_button)

        if app.actions:
            for action in app.actions:
                action_button = widgets.Button(label=action.name, css_classes=["menu-button"])
                def on_action_clicked(btn, act=action):
                    act.launch()
                    popover.popdown()
                action_button.connect("clicked", on_action_clicked)
                menu_box.append(action_button)

        app_button.on_right_click = lambda w: self._show_popover(w, popover)

        return app_button

    def _show_popover(self, widget, popover):
        popover.set_parent(widget)
        popover.popup()

    def _update_dock(self, *args):
        active_app = None
        if SERVICE and hasattr(SERVICE, "active_window"):
            active_window = SERVICE.active_window
            if active_window:
                active_app = self._get_app_from_window(active_window)

        for child in list(self.dock_box):
            child.unparent()

        launcher_button = Button(
            child=widgets.Icon(image="view-app-grid-symbolic", pixel_size=self.icon_size),
            on_click=lambda _: window_manager.toggle_window("Launcher"),
            css_classes=["app-button", "launcher-button"],
        )
        self.dock_box.append(launcher_button)

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
            self.dock_box.append(self._create_app_button(app, is_open, is_active))

        if SERVICE:
            for window in SERVICE.windows:
                app = self._get_app_from_window(window)
                if app and app.id not in pinned_app_ids:
                    if app not in open_unpinned_apps:
                        open_unpinned_apps.append(app)

        if open_unpinned_apps:
            orientation = Gtk.Orientation.VERTICAL if user_settings.interface.dock.vertical else Gtk.Orientation.HORIZONTAL
            separator = Gtk.Separator.new(orientation)
            separator.add_css_class("dock-separator")
            self.dock_box.append(separator)

            for app in open_unpinned_apps:
                is_active = app and active_app and app.id == active_app.id
                self.dock_box.append(self._create_app_button(app, True, is_active))

    def get_window(self):
        return self.__win

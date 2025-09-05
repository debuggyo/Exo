import os
from ignis import widgets, utils
from user_settings import user_settings
from ignis.services.applications import ApplicationsService
from modules.m3components import Button
from gi.repository import Gtk, Gdk

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

    def _handle_app_click(self, app):
        if not SERVICE:
            app.launch()
            return
        
        found_window = None
        for window in SERVICE.windows:
            window_id = None
            if isinstance(SERVICE, NiriService):
                window_id = window.app_id
            elif isinstance(SERVICE, HyprlandService):
                window_id = window.class_name
            
            if self._is_same_app(app.id, window_id):
                found_window = window
                break
        
        if found_window:
            found_window.focus()
        else:
            app.launch()

    def _create_app_button(self, app, is_open: bool):
        icon = widgets.Icon(image=app.icon, pixel_size=self.icon_size)
        
        app_button = Button(
            child=icon,
            on_click=lambda _: self._handle_app_click(app),
            css_classes=["app-button"]
        )

        if is_open:
            app_button.add_css_class("open-app")

        popover = Gtk.Popover.new()
        menu_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        popover.set_child(menu_box)

        is_pinned = app in self.applications_service.pinned
        label = "Unpin from Dock" if is_pinned else "Pin to Dock"
        pin_button = widgets.Button(label=label, css_classes=["menu-button"])
        pin_button.connect("clicked", lambda b: self.applications_service.toggle_pinned(app))
        menu_box.append(pin_button)

        app_button.on_right_click = lambda w: self._show_popover(w, popover)
        
        return app_button

    def _show_popover(self, widget, popover):
        popover.set_parent(widget)
        popover.popup()

    def _update_dock(self, *args):
        for child in list(self.dock_box):
            child.unparent()

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
            self.dock_box.append(self._create_app_button(app, is_open))

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
                self.dock_box.append(self._create_app_button(app, True))

    def get_window(self):
        return self.__win
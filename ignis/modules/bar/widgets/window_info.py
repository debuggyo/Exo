from ignis import widgets, utils
from ignis.services.niri import NiriService
from ignis.services.hyprland import HyprlandService
from ignis.services.applications import ApplicationsService
from user_settings import user_settings
from modules.shared_modules import AppIcon

class WindowInfo:
    def __init__(self):
        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()
        self.applications = ApplicationsService.get_default()

        self.icon = AppIcon(pixel_size=16)
        self.title_label = widgets.Label(
            css_classes=["title"],
            halign="start",
            ellipsize="end",
            max_width_chars=52,
            hexpand=True,
        )
        self.appid_label = widgets.Label(
            css_classes=["app_id"], halign="start", ellipsize="end", hexpand=True
        )
        self.title = None
        self.app_id = None

        self.label_box = widgets.Box(
            vertical=True,
            valign="center",
            hexpand=True,
            child=[self.title_label, self.appid_label],
        )

        self.main_box = widgets.Box(
            vertical=False,
            spacing=8,
            vexpand=True,
            css_classes=["winfo"],
            child=[self.icon, self.label_box],
        )

        self.update_layout()
        if self.niri.is_available:
            self.niri.active_window.connect("notify::title", self.update)
        elif self.hyprland.is_available:
            self.hyprland.active_window.connect("notify::title", self.update)

    def _is_same_app(self, id1: str, id2: str):
        if not id1 or not id2:
            return False
        id1_lower = id1.lower()
        id2_lower = id2.lower()
        return id1_lower in id2_lower or id2_lower in id1_lower

    def update(self, *args):
        FALLBACK_ICON = "application-x-executable-symbolic"

        if self.niri.is_available:
            self.title = self.niri.active_window.title or "Empty Workspace"
            self.app_id = self.niri.active_window.app_id or "Desktop"
        elif self.hyprland.is_available:
            self.title = self.hyprland.active_window.title or "Empty Workspace"
            self.app_id = self.hyprland.active_window.class_name or "Desktop"

        self.title_label.set_label(self.title)
        self.appid_label.set_label(self.app_id)

        self.icon.set_app_id(self.app_id)
        self.icon.set_name(self.title)
        self.icon.set_visible(True)

    def update_layout(self):
        bar = (
            user_settings.interface.bar
            if user_settings.interface.modules.bar_id.window_info == 0
            else user_settings.interface.bar2
        )
        is_vertical = bar.vertical
        is_centered = bar.centered

        if is_vertical:
            self.main_box.set_halign("fill")
            self.main_box.set_valign("fill")
            self.main_box.set_hexpand(True)
            self.main_box.set_width_request(-1)
            self.label_box.set_visible(False)
            self.icon.set_halign("center")
            self.icon.set_hexpand(True)
            self.main_box.set_tooltip_text(f"{self.title}\n{self.app_id}")
        else:
            self.main_box.set_valign("fill")
            self.label_box.set_visible(True)
            self.icon.set_halign("start")
            self.icon.set_hexpand(False)

            if is_centered:
                self.main_box.set_halign("center")
                self.main_box.set_width_request(150)
                self.main_box.set_hexpand(False)
            else:
                self.main_box.set_halign("start")
                self.main_box.set_width_request(-1)
                self.main_box.set_hexpand(True)

            if bar.density == 0:
                self.title_label.set_visible(True)
                self.appid_label.set_visible(True)
                self.main_box.set_tooltip_text(None)
            elif bar.density >= 1:
                self.title_label.set_visible(True)
                self.appid_label.set_visible(False)
                self.main_box.set_tooltip_text(self.app_id)

    def widget(self):
        return self.main_box

from ignis import widgets, utils
from ignis.services.niri import NiriService
from ignis.services.hyprland import HyprlandService
from user_settings import user_settings

class WindowInfo:
    def __init__(self):
        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()
        
        self.full_title_label = widgets.Label(css_classes=["title"], halign="start", ellipsize="end", max_width_chars=52)
        self.full_appid_label = widgets.Label(css_classes=["app_id"], halign="start", ellipsize="end")
        self.full_icon = widgets.Icon(pixel_size=16)

        self.compact_title_label = widgets.Label(css_classes=["title"], halign="start", ellipsize="end", max_width_chars=52)
        self.compact_icon = widgets.Icon(pixel_size=16)

        self.stack = widgets.Stack()
        
        full_layout = widgets.Box(
            vertical=False,
            spacing=8,
            halign="start",
            valign="fill",
            vexpand=True,
            child=[
                self.full_icon,
                widgets.Box(vertical=True, valign="center", child=[self.full_title_label, self.full_appid_label])
            ]
        )
        self.stack.add_titled(full_layout, "full", "Full Layout")
        
        compact_layout = widgets.Box(
            vertical=False,
            spacing=8,
            halign="start",
            valign="fill",
            vexpand=True,
            child=[
                self.compact_icon,
                self.compact_title_label
            ]
        )
        self.stack.add_titled(compact_layout, "compact", "Compact Layout")
        
        self.main_box = widgets.Box(
            vertical=False,
            spacing=0,
            halign="start",
            valign="fill",
            vexpand=True,
            css_classes=["winfo"],
            width_request=200,
            child=[self.stack]
        )
        
        self.update_layout()
        utils.Poll(100, lambda _: self.update())

    def update(self):
        if self.niri.is_available:
            title = self.niri.active_window.title or "Empty Workspace"
            app_id = self.niri.active_window.app_id or "Desktop"
            icon_name = utils.get_app_icon_name(app_id)
            icon_path = icon_name if icon_name else None
        elif self.hyprland.is_available:
            title = self.hyprland.active_window.title or "Empty Workspace"
            app_id = self.hyprland.active_window.class_name or "Desktop"
            icon_name = utils.get_app_icon_name(app_id)
            icon_path = icon_name if icon_name else None
        
        self.full_title_label.set_label(title)
        self.full_appid_label.set_label(app_id)
        self.compact_title_label.set_label(title)

        if icon_path:
            self.full_icon.set_image(icon_path)
            self.full_icon.set_visible(True)
            self.compact_icon.set_image(icon_path)
            self.compact_icon.set_visible(True)
        else:
            self.full_icon.set_visible(False)
            self.compact_icon.set_visible(False)

    def update_layout(self):
        if user_settings.appearance.compact == 0:
            self.stack.set_visible_child_name("full")
        elif user_settings.appearance.compact >= 1:
            self.stack.set_visible_child_name("compact")

    def widget(self):
        return self.main_box
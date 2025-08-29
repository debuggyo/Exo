from ignis import widgets, utils
from ignis.services.niri import NiriService
from ignis.services.hyprland import HyprlandService
from user_settings import user_settings

class WindowInfo:
    def __init__(self):
        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()
        
        self.icon = widgets.Icon(pixel_size=16)
        self.title_label = widgets.Label(css_classes=["title"], halign="start", ellipsize="end", max_width_chars=52, hexpand=True)
        self.appid_label = widgets.Label(css_classes=["app_id"], halign="start", ellipsize="end", hexpand=True)
        
        self.label_box = widgets.Box(vertical=True, valign="center", hexpand=True, child=[self.title_label, self.appid_label])

        self.main_box = widgets.Box(
            vertical=False,
            spacing=8,
            vexpand=True,
            css_classes=["winfo"],
            child=[
                self.icon,
                self.label_box
            ]
        )
        
        self.update_layout()
        utils.Poll(100, lambda _: self.update())

    def update(self):
        FALLBACK_ICON = "application-x-executable-symbolic"
        
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
        
        self.title_label.set_label(title)
        self.appid_label.set_label(app_id)
        
        if icon_path:
            self.icon.set_image(icon_path)
        else:
            self.icon.set_image(FALLBACK_ICON)
        self.icon.set_visible(True)

    def update_layout(self):
        is_vertical = user_settings.interface.bar.vertical
        is_centered = user_settings.interface.bar.centered
        
        if is_vertical:
            self.main_box.set_halign("fill")
            self.main_box.set_valign("fill")
            self.main_box.set_hexpand(True)
            self.main_box.set_width_request(-1)
            self.label_box.set_visible(False)
            self.icon.set_halign("center")
            self.icon.set_hexpand(True)
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
            
            if user_settings.interface.bar.density == 0:
                self.title_label.set_visible(True)
                self.appid_label.set_visible(True)
            elif user_settings.interface.bar.density >= 1:
                self.title_label.set_visible(True)
                self.appid_label.set_visible(False)

    def widget(self):
        return self.main_box
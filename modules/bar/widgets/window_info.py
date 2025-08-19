from ignis import widgets, utils
from ignis.services.niri import NiriService
from ignis.services.hyprland import HyprlandService
from user_settings import user_settings

class WindowInfo:
    def __init__(self):
        self.niri = NiriService.get_default()
        self.hyprland = HyprlandService.get_default()
        self.title_label = widgets.Label(css_classes=["title"], halign="start", ellipsize="end", max_width_chars=52)
        self.appid_label = widgets.Label(css_classes=["app_id"], halign="start", ellipsize="end")
        self.icon = widgets.Icon(pixel_size=16)
        utils.Poll(100, lambda _: self.update())

    def update(self):
        if self.niri.is_available:
            self.title_label.set_label(self.niri.active_window.title or "Empty Workspace")
            self.appid_label.set_label(self.niri.active_window.app_id or "Desktop")
            icon_name = utils.get_app_icon_name(self.niri.active_window.app_id)
            icon_path = icon_name if icon_name else None
        elif self.hyprland.is_available:
            self.title_label.set_label(self.hyprland.active_window.title or "Empty Workspace")
            self.appid_label.set_label(self.hyprland.active_window.class_name or "Desktop")
            icon_name = utils.get_app_icon_name(self.hyprland.active_window.class_name)
            icon_path = icon_name if icon_name else None
        if icon_path:
            self.icon.set_image(icon_path)
            self.icon.set_visible(True)
        else:
            self.icon.set_visible(False)

    def widget(self):
        child = [self.icon]
        if user_settings.appearance.compact == 0:
            child.append(widgets.Box(vertical=True, valign="center", child=[self.title_label, self.appid_label],))
        elif user_settings.appearance.compact >= 1:
            child.append(self.title_label)
        if user_settings.appearance.style == "island":
            width = 200
        else:
            width = 0

        return widgets.Box(
            vertical=False,
            spacing=5,
            halign="start",
            valign="fill",
            vexpand=True,
            css_classes=["winfo"],
            width_request=width,
            child=child
        )

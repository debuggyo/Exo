import asyncio
from ignis import widgets
from ignis.services.system_tray import SystemTrayService, SystemTrayItem

system_tray = SystemTrayService.get_default()


class TrayItem(widgets.Button):
    __gtype_name__ = "TrayItem"

    def __init__(self, item: SystemTrayItem, on_removed_callback=None):
        menu = None
        if item.menu:
            menu = item.menu.copy()
            menu.add_css_class("tray-menu")
        
        icon_box_children = [
            widgets.Icon(image=item.bind("icon"), pixel_size=16, css_classes=["tray-icon"])
        ]
        
        def on_item_removed(x):
            if on_removed_callback:
                on_removed_callback()
            self.unparent()

        super().__init__(
            child=widgets.Box(child=icon_box_children),
            tooltip_text=item.bind("tooltip"),
            on_click=lambda _: asyncio.create_task(item.activate_async()),
            setup=lambda self: item.connect("removed", on_item_removed),
            on_right_click=menu.popup if menu else None,
            css_classes=["tray-item", "unset"],
        )


class Tray(widgets.Box):
    __gtype_name__ = "Tray"

    def __init__(self):
        super().__init__(
            css_classes=["tray"],
            spacing=10,
        )
        self.__setup()

    def __setup(self):
        self.update_visibility()

        system_tray.connect("added", self.handle_added)

        for item in system_tray.items:
            self.append(TrayItem(item, on_removed_callback=self.handle_item_removed))

    def update_visibility(self):
        self.set_visible(len(system_tray.items) > 0)
        
    def handle_added(self, _, item):
        self.append(TrayItem(item, on_removed_callback=self.handle_item_removed))

    def handle_item_removed(self):
        self.update_visibility()
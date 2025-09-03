import os
from ignis import widgets, utils
from user_settings import user_settings

class DockStyles:
    dock_instance = None

    @classmethod
    def set_dock_instance(cls, dock):
        cls.dock_instance = dock

    @staticmethod
    def _apply_dock_css(window):
        if not window:
            return

        side = user_settings.interface.dock.side
        floating = user_settings.interface.dock.floating
        centered = user_settings.interface.dock.centered
        vertical = user_settings.interface.dock.vertical

        all_possible_classes = {"floating", "hug", "centered", "not-centered", "vertical", "horizontal", "top", "bottom", "left", "right"}
        for css_class in all_possible_classes:
            window.remove_css_class(css_class)
        
        if floating:
            window.add_css_class("floating")
        else:
            window.add_css_class("hug")
            
        if centered:
            window.add_css_class("centered")
        else:
            window.add_css_class("not-centered")
        
        if vertical:
            window.add_css_class("vertical")
        else:
            window.add_css_class("horizontal")

        window.add_css_class(side)

    @staticmethod
    def _compute_margins(side: str, floating: bool):
        if not floating:
            return 0, 0, 0, 0

        top, left, right, bottom = 5, 5, 5, 5
        if side == "top":
            bottom = 0
        elif side == "bottom":
            top = 0
        elif side == "left":
            right = 0
        elif side == "right":
            left = 0
        return top, left, right, bottom

    @staticmethod
    def setEnabled(enabled: bool):
        user_settings.interface.dock.set_enabled(enabled)
        if DockStyles.dock_instance:
            win = DockStyles.dock_instance.get_window()
            if enabled:
                win.exclusivity = "exclusive"
                win.visible = True
            else:
                win.exclusivity = "normal"
                win.visible = False

    @staticmethod
    def setSide(side: str):
        user_settings.interface.dock.set_side(side)
        vertical = side in ("left", "right")
        user_settings.interface.dock.set_vertical(vertical)

        if not DockStyles.dock_instance:
            return

        dock = DockStyles.dock_instance
        win = dock.get_window()

        floating = user_settings.interface.dock.floating
        win.margin_top, win.margin_left, win.margin_right, win.margin_bottom = DockStyles._compute_margins(side, floating)

        size = user_settings.interface.dock.size
        height = size + 10
        win.set_width_request(height if vertical else -1)
        win.set_height_request(height if not vertical else -1)

        centered = user_settings.interface.dock.centered
        anchors = [side] if centered else (["top", "bottom", side] if vertical else ["left", "right", side])
        win.anchor = None
        win.anchor = anchors

        win.child.vertical = vertical
        win.child.get_center_widget().vertical = vertical
        
        dock.dock_box.set_vertical(vertical)

        DockStyles._apply_dock_css(win)
        dock._update_dock()

        win.queue_resize()
        win.child.queue_resize()


    @staticmethod
    def setFloating(enabled: bool):
        user_settings.interface.dock.set_floating(enabled)
        if DockStyles.dock_instance:
            win = DockStyles.dock_instance.get_window()
            DockStyles._apply_dock_css(win)
            side = user_settings.interface.dock.side
            win.margin_top, win.margin_left, win.margin_right, win.margin_bottom = DockStyles._compute_margins(side, enabled)
            DockStyles.dock_instance._update_dock()
            
            win.queue_resize()
            win.child.queue_resize()


    @staticmethod
    def setCentered(enabled: bool):
        user_settings.interface.dock.set_centered(enabled)
        if DockStyles.dock_instance:
            win = DockStyles.dock_instance.get_window()
            DockStyles._apply_dock_css(win)
            side = user_settings.interface.dock.side
            vertical = user_settings.interface.dock.vertical
            anchors = [side] if enabled else (["top", "bottom", side] if vertical else ["left", "right", side])
            win.anchor = None
            win.anchor = anchors
            DockStyles.dock_instance._update_dock()

            win.queue_resize()
            win.child.queue_resize()

    @staticmethod
    def setSize(size: int):
        user_settings.interface.dock.set_size(size)
        if DockStyles.dock_instance:
            dock = DockStyles.dock_instance
            dock.icon_size = size
            win = dock.get_window()
            vertical = user_settings.interface.dock.vertical
            height = size + 10
            win.set_width_request(height if vertical else -1)
            win.set_height_request(height if not vertical else -1)
            dock._update_dock()
            
            win.queue_resize()
            win.child.queue_resize()
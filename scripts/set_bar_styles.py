# set_bar_styles.py

from ignis import widgets, utils
from user_settings import user_settings
from .send_notification import send_notification
from modules.corners import Corners
from .wallpaper import Wallpaper
from .apply_bar_css import apply_bar_css

def rebuild_corners():
    Corners.destroy_all()
    if user_settings.interface.misc.screen_corners or user_settings.interface.bar.corners:
        Corners.build()

class BarStyles:
    bar_instance = None

    @classmethod
    def set_bar_instance(cls, bar):
        cls.bar_instance = bar

    @staticmethod
    def _update_all_layouts():
        if BarStyles.bar_instance:
            BarStyles.bar_instance.window_info.update_layout()
            BarStyles.bar_instance.time_date.update_layout()
            BarStyles.bar_instance.media.update_layout()
            BarStyles.bar_instance.workspaces.update_layout()
            BarStyles.bar_instance.media.update_visibility()

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
    def setSide(side: str):
        user_settings.interface.bar.set_side(side)
        vertical = side in ("left", "right")
        user_settings.interface.bar.set_vertical(vertical)
        
        bar = BarStyles.bar_instance
        if not bar or not bar.get_window():
            return
            
        win = bar.get_window()

        # Update orientation classes
        win.remove_css_class("horizontal")
        win.remove_css_class("vertical")
        if vertical:
            win.add_css_class("vertical")
        else:
            win.add_css_class("horizontal")

        # Update side classes
        win.remove_css_class("top")
        win.remove_css_class("bottom")
        win.remove_css_class("left")
        win.remove_css_class("right")
        win.add_css_class(side)
        
        # Compute margins
        floating = user_settings.interface.bar.floating
        win.margin_top, win.margin_left, win.margin_right, win.margin_bottom = BarStyles._compute_margins(side, floating)
        
        # Get dynamic size based on density
        width = 40; height = 40
        compact_mode = user_settings.interface.bar.density
        if compact_mode == 1:
            width = 35; height = 35
        elif compact_mode == 2:
            width = 30; height = 30
        elif compact_mode == 3:
            width = 25; height = 25
        
        # Set window size and anchors
        win.set_width_request(width if vertical else -1)
        win.set_height_request(height if not vertical else -1)
        
        centered = user_settings.interface.bar.centered
        anchors = [side] if centered else (["top", "bottom", side] if vertical else ["left", "right", side])
        win.anchor = None
        win.anchor = anchors
        
        # Update CenterBox and its children
        center_box = win.child
        start_box = center_box.get_start_widget()
        center_box_inner = center_box.get_center_widget()
        end_box = center_box.get_end_widget()

        center_box.vertical = vertical
        
        # CenterBox should always fill its parent container
        center_box.halign = "fill"
        center_box.valign = "fill"
        
        if start_box: start_box.vertical = vertical
        if center_box_inner: center_box_inner.vertical = vertical
        if end_box: end_box.vertical = vertical
        
        # Change alignment based on orientation
        if vertical:
            if start_box:
                start_box.halign = "fill"
                start_box.valign = "start"
                start_box.hexpand = True
                start_box.vexpand = False
            if center_box_inner:
                center_box_inner.halign = "fill"
                center_box_inner.valign = "center"
                center_box_inner.hexpand = True
                center_box_inner.vexpand = True
            if end_box:
                end_box.halign = "fill"
                end_box.valign = "end"
                end_box.hexpand = True
                end_box.vexpand = False
        else: # horizontal
            if start_box:
                start_box.halign = "start"
                start_box.valign = "fill"
                start_box.hexpand = False
                start_box.vexpand = True
            if center_box_inner:
                center_box_inner.halign = "center"
                center_box_inner.valign = "fill"
                center_box_inner.hexpand = True
                center_box_inner.vexpand = False
            if end_box:
                end_box.halign = "end"
                end_box.valign = "fill"
                end_box.hexpand = False
                end_box.vexpand = True
        
        BarStyles._update_all_layouts()
        rebuild_corners()

        # Force CSS update after all properties have been changed
        apply_bar_css(win)

    @staticmethod
    def setCompact(mode: int):
        user_settings.interface.bar.set_density(mode)
        if BarStyles.bar_instance:
            apply_bar_css(BarStyles.bar_instance.get_window())
            
            height = 40
            width = 40
            if mode == 1:
                height = 35
                width = 35
            elif mode == 2:
                height = 30
                width = 30
            elif mode == 3:
                height = 25
                width = 25
            
            win = BarStyles.bar_instance.get_window()
            if win:
                if user_settings.interface.bar.vertical:
                    win.set_width_request(width)
                else:
                    win.set_height_request(height)

        BarStyles._update_all_layouts()

    @staticmethod
    def setMediaWidget(enabled: bool):
        user_settings.interface.bar.modules.set_media_widget(enabled)
        if BarStyles.bar_instance:
            BarStyles.bar_instance.media.update_visibility()

    @staticmethod
    def setSeparation(enabled: bool):
        user_settings.interface.bar.set_separation(enabled)
        if BarStyles.bar_instance:
            apply_bar_css(BarStyles.bar_instance.get_window())

    @staticmethod
    def setFloating(enabled: bool):
        user_settings.interface.bar.set_floating(enabled)
        if BarStyles.bar_instance:
            apply_bar_css(BarStyles.bar_instance.get_window())
        BarStyles.setSide(user_settings.interface.bar.side)
        rebuild_corners()
        BarStyles._update_all_layouts()

    @staticmethod
    def setBarCorners(enabled: bool):
        user_settings.interface.bar.set_corners(enabled)
        rebuild_corners()

    @staticmethod
    def setScreenCorners(enabled: bool):
        user_settings.interface.misc.set_screen_corners(enabled)
        rebuild_corners()
    
    @staticmethod
    def setBarCenter(enabled: bool):
        user_settings.interface.bar.set_centered(enabled)
        BarStyles.setSide(user_settings.interface.bar.side)
        rebuild_corners()
        if BarStyles.bar_instance:
            apply_bar_css(BarStyles.bar_instance.get_window())

    @staticmethod
    def setMilitaryTime(enabled: bool):
        user_settings.interface.bar.modules.set_military_time(enabled)
        BarStyles._update_all_layouts()
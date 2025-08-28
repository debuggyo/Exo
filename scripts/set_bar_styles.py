# set_bar_styles.py

from ignis import utils
from user_settings import user_settings
from .send_notification import send_notification
from modules.corners import Corners
from .wallpaper import Wallpaper
from .apply_bar_css import apply_bar_css

def rebuild_corners():
    Corners.destroy_all()
    if user_settings.appearance.screen_corners or user_settings.appearance.bar_corners:
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
    def _compute_margins(side: str):
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
        user_settings.appearance.set_bar_side(side)
        user_settings.appearance.set_vertical(side in ("left", "right"))
        bar = BarStyles.bar_instance
        if bar and bar.get_window():
            win = bar.get_window()
            vertical = user_settings.appearance.vertical
            floating = user_settings.appearance.bar_floating
            centered = user_settings.appearance.bar_centered
            anchors = [side] if centered else (["top", "bottom", side] if vertical else ["left", "right", side])
            win.anchor = None
            win.anchor = anchors
            win.margin_top, win.margin_left, win.margin_right, win.margin_bottom = BarStyles._compute_margins(side) if floating else (0, 0, 0, 0)
        rebuild_corners()
        BarStyles._update_all_layouts()

    @staticmethod
    def setCompact(mode: int):
        user_settings.appearance.set_compact(mode)
        if BarStyles.bar_instance:
            apply_bar_css(BarStyles.bar_instance.get_window())
            
            height = 40
            if mode == 1:
                height = 35
            elif mode == 2:
                height = 30
            elif mode == 3:
                height = 25
            
            win = BarStyles.bar_instance.get_window()
            if win:
                win.set_height_request(height)

        BarStyles._update_all_layouts()

    @staticmethod
    def setMediaWidget(enabled: bool):
        user_settings.appearance.set_media_widget(enabled)
        if BarStyles.bar_instance:
            BarStyles.bar_instance.media.update_visibility()

    @staticmethod
    def setSeparation(enabled: bool):
        user_settings.appearance.set_bar_separation(enabled)
        if BarStyles.bar_instance:
            apply_bar_css(BarStyles.bar_instance.get_window())

    @staticmethod
    def setFloating(enabled: bool):
        user_settings.appearance.set_bar_floating(enabled)
        if BarStyles.bar_instance:
            apply_bar_css(BarStyles.bar_instance.get_window())
        BarStyles.setSide(user_settings.appearance.bar_side)
        rebuild_corners()
        BarStyles._update_all_layouts()

    @staticmethod
    def setBarCorners(enabled: bool):
        user_settings.appearance.set_bar_corners(enabled)
        rebuild_corners()

    @staticmethod
    def setScreenCorners(enabled: bool):
        user_settings.appearance.set_screen_corners(enabled)
        rebuild_corners()
    
    @staticmethod
    def setBarCenter(enabled: bool):
        user_settings.appearance.set_bar_centered(enabled)
        BarStyles.setSide(user_settings.appearance.bar_side)
        rebuild_corners()
        if BarStyles.bar_instance:
            apply_bar_css(BarStyles.bar_instance.get_window())
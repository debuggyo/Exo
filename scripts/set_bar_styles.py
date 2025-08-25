from ignis import utils
from user_settings import user_settings
from .send_notification import send_notification
from .apply_bar_css import apply_bar_css
from modules.corners import Corners
from .wallpaper import Wallpaper

def rebuild_corners():
    Corners.destroy_all()
    if user_settings.appearance.screen_corners or user_settings.appearance.bar_corners:
        Corners.build()

class BarStyles:
    bar_instance = None  # class-level reference to Bar

    @classmethod
    def set_bar_instance(cls, bar):
        cls.bar_instance = bar  # store Bar instance

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
        if bar:
            win = bar.get_window()
            if win:
                vertical = user_settings.appearance.vertical
                floating = user_settings.appearance.bar_floating
                centered = user_settings.appearance.bar_centered
                anchors = [side] if centered else (["top", "bottom", side] if vertical else ["left", "right", side])

                win.anchor = None  # reset all previous anchors
                win.anchor = anchors  # apply new anchors
                win.margin_top, win.margin_left, win.margin_right, win.margin_bottom = BarStyles._compute_margins(side) if floating else (0, 0, 0, 0)
        rebuild_corners()

    @staticmethod
    def setCompact(mode: int):
        user_settings.appearance.set_compact(mode)

    @staticmethod
    def setSeparation(enabled: bool):
        user_settings.appearance.set_bar_separation(enabled)
        apply_bar_css()

    @staticmethod
    def setFloating(enabled: bool):
        user_settings.appearance.set_bar_floating(enabled)
        apply_bar_css()
        BarStyles.setSide(user_settings.appearance.bar_side)
        rebuild_corners()

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
        apply_bar_css()
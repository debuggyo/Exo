import os
from ignis import widgets, utils
from ignis.window_manager import WindowManager
from user_settings import user_settings
from .send_notification import send_notification
from modules.corners import Corners
from .wallpaper import Wallpaper

def rebuild_corners():
    Corners.destroy_all()
    if user_settings.interface.misc.screen_corners or user_settings.interface.bar.corners:
        Corners.build()

class BarStyles:
    bar_instance = None
    _rounded_corners_row = None

    @classmethod
    def set_bar_instance(cls, bar):
        cls.bar_instance = bar

    @classmethod
    def set_rounded_corners_row(cls, row_instance):
        cls._rounded_corners_row = row_instance

    @staticmethod
    def _apply_css(window):
        if not window:
            return

        side = user_settings.interface.bar.side
        vertical = user_settings.interface.bar.vertical
        separation = user_settings.interface.bar.separation
        floating = user_settings.interface.bar.floating
        centered = user_settings.interface.bar.centered
        compact_mode = user_settings.interface.bar.density

        all_possible_classes = {
            "hug", "extrapadding", "round", "floating", "full",
            "separated", "compact", "compact-plus", "ultracompact",
            "vertical", "top", "bottom", "left", "right", "horizontal"
        }

        for css_class in all_possible_classes:
            window.remove_css_class(css_class)

        if floating:
            window.add_css_class("floating")
        else:
            window.add_css_class("hug")
            if not centered:
                window.add_css_class("extrapadding")
            elif centered:
                window.add_css_class("round")

        if separation:
            window.add_css_class("separated")
        else:
            window.add_css_class("full")

        if compact_mode == 1:
            window.add_css_class("compact")
        elif compact_mode == 2:
            window.add_css_class("compact-plus")
        elif compact_mode == 3:
            window.add_css_class("ultracompact")

        if vertical:
            window.add_css_class("vertical")
        else:
            window.add_css_class("horizontal")

        window.add_css_class(side)

    @staticmethod
    def _update_all_layouts():
        if BarStyles.bar_instance:
            BarStyles.bar_instance.window_info.update_layout()
            BarStyles.bar_instance.media.update_layout()
            BarStyles.bar_instance.workspaces.update_layout()
            BarStyles.bar_instance.media.update_visibility()
            BarStyles.bar_instance.recording_indicator.update_layout()
            BarStyles.bar_instance.systeminfotray.update_layout()

    @staticmethod
    def _update_quick_center():
        wm = WindowManager.get_default()
        quick_center_window = wm.get_window("QuickCenter")
        if quick_center_window:
            quick_center_window.update_side()

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

        floating = user_settings.interface.bar.floating
        win.margin_top, win.margin_left, win.margin_right, win.margin_bottom = BarStyles._compute_margins(side, floating)

        width = 40
        height = 40
        compact_mode = user_settings.interface.bar.density
        if compact_mode == 1:
            width = 35
            height = 35
        elif compact_mode == 2:
            width = 30
            height = 30
        elif compact_mode == 3:
            width = 25
            height = 25

        win.set_width_request(width if vertical else -1)
        win.set_height_request(height if not vertical else -1)

        centered = user_settings.interface.bar.centered
        anchors = [side] if centered else (["top", "bottom", side] if vertical else ["left", "right", side])
        win.anchor = None
        win.anchor = anchors

        center_box = win.child
        start_box = center_box.get_start_widget()
        center_box_inner = center_box.get_center_widget()
        end_box = center_box.get_end_widget()

        center_box.vertical = vertical

        center_box.halign = "fill"
        center_box.valign = "fill"

        if start_box: start_box.vertical = vertical
        if center_box_inner: center_box_inner.vertical = vertical
        if end_box: end_box.vertical = vertical

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
        else:
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

        BarStyles._apply_css(win)

        BarStyles._update_quick_center()

    @staticmethod
    def setCompact(mode: int):
        user_settings.interface.bar.set_density(mode)
        if BarStyles.bar_instance:
            win = BarStyles.bar_instance.get_window()
            BarStyles._apply_css(win)

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
    def setRecordingIndicator(mode: str):
        user_settings.interface.bar.modules.set_recording_indicator(mode)
        if BarStyles.bar_instance and BarStyles.bar_instance.recording_indicator:
            BarStyles.bar_instance.recording_indicator.update_visibility()

    @staticmethod
    def setWorkspacesStyle(style: str):
        user_settings.interface.bar.modules.set_workspaces_style(style)
        if BarStyles.bar_instance and BarStyles.bar_instance.workspaces:
            BarStyles.bar_instance.workspaces.update_workspaces()
            BarStyles.bar_instance.workspaces.update_layout()

    @staticmethod
    def setSeparation(enabled: bool):
        user_settings.interface.bar.set_separation(enabled)
        if BarStyles.bar_instance:
            BarStyles._apply_css(BarStyles.bar_instance.get_window())

    @staticmethod
    def setFloating(enabled: bool):
        user_settings.interface.bar.set_floating(enabled)
        if BarStyles.bar_instance:
            BarStyles._apply_css(BarStyles.bar_instance.get_window())
        BarStyles.setSide(user_settings.interface.bar.side)
        rebuild_corners()
        BarStyles._update_all_layouts()
        BarStyles._update_rounded_corners_visibility()

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
            BarStyles._apply_css(BarStyles.bar_instance.get_window())
        BarStyles._update_rounded_corners_visibility()

    @staticmethod
    def setMilitaryTime(enabled: bool):
        user_settings.interface.bar.modules.set_military_time(enabled)
        BarStyles._update_all_layouts()

    @staticmethod
    def _update_rounded_corners_visibility():
        if BarStyles._rounded_corners_row:
            is_floating = user_settings.interface.bar.floating
            is_centered = user_settings.interface.bar.centered

            BarStyles._rounded_corners_row.visible = (not is_floating) and (not is_centered)

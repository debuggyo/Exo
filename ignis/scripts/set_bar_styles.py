from ignis.window_manager import WindowManager
from user_settings import user_settings
from modules.corners import Corners


def rebuild_corners():
    Corners.destroy_all()
    if (
        user_settings.interface.misc.screen_corners
        or user_settings.interface.misc.shell_corners
    ):
        Corners.build()


class BarStyles:
    bar_instance = None
    _rounded_corners_row = None

    @staticmethod
    def _get_bar_settings(bar_id: int):
        if bar_id == 0:
            return user_settings.interface.bar
        elif bar_id == 1:
            return user_settings.interface.bar2
        return user_settings.interface.bar

    @classmethod
    def set_bar_instance(cls, bar):
        cls.bar_instance = bar

    @classmethod
    def set_rounded_corners_row(cls, row_instance):
        cls._rounded_corners_row = row_instance

    @staticmethod
    def _apply_css(window, bar_id: int = 0):
        if not window:
            return

        bar_settings = BarStyles._get_bar_settings(bar_id)

        side = bar_settings.side
        vertical = bar_settings.vertical
        separation = bar_settings.separation
        floating = bar_settings.floating
        centered = bar_settings.centered
        compact_mode = bar_settings.density
        module_backgrounds = bar_settings.module_backgrounds
        bar_background = bar_settings.bar_background

        all_possible_classes = [
            "hug",
            "extrapadding",
            "round",
            "floating",
            "full",
            "separated",
            "compact",
            "compact-plus",
            "ultracompact",
            "vertical",
            "module-backgrounds",
            "bar-background",
            "top",
            "bottom",
            "left",
            "right",
            "horizontal",
        ]

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

        if module_backgrounds:
            window.add_css_class("module-backgrounds")

        if bar_background:
            window.add_css_class("bar-background")

        window.add_css_class(side)

    @staticmethod
    def _update_all_layouts():
        if BarStyles.bar_instance:
            BarStyles.bar_instance.update_layout()
            BarStyles.bar_instance.clock.update_layout()
            BarStyles.bar_instance.media.update_layout()
            BarStyles.bar_instance.recording_indicator.update_layout()
            BarStyles.bar_instance.recording_indicator.update_visibility()
            BarStyles.bar_instance.systeminfotray.update_layout()
            BarStyles.bar_instance.window_info.update_layout()
            BarStyles.bar_instance.workspaces.update_layout()

    @staticmethod
    def _update_quick_center():
        wm = WindowManager.get_default()
        quick_center_window = wm.get_window("QuickCenter")
        if quick_center_window:
            quick_center_window.update_side()

    @staticmethod
    def _compute_margins(side: str, bar_id: int = 0):
        bar_settings = BarStyles._get_bar_settings(bar_id)
        floating = bar_settings.floating
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
    def setSide(side: str, bar_id: int = 0):
        bar_settings = BarStyles._get_bar_settings(bar_id)
        bar_settings.set_side(side)
        vertical = side in ("left", "right")
        bar_settings.set_vertical(vertical)

        bar = BarStyles.bar_instance
        if not bar or not bar.get_window(bar_id):
            return

        win = bar.get_window(bar_id)

        floating = bar_settings.floating
        win.margin_top, win.margin_left, win.margin_right, win.margin_bottom = (
            BarStyles._compute_margins(side, bar_id)
        )

        width = 40
        height = 40
        compact_mode = bar_settings.density
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

        centered = bar_settings.centered
        anchors = (
            [side]
            if centered
            else (["top", "bottom", side] if vertical else ["left", "right", side])
        )
        win.anchor = None
        win.anchor = anchors

        center_box = win.child
        start_box = center_box.get_start_widget()
        center_box_inner = center_box.get_center_widget()
        end_box = center_box.get_end_widget()

        center_box.vertical = vertical

        center_box.halign = "fill"
        center_box.valign = "fill"

        if start_box:
            start_box.vertical = vertical
        if center_box_inner:
            center_box_inner.vertical = vertical
        if end_box:
            end_box.vertical = vertical

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

        BarStyles._apply_css(win, bar_id)

        BarStyles._update_quick_center()

    @staticmethod
    def setCompact(mode: int, bar_id: int = 0):
        bar_settings = BarStyles._get_bar_settings(bar_id)
        bar_settings.set_density(mode)
        if BarStyles.bar_instance:
            win = BarStyles.bar_instance.get_window(bar_id)
            BarStyles._apply_css(win, bar_id)

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
                if bar_settings.vertical:
                    win.set_width_request(width)
                else:
                    win.set_height_request(height)

        rebuild_corners()
        BarStyles._update_all_layouts()

    @staticmethod
    def setRecordingIndicator(mode: str, bar_id: int = 0):
        user_settings.interface.modules.options.set_recording_indicator(mode)
        BarStyles._update_all_layouts()

    @staticmethod
    def setWorkspacesStyle(style: str, bar_id: int = 0):
        user_settings.interface.modules.options.set_workspaces_style(style)
        if BarStyles.bar_instance and BarStyles.bar_instance.workspaces:
            BarStyles.bar_instance.workspaces.update_workspaces()
            BarStyles.bar_instance.workspaces.update_layout()

    @staticmethod
    def setSeparation(enabled: bool, bar_id: int = 0):
        BarStyles._get_bar_settings(bar_id).set_separation(enabled)
        if BarStyles.bar_instance:
            BarStyles._apply_css(BarStyles.bar_instance.get_window(bar_id), bar_id)

    @staticmethod
    def setBarBackground(enabled: bool, bar_id: int = 0):
        BarStyles._get_bar_settings(bar_id).set_bar_background(enabled)
        if BarStyles.bar_instance:
            BarStyles._apply_css(BarStyles.bar_instance.get_window(bar_id), bar_id)

    @staticmethod
    def setModuleBackgrounds(enabled: bool, bar_id: int = 0):
        BarStyles._get_bar_settings(bar_id).set_module_backgrounds(enabled)
        if BarStyles.bar_instance:
            BarStyles._apply_css(BarStyles.bar_instance.get_window(bar_id), bar_id)

    @staticmethod
    def setFloating(enabled: bool, bar_id: int = 0):
        bar_settings = BarStyles._get_bar_settings(bar_id)
        bar_settings.set_floating(enabled)
        if BarStyles.bar_instance:
            BarStyles._apply_css(BarStyles.bar_instance.get_window(bar_id), bar_id)
        BarStyles.setSide(bar_settings.side, bar_id)
        rebuild_corners()
        BarStyles._update_all_layouts()

    @staticmethod
    def setShellCorners(enabled: bool):
        user_settings.interface.misc.set_shell_corners(enabled)
        rebuild_corners()

    @staticmethod
    def setBarCenter(enabled: bool, bar_id: int = 0):
        bar_settings = BarStyles._get_bar_settings(bar_id)
        bar_settings.set_centered(enabled)
        BarStyles.setSide(bar_settings.side, bar_id)
        rebuild_corners()
        if BarStyles.bar_instance:
            BarStyles._apply_css(BarStyles.bar_instance.get_window(bar_id), bar_id)

    @staticmethod
    def setScreenCorners(enabled: str):
        user_settings.interface.misc.set_screen_corners(enabled)
        rebuild_corners()

    @staticmethod
    def setMilitaryTime(enabled: bool):
        user_settings.interface.modules.options.set_military_time(enabled)
        BarStyles._update_all_layouts()

    @staticmethod
    def setDateVisibility(enabled: bool):
        user_settings.interface.modules.options.set_show_date(enabled)
        BarStyles._update_all_layouts()

    @staticmethod
    def setDayMonthSwapped(enabled: bool):
        user_settings.interface.modules.options.set_day_month_swapped(enabled)
        BarStyles._update_all_layouts()

    @staticmethod
    def setWidgetLocation(widget: str, location: int):
        getattr(user_settings.interface.modules.location, f"set_{widget}")(location)
        BarStyles.bar_instance.update_layout()
        BarStyles._update_all_layouts()

    @staticmethod
    def setWidgetVisibility(widget: str, visibility: bool):
        getattr(user_settings.interface.modules.visibility, f"set_{widget}")(visibility)
        BarStyles.bar_instance.update_layout()
        BarStyles._update_all_layouts()

    @staticmethod
    def setWidgetBarID(widget: str, bar_id: int = 0):
        getattr(user_settings.interface.modules.bar_id, f"set_{widget}")(bar_id)
        BarStyles.bar_instance.update_layout()
        BarStyles._update_all_layouts()

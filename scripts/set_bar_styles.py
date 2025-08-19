from user_settings import user_settings

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
        return top, left, right, bottom  # return margins

    @staticmethod
    def setSide(side: str):
        user_settings.appearance.set_bar_side(side)
        user_settings.appearance.set_vertical(side in ("left", "right"))

        bar = BarStyles.bar_instance
        if bar:
            win = bar.get_window()
            if win:
                vertical = user_settings.appearance.vertical
                style = user_settings.appearance.style
                anchors = [side] if style == "island" else (["top", "bottom", side] if vertical else ["left", "right", side])

                win.anchor = None  # reset all previous anchors
                win.anchor = anchors  # apply new anchors
                win.margin_top, win.margin_left, win.margin_right, win.margin_bottom = BarStyles._compute_margins(side)


    @staticmethod
    def setCompact(mode: int):
        user_settings.appearance.set_compact(mode)  # set compact mode

    @staticmethod
    def setStyle(style: str):
        user_settings.appearance.set_style(style)  # set bar style

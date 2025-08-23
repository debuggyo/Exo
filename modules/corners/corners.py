import os
from ignis import widgets, utils
from ignis.icon_manager import IconManager
from user_settings import user_settings
icon_manager = IconManager.get_default()
icon_manager.add_icons(os.path.join(utils.get_current_dir(), "corners"))

class Corners:
    def corner(anchors: list, name, exclusivity, type, size: int = 25):
        css_classes = [f"{type}-corner"]
        image = ('-'.join(anchors)+"-symbolic")
        return widgets.Window(
            css_classes=css_classes,     
            anchor=anchors,
            visible=True,
            namespace=name,
            height_request=size,
            width_request=size,
            exclusivity=exclusivity,
            child=widgets.Icon(
                image=image,
                pixel_size=size
            )
        )

    def screen(anchors: list, bar_size):
        name = ("screen_corner_" + '_'.join(anchors))

        return Corners.corner(anchors, name, "ignore", "screen", bar_size)

    def bar(anchors: list):
        name = ("bar_corner_" + '_'.join(anchors))

        return Corners.corner(anchors, name, "normal", "bar")

    def build():
        bar_side = user_settings.appearance.bar_side
        bar_style = user_settings.appearance.style
        compact_mode = user_settings.appearance.compact
        top_size = bottom_size = 25

        if compact_mode == 0 or bar_style == "island":
            optimal_size = 25
        elif compact_mode == 1:
            optimal_size = 22.5
        elif compact_mode == 2:
            optimal_size = 20
        elif compact_mode == 3:
            optimal_size = 17.5

        if bar_side == "top":
            top_size = optimal_size
        elif bar_side == "bottom":
            bottom_size = optimal_size

        if user_settings.appearance.screen_corners:
            Corners.screen(["top", "left"], top_size)
            Corners.screen(["top", "right"], top_size)
            Corners.screen(["bottom", "left"], bottom_size)
            Corners.screen(["bottom", "right"], bottom_size)
        if bar_style == "connected" and user_settings.appearance.bar_corners:
            Corners.bar([bar_side, "left"])
            Corners.bar([bar_side, "right"])
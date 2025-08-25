import os
from ignis import widgets, utils
from ignis.icon_manager import IconManager
from user_settings import user_settings
icon_manager = IconManager.get_default()
icon_manager.add_icons(os.path.join(utils.get_current_dir(), "corners"))

class Corners:
    _windows = []  # Class-level list to keep track of all created windows

    @classmethod
    def corner(cls, anchors: list, name, exclusivity, type, size: int = 25):
        css_classes = [f"{type}-corner"]
        image = ('-'.join(anchors)+"-symbolic")
        
        win = widgets.Window(
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
        cls._windows.append(win)  # Add the new window to our list
        return win

    @classmethod
    def screen(cls, anchors: list, bar_size):
        name = ("screen_corner_" + '_'.join(anchors))
        return cls.corner(anchors, name, "ignore", "screen", bar_size)

    @classmethod
    def bar(cls, anchors: list):
        name = ("bar_corner_" + '_'.join(anchors))
        return cls.corner(anchors, name, "normal", "bar")

    @classmethod
    def build(cls):
        bar_side = user_settings.appearance.bar_side
        bar_centered = user_settings.appearance.bar_centered
        compact_mode = user_settings.appearance.compact
        top_size = bottom_size = 25

        if compact_mode == 0 or bar_centered:
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
            cls.screen(["top", "left"], top_size)
            cls.screen(["top", "right"], top_size)
            cls.screen(["bottom", "left"], bottom_size)
            cls.screen(["bottom", "right"], bottom_size)
        if not user_settings.appearance.bar_floating and not user_settings.appearance.bar_centered and user_settings.appearance.bar_corners:
            cls.bar([bar_side, "left"])
            cls.bar([bar_side, "right"])

    @classmethod
    def destroy_all(cls):
        """Destroys all tracked corner windows."""
        for window in cls._windows:
            window.destroy()
        cls._windows.clear()  # Clear the list after destroying the windows
import os
from ignis import widgets, utils
from ignis.icon_manager import IconManager
from user_settings import user_settings

icon_manager = IconManager.get_default()
icon_manager.add_icons(os.path.join(utils.get_current_dir(), "corners"))

class Corners:
    _windows = []

    @classmethod
    def corner(cls, anchors: list, name, exclusivity, corner_type, size: int = 25):
        css_classes = [f"{corner_type}-corner"]
        image = ('-'.join(anchors) + "-symbolic")
        
        for win in cls._windows:
            if win.namespace == name:
                return win

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
        cls._windows.append(win)
        return win

    @classmethod
    def screen(cls, anchors: list, corner_size):
        name = ("screen_corner_" + '_'.join(anchors))
        return cls.corner(anchors, name, "ignore", "screen", corner_size)

    @classmethod
    def bar(cls, anchors: list):
        name = ("bar_corner_" + '_'.join(anchors))
        return cls.corner(anchors, name, "normal", "bar")

    @classmethod
    def build(cls):
        bar_side = user_settings.interface.bar.side
        bar_centered = user_settings.interface.bar.centered
        bar_vertical = user_settings.interface.bar.vertical
        compact_mode = user_settings.interface.bar.density

        optimal_size = 25
        if compact_mode == 1:
            optimal_size = 22.5
        elif compact_mode == 2:
            optimal_size = 20
        elif compact_mode == 3:
            optimal_size = 17.5

        is_floating_and_uncentered = user_settings.interface.bar.floating and not bar_centered

        if user_settings.interface.misc.screen_corners:
            if is_floating_and_uncentered:
                top_left_size = optimal_size if bar_side in ["top", "left"] else 25
                top_right_size = optimal_size if bar_side in ["top", "right"] else 25
                bottom_left_size = optimal_size if bar_side in ["bottom", "left"] else 25
                bottom_right_size = optimal_size if bar_side in ["bottom", "right"] else 25

                cls.screen(["top", "left"], top_left_size)
                cls.screen(["top", "right"], top_right_size)
                cls.screen(["bottom", "left"], bottom_left_size)
                cls.screen(["bottom", "right"], bottom_right_size)
            else:
                cls.screen(["top", "left"], 25)
                cls.screen(["top", "right"], 25)
                cls.screen(["bottom", "left"], 25)
                cls.screen(["bottom", "right"], 25)
                
        is_not_floating_and_uncentered = not user_settings.interface.bar.floating and not bar_centered
        if is_not_floating_and_uncentered and user_settings.interface.bar.corners:
            if bar_vertical:
                cls.bar(["top", bar_side])
                cls.bar(["bottom", bar_side])
            else:
                cls.bar([bar_side, "left"])
                cls.bar([bar_side, "right"])

    @classmethod
    def destroy_all(cls):
        for window in cls._windows:
            window.destroy()
        cls._windows.clear()
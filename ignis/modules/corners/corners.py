from ignis import widgets
from user_settings import user_settings

class Corners:
    _windows = []

    @classmethod
    def corner(cls, anchors: list, name, exclusivity, corner_type, size: int = 25):
        css_classes = [f"{corner_type}-corner"]

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
            child=widgets.Corner(
                orientation='-'.join(anchors)
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
        bar = user_settings.interface.bar
        dock = user_settings.interface.dock
        misc = user_settings.interface.misc

        optimal_size = 25
        if bar.density == 1:
            optimal_size = 22.5
        elif bar.density == 2:
            optimal_size = 20
        elif bar.density == 3:
            optimal_size = 17.5

        if misc.screen_corners:
            if bar.floating and not bar.centered:
                corners = [
                    (["top", "left"], optimal_size if bar.side in ["top", "left"] else 25),
                    (["top", "right"], optimal_size if bar.side in ["top", "right"] else 25),
                    (["bottom", "left"], optimal_size if bar.side in ["bottom", "left"] else 25),
                    (["bottom", "right"], optimal_size if bar.side in ["bottom", "right"] else 25),
                ]

                for corner, size in corners:
                    cls.screen(corner, size)
            else:
                for corner in [["top", "left"], ["top", "right"], ["bottom", "left"], ["bottom", "right"]]:
                    cls.screen(corner, 25)

        if misc.shell_corners:
            dock = user_settings.interface.dock
            corners = []

            bar_is_not_floating_and_uncentered = not bar.floating and not bar.centered
            if bar_is_not_floating_and_uncentered:
                if bar.vertical:
                    corners.append(["top", bar.side])
                    corners.append(["bottom", bar.side])
                else:
                    corners.append([bar.side, "left"])
                    corners.append([bar.side, "right"])

            if dock.enabled:
                dock_is_not_floating_and_uncentered = not dock.floating and not dock.centered
                if dock_is_not_floating_and_uncentered:
                    if dock.vertical:
                        corners.append(["top", dock.side])
                        corners.append(["bottom", dock.side])
                    else:
                        corners.append([dock.side, "left"])
                        corners.append([dock.side, "right"])

            corners = list(map(list, set(map(tuple, corners)))) # remove duplicates

            for corner in corners:
                cls.bar(corner)

    @classmethod
    def destroy_all(cls):
        for window in cls._windows:
            window.destroy()
        cls._windows.clear()

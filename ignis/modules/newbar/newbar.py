from ignis import widgets
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty


class Bar(widgets.Window, BaseWidget):
    __gtype_name__ = "ExoBar"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        widgets.Window.__init__(self, namespace="ExoBar")
        self._constructing = True

        self._monitor: int = 0
        self._bar_id: int = 0
        self._side: str = "top"
        self._density: int = 0
        self._floating: bool = False
        self._centered: bool = False
        self._background: str = "full"
        self._start_background: bool = True
        self._center_background: bool = True
        self._end_background: bool = True
        self._start_module_bg: str = "separated"
        self._center_module_bg: str = "separated"
        self._end_module_bg: str = "separated"
        self._start_modules: list = []
        self._center_modules: list = []
        self._end_modules: list = []

        BaseWidget.__init__(self, **kwargs)
        self._constructing = False
        self.rebuild()

    def rebuild(self):
        if getattr(self, "_constructing", False):
            return

        self.vertical = self.side in ["left", "right"]
        self.anchor = [self.side]
        if not self.centered:
            key = {True: ["top", "bottom"], False: ["left", "right"]}
            self.anchor.extend(key[self.vertical])

        bar_size_key = {0: 40, 1: 35, 2: 30, 3: 25}
        if self.vertical:
            self.width = bar_size_key.get(self.density, 30)
            if self.floating:
                self.width += 5
            self.height = -1
        else:
            self.height = bar_size_key.get(self.density, 30)
            if self.floating:
                self.height += 5
            self.width = -1

        # Create areas
        start_modules_box = widgets.Box(
            vertical=self.vertical,
            css_classes=["area-modules", "start-modules"],
            child=self.start_modules,
        )

        center_modules_box = widgets.Box(
            vertical=self.vertical,
            css_classes=["area-modules", "center-modules"],
            child=self.center_modules,
        )

        end_modules_box = widgets.Box(
            vertical=self.vertical,
            css_classes=["area-modules", "end-modules"],
            child=self.end_modules,
        )

        self.start_area = widgets.Box(
            vertical=self.vertical,
            css_classes=["bar-area", "start-area"],
            child=[start_modules_box],
        )
        self.center_area = widgets.Box(
            vertical=self.vertical,
            css_classes=["bar-area", "center-area"],
            child=[center_modules_box],
        )
        self.end_area = widgets.Box(
            vertical=self.vertical,
            css_classes=["bar-area", "end-area"],
            child=[end_modules_box],
        )

        # Create container
        self.container = widgets.CenterBox(
            vertical=self.vertical,
            start_widget=self.start_area,
            center_widget=self.center_area,
            end_widget=self.end_area,
            css_classes=["bar_container"],
        )

        self.set_child(self.container)

        self.set_monitor(self.monitor)
        self.set_namespace(f"Bar{self.monitor}{self.bar_id}")
        self.set_height_request(self.height)
        self.set_width_request(self.width)
        self.set_anchor(self.anchor)
        self.set_exclusivity("exclusive")

        self.update_css_classes()

    def update_css_classes(self):
        # Window
        classes = ["bar-window", self.side]
        classes.append("vertical" if self.vertical else "horizontal")
        if self.floating:
            classes.append("floating")
        if self.centered:
            classes.append("centered")
        if self.background:
            classes.append(self.background)
        density_key = {0: "cozy", 1: "comfortable", 2: "compact", 3: "condensed"}
        if self.density in density_key:
            classes.append(density_key[self.density])
        self.set_css_classes(classes)

        # Areas
        for area in [self.start_area, self.center_area, self.end_area]:
            modules_key = {
                self.start_area: self.start_modules,
                self.center_area: self.center_modules,
                self.end_area: self.end_modules
            }
            backgrounds_key = {
                self.start_area: self.start_background,
                self.center_area: self.center_background,
                self.end_area: self.end_background
            }
            modules_bg_key = {
                self.start_area: self.start_module_bg,
                self.center_area: self.center_module_bg,
                self.end_area: self.end_module_bg
            }
            all_possible_classes = [
                "empty", "area-background", "module-backgrounds-connected", "module-backgrounds-separate"
            ]

            modules = modules_key[area]
            background = backgrounds_key[area]
            modules_bg = modules_bg_key[area]

            for css_class in all_possible_classes:
                area.remove_css_class(css_class)
            if len(modules) == 0:
                area.add_css_class("empty")
            if background:
                area.add_css_class("area-background")
            if modules_bg == "connected":
                area.add_css_class("module-backgrounds-connected")
            elif modules_bg == "separated":
                area.add_css_class("module-backgrounds-separated")

    @IgnisProperty
    def monitor(self) -> int:
        return self._monitor

    @monitor.setter
    def monitor(self, value: int) -> None:
        if self._monitor == value:
            return
        self._monitor = value
        self.rebuild()

    @IgnisProperty
    def bar_id(self) -> int:
        return self._bar_id

    @bar_id.setter
    def bar_id(self, value: int) -> None:
        if self._bar_id == value:
            return
        self._bar_id = value
        self.rebuild()

    @IgnisProperty
    def side(self) -> str:
        return self._side

    @side.setter
    def side(self, value: str) -> None:
        if self._side == value:
            return
        self._side = value
        self.rebuild()

    @IgnisProperty
    def density(self) -> int:
        return self._density

    @density.setter
    def density(self, value: int) -> None:
        if self._density == value:
            return
        self._density = value
        self.rebuild()

    @IgnisProperty
    def floating(self) -> bool:
        return self._floating

    @floating.setter
    def floating(self, value: bool) -> None:
        if self._floating == value:
            return
        self._floating = value
        self.rebuild()

    @IgnisProperty
    def centered(self) -> bool:
        return self._centered

    @centered.setter
    def centered(self, value: bool) -> None:
        if self._centered == value:
            return
        self._centered = value
        self.rebuild()

    @IgnisProperty
    def background(self) -> str:
        return self._background

    @background.setter
    def background(self, value: str):
        if self._background == value:
            return
        self._background = value
        self.rebuild()

    @IgnisProperty
    def start_background(self) -> bool:
        return self._start_background

    @start_background.setter
    def start_background(self, value: bool):
        if self._start_background == value:
            return
        self._start_background = value
        self.rebuild()

    @IgnisProperty
    def center_background(self) -> bool:
        return self._center_background

    @center_background.setter
    def center_background(self, value: bool):
        if self._center_background == value:
            return
        self._center_background = value
        self.rebuild()

    @IgnisProperty
    def end_background(self) -> bool:
        return self._end_background

    @end_background.setter
    def end_background(self, value: bool):
        if self._end_background == value:
            return
        self._end_background = value
        self.rebuild()

    @IgnisProperty
    def start_module_bg(self) -> str:
        return self._start_module_bg

    @start_module_bg.setter
    def start_module_bg(self, value: str):
        if self._start_module_bg == value:
            return
        self._start_module_bg = value
        self.rebuild()

    @IgnisProperty
    def center_module_bg(self) -> str:
        return self._center_module_bg

    @center_module_bg.setter
    def center_module_bg(self, value: str):
        if self._center_module_bg == value:
            return
        self._center_module_bg = value
        self.rebuild()

    @IgnisProperty
    def end_module_bg(self) -> str:
        return self._end_module_bg

    @end_module_bg.setter
    def end_module_bg(self, value: str):
        if self._end_module_bg == value:
            return
        self._end_module_bg = value
        self.rebuild()

    @IgnisProperty
    def start_modules(self) -> list:
        return self._start_modules

    @start_modules.setter
    def start_modules(self, value: list) -> None:
        self._start_modules = value
        self.rebuild()

    @IgnisProperty
    def center_modules(self) -> list:
        return self._center_modules

    @center_modules.setter
    def center_modules(self, value: list) -> None:
        self._center_modules = value
        self.rebuild()

    @IgnisProperty
    def end_modules(self) -> list:
        return self._end_modules

    @end_modules.setter
    def end_modules(self, value: list) -> None:
        self._end_modules = value
        self.rebuild()

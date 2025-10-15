from ignis import widgets
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
from gi.repository import GObject

class BarSide(GObject.GEnum):
    TOP = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3

class BarBackground(GObject.GEnum):
    FULL = 0
    AREAS = 1
    GRADIENT = 2
    NONE = 3

class ModuleBackground(GObject.GEnum):
    SEPARATED = 0
    CONNECTED = 1
    NONE = 2

class Bar(widgets.Window, BaseWidget):
    __gtype_name__ = "ExoBar"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        self._constructing = True
        self._bar_id: int = kwargs.get("bar_id", 0)
        unique_namespace = f"ExoBar{self.bar_id}"
        widgets.Window.__init__(self, namespace=unique_namespace)
        self._monitor: int = 0
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

        for module in self.start_modules + self.center_modules + self.end_modules:
            if hasattr(module, "get_parent"):
                parent = module.get_parent()
                if parent and hasattr(parent, "remove"):
                    parent.remove(module)

        self.vertical = self.side in ["left", "right"]
        self.anchor = [self.side]
        if not self.centered:
            key = {True: ["top", "bottom"], False: ["left", "right"]}
            self.anchor.extend(key[self.vertical])

        for module in self.start_modules + self.center_modules + self.end_modules:
            if hasattr(module, "vertical"):
                module.vertical = self.vertical
            if hasattr(module, "density"):
                module.density = self.density

        bar_size_key = {0: 40, 1: 35, 2: 30, 3: 25}
        if self.vertical:
            self.width = bar_size_key.get(self.density, 30)
            if self.floating and self.background != "full":
                self.width += 5
            self.height = -1
        else:
            self.height = bar_size_key.get(self.density, 30)
            if self.floating and self.background != "full":
                self.height += 5
            self.width = -1

        start_modules_box = widgets.Box(
            vertical=self.vertical,
            css_classes=["area-modules", "start-modules"],
            child=self.start_modules,
            spacing=2,
        )

        center_modules_box = widgets.Box(
            vertical=self.vertical,
            css_classes=["area-modules", "center-modules"],
            child=self.center_modules,
            spacing=2,
        )

        end_modules_box = widgets.Box(
            vertical=self.vertical,
            css_classes=["area-modules", "end-modules"],
            child=self.end_modules,
            spacing=2,
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

        if self.floating and self.background == "full":
            self.set_margin_top(5 if self.side != "bottom" else 0)
            self.set_margin_left(5 if self.side != "right" else 0)
            self.set_margin_right(5 if self.side != "left" else 0)
            self.set_margin_bottom(5 if self.side != "top" else 0)
        else:
            self.set_margin_top(0)
            self.set_margin_left(0)
            self.set_margin_right(0)
            self.set_margin_bottom(0)

        self.update_css_classes()

    def update_css_classes(self):
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
                "empty", "area-background", "module-backgrounds-connected", "module-backgrounds-separated"
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

    @IgnisProperty(type=BarSide, default=BarSide.TOP)
    def side(self) -> str:
        return self._side

    @side.setter
    def side(self, value: int) -> None:
        INT_TO_STR = {
            BarSide.TOP: "top",
            BarSide.BOTTOM: "bottom",
            BarSide.LEFT: "left",
            BarSide.RIGHT: "right",
        }
        new_side = INT_TO_STR.get(value)

        if not new_side or self._side == new_side:
            return

        self._side = new_side
        self.set_anchor(None)
        self.rebuild()

    @IgnisProperty(type=int, minimum=0, maximum=3, default=0)
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
        self.set_anchor(None)
        self.rebuild()

    @IgnisProperty(type=BarBackground, default=BarBackground.FULL)
    def background(self) -> str:
        return self._background

    @background.setter
    def background(self, value: int):
        INT_TO_STR = {
            BarBackground.FULL: "full",
            BarBackground.AREAS: "areas",
            BarBackground.GRADIENT: "gradient",
            BarBackground.NONE: "none",
        }
        new_background = INT_TO_STR.get(value)

        if not new_background or self._background == new_background:
            return
        self._background = new_background
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

    @IgnisProperty(type=ModuleBackground, default=ModuleBackground.SEPARATED)
    def start_module_bg(self) -> str:
        return self._start_module_bg

    @start_module_bg.setter
    def start_module_bg(self, value: int):
        INT_TO_STR = {
            ModuleBackground.SEPARATED: "separated",
            ModuleBackground.CONNECTED: "connected",
            ModuleBackground.NONE: "none",
        }
        new_bg = INT_TO_STR.get(value)

        if not new_bg or self._start_module_bg == new_bg:
            return
        self._start_module_bg = new_bg
        self.rebuild()

    @IgnisProperty(type=ModuleBackground, default=ModuleBackground.SEPARATED)
    def center_module_bg(self) -> str:
        return self._center_module_bg

    @center_module_bg.setter
    def center_module_bg(self, value: int):
        INT_TO_STR = {
            ModuleBackground.SEPARATED: "separated",
            ModuleBackground.CONNECTED: "connected",
            ModuleBackground.NONE: "none",
        }
        new_bg = INT_TO_STR.get(value)

        if not new_bg or self._center_module_bg == new_bg:
            return
        self._center_module_bg = new_bg
        self.rebuild()

    @IgnisProperty(type=ModuleBackground, default=ModuleBackground.SEPARATED)
    def end_module_bg(self) -> str:
        return self._end_module_bg

    @end_module_bg.setter
    def end_module_bg(self, value: int):
        INT_TO_STR = {
            ModuleBackground.SEPARATED: "separated",
            ModuleBackground.CONNECTED: "connected",
            ModuleBackground.NONE: "none",
        }
        new_bg = INT_TO_STR.get(value)

        if not new_bg or self._end_module_bg == new_bg:
            return
        self._end_module_bg = new_bg
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
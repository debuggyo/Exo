from ignis import widgets, utils
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty

from .modules import (
    Clock
)


class Bar(widgets.Window, BaseWidget):
    __gtype_name__ = "ExoBar"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        widgets.Window.__init__(self, namespace="ExoBar")
        self._monitor: int = 0
        self._bar_id: int = 0
        self._bar_options: dict = {}
        self._area_options: dict = {}
        self._modules: dict = {}

        self.build()

    def build(self):
        # Bar Options
        self.side = self._bar_options.get("side", "top")
        self.vertical = self.side in ["left", "right"]
        self.density = self._bar_options.get("density", 0)
        self.floating = self._bar_options.get("floating", False)
        self.centered = self._bar_options.get("centered", False)
        self.background = self._bar_options.get("background", "full")

        # Anchors
        self.anchor = [self.side]
        if not self.centered:
            key = {True: ["top", "bottom"], False: ["left", "right"]}
            self.anchor.extend(key[self.vertical])

        # heights
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

        # Area Options
        self.area_background = ["start", "center", "end"]
        self.module_backgrounds = {
            "start": "separate",
            "center": "separate",
            "end": "separate",
        }
        for area in ["start", "center", "end"]:
            if area in self._area_options:
                if "area_background" in self._area_options[area] and not self._area_options[area]["area_background"]:
                    self.area_background.remove(area)
                if "module_backgrounds" in self._area_options[area]:
                    module_background_option = self._area_options[area]["module_backgrounds"]
                    if module_background_option in ["connected", "separate", "none"]:
                        self.module_backgrounds[area] = module_background_option

        # Create areas
        self.start_modules = widgets.Box(vertical=self.vertical, css_classes=["area-modules", "start-modules"])
        self.center_modules = widgets.Box(vertical=self.vertical, css_classes=["area-modules", "center-modules"])
        self.end_modules = widgets.Box(vertical=self.vertical, css_classes=["area-modules", "end-modules"])

        self.start_area = widgets.Box(vertical=self.vertical, css_classes=["bar-area", "start-area"],
                                      child=self.start_modules)
        self.center_area = widgets.Box(vertical=self.vertical, css_classes=["bar-area", "center-area"],
                                       child=self.center_modules)
        self.end_area = widgets.Box(vertical=self.vertical, css_classes=["bar-area", "end-area"],
                                    child=self.end_modules)

        # Create container
        self.container = widgets.CenterBox(
            vertical=self.vertical,
            start_widget=self.start_area,
            center_widget=self.center_area,
            end_widget=self.end_area,
            css_classes=["bar_container"],
        )

        self.set_child(self.container)
        self.update_modules(self._modules)

        self.set_monitor(self._monitor)
        self.set_namespace(f"Bar{self._monitor}{self._bar_id}")
        self.set_height_request(self.height)
        self.set_width_request(self.width)
        self.set_anchor(self.anchor)
        self.set_exclusivity("exclusive")

        self.update_css_classes()
        return self

    def rebuild(self):
        # This is a simplified rebuild. A full destroy/re-create can be problematic.
        # For now, we just re-apply settings.
        self.build()

    def add_module(self, area, module_name, attrs):
        AREA_MAPPING = {
            "start": self.start_modules,
            "center": self.center_modules,
            "end": self.end_modules,
        }
        MODULE_MAPPING = {
            "ExampleLabel": widgets.Label,
            "ExampleButton": widgets.Button,
            "clock": Clock
        }
        func = MODULE_MAPPING.get(module_name)
        if func:
            AREA_MAPPING[area].append(func(**attrs))

    def update_modules(self, modules):
        for area in [self.start_modules, self.center_modules, self.end_modules]:
            # Clear children
            child = area.get_first_child()
            while child:
                area.remove(child)
                child = area.get_first_child()

        for area, inner_modules_list in modules.items():
            for module_data in inner_modules_list:
                for module_name, attrs in module_data.items():
                    self.add_module(area, module_name, attrs)
        self.update_css_classes()

    def update_css_classes(self):
        # Window
        classes = ["bar-window", self.side]
        classes.append("vertical" if self.vertical else "horizontal")
        if self.floating: classes.append("floating")
        if self.centered: classes.append("centered")
        if self.background: classes.append(self.background)
        density_key = {0: "cozy", 1: "comfortable", 2: "compact", 3: "condensed"}
        if self.density in density_key:
            classes.append(density_key[self.density])
        self.set_css_classes(classes)

        # Areas
        for area in [self.start_area, self.center_area, self.end_area]:
            key = {self.start_area: "start", self.center_area: "center", self.end_area: "end"}
            modules_key = {self.start_area: self.start_modules, self.center_area: self.center_modules,
                           self.end_area: self.end_modules}

            area.remove_css_class("empty")
            area.remove_css_class("area-background")
            area.remove_css_class(f"module-backgrounds-{self.module_backgrounds.get(key[area])}")

            if len(modules_key[area].child) == 0:
                area.add_css_class("empty")
            if key[area] in self.area_background:
                area.add_css_class("area-background")
            if key[area] in self.module_backgrounds:
                area.add_css_class(f"module-backgrounds-{self.module_backgrounds[key[area]]}")

    @IgnisProperty
    def monitor(self) -> int:
        return self._monitor

    @IgnisProperty
    def bar_id(self) -> int:
        return self._bar_id

    @IgnisProperty
    def bar_options(self) -> dict:
        return self._bar_options

    @IgnisProperty
    def area_options(self) -> dict:
        return self._area_options

    @IgnisProperty
    def modules(self) -> dict:
        return self._modules

    @monitor.setter
    def monitor(self, value: int) -> None:
        if self._monitor == value:
            return
        self._monitor = value
        self.rebuild()

    @bar_id.setter
    def bar_id(self, value: int) -> None:
        if self._bar_id == value:
            return
        self._bar_id = value
        self.rebuild()

    @bar_options.setter
    def bar_options(self, value: dict) -> None:
        if self._bar_options == value:
            return
        self._bar_options = value
        self.rebuild()

    @area_options.setter
    def area_options(self, value: dict) -> None:
        if self._area_options == value:
            return
        self._area_options = value
        self.rebuild()

    @modules.setter
    def modules(self, value: dict) -> None:
        if self._modules == value:
            return
        self._modules = value
        self.update_modules(value)

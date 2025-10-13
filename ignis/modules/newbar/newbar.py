from typing_extensions import Any
from ignis import widgets, utils
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty

from .modules import (
    Clock
)

class Bar:
    # __gtype_name__ = "ExoBar"
    # __gproperties__ = {**BaseWidget.gproperties}

    def __init__(
        self,
        monitor: int = 0,
        bar_id: int = 0,
        bar_options: dict[str, Any] = {},
        area_options: dict[str, Any] = {"start": {}, "center": {}, "end": {}},
        modules: dict[str, Any] = {"start": {}, "center": {}, "end": {}},
    ):
        self.monitor = monitor
        self.window = None
        self.bar_id = bar_id
        self.bar_options = bar_options
        self.area_options = area_options
        self.modules = modules

        self.build()

    def build(self):
        # Bar Options
        self.side = self.bar_options["side"] if "side" in self.bar_options else "top"  # ["top", "bottom", "left", "right"]
        self.vertical = True if self.side in ["left", "right"] else False
        self.density = self.bar_options["density"] if "density" in self.bar_options else 0  # [0, 1, 2, 3]
        self.floating = self.bar_options["floating"] if "floating" in self.bar_options else False  # [True, False]
        self.centered = self.bar_options["centered"] if "centered" in self.bar_options else False  # [True, False]
        self.background = (self.bar_options["background"] if "background" in self.bar_options else "full")  # ["full", "areas", "gradient", None]

        # Anchors
        self.anchor = [self.side]
        if not self.centered:
            key = {True: ["top", "bottom"], False: ["left", "right"]}
            self.anchor.extend(key[self.vertical])

        # heights
        bar_size_key = {0: 40, 1: 35, 2: 30, 3: 25}
        if self.vertical:
            self.width = bar_size_key[self.density]
            if self.floating:
                self.width += 5
            self.height = -1
        else:
            self.height = bar_size_key[self.density]
            if self.floating:
                self.height += 5
            self.width = -1

        # Area Options
        self.area_background = ["start", "center", "end"]
        self.module_backgrounds = {
            "start": "separate",
            "center": "separate",
            "end": "separate",
        }  # ["connected", "separate", "none"]
        for area in ["start", "center", "end"]:
            if area in self.area_options:
                if "area_background" in self.area_options[area]:
                    if not self.area_options[area]["area_background"]:
                        self.area_background.remove(area)
                if "module_backgrounds" in self.area_options[area]:
                    module_background_option = self.area_options[area]["module_backgrounds"]
                    if module_background_option in ["connected", "separate", "none"]:
                        self.module_backgrounds[area] = module_background_option

        # Create areas
        self.start_modules = widgets.Box(
            vertical=self.vertical,
            homogeneous=False,
            spacing=2,
            css_classes=["area-modules", "start-modules"],
        )
        self.center_modules = widgets.Box(
            vertical=self.vertical,
            homogeneous=False,
            spacing=2,
            css_classes=["area-modules", "center-modules"],
        )
        self.end_modules = widgets.Box(
            vertical=self.vertical,
            homogeneous=False,
            spacing=2,
            css_classes=["area-modules", "end-modules"],
        )
        self.start_area = widgets.Box(
            vertical=self.vertical,
            css_classes=["bar-area", "start-area"],
            child=self.start_modules,
        )
        self.center_area = widgets.Box(
            vertical=self.vertical,
            homogeneous=False,
            spacing=2,
            css_classes=["bar-area", "center-area"],
            child=self.center_modules,
        )
        self.end_area = widgets.Box(
            vertical=self.vertical,
            homogeneous=False,
            spacing=2,
            css_classes=["bar-area", "end-area"],
            child=self.end_modules,
        )

        # Create container
        self.container = widgets.CenterBox(
            vertical=self.vertical,
            start_widget=self.start_area,
            center_widget=self.center_area,
            end_widget=self.end_area,
            css_classes=["bar_container"],
        )

        self.update_modules(self.modules)

        # Create window
        self.window = widgets.Window(
            monitor=self.monitor,
            namespace=f"Bar{self.monitor}{self.bar_id}",
            child=self.container,
            visible=True,
            height_request=self.height,
            width_request=self.width,
            anchor=self.anchor,
            exclusivity="exclusive"
        )
        self.update_css_classes()
        return self.window

    def rebuild(self):
        self.window.destroy()
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
        # Clear all areas
        for area in [self.start_modules, self.center_modules, self.end_modules]:
            area.set_child([])
        # Populate modules
        for area, inner_modules_list in modules.items():
            for module_data in inner_modules_list:
                for module_name, attrs in module_data.items():
                    self.add_module(area, module_name, attrs)
        self.start_area.set_child([self.start_modules])
        self.center_area.set_child([self.center_modules])
        self.end_area.set_child([self.end_modules])

    def update_css_classes(self):
        # Window
        classes = ["bar-window", self.side]
        if self.vertical:
            classes.append("vertical")
        if self.floating:
            classes.append("floating")
        if self.centered:
            classes.append("centered")
        if self.background:
            classes.append(self.background)
        if self.density == 0:
            classes.append("cozy")
        elif self.density == 1:
            classes.append("comfortable")
        elif self.density == 2:
            classes.append("compact")
        elif self.density == 3:
            classes.append("condensed")
        self.window.set_css_classes(classes)

        # Areas
        for area in [self.start_area, self.center_area, self.end_area]:
            key = {
                self.start_area: "start",
                self.center_area: "center",
                self.end_area: "end",
            }
            modules_key = {
                self.start_area: self.start_modules,
                self.center_area: self.center_modules,
                self.end_area: self.end_modules,
            }
            possible_area_classes = ["empty", "area-background", "module-backgrounds"]
            for possible_class in possible_area_classes:
                area.remove_css_class(possible_class)
            if len(modules_key[area].child) == 0:
                area.add_css_class("empty")
            if key[area] in self.area_background:
                area.add_css_class("area-background")
            if key[area] in self.module_backgrounds:
                area.add_css_class(
                    f"module-backgrounds-{self.module_backgrounds[key[area]]}"
                )

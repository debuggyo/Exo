from typing_extensions import Any
from ignis import widgets, utils


class Bar:
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

    def build(self):
        # Bar Options
        self.side = (
            self.bar_options["side"] if "side" in self.bar_options else "top"
        )  # ["top", "bottom", "left", "right"]
        self.vertical = True if self.side in ["left", "right"] else False
        self.density = (
            self.bar_options["density"] if "density" in self.bar_options else 0
        )  # [0, 1, 2, 3]
        self.floating = (
            self.bar_options["floating"] if "floating" in self.bar_options else False
        )  # [True, False]
        self.centered = (
            self.bar_options["centered"] if "centered" in self.bar_options else False
        )  # [True, False]
        self.background = (
            self.bar_options["background"]
            if "background" in self.bar_options
            else "full"
        )  # ["full", "areas", "gradient", None]

        # Anchors
        self.anchor = [self.side]
        if not self.centered:
            key = {True: ["top", "bottom"], False: ["left", "right"]}
            self.anchor.extend(key[self.vertical])

        # Margins
        self.top_margin = self.left_margin = self.right_margin = self.bottom_margin = 0
        if self.floating:
            self.top_margin = 0 if self.side == "bottom" else 5
            self.left_margin = 0 if self.side == "right" else 5
            self.right_margin = 0 if self.side == "left" else 5
            self.bottom_margin = 0 if self.side == "top" else 5

        bar_size_key = {0: 40, 1: 35, 2: 30, 3: 25}
        if self.vertical:
            self.width = bar_size_key[self.density]
            self.height = -1
        else:
            self.height = bar_size_key[self.density]
            self.width = -1

        # Area Options
        self.area_background = (
            self.area_options["area_background"]
            if "area_background" in self.area_options
            else None
        )  # [True, False]
        self.module_backgrounds = (
            self.area_options["module_backgrounds"]
            if "module_backgrounds" in self.area_options
            else None
        )  # [True, False]

        # Modules
        self.start_modules = self.modules["start"] if "start" in self.modules else None
        self.center_modules = (
            self.modules["center"] if "center" in self.modules else None
        )
        self.end_modules = self.modules["end"] if "end" in self.modules else None

        # Create areas
        for name in ["start", "center", "end"]:
            css_class = f"{name}_modules"
            box_widget = widgets.Box(
                vertical=self.vertical,
                homogeneous=False,
                spacing=2,
                css_classes=["bar-area", css_class],
            )
            setattr(self, name, box_widget)

        # Create container
        self.container = widgets.CenterBox(
            vertical=self.vertical,
            start_widget=self.start,
            center_widget=self.center,
            end_widget=self.end,
            css_classes=["bar_container"],
        )

        self.update_modules(self.modules)

        # Create window
        self.window = widgets.Window(
            monitor=self.monitor,
            namespace=f"bar_{self.bar_id}",
            child=self.container,
            visible=True,
            height_request=self.height,
            width_request=self.width,
            anchor=self.anchor,
            exclusivity="exclusive",
            margin_top=self.top_margin,
            margin_left=self.left_margin,
            margin_right=self.right_margin,
            margin_bottom=self.bottom_margin,
        )
        self.update_css_classes()
        return self.window

    def rebuild(self):
        self.window.destroy()
        self.build()

    def add_module(self, area, module_name, attrs):
        AREA_MAPPING = {"start": self.start, "center": self.center, "end": self.end}
        MODULE_MAPPING = {
            "ExampleLabel": widgets.Label,
            "ExampleButton": widgets.Button,
        }
        func = MODULE_MAPPING.get(module_name)
        if func:
            AREA_MAPPING[area].append(func(**attrs))

    def update_modules(self, modules):
        # Clear all areas
        for area in [self.start, self.center, self.end]:
            area.set_child([])
            area.remove_css_class("empty")
        # Populate modules
        for area, inner_modules_list in modules.items():
            for module_data in inner_modules_list:
                for module_name, attrs in module_data.items():
                    self.add_module(area, module_name, attrs)
        for area in [self.start, self.center, self.end]:
            if len(area.child) == 0:
                area.add_css_class("empty")

    def update_css_classes(self):
        classes = ["bar-window"]
        classes.append(self.side)
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

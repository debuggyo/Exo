from ignis import widgets
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
from gi.repository import GObject, Gtk
from ignis.services.niri import NiriService
import modules.newbar.modules.settings as settings

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
        self._autohide: bool = False
        self._autohide_fullscreen: bool = False
        self._start_background: bool = True
        self._center_background: bool = True
        self._end_background: bool = True
        self._start_module_bg: str = "separated"
        self._center_module_bg: str = "separated"
        self._end_module_bg: str = "separated"
        self._start_modules: list = []
        self._center_modules: list = []
        self._end_modules: list = []
        self._hot_edge = None
        self._motion_controller = None
        self.niri = NiriService.get_default()

        # Creating the rows before initializing the base widget
        self.modifiers_settings_row = settings.MultiSelectRow(
            icon_name="style",
            title="Modifiers",
            items=[
                ("Floating", lambda: self._floating, lambda v: setattr(self, "floating", v), "page_header"),
                ("Centered", lambda: self._centered, lambda v: setattr(self, "centered", v), "collapse_content"),
            ]
        )
        self.side_settings_row = settings.SingleSelectRow(
            icon_name="toolbar",
            title="Side",
            items=[
                ("Top", "top", "align_vertical_top"),
                ("Bottom", "bottom", "align_vertical_bottom"),
                ("Left", "left", "align_horizontal_left"),
                ("Right", "right", "align_horizontal_right"),
            ]
        )
        self.density_settings_row = settings.SingleSelectRow(
            icon_name="view_compact",
            title="Density",
            items=[
                ("Cozy", 0, "density_large"),
                ("Comfortable", 1, "density_medium"),
                ("Compact", 2, "density_small"),
                ("Condensed", 3, "format_align_justify"),
            ]
        )
        self.autohide_switch = settings.SwitchRow(icon_name="shelf_auto_hide", title="Autohide")
        self.autohide_fullscreen_switch = settings.SwitchRow(icon_name="aspect_ratio", title="Autohide Fullscreen", description="Allows the bar to reveal when in a fullscreen window.")

        BaseWidget.__init__(self, **kwargs)

        # Binding the options after initializing so it doesn't set the options to their defaults
        self.side_settings_row.bind_option(self, "side")
        self.density_settings_row.bind_option(self, "density")
        self.autohide_switch.bind_option(self, "autohide")
        self.autohide_fullscreen_switch.bind_option(self, "autohide_fullscreen")

        self.options = settings.Window(
            title=f"Bar {self.bar_id+1}",
            visible=False,
            anchor=[self._side],
            content=[
                self.side_settings_row,
                self.density_settings_row,
                self.modifiers_settings_row,
                self.autohide_switch,
                self.autohide_fullscreen_switch
            ]
        )


        if self.niri.is_available:
            self.niri.connect("notify::overview-opened", self.niri_overview_opened)


        click_controller = Gtk.GestureClick.new()
        click_controller.set_button(3)
        click_controller.connect("pressed", self.open_options)
        self.add_controller(click_controller)

        self._constructing = False
        self.rebuild()

    def rebuild(self):
        if getattr(self, "_constructing", False):
            return

        if self._hot_edge:
            self._hot_edge.destroy()
            self._hot_edge = None

        for module in self.start_modules + self.center_modules + self.end_modules:
            if hasattr(module, "get_parent"):
                parent = module.get_parent()
                if parent and hasattr(parent, "remove"):
                    parent.remove(module)
            module.add_css_class("bar-module")

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

        bar_size_key = {0: 40, 1: 34, 2: 30, 3: 24}
        if self.vertical:
            self.width = bar_size_key.get(self.density, 40)
            if self.floating and self.background != "full":
                self.width += 5
            self.height = -1
        else:
            self.height = bar_size_key.get(self.density, 40)
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

        bar_size = {0: 40, 1: 34, 2: 30, 3: 24}.get(self.density, 40)
        if self.vertical:
            self.start_area.set_width_request(bar_size)
            self.center_area.set_width_request(bar_size)
            self.end_area.set_width_request(bar_size)
        else:
            self.start_area.set_height_request(bar_size)
            self.center_area.set_height_request(bar_size)
            self.end_area.set_height_request(bar_size)

        self.container = widgets.CenterBox(
            vertical=self.vertical,
            start_widget=self.start_area,
            center_widget=self.center_area,
            end_widget=self.end_area,
            css_classes=["bar-container"],
        )

        self.revealer = widgets.Revealer(
            child=self.container,
            transition_duration=300,
            transition_type="none",
        )
        self.revealer.connect("notify::child-revealed", self._on_revealer_state_change)
        self.set_child(self.revealer)

        self.set_monitor(self.monitor)
        self.set_namespace(f"Bar{self.monitor}{self.bar_id}")
        self.set_height_request(self.height)
        self.set_width_request(self.width)
        self.set_anchor(self.anchor)

        if self._motion_controller:
            self.remove_controller(self._motion_controller)

        self.update_css_classes()

        if self.autohide:
            if self.niri and self.niri.is_available:
                transition_map = {
                    "top": "slide_down",
                    "bottom": "slide_up",
                    "left": "slide_right",
                    "right": "slide_left",
                }
                self.revealer.set_transition_type(transition_map.get(self.side, "none"))

                alignment_map = {
                    "top": ("valign", "start"),
                    "bottom": ("valign", "end"),
                    "left": ("halign", "start"),
                    "right": ("halign", "end"),
                }
                prop, align = alignment_map.get(self.side, (None, None))
                if prop:
                    self.container.set_property(prop, align)
            else:
                self.container.set_valign("fill")
                self.container.set_halign("fill")

            layer = "overlay" if self.autohide_fullscreen else "top"
            self.set_layer(layer)
            self.set_exclusivity("ignore")
            self._motion_controller = Gtk.EventControllerMotion()
            self._motion_controller.connect("leave", self._on_bar_leave)
            self.add_controller(self._motion_controller)
            self._create_hot_edge()
            self.set_visible(False)
        else:
            self.set_layer("top")
            self.set_exclusivity("exclusive")
            self.container.set_valign("fill")
            self.container.set_halign("fill")
            self.revealer.set_reveal_child(True)
            self.set_visible(True)

    def _create_hot_edge(self):
        self._hot_edge = widgets.Window(
            namespace=f"ExoBarHotEdge{self.bar_id}",
            monitor=self.monitor,
            layer="overlay" if self.autohide_fullscreen else "top",
            exclusivity="ignore",
            css_classes=["hot-edge"]
        )
        anchor = [self.side, "left", "right"] if not self.vertical else [self.side, "top", "bottom"]
        self._hot_edge.set_anchor(anchor)

        if self.vertical:
            self._hot_edge.set_width_request(2)
            self._hot_edge.set_height_request(-1)
        else:
            self._hot_edge.set_height_request(2)
            self._hot_edge.set_width_request(-1)

        hot_edge_controller = Gtk.EventControllerMotion()
        hot_edge_controller.connect("enter", self._on_hot_edge_enter)
        self._hot_edge.add_controller(hot_edge_controller)
        self._hot_edge.show()

    def _on_hot_edge_enter(self, controller, x, y):
        if self.autohide and not self.revealer.get_child_revealed():
            self.set_visible(True)
            self.revealer.set_reveal_child(True)

    def _on_bar_leave(self, controller, *args):
        if self.autohide and self.revealer.get_child_revealed():
            self.revealer.set_reveal_child(False)

    def _on_revealer_state_change(self, revealer, _):
        if self.autohide and not revealer.get_child_revealed():
            self.set_visible(False)

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

    def niri_overview_opened(self, *args):
        if self.niri.overview_opened:
            self.add_css_class("niri-overview-opened")
            if self._autohide:

                self.set_visible(True)
                self.revealer.set_reveal_child(True)
        else:
            self.remove_css_class("niri-overview-opened")
            if self._autohide:
                self.revealer.set_reveal_child(False)

    @IgnisProperty
    def monitor(self) -> int:
        return self._monitor

    @monitor.setter
    def monitor(self, value: int):
        if self._monitor == value:
            return
        self._monitor = value
        self.rebuild()

    @IgnisProperty
    def bar_id(self) -> int:
        return self._bar_id

    @bar_id.setter
    def bar_id(self, value: int):
        if self._bar_id == value:
            return
        self._bar_id = value
        self.rebuild()

    @IgnisProperty(type=BarSide, default=BarSide.TOP)
    def side(self) -> str:
        return self._side

    @side.setter
    def side(self, value):
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

        icon_key = {
            BarSide.TOP: "toolbar",
            BarSide.BOTTOM: "dock_to_bottom",
            BarSide.LEFT: "dock_to_right",
            BarSide.RIGHT: "dock_to_left",
        }
        self.side_settings_row.set_icon_name(icon_key[value])

    @IgnisProperty(type=int, minimum=0, maximum=3, default=0)
    def density(self) -> int:
        return self._density

    @density.setter
    def density(self, value: int):
        if self._density == value:
            return
        self._density = value
        self.rebuild()

    @IgnisProperty
    def floating(self) -> bool:
        return self._floating

    @floating.setter
    def floating(self, value: bool):
        if self._floating == value:
            return
        self._floating = value
        self.rebuild()

    @IgnisProperty
    def centered(self) -> bool:
        return self._centered

    @centered.setter
    def centered(self, value: bool):
        if self._centered == value:
            return
        self._centered = value
        self.set_anchor(None)
        self.rebuild()

    @IgnisProperty(type=BarBackground, default=BarBackground.FULL)
    def background(self) -> str:
        return self._background

    @background.setter
    def background(self, value):
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
    def autohide(self) -> bool:
        return self._autohide

    @autohide.setter
    def autohide(self, value: bool):
        if self._autohide == value:
            return
        self._autohide = value
        self.rebuild()

    @IgnisProperty
    def autohide_fullscreen(self) -> bool:
        return self._autohide_fullscreen

    @autohide_fullscreen.setter
    def autohide_fullscreen(self, value: bool):
        if self._autohide_fullscreen == value:
            return
        self._autohide_fullscreen = value
        if self.autohide:
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
    def start_module_bg(self, value):
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
    def center_module_bg(self, value):
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
    def end_module_bg(self, value):
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
    def start_modules(self, value: list):
        self._start_modules = value
        self.rebuild()

    @IgnisProperty
    def center_modules(self) -> list:
        return self._center_modules

    @center_modules.setter
    def center_modules(self, value: list):
        self._center_modules = value
        self.rebuild()

    @IgnisProperty
    def end_modules(self) -> list:
        return self._end_modules

    @end_modules.setter
    def end_modules(self, value: list):
        self._end_modules = value
        self.rebuild()

    def open_options(self, *args):
        self.options.set_visible(True)
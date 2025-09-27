from ignis import widgets
from user_settings import user_settings
from .widgets import WindowInfo, Workspaces, Media, SystemInfoTray, Clock
from ignis.css_manager import CssManager
from ignis.window_manager import WindowManager
from scripts import BarStyles
from scripts.recorder import set_indicator
from .widgets.recording_indicator import RecordingIndicator

css_manager = CssManager.get_default()
window_manager = WindowManager.get_default()


class Bar:
    def __init__(self, monitor: int = 0):
        self.monitor = monitor
        self.__win = None
        self.media = Media()
        self.window_info = WindowInfo()
        self.workspaces = Workspaces()
        self.recording_indicator = RecordingIndicator()
        self.systeminfotray = SystemInfoTray()
        self.clock = Clock()
        set_indicator(self.recording_indicator)

        self.media_widget = self.media.widget()
        self.window_info_widget = self.window_info.widget()
        self.workspaces_widget = self.workspaces.widget()
        self.recording_indicator_widget = self.recording_indicator.widget()
        self.systeminfotray_widget = self.systeminfotray.widget()
        self.clock_widget = self.clock.widget()

    def build(self):
        side = user_settings.interface.bar.side
        vertical = user_settings.interface.bar.vertical
        compact_mode = user_settings.interface.bar.density

        height = 40
        width = 40
        if compact_mode == 1:
            height = 35
            width = 35
        elif compact_mode == 2:
            height = 30
            width = 30
        elif compact_mode == 3:
            height = 25
            width = 25

        anchors = (
            [side]
            if user_settings.interface.bar.centered
            else (["top", "bottom", side] if vertical else ["left", "right", side])
        )

        if vertical:
            size_request = {"width_request": width}
        else:
            size_request = {"height_request": height}

        self.left_widgets = widgets.Box(
            vertical=vertical,
            spacing=2,
            css_classes=["left-widgets"],
        )

        self.center_widgets = widgets.Box(
            vertical=vertical,
            spacing=2,
            css_classes=["center-widgets"],
        )

        self.right_widgets = widgets.Box(
            vertical=vertical,
            spacing=2,
            css_classes=["right-widgets"],
        )

        self.update_layout()

        self.__win = widgets.Window(
            namespace="Bar",
            monitor=self.monitor,
            anchor=anchors,
            css_classes=["bar"],
            exclusivity="exclusive",
            **size_request,
            child=widgets.CenterBox(
                vertical=vertical,
                css_classes=["bar-widgets"],
                start_widget=self.left_widgets,
                center_widget=self.center_widgets,
                end_widget=self.right_widgets,
            ),
        )

        BarStyles.setFloating(user_settings.interface.bar.floating)

        return self.__win

    def update_layout(self):
        self.left_widgets.set_child([])
        self.center_widgets.set_child([])
        self.right_widgets.set_child([])
        location_setting = user_settings.interface.bar.modules.location
        visibility_setting = user_settings.interface.bar.modules.visibility

        widgets = {
            "window_info": {
                "name": "window_info",
                "widget": self.window_info_widget,
            },
            "media": {
                "name": "media",
                "widget": self.media_widget,
            },
            "workspaces": {
                "name": "workspaces",
                "widget": self.workspaces_widget,
            },
            "recording_indicator": {
                "name": "recording_indicator",
                "widget": self.recording_indicator_widget,
            },
            "systeminfotray": {
                "name": "systeminfotray",
                "widget": self.systeminfotray_widget,
            },
            "clock": {
                "name": "clock",
                "widget": self.clock_widget,
            },
        }

        def location(location):
            if location == 0:
                return self.left_widgets
            elif location == 1:
                return self.center_widgets
            elif location == 2:
                return self.right_widgets
            else:
                raise ValueError("Invalid location")

        for widget in widgets.values():
            location(getattr(location_setting, widget["name"])).append(widget["widget"])
            widget["widget"].set_visible(getattr(visibility_setting, widget["name"]))

        for area in [self.left_widgets, self.center_widgets, self.right_widgets]:
            if len(area.child) == 0:
                area.add_css_class("empty")
            else:
                area.remove_css_class("empty")

    def get_window(self):
        return self.__win

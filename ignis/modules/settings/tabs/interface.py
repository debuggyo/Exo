from warnings import showwarning
from ignis import widgets
from modules.m3components import Button
from scripts import BarStyles, send_notification
from user_settings import user_settings
from ..widgets import CategoryLabel, make_toggle_buttons, SwitchRow, SettingsRow
from ignis.app import IgnisApp

app = IgnisApp.get_initialized()


class BarCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=5,
        )

        self.append(CategoryLabel("Bar"))

        self.append(
            SettingsRow(
                title="Position",
                description="Pick a side for the bar to be located.",
                child=[
                    make_toggle_buttons(
                        [
                            ("Top", "top", "align_vertical_top"),
                            ("Bottom", "bottom", "align_vertical_bottom"),
                            ("Left", "left", "align_horizontal_left"),
                            ("Right", "right", "align_horizontal_right"),
                        ],
                        lambda: user_settings.interface.bar.side,
                        BarStyles.setSide,
                        on_any_click=None,
                    )
                ],
            )
        )

        self.append(
            SettingsRow(
                title="Density",
                description="Pick between 4 different density options.",
                child=[
                    make_toggle_buttons(
                        [
                            ("Cozy", 0, "density_large"),
                            ("Comfortable", 1, "density_medium"),
                            ("Compact", 2, "density_small"),
                            ("Condensed", 3, "list"),
                        ],
                        lambda: user_settings.interface.bar.density,
                        BarStyles.setCompact,
                        on_any_click=None,
                    )
                ],
            )
        )

        self.append(
            SwitchRow(
                title="Floating Bar",
                description="Make the bar float away from the edges of the screen.",
                active=user_settings.interface.bar.floating,
                on_change=lambda x, active: BarStyles.setFloating(active),
            )
        )

        self.append(
            SwitchRow(
                title="Separated Islands",
                description="Seperate the bar into 3 separate 'islands'.",
                active=user_settings.interface.bar.separation,
                on_change=lambda x, active: BarStyles.setSeparation(active),
            )
        )

        self.append(
            SwitchRow(
                title="Extend to Edges",
                description="Make the bar span the full width of the screen.",
                active=(not user_settings.interface.bar.centered),
                on_change=lambda x, active: BarStyles.setBarCenter(not active),
            )
        )


class Bar2Category(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=5,
        )

        self.append(CategoryLabel("Second Bar"))

        self.append(
            SettingsRow(
                description="The second bar will be automatically enabled if any modules are located in it.\nIt will automatically be disabled if there are no modules located in it.\nNote: If any disabled modules are located in the second bar, it will still be enabled.",
            )
        )

        self.append(
            SettingsRow(
                title="Position",
                description="Pick a side for the bar to be located.",
                child=[
                    make_toggle_buttons(
                        [
                            ("Top", "top", "align_vertical_top"),
                            ("Bottom", "bottom", "align_vertical_bottom"),
                            ("Left", "left", "align_horizontal_left"),
                            ("Right", "right", "align_horizontal_right"),
                        ],
                        lambda: user_settings.interface.bar2.side,
                        BarStyles.setSide,
                        on_any_click=None,
                        bar_id=1,
                    )
                ],
            )
        )

        self.append(
            SettingsRow(
                title="Density",
                description="Pick between 4 different density options.",
                child=[
                    make_toggle_buttons(
                        [
                            ("Cozy", 0, "density_large"),
                            ("Comfortable", 1, "density_medium"),
                            ("Compact", 2, "density_small"),
                            ("Condensed", 3, "list"),
                        ],
                        lambda: user_settings.interface.bar2.density,
                        BarStyles.setCompact,
                        on_any_click=None,
                        bar_id=1,
                    )
                ],
            )
        )

        self.append(
            SwitchRow(
                title="Floating Bar",
                description="Make the bar float away from the edges of the screen.",
                active=user_settings.interface.bar2.floating,
                on_change=lambda x, active: BarStyles.setFloating(active, 1),
            )
        )

        self.append(
            SwitchRow(
                title="Separated Islands",
                description="Seperate the bar into 3 separate 'islands'.",
                active=user_settings.interface.bar2.separation,
                on_change=lambda x, active: BarStyles.setSeparation(active, 1),
            )
        )

        self.append(
            SwitchRow(
                title="Extend to Edges",
                description="Make the bar span the full width of the screen.",
                active=(not user_settings.interface.bar2.centered),
                on_change=lambda x, active: BarStyles.setBarCenter(not active, 1),
            )
        )


class NotificationsCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=5,
        )

        self.append(CategoryLabel("Notifications"))

        self.append(
            SettingsRow(
                title="Popup Location",
                description="Pick a location for your notification popups.",
                child=[
                    make_toggle_buttons(
                        [
                            ("", ["top", "left"], "north_west"),
                            ("Top", ["top"], "north"),
                            ("", ["top", "right"], "north_east"),
                            ("", ["bottom", "left"], "south_west"),
                            ("Bottom", ["bottom"], "south"),
                            ("", ["bottom", "right"], "south_east"),
                        ],
                        lambda: user_settings.interface.notifications.anchor,
                        user_settings.interface.notifications.set_anchor,
                        on_any_click=None,
                    ),
                ],
            )
        )
        self.append(
            SwitchRow(
                title="Compact Pop-up",
                description="Show a more compact pop-up for incoming notifications.",
                active=user_settings.interface.notifications.compact_popup,
                on_change=lambda x,
                active: user_settings.interface.notifications.set_compact_popup(active),
            )
        )

        self.append(
            SettingsRow(
                title="Send a Test Notification",
                child=[
                    Button.button(
                        icon="notifications_unread",
                        label="Test Notification",
                        halign="start",
                        size="xs",
                        on_click=lambda x: send_notification(
                            "Test Notification", "This is a test notification!"
                        ),
                    )
                ],
            )
        )


class BarModuleSettings(SettingsRow):
    def __init__(self, name: str, widget_name: str, description: str):
        self._widget_name = widget_name

        super().__init__(
            title=f"{name} Widget",
            description=description,
            css_classes=["module-options"],
            child=[
                widgets.Box(
                    vertical=False,
                    child=[
                        make_toggle_buttons(
                            [
                                (None, 0, "timer_1"),
                                (None, 1, "timer_2"),
                            ],
                            lambda: getattr(
                                user_settings.interface.modules.bar_id,
                                self._widget_name,
                            ),
                            self._set_widget_bar_id,
                            on_any_click=None,
                            widget=self._widget_name,
                        ),
                    ],
                ),
                widgets.Separator(),
                widgets.Box(
                    vertical=False,
                    child=[
                        make_toggle_buttons(
                            [
                                ("Start", 0),
                                ("Center", 1),
                                ("End", 2),
                            ],
                            lambda: getattr(
                                user_settings.interface.modules.location,
                                self._widget_name,
                            ),
                            self._set_widget_location,
                            on_any_click=None,
                            widget=self._widget_name,
                        ),
                    ],
                ),
                widgets.Separator(),
                widgets.Switch(
                    vexpand=False,
                    valign="center",
                    active=getattr(
                        user_settings.interface.modules.visibility,
                        self._widget_name,
                    ),
                    on_change=self._set_widget_visibility,
                ),
            ],
        )

    def _set_widget_location(self, _, value):
        BarStyles.setWidgetLocation(self._widget_name, value)

    def _set_widget_visibility(self, _, active: bool):
        BarStyles.setWidgetVisibility(self._widget_name, active)

    def _set_widget_bar_id(self, _, value):
        BarStyles.setWidgetBarID(self._widget_name, value)


class BarModulesCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=5,
            child=[
                CategoryLabel("Bar Modules"),
            ],
        )

        modules = {
            "launcher": {
                "name": "Launcher",
                "widget": "launcher",
                "description": "Button to open the Launcher.",
            },
            "window_info": {
                "name": "Window Info",
                "widget": "window_info",
                "description": "Shows information about the active window.",
            },
            "media": {
                "name": "Media",
                "widget": "media",
                "description": "Shows the currently playing media with controls.",
            },
            "workspaces": {
                "name": "Workspaces",
                "widget": "workspaces",
                "description": "Shows a list of workspaces.",
            },
            "tasks": {
                "name": "Tasks",
                "widget": "tasks",
                "description": "Shows pinned and currently running applications.",
            },
            "recording_indicator": {
                "name": "Recording Indicator",
                "widget": "recording_indicator",
                "description": "Shows the current recording status.",
            },
            "systeminfotray": {
                "name": "System Tray",
                "widget": "systeminfotray",
                "description": "Shows system tray icons.",
            },
            "clock": {
                "name": "Clock",
                "widget": "clock",
                "description": "Shows the current time and date.",
            },
        }

        for module in modules.values():
            name = module["name"]
            widget_name = module["widget"]
            description = module["description"]

            self.append(BarModuleSettings(name, widget_name, description))


class ExtraBarCategory(widgets.Box):
    military_time = user_settings.interface.modules.options.military_time
    show_date = user_settings.interface.modules.options.show_date
    day_month_swapped = user_settings.interface.modules.options.day_month_swapped

    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=5,
            child=[
                CategoryLabel("Extra Module Options"),
                SettingsRow(
                    title="Workspace Indicator Style",
                    description="Pick between 3 different Workspace Indicator styles.",
                    child=[
                        make_toggle_buttons(
                            [
                                ("Icons", "windows", "photo"),
                                ("Numbers", "numbers", "counter_1"),
                                ("Dots", "dots", "more_horiz"),
                            ],
                            lambda: user_settings.interface.modules.options.workspaces_style,
                            BarStyles.setWorkspacesStyle,
                            on_any_click=None,
                        )
                    ],
                ),
                SwitchRow(
                    title="Use 24 hour time",
                    description="Toggle between 12-hour (AM/PM) and 24-hour time formats.",
                    active=self.military_time,
                    on_change=lambda x, active: BarStyles.setMilitaryTime(active),
                ),
                SwitchRow(
                    title="Show the date",
                    description="Toggle the visibility of the date in the bar.",
                    active=self.show_date,
                    on_change=lambda x, active: BarStyles.setDateVisibility(active),
                ),
                SwitchRow(
                    title="Swap the day and month",
                    description="Use the American date format.",
                    active=self.day_month_swapped,
                    on_change=lambda x, active: BarStyles.setDayMonthSwapped(active),
                ),
                SettingsRow(
                    title="Recording Indicator",
                    description="When to show the recording indicator in the bar.",
                    child=[
                        make_toggle_buttons(
                            [
                                ("Always", "always", "visibility"),
                                ("When Recording", "recording", "screen_record"),
                            ],
                            lambda: user_settings.interface.modules.options.recording_indicator,
                            BarStyles.setRecordingIndicator,
                            on_any_click=None,
                        ),
                    ],
                ),
            ],
        )


class MiscCategory(widgets.Box):
    screen_corners = user_settings.interface.misc.screen_corners

    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=5,
            child=[
                CategoryLabel("Miscellaneous"),
                SwitchRow(
                    title="Rounded Shell Corners",
                    description="Add a curve outside the shell that warps around the screen.",
                    active=user_settings.interface.misc.shell_corners,
                    on_change=lambda x, active: BarStyles.setShellCorners(active),
                ),
                SettingsRow(
                    title="Rounded Screen Corners",
                    description="Round the corners of the screen.",
                    child=[
                        make_toggle_buttons(
                            [
                                ("Disabled", "disabled", "close"),
                                (
                                    "When not fullscreen",
                                    "not_fullscreen",
                                    "fullscreen_exit",
                                ),
                                ("Always", "always", "check"),
                            ],
                            lambda: user_settings.interface.misc.screen_corners,
                            BarStyles.setScreenCorners,
                            on_any_click=None,
                        ),
                    ],
                ),
            ],
        )


class InterfaceTab(widgets.Box):
    def __init__(self):
        super().__init__(
            vertical=True,
            spacing=20,
            css_classes=["settings-body"],
            hexpand=False,
            halign="center",
            width_request=800,
        )
        self.append(BarCategory())
        self.append(Bar2Category())
        self.append(BarModulesCategory())
        self.append(ExtraBarCategory())
        self.append(NotificationsCategory())
        self.append(MiscCategory())
        self.hexpand = True
        self.vexpand = True

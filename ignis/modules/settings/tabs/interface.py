from warnings import showwarning
from ignis import widgets
from modules.m3components import Button
from scripts import BarStyles, send_notification
from user_settings import user_settings
from ..widgets import (
    CategoryLabel,
    make_toggle_buttons,
    make_independent_toggle_buttons,
    SwitchRow,
    SettingsRow,
)
from ignis.app import IgnisApp

app = IgnisApp.get_initialized()


class BarCategory(widgets.Box):
    def __init__(self):
        bar = user_settings.interface.bar
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
        )

        self.append(CategoryLabel("Bar", "toolbar"))

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
                        lambda: bar.side,
                        BarStyles.setSide,
                        on_any_click=None,
                    )
                ],
            )
        )

        self.append(widgets.Separator())

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
                        lambda: bar.density,
                        BarStyles.setCompact,
                        on_any_click=None,
                    )
                ],
            )
        )

        self.append(widgets.Separator())

        self.append(
            SettingsRow(
                title="Extra Modifiers",
                description="Add extra modifiers to the bar (You can select multiple).",
                child=[
                    make_independent_toggle_buttons(
                        [
                            (
                                "Floating",
                                bar.get_floating,
                                BarStyles.setFloating,
                                "page_header",
                            ),
                            (
                                "Separated",
                                bar.get_separation,
                                BarStyles.setSeparation,
                                "more_horiz",
                            ),
                            (
                                "Centered",
                                bar.get_centered,
                                BarStyles.setBarCenter,
                                "code",
                            ),
                        ]
                    )
                ],
            )
        )

        self.append(widgets.Separator())

        self.append(
            SettingsRow(
                title="Backgrounds",
                description="Add or remove the backgrounds of the Bar/Modules.",
                child=[
                    make_independent_toggle_buttons(
                        [
                            (
                                "Bar",
                                bar.get_bar_background,
                                BarStyles.setBarBackground,
                                "toolbar",
                            ),
                            (
                                "Modules",
                                bar.get_module_backgrounds,
                                BarStyles.setModuleBackgrounds,
                                "more_horiz",
                            ),
                        ]
                    )
                ],
            )
        )


class Bar2Category(widgets.Box):
    def __init__(self):
        bar = user_settings.interface.bar2
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
        )

        self.append(CategoryLabel("Second Bar", "bottom_navigation"))

        self.append(
            SettingsRow(
                description="The second bar will be automatically enabled if any modules are located in it.\nIt will automatically be disabled if there are no modules located in it.\nNote: If any disabled modules are located in the second bar, it will still be enabled.",
            )
        )

        self.append(widgets.Separator())

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
                        lambda: bar.side,
                        BarStyles.setSide,
                        on_any_click=None,
                        bar_id=1,
                    )
                ],
            )
        )

        self.append(widgets.Separator())

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
                        lambda: bar.density,
                        BarStyles.setCompact,
                        on_any_click=None,
                        bar_id=1,
                    )
                ],
            )
        )

        self.append(widgets.Separator())

        self.append(
            SettingsRow(
                title="Extra Modifiers",
                description="Add extra modifiers to the bar (You can select multiple).",
                child=[
                    make_independent_toggle_buttons(
                        [
                            (
                                "Floating",
                                bar.get_floating,
                                BarStyles.setFloating,
                                "page_header",
                            ),
                            (
                                "Separated",
                                bar.get_separation,
                                BarStyles.setSeparation,
                                "more_horiz",
                            ),
                            (
                                "Centered",
                                bar.get_centered,
                                BarStyles.setBarCenter,
                                "code",
                            ),
                        ],
                        bar_id=1,
                    )
                ],
            )
        )

        self.append(widgets.Separator())

        self.append(
            SettingsRow(
                title="Backgrounds",
                description="Add or remove the backgrounds of the Bar/Modules.",
                child=[
                    make_independent_toggle_buttons(
                        [
                            (
                                "Bar",
                                bar.get_bar_background,
                                BarStyles.setBarBackground,
                                "toolbar",
                            ),
                            (
                                "Modules",
                                bar.get_module_backgrounds,
                                BarStyles.setModuleBackgrounds,
                                "more_horiz",
                            ),
                        ],
                        bar_id=1,
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
            spacing=0,
            child=[
                CategoryLabel("Bar Modules", "dashboard_2"),
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
            if module != list(modules.values())[-1]:
                self.append(widgets.Separator())


class ExtraBarCategory(widgets.Box):
    options = user_settings.interface.modules.options

    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
            child=[
                CategoryLabel("Extra Module Options", "settings"),
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
                            lambda: self.options.workspaces_style,
                            BarStyles.setWorkspacesStyle,
                            on_any_click=None,
                        )
                    ],
                ),
                widgets.Separator(),
                SwitchRow(
                    title="Fixed Workspaces",
                    description="Show a specific amount of workspaces",
                    active=self.options.fixed_workspaces_enabled,
                    on_change=lambda x,
                    active: self.options.set_fixed_workspaces_enabled(active),
                ),
                widgets.Separator(),
                SettingsRow(
                    title="Fixed Workspaces Amount",
                    description="How many workspaces to show.",
                    child=[
                        widgets.SpinButton(
                            min=1,
                            max=20,
                            step=1,
                            value=self.options.fixed_workspaces_amount,
                            on_change=lambda x,
                            value: self.options.set_fixed_workspaces_amount(int(value)),
                        )
                    ],
                ),
                widgets.Separator(),
                SwitchRow(
                    title="Use 24 hour time",
                    description="Toggle between 12-hour (AM/PM) and 24-hour time formats.",
                    active=self.options.military_time,
                    on_change=lambda x, active: BarStyles.setMilitaryTime(active),
                ),
                widgets.Separator(),
                SwitchRow(
                    title="Show the date",
                    description="Toggle the visibility of the date in the bar.",
                    active=self.options.show_date,
                    on_change=lambda x, active: BarStyles.setDateVisibility(active),
                ),
                widgets.Separator(),
                SwitchRow(
                    title="Swap the day and month",
                    description="Use the American date format.",
                    active=self.options.day_month_swapped,
                    on_change=lambda x, active: BarStyles.setDayMonthSwapped(active),
                ),
            ],
        )


class MiscCategory(widgets.Box):
    screen_corners = user_settings.interface.misc.screen_corners

    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
            child=[
                CategoryLabel("Miscellaneous", "more_horiz"),
                SwitchRow(
                    title="Rounded Shell Corners",
                    description="Add a curve outside the shell that warps around the screen.",
                    active=user_settings.interface.misc.shell_corners,
                    on_change=lambda x, active: BarStyles.setShellCorners(active),
                ),
                widgets.Separator(),
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
            spacing=8,
            css_classes=["settings-body"],
            hexpand=False,
            halign="center",
            width_request=800,
        )
        self.append(BarCategory())
        self.append(Bar2Category())
        self.append(BarModulesCategory())
        self.append(ExtraBarCategory())
        self.append(MiscCategory())
        self.hexpand = True
        self.vexpand = True

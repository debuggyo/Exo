import os

from ignis import widgets
from modules.m3components import Button
from scripts import Wallpaper, BarStyles, DockStyles, send_notification
from user_settings import user_settings
from ..widgets import CategoryLabel, make_toggle_buttons, SwitchRow, SettingsRow
from ignis.app import IgnisApp

app = IgnisApp.get_initialized()

class BarCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=2,
        )

        self.append(CategoryLabel("Bar"))

        self.append(SettingsRow(
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
                    on_any_click=None
                )
            ]
        ))

        self.append(SettingsRow(
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
                    on_any_click=None
                )
            ]
        ))

        self.append(SettingsRow(
            title="Workspace Indicator Style",
            description="Pick between 3 different Workspace Indicator styles.",
            child=[
                make_toggle_buttons(
                    [
                        ("Icons", "windows", "photo"),
                        ("Numbers", "numbers", "counter_1"),
                        ("Dots", "dots", "more_horiz"),
                    ],
                    lambda: user_settings.interface.bar.modules.workspaces_style,
                    BarStyles.setWorkspacesStyle,
                    on_any_click=None
                )
            ]
        ))

        self.append(SwitchRow(
                label="Floating Bar",
                description="Make the bar float away from the edges of the screen.",
                active=user_settings.interface.bar.floating,
                on_change=lambda x, active: BarStyles.setFloating(active)
            ))

        self.append(SwitchRow(
                label="Separated Islands",
                description="Seperate the bar into 3 separate 'islands'.",
                active=user_settings.interface.bar.separation,
                on_change=lambda x, active: BarStyles.setSeparation(active)
            ))

        self.append(SwitchRow(
                label="Extend to Edges",
                description="Make the bar span the full width of the screen.",
                active=(not user_settings.interface.bar.centered),
                on_change=lambda x, active: BarStyles.setBarCenter(not active)
            ))

        self._rounded_corners_row = SwitchRow(
                label="Rounded Bar Corners",
                description="Add a curve outside the bar that warps around the screen.",
                active=user_settings.interface.bar.corners,
                on_change=lambda x, active: BarStyles.setBarCorners(active)
            )

        self.append(self._rounded_corners_row)
        BarStyles.set_rounded_corners_row(self._rounded_corners_row)
        BarStyles._update_rounded_corners_visibility()

class DockCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=2,
        )

        self.append(CategoryLabel("Dock"))

        self._enable_switch = SwitchRow(
            label="Enable",
            description="Enable a Dock with your pinned apps. (experimental, scuffed)",
            active=user_settings.interface.dock.enabled,
            on_change=lambda x, active: self._on_enable_change(active)
        )
        self.append(self._enable_switch)

        self._settings_box = widgets.Box(
            css_classes=["dock-settings-container"],
            vertical=True,
            spacing=2,
        )

        self._settings_box.append(SettingsRow(
            title="Position",
            description="Pick a side for the dock to be located.",
            child=[
                make_toggle_buttons(
                    [
                        ("Top", "top", "align_vertical_top"),
                        ("Bottom", "bottom", "align_vertical_bottom"),
                        ("Left", "left", "align_horizontal_left"),
                        ("Right", "right", "align_horizontal_right"),
                    ],
                    lambda: user_settings.interface.dock.side,
                    DockStyles.setSide,
                    on_any_click=None
                )
            ]
        ))

        self._settings_box.append(SettingsRow(
            title="Size",
            description="Set a size for your dock icons.",
            child=[
                widgets.Scale(
                    vertical=False,
                    min=16,
                    max=128,
                    step=1,
                    value=user_settings.interface.dock.size,
                    on_change=lambda x: DockStyles.setSize(x.value),
                    draw_value=True
                )
            ]
        ))

        self._settings_box.append(SwitchRow(
                label="Floating Dock",
                description="Make the dock float away from the edges of the screen.",
                active=user_settings.interface.dock.floating,
                on_change=lambda x, active: DockStyles.setFloating(active)
            ))

        self._settings_box.append(SwitchRow(
                label="Extend to Edges",
                description="Make the dock span the full width of the screen.",
                active=(not user_settings.interface.dock.centered),
                on_change=lambda x, active: DockStyles.setCentered(not active)
            ))

        self.append(self._settings_box)
        self._settings_box.set_visible(user_settings.interface.dock.enabled)

    def _on_enable_change(self, active):
        DockStyles.setEnabled(active)
        self._settings_box.set_visible(active)

class NotificationsCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=2,
        )

        self.append(CategoryLabel("Notifications"))

        self.append(SettingsRow(
            title="Popup Location",
            description="Pick a location for your notification popups.",
            child=[
                make_toggle_buttons(
                    [
                        ("Top Left", ["top", "left"], "north_west"),
                        ("Top Right", ["top", "right"], "north_east"),
                        ("Bottom Left", ["bottom", "left"], "south_west"),
                        ("Bottom Right", ["bottom", "right"], "south_east"),
                    ],
                    lambda: user_settings.interface.notifications.anchor,
                    user_settings.interface.notifications.set_anchor,
                    on_any_click=None
                ),
            ]
        ))

        self.append(SettingsRow(
            title="Send a Test Notification",
            child=[Button.button(
                icon="notifications_unread",
                label="Test Notification",
                halign="start",
                on_click=lambda x: send_notification("Test Notification", "This is a test notification!"),
            )]
        ))

class MiscCategory(widgets.Box):
    screen_corners = user_settings.interface.misc.screen_corners
    media_widget = user_settings.interface.bar.modules.media_widget
    military_time = user_settings.interface.bar.modules.military_time

    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=2,
            child=[
                CategoryLabel("Miscellaneous"),
                SwitchRow(
                    label="Rounded Screen Corners",
                    description="Add rounded corners to the screen.",
                    active=self.screen_corners,
                    on_change=lambda x, active: BarStyles.setScreenCorners(active)
                ),
                SwitchRow(
                    label="Media Widget",
                    description="Adds a media widget to the bar.",
                    active=self.media_widget,
                    on_change=lambda x, active: BarStyles.setMediaWidget(active)
                ),
                SettingsRow(
                    title="Recording Indicator",
                    description="Show a recording indicator in the bar when recording with Exo.",
                    child=[
                        make_toggle_buttons(
                            [
                                ("Always", "always", "visibility"),
                                ("When Recording", "recording", "screen_record"),
                                ("Never", "never", "visibility_off"),
                            ],
                            lambda: user_settings.interface.bar.modules.recording_indicator,
                            BarStyles.setRecordingIndicator,
                            on_any_click=None
                        ),
                    ]
                ),
                SwitchRow(
                    label="Use 24 hour time.",
                    description="Toggle between 12-hour (AM/PM) and 24-hour time formats.",
                    active=self.military_time,
                    on_change=lambda x, active: BarStyles.setMilitaryTime(active)
                ),
            ]
        )


class InterfaceTab(widgets.Box):
    def __init__(self):
        super().__init__(vertical=True, spacing=20, css_classes=["settings-body"], hexpand=False, halign="center", width_request=800)
        self.append(BarCategory())
        self.append(DockCategory())
        self.append(NotificationsCategory())
        self.append(MiscCategory())
        self.hexpand = True
        self.vexpand = True

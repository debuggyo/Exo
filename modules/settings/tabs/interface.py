import os

from ignis import widgets
from modules.m3components import Button
from scripts import Wallpaper, BarStyles
from user_settings import user_settings
from ..widgets import CategoryLabel, make_toggle_buttons, SwitchRow, SettingsRow
from ignis.app import IgnisApp

app = IgnisApp.get_initialized()

class BarStylesCategory(widgets.Box):
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

        # Bar compactness
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

        self.append(SwitchRow(
                label="Rounded Bar Corners",
                description="Add a curve outside the bar that warps around the screen.",
                active=user_settings.interface.bar.corners,
                on_change=lambda x, active: BarStyles.setBarCorners(active)
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
                SwitchRow(
                    label="Military Time",
                    description="Toggle between 12-hour (AM/PM) and 24-hour time formats.",
                    active=self.military_time,
                    on_change=lambda x, active: BarStyles.setMilitaryTime(active)
                ),
            ]
        )


class InterfaceTab(widgets.Box):

    def __init__(self):
        super().__init__(vertical=True, spacing=20, css_classes=["settings-body"], hexpand=False, halign="center", width_request=800)
        self.append(BarStylesCategory())
        self.append(MiscCategory())
        self.hexpand = True
        self.vexpand = True
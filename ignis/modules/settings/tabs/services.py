from ignis import widgets
from modules.m3components.button import Button
from user_settings import user_settings
from ..widgets import (
    CategoryLabel,
    SettingsRow,
    SwitchRow,
    make_toggle_buttons,
    make_independent_toggle_buttons,
)
from scripts import BarStyles, send_notification
from ignis.options import options


class NotificationsCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
            child=[
                CategoryLabel("Notifications", "notifications"),
                SwitchRow(
                    title="Do Not Disturb",
                    description="When enabled, will stop popups for new notifications.",
                    active=options.notifications.dnd,
                    on_change=lambda x, active: options.notifications.set_dnd(active),
                ),
                widgets.Separator(),
                SettingsRow(
                    title="Popup Timeout",
                    description="How long (in seconds) should a notification popup stay on screen.",
                    child=[
                        widgets.SpinButton(
                            min=1,
                            max=60,
                            step=1,
                            value=(options.notifications.popup_timeout / 1000),
                            on_change=lambda _,
                            value: options.notifications.set_popup_timeout(
                                value * 1000
                            ),
                        )
                    ],
                ),
                widgets.Separator(),
                SettingsRow(
                    title="Max Popups",
                    description="How many popup notifications can be shown at once.",
                    child=[
                        widgets.SpinButton(
                            min=1,
                            max=20,
                            step=1,
                            value=options.notifications.max_popups_count,
                            on_change=lambda _,
                            value: options.notifications.set_max_popups_count(value),
                        )
                    ],
                ),
                widgets.Separator(),
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
                ),
                widgets.Separator(),
                SwitchRow(
                    title="Compact Pop-up",
                    description="Show a more compact pop-up for incoming notifications.",
                    active=user_settings.interface.notifications.compact_popup,
                    on_change=lambda x,
                    active: user_settings.interface.notifications.set_compact_popup(
                        active
                    ),
                ),
                widgets.Separator(),
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
                ),
            ],
        )


class RecordingCategory(widgets.Box):
    def __init__(self):
        self.recorder = user_settings.services.recorder

        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
            child=[
                CategoryLabel("Recording", "screen_record"),
                SettingsRow(
                    title="Notifications",
                    description="When should the recorder send a notification.",
                    child=[
                        make_independent_toggle_buttons(
                            [
                                (
                                    "Started",
                                    self.recorder.get_start_notification,
                                    self.recorder.set_start_notification,
                                    "play_arrow",
                                ),
                                (
                                    "Stopped",
                                    self.recorder.get_stop_notification,
                                    self.recorder.set_stop_notification,
                                    "stop",
                                ),
                            ]
                        )
                    ],
                ),
                widgets.Separator(),
                SwitchRow(
                    title="Record Audio",
                    description="Record the systems audio when recording.",
                    active=self.recorder.record_audio,
                    on_change=lambda x, active: self.recorder.set_record_audio(active),
                ),
                widgets.Separator(),
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


class OSDCategory(widgets.Box):
    def __init__(self):
        self.recorder = user_settings.services.recorder

        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=0,
            child=[
                CategoryLabel("OSD", "toast"),
                SettingsRow(
                    title="Popup Location",
                    description="Pick a location for your OSD popups.",
                    child=[
                        make_toggle_buttons(
                            [
                                ("", ["top", "left"], "north_west"),
                                ("Top", ["top"], "north"),
                                ("", ["top", "right"], "north_east"),
                                ("", ["left"], "west"),
                                ("", ["right"], "east"),
                                ("", ["bottom", "left"], "south_west"),
                                ("Bottom", ["bottom"], "south"),
                                ("", ["bottom", "right"], "south_east"),
                            ],
                            lambda: user_settings.services.osd.anchor,
                            user_settings.services.osd.set_anchor,
                            on_any_click=None,
                        ),
                    ],
                ),
                widgets.Separator(),
                SwitchRow(
                    title="Vertical",
                    description="Use a vertical OSD. Only takes effect when located in corners.",
                    active=user_settings.services.osd.vertical,
                    on_change=lambda x, active: user_settings.services.osd.set_vertical(
                        active
                    ),
                ),
            ],
        )


class ServicesTab(widgets.Box):
    def __init__(self):
        super().__init__(
            vertical=True,
            spacing=8,
            css_classes=["settings-body"],
            hexpand=False,
            halign="center",
            width_request=800,
        )
        self.append(NotificationsCategory())
        self.append(RecordingCategory())
        self.append(OSDCategory())

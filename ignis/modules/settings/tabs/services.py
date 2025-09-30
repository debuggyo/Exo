from ignis import widgets
from modules.m3components.button import Button
from user_settings import user_settings
from ..widgets import CategoryLabel, SettingsRow, SwitchRow, make_toggle_buttons
from scripts import send_notification
from ignis.options import options


class NotificationsCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=5,
            child=[
                CategoryLabel("Notifications", "notifications"),
                SwitchRow(
                    title="Do Not Disturb",
                    description="When enabled, will stop popups for new notifications.",
                    active=options.notifications.dnd,
                    on_change=lambda x, active: options.notifications.set_dnd(active),
                ),
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
            spacing=5,
            child=[
                CategoryLabel("Recording", "screen_record"),
                SwitchRow(
                    title="Recording Started Notification",
                    description="Send a notification when recording starts.",
                    active=self.recorder.start_notification,
                    on_change=lambda x, active: self.recorder.set_start_notification(
                        active
                    ),
                ),
                SwitchRow(
                    title="Recording Stopped Notification",
                    description="Send a notification when recording stops.",
                    active=self.recorder.start_notification,
                    on_change=lambda x, active: self.recorder.set_stop_notification(
                        active
                    ),
                ),
                SwitchRow(
                    title="Record Audio",
                    description="Record the systems audio when recording.",
                    active=self.recorder.record_audio,
                    on_change=lambda x, active: self.recorder.set_record_audio(active),
                ),
            ],
        )


class ServicesTab(widgets.Box):
    def __init__(self):
        super().__init__(
            vertical=True,
            spacing=20,
            css_classes=["settings-body"],
            hexpand=False,
            halign="center",
            width_request=800,
        )
        self.append(NotificationsCategory())
        self.append(RecordingCategory())

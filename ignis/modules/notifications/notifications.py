import time
from ignis import widgets, utils
from ignis.services.notifications import Notification
from modules.m3components import Button


def relative_time(timestamp: float) -> str:
    diff = int(time.time() - timestamp)

    if diff < 60:
        return "now"
    elif diff < 3600:
        return f"{diff // 60}m"
    elif diff < 86400:
        return f"{diff // 3600}h"
    else:
        return f"{diff // 86400}d"


class ExoNotification(widgets.Box):
    def __init__(self, notification: Notification) -> None:
        self._timestamp = notification.time

        self._age_label = widgets.Label(
            css_classes=["notification-age"],
            label="",
            halign="start",
            ellipsize="end"
        )

        super().__init__(
            vertical=True,
            hexpand=True,
            halign="fill",
            css_classes=["notification"],
            child=[
                widgets.Box(
                    spacing=10,
                    child=[
                        widgets.Icon(
                            image=notification.icon or "dialog-information-symbolic",
                            pixel_size=24,
                            halign="start",
                            valign="start",
                            css_classes=["notification-icon"],
                        ),
                        widgets.Box(
                            css_classes=["notification-info"],
                            vertical=True,
                            valign="center",
                            hexpand=True,
                            halign="fill",
                            spacing=2,
                            child=[
                                widgets.Box(
                                    spacing=5,
                                    child=[
                                        widgets.Label(
                                            css_classes=["notification-summary"],
                                            label=notification.summary,
                                            halign="start",
                                            ellipsize="end"
                                        ),
                                        widgets.Label(
                                            css_classes=["notification-separator"],
                                            label="•",
                                            halign="start",
                                        ),
                                        self._age_label,
                                    ]
                                ),
                                widgets.Label(
                                    css_classes=["notification-body"],
                                    label=notification.body,
                                    halign="start",
                                    ellipsize="end"
                                ) if notification.body else None,
                                widgets.Box(
                                    css_classes=["notification-actions-container"],
                                    child=[
                                        Button.button(
                                            label=action.label,
                                            on_click=lambda x, action=action: action.invoke(),
                                            css_classes=["notification-action"],
                                            size="xs",
                                            type="text"
                                        ) for action in notification.actions
                                    ]
                                ) if notification.actions else None
                            ]
                        ),
                        Button.button(
                            css_classes=["notification-close"],
                            icon="close",
                            valign="start",
                            vexpand=False,
                            size="xs",
                            on_click=lambda x: notification.close(),
                        )
                    ],
                ),
            ],
        )

        self._update_age_label()

        self._poll = utils.Poll(timeout=60_000, callback=self._on_poll)

    def _on_poll(self, poll: utils.Poll | None = None):
        """Update the label on each poll tick."""
        self._update_age_label()

        if time.time() - self._timestamp >= 86400 and poll is not None:
            poll.cancel()

    def _update_age_label(self):
        self._age_label.set_label(relative_time(self._timestamp))

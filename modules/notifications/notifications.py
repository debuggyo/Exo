from ignis import widgets
from ignis.services.notifications import Notification
from ignis import utils
from modules.m3components import Button

class ExoNotification(widgets.Box):
    def __init__(self, notification: Notification) -> None:
        super().__init__(
            vertical=True,
            hexpand=True,
            css_classes=["notification"],
            child=[
                widgets.Box(
                    child=[
                        widgets.Icon(
                            image=notification.icon
                            if notification.icon
                            else "dialog-information-symbolic",
                            pixel_size=24,
                            halign="start",
                            valign="start",
                            css_classes=["notification-icon"],
                        ),
                        widgets.Box(
                            vertical=True,
                            style="margin-left: 0.75rem; margin-right: 0.75rem;",
                            halign="fill",
                            valign="center",
                            hexpand=True,
                            child=[
                                widgets.Label(
                                    ellipsize="end",
                                    label=notification.summary,
                                    halign="start",
                                    visible=notification.summary != "",
                                    css_classes=["notification-summary"],
                                ),
                                widgets.Label(
                                    label=notification.body,
                                    ellipsize="end",
                                    halign="start",
                                    css_classes=["notification-body"],
                                    visible=notification.body != "",
                                ),
                            ],
                        ),
                        Button.button(
                            icon="close",
                            halign="end",
                            hexpand=True,
                            css_classes=["notification-close"],
                            type="tonal",
                            on_click=lambda x: notification.close(),
                        ),
                    ],
                ),
                widgets.Box(
                    child=[
                        Button.button(
                            label=action.label,
                            on_click=lambda x, action=action: action.invoke(),
                            css_classes=["notification-action"],
                            type="outlined",
                            halign="fill",
                            size="xs",
                        )
                        for action in notification.actions
                    ],
                    homogeneous=True,
                    style="margin-top: 0.75rem;" if notification.actions else "",
                    spacing=2,
                ),
            ],
        )

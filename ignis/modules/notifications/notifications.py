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
    def __init__(self, notification: Notification, compact_popup: bool = False) -> None:
        self._timestamp = notification.time
        self._is_expanded = False

        self._age_label = widgets.Label(
            css_classes=["notification-age"],
            label="",
            halign="start",
            ellipsize="end",
            visible=(not compact_popup),
        )

        self._body_label = (
            widgets.Label(
                css_classes=["notification-body"],
                label=notification.body,
                halign="start",
                ellipsize="end",
                wrap_mode="word_char",
            )
            if notification.body
            else None
        )
        if compact_popup:
            self._body_label.set_single_line_mode(True)

        self._expand_button = (
            Button.button(
                css_classes=["notification-expand"],
                icon="arrow_drop_down",
                valign="start",
                vexpand=False,
                size="xs",
                on_click=self._toggle_expand,
            )
            if self._body_label and not compact_popup
            else None
        )

        super().__init__(
            vertical=True,
            hexpand=True,
            halign="fill",
            css_classes=["notification", "compact-popup" if compact_popup else None],
            child=[
                widgets.Box(
                    spacing=10,
                    child=[
                        widgets.Icon(
                            image=notification.icon or "dialog-information-symbolic",
                            pixel_size=24 if not compact_popup else 16,
                            halign="start",
                            valign="start",
                            css_classes=["notification-icon"],
                        ),
                        widgets.Box(
                            css_classes=["notification-info"],
                            vertical=True if not compact_popup else False,
                            valign="center",
                            hexpand=True,
                            halign="fill",
                            spacing=2 if not compact_popup else 8,
                            child=[
                                widgets.Box(
                                    spacing=5,
                                    child=[
                                        widgets.Label(
                                            css_classes=["notification-summary"],
                                            label=notification.summary,
                                            halign="start",
                                            ellipsize="end",
                                        ),
                                        widgets.Label(
                                            css_classes=["notification-separator"],
                                            label="•",
                                            halign="start",
                                            visible=(not compact_popup),
                                        ),
                                        self._age_label,
                                    ],
                                ),
                                self._body_label,
                                widgets.Box(
                                    css_classes=["notification-actions-container"],
                                    child=[
                                        Button.button(
                                            label=action.label,
                                            on_click=lambda x,
                                            action=action: action.invoke(),
                                            css_classes=["notification-action"],
                                            size="xs",
                                            type="text",
                                        )
                                        for action in notification.actions
                                    ],
                                )
                                if notification.actions and not compact_popup
                                else None,
                            ],
                        ),
                        widgets.Box(
                            vertical=True,
                            spacing=5,
                            child=[
                                Button.button(
                                    css_classes=["notification-close"],
                                    icon="close",
                                    valign="start" if not compact_popup else "center",
                                    vexpand=compact_popup,
                                    size="xs",
                                    on_click=lambda x: notification.close(),
                                ),
                                self._expand_button if not compact_popup else None,
                            ],
                        ),
                    ],
                ),
            ],
        )

        self._update_age_label()

        self._poll = utils.Poll(timeout=60_000, callback=self._on_poll)

    def _toggle_expand(self, _):
        self._is_expanded = not self._is_expanded
        if self._body_label:
            self._body_label.set_ellipsize("none" if self._is_expanded else "end")
            self._body_label.set_wrap(self._is_expanded)

        if self._expand_button:
            self._expand_button.set_icon(
                "arrow_drop_up" if self._is_expanded else "arrow_drop_down"
            )

    def _on_poll(self, poll: utils.Poll | None = None):
        """Update the label on each poll tick."""
        self._update_age_label()

        if time.time() - self._timestamp >= 86400 and poll is not None:
            poll.cancel()

    def _update_age_label(self):
        self._age_label.set_label(relative_time(self._timestamp))

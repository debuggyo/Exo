from ignis import widgets
from ignis import utils
from ignis.services.notifications import Notification, NotificationService
from .notifications import ExoNotification
from user_settings import user_settings

notifications = NotificationService.get_default()

class Popup(widgets.Box):
    def __init__(
        self, box: "PopupBox", window: "NotificationPopup", notification: Notification
    ):
        self._box = box
        self._window = window

        if user_settings.interface.bar.side == "bottom":
            transition_type = "slide_up"
        else:
            transition_type = "slide_down"

        widget = ExoNotification(notification)
        widget.css_classes = ["notification-popup"]
        self._inner = widgets.Revealer(transition_type="crossfade", child=widget, hexpand=True, halign="fill")
        self._outer = widgets.Revealer(transition_type=transition_type, child=self._inner, hexpand=True, halign="fill")
        super().__init__(child=[self._outer], halign="fill", valign="fill", hexpand=True)

        notification.connect("dismissed", lambda x: self.destroy())

    def destroy(self):
        def box_destroy():
            self.unparent()
            if len(notifications.popups) == 0:
                self._window.visible = False

        def outer_close():
            self._outer.reveal_child = False
            utils.Timeout(self._outer.transition_duration, box_destroy)

        self._inner.transition_type = "crossfade"
        self._inner.reveal_child = False
        utils.Timeout(self._outer.transition_duration, outer_close)


class PopupBox(widgets.Box):
    def __init__(self, window: "NotificationPopup", monitor: int):
        self._window = window
        self._monitor = monitor

        super().__init__(
            vertical=True,
            valign="start",
            spacing=3,
            setup=lambda self: notifications.connect(
                "new_popup",
                lambda x, notification: self.__on_notified(notification),
            ),
        )

    def __on_notified(self, notification: Notification) -> None:
        self._window._update_window_properties()
        
        self._window.visible = True
        popup = Popup(box=self, window=self._window, notification=notification)
        if user_settings.interface.bar.side == "top":
            self.prepend(popup)
        else:
            self.append(popup)
        popup._outer.reveal_child = True
        utils.Timeout(
            popup._outer.transition_duration, popup._inner.set_reveal_child, True
        )


class NotificationPopup(widgets.Window):
    def __init__(self, monitor: int):
        super().__init__(
            anchor=user_settings.interface.notifications.anchor,
            monitor=monitor,
            namespace=f"notification",
            layer="top",
            child=PopupBox(window=self, monitor=monitor),
            visible=False,
            dynamic_input_region=True,
            css_classes=["notification-popup-container"],
            style="min-width: 29rem;",
        )
        self._update_window_properties()
    
    def _update_window_properties(self):
        self.set_anchor(None)
        self.set_anchor(user_settings.interface.notifications.anchor)
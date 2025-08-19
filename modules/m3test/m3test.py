from ignis import widgets, utils
from modules.m3components import Button
# from modules import ExoNotification
from ignis.services.notifications import Notification, NotificationService
from gi.repository import GLib
notifications = NotificationService.get_default()

class Popup(widgets.Revealer):
    def __init__(self, notification: Notification, **kwargs):
        widget = ExoNotification(notification)
        super().__init__(child=widget, transition_type="slide_down", **kwargs)

        notification.connect("closed", lambda x: self.destroy())

    def destroy(self):
        self.reveal_child = False
        utils.Timeout(self.transition_duration, self.unparent)

class NotificationList(widgets.Box):
    __gtype_name__ = "NotificationList"

    def __init__(self):
        loading_notifications_label = widgets.Label(
            label="Loading notifications...",
            valign="center",
            vexpand=True,
            css_classes=["notification-center-info-label"],
        )

        super().__init__(
            vertical=True,
            child=[loading_notifications_label],
            vexpand=True,
            css_classes=["rec-unset"],
            spacing=2,
            setup=lambda self: notifications.connect(
                "notified",
                lambda x, notification: self.__on_notified(notification),
            ),
        )

        utils.ThreadTask(
            self.__load_notifications,
            lambda result: self.set_child(result),
        ).run()

    def __on_notified(self, notification: Notification) -> None:
        notify = Popup(notification)
        self.prepend(notify)
        notify.reveal_child = True

    def __load_notifications(self) -> list[widgets.Label | Popup]:
        contents: list[widgets.Label | Popup] = []
        for i in notifications.notifications:
            GLib.idle_add(lambda i=i: contents.append(Popup(i, reveal_child=True)))

        contents.append(
            widgets.Label(
                label="No notifications",
                valign="center",
                vexpand=True,
                visible=notifications.bind(
                    "notifications", lambda value: len(value) == 0
                ),
                css_classes=["notification-center-info-label"],
            )
        )
        return contents

class M3Test(widgets.RegularWindow):
    def __init__(self) -> None:
        super().__init__(
            css_classes=["settings-window"],
            hide_on_close=True,
            visible=False,
            title="Material 3 Testing Window",
            namespace="M3Test",
            child=widgets.Scroll(
                child=widgets.Box(
                    style="padding: 20px;",
                    vertical=True,
                    spacing=10,
                    halign="center",
                    child=[
                        # Label Only
                        widgets.Label(label="Label Only", css_classes=["settings-category-label"]),
                        Button.button(label="Elevated", type="elevated"),
                        Button.button(label="Filled", type="filled"),
                        Button.button(label="Tonal", type="tonal"),
                        Button.button(label="Outlined", type="outlined"),
                        Button.button(label="Text", type="text"),

                        # Icon + Label
                        widgets.Label(label="Icon + Label", css_classes=["settings-category-label"]),
                        Button.button(icon="edit", label="Elevated", type="elevated"),
                        Button.button(icon="edit", label="Filled", type="filled"),
                        Button.button(icon="edit", label="Tonal", type="tonal"),
                        Button.button(icon="edit", label="Outlined", type="outlined"),
                        Button.button(icon="edit", label="Text", type="text"),

                        # Icon Only
                        widgets.Label(label="Icon Only", css_classes=["settings-category-label"]),
                        Button.button(icon="edit", type="elevated"),
                        Button.button(icon="edit", type="filled"),
                        Button.button(icon="edit", type="tonal"),
                        Button.button(icon="edit", type="outlined"),
                        Button.button(icon="edit", type="text"),

                        # Extra Small
                        widgets.Label(label="Extra Small", css_classes=["settings-category-label"]),
                        Button.button(icon="edit", label="Elevated", type="elevated", size="xs"),
                        Button.button(icon="edit", label="Filled", type="filled", size="xs"),
                        Button.button(icon="edit", label="Tonal", type="tonal", size="xs"),
                        Button.button(icon="edit", label="Outlined", type="outlined", size="xs"),
                        Button.button(icon="edit", label="Text", type="text", size="xs"),

                        # Small
                        widgets.Label(label="Small", css_classes=["settings-category-label"]),
                        Button.button(icon="edit", label="Elevated", type="elevated"),
                        Button.button(icon="edit", label="Filled", type="filled"),
                        Button.button(icon="edit", label="Tonal", type="tonal"),
                        Button.button(icon="edit", label="Outlined", type="outlined"),
                        Button.button(icon="edit", label="Text", type="text"),

                        # Medium
                        widgets.Label(label="Medium", css_classes=["settings-category-label"]),
                        Button.button(icon="edit", label="Elevated", type="elevated", size="m"),
                        Button.button(icon="edit", label="Filled", type="filled", size="m"),
                        Button.button(icon="edit", label="Tonal", type="tonal", size="m"),
                        Button.button(icon="edit", label="Outlined", type="outlined", size="m"),
                        Button.button(icon="edit", label="Text", type="text", size="m"),

                        # Large
                        widgets.Label(label="Large", css_classes=["settings-category-label"]),
                        Button.button(icon="edit", label="Elevated", type="elevated", size="l"),
                        Button.button(icon="edit", label="Filled", type="filled", size="l"),
                        Button.button(icon="edit", label="Tonal", type="tonal", size="l"),
                        Button.button(icon="edit", label="Outlined", type="outlined", size="l"),
                        Button.button(icon="edit", label="Text", type="text", size="l"),

                        # Extra Large
                        widgets.Label(label="Extra Large", css_classes=["settings-category-label"]),
                        Button.button(icon="edit", label="Elevated", type="elevated", size="xl"),
                        Button.button(icon="edit", label="Filled", type="filled", size="xl"),
                        Button.button(icon="edit", label="Tonal", type="tonal", size="xl"),
                        Button.button(icon="edit", label="Outlined", type="outlined", size="xl"),
                        Button.button(icon="edit", label="Text", type="text", size="xl"),

                        # Connected Button Groups
                        widgets.Label(label="Connected Button Groups", css_classes=["settings-category-label"]),
                        Button.connected_group(
                            child=[
                                Button.button(icon="counter_1", label="First", shape="square"),
                                Button.button(icon="counter_2", label="Second", shape="square"),
                                Button.button(icon="counter_3", label="Third", shape="square"),
                                Button.button(icon="counter_4", label="Fourth", shape="square"),
                                Button.button(icon="counter_5", label="Fifth", shape="square"),
                                Button.button(icon="counter_6", label="Sixth", shape="square"),
                            ]
                        ),

                        # Switches
                        widgets.Label(label="Switches", css_classes=["settings-category-label"]),
                        widgets.Switch(halign="center"),
                        widgets.Switch(active=True, halign="center"),

                        # Checkboxes
                        widgets.Label(label="Checkboxes", css_classes=["settings-category-label"]),
                        widgets.CheckButton(label="Checkbox 1", halign="center"),
                        widgets.CheckButton(label="Checkbox 2", active=True, halign="center"),

                        # Radio Buttons
                        widgets.Label(label="Radio Buttons", css_classes=["settings-category-label"]),
                        widgets.CheckButton(group=widgets.CheckButton(label='Radio Button 2'), label="Radio Button 1", halign="center"),
                        widgets.CheckButton(group=widgets.CheckButton(label='Radio Button 3'), label="Radio Button 2", halign="center"),
                        widgets.CheckButton(group=widgets.CheckButton(label='Radio Button 4'), label="Radio Button 3", halign="center"),
                        widgets.CheckButton(group=widgets.CheckButton(label='radiobutton'), label="Radio Button 4", halign="center"),


                        # Notifications
                        # widgets.Box(
                        #     vertical=True,
                        #     vexpand=True,
                        #     css_classes=["notification-center"],
                        #     child=[
                        #         widgets.Box(
                        #             css_classes=["notification-center-header", "rec-unset"],
                        #             child=[
                        #                 widgets.Label(
                        #                     label=notifications.bind(
                        #                         "notifications", lambda value: str(len(value))
                        #                     ),
                        #                     css_classes=["notification-count"],
                        #                 ),
                        #                 widgets.Label(
                        #                     label="notifications",
                        #                     css_classes=["notification-header-label"],
                        #                 ),
                        #                 widgets.Button(
                        #                     child=widgets.Label(label="Clear all"),
                        #                     halign="end",
                        #                     hexpand=True,
                        #                     on_click=lambda x: notifications.clear_all(),
                        #                     css_classes=["notification-clear-all"],
                        #                 ),
                        #             ],
                        #         ),
                        #         widgets.Scroll(
                        #             height_request=600,
                        #             child=NotificationList(),
                        #             vexpand=True,
                        #         ),
                        #     ],
                        # )
                    ]
                )
            )
        )

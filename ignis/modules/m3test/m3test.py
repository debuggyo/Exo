from ignis import widgets, utils
from modules.m3components import Button, ConnectedButtonGroup, Icon
from ignis.services.notifications import Notification, NotificationService
from gi.repository import GLib
import modules.newbar.modules.settings as Settings

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
        self.test_variable = False
        self.test_variable_2 = True
        self.test_single_select = "two"
        self.test_multi_select_1 = False
        self.test_multi_select_2 = True
        self.test_multi_select_3 = False

        switch_row_1 = Settings.SwitchRow(
            title="Test Variable 1",
            description="This controls the first variable.",
        )
        switch_row_1.bind_option(self, "test_variable")

        switch_row_2 = Settings.SwitchRow(
            title="Test Variable 2",
            description="This controls the second variable.",
        )
        switch_row_2.bind_option(self, "test_variable_2")

        single_select_row = Settings.SingleSelectRow(
            title="Single Select",
            description="Choose one option.",
            items=[
                ("One", "one"),
                ("Two", "two"),
                ("Three", "three"),
            ],
        )
        single_select_row.bind_option(self, "test_single_select")

        multi_select_row = Settings.MultiSelectRow(
            title="Multi Select",
            description="Choose multiple options.",
            items=[
                ("Option 1", lambda: self.test_multi_select_1, lambda v: setattr(self, "test_multi_select_1", v)),
                ("Option 2", lambda: self.test_multi_select_2, lambda v: setattr(self, "test_multi_select_2", v)),
                ("Option 3", lambda: self.test_multi_select_3, lambda v: setattr(self, "test_multi_select_3", v)),
            ],
        )

        super().__init__(
            css_classes=["m3-testing-window"],
            hide_on_close=True,
            title="Material 3 Testing Window",
            namespace="M3Test",
            visible=False,
            child=widgets.Scroll(
                child=widgets.Box(
                    style="padding: 20px;",
                    vertical=True,
                    spacing=10,
                    halign="center",
                    child=[
                        switch_row_1,
                        switch_row_2,
                        single_select_row,
                        multi_select_row,
                        Settings.Row(
                            title="Hello There!",
                            description="AAAAAAAAAAAA",
                            child=Button(icon="edit", label="Hello")
                        ),

                        Icon("edit", 64, hexpand=False, halign="center"),
                        Icon("edit", 48, hexpand=False, halign="center"),
                        Icon("edit", 32, hexpand=False, halign="center"),
                        Icon("edit", 16, hexpand=False, halign="center"),
                        Icon("edit", 8, hexpand=False, halign="center"),

                        # Label Only
                        widgets.Label(
                            label="Label Only", css_classes=["settings-category-label"]
                        ),
                        Button(label="Elevated", type="elevated"),
                        Button(label="Filled", type="filled"),
                        Button(label="Tonal", type="tonal"),
                        Button(label="Outlined", type="outlined"),
                        Button(label="Text", type="text"),
                        # Icon + Label
                        widgets.Label(
                            label="Icon + Label",
                            css_classes=["settings-category-label"],
                        ),
                        Button(icon="edit", label="Elevated", type="elevated"),
                        Button(icon="edit", label="Filled", type="filled"),
                        Button(icon="edit", label="Tonal", type="tonal"),
                        Button(icon="edit", label="Outlined", type="outlined"),
                        Button(icon="edit", label="Text", type="text"),
                        # Icon Only
                        widgets.Label(
                            label="Icon Only", css_classes=["settings-category-label"]
                        ),
                        Button(icon="edit", type="elevated"),
                        Button(icon="edit", type="filled"),
                        Button(icon="edit", type="tonal"),
                        Button(icon="edit", type="outlined"),
                        Button(icon="edit", type="text"),
                        # Extra Small
                        widgets.Label(
                            label="Extra Small", css_classes=["settings-category-label"]
                        ),
                        Button(
                            icon="edit", label="Elevated", type="elevated", size="xs"
                        ),
                        Button(
                            icon="edit", label="Filled", type="filled", size="xs"
                        ),
                        Button(
                            icon="edit", label="Tonal", type="tonal", size="xs"
                        ),
                        Button(
                            icon="edit", label="Outlined", type="outlined", size="xs"
                        ),
                        Button(
                            icon="edit", label="Text", type="text", size="xs"
                        ),
                        # Small
                        widgets.Label(
                            label="Small", css_classes=["settings-category-label"]
                        ),
                        Button(icon="edit", label="Elevated", type="elevated"),
                        Button(icon="edit", label="Filled", type="filled"),
                        Button(icon="edit", label="Tonal", type="tonal"),
                        Button(icon="edit", label="Outlined", type="outlined"),
                        Button(icon="edit", label="Text", type="text"),
                        # Medium
                        widgets.Label(
                            label="Medium", css_classes=["settings-category-label"]
                        ),
                        Button(
                            icon="edit", label="Elevated", type="elevated", size="m"
                        ),
                        Button(
                            icon="edit", label="Filled", type="filled", size="m"
                        ),
                        Button(
                            icon="edit", label="Tonal", type="tonal", size="m"
                        ),
                        Button(
                            icon="edit", label="Outlined", type="outlined", size="m"
                        ),
                        Button(icon="edit", label="Text", type="text", size="m"),
                        # Large
                        widgets.Label(
                            label="Large", css_classes=["settings-category-label"]
                        ),
                        Button(
                            icon="edit", label="Elevated", type="elevated", size="l"
                        ),
                        Button(
                            icon="edit", label="Filled", type="filled", size="l"
                        ),
                        Button(
                            icon="edit", label="Tonal", type="tonal", size="l"
                        ),
                        Button(
                            icon="edit", label="Outlined", type="outlined", size="l"
                        ),
                        Button(icon="edit", label="Text", type="text", size="l"),
                        # Extra Large
                        widgets.Label(
                            label="Extra Large", css_classes=["settings-category-label"]
                        ),
                        Button(
                            icon="edit", label="Elevated", type="elevated", size="xl"
                        ),
                        Button(
                            icon="edit", label="Filled", type="filled", size="xl"
                        ),
                        Button(
                            icon="edit", label="Tonal", type="tonal", size="xl"
                        ),
                        Button(
                            icon="edit", label="Outlined", type="outlined", size="xl"
                        ),
                        Button(
                            icon="edit", label="Text", type="text", size="xl"
                        ),
                        # Connected Button Groups
                        widgets.Label(
                            label="Connected Button Groups",
                            css_classes=["settings-category-label"],
                        ),
                        ConnectedButtonGroup(
                            [
                                Button(
                                    icon="counter_1", label="First", shape="square"
                                ),
                                Button(
                                    icon="counter_2", label="Second", shape="square"
                                ),
                                Button(
                                    icon="counter_3", label="Third", shape="square"
                                ),
                                Button(
                                    icon="counter_4", label="Fourth", shape="square"
                                ),
                                Button(
                                    icon="counter_5", label="Fifth", shape="square"
                                ),
                                Button(
                                    icon="counter_6", label="Sixth", shape="square"
                                ),
                            ]
                        ),
                        # Switches
                        widgets.Label(
                            label="Switches", css_classes=["settings-category-label"]
                        ),
                        widgets.Switch(halign="center"),
                        widgets.Switch(active=True, halign="center"),
                        # Checkboxes
                        widgets.Label(
                            label="Checkboxes", css_classes=["settings-category-label"]
                        ),
                        widgets.CheckButton(label="Checkbox 1", halign="center"),
                        widgets.CheckButton(
                            label="Checkbox 2", active=True, halign="center"
                        ),
                        # Radio Buttons
                        widgets.Label(
                            label="Radio Buttons",
                            css_classes=["settings-category-label"],
                        ),
                        widgets.CheckButton(
                            group=widgets.CheckButton(label="Radio Button 2"),
                            label="Radio Button 1",
                            halign="center",
                        ),
                        widgets.CheckButton(
                            group=widgets.CheckButton(label="Radio Button 3"),
                            label="Radio Button 2",
                            halign="center",
                        ),
                        widgets.CheckButton(
                            group=widgets.CheckButton(label="Radio Button 4"),
                            label="Radio Button 3",
                            halign="center",
                        ),
                        widgets.CheckButton(
                            group=widgets.CheckButton(label="radiobutton"),
                            label="Radio Button 4",
                            halign="center",
                        ),
                    ],
                )
            ),
        )

        utils.Poll(1000, self.print_test_variables)

    def print_test_variables(self, *args):
        print(f"Var 1: {self.test_variable}, Var 2: {self.test_variable_2}")
        print(f"Single Select: {self.test_single_select}")
        print(f"Multi Select: 1: {self.test_multi_select_1}, 2: {self.test_multi_select_2}, 3: {self.test_multi_select_3}")

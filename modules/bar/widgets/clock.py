import datetime
from ignis import widgets, utils
from user_settings import user_settings
compact_mode = user_settings.appearance.compact
vertical_bar = user_settings.appearance.vertical

class Clock:
    if not vertical_bar:
        def __init__(self):
            self.time_label = widgets.Label(css_classes=["time"], valign="end")
            self.date_label = widgets.Label(css_classes=["date"], valign="start")
            utils.Poll(1000, lambda _: self.update_time())
            if compact_mode < 3:
                utils.Poll(1000, lambda _: self.update_date())

        def update_time(self):
            self.time_label.set_label(datetime.datetime.now().strftime("%I:%M %P"))

        def update_date(self):
            self.date_label.set_label(datetime.datetime.now().strftime("%a %d %b"))

        def widget(self):
            if compact_mode == 0:
                vertical = True
                homogeneous = True
                spacing = 0
            elif compact_mode == 1:
                vertical = False
                homogeneous = False
                spacing = 10
                self.time_label.set_valign("center")
                self.date_label.set_valign("center")
            elif compact_mode == 2:
                vertical = False
                homogeneous = False
                spacing = 6
                self.time_label.set_valign("center")
                self.date_label.set_valign("center")
            elif compact_mode == 3:
                vertical = False
                homogeneous = False
                spacing = 0
                self.time_label.set_valign("center")
                self.date_label = None

            return widgets.Box(
                vertical=vertical,
                spacing=spacing,
                halign="center",
                valign="fill",
                homogeneous=homogeneous,
                vexpand=True,
                css_classes=["timedate"],
                child=[self.time_label, self.date_label]
            )
    else:
        def __init__(self):
            self.time_label = widgets.Label(css_classes=["time"], valign="end")
            self.date_label = widgets.Label(css_classes=["date"], valign="start")
            utils.Poll(1000, lambda _: self.update_time())
            if compact_mode < 3:
                utils.Poll(1000, lambda _: self.update_date())

        def update_time(self):
            self.time_label.set_label(datetime.datetime.now().strftime("%I%n%M"))

        def update_date(self):
            self.date_label.set_label(datetime.datetime.now().strftime("%a%n%d%n%b"))

        def widget(self):
            if compact_mode == 0:
                homogeneous = True
                spacing = 0
            elif compact_mode == 1:
                homogeneous = False
                spacing = 10
                self.time_label.set_valign("center")
                self.date_label.set_valign("center")
            elif compact_mode == 2:
                homogeneous = False
                spacing = 6
                self.time_label.set_valign("center")
                self.date_label.set_valign("center")
            elif compact_mode == 3:
                homogeneous = False
                spacing = 0
                self.time_label.set_valign("center")
                self.date_label = None

            return widgets.Box(
                vertical=True,
                spacing=spacing,
                halign="center",
                valign="fill",
                homogeneous=homogeneous,
                vexpand=True,
                css_classes=["timedate"],
                child=[self.time_label, self.date_label]
            )

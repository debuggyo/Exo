import datetime
from ignis import widgets, utils
from user_settings import user_settings

class Clock:
    def __init__(self):
        self.container = widgets.Box(halign="center", valign="fill")
        self.time_label = widgets.Label(css_classes=["time"])
        self.date_label = widgets.Label(css_classes=["date"])

        self.container.append(self.time_label)
        self.container.append(self.date_label)

        utils.Poll(1000, lambda _: self.update_labels())

    def update_labels(self):
        now = datetime.datetime.now()
        is_vertical = user_settings.appearance.vertical
        
        if is_vertical:
            time_format = "%I%n%M"
            date_format = "%a%n%d%n%b"
        else:
            time_format = "%I:%M %P"
            date_format = "%a %d %b"

        self.time_label.set_label(now.strftime(time_format))
        self.date_label.set_label(now.strftime(date_format))
        
    def update_layout(self):
        compact_mode = user_settings.appearance.compact
        
        if compact_mode == 0:
            self.container.set_spacing(0)
            self.container.set_homogeneous(True)
            self.time_label.set_valign("end")
            self.date_label.set_valign("start")
            self.date_label.set_visible(True)
            self.container.set_vertical(True)
        elif compact_mode == 1:
            self.container.set_spacing(10)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")
            self.date_label.set_valign("center")
            self.date_label.set_visible(True)
            self.container.set_vertical(False)
        elif compact_mode == 2:
            self.container.set_spacing(6)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")
            self.date_label.set_valign("center")
            self.date_label.set_visible(True)
            self.container.set_vertical(False)
        elif compact_mode == 3:
            self.container.set_spacing(0)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")
            self.date_label.set_visible(False)
            self.container.set_vertical(False)
        
    def widget(self):
        self.update_layout()
        return widgets.Box(
            vertical=False,
            halign="center",
            valign="fill",
            vexpand=True,
            css_classes=["timedate"],
            child=[self.container]
        )
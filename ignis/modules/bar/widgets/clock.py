import datetime
from ignis import widgets, utils
from user_settings import user_settings


class Clock:
    def __init__(self):
        self.container = widgets.Box(css_classes=["clock"], hexpand=True, vexpand=True)
        self.time_label = widgets.Label(css_classes=["time"], justify="center")
        self.separator = widgets.Label(
            css_classes=["separator"],
            visible=False,
            label="•",
            hexpand=False,
            vexpand=False,
        )
        self.date_label = widgets.Label(css_classes=["date"], justify="center")
        self.date_separator = widgets.Separator(
            vertical=False, hexpand=False, vexpand=False
        )
        self.month_label = widgets.Label(
            css_classes=["month"], justify="center", visible=False
        )

        self.container.append(self.time_label)
        self.container.append(self.separator)
        self.container.append(self.date_label)
        self.container.append(self.date_separator)
        self.container.append(self.month_label)

        utils.Poll(1000, lambda _: self.update_labels())

        self.update_layout()

    def update_labels(self):
        now = datetime.datetime.now()
        settings = user_settings.interface.modules.options
        bar = (
            user_settings.interface.bar
            if user_settings.interface.modules.bar_id.clock == 0
            else user_settings.interface.bar2
        )
        is_vertical = bar.vertical
        day_month_swapped = settings.day_month_swapped
        military_time = settings.military_time

        if is_vertical:
            time_format = "%H%n%M" if military_time else "%I%n%M"
            date_format = "%d" if not day_month_swapped else "%m"
            month_format = "%m" if not day_month_swapped else "%d"
        else:
            time_format = "%H:%M" if military_time else "%I:%M %p"
            date_format = "%a %d %b" if not day_month_swapped else "%a %b %d"
            month_format = ""

        self.time_label.set_label(now.strftime(time_format))
        self.date_label.set_label(now.strftime(date_format))
        self.month_label.set_label(now.strftime(month_format))

    def update_layout(self):
        settings = user_settings.interface.modules.options
        bar = (
            user_settings.interface.bar
            if user_settings.interface.modules.bar_id.clock == 0
            else user_settings.interface.bar2
        )
        is_vertical = (
            user_settings.interface.bar.vertical
            if user_settings.interface.modules.bar_id.clock == 0
            else user_settings.interface.bar2.vertical
        )
        compact_mode = bar.density
        date_visible = settings.show_date

        self.container.set_halign("fill")
        self.container.set_valign("fill")

        self.container.set_vertical(is_vertical)

        if date_visible:
            self.date_label.set_visible(True)
            if is_vertical:
                self.separator.set_visible(True)
            elif compact_mode == 0:
                self.separator.set_visible(False)
            else:
                self.separator.set_visible(True)
            if is_vertical:
                self.date_separator.set_visible(True)
                self.month_label.set_visible(True)
            else:
                self.date_separator.set_visible(False)
                self.month_label.set_visible(False)
        else:
            self.separator.set_visible(False)
            self.date_label.set_visible(False)
            self.date_separator.set_visible(False)
            self.month_label.set_visible(False)

        if is_vertical:
            self.container.set_spacing(0)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")

        elif compact_mode == 0:
            self.container.set_spacing(0)
            self.container.set_homogeneous(True)
            if date_visible:
                self.time_label.set_valign("end")
                self.date_label.set_valign("start")
            else:
                self.time_label.set_valign("center")
                self.date_label.set_valign("center")
            self.container.set_vertical(True)

        elif compact_mode == 1:
            self.container.set_spacing(10)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")
            self.date_label.set_valign("center")
            self.container.set_vertical(False)

        elif compact_mode == 2:
            self.container.set_spacing(6)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")
            self.date_label.set_valign("center")
            self.container.set_vertical(False)

        elif compact_mode == 3:
            self.container.set_spacing(4)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")
            self.container.set_vertical(False)

    def widget(self):
        return self.container

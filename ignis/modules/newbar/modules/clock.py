import datetime
from ignis import utils
from gi.repository import Gtk
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty

class Clock(Gtk.Box, BaseWidget):
    __gtype_name__ = "ExoClock"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(
        self,
        vertical: bool = False,
        show_date: bool = True,
        density: bool = True,
        month_before_day: bool = False,
        military_time: bool = False,
        **kwargs
    ):
        Gtk.Box.__init__(self)
        self._vertical = vertical
        self._show_date = show_date
        self._two_line = True if density == 0 else False
        self._month_before_day = month_before_day
        self._military_time = military_time

        self.time_label = Gtk.Label(label="Time", justify=Gtk.Justification.CENTER, vexpand=True)
        self.date_label = Gtk.Label(label="Date", justify=Gtk.Justification.CENTER, vexpand=True)
        self.month_label = Gtk.Label(label="Month", justify=Gtk.Justification.CENTER, vexpand=True)
        self.separator = Gtk.Separator()

        self.append(self.time_label)
        self.append(self.separator)
        self.append(self.date_label)

        self.time_label.add_css_class("time")
        self.date_label.add_css_class("date")
        self.add_css_class("exo-clock")
        self.set_overflow(Gtk.Overflow.HIDDEN)

        self.update_layout()
        utils.Poll(1000, lambda _: self.update_time())

        BaseWidget.__init__(self, **kwargs)

    @IgnisProperty
    def vertical(self) -> bool:
        return self._vertical

    @IgnisProperty
    def show_date(self) -> bool:
        return self._show_date

    @IgnisProperty
    def two_line(self) -> bool:
        return self._two_line

    @IgnisProperty
    def month_before_day(self) -> bool:
        return self._month_before_day

    @IgnisProperty
    def military_time(self) -> bool:
        return self._military_time

    @vertical.setter
    def vertical(self, value: bool) -> None:
        self._vertical = value
        self.update_layout()

    @show_date.setter
    def show_date(self, value: bool) -> None:
        self._show_date = value
        self.update_layout()

    @two_line.setter
    def two_line(self, value: bool) -> None:
        self._two_line = value
        self.update_layout()

    @month_before_day.setter
    def month_before_day(self, value: bool) -> None:
        self._month_before_day = value
        self.update_layout()

    @military_time.setter
    def military_time(self, value: bool) -> None:
        self._military_time = value
        self.update_layout()

    def update_layout(self):
        self.set_orientation(Gtk.Orientation.VERTICAL if self._vertical or self._two_line else Gtk.Orientation.HORIZONTAL)
        self.date_label.set_visible(True if self._show_date else False)
        self.separator.set_orientation(Gtk.Orientation.HORIZONTAL if self._vertical else Gtk.Orientation.VERTICAL)
        self.separator.set_visible(True if self._show_date and not self._two_line or self._vertical else False)

        if self._show_date:
            self.time_label.set_valign(Gtk.Align.END if not self._vertical and self._two_line else Gtk.Align.CENTER)
            self.date_label.set_valign(Gtk.Align.START if not self._vertical and self._two_line else Gtk.Align.CENTER)
        else:
            self.time_label.set_valign(Gtk.Align.CENTER)

        if not self._vertical and self._two_line: # date under time, horizontal bar
            self.set_spacing(0)
        else:
            self.set_spacing(5)

        # CSS Classes
        if self._two_line:
            self.add_css_class("two-line")
        else:
            self.remove_css_class("two-line")
        if not self._show_date:
            self.add_css_class("no-date")
        else:
            self.remove_css_class("no-date")

    def update_time(self):
        now = datetime.datetime.now()
        if self._vertical:
            time_format = "%H%n%M" if self._military_time else "%I%n%M"
            date_format = "%d%n%m" if not self._month_before_day else "%m%n%d"
        else:
            time_format = "%H:%M" if self._military_time else "%I:%M %p"
            date_format = "%a %d %b" if not self._month_before_day else "%a %b %d"

        self.time_label.set_label(now.strftime(time_format))
        if self._show_date:
            self.date_label.set_label(now.strftime(date_format))

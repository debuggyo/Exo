import datetime
from ignis import utils
from gi.repository import Gtk
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty

class Clock(Gtk.Box, BaseWidget):
    __gtype_name__ = "ExoClock"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self)
        self._vertical: bool = False
        self._density: int = 0
        self._show_date: bool = True
        self._month_before_day: bool = False
        self._military_time: bool = False

        self.time_label = Gtk.Label(label="Time", justify=Gtk.Justification.CENTER, vexpand=True)
        self.date_label = Gtk.Label(label="Date", justify=Gtk.Justification.CENTER, vexpand=True)
        self.month_label = Gtk.Label(label="Month", justify=Gtk.Justification.CENTER, vexpand=True)
        self.separator = Gtk.Separator()
        self.date_separator = Gtk.Separator()

        self.append(self.time_label)
        self.append(self.separator)
        self.append(self.date_label)
        self.append(self.date_separator)
        self.append(self.month_label)

        self.time_label.add_css_class("time")
        self.separator.add_css_class("main-separator")
        self.date_label.add_css_class("date")
        self.date_separator.add_css_class("date-separator")
        self.month_label.add_css_class("month")
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
    def density(self) -> int:
        return self._density

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

    @density.setter
    def density(self, value: int) -> None:
        self._density = value
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
        two_line = True if self._density == 0 else False

        self.set_visible(False)
        self.set_orientation(Gtk.Orientation.VERTICAL if self._vertical or two_line else Gtk.Orientation.HORIZONTAL)
        self.date_label.set_visible(True if self._show_date else False)
        self.date_separator.set_visible(True if self._vertical and self._show_date else False)
        self.month_label.set_visible(True if self._vertical and self._show_date else False)
        self.separator.set_orientation(Gtk.Orientation.HORIZONTAL if self._vertical else Gtk.Orientation.VERTICAL)
        self.separator.set_visible(True if self._show_date and not two_line or self._show_date and self._vertical else False)

        if self._show_date:
            self.time_label.set_valign(Gtk.Align.END if not self._vertical and two_line else Gtk.Align.CENTER)
            self.date_label.set_valign(Gtk.Align.START if not self._vertical and two_line else Gtk.Align.CENTER)
        else:
            self.time_label.set_valign(Gtk.Align.CENTER)

        if not self._vertical and two_line: # date under time, horizontal bar
            self.set_spacing(0)
        else:
            self.set_spacing(5)


        # CSS Classes
        if two_line:
            self.add_css_class("two-line")
        else:
            self.remove_css_class("two-line")
        if not self._show_date:
            self.add_css_class("no-date")
        else:
            self.remove_css_class("no-date")
        if self._vertical:
            self.add_css_class("clock-vertical")
        else:
            self.remove_css_class("clock-vertical")

    def update_time(self):
        now = datetime.datetime.now()
        if self._vertical:
            time_format = "%H%n%M" if self._military_time else "%I%n%M"
            date_format = "%d" if not self._month_before_day else "%m"
            month_format = "%m" if not self._month_before_day else "%d"
        else:
            time_format = "%H:%M" if self._military_time else "%I:%M %p"
            date_format = "%a %d %b" if not self._month_before_day else "%a %b %d"

        self.set_visible(True)
        self.time_label.set_label(now.strftime(time_format))
        if self._show_date:
            self.date_label.set_label(now.strftime(date_format))
            if self._vertical:
                self.month_label.set_label(now.strftime(month_format))

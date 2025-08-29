import datetime
from ignis import widgets, utils
from user_settings import user_settings

class Clock:
    def __init__(self):
        self.container = widgets.Box(css_classes=["timedate"])
        self.time_label = widgets.Label(css_classes=["time"])
        self.date_label = widgets.Label(css_classes=["date"])

        self.container.append(self.time_label)
        self.container.append(self.date_label)

        utils.Poll(1000, lambda _: self.update_labels())
        
        self.update_layout()

    def update_labels(self):
        now = datetime.datetime.now()
        is_vertical = user_settings.interface.bar.vertical
        military_time = user_settings.interface.bar.modules.military_time

        if is_vertical:
            time_format = "%H" if military_time else "%I"
            date_format = "%M"
        else:
            if military_time:
                time_format = "%H:%M"
            else:
                time_format = "%I:%M %p"
            date_format = "%a %d %b"

        self.time_label.set_label(now.strftime(time_format))
        self.date_label.set_label(now.strftime(date_format))
        
    def update_layout(self):
        is_vertical = user_settings.interface.bar.vertical
        compact_mode = user_settings.interface.bar.density
        
        self.container.set_halign("fill")
        self.container.set_valign("fill")
        
        self.container.set_vertical(is_vertical)
        if is_vertical:
            self.container.set_hexpand(True)
            self.container.set_vexpand(True)
        else:
            self.container.set_hexpand(True)
            self.container.set_vexpand(True)

        if is_vertical:
            self.date_label.set_visible(True)
            self.container.set_spacing(0)
            self.container.set_homogeneous(True)
            self.time_label.set_valign("center")
            
        elif compact_mode == 0:
            self.date_label.set_visible(True)
            self.container.set_spacing(0)
            self.container.set_homogeneous(True)
            self.time_label.set_valign("end")
            self.date_label.set_valign("start")
            self.container.set_vertical(True)
        
        elif compact_mode == 1:
            self.date_label.set_visible(True)
            self.container.set_spacing(10)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")
            self.date_label.set_valign("center")
            self.container.set_vertical(False)
        
        elif compact_mode == 2:
            self.date_label.set_visible(True)
            self.container.set_spacing(6)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")
            self.date_label.set_valign("center")
            self.container.set_vertical(False)
        
        elif compact_mode == 3:
            self.date_label.set_visible(False)
            self.container.set_spacing(0)
            self.container.set_homogeneous(False)
            self.time_label.set_valign("center")
            self.container.set_vertical(False)
        
    def widget(self):
        return self.container
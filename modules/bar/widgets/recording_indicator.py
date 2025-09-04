import datetime
import threading
import time
from ignis import widgets, utils
from user_settings import user_settings
from scripts.recorder import stop_recording, pause_recording, unpause_recording, recorder, record_portal, record_screen, record_region

class RecordingIndicator:
    def __init__(self):
        self.container = widgets.Button(
            on_click=lambda _: self.handle_click(),
            on_right_click=lambda _: self.handle_right_click(),
            css_classes=["recording-indicator"],
            tooltip_text="Click to start/stop recording. \nRight click to pause/unpause."
        )
        self.container.set_name("recording-indicator")
        
        self.is_recording = False
        self.is_paused = False
        self._start_time = 0

        self.icon = widgets.Label(label="screen_record", css_classes=["recording-icon"])
        self.timer_label_hms = widgets.Label(label="00:00")
        self.timer_label_s = widgets.Label(label="")
        
        self.timer_box = widgets.Box(css_classes=["timer-box"])
        self.timer_box.append(self.timer_label_hms)
        self.timer_box.append(self.timer_label_s)

        self.content_box = widgets.Box()
        self.content_box.append(self.icon)
        self.content_box.append(self.timer_box)

        self.container.set_child(self.content_box)

        self.update_layout()
        self.update_visibility()
        
        utils.Poll(1000, lambda _: self._update_timer())
        utils.Poll(1000, lambda _: self.update_layout())

    def _update_timer(self):
        if not self.is_recording or self.is_paused:
            return

        elapsed_time = datetime.datetime.now() - self._start_time
        seconds = int(elapsed_time.total_seconds())
        
        m, s = divmod(seconds, 60)
        
        is_vertical = user_settings.interface.bar.vertical
        if is_vertical:
            self.timer_label_hms.set_label(f"{m:02d}")
            self.timer_label_s.set_label(f"{s:02d}")
        else:
            self.timer_label_hms.set_label(f"{m:02d}:{s:02d}")
            self.timer_label_s.set_label("")
    
    def handle_click(self):
        mode = user_settings.interface.bar.modules.recording_indicator
        
        if mode == "always":
            if recorder.active:
                stop_recording()
            else:
                record_screen()
        elif mode == "recording":
            if recorder.active:
                stop_recording()

    def handle_right_click(self):
        mode = user_settings.interface.bar.modules.recording_indicator

        if mode == "always":
            if recorder.active:
                stop_recording()
            else:
                record_region()
        elif mode == "recording":
            if recorder.active:
                stop_recording()
    
    def toggle_pause_recording(self):
        if self.is_paused:
            unpause_recording()
        else:
            pause_recording()

    def set_paused(self, is_paused: bool):
        self.is_paused = is_paused
        if is_paused:
            self.icon.set_label("pause")
            self.container.add_css_class("paused")
        else:
            self.icon.set_label("screen_record")
            self.container.remove_css_class("paused")

    def update_layout(self):
        is_vertical = user_settings.interface.bar.vertical
        
        self.content_box.set_vertical(is_vertical)
        self.content_box.set_spacing(0)
        self.content_box.set_halign("center")
        self.content_box.set_valign("center")
        self.content_box.set_spacing(8)

        self.timer_box.set_vertical(is_vertical)
        self.timer_box.set_spacing(0)
        
        if is_vertical:
            self.timer_label_s.set_visible(True)
            self.timer_label_s.set_halign("center")
            self.content_box.set_homogeneous(False)
        else:
            self.timer_label_s.set_visible(False)
            self.content_box.set_homogeneous(False)
    
    def update_visibility(self):
        mode = user_settings.interface.bar.modules.recording_indicator
        
        if mode == "never":
            self.container.set_visible(False)
            self.timer_box.set_visible(False)
        elif mode == "always":
            self.container.set_visible(True)
            self.timer_box.set_visible(self.is_recording)
            self.icon.set_visible(True)
        elif mode == "recording":
            self.container.set_visible(self.is_recording)
            self.icon.set_visible(self.is_recording)
            self.timer_box.set_visible(self.is_recording)

    def start_timer(self):
        if not self.is_recording:
            self.is_recording = True
            self._start_time = datetime.datetime.now()
            self.update_visibility()
            self.container.add_css_class("recording-active")

    def stop_timer(self):
        if self.is_recording:
            self.is_recording = False
            self.is_paused = False
            self.container.remove_css_class("paused")
            self.update_visibility()
            self.container.remove_css_class("recording-active")

    def widget(self):
        return self.container
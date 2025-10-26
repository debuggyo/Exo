from ignis import widgets, utils
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
from ignis.services.recorder import RecorderService, RecorderConfig
import modules.m3components as m3
import datetime
import asyncio
from gi.repository import Gtk
from scripts.recorder import (
    stop_recording,
    pause_recording,
    unpause_recording,
    recorder,
    record_screen,
    record_region,
)

class RecordingIndicator(widgets.EventBox, BaseWidget):
    __gtype_name__ = "ExoRecordingIndicator"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        widgets.EventBox.__init__(self, spacing=8)
        self._vertical: bool = False
        self._show_time: bool = True
        self._show_always: bool = False
        self._start_time = None
        self._pause_start_time = None

        self.recorder = RecorderService.get_default()
        self.icon = m3.Icon("screen_record", 16, halign="center", valign="center")
        self.time = widgets.Label(halign="center", valign="center", visible=True, justify="center",)
        self.revealer = Gtk.Revealer(child=self.time, transition_type=Gtk.RevealerTransitionType.SLIDE_LEFT)

        self.append(self.icon)
        self.append(self.revealer)

        self.add_css_class("exo-recording-indicator")

        self.recorder.connect("recording_started", self._on_started)
        self.recorder.connect("recording_stopped", self._on_stopped)
        self.recorder.connect("notify::is-paused", self._on_pause_changed)

        utils.Poll(1000, self._update_timer)

        BaseWidget.__init__(self, **kwargs)

        self.on_click = self._on_left_click

        right_click_gesture = Gtk.GestureClick.new()
        right_click_gesture.set_button(3)
        right_click_gesture.connect("pressed", self._on_right_press)
        self.add_controller(right_click_gesture)

        self._update_info()

    @IgnisProperty
    def vertical(self) -> bool:
        return self.get_orientation() == Gtk.Orientation.VERTICAL

    @vertical.setter
    def vertical(self, value: bool):
        orientation = Gtk.Orientation.VERTICAL if value else Gtk.Orientation.HORIZONTAL
        self.set_orientation(orientation)
        transition = Gtk.RevealerTransitionType.SLIDE_DOWN if value else Gtk.RevealerTransitionType.SLIDE_LEFT
        self.revealer.set_transition_type(transition)

    @IgnisProperty
    def show_time(self) -> bool:
        return self._show_time

    @show_time.setter
    def show_time(self, value: bool) -> None:
        if value == self._show_time:
            return
        self._show_time = value
        self._update_info()

    @IgnisProperty
    def show_always(self) -> bool:
        return self._show_always

    @show_always.setter
    def show_always(self, value: bool) -> None:
        if value == self._show_always:
            return
        self._show_always = value
        self._update_info()

    def _on_left_click(self, _):
        if self.recorder.active:
            stop_recording()
        else:
            record_screen()

    def _on_right_press(self, gesture, n_press, x, y):
        if self.recorder.active:
            if self.recorder.is_paused:
                unpause_recording()
            else:
                pause_recording()
        else:
            record_region()

    def _on_started(self, _):
        self._start_time = datetime.datetime.now()
        self.add_css_class("recording-active")
        self._update_info()

    def _on_stopped(self, _):
        self._start_time = None
        self._pause_start_time = None
        self.remove_css_class("recording-active")
        self.remove_css_class("paused")
        self.icon.set_icon("screen_record")
        self._update_info()

    def _on_pause_changed(self, _, __):
        if self.recorder.is_paused:
            self._pause_start_time = datetime.datetime.now()
            self.add_css_class("paused")
            self.icon.set_icon("pause")
        else:
            if self._pause_start_time and self._start_time:
                pause_duration = datetime.datetime.now() - self._pause_start_time
                self._start_time += pause_duration
                self._pause_start_time = None
            self.remove_css_class("paused")
            self.icon.set_icon("screen_record")

    def _update_timer(self, *args):
        if not self.recorder.active or self.recorder.is_paused or not self._start_time:
            return True

        elapsed_time = datetime.datetime.now() - self._start_time
        seconds = int(elapsed_time.total_seconds())
        m, s = divmod(seconds, 60)
        if self.vertical:
            self.time.set_label(f"{m:02d}\n{s:02d}")
        else:
            self.time.set_label(f"{m:02d}:{s:02d}")
        return True

    def _update_info(self):
        if self.recorder.active:
            self.set_visible(True)
            self.revealer.set_reveal_child(self._show_time)
        else:
            self.set_visible(self._show_always)
            self.revealer.set_reveal_child(False)
            self.time.set_label("")

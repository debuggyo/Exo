import asyncio
from gi.repository import GLib
from ignis import widgets
from ignis.services.audio import AudioService
from ignis.services.backlight import BacklightService
from ignis.window_manager import WindowManager

audio = AudioService.get_default()
backlight = BacklightService.get_default()
window_manager = WindowManager.get_default()


class QuickSliders(widgets.Box):
    def __init__(self):
        children = []
        if audio.speaker:
            self.volume_slider = widgets.Scale(
                min=0,
                max=100,
                step=1.0,
                on_change=self.on_volume_changed,
                hexpand=True,
            )
            volume_box = widgets.Box(
                css_classes=["m3-slider"],
                child=[
                    widgets.Label(label="volume_up", css_classes=["m3-icon"]),
                    self.volume_slider,
                ],
                spacing=12,
            )
            children.append(volume_box)

        if backlight.available:
            self.backlight_slider = widgets.Scale(
                min=0,
                max=100,
                step=1.0,
                on_change=self.on_backlight_changed,
                hexpand=True,
            )
            backlight_box = widgets.Box(
                css_classes=["m3-slider"],
                child=[
                    widgets.Label(label="brightness_6", css_classes=["m3-icon"]),
                    self.backlight_slider,
                ],
                spacing=12,
            )
            children.append(backlight_box)

        super().__init__(
            css_classes=["quick-sliders-container"],
            hexpand=True,
            halign="fill",
            spacing=2,
            vertical=True,
            child=children,
        )

        if audio.speaker:
            audio.speaker.connect("notify::volume", self._on_volume_changed)
            audio.speaker.connect("notify::is-muted", self._on_volume_changed)
        if backlight.available:
            backlight.connect("notify::brightness", self._on_brightness_changed)

    def _on_volume_changed(self, stream, *_):
        if stream.is_muted:
            self.volume_slider.set_value(0)
        else:
            self.volume_slider.set_value(stream.volume)

    def _on_brightness_changed(self, backlight, *_):
        self.backlight_slider.set_value(
            (backlight.brightness / backlight.max_brightness) * 100
        )

    def on_volume_changed(self, slider):
        value = slider.get_value()
        self.set_suppress_osd_flag()
        audio.speaker.volume = value

    def on_backlight_changed(self, slider):
        value = slider.get_value()
        self.set_suppress_osd_flag()
        backlight.brightness = int((value / 100) * backlight.max_brightness)

    def set_suppress_osd_flag(self):
        window_manager.suppress_osd = True
        asyncio.create_task(self.reset_suppress_osd_flag())

    async def reset_suppress_osd_flag(self):
        await asyncio.sleep(0.1)
        window_manager.suppress_osd = False

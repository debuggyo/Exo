from ignis import widgets
from ignis.services.audio import AudioService
from ignis.services.backlight import BacklightService
from modules.m3components import Slider

audio = AudioService.get_default()
backlight = BacklightService.get_default()


class QuickSliders(widgets.Box):
    def __init__(self):
        children = []
        if audio.speaker:
            current_volume = audio.speaker.volume
            self.volume_slider = Slider.slider(
                min=0,
                max=100,
                step=1.0,
                value=current_volume,
                on_change=self.on_volume_changed,
                icon="volume_up",
            )
            children.append(self.volume_slider)

        if backlight.available:
            self.backlight_slider = Slider.slider(
                min=0,
                max=backlight.max_brightness,
                step=1.0,
                value=backlight.brightness,
                on_change=self.on_backlight_changed,
                icon="brightness_6",
            )
            children.append(self.backlight_slider)

        super().__init__(
            css_classes=["quick-toggles-container"],
            hexpand=True,
            halign="fill",
            spacing=2,
            child=children
        )

    def on_volume_changed(self, slider):
        value = slider.value
        audio.speaker.volume = value

    def on_backlight_changed(self, slider):
        value = slider.value
        backlight.brightness = int(value)

import asyncio
from ignis import widgets
from ignis.services.audio import AudioService
from ignis.services.backlight import BacklightService
from ignis.window_manager import WindowManager
from user_settings import user_settings


class OSD(widgets.RevealerWindow):
    def __init__(self):
        self.wm = WindowManager.get_default()
        self.icon = widgets.Label(label="", css_classes=["osd-icon", "m3-icon"])
        self.progress = widgets.Scale(
            css_classes=["osd-progress"],
            draw_value=False,
            min=0,
            max=1,
            sensitive=False,
        )
        main_box = widgets.Box(
            valign="center",
            halign="center",
            css_classes=["osd"],
            spacing=12,
            child=[self.icon, self.progress],
        )

        revealer = widgets.Revealer(
            child=main_box,
            transition_duration=250,
            transition_type="crossfade",
            halign="center",
            valign="center",
        )

        super().__init__(
            revealer=revealer,
            child=revealer,
            kb_mode="none",
            namespace="OSD",
            exclusivity="normal",
            visible=False,
            layer="overlay",
            margin_top=20,
            margin_bottom=20,
            margin_left=20,
            margin_right=20,
        )

        self.main_box = main_box
        self.revealer = revealer
        self.hide_task = None

        self.connect("notify::visible", self._toggle_revealer)

        self.audio = AudioService.get_default()
        self.backlight = BacklightService.get_default()

        self.audio.speaker.connect("notify::volume", self._on_volume_changed)
        self.audio.speaker.connect("notify::is-muted", self._on_volume_changed)
        self.backlight.connect("notify::brightness", self._on_brightness_changed)
        user_settings.services.osd.connect_option(
            "anchor", lambda: self.update_layout()
        )
        user_settings.services.osd.connect_option(
            "vertical", lambda: self.update_layout()
        )

        self.update_layout()

        self._on_volume_changed(self.audio.speaker)
        self._on_brightness_changed(self.backlight)

    def _toggle_revealer(self, *_):
        self.revealer.reveal_child = self.visible

    def _on_volume_changed(self, stream, *_):
        self.show_osd()
        if stream.is_muted:
            self.icon.set_label("volume_off")
            self.progress.set_value(0)
        else:
            self.icon.set_label("volume_up")
            self.progress.set_value(stream.volume / 100)

    def _on_brightness_changed(self, backlight, *_):
        self.show_osd()
        self.icon.set_label("brightness_medium")
        self.progress.set_value(backlight.brightness / backlight.max_brightness)

    def show_osd(self):
        if hasattr(self.wm, "suppress_osd") and self.wm.suppress_osd:
            return
        self.visible = True
        if self.hide_task:
            self.hide_task.cancel()
        self.hide_task = asyncio.create_task(self._hide_osd())

    async def _hide_osd(self):
        await asyncio.sleep(2)
        self.visible = False

    def update_layout(self):
        settings = user_settings.services.osd

        self.set_anchor(None)
        self.set_anchor(settings.anchor)
        if settings.anchor not in [["left"], ["right"], ["top"], ["bottom"]]:
            vertical = settings.vertical
        elif settings.anchor in [["top"], ["bottom"]]:
            vertical = False
        elif settings.anchor in [["left"], ["right"]]:
            vertical = True
        self.main_box.set_vertical(vertical)
        self.progress.set_vertical(vertical)
        if vertical:
            self.add_css_class("vertical")
            self.progress.set_height_request(200)
            self.progress.set_width_request(20)
        else:
            self.remove_css_class("vertical")
            self.progress.set_height_request(20)
            self.progress.set_width_request(200)

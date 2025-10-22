import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
from ignis import widgets, utils
from ignis.services.mpris import MprisService, MprisPlayer

class Media(Gtk.Box, BaseWidget):
    __gtype_name__ = "ExoMedia"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, spacing=8)
        self._vertical: bool = False
        self._density: int = 0
        self._show_labels: bool = True
        self._show_controls: bool = True
        self._player: MprisPlayer = None
        self._player_index: int = 0

        self.mpris = MprisService.get_default()

        scroll_controller = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.VERTICAL)
        scroll_controller.connect("scroll", self.on_scroll)
        self.add_controller(scroll_controller)

        self.icon = widgets.Icon(pixel_size=24, halign="center", valign="center", css_classes=["icon"], overflow=Gtk.Overflow.HIDDEN)

        self.labels_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER)
        self.title_label = Gtk.Label(
            halign=Gtk.Align.START, xalign=0, ellipsize=Pango.EllipsizeMode.END, max_width_chars=20, width_chars=20,
        )
        self.artist_label = Gtk.Label(
            halign=Gtk.Align.START, xalign=0, ellipsize=Pango.EllipsizeMode.END, max_width_chars=24, width_chars=20,
        )
        self.labels_box.append(self.title_label)
        self.labels_box.append(self.artist_label)

        self.controls_box = Gtk.Box(spacing=4)
        self.prev_label = widgets.Label(label="skip_previous", css_classes=["m3-icon"])
        self.play_pause_label = widgets.Label(css_classes=["m3-icon"])
        self.next_label = widgets.Label(label="skip_next", css_classes=["m3-icon"])
        self.prev_button = widgets.Button(child=self.prev_label, on_click=lambda _: self.prev(), halign="center", hexpand=False, valign="center", vexpand=False)
        self.play_pause_button = widgets.Button(child=self.play_pause_label, on_click=lambda _: self.play_pause(), css_classes=["play-pause-button"], halign="center", hexpand=False, valign="center", vexpand=False)
        self.next_button = widgets.Button(child=self.next_label, on_click=lambda _: self.next(), halign="center", hexpand=False, valign="center", vexpand=False)
        self.controls_box.append(self.prev_button)
        self.controls_box.append(self.play_pause_button)
        self.controls_box.append(self.next_button)

        self.append(self.icon)
        self.append(self.labels_box)
        self.append(self.controls_box)

        self.add_css_class("exo-media")
        self.icon.add_css_class("icon")
        self.title_label.add_css_class("title")
        self.artist_label.add_css_class("artist")
        self.controls_box.add_css_class("controls")

        BaseWidget.__init__(self, **kwargs)
        self.mpris.connect("notify::players", self._update_player)
        utils.Poll(1000, self._update_player)

        self._update_player()
        self.update_layout()

    @IgnisProperty
    def vertical(self) -> bool: return self._vertical

    @vertical.setter
    def vertical(self, value: bool):
        self._vertical = value
        self.update_layout()

    @IgnisProperty
    def density(self) -> int: return self._density

    @density.setter
    def density(self, value: int):
        self._density = value
        self.update_layout()

    @IgnisProperty
    def show_labels(self) -> bool: return self._show_labels

    @show_labels.setter
    def show_labels(self, value: bool):
        self._show_labels = value
        self.update_layout()

    @IgnisProperty
    def show_controls(self) -> bool: return self._show_controls

    @show_controls.setter
    def show_controls(self, value: bool):
        self._show_controls = value
        self.update_layout()

    def on_scroll(self, _, _dx, dy):
        players = self.mpris.players
        if len(players) < 2:
            return

        if dy > 0:
            self._player_index = (self._player_index + 1) % len(players)
        else:
            self._player_index = (self._player_index - 1 + len(players)) % len(players)

        new_player = players[self._player_index]
        if new_player != self._player:
            if self._player:
                self._player.disconnect_by_func(self._update_info)
            self._player = new_player
            self._player.connect("notify::metadata", self._update_info)
            self._player.connect("notify::playback-status", self._update_info)
            self._player.connect("notify::art-url", self._update_info)
            self._update_info()

    def play_pause(self):
        if self._player: self._player.play_pause()

    def next(self):
        if self._player: self._player.next()

    def prev(self):
        if self._player: self._player.previous()

    def _update_player(self, *args):
        players = self.mpris.players

        if self._player not in players:
            if self._player:
                self._player.disconnect_by_func(self._update_info)

            if players:
                if self._player_index >= len(players):
                    self._player_index = 0
                self._player = players[self._player_index]
                self._player.connect("notify::metadata", self._update_info)
                self._player.connect("notify::playback-status", self._update_info)
                self._player.connect("notify::art-url", self._update_info)
            else:
                self._player = None
        elif players:
            self._player_index = players.index(self._player)

        self._update_info()

    def _update_info(self, *args):
        if self._player:
            self.remove_css_class("placeholder")
            self.icon.remove_css_class("playing")
            self.icon.remove_css_class("paused")
            title = self._player.title or "Unknown Title"
            artist = self._player.artist or "Unknown Artist"
            self.title_label.set_label(title)
            self.artist_label.set_label(artist)

            tooltip_text = f"{title} - {artist}"
            self.icon.set_tooltip_text(tooltip_text)
            self.labels_box.set_tooltip_text(tooltip_text)

            if self._player.art_url:
                self.icon.set_image(self._player.art_url)
            else:
                image = utils.get_app_icon_name(self._player.desktop_entry)
                if image:
                    self.icon.set_image(image)
                else:
                    self.icon.set_image("audio-x-generic-symbolic")

            status = self._player.playback_status
            is_playing = status == "Playing"
            self.play_pause_label.set_label("pause" if is_playing else "play_arrow")
            self.icon.add_css_class("playing" if is_playing else "paused")

            self.prev_button.set_sensitive(self._player.can_go_previous)
            self.next_button.set_sensitive(self._player.can_go_next)
            self.play_pause_button.set_sensitive(self._player.can_play or self._player.can_pause)
        else:
            self.add_css_class("placeholder")
            self.title_label.set_label("No Media Playing")
            self.artist_label.set_label("Play something!")
            self.icon.set_image("audio-x-generic-symbolic")
            self.play_pause_label.set_label("play_arrow")
            self.prev_button.set_sensitive(False)
            self.next_button.set_sensitive(False)
            self.play_pause_button.set_sensitive(False)
            self.icon.set_tooltip_text(None)
            self.labels_box.set_tooltip_text(None)

    def update_layout(self):
        self.set_orientation(Gtk.Orientation.VERTICAL if self._vertical else Gtk.Orientation.HORIZONTAL)
        self.labels_box.set_visible(self._show_labels and not self._vertical)
        self.controls_box.set_visible(self._show_controls)

        if self._density > 0:
            self.artist_label.set_visible(False)
            self.icon.set_pixel_size(16)
            self.set_spacing(4)
        elif self._density == 1:
            self.icon.set_pixel_size(24)
        else:
            self.artist_label.set_visible(True)
            self.icon.set_pixel_size(24)
            self.set_spacing(8)

        self.controls_box.set_orientation(Gtk.Orientation.VERTICAL if self._vertical else Gtk.Orientation.HORIZONTAL)

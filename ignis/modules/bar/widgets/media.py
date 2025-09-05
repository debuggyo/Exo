# media.py

from ignis import widgets, utils
from ignis.services.mpris import MprisService, MprisPlayer
from user_settings import user_settings
from gi.repository import Gtk

mpris = MprisService.get_default()

class Player(widgets.Box):
    def update_labels_and_icon(self):
        self.title_label.set_label(str(self.player.title))
        self.artist_label.set_label(str(self.player.artist))
        
        if self.player.art_url:
            self.icon.set_image(self.player.art_url)
        else:
            self.icon.set_image("audio-volume-high")
        
        self.update_tooltip()

    def update_tooltip(self):
        if not self._show_labels:
            tooltip_text = f"{self.player.title}\nby {self.player.artist}"
            if self.get_parent():
                self.get_parent().set_tooltip_text(tooltip_text)
        else:
            if self.get_parent():
                self.get_parent().set_tooltip_text("")

    def update_layout(self):
        vertical = user_settings.interface.bar.vertical
        
        if self._show_labels and not vertical:
            self.labels_box.set_visible(True)
            if user_settings.interface.bar.density > 0:
                self.artist_label.set_visible(False)
                self.icon.set_pixel_size(16)
                self.icon_container.set_size_request(16, 16)
                self.play_pause_label.set_size_request(16, 16)
            else:
                self.artist_label.set_visible(True)
                self.icon.set_pixel_size(24)
                self.icon_container.set_size_request(24, 24)
                self.play_pause_label.set_size_request(24, 24)
        else:
            self.labels_box.set_visible(False)
            if user_settings.interface.bar.density > 0:
                self.icon.set_pixel_size(16)
                self.icon_container.set_size_request(16, 16)
                self.play_pause_label.set_size_request(16, 16)
            else:
                self.icon.set_pixel_size(24)
                self.icon_container.set_size_request(24, 24)
                self.play_pause_label.set_size_request(24, 24)
        
        self.update_tooltip()

    def on_playback_status_changed(self, player, gparam):
        status = player.playback_status
        if status == "Playing" or status == "Paused":
            self.play_pause_label.set_visible(True)
            self.overlay_bg.set_visible(True)
            if status == "Playing":
                self.play_pause_label.set_label("pause")
                self.remove_css_class("is-paused")
            else:
                self.play_pause_label.set_label("play_arrow")
                self.add_css_class("is-paused")
        else:
            self.play_pause_label.set_visible(False)
            self.overlay_bg.set_visible(False)
            self.remove_css_class("is-paused")

    def __init__(self, player: MprisPlayer, show_labels: bool):
        self.player = player
        self._show_labels = show_labels
        
        self.icon = widgets.Icon(
            css_classes=["icon"],
            valign="center",
            pixel_size=24,
        )
        
        self.icon_container = widgets.Box(
            css_classes=["icon_container"],
            valign="center",
            child=[self.icon]
        )
        self.icon_container.set_overflow(Gtk.Overflow.HIDDEN)

        self.play_pause_label = widgets.Label(
            css_classes=["overlay-icon"],
            style="font-family: 'Material Symbols Outlined';",
            halign="center",
            valign="center",
        )
        self.overlay_bg = widgets.Box(
            css_classes=["overlay-bg"],
            halign="fill",
            valign="fill",
        )
        self.overlay = widgets.Overlay(
            valign="center",
            child=self.icon_container,
            overlays=[self.overlay_bg, self.play_pause_label],
            css_classes=["media-overlay"],
        )
        
        self.title_label = widgets.Label(
            css_classes=["title"],
            valign="end",
            halign="start",
            ellipsize="end",
            max_width_chars=24,
        )
        self.artist_label = widgets.Label(
            css_classes=["artist"],
            valign="end",
            halign="start",
            ellipsize="end",
            max_width_chars=24,
        )
        
        self.labels_box = widgets.Box(
            vertical=True,
            spacing=0,
            valign="center",
            vexpand=True,
            child=[
                self.title_label, self.artist_label
            ]
        )

        super().__init__(
            vertical=False,
            spacing=5,
            valign="center",
            homogeneous=False,
            vexpand=True,
            css_classes=[],
            child=[
                self.overlay,
                self.labels_box
            ]
        )

        utils.Poll(1000, lambda _: self.update_labels_and_icon())
        
        self.player.connect("notify::playback-status", self.on_playback_status_changed)
        self.on_playback_status_changed(self.player, None)
        self.update_layout()

class Media:
    def __init__(self):
        self.player_count = 0
        self.main_box = None
        self.__players = []

    def __setup(self, widget):
        self.main_box = widget
        utils.Poll(1000, self.__poll_players)
        self.__update_players()
        self.update_visibility()
        self.update_layout()

    def update_layout(self):
        if self.main_box:
            if user_settings.interface.bar.vertical:
                self.main_box.set_orientation(Gtk.Orientation.VERTICAL)
                self.main_box.width_request = -1
            else:
                self.main_box.set_orientation(Gtk.Orientation.HORIZONTAL)
                self.main_box.width_request = 150 if user_settings.interface.bar.centered else -1
            
            for player in self.__players:
                player.update_layout()

    def update_visibility(self):
        if self.main_box:
            self.main_box.set_visible(user_settings.interface.bar.modules.media_widget)

    def __poll_players(self, _):
        current_players = len(mpris.players)
        if current_players != self.player_count:
            self.player_count = current_players
            self.__update_players()

    def __update_players(self):
        if self.main_box:
            has_players = len(mpris.players) > 0
            self.main_box.set_visible(user_settings.interface.bar.modules.media_widget and has_players)
            
            last_child = self.main_box.get_last_child()
            while last_child:
                self.main_box.remove(last_child)
                last_child = self.main_box.get_last_child()
            
            self.__players = []
            
            num_players = len(mpris.players)
            for index, player_obj in enumerate(mpris.players):
                self.__add_player(player_obj, show_labels=(index == num_players - 1))

    def __add_player(self, obj: MprisPlayer, show_labels: bool) -> None:
        player = Player(obj, show_labels)
        self.__players.append(player)
        
        player_button = widgets.Button(
            child=player,
            vexpand=True,
            halign="center",
            on_click=lambda _: obj.play_pause(),
            css_classes=["media"],
        )
        
        self.main_box.append(player_button)
        
    def widget(self):
        return widgets.Box(
            vertical=False,
            setup=self.__setup
        )
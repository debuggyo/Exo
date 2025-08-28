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
            self.icon.set_visible(True)
            self.icon_label.set_visible(False)
            self.icon.set_image(self.player.art_url)
        else:
            self.icon.set_visible(False)
            self.icon_label.set_visible(True)

    def update_layout(self):
        # This function now re-applies the layout based on the current setting.
        if user_settings.appearance.compact > 0:
            self.artist_label.set_visible(False)
            self.icon.set_pixel_size(16)
        else:
            self.artist_label.set_visible(True)
            self.icon.set_pixel_size(24)

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

    def __init__(self, player: MprisPlayer):
        self.player = player
        
        self.icon = widgets.Icon(
            css_classes=["icon"],
            valign="center",
            pixel_size=24,
        )
        self.icon_label = widgets.Label(
            css_classes=["icon"],
            style="font-family: 'Material Symbols Outlined'; padding-left: 5px;",
            label="music_note"
        )
        
        self.icon_container = widgets.Box(
            css_classes=["icon_container"],
            valign="center",
            child=[self.icon, self.icon_label]
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

        super().__init__(
            vertical=False,
            spacing=5,
            halign="center",
            valign="center",
            homogeneous=False,
            vexpand=True,
            css_classes=[],
            child=[
                self.overlay,
                widgets.Box(
                    vertical=True,
                    spacing=0,
                    valign="center",
                    vexpand=True,
                    child=[
                        self.title_label, self.artist_label
                    ]
                )
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

    def update_layout(self):
        for player in self.__players:
            player.update_layout()

    def update_visibility(self):
        if self.main_box:
            self.main_box.set_visible(user_settings.appearance.media_widget)

    def __poll_players(self, _):
        current_players = len(mpris.players)
        if current_players != self.player_count:
            self.player_count = current_players
            self.__update_players()

    def __update_players(self):
        if self.main_box:
            # Check if there are any players
            has_players = len(mpris.players) > 0

            # The widget is visible if the setting is true AND there are players
            self.main_box.set_visible(user_settings.appearance.media_widget and has_players)
            
            last_child = self.main_box.get_last_child() # Corrected from self.box_widget
            while last_child:
                self.main_box.remove(last_child) # Corrected from self.box_widget
                last_child = self.main_box.get_last_child() # Corrected from self.box_widget
            
            self.__players = []

            for player_obj in mpris.players:
                self.__add_player(player_obj)

    def __add_player(self, obj: MprisPlayer) -> None:
        player = Player(obj)
        self.__players.append(player)
        
        player_button = widgets.Button(
            child=player,
            vexpand=True,
            halign="start",
            on_click=lambda _: obj.play_pause(),
            css_classes=["media"],
        )
        
        self.main_box.append(player_button) # Corrected from self.box_widget
        
    def widget(self):
        return widgets.Box(
            vertical=True,
            width_request=150,
            setup=self.__setup
        )
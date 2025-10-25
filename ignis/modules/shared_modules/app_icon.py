from ignis import widgets, utils
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty
from ignis.services.applications import ApplicationsService
import re

class AppIcon(widgets.Icon, BaseWidget):
    __gtype_name__ = "ExoAppIcon"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, **kwargs):
        widgets.Icon.__init__(self)
        self._app = None
        self._app_id: str = None
        self._name: str = None
        self.icon_path: str = None
        self.applications = ApplicationsService.get_default()

        self.get_icon()

        BaseWidget.__init__(self, **kwargs)


    def get_match_score(self, app, app_id: str) -> int:
        if not app or not app_id:
            return 0

        app_id_lower = app_id.lower()
        app_id_from_app_lower = app.id.lower()

        if app_id_lower == app_id_from_app_lower:
            return 400

        if app_id_lower in app_id_from_app_lower or app_id_from_app_lower in app_id_lower:
            return 300

        score = 0
        app_name_lower = ""
        if hasattr(app, 'name') and app.name:
            app_name_lower = app.name.lower()
            if app_id_lower == app_name_lower:
                score = 200

        app_id_tokens = set(re.split(r'[._-]', app_id_lower))
        
        app_id_from_app_tokens = set(re.split(r'[._-]', app_id_from_app_lower))
        id_intersection = app_id_tokens.intersection(app_id_from_app_tokens)
        id_union = app_id_tokens.union(app_id_from_app_tokens)
        if id_union:
            id_jaccard_score = int(100 * len(id_intersection) / len(id_union))
            score = max(score, id_jaccard_score)

        if app_name_lower:
            app_name_tokens = set(re.split(r'[._-]', app_name_lower))
            name_intersection = app_id_tokens.intersection(app_name_tokens)
            name_union = app_id_tokens.union(app_name_tokens)
            if name_union:
                name_jaccard_score = int(100 * len(name_intersection) / len(name_union))
                score = max(score, name_jaccard_score)

        return score

    def get_icon(self):
        FALLBACK_ICON = "application-x-executable-symbolic"

        if self._app:
            self.icon_path = self._app.icon or FALLBACK_ICON
        else:
            self.icon_path = None
            if self._app_id:
                self.icon_path = utils.get_app_icon_name(self._app_id) or None
            if not self.icon_path and self._name:
                self.icon_path = utils.get_app_icon_name(self._name) or None

            if not self.icon_path and (self._app_id or self._name):
                best_match = None
                highest_score = 0
                for app in self.applications.apps:
                    score = 0
                    if self._name:
                        score = self.get_match_score(app, self._name)
                    if self._app_id:
                        score = max(score, self.get_match_score(app, self._app_id))

                    if score > highest_score:
                        highest_score = score
                        best_match = app

                if best_match:
                    self.icon_path = best_match.icon if best_match.icon else FALLBACK_ICON

        self.set_image(self.icon_path or "application-x-executable-symbolic")

    @IgnisProperty
    def app(self):
        return self._app

    @app.setter
    def app(self, value) -> None:
        if value == self._app:
            return
        self._app = value
        self.get_icon()

    @IgnisProperty
    def app_id(self) -> str:
        return self._app_id

    @app_id.setter
    def app_id(self, value: str) -> None:
        if value == self._app_id:
            return
        self._app_id = value
        self.get_icon()

    @IgnisProperty
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if value == self._name:
            return
        self._name = value
        self.get_icon()

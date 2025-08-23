from ignis import widgets
from ignis.services.fetch import FetchService
from ..widgets import CategoryLabel
fetch = FetchService.get_default()

class AboutTab(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-body"],
            vertical=True,
            spacing=2,
            child=[
                CategoryLabel("About System"),
                widgets.Label(label=fetch.os_name),
                widgets.Label(label=fetch.os_id),
                widgets.Label(label=fetch.os_home_url),
                widgets.Label(label=fetch.current_desktop),
                widgets.Label(label=fetch.hostname),
                widgets.Label(label=(str(round(fetch.mem_total / 1024 / 1024, 2)) + " GiB")),
            ]
        )

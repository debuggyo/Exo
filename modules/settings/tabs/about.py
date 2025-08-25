from ignis import widgets
from ignis.services.fetch import FetchService
from ..widgets import CategoryLabel, SettingsRow
fetch = FetchService.get_default()

class SoftwareCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=2,
            child=[
                CategoryLabel("Software"),
                SettingsRow(title="Operating System", description=fetch.os_name),
                SettingsRow(title="Desktop", description=fetch.current_desktop),
                SettingsRow(title="Hostname", description=fetch.hostname.replace("\n", "")), # .replace("\n", "") makes it a single line because for some reason there was an empty line under.
            ]
        )
class HardwareCategory(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-category"],
            vertical=True,
            spacing=2,
            child=[
                CategoryLabel("Hardware"),
                SettingsRow(title="CPU", description=fetch.cpu),
                SettingsRow(title="RAM", description=(str(round(fetch.mem_total / 1024 / 1024, 2)) + " GiB")),
            ]
        )

class AboutTab(widgets.Box):
    def __init__(self):
        super().__init__(
            css_classes=["settings-body"],
            vertical=True,
            spacing=2,
            child=[
                SoftwareCategory(),
                HardwareCategory()
            ]
        )

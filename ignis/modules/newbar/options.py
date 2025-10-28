### Bar
monitor: int = 0

## Appearance
side: str = "top"					# ["top", "left", "right", "bottom"]
density: int = 0					# 0-3
floating: bool = False
centered: bool = False
background: str = "full"			# ["full", "areas", "gradient", "none"]

## Area Options
start_background: bool = True
center_background: bool = True
end_background: bool = True
start_module_bg: str = "separated"	# ["connected", "separated", "none"]
center_module_bg: str = "separated"	# ["connected", "separated", "none"]
end_module_bg: str = "separated"	# ["connected", "separated", "none"]
start_modules: list = []			# list of modules
center_modules: list = []			# list of modules
end_modules: list = []				# list of modules

## Autohide
autohide: bool = False
autohide_fullscreen: bool = False


### Clock
## Displays the current time and optionally date
show_date: bool = True
month_before_day: bool = True
military_time: bool = True


### Window
## Displays the icon/title/id of the active window
show_icon: bool = True
show_title: bool = True             # horizontal only
show_app_id: bool = True            # horizontal only
show_on_empty: bool = False
fixed_width: bool = True            # horizontal only


### Workspaces
## Displays your workspaces and shows the active one
workspace_style: str = "impulse"    # ["impulse", "dots"]
icons: bool = True                  # impulse only
names: bool = True                  # impulse only
numbers: bool = False               # impulse only
bigger_active: bool = False         # impulse only
fixed_workspaces: bool = True
fixed_workspace_amount: int = 5


### Media
## Displays the currently playing media with controls
show_labels: bool = True
show_controls: bool = True
show_artwork: bool = True
show_when_no_player: bool = True


### Layout
## Displays an overview of windows in the active workspace (Niri only)
show_on_single: bool = True
show_icons: bool = True


### Recording Indicator
## Displays the status of Exo's built-in recorder
show_time: bool = True
show_always: bool = False


### Launcher
## A button that will open the launcher when clicked
icon_name: str = "apps"


### Action
## A button that can be used to run quick commands
icon_name: str = "apps"
left_click: str = ""
right_click: str = ""
middle_click: str = ""
scroll_up: str = ""
scroll_down: str = ""
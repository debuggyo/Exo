import datetime
from scripts import Wallpaper
from user_settings import user_settings


def auto_dark():
    options = user_settings.appearance.wallcolors.auto_dark
    if options.enabled:
        start_time = datetime.time(int(options.start_hour), int(options.start_min))
        end_time = datetime.time(int(options.end_hour), int(options.end_min))
        current_time = datetime.datetime.now().time()

        dark_mode = user_settings.appearance.wallcolors.dark_mode

        if start_time < end_time:
            if start_time <= current_time <= end_time:
                if not dark_mode:
                    Wallpaper.setDarkMode(True)
            else:
                if dark_mode:
                    Wallpaper.setDarkMode(False)
        else:
            if current_time >= start_time or current_time <= end_time:
                if not dark_mode:
                    Wallpaper.setDarkMode(True)
            else:
                if dark_mode:
                    Wallpaper.setDarkMode(False)


def setAutoDark(active):
    user_settings.appearance.wallcolors.auto_dark.set_enabled(active)
    auto_dark()

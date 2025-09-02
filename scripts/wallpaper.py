import os
import asyncio
from ignis import utils
from user_settings import user_settings
from ignis.css_manager import CssManager
css_manager = CssManager.get_default()
from .send_notification import send_notification

class Wallpaper:
    def setWall(path):
        schemes = ["content", "expressive", "fidelity", "fruit-salad", "monochrome", "neutral", "rainbow", "tonal-spot"]
        colorScheme = user_settings.appearance.wallcolors.color_scheme
        if user_settings.appearance.wallcolors.dark_mode:
            mode = "dark"
        else:
            mode = "light"

        if colorScheme in schemes:
            print(f"Color Scheme: {colorScheme}")
            print(f"Wallpaper: {path}")
            asyncio.create_task(utils.exec_sh_async(f"matugen image -t scheme-{colorScheme} '{path}' -m '{mode}'"))
        else:
            asyncio.create_task(utils.exec_sh_async(f"matugen image -t scheme-tonal-spot '{path}' -m '{mode}'"))

        send_notification("Wallpaper Set!", str(os.path.basename(path)))
        user_settings.appearance.wallcolors.set_wallpaper_path(path)
        utils.Timeout(ms=3000, target=lambda: css_manager.reload_all_css())

    def setColors(colorScheme):
        schemes = ["content", "expressive", "fidelity", "fruit-salad", "monochrome", "neutral", "rainbow", "tonal-spot"]
        path = user_settings.appearance.wallcolors.wallpaper_path
        if user_settings.appearance.wallcolors.dark_mode:
            mode = "dark"
        else:
            mode = "light"

        if colorScheme in schemes:
            asyncio.create_task(utils.exec_sh_async(f"matugen image -t scheme-{colorScheme} '{path}' -m '{mode}'"))
        else:
            asyncio.create_task(utils.exec_sh_async(f"matugen image -t scheme-tonal-spot '{path}' -m '{mode}'"))

        user_settings.appearance.wallcolors.set_color_scheme(colorScheme)
        utils.Timeout(ms=3000, target=lambda: css_manager.reload_all_css())


    def setDarkMode(active):
        schemes = ["content", "expressive", "fidelity", "fruit-salad", "monochrome", "neutral", "rainbow", "tonal-spot"]
        colorScheme = user_settings.appearance.wallcolors.color_scheme
        path = user_settings.appearance.wallcolors.wallpaper_path
        if active:
            mode = "dark"
        else:
            mode = "light"

        if colorScheme in schemes:
            asyncio.create_task(utils.exec_sh_async(f"matugen image -t scheme-{colorScheme} '{path}' -m '{mode}'"))
            asyncio.create_task(utils.exec_sh_async(f"gsettings set org.gnome.desktop.interface color-scheme 'prefer-{mode}'"))
        else:
            asyncio.create_task(utils.exec_sh_async(f"matugen image -t scheme-tonal-spot '{path}' -m '{mode}'"))
            asyncio.create_task(utils.exec_sh_async(f"gsettings set org.gnome.desktop.interface color-scheme 'prefer-{mode}'"))

        user_settings.appearance.wallcolors.set_dark_mode(active)
        utils.Timeout(ms=2000, target=lambda: css_manager.reload_all_css())

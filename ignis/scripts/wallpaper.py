import os
import asyncio
import json
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
            asyncio.create_task(utils.exec_sh_async(f"matugen image -t scheme-{colorScheme} '{path}' -m '{mode}'"))
        else:
            asyncio.create_task(utils.exec_sh_async(f"matugen image -t scheme-tonal-spot '{path}' -m '{mode}'"))

        send_notification("Wallpaper Set!", str(os.path.basename(path)))
        user_settings.appearance.wallcolors.set_wallpaper_path(path)
        Wallpaper.generatePreviews()
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
        Wallpaper.generatePreviews()
        utils.Timeout(ms=2000, target=lambda: css_manager.reload_all_css())

    def generatePreviews():
        async def do_generate():
            schemes = ["content", "expressive", "fidelity", "fruit-salad", "monochrome", "neutral", "rainbow", "tonal-spot"]
            path = user_settings.appearance.wallcolors.wallpaper_path
            if not path or not os.path.exists(path):
                return

            current_mode = "dark" if user_settings.appearance.wallcolors.dark_mode else "light"
            current_scheme = user_settings.appearance.wallcolors.color_scheme

            scss_content = ""

            tasks_palette = []
            for scheme in schemes:
                command = f"matugen image -t scheme-{scheme} '{path}' -m {current_mode} --json hex --dry-run"
                tasks_palette.append(utils.exec_sh_async(command))

            results_palette = await asyncio.gather(*tasks_palette)

            for i, result in enumerate(results_palette):
                scheme = schemes[i]
                if result.stdout:
                    try:
                        data = json.loads(result.stdout)
                        if current_mode in data.get('colors', {}):
                            for color_name, color_value in data['colors'][current_mode].items():
                                variable_name = f"palette-{scheme}-{color_name.replace('_', '-')}"
                                scss_content += '$' + variable_name + ': ' + color_value + ';\n'
                    except json.JSONDecodeError as e:
                        stderr = result.stderr if result.stderr else ''
                        print(f"Failed to decode json for palette {scheme}: {stderr} | {e}")
                        pass

            tasks_theme = []
            for mode in ["light", "dark"]:
                command = f"matugen image -t scheme-{current_scheme} '{path}' -m {mode} --json hex --dry-run"
                tasks_theme.append(utils.exec_sh_async(command))

            results_theme = await asyncio.gather(*tasks_theme)

            for i, result in enumerate(results_theme):
                mode = ["light", "dark"][i]
                if result.stdout:
                    try:
                        data = json.loads(result.stdout)
                        if mode in data.get('colors', {}):
                            for color_name, color_value in data['colors'][mode].items():
                                variable_name = f"theme-{mode}-{color_name.replace('_', '-')}"
                                scss_content += '$' + variable_name + ': ' + color_value + ';\n'
                    except json.JSONDecodeError as e:
                        stderr = result.stderr if result.stderr else ''
                        print(f"Failed to decode json for theme preview {mode}: {stderr} | {e}")
                        pass

            scss_file_path = os.path.expanduser("~/.config/ignis/styles/preview-colors.scss")
            os.makedirs(os.path.dirname(scss_file_path), exist_ok=True)
            with open(scss_file_path, "w") as f:
                f.write(scss_content)

        asyncio.create_task(do_generate())

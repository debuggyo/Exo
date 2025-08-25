import os
from ignis import utils
from user_settings import user_settings
from ignis.css_manager import CssManager, CssInfoPath, CssInfoNotFoundError
css_manager = CssManager.get_default()

def apply_bar_css():
    # A list of all possible CSS names this function can apply.
    # This allows us to clear all of them before applying new ones.
    all_possible_css_names = [
        "hug", "extrapadding", "roundbar", "floating",
        "full", "separated", "compact", "compactplus",
        "ultracompact", "vertical"
    ]

    # Remove all possible CSS files, and handle the error if a file is not found.
    for name in all_possible_css_names:
        try:
            css_manager.remove_css(name)
        except CssInfoNotFoundError:
            # This is expected behavior if the CSS file wasn't applied before.
            # We can safely ignore this error and continue.
            pass

    side = user_settings.appearance.bar_side
    vertical = user_settings.appearance.vertical
    separation = user_settings.appearance.bar_separation
    floating = user_settings.appearance.bar_floating
    centered = user_settings.appearance.bar_centered
    compact_mode = user_settings.appearance.compact

    # Bar Connection
    if floating:
        css_manager.apply_css(CssInfoPath(
            name="floating",
            path=os.path.expanduser("~/.config/ignis/styles/barconnection/floating.scss"),
            compiler_function=lambda path: utils.sass_compile(path=path),
        ))
    else:
        topmargin = leftmargin = rightmargin = bottommargin = 0
        css_manager.apply_css(CssInfoPath(
            name="hug",
            path=os.path.expanduser("~/.config/ignis/styles/barconnection/hug.scss"),
            compiler_function=lambda path: utils.sass_compile(path=path),
        ))
        if not centered:
            css_manager.apply_css(CssInfoPath(
                name="extrapadding",
                path=os.path.expanduser("~/.config/ignis/styles/barstyles/extrapadding.scss"),
                compiler_function=lambda path: utils.sass_compile(path=path),
            ))
        elif centered:
            css_manager.apply_css(CssInfoPath(
                name="roundbar",
                path=os.path.expanduser("~/.config/ignis/styles/barstyles/roundbar.scss"),
                compiler_function=lambda path: utils.sass_compile(path=path),
            ))
    
    # Bar Style
    if separation:
        css_manager.apply_css(CssInfoPath(
            name="separated",
            path=os.path.expanduser("~/.config/ignis/styles/barstyles/separated.scss"),
            compiler_function=lambda path: utils.sass_compile(path=path),
        ))
    else:
        css_manager.apply_css(CssInfoPath(
            name="full",
            path=os.path.expanduser("~/.config/ignis/styles/barstyles/full.scss"),
            compiler_function=lambda path: utils.sass_compile(path=path),
        ))

    # determine height
    if compact_mode == 1:
        css_manager.apply_css(CssInfoPath(
            name="compact",
            path=os.path.expanduser("~/.config/ignis/styles/compactmodes/compact.scss"),
            compiler_function=lambda path: utils.sass_compile(path=path),
        ))
    if compact_mode in (2, 3):
        css_manager.apply_css(CssInfoPath(
            name="compactplus",
            path=os.path.expanduser("~/.config/ignis/styles/compactmodes/compactplus.scss"),
            compiler_function=lambda path: utils.sass_compile(path=path),
        ))
        if compact_mode == 3:
            css_manager.apply_css(CssInfoPath(
                name="ultracompact",
                path=os.path.expanduser("~/.config/ignis/styles/compactmodes/ultracompact.scss"),
                compiler_function=lambda path: utils.sass_compile(path=path),
            ))

    # vertical CSS
    if vertical:
        css_manager.apply_css(CssInfoPath(
            name="vertical",
            path=os.path.expanduser("~/.config/ignis/styles/barstyles/vertical.scss"),
            compiler_function=lambda path: utils.sass_compile(path=path),
        ))
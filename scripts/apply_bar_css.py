from user_settings import user_settings

def apply_bar_css(window):
    if not window:
        return

    side = user_settings.interface.bar.side
    vertical = user_settings.interface.bar.vertical
    separation = user_settings.interface.bar.separation
    floating = user_settings.interface.bar.floating
    centered = user_settings.interface.bar.centered
    compact_mode = user_settings.interface.bar.density

    all_possible_classes = {
        "hug", "extrapadding", "round", "floating", "full",
        "separated", "compact", "compact-plus", "ultracompact",
        "vertical", "top", "bottom", "left", "right"
    }

    for css_class in all_possible_classes:
        window.remove_css_class(css_class)
    
    if floating:
        window.add_css_class("floating")
    else:
        window.add_css_class("hug")
        if not centered:
            window.add_css_class("extrapadding")
        elif centered:
            window.add_css_class("round")
    
    if separation:
        window.add_css_class("separated")
    else:
        window.add_css_class("full")

    if compact_mode == 1:
        window.add_css_class("compact")
    elif compact_mode == 2:
        window.add_css_class("compact-plus")
    elif compact_mode == 3:
        window.add_css_class("ultracompact")

    if vertical:
        window.add_css_class("vertical")

    window.add_css_class(side)
from ignis import widgets

class Slider():
    @staticmethod
    def slider(
        min: float,
        max: float,
        value: float,
        vertical: bool = False,
        step: float = 1.0,
        icon: str = None,
        on_change: callable = None,
        **kwargs
    ):
        icon = widgets.Label(css_classes=["m3-slider-icon"], label=icon, valign="center") if icon else None
        return widgets.Box(
            css_classes=["m3-slider"],
            halign="fill",
            hexpand=True,
            child=[
                icon,
                widgets.Scale(
                    min=min,
                    max=max,
                    value=value,
                    step=step,
                    vertical=vertical,
                    halign="fill",
                    hexpand=True,
                    on_change=on_change,
                    draw_value=True,
                    value_pos="top",
                )
            ],
            **kwargs
        )

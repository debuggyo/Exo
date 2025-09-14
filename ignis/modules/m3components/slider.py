from ignis import widgets

class Slider():
    @staticmethod
    def slider(
        min: float,
        max: float,
        value: float,
        vertical: bool = False,
        step: float = 1.0,
        **kwargs
    ):
        return widgets.Scale(
            css_classes=["m3-slider"],
            min=min,
            max=max,
            value=value,
            step=step,
            vertical=vertical,
            **kwargs
        )

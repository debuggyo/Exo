from gi.repository import Gtk, Pango, PangoCairo
from ignis.base_widget import BaseWidget
from ignis.gobject import IgnisProperty


class Icon(Gtk.DrawingArea, BaseWidget):
    __gtype_name__ = "M3Icon"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, icon: str = "question_mark", size: int = 16, **kwargs):
        Gtk.DrawingArea.__init__(self)
        BaseWidget.__init__(self, **kwargs)
        self._icon: str = icon
        self._size: int = size

        self.add_css_class("m3-icon")
        self.set_size_request(self._size, self._size)
        self.set_draw_func(self._draw_icon)

    def _draw_icon(self, area, cr, width, height):
        style_context = self.get_style_context()
        color = style_context.get_color()
        cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)

        layout = self.create_pango_layout(self._icon)

        font_desc = Pango.FontDescription()
        font_desc.set_size(self._size * Pango.SCALE)
        layout.set_font_description(font_desc)

        layout_width, layout_height = layout.get_pixel_size()

        x = (width - layout_width) / 2
        y = (height - layout_height) / 2

        cr.move_to(x, y)
        PangoCairo.show_layout(cr, layout)

    @IgnisProperty
    def icon(self) -> str:
        return self._icon

    @icon.setter
    def icon(self, value: str):
        if self._icon == value:
            return
        self._icon = value
        self.queue_draw()

    @IgnisProperty
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int):
        if self._size == value:
            return
        self._size = value
        self.set_size_request(self._size, self._size)
        self.queue_draw()

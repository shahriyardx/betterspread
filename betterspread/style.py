from dataclasses import dataclass, field

from gspread_formatting import CellFormat, Color, TextFormat


@dataclass
class Style:
    """A convenience wrapper around :class:`gspread_formatting.CellFormat`.

    You can either supply individual style properties (colours, alignment,
    text decorations) and let :class:`Style` build the underlying
    :class:`CellFormat` for you, or pass a pre-built *raw* :class:`CellFormat`
    directly.

    When *raw* is provided the individual keyword arguments are ignored.

    Examples::

        # Build from individual properties
        style = Style(bg_color="#ffff00", bold=True)

        # Wrap an existing CellFormat
        from gspread_formatting import CellFormat, Color
        style = Style(raw=CellFormat(backgroundColor=Color(1, 0, 0)))

    Attributes:
        bg_color: Background colour as a hex string (e.g. ``"#ffffff"``).
        text_color: Foreground (text) colour as a hex string.
        horizontal_align: One of ``"left"``, ``"center"``, or ``"right"``.
        vertical_align: One of ``"top"``, ``"middle"``, or ``"bottom"``.
        bold: Whether the text is bold.
        italic: Whether the text is italic.
        strikethrough: Whether the text has a strikethrough decoration.
        raw: The compiled :class:`gspread_formatting.CellFormat` object.
            Populated automatically in :meth:`__post_init__` when not supplied
            by the caller.
    """

    bg_color: str = "#ffffff"
    text_color: str = "#000000"
    horizontal_align: str = "left"
    vertical_align: str = "middle"
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    raw: CellFormat | None = field(default=None)

    def __post_init__(self) -> None:
        if self.raw is None:
            bg = Color.fromHex(self.bg_color)
            fg = Color.fromHex(self.text_color)

            self.raw = CellFormat(
                backgroundColor=bg,
                textFormat=TextFormat(
                    foregroundColor=fg,
                    bold=self.bold,
                    italic=self.italic,
                    strikethrough=self.strikethrough,
                ),
                horizontalAlignment=self.horizontal_align.upper(),
                verticalAlignment=self.vertical_align.upper(),
            )

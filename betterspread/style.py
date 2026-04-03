from gspread_formatting import CellFormat, Color, TextFormat


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
            Always populated after construction.
    """

    raw: CellFormat

    def __init__(
        self,
        bg_color: str = "#ffffff",
        text_color: str = "#000000",
        horizontal_align: str = "left",
        vertical_align: str = "middle",
        bold: bool = False,
        italic: bool = False,
        strikethrough: bool = False,
        raw: CellFormat | None = None,
    ) -> None:
        self.bg_color = bg_color
        self.text_color = text_color
        self.horizontal_align = horizontal_align
        self.vertical_align = vertical_align
        self.bold = bold
        self.italic = italic
        self.strikethrough = strikethrough

        if raw is not None:
            self.raw = raw
        else:
            bg = Color.fromHex(bg_color)
            fg = Color.fromHex(text_color)

            self.raw = CellFormat(
                backgroundColor=bg,
                textFormat=TextFormat(
                    foregroundColor=fg,
                    bold=bold,
                    italic=italic,
                    strikethrough=strikethrough,
                ),
                horizontalAlignment=horizontal_align.upper(),
                verticalAlignment=vertical_align.upper(),
            )

    def __repr__(self) -> str:
        return (
            f"Style(bg_color={self.bg_color!r}, text_color={self.text_color!r}, "
            f"bold={self.bold}, italic={self.italic}, "
            f"strikethrough={self.strikethrough})"
        )

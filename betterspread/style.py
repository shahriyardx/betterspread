from gspread_formatting import CellFormat, Color, TextFormat


class Style:
    """A convenience wrapper around :class:`gspread_formatting.CellFormat`.

    You can either supply individual style properties (colours, alignment,
    text decorations) and let :class:`Style` build the underlying
    :class:`CellFormat` for you, or pass a pre-built *raw* :class:`CellFormat`
    directly.

    Only the properties you actually pass are written to the cell.  Anything
    left as ``None`` is omitted from the compiled :class:`CellFormat`, so
    applying a :class:`Style` never clobbers formatting you did not set (e.g.
    ``Style(bold=True)`` leaves the existing background colour untouched).

    When *raw* is provided the individual keyword arguments are ignored.

    Examples::

        # Build from individual properties (only bold is changed)
        style = Style(bold=True)

        # Wrap an existing CellFormat
        from gspread_formatting import CellFormat, Color
        style = Style(raw=CellFormat(backgroundColor=Color(1, 0, 0)))

    Attributes:
        bg_color: Background colour as a hex string (e.g. ``"#ffffff"``), or
            ``None`` to leave it unchanged.
        text_color: Foreground (text) colour as a hex string, or ``None``.
        horizontal_align: One of ``"left"``, ``"center"``, or ``"right"``, or
            ``None``.
        vertical_align: One of ``"top"``, ``"middle"``, or ``"bottom"``, or
            ``None``.
        bold: Whether the text is bold, or ``None`` to leave unchanged.
        italic: Whether the text is italic, or ``None`` to leave unchanged.
        strikethrough: Whether the text has a strikethrough decoration, or
            ``None`` to leave unchanged.
        raw: The compiled :class:`gspread_formatting.CellFormat` object.
            Always populated after construction.
    """

    raw: CellFormat

    def __init__(
        self,
        bg_color: str | None = None,
        text_color: str | None = None,
        horizontal_align: str | None = None,
        vertical_align: str | None = None,
        bold: bool | None = None,
        italic: bool | None = None,
        strikethrough: bool | None = None,
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
            return

        text_kwargs: dict = {}
        if text_color is not None:
            text_kwargs["foregroundColor"] = Color.fromHex(text_color)
        if bold is not None:
            text_kwargs["bold"] = bold
        if italic is not None:
            text_kwargs["italic"] = italic
        if strikethrough is not None:
            text_kwargs["strikethrough"] = strikethrough

        fmt_kwargs: dict = {}
        if bg_color is not None:
            fmt_kwargs["backgroundColor"] = Color.fromHex(bg_color)
        if horizontal_align is not None:
            fmt_kwargs["horizontalAlignment"] = horizontal_align.upper()
        if vertical_align is not None:
            fmt_kwargs["verticalAlignment"] = vertical_align.upper()
        if text_kwargs:
            fmt_kwargs["textFormat"] = TextFormat(**text_kwargs)

        self.raw = CellFormat(**fmt_kwargs)

    def __repr__(self) -> str:
        return (
            f"Style(bg_color={self.bg_color!r}, text_color={self.text_color!r}, "
            f"bold={self.bold}, italic={self.italic}, "
            f"strikethrough={self.strikethrough})"
        )

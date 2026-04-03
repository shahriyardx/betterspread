"""
Tests for betterspread.Style

Only covers what betterspread adds on top of gspread_formatting:
  - Building a CellFormat from simple keyword arguments
  - Passing a pre-built CellFormat through unchanged (raw passthrough)
"""

from gspread_formatting import CellFormat, Color

from betterspread.style import Style


class TestStyleBuildsFromKeywords:
    def test_creates_a_cell_format(self):
        assert isinstance(Style().raw, CellFormat)

    def test_bold(self):
        tf = Style(bold=True).raw.textFormat
        assert tf is not None
        assert tf.bold is True

    def test_italic(self):
        tf = Style(italic=True).raw.textFormat
        assert tf is not None
        assert tf.italic is True

    def test_strikethrough(self):
        tf = Style(strikethrough=True).raw.textFormat
        assert tf is not None
        assert tf.strikethrough is True

    def test_flags_default_to_false(self):
        tf = Style().raw.textFormat
        assert tf is not None
        assert tf.bold is False
        assert tf.italic is False
        assert tf.strikethrough is False

    def test_horizontal_align_is_uppercased(self):
        assert Style(horizontal_align="center").raw.horizontalAlignment == "CENTER"

    def test_vertical_align_is_uppercased(self):
        assert Style(vertical_align="top").raw.verticalAlignment == "TOP"

    def test_default_horizontal_align(self):
        assert Style().raw.horizontalAlignment == "LEFT"

    def test_default_vertical_align(self):
        assert Style().raw.verticalAlignment == "MIDDLE"

    def test_background_color_is_set(self):
        assert Style(bg_color="#ff0000").raw.backgroundColor is not None

    def test_text_color_is_set(self):
        tf = Style(text_color="#0000ff").raw.textFormat
        assert tf is not None
        assert tf.foregroundColor is not None

    def test_two_different_bg_colors_differ(self):
        red = Style(bg_color="#ff0000").raw.backgroundColor
        blue = Style(bg_color="#0000ff").raw.backgroundColor
        assert red != blue


class TestStyleRawPassthrough:
    def test_raw_is_returned_unchanged(self):
        fmt = CellFormat(backgroundColor=Color(1, 0, 0))
        assert Style(raw=fmt).raw is fmt

    def test_raw_takes_priority_over_other_kwargs(self):
        fmt = CellFormat()
        style = Style(raw=fmt, bold=True, bg_color="#ff0000")
        assert style.raw is fmt

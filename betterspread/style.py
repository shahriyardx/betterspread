from dataclasses import dataclass

from gspread_formatting import CellFormat, Color, TextFormat


@dataclass
class Style:
    bg_color: str = "#ffffff"
    text_color: str = "#000000"
    horizontal_align: str = "left"
    vertical_align: str = "middle"
    raw: CellFormat = None
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False

    def __post_init__(self):
        if not self.raw:
            self.bg_color = Color.fromHex(self.bg_color)
            self.text_color = Color.fromHex(self.text_color)
            self.horizontal_align = self.horizontal_align.upper()
            self.vertical_align = self.vertical_align.upper()

            self.raw = CellFormat(
                backgroundColor=self.bg_color,
                textFormat=TextFormat(
                    foregroundColor=self.text_color,
                    bold=self.bold,
                    italic=self.italic,
                    strikethrough=self.strikethrough,
                ),
                horizontalAlignment=self.horizontal_align,
                verticalAlignment=self.vertical_align,
            )

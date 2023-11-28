from typing import TYPE_CHECKING, Any

from gspread.utils import ValueInputOption, ValueRenderOption
from gspread_formatting import format_cell_range

from .style import Style

if TYPE_CHECKING:
    from .row import Row
    from .tab import Tab


input_formats = {
    "raw": ValueInputOption.raw,
    "user_entered": ValueInputOption.user_entered,
}

render_formats = {
    "formatted": ValueRenderOption.formatted,
    "unformatted": ValueRenderOption.unformatted,
    "formula": ValueRenderOption.formula,
}


class Cell(str):
    def __new__(cls, value, tab: "Tab", label: str, row_index: int, row: "Row" = None):
        instance = super().__new__(cls, value)
        instance.tab = tab
        instance.label = label
        instance.row_index = row_index
        instance.row = row
        return instance

    def clear(self):
        if self.row:
            self.row[self.row.row_index - 1] = Cell(
                "", self.tab, label=self.label, row_index=self.row_index, row=self.row
            )
        self.tab.sheet.values_clear(f"{self.label}{self.row_index}")

    def update(
        self, value: Any, input_format: str = "raw", render_format: str = "formatted"
    ):
        if self.row:
            self.row[self.row_index - 1] = Cell(
                value,
                self.tab,
                label=self.label,
                row_index=self.row_index,
                row=self.row,
            )

        self.tab.update(
            f"{self.label}{self.row_index}",
            value,
            value_input_option=input_formats.get(input_format, "raw"),
            response_value_render_option=render_formats.get(render_format, "formatted"),
        )

    def style(self, obj: Style):
        style = obj.raw if isinstance(obj, Style) else obj
        format_cell_range(self.tab, f"{self.label}{self.row_index}", style)

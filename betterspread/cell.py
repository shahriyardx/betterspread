from typing import TYPE_CHECKING, Any

from gspread.utils import ValueInputOption, ValueRenderOption
from gspread_formatting import format_cell_range

from .style import Style
from .utils import run_in_executor

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
    def __new__(
        cls,
        value,
        tab: "Tab",
        label: str,
        row_index: int,
        cell_index: int = 0,
        row: "Row" = None,
    ):
        instance = super().__new__(cls, value)
        instance.tab = tab
        instance.label = label
        instance.row_index = row_index
        instance.cell_index = cell_index
        instance.row = row
        return instance

    async def clear(self):
        if self.row:
            self.row[self.cell_index] = Cell(
                "", self.tab, label=self.label, row_index=self.row_index, row=self.row
            )

        print(self.label, self.row_index)
        await run_in_executor(self.tab.batch_clear, [f"{self.label}{self.row_index}"])

    async def update(
        self, value: Any, input_format: str = "raw", render_format: str = "formatted"
    ):
        if self.row:
            self.row[self.cell_index] = Cell(
                value,
                self.tab,
                label=self.label,
                row_index=self.row_index,
                row=self.row,
            )

        await run_in_executor(
            self.tab.update,
            [[value]],
            f"{self.label}{self.row_index}",
            value_input_option=input_formats.get(input_format, "raw"),
            response_value_render_option=render_formats.get(render_format, "formatted"),
        )
        return Cell(
            value, self.tab, self.label, self.row_index, self.cell_index, self.row
        )

    async def style(self, obj: Style):
        style = obj.raw if isinstance(obj, Style) else obj
        await run_in_executor(
            format_cell_range, self.tab, f"{self.label}{self.row_index}", style
        )

    async def delete(self, shift: str = "left"):
        await self.tab.del_cell(f"{self.label}{self.row_index}", shift=shift)

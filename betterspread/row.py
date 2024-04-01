from typing import TYPE_CHECKING, List, Union

from gspread_formatting import CellFormat, format_cell_range

from .cell import Cell
from .style import Style
from .utils import get_location, run_in_executor

if TYPE_CHECKING:
    from .tab import Tab


class Row(list):
    def __init__(self, items, tab: "Tab", index: int):
        self.tab = tab
        self.row_index = index
        self.items = self.convert_to_cell(items)
        super().__init__(self.items)

    def convert_to_cell(self, items):
        def to_cell(item):
            i, value = item
            return Cell(value, self.tab, get_location(i + 1), self.row_index, i, self)

        converted: List[Cell] = list(map(to_cell, enumerate(items)))
        return converted

    async def clear(self) -> None:
        await run_in_executor(
            self.tab.batch_clear, [f"{self.row_index}:{self.row_index}"]
        )
        empty_items = self.convert_to_cell(list(map(lambda _: "", self.items)))
        self.items = empty_items
        super().__init__(empty_items)

    async def update(self, values: list, start: str = "A", *args, **kwargs):
        await run_in_executor(
            self.tab.update, [values], f"{start}{self.row_index}", *args, **kwargs
        )
        self.items = self.convert_to_cell(values)
        super().__init__(self.items)

    async def style(self, obj: Union[Style, CellFormat]):
        style = obj.raw if isinstance(obj, Style) else obj
        await run_in_executor(
            format_cell_range, self.tab, f"{self.row_index}:{self.row_index}", style
        )

    async def refetch(self):
        values = await run_in_executor(self.tab.values)
        row = values[self.row_index - 1]
        self.items = self.convert_to_cell(row)
        super().__init__(self.items)

    async def append_cell(self, value, *args, **kwargs):
        new_values = value if isinstance(value, list) else [value]
        new_data = [*self.items, *new_values]
        await self.update(new_data, *args, **kwargs)

    async def delete(self):
        await self.tab.del_row(self.row_index)

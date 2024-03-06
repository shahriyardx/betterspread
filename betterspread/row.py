from typing import TYPE_CHECKING, List, Union

from gspread_formatting import CellFormat, format_cell_range

from .cell import Cell
from .style import Style
from .utils import next_char, run_in_executor, to_range

if TYPE_CHECKING:
    from .tab import Tab


class Row(list):
    def __init__(self, items, tab: "Tab", index: int):
        self.tab = tab
        self.row_index = index
        self.items = self.convert_to_cell(items)
        self.range = to_range("A", len(self.items) - 1, index=self.row_index)
        super().__init__(self.items)

    def convert_to_cell(self, items):
        def to_cell(item):
            i, value = item
            return Cell(value, self.tab, next_char("A", i), self.row_index, i, self)

        converted: List[Cell] = list(map(to_cell, enumerate(items)))
        return converted

    async def clear(self) -> None:
        await run_in_executor(self.tab.batch_clear, [self.range])
        empty_items = self.convert_to_cell(list(map(lambda _: "", self.items)))
        self.items = empty_items
        super().__init__(empty_items)

    async def update(self, values: list, *args, **kwargs):
        self.range = to_range("A", len(values) - 1, index=self.row_index)
        await run_in_executor(self.tab.update, self.range, [values], *args, **kwargs)
        self.items = self.convert_to_cell(values)
        super().__init__(self.items)

    async def style(self, obj: Union[Style, CellFormat]):
        style = obj.raw if isinstance(obj, Style) else obj
        await run_in_executor(format_cell_range, self.tab, self.range, style)

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

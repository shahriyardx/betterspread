from typing import TYPE_CHECKING, List, Union

from gspread_formatting import format_cell_range, CellFormat

from .cell import Cell
from .style import Style
from .utils import next_char, to_range

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
            return Cell(value, self.tab, next_char("A", i), self.row_index, self)

        converted: List[Cell] = list(map(to_cell, enumerate(items)))
        return converted

    def clear(self) -> None:
        self.tab.sheet.values_clear(self.range)
        self.items = []
        super().__init__([])

    def update(self, values: list, *args, **kwargs):
        self.range = to_range("A", len(values) - 1, index=self.row_index)
        self.tab.update(self.range, [values], *args, **kwargs)
        self.items = self.convert_to_cell(values)
        super().__init__(self.items)

    def style(self, obj: Union[Style, CellFormat]):
        style = obj.raw if isinstance(obj, Style) else obj
        format_cell_range(self.tab, self.range, style)

    def refetch(self):
        values = self.tab.values()
        row = values[self.row_index - 1]
        self.items = self.convert_to_cell(row)
        super().__init__(self.items)

    def append_cell(self, value, *args, **kwargs):
        new_values = value if isinstance(value, list) else [value]
        new_data = [*self.items, *new_values]
        self.update(new_data, *args, **kwargs)

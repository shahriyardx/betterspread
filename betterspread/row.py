from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from gspread_formatting import format_cell_range

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
        new_items = self.convert_to_cell([list(map(lambda _x: "", self.items))])
        self.tab.update(
            self.range,
            new_items,
        )
        super().__init__(new_items)

    def update(self, values: list, **kwargs):
        self.range = to_range("A", len(values) - 1, index=self.row_index)
        self.tab.update(self.range, [values], **kwargs)
        self.items = self.convert_to_cell(values)
        super().__init__(self.items)

    def style(self, obj: Style):
        format_cell_range(self.tab, self.range, obj)

    def refetch(self):
        values = self.tab.values()
        row = values[self.row_index - 1]
        self.items = self.convert_to_cell(row)
        super().__init__(self.items)

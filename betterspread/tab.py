from dataclasses import dataclass
from typing import List

from gspread import Worksheet
from gspread.utils import ValueRenderOption

from .cell import Cell
from .row import Row

render_formats = {
    "formatted": ValueRenderOption.formatted,
    "unformatted": ValueRenderOption.unformatted,
    "formula": ValueRenderOption.formula,
}


@dataclass
class Tab(Worksheet):
    def __init__(self, sheet, *args, **kwargs):
        self.sheet = sheet
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Tab title='{self.title}' id={self.id}>"

    def values(self, **kwargs) -> List[Row]:
        rows = self.get_values(**kwargs)

        for i, row in enumerate(rows):
            rows[i] = Row(row, tab=self, index=i + 1)

        return rows

    def get_row(self, serial_no: int):
        values = self.values()
        return values[serial_no - 1]

    def get_cell(self, cell_name: str, render_option: str = "formatted", **kwargs):
        data = self.get(
            cell_name,
            value_render_option=render_formats.get(render_option, "formatted"),
            **kwargs,
        )[0][0]

        return Cell(
            data, tab=self, label=cell_name[0], row_index=int(cell_name[1:]), cell_index=0, row=None
        )

    def append(self, data: list):
        self.append_row(data)

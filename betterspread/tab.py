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

    def get_cell(
        self, cell_name: str, render_option: str = "formatted", **kwargs
    ):
        resp = self.get(
            cell_name,
            value_render_option=render_formats.get(render_option, "formatted"),
            **kwargs,
        )

        try:
            data = resp[0][0]
        except IndexError:
            data = ""

        return Cell(
            data,
            tab=self,
            label=cell_name[0],
            row_index=int(cell_name[1:]),
            cell_index=0,
            row=None,
        )

    def append(self, data: list, get_row: bool = False):
        self.append_row(data)

        if get_row:
            values = self.values()
            return values[-1]

    def del_row(self, start: int, end: int = None):
        self.delete_rows(start_index=start, end_index=end or start)

    def del_cell(self, start: str, end: str = None, shift: str = "up"):
        [start_col_name, *start_row_indexs] = list(start)
        if end:
            [end_col_name, *end_row_indexs] = list(end)
        else:
            end_col_name = start_col_name
            end_row_indexs = start_row_indexs

        start_row_index = int("".join(start_row_indexs)) - 1
        end_row_index = int("".join(end_row_indexs))

        start_col_index = ord(start_col_name) - 65
        end_col_index = ord(end_col_name) - 64

        sheet_id = self._properties["sheetId"]
        requests = [
            {
                "deleteRange": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": start_row_index,
                        "endRowIndex": end_row_index,
                        "startColumnIndex": start_col_index,
                        "endColumnIndex": end_col_index,
                    },
                    "shiftDimension": "COLUMNS" if shift == "left" else "ROWS",
                }
            }
        ]

        self.sheet.batch_update({"requests": requests})

from gspread import Worksheet

from .cell import Cell
from .row import Row
from .utils import col_label_to_index, parse_cell_name, render_formats, run_in_executor


class Tab(Worksheet):
    """A single worksheet tab, extending :class:`gspread.Worksheet` with async helpers."""

    def __init__(self, sheet, *args, **kwargs) -> None:
        self.sheet = sheet
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<Tab title='{self.title}' id={self.id}>"

    async def values(self, **kwargs) -> list[Row]:
        """Return all rows in the sheet as a list of :class:`Row` objects."""
        rows: list = await run_in_executor(self.get_values, **kwargs)

        for i, row in enumerate(rows):
            rows[i] = Row(row, tab=self, index=i + 1)

        return rows

    async def get_row(self, serial_no: int) -> Row:
        """Return the row at the given 1-based *serial_no*."""
        all_rows = await self.values()
        return all_rows[serial_no - 1]

    async def get_cell(
        self,
        cell_name: str,
        render_option: str = "formatted",
        **kwargs,
    ) -> Cell:
        """Fetch a single cell by its address (e.g. ``"A1"``, ``"AA15"``).

        Args:
            cell_name: A standard A1-notation cell address.  Both single- and
                multi-letter column labels are supported.
            render_option: One of ``"formatted"``, ``"unformatted"``, or
                ``"formula"``.

        Returns:
            A :class:`Cell` whose string value is the current cell content.
        """
        resp = await run_in_executor(
            self.get,
            cell_name,
            value_render_option=render_formats.get(
                render_option, render_formats["formatted"]
            ),
            **kwargs,
        )

        try:
            data = resp[0][0]
        except IndexError:
            data = ""

        col_label, row_idx = parse_cell_name(cell_name)
        cell_idx = col_label_to_index(col_label)

        return Cell(
            data,
            tab=self,
            label=col_label,
            row_index=row_idx,
            cell_index=cell_idx,
            row=None,
        )

    async def append(self, data: list, get_row: bool = False) -> Row | None:
        """Append *data* as a new row at the bottom of the sheet.

        Args:
            data: A flat list of values to write.
            get_row: When ``True``, refetch all rows and return the newly
                appended :class:`Row`.

        Returns:
            The appended :class:`Row` if *get_row* is ``True``, else ``None``.
        """
        await run_in_executor(self.append_row, data)

        if get_row:
            all_rows = await self.values()
            return all_rows[-1]

        return None

    async def del_row(self, start: int, end: int | None = None) -> None:
        """Delete one or more rows by their 1-based indices.

        Args:
            start: First row to delete (1-based, inclusive).
            end: Last row to delete (1-based, inclusive).  Defaults to *start*
                so that a single row is deleted when *end* is omitted.
        """
        await run_in_executor(
            self.delete_rows,
            start_index=start,
            end_index=end if end is not None else start,
        )

    async def del_cell(
        self,
        start: str,
        end: str | None = None,
        shift: str = "up",
    ) -> None:
        """Delete a cell or rectangular range of cells.

        Args:
            start: Top-left cell address in A1 notation (e.g. ``"B2"``).
            end: Bottom-right cell address.  Defaults to *start* for a single
                cell.
            shift: Direction to shift remaining cells after deletion.
                Use ``"left"`` to shift columns left, or ``"up"`` (default) to
                shift rows up.
        """
        start_col, start_row = parse_cell_name(start)

        if end:
            end_col, end_row = parse_cell_name(end)
        else:
            end_col, end_row = start_col, start_row

        start_col_index = col_label_to_index(start_col)
        end_col_index = col_label_to_index(end_col) + 1  # exclusive upper bound

        start_row_index = start_row - 1  # convert to 0-based
        end_row_index = end_row  # already exclusive in the Sheets API

        sheet_id = self._properties["sheetId"]  # noqa: SLF001
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

        await run_in_executor(self.sheet.batch_update, {"requests": requests})

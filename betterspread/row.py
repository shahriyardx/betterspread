from typing import TYPE_CHECKING

from gspread_formatting import CellFormat, format_cell_range

from .cell import Cell
from .style import Style
from .utils import get_location, run_in_executor

if TYPE_CHECKING:
    from .tab import Tab


class Row(list):
    """A spreadsheet row represented as a :class:`list` of :class:`Cell` objects.

    Mutating operations (``update``, ``clear``, ``style``, ``delete``,
    ``append_cell``) are async and write through to the remote spreadsheet.

    Attributes:
        tab: The :class:`~betterspread.tab.Tab` this row belongs to.
        row_index: The 1-based row number within the sheet.
        items: The list of :class:`Cell` objects in their current state.
    """

    def __init__(self, items: list, tab: "Tab", index: int) -> None:
        self.tab = tab
        self.row_index = index
        self.items = self._to_cells(items)
        super().__init__(self.items)

    def __repr__(self) -> str:
        return f"<Row {self.row_index} {list(self)!r}>"

    def _to_cells(self, items: list) -> list[Cell]:
        """Convert a flat list of raw values into :class:`Cell` objects."""

        def _make_cell(enum_item: tuple[int, object]) -> Cell:
            i, value = enum_item
            return Cell(
                value,
                self.tab,
                get_location(i + 1),
                self.row_index,
                i,
                self,
            )

        return list(map(_make_cell, enumerate(items)))

    async def clear(self) -> None:  # type: ignore[override]
        """Clear all values in this row in the remote spreadsheet."""
        await run_in_executor(
            self.tab.batch_clear, [f"{self.row_index}:{self.row_index}"]
        )
        empty_items = self._to_cells([""] * len(self.items))
        self.items = empty_items
        super().__init__(empty_items)

    async def update(
        self,
        values: list,
        start: str = "A",
        *args,
        **kwargs,
    ) -> None:
        """Overwrite the row's values starting from the *start* column.

        Args:
            values: A flat list of new values to write.
            start: Column label of the first cell to write (default ``"A"``).
        """
        await run_in_executor(
            self.tab.update, [values], f"{start}{self.row_index}", *args, **kwargs
        )
        updated_items = self._to_cells(values)
        self.items = updated_items
        super().__init__(updated_items)

    async def style(self, obj: Style | CellFormat) -> None:
        """Apply *obj* formatting to every cell in this row.

        Args:
            obj: A :class:`~betterspread.style.Style` wrapper or a raw
                :class:`gspread_formatting.CellFormat` object.
        """
        fmt = obj.raw if isinstance(obj, Style) else obj
        await run_in_executor(
            format_cell_range,
            self.tab,
            f"{self.row_index}:{self.row_index}",
            fmt,
        )

    async def refetch(self) -> None:
        """Reload this row's values from the remote spreadsheet."""
        all_rows = await self.tab.values()
        raw_row = all_rows[self.row_index - 1]
        # raw_row is already a Row; extract the underlying string values
        refreshed = self._to_cells([str(cell) for cell in raw_row])
        self.items = refreshed
        super().__init__(refreshed)

    async def append_cell(self, value, *args, **kwargs) -> None:
        """Append one or more values to the end of this row.

        Args:
            value: A single value or a list of values to append.
        """
        new_values = value if isinstance(value, list) else [value]
        combined = [str(cell) for cell in self.items] + new_values
        await self.update(combined, *args, **kwargs)

    async def delete(self) -> None:
        """Delete this entire row from the remote spreadsheet."""
        await self.tab.del_row(self.row_index)

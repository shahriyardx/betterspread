from typing import TYPE_CHECKING, Any

from gspread_formatting import format_cell_range

from .style import Style
from .utils import input_formats, render_formats, run_in_executor

if TYPE_CHECKING:
    from .row import Row
    from .tab import Tab


class Cell(str):
    """A single spreadsheet cell represented as an immutable string subclass.

    The cell's current value is the string itself.  All mutating operations
    (``update``, ``clear``, ``style``, ``delete``) are async and write through
    to the remote spreadsheet immediately.

    Attributes:
        tab: The :class:`~betterspread.tab.Tab` this cell belongs to.
        label: The column label of this cell (e.g. ``"A"``, ``"AA"``).
        row_index: The 1-based row number of this cell.
        cell_index: The 0-based column index within its parent row.
        row: The parent :class:`~betterspread.row.Row`, or ``None`` when the
            cell was fetched directly via :meth:`Tab.get_cell`.
    """

    # Class-level annotations let pyright (and other type-checkers) know that
    # these instance attributes exist even though they are set inside __new__.
    tab: "Tab"
    label: str
    row_index: int
    cell_index: int
    row: "Row | None"

    def __new__(
        cls,
        value: Any,
        tab: "Tab",
        label: str,
        row_index: int,
        cell_index: int = 0,
        row: "Row | None" = None,
    ) -> "Cell":
        instance = super().__new__(cls, value)
        instance.tab = tab
        instance.label = label
        instance.row_index = row_index
        instance.cell_index = cell_index
        instance.row = row
        return instance

    def __repr__(self) -> str:
        return f"<Cell {self.label}{self.row_index}={str(self)!r}>"

    # ------------------------------------------------------------------
    # Mutating operations
    # ------------------------------------------------------------------

    async def clear(self) -> None:
        """Clear the value of this cell in the remote spreadsheet."""
        if self.row is not None:
            self.row[self.cell_index] = Cell(
                "",
                self.tab,
                label=self.label,
                row_index=self.row_index,
                cell_index=self.cell_index,
                row=self.row,
            )

        await run_in_executor(self.tab.batch_clear, [f"{self.label}{self.row_index}"])

    async def update(
        self,
        value: Any,
        input_format: str = "raw",
        render_format: str = "formatted",
    ) -> "Cell":
        """Write *value* to the remote spreadsheet and return an updated cell.

        Args:
            value: The new cell value.
            input_format: One of ``"raw"`` or ``"user_entered"``.
            render_format: One of ``"formatted"``, ``"unformatted"``, or
                ``"formula"``.

        Returns:
            A new :class:`Cell` instance whose string value equals *value*.
        """
        updated = Cell(
            value,
            self.tab,
            label=self.label,
            row_index=self.row_index,
            cell_index=self.cell_index,
            row=self.row,
        )

        if self.row is not None:
            self.row[self.cell_index] = updated

        await run_in_executor(
            self.tab.update,
            [[value]],
            f"{self.label}{self.row_index}",
            value_input_option=input_formats.get(input_format, input_formats["raw"]),
            response_value_render_option=render_formats.get(
                render_format, render_formats["formatted"]
            ),
        )
        return updated

    async def style(self, obj: Style) -> None:
        """Apply *obj* formatting to this cell in the remote spreadsheet."""
        fmt = obj.raw if isinstance(obj, Style) else obj
        await run_in_executor(
            format_cell_range, self.tab, f"{self.label}{self.row_index}", fmt
        )

    async def delete(self, shift: str = "left") -> None:
        """Delete this cell, shifting neighbouring cells in *shift* direction."""
        await self.tab.del_cell(f"{self.label}{self.row_index}", shift=shift)

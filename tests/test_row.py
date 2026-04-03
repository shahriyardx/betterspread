"""
Tests for betterspread.Row

Only covers what betterspread adds on top of a plain list:
  - Row is a list subclass whose items are Cell objects
  - Column labels are correctly derived from position (including multi-letter columns)
  - Each Cell carries the correct row_index, cell_index, and back-reference to its Row
  - async mutations: update, clear, refetch, append_cell, delete
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from betterspread.cell import Cell
from betterspread.row import Row


def make_row(values: list, index: int = 1) -> Row:
    return Row(values, tab=MagicMock(), index=index)


# ---------------------------------------------------------------------------
# Row is a list subclass whose items are Cells
# ---------------------------------------------------------------------------


class TestRowIsListOfCells:
    def test_row_is_a_list(self):
        assert isinstance(make_row(["a", "b"]), list)

    def test_all_items_are_cells(self):
        row = make_row(["x", "y", "z"])
        assert all(isinstance(item, Cell) for item in row)

    def test_values_are_preserved(self):
        row = make_row(["alpha", "beta"])
        assert str(row[0]) == "alpha"
        assert str(row[1]) == "beta"

    def test_empty_row(self):
        assert len(make_row([])) == 0

    def test_row_index_stored(self):
        assert make_row(["a"], index=5).row_index == 5


# ---------------------------------------------------------------------------
# Column labels assigned to each Cell
# ---------------------------------------------------------------------------


class TestCellColumnLabels:
    def test_first_three_columns(self):
        row = make_row(["a", "b", "c"])
        assert row[0].label == "A"
        assert row[1].label == "B"
        assert row[2].label == "C"

    def test_column_27_is_aa(self):
        row = make_row([""] * 27)
        assert row[26].label == "AA"

    def test_column_52_is_az(self):
        # AZ was a broken edge case (remainder=0) in the original get_location
        row = make_row([""] * 52)
        assert row[51].label == "AZ"

    def test_column_53_is_ba(self):
        row = make_row([""] * 53)
        assert row[52].label == "BA"


# ---------------------------------------------------------------------------
# Cell metadata (row_index, cell_index, back-reference to Row)
# ---------------------------------------------------------------------------


class TestCellMetadata:
    def test_cell_row_index_matches_row(self):
        row = make_row(["v"], index=7)
        assert row[0].row_index == 7

    def test_cell_index_is_zero_based(self):
        row = make_row(["a", "b", "c"])
        assert row[0].cell_index == 0
        assert row[1].cell_index == 1
        assert row[2].cell_index == 2

    def test_cells_hold_back_reference_to_row(self):
        row = make_row(["a", "b"])
        assert row[0].row is row
        assert row[1].row is row


# ---------------------------------------------------------------------------
# async update()
# ---------------------------------------------------------------------------


class TestRowUpdate:
    async def test_calls_tab_update(self):
        mock_tab = MagicMock()
        row = Row(["a", "b"], tab=mock_tab, index=1)

        with patch("betterspread.row.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            await row.update(["x", "y"])

        m.assert_called_once()

    async def test_cells_reflect_new_values(self):
        mock_tab = MagicMock()
        row = Row(["old_a", "old_b"], tab=mock_tab, index=1)

        with patch("betterspread.row.run_in_executor", new_callable=AsyncMock):
            await row.update(["new_a", "new_b"])

        assert str(row[0]) == "new_a"
        assert str(row[1]) == "new_b"

    async def test_updated_items_are_still_cells(self):
        mock_tab = MagicMock()
        row = Row(["a"], tab=mock_tab, index=1)

        with patch("betterspread.row.run_in_executor", new_callable=AsyncMock):
            await row.update(["fresh"])

        assert isinstance(row[0], Cell)


# ---------------------------------------------------------------------------
# async clear()
# ---------------------------------------------------------------------------


class TestRowClear:
    async def test_calls_batch_clear_with_row_range(self):
        mock_tab = MagicMock()
        row = Row(["a", "b"], tab=mock_tab, index=3)

        with patch("betterspread.row.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            await row.clear()

        m.assert_called_once_with(mock_tab.batch_clear, ["3:3"])

    async def test_cells_become_empty_strings(self):
        mock_tab = MagicMock()
        row = Row(["alpha", "beta"], tab=mock_tab, index=1)

        with patch("betterspread.row.run_in_executor", new_callable=AsyncMock):
            await row.clear()

        assert all(str(cell) == "" for cell in row)

    async def test_length_preserved_after_clear(self):
        mock_tab = MagicMock()
        row = Row(["a", "b", "c"], tab=mock_tab, index=1)

        with patch("betterspread.row.run_in_executor", new_callable=AsyncMock):
            await row.clear()

        assert len(row) == 3


# ---------------------------------------------------------------------------
# async refetch()
# ---------------------------------------------------------------------------


class TestRowRefetch:
    async def test_reloads_values_from_tab(self):
        mock_tab = MagicMock()
        row = Row(["old"], tab=mock_tab, index=1)

        refreshed = Row(["new_value"], tab=mock_tab, index=1)
        mock_tab.values = AsyncMock(return_value=[refreshed])

        await row.refetch()

        assert str(row[0]) == "new_value"

    async def test_calls_tab_values(self):
        mock_tab = MagicMock()
        row = Row(["x"], tab=mock_tab, index=1)

        mock_tab.values = AsyncMock(return_value=[Row(["y"], tab=mock_tab, index=1)])
        await row.refetch()

        mock_tab.values.assert_called_once()


# ---------------------------------------------------------------------------
# async append_cell()
# ---------------------------------------------------------------------------


class TestRowAppendCell:
    async def test_appends_single_value(self):
        mock_tab = MagicMock()
        row = Row(["a", "b"], tab=mock_tab, index=1)

        with patch("betterspread.row.run_in_executor", new_callable=AsyncMock):
            await row.append_cell("c")

        assert str(row[-1]) == "c"

    async def test_appends_list_of_values(self):
        mock_tab = MagicMock()
        row = Row(["a"], tab=mock_tab, index=1)

        with patch("betterspread.row.run_in_executor", new_callable=AsyncMock):
            await row.append_cell(["b", "c"])

        assert len(row) == 3


# ---------------------------------------------------------------------------
# async delete()
# ---------------------------------------------------------------------------


class TestRowDelete:
    async def test_delegates_to_tab_del_row(self):
        mock_tab = MagicMock()
        mock_tab.del_row = AsyncMock()
        row = Row(["a"], tab=mock_tab, index=5)

        await row.delete()

        mock_tab.del_row.assert_called_once_with(5)

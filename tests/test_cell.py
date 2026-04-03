"""
Tests for betterspread.cell.Cell

Only covers what betterspread adds on top of a plain string:
  - Cell is a str subclass with extra attributes
  - __repr__
  - update() / clear() delegate to the right tab methods with the right args
  - Row back-reference is updated on mutation
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from betterspread.cell import Cell

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_cell(value="hello", label="A", row_index=1, cell_index=0, row=None):
    return Cell(value, MagicMock(), label, row_index, cell_index, row)


# ---------------------------------------------------------------------------
# Cell is a str subclass with betterspread-specific attributes
# ---------------------------------------------------------------------------


class TestCellIsAString:
    def test_inherits_from_str(self):
        assert isinstance(make_cell("hello"), str)

    def test_value_equals_string(self):
        assert make_cell("world") == "world"

    def test_empty_value(self):
        assert make_cell("") == ""

    def test_supports_string_operations(self):
        cell = make_cell("hello")
        assert cell.upper() == "HELLO"
        assert cell.startswith("he")
        assert len(cell) == 5


class TestCellAttributes:
    def test_label_stored(self):
        assert make_cell(label="B").label == "B"

    def test_multi_letter_label(self):
        assert make_cell(label="AA").label == "AA"

    def test_row_index_stored(self):
        assert make_cell(row_index=5).row_index == 5

    def test_cell_index_stored(self):
        assert make_cell(cell_index=3).cell_index == 3

    def test_cell_index_defaults_to_zero(self):
        tab = MagicMock()
        cell = Cell("v", tab, "A", 1)
        assert cell.cell_index == 0

    def test_row_defaults_to_none(self):
        tab = MagicMock()
        cell = Cell("v", tab, "A", 1)
        assert cell.row is None

    def test_row_stored_when_provided(self):
        mock_row = MagicMock()
        assert make_cell(row=mock_row).row is mock_row

    def test_tab_stored(self):
        mock_tab = MagicMock()
        cell = Cell("v", mock_tab, "A", 1)
        assert cell.tab is mock_tab


# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------


class TestCellRepr:
    def test_contains_label_and_row_index(self):
        assert "B3" in repr(make_cell(label="B", row_index=3))

    def test_contains_value(self):
        assert "myvalue" in repr(make_cell("myvalue"))

    def test_exact_format(self):
        assert repr(make_cell("x", label="C", row_index=7)) == "<Cell C7='x'>"

    def test_multi_letter_label(self):
        assert repr(make_cell("v", label="AA", row_index=10)) == "<Cell AA10='v'>"

    def test_empty_value(self):
        assert repr(make_cell("", label="A", row_index=1)) == "<Cell A1=''>"


# ---------------------------------------------------------------------------
# update() — delegates to tab, returns a new Cell, updates the row
# ---------------------------------------------------------------------------


class TestCellUpdate:
    async def test_calls_tab_update_via_executor(self):
        cell = make_cell("old", label="A", row_index=1)
        with patch("betterspread.cell.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            await cell.update("new")
        m.assert_called_once()

    async def test_passes_value_matrix_to_executor(self):
        cell = make_cell("old", label="A", row_index=1)
        with patch("betterspread.cell.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            await cell.update("new_value")
        assert m.call_args.args[1] == [["new_value"]]

    async def test_passes_correct_range_to_executor(self):
        cell = make_cell("old", label="B", row_index=4)
        with patch("betterspread.cell.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            await cell.update("val")
        assert m.call_args.args[2] == "B4"

    async def test_returns_new_cell_with_updated_value(self):
        cell = make_cell("old", label="A", row_index=1)
        with patch("betterspread.cell.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            result = await cell.update("updated")
        assert isinstance(result, Cell)
        assert result == "updated"

    async def test_returned_cell_preserves_metadata(self):
        mock_tab = MagicMock()
        cell = Cell("old", mock_tab, "C", 5, 2)
        with patch("betterspread.cell.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            result = await cell.update("new")
        assert result.label == "C"
        assert result.row_index == 5
        assert result.cell_index == 2
        assert result.tab is mock_tab

    async def test_original_cell_is_not_mutated(self):
        # Cell is an immutable str subclass — the original must stay unchanged.
        cell = make_cell("original")
        with patch("betterspread.cell.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            await cell.update("changed")
        assert cell == "original"

    async def test_writes_new_cell_to_row_when_present(self):
        mock_row = MagicMock()
        cell = make_cell("old", label="A", row_index=1, cell_index=0, row=mock_row)
        with patch("betterspread.cell.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            await cell.update("new")
        updated_cell = mock_row.__setitem__.call_args.args[1]
        assert updated_cell == "new"

    async def test_does_not_touch_row_when_row_is_none(self):
        mock_row = MagicMock()
        cell = make_cell("old", row=None)
        with patch("betterspread.cell.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            await cell.update("new")
        mock_row.__setitem__.assert_not_called()


# ---------------------------------------------------------------------------
# clear() — delegates to tab.batch_clear, updates the row
# ---------------------------------------------------------------------------


class TestCellClear:
    async def test_calls_batch_clear_with_correct_range(self):
        mock_tab = MagicMock()
        cell = Cell("v", mock_tab, "B", 2, 1)
        with patch("betterspread.cell.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            await cell.clear()
        m.assert_called_once_with(mock_tab.batch_clear, ["B2"])

    async def test_multi_letter_column_range(self):
        mock_tab = MagicMock()
        cell = Cell("v", mock_tab, "AA", 15, 26)
        with patch("betterspread.cell.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            await cell.clear()
        m.assert_called_once_with(mock_tab.batch_clear, ["AA15"])

    async def test_writes_empty_cell_to_row(self):
        mock_row = MagicMock()
        cell = Cell("v", MagicMock(), "A", 1, 0, mock_row)
        with patch("betterspread.cell.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            await cell.clear()
        cleared_cell = mock_row.__setitem__.call_args.args[1]
        assert cleared_cell == ""

    async def test_does_not_touch_row_when_row_is_none(self):
        mock_row = MagicMock()
        cell = Cell("v", MagicMock(), "A", 1, 0, None)
        with patch("betterspread.cell.run_in_executor", new_callable=AsyncMock) as m:
            m.return_value = None
            await cell.clear()
        mock_row.__setitem__.assert_not_called()

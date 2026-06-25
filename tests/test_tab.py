"""
Tests for betterspread.tab.Tab

Covers the async helpers betterspread adds on top of gspread.Worksheet:
  - __init__ / __repr__
  - values / get_row / get_cell (value + empty-cell paths)
  - append (with and without get_row)
  - del_row (single + range) / del_cell (single + range, both shift dirs)
Tab instances are built without gspread's networked Worksheet.__init__.
"""

from unittest.mock import AsyncMock, MagicMock, patch

from gspread import Worksheet

from betterspread.cell import Cell
from betterspread.row import Row
from betterspread.tab import Tab


def make_tab():
    """Build a Tab without invoking gspread's networked Worksheet.__init__."""
    tab = object.__new__(Tab)
    tab.sheet = MagicMock()
    tab._properties = {"sheetId": 42, "title": "Sheet1", "index": 0}
    return tab


# ---------------------------------------------------------------------------
# __init__ / __repr__
# ---------------------------------------------------------------------------


class TestTabInit:
    def test_stores_sheet_and_calls_super(self):
        sentinel = MagicMock()
        with patch.object(Worksheet, "__init__", return_value=None) as super_init:
            tab = Tab(sheet=sentinel, properties={}, spreadsheet_id="x", client=MagicMock())
        assert tab.sheet is sentinel
        super_init.assert_called_once()


class TestTabRepr:
    def test_shows_title_and_id(self):
        r = repr(make_tab())
        assert "Sheet1" in r
        assert "42" in r


# ---------------------------------------------------------------------------
# values()
# ---------------------------------------------------------------------------


class TestTabValues:
    async def test_returns_rows_of_cells(self):
        tab = make_tab()
        raw = [["a", "b"], ["c"]]
        with patch(
            "betterspread.tab.run_in_executor", new_callable=AsyncMock, return_value=raw
        ):
            rows = await tab.values()

        assert all(isinstance(r, Row) for r in rows)
        assert rows[0].row_index == 1
        assert rows[1].row_index == 2
        assert str(rows[0][1]) == "b"


# ---------------------------------------------------------------------------
# get_row()
# ---------------------------------------------------------------------------


class TestTabGetRow:
    async def test_returns_one_based_row(self):
        tab = make_tab()
        raw = [["r1"], ["r2"], ["r3"]]
        with patch(
            "betterspread.tab.run_in_executor", new_callable=AsyncMock, return_value=raw
        ):
            row = await tab.get_row(2)
        assert str(row[0]) == "r2"


# ---------------------------------------------------------------------------
# get_cell()
# ---------------------------------------------------------------------------


class TestTabGetCell:
    async def test_returns_cell_with_metadata(self):
        tab = make_tab()
        with patch(
            "betterspread.tab.run_in_executor",
            new_callable=AsyncMock,
            return_value=[["hello"]],
        ):
            cell = await tab.get_cell("B2")
        assert isinstance(cell, Cell)
        assert str(cell) == "hello"
        assert cell.label == "B"
        assert cell.row_index == 2
        assert cell.cell_index == 1

    async def test_empty_response_yields_empty_cell(self):
        tab = make_tab()
        with patch(
            "betterspread.tab.run_in_executor",
            new_callable=AsyncMock,
            return_value=[],
        ):
            cell = await tab.get_cell("A1")
        assert str(cell) == ""

    async def test_multi_letter_column(self):
        tab = make_tab()
        with patch(
            "betterspread.tab.run_in_executor",
            new_callable=AsyncMock,
            return_value=[["x"]],
        ):
            cell = await tab.get_cell("AA10")
        assert cell.label == "AA"
        assert cell.row_index == 10
        assert cell.cell_index == 26


# ---------------------------------------------------------------------------
# append()
# ---------------------------------------------------------------------------


class TestTabAppend:
    async def test_returns_none_without_get_row(self):
        tab = make_tab()
        resp = {"updates": {"updatedRange": "Sheet1!A5:C5"}}
        with patch(
            "betterspread.tab.run_in_executor",
            new_callable=AsyncMock,
            return_value=resp,
        ):
            assert await tab.append(["x"]) is None

    async def test_resolves_appended_row_from_response(self):
        tab = make_tab()
        resp = {"updates": {"updatedRange": "Sheet1!A2:C2"}}
        rows_raw = [["r1"], ["r2"], ["r3"]]
        # 1st executor call: append_row -> resp; 2nd: get_values (inside get_row)
        with patch(
            "betterspread.tab.run_in_executor",
            new_callable=AsyncMock,
            side_effect=[resp, rows_raw],
        ):
            row = await tab.append(["r2"], get_row=True)
        assert row.row_index == 2
        assert str(row[0]) == "r2"


# ---------------------------------------------------------------------------
# del_row()
# ---------------------------------------------------------------------------


class TestTabDelRow:
    async def test_single_row_defaults_end_to_start(self):
        tab = make_tab()
        with patch(
            "betterspread.tab.run_in_executor", new_callable=AsyncMock
        ) as m:
            await tab.del_row(5)
        assert m.call_args.kwargs["start_index"] == 5
        assert m.call_args.kwargs["end_index"] == 5

    async def test_range(self):
        tab = make_tab()
        with patch(
            "betterspread.tab.run_in_executor", new_callable=AsyncMock
        ) as m:
            await tab.del_row(3, end=5)
        assert m.call_args.kwargs["start_index"] == 3
        assert m.call_args.kwargs["end_index"] == 5


# ---------------------------------------------------------------------------
# del_cell()
# ---------------------------------------------------------------------------


def _delete_range(call_args):
    body = call_args.args[1]
    return body["requests"][0]["deleteRange"]


class TestTabDelCell:
    async def test_single_cell_shifts_rows_up(self):
        tab = make_tab()
        with patch(
            "betterspread.tab.run_in_executor", new_callable=AsyncMock
        ) as m:
            await tab.del_cell("B2")
        dr = _delete_range(m.call_args)
        assert dr["shiftDimension"] == "ROWS"
        assert dr["range"] == {
            "sheetId": 42,
            "startRowIndex": 1,
            "endRowIndex": 2,
            "startColumnIndex": 1,
            "endColumnIndex": 2,
        }

    async def test_range_shifts_columns_left(self):
        tab = make_tab()
        with patch(
            "betterspread.tab.run_in_executor", new_callable=AsyncMock
        ) as m:
            await tab.del_cell("A1", "C3", shift="left")
        dr = _delete_range(m.call_args)
        assert dr["shiftDimension"] == "COLUMNS"
        assert dr["range"]["startColumnIndex"] == 0
        assert dr["range"]["endColumnIndex"] == 3
        assert dr["range"]["startRowIndex"] == 0
        assert dr["range"]["endRowIndex"] == 3

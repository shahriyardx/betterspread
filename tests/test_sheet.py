"""
Tests for betterspread.sheet.Sheet

Covers what betterspread adds on top of gspread.Spreadsheet:
  - construction / repr / lazy + idempotent + concurrency-safe open()
  - get_tab / tabs build Tab objects from the opened spreadsheet
No real network calls are made — run_in_executor and Tab are patched.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from betterspread.sheet import Sheet


def make_sheet(folder_id=None):
    return Sheet(sheet_name="My Sheet", connection=MagicMock(), folder_id=folder_id)


def _opened_spreadsheet():
    sp = MagicMock()
    sp.client = MagicMock()
    sp._properties = {"title": "My Sheet"}
    sp.id = "spreadsheet-id"
    return sp


# ---------------------------------------------------------------------------
# construction
# ---------------------------------------------------------------------------


class TestSheetInit:
    def test_stores_attributes(self):
        con = MagicMock()
        sheet = Sheet("My Sheet", con, folder_id="fid")
        assert sheet.sheet_name == "My Sheet"
        assert sheet.connection is con
        assert sheet.folder_id == "fid"

    def test_starts_closed(self):
        sheet = make_sheet()
        assert sheet.sheet is None
        assert sheet._is_open is False

    def test_folder_id_defaults_to_none(self):
        assert make_sheet().folder_id is None


# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------


class TestSheetRepr:
    def test_closed(self):
        r = repr(make_sheet())
        assert "My Sheet" in r
        assert "closed" in r

    def test_open(self):
        sheet = make_sheet()
        sheet._is_open = True
        assert "open" in repr(sheet)


# ---------------------------------------------------------------------------
# open()
# ---------------------------------------------------------------------------


class TestSheetOpen:
    async def test_opens_and_copies_state(self):
        sheet = make_sheet(folder_id="fid")
        sp = _opened_spreadsheet()
        with patch(
            "betterspread.sheet.run_in_executor",
            new_callable=AsyncMock,
            return_value=sp,
        ) as m:
            await sheet.open()

        assert sheet._is_open is True
        assert sheet.sheet is sp
        assert sheet.client is sp.client
        assert sheet._properties == sp._properties
        # opened with the configured name + folder
        assert m.call_args.args[1] == "My Sheet"
        assert m.call_args.kwargs["folder_id"] == "fid"

    async def test_noop_when_already_open(self):
        sheet = make_sheet()
        sheet._is_open = True
        with patch(
            "betterspread.sheet.run_in_executor", new_callable=AsyncMock
        ) as m:
            await sheet.open()
        m.assert_not_called()

    async def test_concurrent_opens_fire_once(self):
        sheet = make_sheet()
        sp = _opened_spreadsheet()
        calls = {"n": 0}

        async def fake_open(*args, **kwargs):
            calls["n"] += 1
            await asyncio.sleep(0)  # yield so both coroutines interleave
            return sp

        with patch("betterspread.sheet.run_in_executor", fake_open):
            await asyncio.gather(sheet.open(), sheet.open())

        assert calls["n"] == 1


# ---------------------------------------------------------------------------
# get_tab()
# ---------------------------------------------------------------------------


class TestSheetGetTab:
    async def test_builds_tab_from_worksheet(self):
        sheet = make_sheet()
        sheet._is_open = True
        sheet.sheet = _opened_spreadsheet()

        ws = MagicMock()
        ws._properties = {"title": "Sheet1", "sheetId": 0}

        with (
            patch(
                "betterspread.sheet.run_in_executor",
                new_callable=AsyncMock,
                return_value=ws,
            ),
            patch("betterspread.sheet.Tab") as TabMock,
        ):
            result = await sheet.get_tab("Sheet1")

        assert result is TabMock.return_value
        TabMock.assert_called_once()
        assert TabMock.call_args.kwargs["sheet"] is sheet
        assert TabMock.call_args.kwargs["properties"] == ws._properties


# ---------------------------------------------------------------------------
# tabs()
# ---------------------------------------------------------------------------


class TestSheetTabs:
    async def test_returns_one_tab_per_worksheet(self):
        sheet = make_sheet()
        sheet._is_open = True
        sheet.sheet = _opened_spreadsheet()

        ws1, ws2 = MagicMock(), MagicMock()
        ws1._properties = {"title": "a"}
        ws2._properties = {"title": "b"}

        with (
            patch(
                "betterspread.sheet.run_in_executor",
                new_callable=AsyncMock,
                return_value=[ws1, ws2],
            ),
            patch("betterspread.sheet.Tab") as TabMock,
        ):
            result = await sheet.tabs()

        assert len(result) == 2
        assert TabMock.call_count == 2

    async def test_passes_exclude_hidden_through(self):
        sheet = make_sheet()
        sheet._is_open = True
        sheet.sheet = _opened_spreadsheet()

        with (
            patch(
                "betterspread.sheet.run_in_executor",
                new_callable=AsyncMock,
                return_value=[],
            ) as m,
            patch("betterspread.sheet.Tab"),
        ):
            await sheet.tabs(exclude_hidden=True)

        assert m.call_args.kwargs["exclude_hidden"] is True

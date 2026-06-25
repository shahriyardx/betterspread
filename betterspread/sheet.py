import asyncio

from gspread import Client, Spreadsheet

from .connection import Connection
from .tab import Tab
from .utils import run_in_executor


class Sheet(Spreadsheet):
    """An async-friendly wrapper around :class:`gspread.Spreadsheet`.

    The underlying gspread spreadsheet is opened lazily on the first call to
    any async method.  You can also trigger the connection explicitly with
    ``await sheet.open()``.

    Args:
        sheet_name: The exact title of the spreadsheet as it appears in
            Google Drive.
        connection: An authenticated :class:`~betterspread.connection.Connection`.
        folder_id: Optional Google Drive folder ID.  When provided, the search
            for *sheet_name* is scoped to that folder.

    Examples::

        con = Connection(credentials_path="./credentials.json")
        sheet = Sheet(connection=con, sheet_name="My Spreadsheet")
        tab = await sheet.get_tab("Sheet1")
    """

    # Class-level annotations so type-checkers know about the instance attrs
    # that are populated lazily inside open().
    sheet_name: str
    folder_id: str | None
    connection: Connection
    _is_open: bool

    def __init__(
        self,
        sheet_name: str,
        connection: Connection,
        folder_id: str | None = None,
    ) -> None:
        self.sheet_name = sheet_name
        self.connection = connection
        self.folder_id = folder_id
        self.sheet: Spreadsheet | None = None
        self._is_open = False
        self._open_lock = asyncio.Lock()

    def __repr__(self) -> str:
        status = "open" if self._is_open else "closed"
        return f"<Sheet name={self.sheet_name!r} status={status}>"

    async def open(self) -> None:
        """Open the remote spreadsheet (no-op if already open)."""
        if self._is_open:
            return

        # Serialize concurrent opens so two coroutines can't both fire the
        # network call; re-check inside the lock for the waiter that follows.
        async with self._open_lock:
            if self._is_open:
                return
            _sheet = await run_in_executor(
                self.connection.client.open,
                self.sheet_name,
                folder_id=self.folder_id,
            )
            self.sheet = _sheet
            # NOTE: we deliberately do NOT call Spreadsheet.__init__ here.
            # gspread's base __init__ fires a synchronous fetch_sheet_metadata()
            # network request, which would block the event loop and duplicate
            # the work already done by client.open(). Instead we copy the two
            # attributes inherited methods rely on (client + _properties) off the
            # spreadsheet object we already fetched.
            self.client: Client = _sheet.client
            self._properties: dict = _sheet._properties
            self._is_open = True

    async def get_tab(self, tab_name: str) -> Tab:
        """Return the worksheet named *tab_name* as a :class:`Tab`.

        Args:
            tab_name: The exact title of the worksheet tab.

        Returns:
            A :class:`~betterspread.tab.Tab` wrapping the requested worksheet.
        """
        await self.open()
        assert self.sheet is not None
        _tab = await run_in_executor(self.worksheet, tab_name)
        return Tab(
            spreadsheet=self.sheet,
            properties=_tab._properties,
            sheet=self,
            spreadsheet_id=self.sheet.id,
            client=self.sheet.client,
        )

    async def tabs(self, exclude_hidden: bool = False) -> list[Tab]:
        """Return all worksheet tabs in this spreadsheet.

        Args:
            exclude_hidden: When ``True``, hidden worksheets are omitted from
                the result.

        Returns:
            A list of :class:`~betterspread.tab.Tab` objects, one per
            worksheet.
        """
        await self.open()
        assert self.sheet is not None  # guaranteed after open()
        sheets = await run_in_executor(self.worksheets, exclude_hidden=exclude_hidden)
        return [
            Tab(
                spreadsheet=self.sheet,
                properties=tab._properties,  # noqa: SLF001
                sheet=self,
                spreadsheet_id=self.sheet.id,  # fixed: was tab.id (sheetId, not spreadsheet ID)
                client=self.sheet.client,
            )
            for tab in sheets
        ]

from dataclasses import dataclass

from gspread import Client, Spreadsheet

from .connection import Connection
from .tab import Tab
from .utils import run_in_executor


@dataclass
class Sheet(Spreadsheet):
    sheet_name: str
    folder_id: str = None
    connection: Connection = None
    sheet: Spreadsheet = None
    _properties: dict = None
    _open: bool = False

    async def open(self):
        if not self._open:
            sheet = await run_in_executor(
                self.connection.client.open, self.sheet_name, folder_id=self.folder_id
            )
            self.sheet = sheet
            self.client: Client = sheet.client
            self._properties: dict = sheet._properties  # noqa
            self._open = True

    async def get_tab(self, tab_name: str) -> Tab:
        await self.open()
        _tab = await run_in_executor(self.worksheet, tab_name)
        return Tab(
            spreadsheet=self.sheet,
            properties=_tab._properties,  # noqa
            sheet=self,
            spreadsheet_id=self.sheet.id,
            client=self.sheet.client,
        )

    async def tabs(self, exclude_hidden: bool = False):
        await self.open()
        sheets = await run_in_executor(self.worksheets, exclude_hidden=exclude_hidden)

        return [
            Tab(
                spreadsheet=self,
                properties=tab._properties,  # noqa
                sheet=self,
                spreadsheet_id=tab.id,
                client=self.sheet.client,
            )
            for tab in sheets
        ]

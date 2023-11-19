from dataclasses import dataclass

from gspread import Client, Spreadsheet

from .connection import Connection
from .tab import Tab


@dataclass
class Sheet(Spreadsheet):
    sheet_name: str
    connection: Connection
    sheet: Spreadsheet = None

    def __post_init__(self):
        sheet = self.connection.client.open(self.sheet_name)
        self.client: Client = sheet.client
        self._properties: dict = sheet._properties

    def get_tab(self, tab_name: str) -> Tab:
        _tab = self.worksheet(tab_name)
        return Tab(spreadsheet=self, properties=_tab._properties)

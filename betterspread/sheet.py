from dataclasses import dataclass

from gspread import Client, Spreadsheet

from .connection import Connection
from .tab import Tab


@dataclass
class Sheet(Spreadsheet):
    sheet_name: str
    folder_id: str = None
    connection: Connection = None
    sheet: Spreadsheet = None
    _properties: dict = None

    def __post_init__(self):
        sheet = self.connection.client.open(self.sheet_name, folder_id=self.folder_id)
        self.client: Client = sheet.client
        self._properties: dict = sheet._properties  # noqa

    def get_tab(self, tab_name: str) -> Tab:
        _tab = self.worksheet(tab_name)
        return Tab(spreadsheet=self, properties=_tab._properties, sheet=self)  # noqa

    def tabs(self, exclude_hidden: bool = False):
        sheets = self.worksheets(exclude_hidden=exclude_hidden)
        return [
            Tab(spreadsheet=self, properties=tab._properties, sheet=self)  # noqa
            for tab in sheets
        ]

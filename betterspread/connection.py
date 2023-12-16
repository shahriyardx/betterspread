from pathlib import Path
from typing import Union

from gspread import service_account, service_account_from_dict


class Connection:
    def __init__(
        self, credentials_path: Union[Path, str] = None, credentials_dict: dict = None
    ):
        self.open = False
        func = service_account if credentials_path else service_account_from_dict
        self.client = func(credentials_path or credentials_dict)

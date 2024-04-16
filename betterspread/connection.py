from pathlib import Path
from typing import Union

from gspread import service_account, service_account_from_dict


class Connection:
    def __init__(self, credentials: Union[Path, str, dict] = None):
        self.open = False
        func = (
            service_account
            if isinstance(credentials, (Path, str))
            else service_account_from_dict
        )
        self.client = func(credentials)

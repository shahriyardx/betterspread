from pathlib import Path
from typing import Union

from gspread import service_account, service_account_from_dict


class Connection:
    def __init__(
        self, credentials_path: Union[Path, str] = None, credentials_dict: dict = None
    ):
        if not credentials_path and credentials_dict:
            raise ValueError("credentials path or dict is required")

        self.client = (
            service_account(credentials_path)
            if credentials_path
            else service_account_from_dict(credentials_dict)
        )

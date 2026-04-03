from pathlib import Path

from gspread import Client, service_account, service_account_from_dict


class Connection:
    """Wraps a gspread authenticated client.

    Exactly one of *credentials_path* or *credentials_dict* must be supplied.

    Args:
        credentials_path: Path to a service-account JSON key file.
        credentials_dict: Service-account credentials as a plain dictionary
            (useful when credentials are stored in environment variables or a
            secrets manager rather than on disk).

    Raises:
        ValueError: If neither *credentials_path* nor *credentials_dict* is
            provided.
    """

    client: Client

    def __init__(
        self,
        credentials_path: Path | str | None = None,
        credentials_dict: dict | None = None,
    ) -> None:
        if credentials_path is None and credentials_dict is None:
            raise ValueError(
                "Either credentials_path or credentials_dict must be provided."
            )

        if credentials_path is not None:
            self.client = service_account(filename=credentials_path)
        else:
            self.client = service_account_from_dict(credentials_dict)  # type: ignore[arg-type]

from unittest.mock import MagicMock, patch

import pytest

from betterspread.connection import Connection


def _mock_client():
    return MagicMock()


class TestConnectionValidation:
    def test_raises_when_no_args(self):
        with pytest.raises(
            ValueError, match="Either credentials_path or credentials_dict"
        ):
            Connection()

    def test_raises_when_both_none_explicit(self):
        with pytest.raises(ValueError):
            Connection(credentials_path=None, credentials_dict=None)

    def test_error_message_mentions_both_params(self):
        with pytest.raises(ValueError) as exc_info:
            Connection()
        assert "credentials_path" in str(exc_info.value)
        assert "credentials_dict" in str(exc_info.value)


class TestConnectionDispatch:
    def test_path_calls_service_account(self):
        with patch("betterspread.connection.service_account") as mock_sa:
            mock_sa.return_value = _mock_client()
            Connection(credentials_path="./credentials.json")
            mock_sa.assert_called_once_with(filename="./credentials.json")

    def test_dict_calls_service_account_from_dict(self):
        creds = {"type": "service_account"}
        with patch("betterspread.connection.service_account_from_dict") as mock_sad:
            mock_sad.return_value = _mock_client()
            Connection(credentials_dict=creds)
            mock_sad.assert_called_once_with(creds)

    def test_path_takes_priority_over_dict(self):
        with (
            patch("betterspread.connection.service_account") as mock_sa,
            patch("betterspread.connection.service_account_from_dict") as mock_sad,
        ):
            mock_sa.return_value = _mock_client()
            Connection(
                credentials_path="./credentials.json",
                credentials_dict={"type": "service_account"},
            )
            mock_sa.assert_called_once()
            mock_sad.assert_not_called()

    def test_client_is_stored(self):
        fake_client = _mock_client()
        with patch("betterspread.connection.service_account", return_value=fake_client):
            con = Connection(credentials_path="./credentials.json")
        assert con.client is fake_client

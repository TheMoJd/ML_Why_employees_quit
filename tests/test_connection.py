"""
Tests pour la connexion à la base de données.
Teste get_db() et db_test_connection() depuis connection.py.
"""

from unittest.mock import patch, MagicMock
from src.database.connection import get_db
from src.database.connection import test_connection as db_test_connection


class TestGetDb:

    def test_get_db_yields_session_and_closes(self):
        """get_db() doit yield une session puis la fermer."""
        gen = get_db()
        session = next(gen)
        assert session is not None
        try:
            gen.send(None)
        except StopIteration:
            pass


class TestTestConnection:

    def test_connection_success(self):
        """Avec un engine valide qui répond, retourne True."""
        mock_conn = MagicMock()
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__ = lambda s: mock_conn
        mock_engine.connect.return_value.__exit__ = MagicMock(
            return_value=False
        )

        with patch("src.database.connection.engine", mock_engine):
            assert db_test_connection() is True

    def test_connection_failure(self):
        """Avec un engine qui échoue, retourne False."""
        mock_engine = MagicMock()
        mock_engine.connect.side_effect = Exception("connection refused")

        with patch("src.database.connection.engine", mock_engine):
            assert db_test_connection() is False

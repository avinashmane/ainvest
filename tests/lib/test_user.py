"""
Tests for lib/user.py

User and Accounts use a db_client injected via the constructor (or the module-
level `db` singleton).  All tests pass a MagicMock db_client so no real
Firestore calls are made.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import pandas as pd

from lib.user import User, Accounts


def _mock_doc(data: dict):
    """Return a mock DocumentSnapshot whose .to_dict() returns *data*."""
    doc = MagicMock()
    doc.to_dict.return_value = data
    return doc


class TestUser(unittest.TestCase):

    def setUp(self):
        self.email = 'test@example.com'
        self.mock_db = MagicMock()
        self.user = User(self.email, db_client=self.mock_db)

    def test_user_initialization(self):
        self.assertEqual(self.user.email, self.email)

    def test_get_profile_returns_dict(self):
        profile_data = {"name": "Test", "cash_balance": 1000}
        self.mock_db.document.return_value.get.return_value = _mock_doc(profile_data)
        profile = self.user.get_profile()
        self.assertEqual(profile["name"], "Test")
        self.assertEqual(profile["cash_balance"], 1000)

    def test_update_calls_firestore(self):
        self.user.update(name='Test User')
        self.mock_db.document.return_value.update.assert_called_once()
        call_kwargs = self.mock_db.document.return_value.update.call_args[0][0]
        self.assertEqual(call_kwargs["name"], "Test User")

    def test_load_pvt_portfolio_empty(self):
        self.mock_db.collection.return_value.list_documents.return_value = []
        df = self.user.load_pvt_portfolio()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)

    def test_load_pvt_portfolio_rows(self):
        row = {"Symbol": "INFY.NS", "Quantity": "10", "Cost Basis": "15000"}
        mock_ref = MagicMock()
        mock_ref.get.return_value = _mock_doc(row)
        self.mock_db.collection.return_value.list_documents.return_value = [mock_ref]
        df = self.user.load_pvt_portfolio()
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["Symbol"], "INFY.NS")

    def test_list_transactions_empty(self):
        self.mock_db.collection.return_value.list_documents.return_value = []
        df = self.user.list_transactions()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)

    @unittest.skip("Integration test — requires running API server.")
    def test_transaction(self):
        pass


class TestAccounts(unittest.TestCase):

    @patch("lib.user.db")
    def test_list_users_empty(self, mock_db):
        mock_db.db_client.collection.return_value.list_documents.return_value = []
        users = Accounts.list_users()
        self.assertIsInstance(users, pd.DataFrame)
        self.assertTrue(users.empty)

    @patch("lib.user.db")
    def test_list_users_filters_hidden(self, mock_db):
        refs = []
        for data in [
            {"name": "Alice", "cash_balance": 1000},
            {"name": "Bob",   "cash_balance": 2000, "hide": True},
        ]:
            ref = MagicMock()
            ref.id = data.get("name", "unknown") + "@b.com"
            ref.get.return_value = _mock_doc(data)
            refs.append(ref)
        mock_db.db_client.collection.return_value.list_documents.return_value = refs
        users = Accounts.list_users()
        self.assertEqual(len(users), 1)

    @patch("lib.user.db")
    def test_get_leaderboard_returns_dataframe(self, mock_db):
        ref = MagicMock()
        ref.id = "a@b.com"
        ref.get.return_value = _mock_doc({"cash_balance": 1000})
        mock_db.db_client.collection.return_value.list_documents.return_value = [ref]
        # patch User.get_portfolio to avoid a second db round-trip
        with patch.object(User, "get_portfolio", return_value=pd.DataFrame({"value": [500.0]})):
            lb = Accounts.get_leaderboard()
        self.assertIsInstance(lb, pd.DataFrame)
        self.assertEqual(len(lb), 1)


if __name__ == '__main__':
    unittest.main()

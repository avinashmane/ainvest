"""
Tests for app/lib/portfolio_gsheet.py

The tests mock the gspread client so no real network call is made.
"""

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from lib.portfolio_gsheet import read_portfolio
from lib.config import PORTFOLIO_NAMED_RANGE, PORTFOLIO_URL
from lib.gsheets import named_range_to_df as _named_range_to_df


def _make_cell(row: int, col: int, value: str):
    cell = MagicMock()
    cell.row = row
    cell.col = col
    cell.value = value
    return cell


SAMPLE_CELLS = [
    # header row
    _make_cell(1, 1, "Ticker"),
    _make_cell(1, 2, "Quantity"),
    _make_cell(1, 3, "Avg Cost"),
    # data row 1
    _make_cell(2, 1, "INFY"),
    _make_cell(2, 2, "10"),
    _make_cell(2, 3, "1500.00"),
    # data row 2
    _make_cell(3, 1, "TCS"),
    _make_cell(3, 2, "5"),
    _make_cell(3, 3, "3200.00"),
]


class TestNamedRangeToDF(unittest.TestCase):
    """Unit tests for the pure conversion helper (lib.gsheets.named_range_to_df)."""

    def test_returns_dataframe(self):
        mock_wb = MagicMock()
        mock_wb.named_range.return_value = SAMPLE_CELLS
        df = _named_range_to_df(mock_wb, "stockSumm")
        self.assertIsInstance(df, pd.DataFrame)

    def test_correct_columns(self):
        mock_wb = MagicMock()
        mock_wb.named_range.return_value = SAMPLE_CELLS
        df = _named_range_to_df(mock_wb, "stockSumm")
        self.assertEqual(list(df.columns), ["Ticker", "Quantity", "Avg Cost"])

    def test_correct_row_count(self):
        mock_wb = MagicMock()
        mock_wb.named_range.return_value = SAMPLE_CELLS
        df = _named_range_to_df(mock_wb, "stockSumm")
        self.assertEqual(len(df), 2)

    def test_correct_values(self):
        mock_wb = MagicMock()
        mock_wb.named_range.return_value = SAMPLE_CELLS
        df = _named_range_to_df(mock_wb, "stockSumm")
        self.assertEqual(df.iloc[0]["Ticker"], "INFY")
        self.assertEqual(df.iloc[1]["Ticker"], "TCS")

    def test_empty_named_range_returns_empty_df(self):
        mock_wb = MagicMock()
        mock_wb.named_range.return_value = []
        df = _named_range_to_df(mock_wb, "stockSumm")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 0)

    def test_header_only_returns_empty_df_with_columns(self):
        header_only = [
            _make_cell(1, 1, "Ticker"),
            _make_cell(1, 2, "Quantity"),
        ]
        mock_wb = MagicMock()
        mock_wb.named_range.return_value = header_only
        df = _named_range_to_df(mock_wb, "stockSumm")
        self.assertEqual(list(df.columns), ["Ticker", "Quantity"])
        self.assertEqual(len(df), 0)


class TestReadPortfolio(unittest.TestCase):
    """Integration-style tests that mock the gspread client."""

    @patch("lib.portfolio_gsheet.get_client")
    def test_returns_dataframe(self, mock_get_client):
        mock_wb = MagicMock()
        mock_wb.named_range.return_value = SAMPLE_CELLS
        mock_get_client.return_value.open_by_url.return_value = mock_wb

        df = read_portfolio()
        self.assertIsInstance(df, pd.DataFrame)

    @patch("lib.portfolio_gsheet.get_client")
    def test_uses_default_url_and_range(self, mock_get_client):
        mock_wb = MagicMock()
        mock_wb.named_range.return_value = SAMPLE_CELLS
        mock_client = mock_get_client.return_value
        mock_client.open_by_url.return_value = mock_wb

        read_portfolio()

        mock_client.open_by_url.assert_called_once_with(PORTFOLIO_URL)
        mock_wb.named_range.assert_called_once_with(PORTFOLIO_NAMED_RANGE)

    @patch("lib.portfolio_gsheet.get_client")
    def test_custom_url_and_range_forwarded(self, mock_get_client):
        mock_wb = MagicMock()
        mock_wb.named_range.return_value = SAMPLE_CELLS
        mock_client = mock_get_client.return_value
        mock_client.open_by_url.return_value = mock_wb

        custom_url = "https://docs.google.com/spreadsheets/d/custom/"
        read_portfolio(url=custom_url, named_range="myRange")

        mock_client.open_by_url.assert_called_once_with(custom_url)
        mock_wb.named_range.assert_called_once_with("myRange")

    @patch("lib.portfolio_gsheet.get_client")
    def test_row_data_correct(self, mock_get_client):
        mock_wb = MagicMock()
        mock_wb.named_range.return_value = SAMPLE_CELLS
        mock_get_client.return_value.open_by_url.return_value = mock_wb

        df = read_portfolio()
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["Ticker"], "INFY")


if __name__ == "__main__":
    unittest.main()

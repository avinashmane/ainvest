"""
lib/gsheets.py
--------------
Low-level Google Sheets helpers shared across the codebase.

Public API
----------
get_client() -> gspread.Client
    Return an authenticated gspread client (env-var creds or local key file).

named_range_to_df(workbook, named_range) -> pd.DataFrame
    Convert a gspread named-range into a DataFrame (first row = headers).
"""

from __future__ import annotations

import json
import os

import gspread
import pandas as pd


def get_client() -> gspread.Client:
    """Return an authenticated gspread client using env-var or local key file."""
    cred_json = os.getenv("GOOGLE_CRED_JSON", "")
    if len(cred_json) > 100:
        return gspread.service_account_from_dict(json.loads(cred_json))
    return gspread.service_account(filename=".streamlit/firebase_key.json")


def named_range_to_df(workbook: gspread.Spreadsheet, named_range: str) -> pd.DataFrame:
    """Convert a gspread named-range into a DataFrame (first row = headers)."""
    cells = workbook.named_range(named_range)
    if not cells:
        return pd.DataFrame()

    # Group cells by row number preserving column order
    rows: dict[int, dict[int, str]] = {}
    for cell in cells:
        rows.setdefault(cell.row, {})[cell.col] = cell.value

    matrix = [list(row.values()) for row in rows.values()]
    if len(matrix) < 2:
        # Only a header row or empty – return empty frame with those columns
        return pd.DataFrame(columns=matrix[0] if matrix else [])

    return pd.DataFrame(matrix[1:], columns=matrix[0])


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(verbose=True)
    gc = get_client()
    wks = gc.open_by_url(
        "https://docs.google.com/spreadsheets/d/1c4QkJmryNjxv4Ss7cRIoZSIbwJ6BYRWB9JE3-CIZ9ps/edit?gid=838891933"
    )
    print(named_range_to_df(wks, "stockSumm"))

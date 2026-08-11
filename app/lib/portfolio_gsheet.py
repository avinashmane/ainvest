"""
portfolio_gsheet.py
-------------------
Reads the portfolio data table from a Google Sheet.

The spreadsheet URL is fixed to the ainvest portfolio sheet; the named
range "stockSumm" holds the holdings summary table.

Public API
----------
read_portfolio(url, named_range) -> pd.DataFrame
"""

from __future__ import annotations

import pandas as pd

from lib.config import PORTFOLIO_URL, PORTFOLIO_NAMED_RANGE
from lib.gsheets import get_client, named_range_to_df


def read_portfolio(
    url: str = PORTFOLIO_URL,
    named_range: str = PORTFOLIO_NAMED_RANGE,
) -> pd.DataFrame:
    """
    Open *url* and return the *named_range* table as a DataFrame.

    Parameters
    ----------
    url:
        Full Google Sheets URL.  Defaults to the ainvest portfolio sheet.
    named_range:
        Name of the named range that contains the portfolio table.
        Defaults to ``"PF"``.

    Returns
    -------
    pd.DataFrame
        Rows are individual holdings; columns come from the first row of the
        named range.
    """
    gc = get_client()
    workbook = gc.open_by_url(url)
    return named_range_to_df(workbook, named_range)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(verbose=True)
    df = read_portfolio()
    print(df.to_string())

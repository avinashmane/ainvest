import yfinance as yf
from pydash import pick
from functools import lru_cache

def lookup_tickers(profile, ticker):
    lst=yf.Search(ticker,
                max_results=20,
                news_count=0,
                enable_fuzzy_query=True).all
    quotes=[x for x in lst["quotes"] if (x["isYahooFinance"]==True) 
            and (x["exchange"] in profile.get('exchanges',["BSE","NSI"]))]
            
    return quotes

@lru_cache(maxsize=128)
def get_quote(ticker):
    t = yf.Ticker(ticker)
    return pick(t.fast_info,
                ['currency', 'dayHigh', 'dayLow', 'exchange', 'lastPrice', 'previousClose','timezone'])
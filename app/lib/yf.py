import yfinance as yf
from pydash import pick
# from functools import lru_cache,cache
from cachetools import TTLCache,cached


def lookup_tickers(profile, ticker):
    lst=yf.Search(ticker,
                max_results=30,
                recommended = 30,
                news_count=0,
                enable_fuzzy_query=True).all
    if 'quotes' in lst:
        quotes=[x for x in lst["quotes"] if (x["isYahooFinance"]==True) 
            and (x["exchange"] in profile.get('exchanges',["BSE","NSI"]))]
        return quotes        
    return []

@cached(cache=TTLCache(maxsize=1024, ttl=60))
def get_quote(ticker):

    t = yf.Ticker(ticker)
    keys=['name','currency', 'dayHigh', 'dayLow', 'exchange', 'lastPrice', 'previousClose','timezone']
    info=t.info

    quote_info = { f:info.get(f) for f in keys}
    # print( {f:info.get(f) for f in info.keys() if 'name' in f }) #
    quote_info['ticker']=ticker

    name = info.get("shortName")
    if name and (name!=ticker):
        quote_info['name']=name
    else:
        quote_info['name'] = info.get("longName")

    if not quote_info['lastPrice']: 
        quote_info['lastPrice'] = quote_info['previousClose']
    return quote_info
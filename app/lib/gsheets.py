import gspread

import os
# from gspread.auth import service_account_from_dict
# from google.oauth2.service_account import Credentials
import json
import pandas as pd
from box import Box

pvt_data=Box({"url":None})

def open_url(url):
    cred_json=os.getenv('GOOGLE_CRED_JSON')
    if len(cred_json)>100:
        cred_json=json.loads(cred_json)
        gc = gspread.service_account_from_dict(cred_json)
    else:
        gc= gspread.service_account(filename='.streamlit/firebase_key.json')
    pvt_data.wks = wks =  gc.open_by_url(url)
    return wks

def get_named_range(named_range):
    arr={}
    for c in pvt_data.wks.named_range(named_range):
        if not c.row in arr: 
            arr[c.row]={}
        
        if not c.col in arr[c.row]: 
            arr[c.row][c.col]=c.value
        # arr[c.row].append(c.value)
    arr=list(map(lambda x:list(x.values()),arr.values()))
    return pd.DataFrame(arr[1:],columns=arr[0])

if __name__=='__main__':
    from dotenv import load_dotenv
    load_dotenv(verbose=True)

    print('main')
    open_url('https://docs.google.com/spreadsheets/d/1c4QkJmryNjxv4Ss7cRIoZSIbwJ6BYRWB9JE3-CIZ9ps/edit?gid=838891933')
    get_named_range()
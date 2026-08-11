"""
lib/user.py
-----------
Streamlit-side user model.

All Firestore and yfinance I/O is delegated to the FastAPI server via
lib.api_client.  No direct firebase-admin / yfinance imports here.
"""
from __future__ import annotations

import pandas as pd
from lib import api_client
from lib.config import PVT_PF_SAVE_COLS

from lib import now
from lib.yf import get_quote
from google.cloud import firestore
from copy import copy
from lib.database import db

# Re-exported so other modules that do `from lib.user import PVT_PF_SAVE_COLS`
# continue to work.
__all__ = ["User", "Accounts", "default_profile", "PVT_PF_SAVE_COLS"]

default_profile={
    "currency":"INR",
    "cash_balance": 1_00_00_000,
    "exchanges":["BSE","NSI"],
    "pvt_sheet_url": "",
    "pvt_named_range": "PF",
}

class User:
    
    profile={}
    tx_cols="ticker amount quantity date price type".split()
    def __init__(self, email,db_client=None):
        self.email=email
        if db_client == None:
            self.db_client=db.db_client
        else:
            self.db_client=db_client
    def __repr__(self):
        return f"<{self.email}>"

    def get_profile(self):
        self.profile.update(self.db_client.document(f'users/{self.email}'
                                           ).get().to_dict())
        return self.profile
    
    def create(self):
        data=copy(default_profile)
        data['createon']=now()
        print(data)
        return self.db_client.document(f'users/{self.email}'
                                           ).set(data)

    def update(self,**kw):
        kw.update({"lastlogged":now()})
        return self.db_client.document(f'users/{self.email}'
                                           ).update(kw)
        
    def add_transaction(self,ticker: str, quantity: int, price: float, amount: float):
    
        self.profile['cash_balance']+=amount
        self.db_client.document(f'users/{self.email}'
                                ).update(self.profile)
        
        if quantity * price == -amount:
            timestamp=now()
            ret = self.db_client.document(f'users/{self.email}/tx/{timestamp}'
                                            ).set(dict( date=now(),
                                                        ticker=ticker,
                                                        quantity=quantity,
                                                        price=price,
                                                        amount=amount))
            return timestamp
        else:
            raise Exception('For Buy: use -ve amount n +qty, for Sell use +ve amount n -qty')
    
    def list_transactions(self):
        data=[x.get().to_dict() for x in 
                self.db_client.collection(f'users/{self.email}/tx'
                                           ).list_documents()]
        for tx in data:
            tx['type']='Buy' if tx['quantity']>0 else 'Sell'

        if len(data):
            return pd.DataFrame(data )[self.tx_cols] 
        else:
            return pd.DataFrame([],columns=self.tx_cols)
    
    def get_portfolio(self, ) -> pd.DataFrame:
        data=self.list_transactions()
        if len(data):
            df=data[self.tx_cols[:3]].groupby(['ticker']).sum().reset_index()
            # print(df.apply(lambda r: r['ticker'], axis=1))
            df['lastPrice']=df.apply(lambda r: get_quote(r['ticker']).get('lastPrice'), axis=1)
            df['value']=df['lastPrice']*df['quantity']
            df['gain']=df['value']+df['amount']
            return df
        else:
            return pd.DataFrame()

    def update_cash_balance(self, 
                            start_bal: float= 1_00_00_000, 
                            txs= None) -> float:
        if not txs:
            txs=self.list_transactions()
        cost_basis=- txs.amount.sum().tolist()
        cash_balance=start_bal - cost_basis
        
        if cash_balance!=self.cash_balance:
            print(f"updating cash balance {self.cash_balance}->{cash_balance}",
            self.db_client.document(f'users/{self.email}'
                                        ).update({"cash_balance":cash_balance}))
        return cash_balance

            
    @property
    def cash_balance(self):
        if (ret:=self.profile.get('cash_balance',) ) != None:
            return ret
        return self.get_profile().get('cash_balance',)
               
    # ── Private portfolio (Firestore) ─────────────────────────────────────────

    def load_pvt_portfolio(self) -> pd.DataFrame:
        rows=[x.get().to_dict() for x in 
                self.db_client.collection(f'users/{self.email}/pvt_pf'
                                           ).list_documents()]
        # rows = api_client.get_pvt_pf(self.email)
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    def save_pvt_portfolio(self, df: pd.DataFrame) -> int:
        present = [c for c in PVT_PF_SAVE_COLS if c in df.columns]
        subset = df[present].copy() if present else df.copy()
        rows = subset.to_dict(orient="records")
        # 3. Initialize a write batch
        batch = self.db_client.batch()

        # 4. Loop through data and add to the batch
        for i,data in enumerate(rows):
            # Separate the custom document ID from the rest of the data
            doc_id = data.pop(i) 
            doc_ref = db.collection(f"users/{self.email}/pvt_pf/").document(doc_id)
            
            # Add the set operation to the batch
            batch.set(doc_ref, data)

        # 5. Commit all documents at once
        batch.commit()
        print(f"Successfully saved {len(rows)} documents.")
        self.pvt_pf = subset
        return len(rows)



        
class Accounts:
    @staticmethod
    def list_users():
        
        data=[{"id":x.id,**x.get().to_dict()} for x in 
                db.db_client.collection(f'users'
                                           ).list_documents()]
        return pd.DataFrame([x for x in data if not 'hide' in x] ) if len(data) \
            else pd.DataFrame([])
    
    @staticmethod
    def get_leaderboard():
        
        def get_pf_value(row):
            try:
                portfolio=User(row.id).get_portfolio()
                pf_value=portfolio['value'].sum()
            except:
                pf_value=0
            return pf_value
        
        ## method
        try:
            users=Accounts.list_users()
            users['portfolio'] = users.apply(get_pf_value,axis=1)
            users['total'] = users['portfolio'] + users['cash_balance'] 
        finally:
            return users
############################################################333            







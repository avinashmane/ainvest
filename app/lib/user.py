import pandas as pd
from lib import now
from yfinance import Ticker
from google.cloud import firestore
from copy import copy

default_profile={
    "currency":"INR",
    "cash_balance": 1_00_00_000,
    "exchanges":["BSE","NSI"]
}

class User:
    
    profile={}
    tx_cols="ticker amount quantity date price".split()
    def __init__(self, email,db_client=None):
        self.email=email
        if db_client == None:
            from lib.database import db
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
        timestamp=now()
        ret = self.db_client.document(f'users/{self.email}/tx/{timestamp}'
                                           ).set(dict(date=now(),
                                                         ticker=ticker,
                                                         quantity=quantity,
                                                         price=price,
                                                         amount=amount))
        return timestamp
    
    def list_transactions(self):
        data=[x.get().to_dict() for x in 
                self.db_client.collection(f'users/{self.email}/tx'
                                           ).list_documents()]
        # print(f'users/{self.email}/tx', data)
        return pd.DataFrame(data )[self.tx_cols] if len(data) \
            else pd.DataFrame([],columns=self.tx_cols)
    
    def get_portfolio(self):
        data=self.list_transactions()
        if len(data):
            df=data[self.tx_cols[:3]].groupby(['ticker']).sum().reset_index()
            # print(df.apply(lambda r: r['ticker'], axis=1))
            df['lastPrice']=df.apply(lambda r: Ticker(r['ticker']).fast_info.get('lastPrice') , 
                                    axis=1)
            df['value']=df['lastPrice']*df['quantity']
            df['gain']=df['value']+df['amount']
            
            # print(df)
            return df
        else:
            return pd.DataFrame()
    
    @property
    def cash_balance(self):
        return self.profile.get('cash_balance',default_profile["cash_balance"])

        
    
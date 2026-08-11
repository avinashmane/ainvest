import os
from agno.db.in_memory import InMemoryDb
from agno.db.firestore import FirestoreDb
from google.cloud.firestore import Client
from google.oauth2.service_account import Credentials
import json

creds=None

try: 
    cred_json=json.loads(os.getenv("GOOGLE_CRED_JSON"))
    creds=Credentials.from_service_account_info(cred_json)
except json.JSONDecodeError as e : 
    print(f"Error GOOGLE_CRED_JSON from env {e!r}")     
    creds=Credentials.from_service_account_file(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
except Exception as e : 
    print(f"Error google creds from env / file {e!r}")

db_client=Client(credentials=creds)

# 
db = FirestoreDb(db_client=db_client)


import os
from agno.db.in_memory import InMemoryDb
from agno.db.firestore import FirestoreDb
from google.cloud.firestore import Client
from google.oauth2.service_account import Credentials
import json

cred_json=json.loads(os.getenv("GOOGLE_CRED_JSON"))
try: creds=Credentials.from_service_account_info(cred_json)
except Exception as e : print(f"Error creds {e!r}")
db_client=Client(credentials=creds)
# Setup in-memory database
# db = InMemoryDb()

# 
db = FirestoreDb(db_client=db_client)
# db = FirestoreDb(project_id=os.getenv('PROJECT_ID','ainvest-avi'))


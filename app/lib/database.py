import os
from agno.db.in_memory import InMemoryDb
from agno.db.firestore import FirestoreDb
from google.cloud.firestore import Client
from google.oauth2.service_account import Credentials
import json

cred_json=json.loads(os.getenv("GOOGLE_CRED_JSON"))
creds=Credentials.from_service_account_info(cred_json)
db_client=Client(credentials=creds)
# Setup in-memory database
# db = InMemoryDb()

# 
db = FirestoreDb(db_client=db_client)
# db = FirestoreDb(project_id=os.getenv('PROJECT_ID','ainvest-avi'))
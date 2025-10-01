import os
from agno.db.in_memory import InMemoryDb
from agno.db.firestore import FirestoreDb
# Setup in-memory database
# db = InMemoryDb()

# 
db = FirestoreDb(project_id=os.getenv('PROJECT_ID','ainvest-avi'))
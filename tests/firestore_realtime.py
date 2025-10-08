# from google.cloud import firestore

# # Initialize Firestore DB client
# db = firestore.Client()
import os
root='/home/avinash/ainvest' #os.getenv("ROOT")
import sys
if not root in sys.path: sys.path.append(root)
# print(sys.path)
from app.lib.database import db

db=db.db_client


def on_snapshot(col_snapshot, changes, read_time):
    print(f"Callback received document snapshot: {read_time}")
    for change in changes:
        if change.type.name == 'ADDED':
            print(f"New document: {change.document.id} => {change.document.to_dict()}")
        elif change.type.name == 'MODIFIED':
            print(f"Modified document: {change.document.id} => {change.document.to_dict()}")
        elif change.type.name == 'REMOVED':
            print(f"Removed document: {change.document.id} => {change.document.to_dict()}")


doc_ref = db.collection('test').document('your_document_id')
doc_watch = doc_ref.on_snapshot(on_snapshot)



col_ref = db.collection('test')
col_watch = col_ref.on_snapshot(on_snapshot)



# To keep the listener active, you might need to add a loop or similar mechanism
# In a simple script, you might use:
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Listener stopped.")
    # Optionally, you can explicitly unsubscribe the listener
    # doc_watch.unsubscribe() or col_watch.unsubscribe()

import unittest
from lib.database import db
from agno.db.firestore import FirestoreDb
from datetime import date

class TestDatabase(unittest.TestCase):

    def test_db_instance(self):
        self.assertIsNotNone(db)

    def test_db_is_firestore(self):
        self.assertTrue(isinstance(db, FirestoreDb))

    def test_db_add(self):
        ret=''
        try:
            ret=db.db_client.collection('test'
                                        ).document(date.today().isoformat()
                                                   ).set({"a": date.today().isoformat()})
        except Exception as e:
            self.fail(f"conditions not met {e!r}")
        
    def test_sf(self):
        try:
            cities = db.db_client.collection("cities")

            sf_landmarks = cities.document("SF").collection("landmarks")
            sf_landmarks.document().set({"name": "Golden Gate Bridge", "type": "bridge"})
            sf_landmarks.document().set({"name": "Legion of Honor", "type": "museum"})
            la_landmarks = cities.document("LA").collection("landmarks")
            la_landmarks.document().set({"name": "Griffith Park", "type": "park"})
            la_landmarks.document().set({"name": "The Getty", "type": "museum"})
            dc_landmarks = cities.document("DC").collection("landmarks")
            dc_landmarks.document().set({"name": "Lincoln Memorial", "type": "memorial"})
            dc_landmarks.document().set(
                {"name": "National Air and Space Museum", "type": "museum"}
            )
            tok_landmarks = cities.document("TOK").collection("landmarks")
            tok_landmarks.document().set({"name": "Ueno Park", "type": "park"})
            tok_landmarks.document().set(
                {"name": "National Museum of Nature and Science", "type": "museum"}
            )
            bj_landmarks = cities.document("BJ").collection("landmarks")
            bj_landmarks.document().set({"name": "Jingshan Park", "type": "park"})
            bj_landmarks.document().set(
                {"name": "Beijing Ancient Observatory", "type": "museum"}
            )
        except Exception as e:
            self.fail( f'failed SF  {e!r}')

    def test_sf_del(self):
        try:
            cities = db.db_client.collection("cities")

            for doc in cities.list_documents():
                for coll in doc.collections():
                    for subdoc in coll.list_documents():
                        print(subdoc.path)#get().to_dict()) 
                        subdoc.delete()
                print(doc.path)
                doc.delete()
        except Exception as e:
            self.fail( f'failed SF  {e!r}')

if __name__ == '__main__':
    unittest.main()

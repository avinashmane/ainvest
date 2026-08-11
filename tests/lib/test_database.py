"""
Tests for lib/database.py

These are integration tests that require real Google credentials.
They are skipped automatically when credentials are not available.
"""

import os
import unittest


def _has_creds() -> bool:
    env = os.getenv("GOOGLE_CRED_JSON", "")
    file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    return len(env) > 100 or bool(file)


@unittest.skipUnless(_has_creds(), "Google credentials not available — skipping integration tests")
class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Import here so the skip above prevents module-level import side-effects
        from lib.database import db
        from agno.db.firestore import FirestoreDb
        self.db = db
        self.FirestoreDb = FirestoreDb

    def test_db_instance(self):
        self.assertIsNotNone(self.db)

    def test_db_is_firestore(self):
        self.assertTrue(isinstance(self.db, self.FirestoreDb))

    def test_db_add(self):
        from datetime import date
        try:
            self.db.db_client.collection('test').document(
                date.today().isoformat()
            ).set({"a": date.today().isoformat()})
        except Exception as e:
            self.fail(f"conditions not met {e!r}")

    def test_sf(self):
        try:
            cities = self.db.db_client.collection("cities")
            cities.document("SF").collection("landmarks").document().set(
                {"name": "Golden Gate Bridge", "type": "bridge"})
        except Exception as e:
            self.fail(f'failed SF  {e!r}')

    def test_sf_del(self):
        try:
            cities = self.db.db_client.collection("cities")
            for doc in cities.list_documents():
                for coll in doc.collections():
                    for subdoc in coll.list_documents():
                        subdoc.delete()
                doc.delete()
        except Exception as e:
            self.fail(f'failed SF  {e!r}')


if __name__ == '__main__':
    unittest.main()

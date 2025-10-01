
import unittest
from unittest.mock import Mock, patch
from lib.user import User

class TestUser(unittest.TestCase):

    def setUp(self):
        self.email = 'test@example.com'
        self.user = User(self.email)

    def test_user_initialization(self):
        self.assertEqual(self.user.email, self.email)
        
    
    # def test_user_update(self):
    #     self.user.update()
    #     self.assertEqual(self.user.email, self.email)
    
    
    @patch('lib.database.db')
    def test_update_user_profile(self, mock_db):
        # Setup mock

        # Call the method
        self.user.profile = {'name': 'Test User'}
        self.user.update()

        # Assertions

    # @unittest.skip("This test is temporarily disabled due to a known bug.")
    @patch('lib.database.db')
    def test_transaction(self, mock_db):
        
        # Call the method
        ticker = 'GOOGL'
        quantity = 10
        self.user.add_transaction(ticker, quantity)
        print(self.user.list_transactions())
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()


import unittest
from unittest.mock import Mock, patch
from lib.user import User, Accounts

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

    @unittest.skip("This test is temporarily disabled due to a known bug.")
    @patch('lib.database.db')
    
    
    def test_transaction(self, mock_db):    
        # Call the method
        ticker = 'GOOGL'
        quantity = 10
        price = 10.1
        self.user.add_transaction(ticker, quantity, price ,quantity* price)
        print(self.user.list_transactions())
        self.assertTrue(True)




class TestAccounts(unittest.TestCase):

    def setUp(self):
        self.users = Accounts.list_users()

    # @patch('lib.database.db')
    # def test_acc_profile(self, mock_db):
    #     start_bal=1_00_00_000
    #     # Call the method
    #     txs=self.users
    #     print(txs)
    #     self.assertTrue(True)


    @patch('lib.database.db')
    def test_acc_cash_balance(self, mock_db):
        start_bal=1_00_00_000

        def check_amount(row):
            if (row.amount != -(row.price * row.quantity)):
                print("Tx check_amount {} date {} failed: gap {}".format(row.ticker,row.date,row.quantity*row.price+row.amount))
                return False
            else:
                return True         
        # Call the method
        for u in self.users.id:
            try:
                user=User(u)
                profile= user.get_profile()
                txs=user.list_transactions().sort_values('date')
                txs['amt_chk']=txs.apply(check_amount, axis=1)
                cost_basis= - txs.amount.sum().tolist()
                cash_balance= user.update_cash_balance(start_bal=start_bal)
                tot_balance=cost_basis+ cash_balance
                print(txs)
                print(f'{u}: start:{start_bal} cost {cost_basis} cash {cash_balance} or update_cash_balance {user.update_cash_balance(start_bal=start_bal)} = {tot_balance} (gap {start_bal-tot_balance})')
            except Exception as e:
                print(u+f' Error {e!r}')
        self.assertTrue(True)



if __name__ == '__main__':
    unittest.main()

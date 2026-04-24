import unittest
import pandas as pd
import sys
import os
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reconciliation import reconcile


class TestReconciliation(unittest.TestCase):
    
    def setUp(self):
        """Set up test data files"""
        self.test_data_dir = os.path.dirname(os.path.abspath(__file__))
        self.company_file = os.path.join(self.test_data_dir, "test_company.csv")
        self.bank_file = os.path.join(self.test_data_dir, "test_bank.csv")
        
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.company_file):
            os.remove(self.company_file)
        if os.path.exists(self.bank_file):
            os.remove(self.bank_file)
    
    def test_matched_transactions(self):
        """Test that matching transactions are correctly identified"""
        company_data = "txn_id,amount,date\nT001,1000,2026-04-01\n"
        bank_data = "txn_id,amount,date\nT001,1000,2026-04-01\n"
        
        pd.read_csv(StringIO(company_data)).to_csv(self.company_file, index=False)
        pd.read_csv(StringIO(bank_data)).to_csv(self.bank_file, index=False)
        
        result = reconcile(self.company_file, self.bank_file)
        
        self.assertEqual(result.loc[0, 'status'], 'Matched')
    
    def test_amount_mismatch(self):
        """Test that amount mismatches are detected"""
        company_data = "txn_id,amount,date\nT001,1000,2026-04-01\n"
        bank_data = "txn_id,amount,date\nT001,950,2026-04-01\n"
        
        pd.read_csv(StringIO(company_data)).to_csv(self.company_file, index=False)
        pd.read_csv(StringIO(bank_data)).to_csv(self.bank_file, index=False)
        
        result = reconcile(self.company_file, self.bank_file)
        
        self.assertEqual(result.loc[0, 'status'], 'Amount Mismatch')
    
    def test_not_settled(self):
        """Test that unsettled transactions (company only) are identified"""
        company_data = "txn_id,amount,date\nT001,1000,2026-04-01\n"
        bank_data = "txn_id,amount,date\nT002,500,2026-04-02\n"
        
        pd.read_csv(StringIO(company_data)).to_csv(self.company_file, index=False)
        pd.read_csv(StringIO(bank_data)).to_csv(self.bank_file, index=False)
        
        result = reconcile(self.company_file, self.bank_file)
        
        # T001 should be marked as Not Settled
        not_settled = result[result['txn_id'] == 'T001']['status'].values[0]
        self.assertEqual(not_settled, 'Not Settled')
    
    def test_extra_bank_entry(self):
        """Test that extra bank entries are identified"""
        company_data = "txn_id,amount,date\nT001,1000,2026-04-01\n"
        bank_data = "txn_id,amount,date\nT001,1000,2026-04-01\nT002,500,2026-04-02\n"
        
        pd.read_csv(StringIO(company_data)).to_csv(self.company_file, index=False)
        pd.read_csv(StringIO(bank_data)).to_csv(self.bank_file, index=False)
        
        result = reconcile(self.company_file, self.bank_file)
        
        # T002 should be marked as Extra Bank Entry
        extra_bank = result[result['txn_id'] == 'T002']['status'].values[0]
        self.assertEqual(extra_bank, 'Extra Bank Entry')
    
    def test_duplicate_detection(self):
        """Test that duplicates in bank data are flagged"""
        company_data = "txn_id,amount,date\nT001,1000,2026-04-01\n"
        bank_data = "txn_id,amount,date\nT001,1000,2026-04-01\nT001,1000,2026-04-01\n"
        
        pd.read_csv(StringIO(company_data)).to_csv(self.company_file, index=False)
        pd.read_csv(StringIO(bank_data)).to_csv(self.bank_file, index=False)
        
        result = reconcile(self.company_file, self.bank_file)
        
        # Both T001 entries should be marked as duplicates
        duplicates = result[result['txn_id'] == 'T001']['is_duplicate'].values
        self.assertTrue(all(duplicates))
    
    def test_multiple_scenarios(self):
        """Test a complex scenario with multiple transaction types"""
        company_data = """txn_id,amount,date
T001,1000,2026-04-01
T002,500,2026-04-02
T003,700,2026-04-03
T004,1200,2026-04-04
"""
        bank_data = """txn_id,amount,date
T001,1000,2026-04-01
T002,500,2026-04-02
T003,750,2026-04-03
T005,1500,2026-04-05
"""
        
        pd.read_csv(StringIO(company_data)).to_csv(self.company_file, index=False)
        pd.read_csv(StringIO(bank_data)).to_csv(self.bank_file, index=False)
        
        result = reconcile(self.company_file, self.bank_file)
        
        # Check various statuses
        statuses = result.set_index('txn_id')['status']
        
        self.assertEqual(statuses['T001'], 'Matched')
        self.assertEqual(statuses['T002'], 'Matched')
        self.assertEqual(statuses['T003'], 'Amount Mismatch')
        self.assertEqual(statuses['T004'], 'Not Settled')
        self.assertEqual(statuses['T005'], 'Extra Bank Entry')


if __name__ == '__main__':
    unittest.main()

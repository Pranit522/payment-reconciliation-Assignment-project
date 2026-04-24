# Payment Reconciliation System

## Project Overview
A payment reconciliation system that identifies and categorizes discrepancies between company transaction records and bank settlement records.

## Problem Statement
A payments company's books don't balance at month end. The platform records transactions instantly when customers pay, but the bank batches and settles funds 1-2 days later. At month end, every transaction should have a matching settlement. This system finds why they don't match and shows where the gaps are.

## Solution Architecture

### Core Components

**1. Reconciliation Engine (`reconciliation.py`)**
- Reads company and bank transaction CSV files
- Performs outer merge on `txn_id` to capture all transactions
- Categorizes each transaction into one of 4 statuses:
  - **Matched**: Amount matches between company and bank
  - **Amount Mismatch**: Same transaction but different amounts
  - **Not Settled**: Transaction in company records but not yet in bank
  - **Extra Bank Entry**: Transaction in bank but not in company records
- Detects duplicate transactions in bank data using `txn_id`

**2. Web Dashboard (`app.py`)**
- Streamlit-based UI for running reconciliation
- Displays results in interactive dataframe
- Provides CSV download functionality
- Runs at `http://localhost:8503`

**3. Test Suite (`data/test_cases.py`)**
- 6 comprehensive unit tests covering all scenarios
- 100% pass rate
- Tests all transaction types and edge cases

### Assumptions Made

1. **Transaction ID (`txn_id`) is the primary matching key**
   - Assumption: Both systems use the same unique transaction identifier

2. **Date discrepancies are acceptable**
   - Assumption: 1-2 day settlement delay is normal; date differences don't cause mismatch

3. **Amount comparison is exact (no tolerance)**
   - Assumption: Any amount difference indicates a mismatch (could be rounding errors or partial refunds)

4. **Duplicates only occur in bank data**
   - Assumption: Company records are authoritative; duplicates appear in bank batching

5. **NULL/NaN indicates missing transaction**
   - Assumption: Using pandas merge to identify transactions missing from one side

6. **CSV format with columns: txn_id, amount, date**
   - Assumption: Consistent data structure across all input files

## Data Structure

### Input CSV Format
```csv
txn_id,amount,date
T001,1000,2026-04-01
T002,500,2026-04-02
```

### Output CSV Contains
```
txn_id, amount_company, amount_bank, status, is_duplicate, date_company, date_bank
```

## Gap Types Identified

1. **Transaction settled next month** - Marked as "Not Settled" (in company but not bank)
2. **Rounding differences** - Marked as "Amount Mismatch" 
3. **Duplicate entries** - Flagged with `is_duplicate = True`
4. **Refund with no matching original** - Marked as "Extra Bank Entry" (in bank but not company)

## Test Data

**Company Transactions** (`data/company_transactions.csv`):
- T001: 1000 (matched)
- T002: 500 (matched)
- T003: 700 (amount mismatch - bank shows 750)
- T004: 1200 (not settled - not in bank)
- T006: 500 (duplicate in bank)

**Bank Transactions** (`data/bank_transaction.csv`):
- T001: 1000 (matched)
- T002: 500 (matched)
- T003: 750 (amount mismatch)
- T005: 1500 (extra - not in company)
- T006: 500 (appears twice - duplicate)

## Results

| txn_id | Status | Reason |
|--------|--------|--------|
| T001 | Matched | Same amount in both |
| T002 | Matched | Same amount in both |
| T003 | Amount Mismatch | Company: 700, Bank: 750 |
| T004 | Not Settled | Only in company records |
| T005 | Extra Bank Entry | Only in bank records |
| T006 | Matched | Present in both (flagged as duplicate) |

## Test Cases

All tests located in `data/test_cases.py`:
- ✅ test_matched_transactions
- ✅ test_amount_mismatch
- ✅ test_not_settled
- ✅ test_extra_bank_entry
- ✅ test_duplicate_detection
- ✅ test_multiple_scenarios

Run tests: `python -m unittest data.test_cases -v`

## Production Considerations - What Would Get Wrong

1. **Rounding Precision**: Real-world systems may have rounding errors that don't appear in test data. The current exact-match approach could flag legitimate rounding discrepancies.

2. **Duplicate Handling**: Current logic flags duplicates but still processes them. Real systems might need to quarantine duplicates or provide exception handling workflows.

3. **Date Window Tolerance**: The system doesn't account for multi-day settlement windows. A transaction might be "not settled" but legitimately pending; we need configurable reconciliation windows.

## Files

- `reconciliation.py` - Core reconciliation logic
- `app.py` - Streamlit web interface
- `data/test_cases.py` - Test suite with 6 tests
- `data/company_transactions.csv` - Sample company data
- `data/bank_transaction.csv` - Sample bank data
- `output.csv` - Sample reconciliation output
- `requirements.txt` - Python dependencies

## Running the Project

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Run reconciliation script:**
```bash
python reconciliation.py
```

**3. Launch Streamlit dashboard:**
```bash
streamlit run app.py
```
Access at: `http://localhost:8503`

**4. Run tests:**
```bash
python -m unittest data.test_cases -v
```

## Deployment Status

✅ **Working**: Local deployment at `http://localhost:8503`
✅ **Code**: All files ready for submission
✅ **Tests**: All 6 tests passing (100%)
✅ **Output**: Sample output in `output.csv`

Features:
- Transaction Matching
- Duplicate Detection
- Missing Settlement
- Amount Mismatch

How to Run:
1. pip install -r requirements.txt
2. python reconciliation.py
3. streamlit run app.py
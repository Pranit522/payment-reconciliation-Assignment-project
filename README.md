# Payment Reconciliation System

## What's This Project?

This is a tool to match payments between what our company records and what the bank actually settled. Sometimes they don't match - maybe the bank hasn't processed it yet, or there's a rounding error. This tool finds all those mismatches.

## The Problem

At the end of every month, our payment records and the bank statements don't match up. The company records transactions instantly, but the bank takes 1-2 days to actually settle the funds. So we need to find out which transactions are still pending, which ones have amount mismatches, and which ones appear in the bank but not in our records.

## How It Works

**Main Code (`reconciliation.py`):**
- Takes two CSV files: company transactions and bank transactions
- Matches them by transaction ID
- Puts each transaction in one of 4 categories:
  - **Matched** - Same amount in both, all good
  - **Amount Mismatch** - Same transaction but different amounts (rounding issue? refund?)
  - **Not Settled** - We have it but the bank doesn't yet
  - **Extra Bank Entry** - Bank has it but we don't
- Also flags any duplicate transactions

**Dashboard (`app.py`):**
- Simple web interface using Streamlit
- Click a button to run the reconciliation
- Shows results in a table
- Can download the results as CSV
- Access it at `http://localhost:8503`

**Tests (`data/test_cases.py`):**
- 6 tests to make sure everything works
- All tests pass ✅

## Test Data

I created some sample data to test it:

**Company has these transactions:**
- T001: 1000 (matches bank)
- T002: 500 (matches bank)
- T003: 700 (bank shows 750 - oops!)
- T004: 1200 (bank doesn't have it yet)
- T006: 500 (appears twice in bank - duplicate)

**Bank has:**
- T001: 1000 (matches company)
- T002: 500 (matches company)
- T003: 750 (company shows 700)
- T005: 1500 (company doesn't have it)
- T006: 500 (shows up twice)

## Results

When you run it, you get:

| ID | Status | Why |
|----|--------|-----|
| T001 | Matched | Both have 1000 |
| T002 | Matched | Both have 500 |
| T003 | Mismatch | Company: 700, Bank: 750 |
| T004 | Not Settled | Only in company |
| T005 | Extra | Only in bank |
| T006 | Matched | Has both versions (flagged as duplicate) |

## How to Run

**1. Install what you need:**
```bash
pip install pandas streamlit
```

**2. Run the script:**
```bash
python reconciliation.py
```
This outputs the results to `output.csv`

**3. Run the web app:**
```bash
streamlit run app.py
```
Then go to `http://localhost:8503` and click the button

**4. Run the tests:**
```bash
python -m unittest data.test_cases -v
```
All 6 should pass ✅

## What Could Go Wrong in Real Life

1. **Rounding issues** - In real systems, amounts might be slightly different due to rounding. Right now we do an exact match, so any small difference gets flagged as a mismatch.

2. **Settlement time** - We assume 1-2 days is normal, but some systems might need more time. We're hardcoding the timeframe instead of making it flexible.

3. **Duplicates** - When we find duplicates, we just flag them and keep going. Real systems would probably need to quarantine them and have someone manually check what happened.

## Files Included

- `reconciliation.py` - The main logic
- `app.py` - The web interface
- `data/test_cases.py` - All the tests
- `data/company_transactions.csv` - Sample company data
- `data/bank_transaction.csv` - Sample bank data
- `output.csv` - The results
- `requirements.txt` - Dependencies

That's it!

import pandas as pd

def reconcile(company_path, bank_path):

    company = pd.read_csv(company_path)
    bank = pd.read_csv(bank_path)

    # Duplicate detection
    bank['is_duplicate'] = bank.duplicated(subset=['txn_id'], keep=False)

    merged = company.merge(
        bank,
        on="txn_id",
        how="outer",
        suffixes=('_company', '_bank')
    )

    results = []

    for _, row in merged.iterrows():

        if pd.isna(row['amount_company']):
            status = "Extra Bank Entry"

        elif pd.isna(row['amount_bank']):
            status = "Not Settled"

        elif row['amount_company'] == row['amount_bank']:
            status = "Matched"

        else:
            status = "Amount Mismatch"

        results.append(status)

    merged['status'] = results

    return merged


if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output = reconcile(
        os.path.join(base_dir, "data/company_transactions.csv"),
        os.path.join(base_dir, "data/bank_transaction.csv")
    )

    output.to_csv("output.csv", index=False)
    print(output)
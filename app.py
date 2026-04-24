import streamlit as st
import pandas as pd
from reconciliation import reconcile

st.title("💳 Payment Reconciliation Dashboard")

if st.button("Run Reconciliation"):

    df = reconcile(
        "data/company_transactions.csv",
        "data/bank_transaction.csv"
    )

    st.dataframe(df)

    st.download_button(
        "Download Output",
        df.to_csv(index=False),
        file_name="output.csv"
    )
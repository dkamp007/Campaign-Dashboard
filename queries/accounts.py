import streamlit as st
from utils.db import run_query

# --- Caching functions to improve performance ---

@st.cache_data(ttl=21600)
def get_bing_accounts():
    query = "select distinct account_id, account_name from bingads_account_master order by account_name asc"
    df = run_query(query)
    return df.set_index('account_name')['account_id'].to_dict()
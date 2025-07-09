import streamlit as st
from utils.db import run_query

# --- Caching functions to improve performance ---

@st.cache_data(ttl=21600)
def fetch_user_mapping():
    query = "select distinct id, name from users order by name asc"
    df = run_query(query)
    return df.set_index('name')['id'].to_dict()

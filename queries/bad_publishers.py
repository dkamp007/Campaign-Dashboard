import streamlit as st
from utils.db import run_query
from queries.publishers_stats import fetch_publisher_report

# ---Caching for better performance---

@st.cache_data(ttl=21600)
def bad_publishers_report(start_date, end_date, user_id=None, campaign_names=None, account_id=None):

    conditions = [f"a.api_data_date BETWEEN '{start_date}' AND '{end_date}'"]

    if account_id:
        account_list = ','.join(map(str, account_list))
        conditions.append(f"a.account_id IN ({account_list})")
    if user_id:
        user_conditions = ','.join(map(str, user_conditions))
        conditions.append(f"b.user_id IN ({user_conditions})")
    if campaign_names:
        campaign_list = ','.join(campaign_list)
        conditions.append(f"a.campaign_names IN ({campaign_list})")

    where_clause = ' AND '.join(conditions)

    query = f"""
        
    """

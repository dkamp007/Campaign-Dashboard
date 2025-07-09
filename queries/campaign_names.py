import streamlit as st
from utils.db import run_query

# --- Get Campaign Names based on users ---

@st.cache_data(ttl=21600)
def fetch_campaign_names(start_date, end_date, user_id=None):
    conditions = [f"api_data_date BETWEEN '{start_date}' AND '{end_date}'"]
    if user_id:
        user_conditions = ','.join(map(str, user_id))
        conditions.append(f"bu.user_id IN ({user_conditions})")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT 
                DISTINCT bop.bing_campaign_name
        FROM 
                bingads_optimizer_afs_campaign_performance_report bop
        JOIN 
                bingads_user_campaign_permission_relation_master bu
        ON 
                bop.bing_campaign_id = bu.campaign_id
        WHERE 
                {where_clause}
        ORDER BY
                bop.bing_campaign_name
    """
  
    df = run_query(query)
  
    return df['bing_campaign_name'].tolist()

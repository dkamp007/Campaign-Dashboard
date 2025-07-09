import streamlit as st
from utils.db import run_query

# --- Get overall spend & tcl-revenue data for charts ---

@st.cache_data(ttl=21600)
def fetch_overall_trend_data(start_date, end_date):
    query = f"""
        SELECT
            bop.api_data_date AS Date,
            SUM(bop.bing_spend) AS Spend,
            SUM(bop.tcl_revenue) AS TCL
        FROM
            bingads_optimizer_afs_campaign_performance_report bop
        WHERE
            bop.api_data_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY
            bop.api_data_date
        ORDER BY
            bop.api_data_date ASC
    """
    
    df_overall = run_query(query)
    
    return df_overall

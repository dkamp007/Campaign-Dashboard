import streamlit as st
from utils.db import run_query

# --- Get aggregated daily stats bases on users & campaign names ---

@st.cache_data(ttl=21600)
def fetch_aggregated_daily_data(start_date, end_date, user_ids=None, campaign_names=None):
    conditions = [f"bop.api_data_date BETWEEN '{start_date}' AND '{end_date}'"]
    if user_ids:
        user_conditions = ','.join(map(str, user_ids))
        conditions.append(f"bu.user_id IN ({user_conditions})")
    if campaign_names:
        campaign_list = "', '".join(campaign_names)
        conditions.append(f"bop.bing_campaign_name IN ('{campaign_list}')")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            bop.api_data_date AS Date,
            SUM(bop.bing_impressions) AS Impr,
            SUM(bop.bing_clicks) AS Clicks,
            SUM(bop.bing_spend) AS Spend,
            SUM(bop.tcl_revenue) AS TCL,
            SUM(bop.afs_estimated_earnings) AS AFS,
            ROUND(SUM(bop.afs_estimated_earnings) - SUM(bop.bing_spend), 2) AS PL_AFS,
            ROUND(SUM(bop.tcl_revenue) - SUM(bop.bing_spend), 2) AS PL_TCL,
            ROUND((SUM(bop.afs_estimated_earnings) - SUM(bop.bing_spend)) / NULLIF(SUM(bop.bing_spend), 0) * 100, 2) AS ROI_AFS,
            ROUND((SUM(bop.tcl_revenue) - SUM(bop.bing_spend)) / NULLIF(SUM(bop.bing_spend), 0) * 100, 2) AS ROI_TCL
        FROM
            bingads_optimizer_afs_campaign_performance_report bop
        JOIN
            bingads_user_campaign_permission_relation_master bu
            ON bop.bing_campaign_id = bu.campaign_id
        WHERE {where_clause}
        GROUP BY bop.api_data_date
        ORDER BY bop.api_data_date DESC
    """

    df = run_query(query)
    return df

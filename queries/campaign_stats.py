import streamlit as st
from utils.db import run_query

# --- Get campaign level data for detailed view ---

@st.cache_data(ttl=21600)
def fetch_data(start_date, end_date, user_ids=None, campaign_names=None, account_id=None):
    conditions = [f"bop.api_data_date BETWEEN '{start_date}' AND '{end_date}'"]
    if account_id:
        account_list = "', '".join(map(str, account_id))
        conditions.append(f"bop.bing_account_id IN ('{account_list}')")
    if user_ids:
        user_conditions = ','.join(map(str, user_ids))
        conditions.append(f"bu.user_id IN ({user_conditions})")
    if campaign_names:
        campaign_list = "', '".join(campaign_names)
        conditions.append(f"bop.bing_campaign_name IN ('{campaign_list}')")

    where_clause = " AND ".join(conditions)

    query = f"""
        WITH AggregatedData AS (
            SELECT
                bop.api_data_date AS Date,
                bop.bing_campaign_name AS Campaign,
                SUM(bop.bing_impressions) AS Impr,
                SUM(bop.bing_spend) AS Spend,
                SUM(bop.pbt_adclick_count) AS Clicks,
                SUM(bop.tcl_revenue) AS TCL,
                SUM(bop.afs_estimated_earnings) AS AFS
            FROM
                bingads_optimizer_afs_campaign_performance_report bop
            JOIN
                bingads_user_campaign_permission_relation_master bu
                ON bop.bing_campaign_id = bu.campaign_id
            WHERE {where_clause}
            GROUP BY bop.api_data_date, bop.bing_campaign_name
        ),
        RevenueChanges AS (
            SELECT *,
                LAG(Impr) OVER (PARTITION BY Campaign ORDER BY Date) AS y_Impr,
                LAG(Clicks) OVER (PARTITION BY Campaign ORDER BY Date) AS y_Clicks,
                LAG(Spend) OVER (PARTITION BY Campaign ORDER BY Date) AS y_Spend,
                LAG(TCL) OVER (PARTITION BY Campaign ORDER BY Date) AS y_TCL,
                LAG(AFS) OVER (PARTITION BY Campaign ORDER BY Date) AS y_AFS
            FROM AggregatedData
        )
        SELECT
            Date,
            Campaign,
            Impr,
            ROUND((Impr - y_Impr)/NULLIF(y_Impr, 0)*100, 2) AS Impr_Δ,
            Clicks,
            ROUND((Clicks - y_Clicks)/NULLIF(y_Clicks, 0)*100, 2) AS Clicks_Δ,
            Spend,
            ROUND((Spend - y_Spend)/NULLIF(y_Spend, 0)*100, 2) AS Spend_Δ,
            TCL,
            ROUND((TCL - y_TCL)/NULLIF(y_TCL, 0)*100, 2) AS TCL_Δ,
            AFS,
            ROUND((AFS - y_AFS)/NULLIF(y_AFS, 0)*100, 2) AS AFS_Δ,
            ROUND(AFS - Spend, 2) AS PL_AFS,
            ROUND(TCL - Spend, 2) AS PL_TCL,
            ROUND((AFS - Spend)/NULLIF(Spend, 0)*100, 2) AS ROI_AFS,
            ROUND((TCL - Spend)/NULLIF(Spend, 0)*100, 2) AS ROI_TCL
        FROM RevenueChanges
        ORDER BY Date DESC
    """

    df = run_query(query)
    return df

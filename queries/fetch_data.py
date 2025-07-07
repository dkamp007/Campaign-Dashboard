import streamlit as st
from utils.db import run_query

# --- Caching functions to improve performance ---

# --- Get User Data ---

@st.cache_data(ttl=21600)
def fetch_user_mapping():
    query = "select distinct id, name from users order by name asc"
    df = run_query(query)
    return df.set_index('name')['id'].to_dict()




# --- Get Campaign Names based on users ---

@st.cache_data(ttl=21600)
def fetch_campaign_names(start_date, end_date, user_id=None):
    conditions = [f"api_data_date BETWEEN '{start_date}' AND '{end_date}'"]
    if user_id:
        user_conditions = ','.join(map(str, user_id))
        conditions.append(f"bu.user_id IN ({user_conditions})")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT DISTINCT bop.bing_campaign_name
        FROM bingads_optimizer_afs_campaign_performance_report bop
        JOIN bingads_user_campaign_permission_relation_master bu
            ON bop.bing_campaign_id = bu.campaign_id
        WHERE {where_clause}
        ORDER BY bop.bing_campaign_name
    """
    df = run_query(query)
    return df['bing_campaign_name'].tolist()




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




# --- Get campaign level data for detailed view ---

@st.cache_data(ttl=21600)
def fetch_data(start_date, end_date, user_ids=None, campaign_names=None):
    conditions = [f"bop.api_data_date BETWEEN '{start_date}' AND '{end_date}'"]
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
                SUM(bop.bing_clicks) AS Clicks,
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




# --- Get publishers' report ---

@st.cache_data(ttl=21600)
def fetch_publisher_report(start_date, end_date, user_id=None, campaign_names=None):
    
    conditions = [f"a.api_data_date BETWEEN '{start_date}' AND '{end_date}'"]
    if user_id:
        user_conditions = ','.join(map(str, user_id))
        conditions.append(f"b.user_id IN ({user_conditions})")
    if campaign_names:
        campaign_list = "', '".join(campaign_names)
        conditions.append(f"a.campaign_name IN ('{campaign_list}')")

    where_clause = " AND ".join(conditions)
    
    query = f"""
        select 
            a.api_data_date as Date, 
            a.campaign_name as Campaign, 
            a.ad_group_name as `Ad Group`, 
            a.final_main_domain as Publisher, 
            a.blocked_at_ad_group as `Blocked (Ad Group)`, 
            a.blocked_at_campaign as `Blocked (Campaign)`, 
            sum(a.bing_impression) as Impr, 
            sum(a.pbt_adclick_count) as Clicks, 
            round(sum(a.bing_spend), 2) as Spend, 
            round(sum(a.tcl_revenue), 2) as Revenue, 
            round((sum(a.tcl_revenue)-sum(a.bing_spend)), 2) as PnL, 
            round(((sum(a.tcl_revenue)-sum(a.bing_spend))/sum(a.bing_spend))*100, 2) as ROI 
        from bingads_optimizer_afs_pub_report a
        join bingads_user_campaign_permission_relation_master b 
        on a.campaign_id = b.campaign_id 
        where {where_clause}
        group by a.api_data_date, a.final_main_domain 
        order by a.api_data_date desc
    """
    df_publisher = run_query(query)
    return df_publisher

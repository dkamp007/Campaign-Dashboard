import streamlit as st
from utils.db import run_query

# --- Get publishers' report ---

@st.cache_data(ttl=21600)
def fetch_publisher_report(start_date, end_date, user_id=None, campaign_names=None, account_id=None):
    
    conditions = [f"a.api_data_date BETWEEN '{start_date}' AND '{end_date}'"]
    if account_id:
        account_list = ','.join(map(str, account_id))
        conditions.append(f"a.account_id IN ({account_list}))
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

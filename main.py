import streamlit as st
import pandas as pd
from datetime import date, timedelta
from streamlit_extras.metric_cards import style_metric_cards
from queries.campaign_stats import fetch_data
from queries.daily_stats import fetch_aggregated_daily_data
from queries.chart_data import fetch_overall_trend_data
from queries.publishers_stats import fetch_publisher_report
from components.sidebar_filters import render_sidebar_filters
from components.kpis import render_kpi_block
from components.charts import render_line_chart
from components.tabs import render_data_tabs


# --- Streamlit Config ---
st.set_page_config(page_title="📊 Campaign Dashboard", layout="wide")



# --- Apply Styling ---
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("`style.css` not found. Some custom styling may be missing.")



# --- Sidebar Filters ---
start_date, end_date, user_id_selection, campaign_name_selection = render_sidebar_filters()



# --- Fetch Core Data ---
df_campaign_table = fetch_data(start_date, end_date, user_id_selection, campaign_name_selection)

df_daily_aggregated = fetch_aggregated_daily_data(start_date, end_date, user_id_selection, campaign_name_selection)

df_pub_data = fetch_publisher_report(start_date, end_date, user_id_selection, campaign_name_selection)



# --- Determine if Overall or Filtered Charts Should Be Used ---
is_filtered_by_campaigns = bool(campaign_name_selection)
is_filtered_by_users = bool(user_id_selection)


if not is_filtered_by_campaigns and not is_filtered_by_users:
    df_for_charts = fetch_overall_trend_data(start_date, end_date)
    chart_title_suffix = " (Overall Performance)"
else:
    if not df_campaign_table.empty:
        df_for_charts = df_campaign_table.groupby("Date", as_index=False).agg({"Spend": "sum", "TCL": "sum"})
    else:
        df_for_charts = pd.DataFrame(columns=["Date", "Spend", "TCL"])
    chart_title_suffix = " (Filtered Performance)"



# --- Main Dashboard ---
if not df_campaign_table.empty:
    st.title("📊 Campaign :green[Performance] Dashboard")
    st.markdown("Analyze your Bing Ads campaign performance across key metrics and time periods.")
    st.divider()

    # --- KPI Cards ---
    render_kpi_block(df_campaign_table, start_date, end_date, user_id_selection, campaign_name_selection)

    st.divider()

    # --- Line Chart ---
    render_line_chart(df_for_charts, chart_title_suffix)

    st.divider()

    # --- Report Tabs ---
    st.subheader("📅 Campaign Report Table")
    render_data_tabs(df_daily_aggregated, df_campaign_table, df_pub_data, start_date, end_date, user_id_selection, campaign_name_selection)

else:
    st.warning("No data found for the selected filters. Please adjust the dates, user IDs, or campaign names.")

st.divider()
st.caption("Crafted with ❤️ by **dkamp007**")

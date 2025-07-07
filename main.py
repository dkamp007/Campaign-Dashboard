import streamlit as st
import pandas as pd
from utils.db import run_query
from queries.fetch_data import fetch_user_mapping, fetch_campaign_names, fetch_overall_trend_data, fetch_aggregated_daily_data, fetch_data, fetch_publisher_report
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import date, timedelta
from streamlit_extras.metric_cards import style_metric_cards


st.set_page_config(page_title="📊 Campaign Dashboard", layout="wide")

# --- Fetching Style.css ---
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("`style.css` not found. Some custom styling may be missing.")



# --- SIDEBAR FILTERS ---
st.sidebar.title("Welcome! This is the Dashboard of Bing Reports")
st.sidebar.markdown('Play around with the filters for more details.')



# --- QUICK FILTER LOGIC ---
today = date.today()

with st.sidebar.expander("**Quick Date Filters**", expanded=False):
    date_range_option = st.radio(
        'Select a period',
        ["Last 7 Days", "Last 15 Days", "Last 30 Days", "Last 60 Days", "Last 90 Days"],
        label_visibility='collapsed',
        index=2)
    
    num_days_map = {
            "Last 7 Days": 7,
            "Last 15 Days": 15,
            "Last 30 Days": 30,
            "Last 60 Days": 60,
            "Last 90 Days": 90}
    
    days_offset = num_days_map.get(date_range_option, 30) # Default to 30 if key not found
    
    quick_filter_start_date = today - timedelta(days=days_offset)
    
    quick_filter_end_date = today



# --- MANUAL DATE INPUTS ---
# These inputs will be pre-filled by the quick filters, but can be manually overridden.

with st.sidebar.expander('**Custom Date Range**', expanded=False):
    custom_start_date = st.date_input(
        "Start Date",
        value=quick_filter_start_date, # Default from quick filter
        max_value=today,
        key='custom_start_date' # Important for Streamlit to track state
    )
    custom_end_date = st.date_input(
        "End Date",
        value=quick_filter_end_date,
        max_value=today,
        key='custom_end_date'
    )

# The `start_date` and `end_date` used by data fetching will be the values from manual inputs.
# If manual inputs haven't been touched, they'll reflect the quick filter.
    
start_date = custom_start_date
end_date = custom_end_date

# Calculate and display the number of days for the *final* selected period
num_days_selected = (end_date - start_date).days
st.sidebar.markdown(f"**Selected period:** :blue[{num_days_selected} days]")



# --- USER FILTER USING NAME-TO-ID MAPPING ---
user_mapping = fetch_user_mapping()
all_user_names = list(user_mapping.keys())

with st.sidebar.expander('**User Selection**', expanded=False):
    if 'user_selection_all_checked' not in st.session_state:
        st.session_state.user_selection_all_checked = True
    if 'current_user_names' not in st.session_state:
        st.session_state.current_user_names = all_user_names

    select_all_users = st.checkbox("Select All Users", value=st.session_state.user_selection_all_checked)

    if select_all_users:
        selected_user_names = all_user_names
    else:
        selected_user_names = st.multiselect(
            "Select User(s)",
            all_user_names,
            default=st.session_state.current_user_names
        )
    
    st.session_state.current_user_names = selected_user_names
    st.session_state.user_selection_all_checked = select_all_users

# Finally map selected names to IDs
user_id_selection = [user_mapping[name] for name in selected_user_names]


# --- CAMPAIGN NAME FILTER ---
# Fetch campaigns based on selected dates & user_ids

campaign_options = fetch_campaign_names(start_date, end_date, user_id_selection if user_id_selection else None)

with st.sidebar.expander('**Campaign Selection**', expanded=False):
    # Use session_state for campaign selection as well
    if 'campaign_selection_all_checked' not in st.session_state:
        st.session_state.campaign_selection_all_checked = True
    if 'current_campaign_names' not in st.session_state:
        st.session_state.current_campaign_names = campaign_options # Default to all initially

    select_all_campaigns = st.checkbox("Select All Campaigns", 
                                       value=st.session_state.campaign_selection_all_checked,
                                       key='select_all_campaigns_checkbox')

    if select_all_campaigns:
        campaign_name_selection = campaign_options
        st.session_state.current_campaign_names = campaign_options
    else:
        campaign_name_selection = st.multiselect(
            "Select Campaign Names",
            campaign_options,
            default=st.session_state.current_campaign_names,
            key='campaign_name_multiselect'
        )
        st.session_state.current_campaign_names = campaign_name_selection

    st.session_state.campaign_selection_all_checked = select_all_campaigns



# --- Fetching data for KPIs, report tables & Charts ---

df_table = fetch_data(start_date, end_date, user_id_selection, campaign_name_selection)


is_filtered_by_campaigns_charts = bool(campaign_name_selection and len(campaign_name_selection) < len(campaign_options))

is_filtered_by_users_charts = bool(user_id_selection and len(user_id_selection) < len(list(user_mapping.values())))


if not is_filtered_by_campaigns_charts and not is_filtered_by_users_charts:
    df_for_charts = fetch_overall_trend_data(start_date, end_date)
    chart_title_suffix = " (Overall Performance)"
else:
    if not df_table.empty:
        df_for_charts = df_table.groupby("Date", as_index=False).agg({"Spend": "sum", "TCL": "sum"})
    else:
        df_for_charts = pd.DataFrame(columns=['Date', 'Spend', 'TCL'])
    
    chart_title_suffix = " (Filtered Performance)"



# --- MAIN DASHBOARD CONTENT ---

if not df_table.empty: # Use df_table for KPI calculations as it has all relevant columns
    st.title("📊 Campaign :green[Performance] Dashboard")
    st.markdown("Analyze your Bing Ads campaign performance across key metrics and time periods.")

    st.divider()

    # --- KPI Metrics Columns ---
    col1, col2, col3, col4 = st.columns(4)

    # --- Metrics ---
    
    total_spend = df_table['Spend'].sum()
    
    total_tcl = df_table['TCL'].sum()
    
    total_profit_tcl = total_tcl - total_spend
    
    roi_tcl = (total_profit_tcl / total_spend * 100) if total_spend != 0 else 0

    
    # --- Calculate previous period dates for KPI comparison ---
    period_length = (end_date - start_date).days + 1
    
    prev_end_date = start_date - timedelta(days=1)
    
    prev_start_date = prev_end_date - timedelta(days=period_length - 1)

    
    prev_df = fetch_data(prev_start_date, prev_end_date, user_id_selection, campaign_name_selection)

    prev_spend = prev_df['Spend'].sum() if not prev_df.empty else 0
    
    prev_tcl = prev_df['TCL'].sum() if not prev_df.empty else 0
    
    prev_profit_tcl = prev_tcl - prev_spend
    
    prev_roi_tcl = (prev_profit_tcl / prev_spend * 100) if prev_spend != 0 else 0

    
    # --- Calculate percentage changes ---
    def calc_pct_change(current, previous):
        if previous == 0 or pd.isna(previous):
            return None
        return (current - previous) / previous * 100

    spend_pct_change = calc_pct_change(total_spend, prev_spend)
    
    tcl_pct_change = calc_pct_change(total_tcl, prev_tcl)
    
    profit_pct_change = calc_pct_change(total_profit_tcl, prev_profit_tcl)
    
    roi_pct_change = calc_pct_change(roi_tcl, prev_roi_tcl)

    
    # --- Display KPI metrics with delta using custom HTML ---
    def format_kpi_metric(value, pct_change):
        formatted_value = f"${value:,.2f}" if isinstance(value, (int, float)) else str(value)
        
        if pct_change is None:
            
            return formatted_value, '<span class="kpi-change neutral">N/A</span>'
        
        color_class = "positive" if pct_change >= 0 else "negative"
        
        sign = "+" if pct_change >= 0 else ""
        
        delta_html = f'<span class="kpi-change {color_class}">{sign}{pct_change:.2f}%</span>'
        
        return formatted_value, delta_html

    spend_val, spend_delta_html = format_kpi_metric(total_spend, spend_pct_change)
        
    tcl_val, tcl_delta_html = format_kpi_metric(total_tcl, tcl_pct_change)
    
    profit_val, profit_delta_html = format_kpi_metric(total_profit_tcl, profit_pct_change)
    
    roi_val_display = f"{roi_tcl:.2f}%"
    
    roi_delta_html = "N/A" # Default for ROI, handled separately if `roi_pct_change` is not None
    
    if roi_pct_change is not None:
        roi_color_class = "positive" if roi_pct_change >= 0 else "negative"
        
        roi_sign = "+" if roi_pct_change >= 0 else ""
        
        roi_delta_html = f'<span class="kpi-change {roi_color_class}">{roi_sign}{roi_pct_change:.2f}%</span>'


    # Using custom HTML for KPI cards
    col1.markdown(f"""
                    <div class="kpi-container">
                      <div class="kpi-card">
                        <div class="kpi-title">Total Spend</div>
                        <div class="kpi-value">{spend_val}</div>
                        {spend_delta_html}
                      </div>
                    </div>""", unsafe_allow_html=True)

    col2.markdown(f"""
                    <div class="kpi-container">
                      <div class="kpi-card">
                        <div class="kpi-title">TCL Revenue</div>
                        <div class="kpi-value">{tcl_val}</div>
                        {tcl_delta_html}
                    </div>
                    </div>""", unsafe_allow_html=True)

    col3.markdown(f"""
                    <div class="kpi-container">
                      <div class="kpi-card">
                        <div class="kpi-title">TCL Profit</div>
                        <div class="kpi-value">{profit_val}</div>
                        {profit_delta_html}
                    </div>
                    </div>""", unsafe_allow_html=True)

    col4.markdown(f"""
                    <div class="kpi-container">
                      <div class="kpi-card">
                        <div class="kpi-title">ROI TCL</div>
                        <div class="kpi-value">{roi_val_display}</div>
                        {roi_delta_html}
                      </div>
                    </div>""", unsafe_allow_html=True)

    st.divider()

    
    # --- LINE CHART (Spend vs TCL) ---
    st.markdown("### :chart_with_upwards_trend: Trends")

    if not df_for_charts.empty:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=df_for_charts['Date'], y=df_for_charts['Spend'], name="💸 Spend", line=dict(color="darkorange")),
            secondary_y=False,)

        fig.add_trace(
            go.Scatter(x=df_for_charts['Date'], y=df_for_charts['TCL'], name="📈 TCL Revenue", line=dict(color="royalblue")),
            secondary_y=True,)

        fig.update_layout(
            title=f"📈 Spend vs TCL Over Time{chart_title_suffix}",
            template="plotly_white",
            height=470,
            xaxis=dict(title='Date'),
            yaxis = dict(title='Spend ($)'),
            yaxis2 = dict(title='TCL Revenue ($)', overlaying='y', side='right'),
            legend=dict(x=1, y=1.02, orientation="h", yanchor="bottom", xanchor="right"))

        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Spend ($)", secondary_y=False, showgrid=True)
        fig.update_yaxes(title_text="TCL Revenue ($)", secondary_y=True, showgrid=False)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available to display trends based on the current selection.")

    
    
    st.divider()



    # --- Replace existing Data Table section at the end ---
    st.subheader("📅 Campaign Report Table")
    
    
    # --- Styling Logic for DataFrame ---
          
    def color_percentage_change(val):
        if pd.isna(val):
            return ''
        if isinstance(val, (int, float)):
            if val > 0:
                return 'color: green; font-weight: bold;'
            elif val < 0:
                return 'color: red; font-weight: bold;'
        return ''
    
    percentage_cols = ['Impr_Δ', 'Clicks_Δ', 'Spend_Δ', 'TCL_Δ', 'AFS_Δ']
    roi_cols = ['ROI_AFS', 'ROI_TCL']
    pnl_cols = ['PL_AFS', 'PL_TCL']
    pub_pnl_cols = ['PnL']
    pub_roi_cols = ['ROI']
    
    def color_pnl(val):
        if pd.isna(val):
            return ''
        if isinstance(val, (int, float)):
            if val > 0:
                return 'color: green; font-weight: bold;'
            elif val < 0:
                return 'color: red; font-weight: bold;'
        return ''
    
    
    
    df_aggregated = fetch_aggregated_daily_data(start_date, end_date, user_id_selection, campaign_name_selection)
    
    # --- Data tabs ---
    tab1, tab2, tab3 = st.tabs(["📅 Daily Aggregated", "📋 Campaign Breakdown", '📑 Publishers Breakdown'])
    
    with tab1:
        st.markdown("### 🔄 Daily Aggregated View")
        st.dataframe(df_aggregated.style \
                     .map(color_pnl, subset=pnl_cols) \
                     .map(color_percentage_change, subset=roi_cols) \
                     .background_gradient(cmap='Greens', subset=['TCL', 'AFS'], low=0.2, high=0.4) \
                     .background_gradient(cmap='Oranges', subset=['Spend'], low=0.2, high=0.8) \
                     .bar(subset=['PL_AFS', 'PL_TCL'], align='zero', color=['#FF6347', '#7CFC00']) \
                     .format({
            'Date': lambda x: x.strftime("%Y-%m-%d") if isinstance(x, (pd.Timestamp, date)) else x,
            "Impr": "{:,.0f}", "Clicks": "{:,.0f}", 'Spend': "${:,.2f}", 'TCL': "${:,.2f}", 'AFS': "${:,.2f}",
            'PL_AFS': "${:,.2f}", 'PL_TCL': "${:,.2f}", 'ROI_AFS': "{:.2f}%", 'ROI_TCL': "{:.2f}%"
        }), use_container_width=True, hide_index=True)
    
    with tab2:
        st.markdown("### 🎯 Campaign-level View")
        styled_df = df_table.style \
                            .map(color_percentage_change, subset=percentage_cols) \
                            .map(color_percentage_change, subset=roi_cols) \
                            .map(color_pnl, subset=pnl_cols) \
                            .background_gradient(cmap='Greens', subset=['Impr', 'Clicks', 'TCL', 'AFS'], low=0.2, high=0.4) \
                            .background_gradient(cmap='Oranges', subset=['Spend'], low=0.2, high=0.8) \
                            .bar(subset=['PL_AFS', 'PL_TCL'], align='zero', color=['#FF6347', '#7CFC00']) \
                            .format({
                                'Date': lambda x: x.strftime("%Y-%m-%d") if isinstance(x, (pd.Timestamp, date)) else x,
                                "Impr": "{:,.0f}", "Clicks": "{:,.0f}", 'Spend': "${:,.2f}", 'TCL': "${:,.2f}", 
                                'AFS': "${:,.2f}", 'PL_AFS': "${:,.2f}", 'PL_TCL': "${:,.2f}", 'Impr_Δ': "{:.2f}%", 
                                'Clicks_Δ': "{:.2f}%", 'Spend_Δ': "{:.2f}%", 'TCL_Δ': "{:.2f}%", 'AFS_Δ': "{:.2f}%", 
                                'ROI_AFS': "{:.2f}%", 'ROI_TCL': "{:.2f}%"
                            })
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)


    with tab3:
        st.markdown('### 📑 Publishers-level View')

        # --- Fetch Publisher Report Early ---
        pub_df = fetch_publisher_report(start_date, end_date, user_id_selection, campaign_name_selection)
        
        st.write(f"Total **{len(pub_df)}** publishers with total spend: **${pub_df['Spend'].sum():,.2f}**")
    
        # --- Dynamic Filter Builder ---
        with st.expander('*🔍 Advanced Publisher Filters*', expanded=False):
    
            if 'num_pub_filters' not in st.session_state:
                st.session_state.num_pub_filters = 1
    
            col_add, col_remove = st.columns(2)
    
            with col_add:
                if st.button("➕ Add Filter"):
                    st.session_state.num_pub_filters += 1
    
            with col_remove:
                if st.button("❌ Remove Last Filter") and st.session_state.num_pub_filters > 1:
                    st.session_state.num_pub_filters -= 1
    
            filter_metrics = ['', 'Impr','Clicks', 'Spend', 'Revenue', 'ROI']
            operators = ['', '=', '>', '<', '>=', '<=']


            # --- Duplicating the publisher report data ---
            filtered_pub_df = pub_df.copy()
    
            for i in range(st.session_state.num_pub_filters):
                filter_row = st.columns([3, 2, 3])
    
                metric = filter_row[0].selectbox(f"Metric_{i}", filter_metrics, key=f"metric_{i}")
                operator = filter_row[1].selectbox(f"Operator_{i}", operators, key=f"operator_{i}")
                value = filter_row[2].number_input(f"Value_{i}", key=f"value_{i}", step=0.01)
    
                # Apply filter to dataframe if metric exists
                if metric in filtered_pub_df.columns:
                    if operator == '>':
                        filtered_pub_df = filtered_pub_df[filtered_pub_df[metric] > value]
                    elif operator == '<':
                        filtered_pub_df = filtered_pub_df[filtered_pub_df[metric] < value]
                    elif operator == '>=':
                        filtered_pub_df = filtered_pub_df[filtered_pub_df[metric] >= value]
                    elif operator == '<=':
                        filtered_pub_df = filtered_pub_df[filtered_pub_df[metric] <= value]
                    elif operator == '=':
                        filtered_pub_df = filtered_pub_df[filtered_pub_df[metric] == value]
    
        styled_df2 = filtered_pub_df.style \
                .map(color_percentage_change, subset=pub_roi_cols) \
                .map(color_pnl, subset=pub_pnl_cols) \
                .background_gradient(cmap='Greens', subset=['Impr', 'Clicks', 'Revenue'], low=0.2, high=0.4) \
                .background_gradient(cmap='Oranges', subset=['Spend'], low=0.2, high=0.8) \
                .bar(subset=['ROI'], align='zero', color=['#FF6347', '#7CFC00']) \
                .format({
                    'Date': lambda x: x.strftime("%Y-%m-%d") if isinstance(x, (pd.Timestamp, date)) else x,
                    "Impr": "{:,.0f}",
                    "Clicks": "{:,.0f}",
                    'Spend': "${:,.2f}",
                    'Revenue': "${:,.2f}",
                    'ROI': "{:.2f}%"
                })
    
        st.dataframe(styled_df2, use_container_width=True, hide_index=True)
else:
    st.warning("No data found for the selected filters. Please adjust the dates, user IDs, or campaign names.")

st.divider()
st.caption("Crafted with ❤️ by Dinero Software Pvt Ltd")

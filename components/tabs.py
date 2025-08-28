import streamlit as st
import pandas as pd
from datetime import date

# --- Utility Functions ---
def color_percentage_change(val):
    if pd.isna(val):
        return ''
    if isinstance(val, (int, float)):
        if val > 0:
            return 'color: green; font-weight: bold;'
        elif val < 0:
            return 'color: red; font-weight: bold;'
    return ''

def color_pnl(val):
    if pd.isna(val):
        return ''
    if isinstance(val, (int, float)):
        if val > 0:
            return 'color: green; font-weight: bold;'
        elif val < 0:
            return 'color: red; font-weight: bold;'
    return ''


# --- MAIN TAB FUNCTION ---
def render_data_tabs(df_aggregated, df_campaign, df_pub, start_date, end_date, user_id_selection, campaign_name_selection, account_id_selection):
    pub_pnl_cols = ['PnL']
    pub_roi_cols = ['ROI']
    percentage_cols = ['Impr_Δ', 'Clicks_Δ', 'Spend_Δ', 'TCL_Δ', 'AFS_Δ']
    roi_cols = ['ROI_AFS', 'ROI_TCL']
    pnl_cols = ['PL_AFS', 'PL_TCL']

    tab1, tab2, tab3 = st.tabs(["📅 Daily Aggregated", "📋 Campaign Breakdown", "📑 Publishers Breakdown"])

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
                        "Impr": "{:,.0f}",
                        "Clicks": "{:,.0f}",
                         'Spend': lambda x: f"${x:,.2f}" if pd.notna(x) else "-",
                         'TCL': lambda x: f"${x:,.2f}" if pd.notna(x) else "-",
                         'AFS': lambda x: f"${x:,.2f}" if pd.notna(x) else "-",
                        'PL_AFS': lambda x: f"${x:,.2f}" if pd.notna(x) else "-",
                         'PL_TCL': lambda x: f"${x:,.2f}" if pd.notna(x) else "-",
                         'ROI_AFS': lambda x: f"{x:,.2f}%" if pd.notna(x) else "-",
                         'ROI_TCL': lambda x: f"{x:,.2f}%" if pd.notna(x) else "-"
        }), use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### 🎯 Campaign-level View")
        styled_df = df_campaign.style \
            .map(color_percentage_change, subset=percentage_cols) \
            .map(color_percentage_change, subset=roi_cols) \
            .map(color_pnl, subset=pnl_cols) \
            .background_gradient(cmap='Greens', subset=['Impr', 'Clicks', 'TCL', 'AFS'], low=0.2, high=0.4) \
            .background_gradient(cmap='Oranges', subset=['Spend'], low=0.2, high=0.8) \
            .bar(subset=['PL_AFS', 'PL_TCL'], align='zero', color=['#FF6347', '#7CFC00']) \
            .format({
                              'Date': lambda x: x.strftime("%Y-%m-%d") if isinstance(x, (pd.Timestamp, date)) else x,
                                "Impr": "{:,.0f}",
                                "Clicks": "{:,.0f}",
                                'Spend': lambda x: f"${x:,.2f}" if pd.notna(x) else "-",
                                'TCL': lambda x: f"${x:,.2f}" if pd.notna(x) else "-",
                                'AFS': lambda x: f"${x:,.2f}" if pd.notna(x) else "-",
                                'PL_AFS': lambda x: f"${x:,.2f}" if pd.notna(x) else "-",
                                'PL_TCL': lambda x: f"${x:,.2f}" if pd.notna(x) else "-",
                                'Impr_Δ': lambda x: f"{x:,.2f}%" if pd.notna(x) else "-", 
                                'Clicks_Δ': lambda x: f"{x:,.2f}%" if pd.notna(x) else "-",
                                'Spend_Δ': lambda x: f"{x:,.2f}%" if pd.notna(x) else "-",
                                'TCL_Δ': lambda x: f"{x:,.2f}%" if pd.notna(x) else "-",
                                'AFS_Δ': lambda x: f"{x:,.2f}%" if pd.notna(x) else "-", 
                                'ROI_AFS': lambda x: f"{x:,.2f}%" if pd.notna(x) else "-",
                                'ROI_TCL': lambda x: f"{x:,.2f}%" if pd.notna(x) else "-"
            })

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("### 📑 Publishers-level View")

        st.write(f"Total **{len(df_pub)}** publishers with total spend: **${df_pub['Spend'].sum():,.2f}**")

        with st.expander("*🔍 Advanced Publisher Filters*", expanded=False):
            if 'num_pub_filters' not in st.session_state:
                st.session_state.num_pub_filters = 1

            col_add, col_remove = st.columns(2)

            with col_add:
                if st.button("➕ Add Filter"):
                    st.session_state.num_pub_filters += 1

            with col_remove:
                if st.button("❌ Remove Last Filter") and st.session_state.num_pub_filters > 1:
                    st.session_state.num_pub_filters -= 1

            filter_metrics = ['', 'Spend', 'Clicks', 'Impr', 'ROI']
            operators = ['', '>', '<', '>=', '<=', '=']

            filtered_pub_df = df_pub.copy()

            for i in range(st.session_state.num_pub_filters):
                filter_row = st.columns([3, 2, 3])

                metric = filter_row[0].selectbox(f"Metric", filter_metrics, key=f"metric {i}")
                operator = filter_row[1].selectbox(f"Operator", operators, key=f"operator {i}")
                value = filter_row[2].number_input(f"Value", key={i}, step=0.01)

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

        styled_pub_df = filtered_pub_df.style \
            .map(color_percentage_change, subset=pub_roi_cols) \
            .map(color_pnl, subset=pub_pnl_cols) \
            .background_gradient(cmap='Greens', subset=['Impr', 'Clicks', 'Revenue'], low=0.2, high=0.4) \
            .background_gradient(cmap='Oranges', subset=['Spend'], low=0.2, high=0.8) \
            .bar(subset=['ROI'], align='zero', color=['#FF6347', '#7CFC00']) \
            .format({
                'Date': lambda x: x.strftime("%Y-%m-%d") if isinstance(x, (pd.Timestamp, date)) else x,
                "Impr": "{:,.0f}",
                "Clicks": "{:,.0f}",
                'Spend': lambda x: f"${x:,.2f}" if pd.notna(x) else "-",
                'Revenue': lambda x: f"${x:,.2f}" if pd.notna(x) else "-",
                'ROI': lambda x: f"{x:.2f}%" if pd.notna(x) else "-",
                'PnL': lambda x: f"{x:.2f}%" if pd.notna(x) else "-"
            })

        st.dataframe(styled_pub_df, use_container_width=True, hide_index=True)

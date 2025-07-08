import streamlit as st
from datetime import timedelta
from queries.fetch_data import fetch_data


def render_kpi_block(df_table, start_date, end_date, user_id_selection, campaign_name_selection):
    st.subheader("🔢 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    total_spend = df_table['Spend'].sum()
    total_tcl = df_table['TCL'].sum()
    total_profit_tcl = total_tcl - total_spend
    roi_tcl = (total_profit_tcl / total_spend * 100) if total_spend != 0 else 0

    # Previous Period
    period_length = (end_date - start_date).days + 1
    prev_end_date = start_date - timedelta(days=1)
    prev_start_date = prev_end_date - timedelta(days=period_length - 1)
    prev_df = fetch_data(prev_start_date, prev_end_date, user_id_selection, campaign_name_selection)

    prev_spend = prev_df['Spend'].sum() if not prev_df.empty else 0
    prev_tcl = prev_df['TCL'].sum() if not prev_df.empty else 0
    prev_profit_tcl = prev_tcl - prev_spend
    prev_roi_tcl = (prev_profit_tcl / prev_spend * 100) if prev_spend != 0 else 0

    def calc_pct_change(current, previous):
        if previous == 0 or pd.isna(previous):
            return None
        return (current - previous) / previous * 100

    spend_pct_change = calc_pct_change(total_spend, prev_spend)
    tcl_pct_change = calc_pct_change(total_tcl, prev_tcl)
    profit_pct_change = calc_pct_change(total_profit_tcl, prev_profit_tcl)
    roi_pct_change = calc_pct_change(roi_tcl, prev_roi_tcl)

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
    roi_delta_html = "N/A"

    if roi_pct_change is not None:
        roi_color_class = "positive" if roi_pct_change >= 0 else "negative"
        roi_sign = "+" if roi_pct_change >= 0 else ""
        roi_delta_html = f'<span class="kpi-change {roi_color_class}">{roi_sign}{roi_pct_change:.2f}%</span>'

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

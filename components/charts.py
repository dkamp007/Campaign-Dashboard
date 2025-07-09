import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_line_chart(df_for_charts: pd.DataFrame, chart_title_suffix: str):
    st.markdown("### :chart_with_upwards_trend: Trends")

    if not df_for_charts.empty:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=df_for_charts['Date'], y=df_for_charts['Spend'],
                       name="💸 Spend", line=dict(color="darkorange")),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=df_for_charts['Date'], y=df_for_charts['TCL'],
                       name="📈 TCL Revenue", line=dict(color="royalblue")),
            secondary_y=True,
        )

        fig.update_layout(
            title=f"📈 Spend vs TCL Over Time{chart_title_suffix}",
            template="plotly_white",
            height=470,
            xaxis=dict(title='Date'),
            yaxis=dict(title='Spend ($)'),
            yaxis2=dict(title='TCL Revenue ($)', overlaying='y', side='right'),
            legend=dict(x=1, y=1.02, orientation="h", yanchor="bottom", xanchor="right")
        )

        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Spend ($)", secondary_y=False, showgrid=True)
        fig.update_yaxes(title_text="TCL Revenue ($)", secondary_y=True, showgrid=False)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available to display trends based on the current selection.")

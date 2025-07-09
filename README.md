# Campaign-Dashboard

A fully interactive and modular web-based dashboard to analyze Bing Ads campaign performance. Built using Streamlit, Plotly, and Python, this dashboard empowers marketing analysts and campaign managers to explore campaign-level, publisher-level, and daily aggregated data with dynamic filters, KPI comparisons, trend charts, and advanced filtering options.

---

## 🚀 Features

- **Dynamic Date Filtering:** Quick filters like Last **7/15/30** days or custom date selection.

- **User-Based Filtering:** Select campaigns by user (name-based UI with ID mapping).

- **Campaign Name Auto-Filtering:** Campaigns are filtered based on selected users.

- **KPI Cards with Deltas:** Spend, Revenue, Profit, and ROI shown with previous period comparison.

- **Dual-Axis Line Charts:** Spend vs. Revenue trends over time.

- **Interactive Tabs:**

  - **📅 Daily Aggregated:** Date-wise summary of performance metrics.

  - **📋 Campaign Breakdown:** Campaign-wise daily performance with % changes.

  - **📑 Publishers Breakdown:** Domain-level analysis with impressions, clicks, spend, ROI.

- **Advanced Filter Builder:** Users can dynamically add filter rows for Spend, Clicks, ROI, etc.

- **Clean UI with Custom Styling:** HTML/CSS-enhanced metric cards and styled data tables.

- **Performance Optimized:** Cached queries for faster loading and reduced database strain.

---

## 🛠️ Tech Stack

- **Frontend/UI:** Streamlit

- **Visualization:** Plotly

- **Backend/Database:** MySQL (via SQL queries)

- **Data Access Layer:** Modular SQL query handler in utils/db.py

- **Styling:** Custom CSS + Streamlit widgets

---

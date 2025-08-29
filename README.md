# 📊 Campaign-Dashboard

A fully interactive and modular web-based dashboard to analyze Bing Ads campaign performance. Built using Streamlit, Plotly, and Python, this dashboard empowers marketing analysts and campaign managers to explore campaign-level, publisher-level, and daily aggregated data with dynamic filters, KPI comparisons, trend charts, and advanced filtering options.

---

## 🚀 Features

- **Dynamic Date Filtering:** Quick filters like Last **7/15/30** days or custom date selection.

- **Account-Based Filtering:** Select campaigns by the bing accounts (name-based UI with ID mapping).

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

## 📁 Project Structure

```
📦 campaign-dashboard/
│
├── main.py                # Main Streamlit app file
├── utils/
│   └── db.py              # Database query functions (run_query)
├── queries/
│   └── campaign_names.py
│   └── campaign_stats.py
│   └── daily_stats.py
│   └── fetch_data.py
│   └── publishers_stats.py
│   └── user.py
│   └── accounts.py
│   └── chart_data.py
├── components/
│   └── kpis.py
│   └── sidebar_filters.py
│   └── tabs.py
│   └── charts.py
├── style.css              # Custom styling for KPIs and components
├── README.md              # Project documentation
└── requirements.txt       # Python dependencies
```
---

## ✅ Requirements
```bash
streamlit
pandas
mysql-connector-python
sqlalchemy
plotly
matplotlib
streamlit-extras
streamlit-components
```
You can install the dependencies with:
```bash
pip install -r requirements.txt
```

---


## 🧠 How to Use

**1.** Clone the repository:

```bash
git clone https://github.com/dkamp007/Campaign-Dashboard.git
cd campaign-dashboard
```

**2.** Add your database credentials to the `utils/db.py` connection method.

**3.** Run the app:
```bash
streamlit run main.py
```

---

## 👨‍💻 Author

Created with ❤️ by Dkamp007

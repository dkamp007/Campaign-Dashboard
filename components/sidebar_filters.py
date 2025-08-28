import streamlit as st
from datetime import date, timedelta
from queries.accounts import get_bing_accounts
from queries.user import fetch_user_mapping
from queries.campaign_names import fetch_campaign_names

def render_sidebar_filters():
    st.sidebar.title("Welcome! This is the Dashboard of Bing Reports")
    st.sidebar.markdown('Play around with the filters for more details.')

    today = date.today()

    # --- QUICK FILTER ---
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

        days_offset = num_days_map.get(date_range_option, 30)
        quick_filter_start_date = today - timedelta(days=days_offset) + timedelta(days=1)
        quick_filter_end_date = today

    # --- MANUAL DATE INPUT ---
    with st.sidebar.expander('**Custom Date Range**', expanded=False):
        custom_start_date = st.date_input("Start Date", value=quick_filter_start_date, max_value=today, key='custom_start_date')
        custom_end_date = st.date_input("End Date", value=quick_filter_end_date, max_value=today, key='custom_end_date')

    start_date = custom_start_date
    end_date = custom_end_date
    
    num_days_selected = (end_date - start_date).days + 1
    
    if start_date == end_date:
        num_days_selected = 1
    else:
        num_days_selected
    
    st.sidebar.markdown(f"**Selected period:** :blue[{num_days_selected} days]")


    # --- ACCOUNTS FILTER ---
    account_options = get_bing_accounts()
    all_accounts = list(account_options.keys())

    with st.sidebar.expander('**Accounts Manager**', expanded=False):
        if 'accounts_selection_all_checked' not in st.session_state:
            st.session_state.accounts_selection_all_checked = True
        if 'current_account_selected' not in st.session_state:
            st.session_state.current_account_selected = all_accounts

        select_all_accounts = st.checkbox("Select All Accounts", value=st.session_state.accounts_selection_all_checked)

        if select_all_accounts:
            account_selection = all_accounts
            st.session_state.current_account_selected = all_accounts
        else:
            account_selection = st.multiselect(
                "Select Account(s)",
                all_accounts,
                default=st.session_state.current_account_selected,
                key='account_multiselect'
            )
            st.session_state.current_account_selected = account_selection

        st.session_state.accounts_selection_all_checked = select_all_accounts

    account_id_selection = [account_options[name] for name in account_selection]

    

    # --- USER FILTER ---
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
            selected_user_names = st.multiselect("Select User(s)", all_user_names, default=st.session_state.current_user_names)

        st.session_state.current_user_names = selected_user_names
        st.session_state.user_selection_all_checked = select_all_users

    user_id_selection = [user_mapping[name] for name in selected_user_names]

    # --- CAMPAIGN FILTER ---
    campaign_options = fetch_campaign_names(start_date, end_date, user_id_selection if user_id_selection else None)

    with st.sidebar.expander('**Campaign Selection**', expanded=False):
        if 'campaign_selection_all_checked' not in st.session_state:
            st.session_state.campaign_selection_all_checked = True
        if 'current_campaign_names' not in st.session_state:
            st.session_state.current_campaign_names = campaign_options

        select_all_campaigns = st.checkbox("Select All Campaigns", value=st.session_state.campaign_selection_all_checked, key='select_all_campaigns_checkbox')

        if select_all_campaigns:
            campaign_name_selection = campaign_options
            st.session_state.current_campaign_names = campaign_options
        else:
            campaign_name_selection = st.multiselect(
                "Select Campaign Names",
                campaign_options,
                default=st.session_state.current_campaign_names,
                key='campaign_name_multiselect')
            st.session_state.current_campaign_names = campaign_name_selection

        st.session_state.campaign_selection_all_checked = select_all_campaigns

    
    return start_date, end_date, account_id_selection, user_id_selection, campaign_name_selection

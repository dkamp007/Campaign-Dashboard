import pandas as pd
import sqlalchemy
import streamlit as st
import toml

@st.cache_resource
def run_query(query):
    config = toml.load("config.toml")["database"]
    engine = None
    try:
        engine = sqlalchemy.create_engine
        (
            f"mysql+mysqlconnector://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
        )
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"An error occurred: {e}")

import pandas as pd
import sqlalchemy
import streamlit as st
import toml

@st.cache_resource
def get_connection():
    config = toml.load("config.toml")["database"]
    engine = sqlalchemy.create_engine(
        f"mysql+mysqlconnector://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
    )
    return engine

def run_query(query):
    engine = get_connection()
    return pd.read_sql(query, engine)

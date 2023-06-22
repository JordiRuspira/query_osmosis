import streamlit as st
from streamlit_ace import st_ace
import time
import os
import pandas as pd
from shroomdk import ShroomDK
from transpose import Transpose
import requests
import json
import math

# Configure Streamlit Page
#page_icon = "assets/img/eth.jpg"
page_icon = "assets/img/osmosis-55faa201.png"
st.set_page_config(page_title="Query ETH", page_icon=page_icon, layout="wide")
st.header("Query Ethereum")
st.warning(
    "Quickly explore Ethereum blockchain data w/ different providers. For extensive usage, register directly with providers."
)

# Read Custom CSS
with open("assets/css/style.css", "r") as f:
    css_text = f.read()
custom_css = f"<style>{css_text}</style>"
st.markdown(custom_css, unsafe_allow_html=True)

# Get API Keys
flipside_key = os.environ["FLIPSIDE_KEY"]

# Query Flipside using their Python SDK
def query_flipside(q):
    sdk = ShroomDK(flipside_key)
    result_list = []
    for i in range(1, 11):  # max is a million rows @ 100k per page
        data = sdk.query(q, page_size=100000, page_number=i)
        if data.run_stats.record_count == 0:
            break
        else:
            result_list.append(data.records)
    result_df = pd.DataFrame()
    for idx, each_list in enumerate(result_list):
        if idx == 0:
            result_df = pd.json_normalize(each_list)
        else:
            try:
                result_df = pd.concat([result_df, pd.json_normalize(each_list)])
            except:
                continue
    result_df.drop(columns=["__row_index"], inplace=True)
    return result_df



# Provider names mapped to their respective query functions
def run_query(q, provider):
    provider_query = {
        "Flipside": query_flipside
    }
    df = provider_query[provider](q)
    return df


# Fetch data
schema_df = pd.read_csv("assets/provider_schema_data.csv")

# Sidebar
st.sidebar.image("assets/img/osmosis-55faa201.png", width=300)
provider = st.sidebar.selectbox("Providers", ["Flipside"])
st.sidebar.write("Tables")

# Render the Query Editor
provider_schema_df = schema_df[schema_df["datawarehouse"] == provider]
provider_tables_df = (
    provider_schema_df.drop(columns=["column_name"])
    .drop_duplicates()
    .sort_values(by=["table_name"])
)

for index, row in provider_tables_df.iterrows():
    table_name = row["table_name"]
    table_schema = row["table_schema"]
    table_catalog = row["table_catalog"]
    if str(table_catalog) != "nan":
        table_catalog = f"{table_catalog}."
    else:
        table_catalog = ""

    with st.sidebar.expander(table_name):
        st.code(f"{table_catalog}{table_schema}.{table_name}", language="sql")
        columns_df = provider_schema_df[provider_schema_df["table_name"] == table_name][
            ["column_name"]
        ]
        st.table(columns_df)


# Query Editor
ace_query = st_ace(
    language="sql",
    placeholder="SELECT * FROM osmosis.blocks limit 10",
    theme="twilight",
)

try:
    if ace_query:
        results_df = run_query(ace_query, provider)
        st.write(results_df)
except:
    st.write("Write a new query.")

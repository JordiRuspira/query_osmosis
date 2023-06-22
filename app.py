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
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as ticker
import numpy as np
import plotly.express as px

# Configure Streamlit Page
#page_icon = "assets/img/eth.jpg"
page_icon = "assets/img/osmosis-55faa201.png"
st.set_page_config(page_title="Query ETH", page_icon=page_icon, layout="wide")
st.header("Query Osmosis")
st.warning(
    "Quickly explore Osmosis blockchain data w/ different providers. For extensive usage, register directly with Flipside."
)

# Read Custom CSS
with open("assets/css/style.css", "r") as f:
    css_text = f.read()
custom_css = f"<style>{css_text}</style>"
st.markdown(custom_css, unsafe_allow_html=True)

# Get API Keys
flipside_key = st.secrets["API_KEY"]
sdk = ShroomDK(flipside_key)

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


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Introduction and basics", "SQL basics", "Osmosis basics", "Osmosis - create a few complex tables", "JSON basics"])

with tab1:
    
    st.subheader("Introduction")
    st.write('')
    st.write('This tool pretends to be an introduction and a go-to place for users who have never queried Osmosis data, and want to start without complex stuff or registering anywhere.')
    st.write('')
    st.write('On the left hand side, you will always have available the different tables regarding Osmosis and Mars outpost on Osmosis, their columns and description. This way, you can always refer to them throughout the tool. Additionally, I have structured this site in different tabs so you can always be playing around it. These tabs include: ')
    st.write('- SQL basic information. You can always look for more advanced stuff online.')
    st.write('- Osmosis basics. Having a small knowledge on SQL, we`ll look at some Osmosis specific information and how to query it.')
    st.write('- We`ll create some specific tables using the already existing ones, making use of more advanced knowledge.')
    st.write('- A last tab regarding how to query JSON data. Many data is stored in JSON, so knowing how to query it is always useful.')
    st.write('')
    st.write('With this being said, I have to thank both Primo Data and Antonidas, because many of this work is already done by them, I`ve taken different pieces, structured it and tried to make it user friendly and specific for Osmosis users.')
 
with tab2:
    
    st.subheader("SQL basics")
    st.write('')
    st.write('Snowflake is a data platform and data warehouse that supports the most common standardized version of SQL, and FlipsideCrypto is leverages snowflake SQL. There are many tutorials online which will go far beyond the scope of this tool, but having a starting point is useful.')
    st.write('Here`s the basic order of functions. You will not need to use everything for every SQL.')
    
    code = '''SELECT [column_name]
    FROM [table_name]
    LFET JOIN [table_name] ON [column_name = column_name] 
    WHERE [column_name = 1]
    GROUP BY 1,2,3
    HAVING [column_name = 1]
    QUALIFY [column_name = 1]
    ORDER BY 1,2,3
    LIMIT 1''' 

    st.code(code, language="sql", line_numbers=False)
    
    st.write('It is always good to add a limit so that the query doesn`t take too long')
    
    code1 = '''SELECT *
    FROM table_name
    LIMIT 10''' 

    st.code(code1, language="sql", line_numbers=False)
    
    st.write('You have to add conditions in order to filter.')
    
    code2 = '''SELECT *
    FROM table_name
    WHERE block_timestamp > current_date() - 30
    AND amount_in_usd is not null
    LIMIT 10''' 

    st.code(code2, language="sql", line_numbers=False)    
    
    
    st.write('You can also select only interested columns.')

    code3 = '''SELECT
    block_timestamp,
    amount_in_usd
    FROM table_name
    WHERE block_timestamp > current_date() - 30
    AND amount_in_usd is not null
    LIMIT 10''' 

    st.code(code3, language="sql", line_numbers=False)        
    
    st.write('Group the days together... and remove the LIMITS.')
    
     
    code4 = '''SELECT
    date_trunc('day', block_timestamp) as day_date,
    sum(amount_in_usd) as sum_amount_usd
    FROM table_name
    WHERE block_timestamp > current_date() - 30
    AND amount_in_usd is not null
    GROUP BY 1 -- this is the first column. And this is a comment.
    -- everything written after the double - is not processed''' 

    st.code(code4, language="sql", line_numbers=False)            
    
    st.write('With the most basic things covered, time to move up to Osmosis data!')

with tab3:    
    
    
    st.subheader("Osmosis basics")
    
    st.write('')
    st.write('Since the purpose of this tool is not an introduction on Osmosis, I will not spend much time explaining it, but it is usefull to remember which actions users can perform on Osmosis:')
    st.write('- Transfer tokens (both between Osmosis accounts and to other IBC connected chains)')
    st.write('- Stake, unstake, restake OSMO tokens to validators')
    st.write('- Vote, create proposals')
    st.write('- Perform swap operations')
    st.write('- Provide liquidity to a pool')
    st.write('- Claim rewards from staking')
    st.write('- As new tools appear, the complexity increases, but it is somewhat still a combination of all prior operations')
    
    st.write('With this being said, lets get hands-on, shall we?')
    
    st.subheader("Daily Transfers")
    st.write('')
    st.write('Now that we have all the tools needed, we can start querying. We will look at a couple of examples, starting with transfers, both IBC transfers and non-IBC transfers')
    
    code5 = '''select distinct transfer_type from osmosis.core.fact_transfers
    ''' 

    st.code(code5, language="sql", line_numbers=False)            
    
    st.write('The code above shows the different types of transfers. We can execute it below, and see what it returns.')
    # Query Editor
    ace_query = st_ace(
        language="sql",
        placeholder="select distinct transfer_type from osmosis.core.fact_transfers",
        theme="twilight",
    )  
    
    try:
        if ace_query:
            results_df = run_query(ace_query, provider)
            st.write(results_df)
    except:
        st.write("Write a new query.")
        
    st.write('So it returns three values: IBC_TRANSFER_OUT, IBC_TRANSFER_IN and OSMOSIS. Therefore, the two first values correspond to tokens being sent out and received to and from other IBC-enabled blockchains. Consider the following code:')


    code6 = '''select date_trunc('day', block_timestamp) as date,
    transfer_type,
    count(distinct tx_id) as num_tx from osmosis.core.fact_transfers a 
    where tx_succeeded = 'TRUE'
    and  date_trunc('day', block_timestamp) >= current_date - 30
    and transfer_type in ('IBC_TRANSFER_IN','IBC_TRANSFER_OUT')
    group by date, transfer_type
    ''' 

    st.code(code6, language="sql", line_numbers=False)            
    
    st.write('If we execute and plot the results of the previous statement, we can plot the daily number of IBC transactions in and out of Osmosis from the past 30 days.')
   
    
    sql0 = """
       select date_trunc('day', block_timestamp) as date,
    transfer_type,
    count(distinct tx_id) as num_tx from osmosis.core.fact_transfers a 
    where tx_succeeded = 'TRUE'
    and  date_trunc('day', block_timestamp) >= current_date - 30
    and transfer_type in ('IBC_TRANSFER_IN','IBC_TRANSFER_OUT')
    group by date, transfer_type

    
    """
    
    st.experimental_memo(ttl=1000000)
    @st.experimental_memo
    def compute(a):
        results=sdk.query(a)
        return results
    
    results0 = compute(sql0)
    df0 = pd.DataFrame(results0.records)
    
    fig1 = px.bar(df0, x="date", y="num_tx", color="transfer_type", color_discrete_sequence=px.colors.qualitative.Pastel2)
    fig1.update_layout(
    title='Daily number of IBC transactions - last 30 days',
    xaxis_tickfont_size=14,
    yaxis_tickfont_size=14,
    bargap=0.15, # gap between bars of adjacent location coordinates.
    bargroupgap=0.1 # gap between bars of the same location coordinate.
    )
    st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
 

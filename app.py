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
st.set_page_config(page_title="Query Osmosis", page_icon=page_icon, layout="wide")
st.header("Query Osmosis")
st.warning(
    "Quickly explore Osmosis blockchain data. For extensive usage, register directly with Flipside, using an amazing guide made by Chordtus [here](https://hackmd.io/@ILT-2i1MSgCJAtK6mNy40Q/SyLjS7UW3)."
)
st.warning(
    "The following tool will be on the top side at all times for users to interact better with the queries."
)


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
    


# Read Custom CSS
with open("assets/css/style.css", "r") as f:
    css_text = f.read()
custom_css = f"<style>{css_text}</style>"
st.markdown(custom_css, unsafe_allow_html=True)



# Fetch data
schema_df = pd.read_csv("assets/provider_schema_data.csv")

# Sidebar
st.sidebar.image("assets/img/osmosis-55faa201.png", width=300)
provider = st.sidebar.selectbox("Schema", ["Osmosis core tables"])
st.sidebar.write("Tables")

# Render the Query Editor
provider_schema_df = schema_df[schema_df["table_schema"] == 'core']
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

provider_2 = st.sidebar.selectbox("Schema", ["Mars tables on Osmosis"])
st.sidebar.write("Tables")

# Render the Query Editor
provider_schema_df_2 = schema_df[schema_df["table_schema"] == 'mars']
provider_tables_df_2 = (
    provider_schema_df_2.drop(columns=["column_name"])
    .drop_duplicates()
    .sort_values(by=["table_name"])
)

for index, row in provider_tables_df_2.iterrows():
    table_name = row["table_name"]
    table_schema = row["table_schema"]
    table_catalog = row["table_catalog"]
    if str(table_catalog) != "nan":
        table_catalog = f"{table_catalog}."
    else:
        table_catalog = ""

    with st.sidebar.expander(table_name):
        st.code(f"{table_catalog}{table_schema}.{table_name}", language="sql")
        columns_df = provider_schema_df_2[provider_schema_df_2["table_name"] == table_name][
            ["column_name"]
        ]
        st.table(columns_df)


tab1, tab2, tab3, tab4  = st.tabs(["Introduction and basics", "SQL and JSON basics", "Osmosis basics", "Osmosis - create a few complex tables"])

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
    st.write('This would not be fair at all without giving credit to them:')
    st.write('- Inspiration and maaany thinks forked from [here](https://queryeth.streamlit.app/) by [Primo Data](https://twitter.com/primo_data)')
    st.write('- SQL basics and JSON taken from [here](https://flipsidecrypto.xyz/Antonidas/the-flipside-helpdesk-7xL0-n) by [Anton](https://twitter.com/msgAnton)')
    st.write('')
    st.write('This tool is created so that users who want to learn the first basics don`t have to go through the process of creating an user on flipside, which will be better for them once they want to explore everything with more detail. Using tools like the one below, I expect this to be more friendly to a user who has never or barely ever touched SQL, and has no clue about what flipside is and how it works.')
    
    ace_query = st_ace(
        language="sql",
        placeholder="select * from osmosis.core.fact_transfers limit 10",
        theme="twilight",
    )  
    

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
    
    
    st.subheader("JSON basics")
    
    st.write('As stated by Antonidas, any field that comes from JSON should be casted or there will be problems with types. Never Trust JSON Fields, always use the TRY_* functions.')
    st.write('')
    st.write('I will not go into detail, since this pretends to serve as an introduction, but here are a couple of examples:')
    
    code11 = '''with
      raw_data as (
        select
          '{
    "field1":"text",
    "field2":100,
    "field3":1.05,
    "field4":"0x020",
    }' as json_raw_string
      ),
      parsed_data as (
        select
          try_parse_json(json_raw_string)::variant as my_json_object
        from
          raw_data
      )
    select
      my_json_object:field1::text as field1, 
      try_to_numeric(my_json_object:field2::text)::integer as field2,
      TRY_TO_DOUBLE(my_json_object:field3::text)::double as field3,
      ethereum.public.udf_hex_to_int (my_json_object:field4)::integer as field4
    from
      parsed_data''' 

    st.code(code11, language="sql", line_numbers=False)  
    
    st.write('And an example using real data:')
    
    code11 = '''with raw_data as (
    select livequery.live.udf_api('https://ipfs.io/ipfs/Qmc8F75h1fRJbZTWrP6vjaTeCQe9XWxZrxJfbRqqvfNihE')
    as ipfs_data
    )
    
    select 
    ipfs_data:data:description::string  as data_description,
    ipfs_data:data:image::string  as data_image,
    ipfs_data
    from raw_data''' 

    st.code(code11, language="sql", line_numbers=False)   
     
        
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
 
      
    st.subheader("Daily amount delegated/undelegated/redelegated")
    st.write('')
    st.write('Same structure as before, we can calculate daily amount of OSMO delegated, undelegated and redelegated.')
    


    code7 = '''select date_trunc('day', block_timestamp) as date,
    action,
    sum(amount/pow(10, decimal)) as total_amount from osmosis.core.fact_staking a 
    where tx_succeeded = 'TRUE'
    and  date_trunc('day', block_timestamp) >= current_date - 30
    and currency = 'uosmo'
    group by date, action
    ''' 

    st.code(code7, language="sql", line_numbers=False)            
    
    st.write('If we execute and plot the results of the previous statement, we can plot the daily number of IBC transactions in and out of Osmosis from the past 30 days.')
   
    
    sql1 = """
       select date_trunc('day', block_timestamp) as date,
    action,
    sum(amount/pow(10, decimal)) as total_amount from osmosis.core.fact_staking a 
    where tx_succeeded = 'TRUE'
    and  date_trunc('day', block_timestamp) >= current_date - 30
    and currency = 'uosmo'
    group by date, action   
    """
    
    st.experimental_memo(ttl=1000000)
    @st.experimental_memo
    def compute(a):
        results=sdk.query(a)
        return results
    
    results1 = compute(sql1)
    df1 = pd.DataFrame(results1.records)
    
    fig1 = px.bar(df1, x="date", y="total_amount", color="action", color_discrete_sequence=px.colors.qualitative.Pastel2)
    fig1.update_layout(
    title='Daily OSMO delegated, undelegated and redelegated - last 30 days',
    xaxis_tickfont_size=14,
    yaxis_tickfont_size=14,
    bargap=0.15, # gap between bars of adjacent location coordinates.
    bargroupgap=0.1 # gap between bars of the same location coordinate.
    )
    st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
 
    
with tab4:    
    
    
    st.subheader("Creation of more complex tables")
    st.write('')
    st.write('So far we have only used examples of queries using only a single table. In SQL however there is a very usefull tool known as CTE (Common Table Expression), which allows users to create a temporary table using a query (then known as subquery), store it in a temporary table and use that one later for further purposes. For instance, imagine a very basic example:')
    
    code8 = '''with table_example as (
    select '20230101' as day, 'January' as month, 'this is a example column' as column1 from dual
    )
    select * from table_example 
    ''' 

    st.code(code8, language="sql", line_numbers=False)            

        
    st.write('If you copy and execute the code, this shows two useful things:')
    st.write('- We have introduced the concept of dual. The dual table allows you to create a completely invented table and use it later on.')
    st.write('- We have named that table as "table_example", and then selected everything from that table. You may now start seeing why this is useful.')
    st.write('With this concepts introduced, we can now go finally one step further, and create a complex query which gives you the amount staked per address.')
    
    
    code9 = '''WITH time as (
    select
      max(date_trunc('day', block_timestamp)) as date
    from
      osmosis.core.fact_blocks 
  ),
  delegations as (
    select
      date_trunc('day', block_timestamp) as date,
      delegator_address,
      validator_address,
      sum(amount / pow(10, decimal)) as amount
    from
      osmosis.core.fact_staking
    where
      tx_succeeded = 'TRUE'
      and action = 'delegate'
      and date_trunc('day', block_timestamp) <= (
        select
          date
        from
          time
      )
    group by
      date,
      delegator_address,
      validator_address
  ),
  undelegations as (
    select
      date_trunc('day', block_timestamp) as date,
      delegator_address,
      validator_address,
      sum(amount / pow(10, decimal)) * (-1) as amount
    from
      osmosis.core.fact_staking
    where
      tx_succeeded = 'TRUE'
      and action = 'undelegate'
      and date_trunc('day', block_timestamp) <= (
        select
          date
        from
          time
      )
    group by
      date,
      delegator_address,
      validator_address
  ),
  redelegations_to as (
    select
      date_trunc('day', block_timestamp) as date,
      delegator_address,
      validator_address,
      sum(amount / pow(10, decimal)) as amount
    from
      osmosis.core.fact_staking
    where
      tx_succeeded = 'TRUE'
      and action = 'redelegate'
      and date_trunc('day', block_timestamp) <= (
        select
          date
        from
          time
      )
    group by
      date,
      delegator_address,
      validator_address
  ),
  redelegations_from as (
    select
      date_trunc('day', block_timestamp) as date,
      delegator_address,
      redelegate_source_validator_address as validator_address,
      sum(amount / pow(10, decimal)) * (-1) as amount
    from
      osmosis.core.fact_staking
    where
      tx_succeeded = 'TRUE'
      and action = 'redelegate'
      and date_trunc('day', block_timestamp) <= (
        select
          date
        from
          time
      )
    group by
      date,
      delegator_address,
      redelegate_source_validator_address
  ),
  total_staked_user_1 as (
    select
      delegator_address,
      b.total_amount,
      sum(amount) as amount_delegated_user,
      amount_delegated_user / b.total_amount * 100 as percentage_over_total,
      rank() over (
        order by
          percentage_over_total desc
      ) as rank
    from
      (
        select
          *
        from
          delegations
        union all
        select
          *
        from
          undelegations
        union all
        select
          *
        from
          redelegations_to
        union all
        select
          *
        from
          redelegations_from
      ) a
      join (
        select
          sum(amount) as total_amount
        from
          (
            select
              *
            from
              delegations
            union all
            select
              *
            from
              undelegations
            union all
            select
              *
            from
              redelegations_to
            union all
            select
              *
            from
              redelegations_from
          )
      ) b
    group by
      1,
      2
    order by
      percentage_over_total desc
  )
select * from total_staked_user_1
limit 20
    ''' 
    st.code(code9, language="sql", line_numbers=False)       
    
    st.write('So yeah that is a large query. It takes the last available date, delegations, undelegations, redelegations from and redelegations to other validators, and finally calculates the percentage each user has over the total amount staked, and assigns a rank based on that order. I have set a limit to only show the first 20 rows, but feel free to erase that in order to have a full list. Even more, if you select a specific date in the first CTE, it will show the amount staked by each user on that specific date.')
    
    ace_query = st_ace(
        language="sql",
        placeholder="select * from osmosis.core.fact_transfers limit 10",
        theme="twilight",
    )  
    
        

  

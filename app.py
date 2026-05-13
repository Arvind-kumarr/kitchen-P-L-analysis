%%writefile app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Set Page Config
st.set_page_config(layout="wide", page_title="Kitchen PNL Dashboard")

# Load Cleaned Data
@st.cache_data
def get_data(file_path, file_timestamp):
    df = pd.read_csv(file_path)
    df['MONTH'] = pd.to_datetime(df['MONTH'])
    return df

# Get the modification time of the CSV file to use as a cachebuster
csv_file_path = 'cleaned_kitchen_data.csv'
file_mod_time = os.path.getmtime(csv_file_path)

df = get_data(csv_file_path, file_mod_time)

# --- SIDEBAR FILTERS ---
st.sidebar.header("Global Filters")
selected_months = st.sidebar.multiselect("Select Months", options=df['MONTH'].dt.strftime('%b-%Y').unique())
selected_zones = st.sidebar.multiselect("Select Zone", options=df['ZONE MAPPING'].unique(), default=df['ZONE MAPPING'].unique())

# --- DASHBOARD 1: KITCHEN LEVEL PNL ---
st.title("1. Kitchen Level PNL")

# EBITDA Range Slider
ebitda_min, ebitda_max = int(df['KITCHEN EBITDA'].min()), int(df['KITCHEN EBITDA'].max())
selected_ebitda = st.slider("Select EBITDA Range (in ₹)", ebitda_min, ebitda_max, (ebitda_min, ebitda_max))

col1, col2, col3 = st.columns(3)
with col1:
    store_filter = st.multiselect("Store", options=df['STORE'].unique())
with col2:
    eb_cat_filter = st.multiselect("EBITDA category", options=df['EBITDA CATEGORY'].unique())
with col3:
    rev_cat_filter = st.multiselect("Revenue category", options=df['Revenue category'].unique())

# Filtering logic
mask = (df['KITCHEN EBITDA'].between(selected_ebitda[0], selected_ebitda[1])) & \
       (df['ZONE MAPPING'].isin(selected_zones))

if store_filter: mask &= df['STORE'].isin(store_filter)
if rev_cat_filter: mask &= df['Revenue category'].isin(rev_cat_filter)

filtered_df = df[mask]

st.subheader("KITCHEN SNAPSHOT")
st.dataframe(filtered_df[['MONTH', 'STORE', 'NET REVENUE', 'GM %', 'KITCHEN EBITDA', 'Revenue category']], use_container_width=True)

# --- DASHBOARD 2: VARIANCE LEVEL ---
st.markdown("---")
st.title("2. VARIANCE BY REVENUE CATEGORY")

# Sub-dashboard: Avg Variance % Pivot
st.write("### Average Variance % on Cart")
pivot_var = filtered_df.pivot_table(
    index='Revenue category',
    columns=filtered_df['MONTH'].dt.strftime('%b-%Y'),
    values='VARIANCE %',
    aggfunc='mean'
).fillna(0)
st.table(pivot_var.style.format("{:.1f}%"))

# Sub-dashboard: Kitchen Count Pivot
st.write("### Count of Kitchen Stores")
pivot_count = filtered_df.pivot_table(
    index='Revenue category',
    columns=filtered_df['MONTH'].dt.strftime('%b-%Y'),
    values='STORE',
    aggfunc='count'
).fillna(0)
st.table(pivot_count.astype(int))

import streamlit as st
import pandas as pd
import mysql.connector

# --- MySQL Connection ---
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )

# --- Fetch Data from MySQL ---
@st.cache_data
def fetch_data():
    conn = get_connection()
    query = "SELECT * FROM supplier_sales"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- Load Data ---
df = fetch_data()
df['Date Sold'] = pd.to_datetime(df['Date Sold'])

# ----- Sidebar Filters -----
st.sidebar.header("Filter Data")
supplier_filter = st.sidebar.multiselect("Select Supplier", options=df['Supplier'].unique(), default=df['Supplier'].unique())
date_range = st.sidebar.date_input("Select Date Range", [df['Date Sold'].min(), df['Date Sold'].max()])

filtered_df = df[
    (df['Supplier'].isin(supplier_filter)) &
    (df['Date Sold'] >= pd.to_datetime(date_range[0])) &
    (df['Date Sold'] <= pd.to_datetime(date_range[1]))
]

# ----- Main Dashboard -----
st.title("📊 Supplier Performance Dashboard")

# Metrics
total_sales = (filtered_df['Cost per Unit'] * filtered_df['Units Sold']).sum()
total_profit = ((filtered_df['Actual Margin (%)'] / 100) * filtered_df['Cost per Unit'] * filtered_df['Units Sold']).sum()
avg_margin = filtered_df['Actual Margin (%)'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Profit", f"${total_profit:,.2f}")
col3.metric("Avg. Margin", f"{avg_margin:.2f}%")

# Profit by Supplier Chart
st.subheader("Profit by Supplier")
supplier_profit = filtered_df.groupby('Supplier').apply(
    lambda x: ((x['Actual Margin (%)'] / 100) * x['Cost per Unit'] * x['Units Sold']).sum()
).reset_index(name='Total Profit')

st.bar_chart(supplier_profit.set_index('Supplier'))

# Sales Over Time
st.subheader("Sales Over Time")
sales_over_time = filtered_df.groupby('Date Sold').apply(
    lambda x: (x['Cost per Unit'] * x['Units Sold']).sum()
).reset_index(name='Daily Sales')

st.line_chart(sales_over_time.set_index('Date Sold'))

# Detailed Table
st.subheader("Detailed Performance Table")
st.dataframe(filtered_df)

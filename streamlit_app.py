import streamlit as st
import pandas as pd
import numpy as np
import datetime

# ----- Sample Data -----
# Simulating supplier and product performance data
data = {
    'Supplier': ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier A', 'Supplier B'],
    'Product': ['Shirt', 'Jeans', 'Jacket', 'T-shirt', 'Skirt'],
    'Expected Margin (%)': [30, 25, 35, 20, 40],
    'Actual Margin (%)': [28, 22, 37, 18, 38],
    'Units Sold': [120, 90, 60, 200, 150],
    'Cost per Unit': [10, 20, 30, 8, 12],
    'Date Sold': pd.date_range(start='2025-05-01', periods=5, freq='D')
}
df = pd.DataFrame(data)

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


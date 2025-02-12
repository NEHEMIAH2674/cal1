import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set the page configuration
st.set_page_config(
    page_title="ACM Hourly Productivity Dashboard",  # Title displayed in the browser tab
    page_icon="📊",  # Favicon displayed in the browser tab
    layout="wide"  # Use the full width of the browser window
)

# Add a title to the dashboard
st.title("ACM Hourly Productivity Dashboard")

# Load data from both sheets
file_path = "callsmade.xlsx"
df1 = pd.read_excel(file_path, sheet_name='Sheet1')
df2 = pd.read_excel(file_path, sheet_name='Sheet2')

# Normalize column names (strip spaces and convert to lowercase)
df1.columns = df1.columns.str.strip().str.lower()
df2.columns = df2.columns.str.strip().str.lower()  # Do the same for df2

# Ensure numeric conversion works
df1["callsmade"] = pd.to_numeric(df1["callsmade"])
df1["ptpamount"] = pd.to_numeric(df1["ptpamount"])

# Calculate total Calls Made and Total PTP Amount before filtering
total_calls_made = df1["callsmade"].sum()
total_ptp_amount = df1["ptpamount"].sum()

# Display total metrics in the sidebar
st.sidebar.markdown("### Overall Performance Metrics")
st.sidebar.metric(label="📞 Total Calls Made", value=f"{total_calls_made:,}")  # Add commas for readability
st.sidebar.metric(label="💰 Total PTP Amount", value=f"{total_ptp_amount:,.2f}")  # Format as currency

# Ensure 'branches' column exists
if 'branches' in df1.columns:
    branches = df1['branches'].unique()
    selected_branch = st.sidebar.selectbox('Select Branch', branches)

    # Filter data based on selected branch
    df1_filtered = df1[df1['branches'] == selected_branch]
else:
    st.error("Column 'branches' not found in the dataset.")
    st.stop()

# Top & Bottom ACM by Calls Made
top_acm_calls = df1_filtered.loc[df1_filtered["callsmade"].idxmax(), "acmname"]
bottom_acm_calls = df1_filtered.loc[df1_filtered["callsmade"].idxmin(), "acmname"]

st.write(f"Top ACM by Calls Made: {top_acm_calls}")
st.write(f"Bottom ACM by Calls Made: {bottom_acm_calls}")

# Aggregate data by ACM Name for Calls Made & PTP Amount
acm_summary = df1_filtered.groupby("acmname").agg({"callsmade": "sum", "ptpamount": "sum"}).reset_index()

# Select the top 3 and bottom 3 ACMs
top_3 = acm_summary.nlargest(3, "callsmade")
bottom_3 = acm_summary.nsmallest(3, "callsmade")
selected_acms = pd.concat([top_3, bottom_3])

# Create two columns for side-by-side display
col1, col2 = st.columns(2)

# Display table in the first column
with col1:
    st.write("Top 3 and Bottom 3 ACMs by Calls Made & PTP Amount")
    st.write(selected_acms)

# Display heatmap in the second column
with col2:
    st.write("Heatmap of Top and Bottom ACMs")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(selected_acms.set_index("acmname"), annot=True, cmap="coolwarm", fmt="g", linewidths=0.5, ax=ax)
    st.pyplot(fig)

# Merging the data from Sheet2 for Trend Analysis of PTPAmount
df2['dateactioned'] = pd.to_datetime(df2['dateactioned'])

# Extract the hour from the 'dateactioned' column and group by hour
df2['hour'] = df2['dateactioned'].dt.hour
ptp_trend_hourly = df2.groupby('hour').agg({'ptpamount': 'sum'}).reset_index()

# Plot the hourly trend of PTPAmount
fig2, ax2 = plt.subplots(figsize=(12, 6))
sns.lineplot(x='hour', y='ptpamount', data=ptp_trend_hourly, marker='o', linestyle='-', color='green', ax=ax2)
ax2.set_xlabel("Hour of the Day", fontsize=12)
ax2.set_ylabel("Total PTP Amount", fontsize=12)
ax2.set_title("Hourly Trend of PTP Amount Collected", fontsize=14)
ax2.grid(axis="y", linestyle="--", alpha=0.7)
st.pyplot(fig2)

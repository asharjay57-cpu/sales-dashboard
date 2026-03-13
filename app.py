import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="Directors Sales Dashboard",
    layout="wide"
)

# -------------------------------------------------
# GOOGLE SHEETS CONNECTION
# -------------------------------------------------

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1_r4JTBlQwLIxes2wcG6z_nYeqhRxN7UwzNo_Xcpndr0/edit"
).sheet1

# -------------------------------------------------
# LOGIN USERS
# -------------------------------------------------

users = {
    "director": {"password": "director123", "role": "Director"},
    "ac": {"password": "ac123", "role": "AC"},
    "ps": {"password": "ps123", "role": "PS"},
    "mn": {"password": "mn123", "role": "MN"},
}

# -------------------------------------------------
# LOGIN SYSTEM
# -------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("Company Sales Dashboard Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in users and password == users[username]["password"]:

            st.session_state.logged_in = True
            st.session_state.role = users[username]["role"]
            st.rerun()

        else:
            st.error("Invalid Username or Password")

    st.stop()

# -------------------------------------------------
# SIDEBAR USER INFO
# -------------------------------------------------

st.sidebar.success(f"Logged in as: {st.session_state.role}")

if st.sidebar.button("🚪 Sign Out"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.rerun()

# -------------------------------------------------
# DATA LOADING
# -------------------------------------------------

@st.cache_data
def load_data():

    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df


df = load_data()

# -------------------------------------------------
# ROLE BASED FILTER
# -------------------------------------------------

role = st.session_state.get("role")

if role and role != "Director":
    df = df[df["Sales_Team"] == role]

# -------------------------------------------------
# HANDLE EMPTY DATA
# -------------------------------------------------

if df.empty:
    st.warning("No data available for this user.")
    st.stop()

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------

st.sidebar.header("Dashboard Filters")

min_date = df["Date"].min()
max_date = df["Date"].max()

if pd.isna(min_date) or pd.isna(max_date):
    min_date = pd.Timestamp.today()
    max_date = pd.Timestamp.today()

date_range = st.sidebar.date_input(
    "Date Range",
    [min_date, max_date]
)

customers = st.sidebar.multiselect(
    "Customer",
    df["Customer_Name"].unique(),
    default=df["Customer_Name"].unique()
)

sort_no = st.sidebar.multiselect(
    "Sort No",
    df["Sort_Number"].unique(),
    default=df["Sort_Number"].unique()
)

sales_team = st.sidebar.multiselect(
    "Sales Team",
    df["Sales_Team"].unique(),
    default=df["Sales_Team"].unique()
)

# -------------------------------------------------
# FILTER DATA
# -------------------------------------------------

filtered_df = df[
    (df["Customer_Name"].isin(customers)) &
    (df["Sort_Number"].isin(sort_no)) &
    (df["Sales_Team"].isin(sales_team)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]


# -------------------------------------------------
# DASHBOARD TITLE
# -------------------------------------------------

st.title("Directors Sales Dashboard")
st.caption("Textile Dispatch & Sales Performance Overview")

# -------------------------------------------------
# KPI CALCULATIONS
# -------------------------------------------------

current_dispatch = filtered_df["Dispatch_Meters"].sum()

total_orders = filtered_df["GUI"].nunique()
total_customers = filtered_df["Customer_Name"].nunique()

avg_order = current_dispatch / total_orders if total_orders > 0 else 0

# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------



col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Dispatch", f"{current_dispatch:,.0f}")
col2.metric("Total Orders", f"{total_orders}")
col3.metric("Customers", f"{total_customers}")
col4.metric("Avg Order Size", f"{avg_order:,.0f}")

st.markdown("---")

# -------------------------------------------------
# DISPATCH TREND
# -------------------------------------------------

granularity = st.selectbox(
    "Time View",
    ["Daily", "Weekly", "Monthly"]
)

trend_df = filtered_df.copy()

if granularity == "Weekly":
    trend_df["Date"] = trend_df["Date"].dt.to_period("W").apply(lambda r: r.start_time)

elif granularity == "Monthly":
    trend_df["Date"] = trend_df["Date"].dt.to_period("M").apply(lambda r: r.start_time)

dispatch_trend = trend_df.groupby("Date")["Dispatch_Meters"].sum().reset_index()

fig1 = px.line(
    dispatch_trend,
    x="Date",
    y="Dispatch_Meters",
    markers=True,
    title="Dispatch Trend"
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------------------------------
# TOP CUSTOMERS
# -------------------------------------------------

st.subheader("Top 5 Customers")

top_customers = (
    filtered_df.groupby("Customer_Name")["Dispatch_Meters"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

fig = px.bar(
    top_customers,
    x="Customer_Name",
    y="Dispatch_Meters",
    text="Dispatch_Meters"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# CITY PERFORMANCE
# -------------------------------------------------

st.subheader("City Performance")

city_sales = (
    filtered_df.groupby("City")["Dispatch_Meters"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_city = px.bar(
    city_sales,
    x="Dispatch_Meters",
    y="City",
    orientation="h",
    text="Dispatch_Meters"
)

st.plotly_chart(fig_city, use_container_width=True)

# -------------------------------------------------
# EXPORT DATA
# -------------------------------------------------

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Filtered Data",
    csv,
    "sales_data.csv",
    "text/csv"
)
st.button("📧 Send Report by Email")






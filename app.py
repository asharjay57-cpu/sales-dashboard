import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gspread
from google.oauth2.service_account import Credentials

# ════════════════════════════════════════════════════════════
# PAGE CONFIG  ← no changes needed here
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Directors Sales Dashboard",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════
# ★ NEW — POWER BI DARK THEME CSS
#   Paste this entire block right after set_page_config()
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ── Core backgrounds ── */
    .stApp                              { background-color: #111318; }
    .main .block-container              { padding: 1.5rem 2rem 2rem; }
    [data-testid="stSidebar"]           { background-color: #1a1d27 !important;
                                          border-right: 1px solid #2e3250; }
    [data-testid="stSidebar"] *         { color: #e8eaf6 !important; }

    /* ── Global text ── */
    html, body, [class*="css"]          { color: #e8eaf6;
                                          font-family: 'DM Sans', 'Segoe UI', sans-serif; }
    h1  { font-size: 22px !important; font-weight: 700 !important; color: #e8eaf6 !important; }
    h2  { font-size: 17px !important; font-weight: 600 !important; color: #e8eaf6 !important; }
    h3  { font-size: 14px !important; font-weight: 600 !important; color: #e8eaf6 !important; }
    p, label, div                       { color: #e8eaf6; }
    .stMarkdown p                       { color: #8b93b8; }
    caption, small                      { color: #555d85 !important; }

    /* ── Sidebar widgets ── */
    [data-testid="stSidebar"] .stSelectbox > div,
    [data-testid="stSidebar"] .stMultiSelect > div,
    [data-testid="stSidebar"] .stDateInput > div  { background: #1e2130 !important;
                                                     border-color: #2e3250 !important; }

    /* ── Main widgets (selectbox, multiselect) ── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div          { background: #1e2130 !important;
                                          border: 1px solid #2e3250 !important;
                                          color: #e8eaf6 !important;
                                          border-radius: 8px !important; }

    /* ── Metric cards — KPI tiles ── */
    [data-testid="metric-container"]    { background: #1e2130;
                                          border: 1px solid #2e3250;
                                          border-radius: 10px;
                                          padding: 16px 20px !important; }
    [data-testid="stMetricLabel"]       { color: #555d85 !important;
                                          font-size: 11px !important;
                                          text-transform: uppercase;
                                          letter-spacing: 0.6px; }
    [data-testid="stMetricValue"]       { color: #4f8ef7 !important;
                                          font-size: 28px !important;
                                          font-weight: 700 !important; }
    [data-testid="stMetricDelta"]       { font-size: 11px !important; }

    /* ── Buttons ── */
    .stButton > button                  { background: linear-gradient(135deg,#4f8ef7,#a259f7) !important;
                                          border: none !important;
                                          color: white !important;
                                          border-radius: 8px !important;
                                          font-weight: 600 !important;
                                          padding: 8px 20px !important; }
    .stButton > button:hover            { opacity: 0.88 !important; }

    /* ── Download button ── */
    .stDownloadButton > button          { background: rgba(79,142,247,0.15) !important;
                                          border: 1px solid rgba(79,142,247,0.35) !important;
                                          color: #4f8ef7 !important;
                                          border-radius: 8px !important;
                                          font-weight: 600 !important; }

    /* ── Text inputs ── */
    .stTextInput > div > div > input    { background: #1e2130 !important;
                                          border: 1px solid #2e3250 !important;
                                          color: #e8eaf6 !important;
                                          border-radius: 8px !important; }
    .stTextInput > div > div > input[type="password"] { background: #1e2130 !important;
                                                         color: #e8eaf6 !important; }

    /* ── Dataframe / table ── */
    [data-testid="stDataFrame"]         { background: #1e2130 !important;
                                          border: 1px solid #2e3250;
                                          border-radius: 10px; }
    .dvn-scroller                       { background: #1e2130 !important; }

    /* ── Divider ── */
    hr                                  { border-color: #2e3250 !important; }

    /* ── Alerts / info boxes ── */
    .stAlert                            { background: #1e2130 !important;
                                          border: 1px solid #2e3250 !important;
                                          color: #8b93b8 !important; }

    /* ── Success badge in sidebar ── */
    .stAlert[data-baseweb="notification"] { background: rgba(62,207,142,0.12) !important;
                                             border-color: rgba(62,207,142,0.3) !important; }

    /* ── Tab bar (for Time View selectbox area) ── */
    .stTabs [data-baseweb="tab-list"]   { background: #1a1d27;
                                          border-bottom: 1px solid #2e3250; }
    .stTabs [data-baseweb="tab"]        { color: #555d85 !important; }
    .stTabs [aria-selected="true"]      { color: #4f8ef7 !important;
                                          border-bottom: 2px solid #4f8ef7 !important; }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header           { visibility: hidden; }

    /* ── KPI accent bars (custom HTML cards) ── */
    .kpi-card                           { background: #1e2130;
                                          border: 1px solid #2e3250;
                                          border-radius: 10px;
                                          padding: 16px 20px;
                                          position: relative;
                                          overflow: hidden; }
    .kpi-card::before                   { content: '';
                                          position: absolute;
                                          top: 0; left: 0; right: 0;
                                          height: 3px;
                                          border-radius: 10px 10px 0 0; }
    .kpi-blue::before   { background: #4f8ef7; }
    .kpi-teal::before   { background: #00c7b1; }
    .kpi-orange::before { background: #f7a84f; }
    .kpi-pink::before   { background: #e05c8a; }
    .kpi-lbl            { color: #555d85; font-size: 11px; text-transform: uppercase;
                          letter-spacing: 0.6px; font-weight: 600; margin-bottom: 4px; }
    .kpi-val-blue   { color: #4f8ef7; font-size: 28px; font-weight: 700; line-height: 1.1; }
    .kpi-val-teal   { color: #00c7b1; font-size: 28px; font-weight: 700; line-height: 1.1; }
    .kpi-val-orange { color: #f7a84f; font-size: 28px; font-weight: 700; line-height: 1.1; }
    .kpi-val-pink   { color: #e05c8a; font-size: 28px; font-weight: 700; line-height: 1.1; }
    .kpi-sub        { color: #555d85; font-size: 11px; margin-top: 4px; }

    /* ── Section card wrapper ── */
    .section-card               { background: #1e2130;
                                  border: 1px solid #2e3250;
                                  border-radius: 10px;
                                  padding: 18px;
                                  margin-bottom: 14px; }
    .section-title              { font-size: 13px; font-weight: 600;
                                  color: #e8eaf6; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# PLOTLY DARK THEME HELPER  ← ★ NEW — call apply_theme(fig) on every chart
# ════════════════════════════════════════════════════════════
PAL = ['#4f8ef7','#00c7b1','#f7a84f','#a259f7','#e05c8a','#3ecf8e','#f06070','#ffcc44','#56cfff','#b07cff']

def apply_theme(fig, height=300):
    """Apply Power BI dark theme to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor='#1e2130',
        plot_bgcolor='#1e2130',
        font=dict(color='#8b93b8', family='DM Sans, Segoe UI, sans-serif', size=11),
        height=height,
        margin=dict(l=10, r=10, t=36, b=10),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#8b93b8', size=10)),
        colorway=PAL,
        title_font=dict(color='#e8eaf6', size=13),
    )
    fig.update_xaxes(gridcolor='rgba(46,50,80,0.6)', linecolor='#2e3250',
                     tickfont=dict(color='#555d85'))
    fig.update_yaxes(gridcolor='rgba(46,50,80,0.6)', linecolor='#2e3250',
                     tickfont=dict(color='#555d85'))
    return fig

def kpi_html(label, value, sub, color):
    """Render a KPI card with coloured top-border accent."""
    return f"""
    <div class="kpi-card kpi-{color}">
        <div class="kpi-lbl">{label}</div>
        <div class="kpi-val-{color}">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""

# ════════════════════════════════════════════════════════════
# GOOGLE SHEETS CONNECTION  ← no changes needed
# ════════════════════════════════════════════════════════════
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

# ════════════════════════════════════════════════════════════
# LOGIN USERS  ← no changes needed
# ════════════════════════════════════════════════════════════
users = {
    "director": {"password": "director123", "role": "Director"},
    "ac":       {"password": "ac123",        "role": "AC"},
    "ps":       {"password": "ps123",        "role": "PS"},
    "mn":       {"password": "mn123",        "role": "MN"},
}

# ════════════════════════════════════════════════════════════
# LOGIN SCREEN  ← ★ UPDATED — dark-themed login card
# ════════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])

    with mid:
        st.markdown("""
        <div style="background:#1e2130;border:1px solid #2e3250;border-radius:14px;
                    padding:36px 32px;text-align:center;margin-bottom:24px;">
            <div style="font-size:40px;margin-bottom:10px;">🧵</div>
            <div style="font-size:20px;font-weight:700;color:#e8eaf6;margin-bottom:4px;">
                Directors Sales Dashboard</div>
            <div style="font-size:12px;color:#555d85;">Textile Dispatch & Sales Performance</div>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")

        if st.button("Login →", use_container_width=True):
            if username in users and password == users[username]["password"]:
                st.session_state.logged_in = True
                st.session_state.role = users[username]["role"]
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    st.stop()

# ════════════════════════════════════════════════════════════
# SIDEBAR  ← ★ UPDATED — dark sidebar with logo + sign out
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
        <div style="width:34px;height:34px;background:linear-gradient(135deg,#4f8ef7,#a259f7);
                    border-radius:8px;display:flex;align-items:center;justify-content:center;
                    font-size:18px;">🧵</div>
        <div>
            <div style="font-size:14px;font-weight:700;color:#e8eaf6;">Textile Sales</div>
            <div style="font-size:10px;color:#555d85;">Analytics Dashboard</div>
        </div>
    </div>
    <div style="background:rgba(62,207,142,0.1);border:1px solid rgba(62,207,142,0.25);
                border-radius:7px;padding:7px 12px;font-size:11px;color:#3ecf8e;margin-bottom:4px;">
        ● Logged in as <b>{st.session_state.role}</b>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

    st.markdown("<hr style='border-color:#2e3250;margin:14px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='color:#555d85;font-size:10px;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;'>Dashboard Filters</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# DATA LOADING  ← no changes needed
# ════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

df = load_data()

# ════════════════════════════════════════════════════════════
# ROLE-BASED FILTER  ← no changes needed
# ════════════════════════════════════════════════════════════
role = st.session_state.get("role")
if role and role != "Director":
    df = df[df["Sales_Team"] == role]

if df.empty:
    st.warning("No data available for this user.")
    st.stop()

# ════════════════════════════════════════════════════════════
# SIDEBAR FILTERS  ← no changes needed (filters still work same)
# ════════════════════════════════════════════════════════════
with st.sidebar:
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    if pd.isna(min_date) or pd.isna(max_date):
        min_date = max_date = pd.Timestamp.today()

    date_range = st.date_input("📅 Date Range", [min_date, max_date])

    customers = st.multiselect(
        "👤 Customer",
        df["Customer_Name"].unique(),
        default=df["Customer_Name"].unique()
    )
    sort_no = st.multiselect(
        "🔢 Sort No",
        df["Sort_Number"].unique(),
        default=df["Sort_Number"].unique()
    )
    sales_team = st.multiselect(
        "👥 Sales Team",
        df["Sales_Team"].unique(),
        default=df["Sales_Team"].unique()
    )

# ════════════════════════════════════════════════════════════
# APPLY FILTERS  ← no changes needed
# ════════════════════════════════════════════════════════════
filtered_df = df[
    (df["Customer_Name"].isin(customers)) &
    (df["Sort_Number"].isin(sort_no)) &
    (df["Sales_Team"].isin(sales_team)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

# ════════════════════════════════════════════════════════════
# PAGE HEADER  ← ★ UPDATED — dark styled header
# ════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:18px;">
    <div>
        <div style="font-size:22px;font-weight:700;color:#e8eaf6;">Directors Sales Dashboard</div>
        <div style="font-size:12px;color:#555d85;margin-top:3px;">
            Textile Dispatch & Sales Performance Overview ·
            <span style="color:#4f8ef7;">{len(filtered_df):,} rows</span>
        </div>
    </div>
    <div style="font-size:11px;color:#555d85;">Role: <b style="color:#3ecf8e;">{role}</b></div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# KPI CALCULATIONS  ← no changes needed
# ════════════════════════════════════════════════════════════
current_dispatch  = filtered_df["Dispatch_Meters"].sum()
total_orders      = filtered_df["GUI"].nunique()
total_customers   = filtered_df["Customer_Name"].nunique()
avg_order         = current_dispatch / total_orders if total_orders > 0 else 0

# ════════════════════════════════════════════════════════════
# ★ NEW — COLOURED KPI CARDS (replaces st.metric)
# ════════════════════════════════════════════════════════════
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(kpi_html("Total Dispatch (m)",
                         f"{current_dispatch:,.0f}",
                         "Total meters dispatched", "blue"),
                unsafe_allow_html=True)
with k2:
    st.markdown(kpi_html("Total Orders",
                         f"{total_orders:,}",
                         "Unique order IDs", "teal"),
                unsafe_allow_html=True)
with k3:
    st.markdown(kpi_html("Active Customers",
                         f"{total_customers:,}",
                         "Unique customers", "orange"),
                unsafe_allow_html=True)
with k4:
    st.markdown(kpi_html("Avg Order Size (m)",
                         f"{avg_order:,.0f}",
                         "Meters per order", "pink"),
                unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ★ NEW — ROW 2: Dispatch Trend (wide) + Fabric Donut
# ════════════════════════════════════════════════════════════
row2_left, row2_right = st.columns([2, 1])

with row2_left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    # ── Time granularity selector (your original logic, kept intact) ──
    granularity = st.selectbox("Time View", ["Daily", "Weekly", "Monthly"], key="gran")

    trend_df = filtered_df.copy()
    if granularity == "Weekly":
        trend_df["Date"] = trend_df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    elif granularity == "Monthly":
        trend_df["Date"] = trend_df["Date"].dt.to_period("M").apply(lambda r: r.start_time)

    dispatch_trend = trend_df.groupby("Date")["Dispatch_Meters"].sum().reset_index()

    # ── ★ UPDATED chart style ──
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=dispatch_trend["Date"],
        y=dispatch_trend["Dispatch_Meters"],
        name="Dispatch Meters",
        marker_color='rgba(79,142,247,0.7)',
        marker_line_color='#4f8ef7',
        marker_line_width=1,
    ))
    fig1.add_trace(go.Scatter(
        x=dispatch_trend["Date"],
        y=dispatch_trend["Dispatch_Meters"],
        name="Trend",
        line=dict(color='#3ecf8e', width=2),
        mode='lines+markers',
        marker=dict(size=4),
    ))
    fig1.update_layout(title="Dispatch Trend")
    apply_theme(fig1, height=300)
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with row2_right:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    # ── ★ NEW — Fabric Type donut (uses Fabric_Type column) ──
    if "Fabric_Type" in filtered_df.columns:
        fab_data = (filtered_df.groupby("Fabric_Type")["Dispatch_Meters"]
                    .sum().reset_index()
                    .sort_values("Dispatch_Meters", ascending=False))
        fig_fab = px.pie(fab_data, values="Dispatch_Meters", names="Fabric_Type",
                         hole=0.62, title="Meters by Fabric Type",
                         color_discrete_sequence=PAL)
        fig_fab.update_traces(textinfo='percent',
                              hovertemplate='<b>%{label}</b><br>%{value:,.0f} m<extra></extra>')
        fig_fab.update_layout(legend=dict(orientation='h', y=-0.15,
                                          font=dict(color='#8b93b8', size=10)))
        apply_theme(fig_fab, height=300)
        st.plotly_chart(fig_fab, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ★ NEW — ROW 3: Top Customers | City | Sales Team
# ════════════════════════════════════════════════════════════
r3c1, r3c2, r3c3 = st.columns(3)

with r3c1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    # ── your original Top Customers logic, updated styling ──
    top_customers = (
        filtered_df.groupby("Customer_Name")["Dispatch_Meters"]
        .sum().sort_values(ascending=False).head(5).reset_index()
    )
    fig_cust = px.bar(
        top_customers, x="Customer_Name", y="Dispatch_Meters",
        title="Top 5 Customers",
        text=top_customers["Dispatch_Meters"].apply(lambda x: f"{x:,.0f}"),
        color="Customer_Name", color_discrete_sequence=PAL
    )
    fig_cust.update_traces(textposition='outside', textfont=dict(color='#8b93b8', size=10))
    fig_cust.update_layout(showlegend=False)
    apply_theme(fig_cust, height=290)
    st.plotly_chart(fig_cust, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r3c2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    # ── your original City Performance logic, updated styling ──
    city_sales = (
        filtered_df.groupby("City")["Dispatch_Meters"]
        .sum().sort_values(ascending=False).reset_index()
    )
    fig_city = px.bar(
        city_sales, x="Dispatch_Meters", y="City",
        orientation="h", title="City Performance",
        text=city_sales["Dispatch_Meters"].apply(lambda x: f"{x:,.0f}"),
        color="City", color_discrete_sequence=PAL
    )
    fig_city.update_traces(textposition='outside', textfont=dict(color='#8b93b8', size=10))
    fig_city.update_layout(showlegend=False)
    apply_theme(fig_city, height=290)
    st.plotly_chart(fig_city, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r3c3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    # ── ★ NEW — Sales Team performance bar ──
    team_data = (
        filtered_df.groupby("Sales_Team")["Dispatch_Meters"]
        .sum().sort_values(ascending=False).reset_index()
    )
    fig_team = px.bar(
        team_data, x="Sales_Team", y="Dispatch_Meters",
        title="Sales Team Performance",
        color="Sales_Team", color_discrete_sequence=PAL,
        text=team_data["Dispatch_Meters"].apply(lambda x: f"{x:,.0f}")
    )
    fig_team.update_traces(textposition='outside', textfont=dict(color='#8b93b8', size=10))
    fig_team.update_layout(showlegend=False)
    apply_theme(fig_team, height=290)
    st.plotly_chart(fig_team, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ★ NEW — TOP CUSTOMERS TABLE  (replaces raw st.dataframe)
# ════════════════════════════════════════════════════════════
st.markdown("<hr style='border-color:#2e3250;margin:6px 0 18px;'>", unsafe_allow_html=True)
st.markdown("### 🏆 Top Customers — Detail")

cust_tbl = (
    filtered_df.groupby("Customer_Name").agg(
        City=("City", "first"),
        Sales_Team=("Sales_Team", "first"),
        Dispatch_Meters=("Dispatch_Meters", "sum"),
        Orders=("GUI", "nunique"),
        Avg_Rate=("Rate", "mean"),
    ).reset_index()
    .sort_values("Dispatch_Meters", ascending=False)
    .head(10)
    .reset_index(drop=True)
)
cust_tbl.index += 1
cust_tbl["Dispatch_Meters"] = cust_tbl["Dispatch_Meters"].apply(lambda x: f"{x:,.0f} m")
cust_tbl["Avg_Rate"]        = cust_tbl["Avg_Rate"].apply(lambda x: f"₹{x:,.1f}")
cust_tbl.columns            = ["Customer", "City", "Team", "Meters", "Orders", "Avg Rate"]

st.dataframe(cust_tbl, use_container_width=True, height=340)

# ════════════════════════════════════════════════════════════
# EXPORT  ← no changes needed, button style auto-updated by CSS
# ════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Filtered Data (CSV)",
    csv,
    "sales_data.csv",
    "text/csv"
)

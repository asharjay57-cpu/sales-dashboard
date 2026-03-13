import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

# ════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════
st.set_page_config(
    page_title="Directors Sales Dashboard",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ╔══════════════════════════════════════════╗
# ║  ★ PASTE 1 — DARK THEME CSS             ║
# ║  Put this right after set_page_config() ║
# ╚══════════════════════════════════════════╝
st.markdown("""
<style>
    .stApp { background-color: #111318; }
    .main .block-container { padding: 1.5rem 2rem 2rem; }
    [data-testid="stSidebar"] { background-color: #1a1d27 !important; border-right: 1px solid #2e3250; }
    [data-testid="stSidebar"] * { color: #e8eaf6 !important; }
    html, body, [class*="css"] { color: #e8eaf6; font-family: 'DM Sans', 'Segoe UI', sans-serif; }
    h1, h2, h3 { color: #e8eaf6 !important; }
    p, label, div { color: #e8eaf6; }
    .stMarkdown p { color: #8b93b8; }
    .stSelectbox > div > div,
    .stMultiSelect > div > div { background: #1e2130 !important; border: 1px solid #2e3250 !important; color: #e8eaf6 !important; border-radius: 8px !important; }
    [data-testid="stSidebar"] .stSelectbox > div,
    [data-testid="stSidebar"] .stMultiSelect > div,
    [data-testid="stSidebar"] .stDateInput > div { background: #1e2130 !important; border-color: #2e3250 !important; }
    .stTextInput > div > div > input { background: #1e2130 !important; border: 1px solid #2e3250 !important; color: #e8eaf6 !important; border-radius: 8px !important; }
    .stTextInput > div > div > input[type="password"] { background: #1e2130 !important; color: #e8eaf6 !important; }
    .stButton > button { background: linear-gradient(135deg,#4f8ef7,#a259f7) !important; border: none !important; color: white !important; border-radius: 8px !important; font-weight: 600 !important; padding: 8px 20px !important; }
    .stButton > button:hover { opacity: 0.88 !important; }
    .stDownloadButton > button { background: rgba(79,142,247,0.15) !important; border: 1px solid rgba(79,142,247,0.35) !important; color: #4f8ef7 !important; border-radius: 8px !important; font-weight: 600 !important; }
    [data-testid="stDataFrame"] { background: #1e2130 !important; border: 1px solid #2e3250; border-radius: 10px; }
    .dvn-scroller { background: #1e2130 !important; }
    hr { border-color: #2e3250 !important; }
    .stAlert { background: #1e2130 !important; border: 1px solid #2e3250 !important; color: #8b93b8 !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .kpi-card { background: #1e2130; border: 1px solid #2e3250; border-radius: 10px; padding: 18px 20px; position: relative; overflow: hidden; }
    .kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 10px 10px 0 0; }
    .kpi-blue::before   { background: #4f8ef7; }
    .kpi-teal::before   { background: #00c7b1; }
    .kpi-orange::before { background: #f7a84f; }
    .kpi-pink::before   { background: #e05c8a; }
    .kpi-lbl  { color: #555d85; font-size: 10px; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; margin-bottom: 5px; }
    .kpi-val-blue   { color: #4f8ef7; font-size: 28px; font-weight: 700; line-height: 1.1; }
    .kpi-val-teal   { color: #00c7b1; font-size: 28px; font-weight: 700; line-height: 1.1; }
    .kpi-val-orange { color: #f7a84f; font-size: 28px; font-weight: 700; line-height: 1.1; }
    .kpi-val-pink   { color: #e05c8a; font-size: 28px; font-weight: 700; line-height: 1.1; }
    .kpi-sub  { color: #555d85; font-size: 11px; margin-top: 4px; }
    .chart-card { background: #1e2130; border: 1px solid #2e3250; border-radius: 10px; padding: 16px 18px; margin-bottom: 14px; }
</style>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════╗
# ║  ★ PASTE 2 — HELPER FUNCTIONS           ║
# ║  Put this right after the CSS block     ║
# ╚══════════════════════════════════════════╝
PAL = ['#4f8ef7','#00c7b1','#f7a84f','#a259f7','#e05c8a','#3ecf8e','#f06070','#ffcc44','#56cfff','#b07cff']

def kpi_card(label, value, sub, color):
    return f"""<div class="kpi-card kpi-{color}">
        <div class="kpi-lbl">{label}</div>
        <div class="kpi-val-{color}">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""

def dark_chart(fig, height=300):
    fig.update_layout(
        paper_bgcolor='#1e2130', plot_bgcolor='#1e2130',
        font=dict(color='#8b93b8', family='DM Sans, Segoe UI, sans-serif', size=11),
        height=height, margin=dict(l=10, r=10, t=36, b=10),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#8b93b8', size=10)),
        colorway=PAL, title_font=dict(color='#e8eaf6', size=13),
    )
    fig.update_xaxes(gridcolor='rgba(46,50,80,0.6)', linecolor='#2e3250', tickfont=dict(color='#555d85'))
    fig.update_yaxes(gridcolor='rgba(46,50,80,0.6)', linecolor='#2e3250', tickfont=dict(color='#555d85'))
    return fig


# ════════════════════════════════════════
# YOUR EXISTING CODE GOES HERE (unchanged)
# — Google Sheets connection
# — Login users dict
# — Login logic
# — Sidebar sign out
# — load_data()
# — Role based filter
# — Empty data check
# — Sidebar filters
# — filtered_df
# ════════════════════════════════════════


# ╔══════════════════════════════════════════╗
# ║  ★ PASTE 3 — PAGE HEADER               ║
# ║  Replace your st.title() + st.caption() ║
# ╚══════════════════════════════════════════╝
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:20px;">
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


# ╔══════════════════════════════════════════╗
# ║  ★ PASTE 4 — KPI CARDS                 ║
# ║  Replace your col1.metric() lines       ║
# ╚══════════════════════════════════════════╝

# Keep your original KPI calculations unchanged:
# current_dispatch = filtered_df["Dispatch_Meters"].sum()
# total_orders     = filtered_df["GUI"].nunique()
# total_customers  = filtered_df["Customer_Name"].nunique()
# avg_order        = current_dispatch / total_orders if total_orders > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(kpi_card("Total Dispatch", f"{current_dispatch:,.0f}", "Total meters dispatched", "blue"), unsafe_allow_html=True)
with col2:
    st.markdown(kpi_card("Total Orders", f"{total_orders:,}", "Unique order IDs", "teal"), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_card("Customers", f"{total_customers:,}", "Unique customers", "orange"), unsafe_allow_html=True)
with col4:
    st.markdown(kpi_card("Avg Order Size", f"{avg_order:,.0f}", "Meters per order", "pink"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ╔══════════════════════════════════════════╗
# ║  ★ PASTE 5 — CHARTS                    ║
# ║  Replace everything from your           ║
# ║  granularity selectbox to the end       ║
# ╚══════════════════════════════════════════╝

# ── ROW 2: Dispatch Trend + Fabric Donut ──
left_col, right_col = st.columns([2, 1])

with left_col:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    granularity = st.selectbox("Time View", ["Daily", "Weekly", "Monthly"])

    trend_df = filtered_df.copy()
    if granularity == "Weekly":
        trend_df["Date"] = trend_df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    elif granularity == "Monthly":
        trend_df["Date"] = trend_df["Date"].dt.to_period("M").apply(lambda r: r.start_time)

    dispatch_trend = trend_df.groupby("Date")["Dispatch_Meters"].sum().reset_index()

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=dispatch_trend["Date"], y=dispatch_trend["Dispatch_Meters"],
        name="Dispatch Meters", marker_color='rgba(79,142,247,0.7)',
        marker_line_color='#4f8ef7', marker_line_width=1,
    ))
    fig1.add_trace(go.Scatter(
        x=dispatch_trend["Date"], y=dispatch_trend["Dispatch_Meters"],
        name="Trend Line", line=dict(color='#3ecf8e', width=2),
        mode='lines+markers', marker=dict(size=4),
    ))
    fig1.update_layout(title="Dispatch Trend")
    dark_chart(fig1, height=300)
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    if "Fabric_Type" in filtered_df.columns:
        fab = (filtered_df.groupby("Fabric_Type")["Dispatch_Meters"]
               .sum().reset_index().sort_values("Dispatch_Meters", ascending=False))
        fig_fab = px.pie(fab, values="Dispatch_Meters", names="Fabric_Type",
                         hole=0.62, title="Meters by Fabric Type",
                         color_discrete_sequence=PAL)
        fig_fab.update_traces(textinfo='percent',
                              hovertemplate='<b>%{label}</b><br>%{value:,.0f} m<extra></extra>')
        fig_fab.update_layout(legend=dict(orientation='h', y=-0.15, font=dict(color='#8b93b8', size=10)))
        dark_chart(fig_fab, height=300)
        st.plotly_chart(fig_fab, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── ROW 3: Top Customers | City | Sales Team ──
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    top_customers = (filtered_df.groupby("Customer_Name")["Dispatch_Meters"]
                     .sum().sort_values(ascending=False).head(5).reset_index())
    fig_cust = px.bar(
        top_customers, x="Customer_Name", y="Dispatch_Meters",
        title="Top 5 Customers",
        text=top_customers["Dispatch_Meters"].apply(lambda x: f"{x:,.0f}"),
        color="Customer_Name", color_discrete_sequence=PAL
    )
    fig_cust.update_traces(textposition='outside', textfont=dict(color='#8b93b8', size=10))
    fig_cust.update_layout(showlegend=False)
    dark_chart(fig_cust, height=290)
    st.plotly_chart(fig_cust, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    city_sales = (filtered_df.groupby("City")["Dispatch_Meters"]
                  .sum().sort_values(ascending=False).reset_index())
    fig_city = px.bar(
        city_sales, x="Dispatch_Meters", y="City",
        orientation="h", title="City Performance",
        text=city_sales["Dispatch_Meters"].apply(lambda x: f"{x:,.0f}"),
        color="City", color_discrete_sequence=PAL
    )
    fig_city.update_traces(textposition='outside', textfont=dict(color='#8b93b8', size=10))
    fig_city.update_layout(showlegend=False)
    dark_chart(fig_city, height=290)
    st.plotly_chart(fig_city, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    team_data = (filtered_df.groupby("Sales_Team")["Dispatch_Meters"]
                 .sum().sort_values(ascending=False).reset_index())
    fig_team = px.bar(
        team_data, x="Sales_Team", y="Dispatch_Meters",
        title="Sales Team Performance",
        color="Sales_Team", color_discrete_sequence=PAL,
        text=team_data["Dispatch_Meters"].apply(lambda x: f"{x:,.0f}")
    )
    fig_team.update_traces(textposition='outside', textfont=dict(color='#8b93b8', size=10))
    fig_team.update_layout(showlegend=False)
    dark_chart(fig_team, height=290)
    st.plotly_chart(fig_team, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── TOP CUSTOMERS TABLE ──
st.markdown("<hr style='border-color:#2e3250;margin:8px 0 20px;'>", unsafe_allow_html=True)
st.markdown("### 🏆 Top Customers — Detail")

cust_tbl = (
    filtered_df.groupby("Customer_Name").agg(
        City=("City", "first"),
        Sales_Team=("Sales_Team", "first"),
        Dispatch_Meters=("Dispatch_Meters", "sum"),
        Orders=("GUI", "nunique"),
    ).reset_index()
    .sort_values("Dispatch_Meters", ascending=False)
    .head(10).reset_index(drop=True)
)
cust_tbl.index += 1
cust_tbl["Dispatch_Meters"] = cust_tbl["Dispatch_Meters"].apply(lambda x: f"{x:,.0f} m")
cust_tbl.columns = ["Customer", "City", "Team", "Meters Dispatched", "Orders"]
st.dataframe(cust_tbl, use_container_width=True, height=340)

# ── EXPORT — your original download button, unchanged ──
st.markdown("<br>", unsafe_allow_html=True)
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Filtered Data", csv, "sales_data.csv", "text/csv")

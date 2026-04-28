import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nassau Candy – Shipping Route Efficiency",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #f72585;
        margin-bottom: 10px;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #f72585; }
    .metric-label { font-size: 0.85rem; color: #a0a0b0; margin-top: 4px; }
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        border-bottom: 2px solid #f72585;
        padding-bottom: 8px;
        margin: 20px 0 15px 0;
    }
    .stSelectbox label, .stSlider label, .stMultiSelect label { color: #c0c0d0 !important; }
    div[data-testid="stSidebarContent"] { background: #161825; }
</style>
""", unsafe_allow_html=True)

# ─── FACTORY DATA ────────────────────────────────────────────────────────────
FACTORY_COORDS = {
    "Lot's O' Nuts":    {"lat": 32.881893, "lon": -111.768036, "state": "Arizona"},
    "Wicked Choccy's":  {"lat": 32.076176, "lon": -81.088371,  "state": "Georgia"},
    "Sugar Shack":      {"lat": 48.11914,  "lon": -96.18115,   "state": "Minnesota"},
    "Secret Factory":   {"lat": 41.446333, "lon": -90.565487,  "state": "Iowa"},
    "The Other Factory":{"lat": 35.1175,   "lon": -89.971107,  "state": "Tennessee"},
}

PRODUCT_FACTORY = {
    'Wonka Bar - Nutty Crunch Surprise':  "Lot's O' Nuts",
    'Wonka Bar - Fudge Mallows':          "Lot's O' Nuts",
    'Wonka Bar -Scrumdiddlyumptious':     "Lot's O' Nuts",
    'Wonka Bar - Milk Chocolate':         "Wicked Choccy's",
    'Wonka Bar - Triple Dazzle Caramel':  "Wicked Choccy's",
    'Laffy Taffy':                        'Sugar Shack',
    'SweeTARTS':                          'Sugar Shack',
    'Nerds':                              'Sugar Shack',
    'Fun Dip':                            'Sugar Shack',
    'Fizzy Lifting Drinks':               'Sugar Shack',
    'Everlasting Gobstopper':             'Secret Factory',
    'Hair Toffee':                        'The Other Factory',
    'Lickable Wallpaper':                 'Secret Factory',
    'Wonka Gum':                          'Secret Factory',
    'Kazookles':                          'The Other Factory',
}

# US State abbreviations for map
STATE_ABBREV = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC',
}

# ─── DATA LOADING ────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    import os
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Nassau_Candy_Distributor.csv")
    df = pd.read_csv(csv_path)
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
    df['Ship Date']  = pd.to_datetime(df['Ship Date'],  dayfirst=True)
    df['Lead Time']  = (df['Ship Date'] - df['Order Date']).dt.days
    df = df[df['Lead Time'] >= 0].copy()
    df['Factory'] = df['Product Name'].map(PRODUCT_FACTORY)
    df['Route']   = df['Factory'] + ' → ' + df['State/Province']
    df['Factory_Region_Route'] = df['Factory'] + ' → ' + df['Region']
    df['State Abbrev'] = df['State/Province'].map(STATE_ABBREV)
    # Efficiency Score: lower lead time = higher score (0-100)
    min_lt = df['Lead Time'].min()
    max_lt = df['Lead Time'].max()
    df['Efficiency Score'] = 100 - ((df['Lead Time'] - min_lt) / (max_lt - min_lt) * 100)
    return df

df_raw = load_data()

# ─── SIDEBAR FILTERS ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍬 Nassau Candy")
    st.markdown("### Filters")

    date_min = df_raw['Order Date'].min().date()
    date_max = df_raw['Order Date'].max().date()
    date_range = st.date_input("📅 Order Date Range", value=(date_min, date_max),
                               min_value=date_min, max_value=date_max)

    regions = st.multiselect("🗺️ Region", options=sorted(df_raw['Region'].unique()),
                             default=sorted(df_raw['Region'].unique()))

    ship_modes = st.multiselect("🚚 Ship Mode", options=sorted(df_raw['Ship Mode'].unique()),
                                default=sorted(df_raw['Ship Mode'].unique()))

    factories = st.multiselect("🏭 Factory", options=sorted(df_raw['Factory'].unique()),
                               default=sorted(df_raw['Factory'].unique()))

    lt_threshold = st.slider("⏱️ Lead Time Threshold (days)",
                             min_value=int(df_raw['Lead Time'].min()),
                             max_value=int(df_raw['Lead Time'].max()),
                             value=int(df_raw['Lead Time'].quantile(0.75)))

    st.markdown("---")
    st.markdown("**📊 Dashboard Modules**")
    st.markdown("↑ Use tabs above to navigate")

# ─── APPLY FILTERS ───────────────────────────────────────────────────────────
if len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_date, end_date = df_raw['Order Date'].min(), df_raw['Order Date'].max()

df = df_raw[
    (df_raw['Order Date'] >= start_date) &
    (df_raw['Order Date'] <= end_date) &
    (df_raw['Region'].isin(regions)) &
    (df_raw['Ship Mode'].isin(ship_modes)) &
    (df_raw['Factory'].isin(factories))
].copy()

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background: linear-gradient(90deg, #f72585, #7209b7); padding: 25px 30px; border-radius: 16px; margin-bottom: 25px;'>
    <h1 style='color:white; margin:0; font-size:2.2rem;'>🍬 Nassau Candy Distributor</h1>
    <p style='color:#f0d0ff; margin:6px 0 0 0; font-size:1.05rem;'>Factory-to-Customer Shipping Route Efficiency Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ─── KPI CARDS ───────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
total_orders    = len(df)
avg_lead_time   = df['Lead Time'].mean()
delay_pct       = (df['Lead Time'] > lt_threshold).mean() * 100
avg_eff_score   = df['Efficiency Score'].mean()
total_routes    = df['Route'].nunique()

for col, val, label, icon in zip(
    [k1, k2, k3, k4, k5],
    [f"{total_orders:,}", f"{avg_lead_time:.0f} days", f"{delay_pct:.1f}%", f"{avg_eff_score:.1f}/100", f"{total_routes}"],
    ["Total Orders", "Avg Lead Time", "Delay Rate", "Avg Efficiency Score", "Unique Routes"],
    ["📦", "⏱️", "⚠️", "⭐", "🛣️"]
):
    col.markdown(f"""
    <div class='metric-card'>
        <div style='font-size:1.5rem;'>{icon}</div>
        <div class='metric-value'>{val}</div>
        <div class='metric-label'>{label}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Route Efficiency Overview",
    "🗺️ Geographic Map",
    "🚚 Ship Mode Analysis",
    "🔍 Route Drill-Down"
])

# ════════════════════════════════════════════════════════════════════
# TAB 1 — ROUTE EFFICIENCY OVERVIEW
# ════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-header'>Route Performance Leaderboard</div>", unsafe_allow_html=True)

    route_stats = df.groupby('Route').agg(
        Avg_Lead_Time=('Lead Time', 'mean'),
        Std_Lead_Time=('Lead Time', 'std'),
        Total_Shipments=('Row ID', 'count'),
        Avg_Efficiency=('Efficiency Score', 'mean'),
        Delay_Count=('Lead Time', lambda x: (x > lt_threshold).sum()),
    ).reset_index()
    route_stats['Delay Rate %'] = (route_stats['Delay_Count'] / route_stats['Total_Shipments'] * 100).round(1)
    route_stats['Avg_Lead_Time'] = route_stats['Avg_Lead_Time'].round(1)
    route_stats['Avg_Efficiency'] = route_stats['Avg_Efficiency'].round(1)
    route_stats = route_stats.sort_values('Avg_Lead_Time')

    col_top, col_bot = st.columns(2)

    with col_top:
        st.markdown("#### 🏆 Top 10 Most Efficient Routes")
        top10 = route_stats.head(10).copy()
        fig = px.bar(top10, x='Avg_Lead_Time', y='Route', orientation='h',
                     color='Avg_Efficiency',
                     color_continuous_scale='RdYlGn',
                     labels={'Avg_Lead_Time': 'Avg Lead Time (days)', 'Route': ''},
                     text='Avg_Lead_Time')
        fig.update_traces(texttemplate='%{text:.0f}d', textposition='outside')
        fig.update_layout(
            plot_bgcolor='#1e2130', paper_bgcolor='#1e2130',
            font_color='white', height=420,
            yaxis={'categoryorder': 'total ascending'},
            coloraxis_colorbar=dict(title='Efficiency', tickfont=dict(color='white'), title_font=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_bot:
        st.markdown("#### 🐌 Bottom 10 Least Efficient Routes")
        bot10 = route_stats.tail(10).copy()
        fig2 = px.bar(bot10, x='Avg_Lead_Time', y='Route', orientation='h',
                      color='Avg_Efficiency',
                      color_continuous_scale='RdYlGn',
                      labels={'Avg_Lead_Time': 'Avg Lead Time (days)', 'Route': ''},
                      text='Avg_Lead_Time')
        fig2.update_traces(texttemplate='%{text:.0f}d', textposition='outside')
        fig2.update_layout(
            plot_bgcolor='#1e2130', paper_bgcolor='#1e2130',
            font_color='white', height=420,
            yaxis={'categoryorder': 'total descending'},
            coloraxis_colorbar=dict(title='Efficiency', tickfont=dict(color='white'), title_font=dict(color='white'))
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>Lead Time Distribution by Factory</div>", unsafe_allow_html=True)
    fig3 = px.box(df, x='Factory', y='Lead Time', color='Factory',
                  points='outliers',
                  color_discrete_sequence=px.colors.qualitative.Bold)
    fig3.update_layout(plot_bgcolor='#1e2130', paper_bgcolor='#1e2130',
                       font_color='white', height=400, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='section-header'>Full Route Statistics Table</div>", unsafe_allow_html=True)
    display_df = route_stats[['Route','Total_Shipments','Avg_Lead_Time','Std_Lead_Time','Avg_Efficiency','Delay Rate %']].copy()
    display_df.columns = ['Route','Shipments','Avg Lead Time (days)','Std Dev','Efficiency Score','Delay Rate %']
    display_df['Std Dev'] = display_df['Std Dev'].round(1)
    st.dataframe(display_df, use_container_width=True, height=350)

# ════════════════════════════════════════════════════════════════════
# TAB 2 — GEOGRAPHIC MAP
# ════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-header'>US Shipping Efficiency Heatmap</div>", unsafe_allow_html=True)

    state_stats = df.groupby(['State/Province', 'State Abbrev']).agg(
        Avg_Lead_Time=('Lead Time', 'mean'),
        Total_Shipments=('Row ID', 'count'),
        Avg_Efficiency=('Efficiency Score', 'mean'),
    ).reset_index().dropna(subset=['State Abbrev'])
    state_stats['Avg_Lead_Time'] = state_stats['Avg_Lead_Time'].round(1)
    state_stats['Avg_Efficiency'] = state_stats['Avg_Efficiency'].round(1)

    map_metric = st.radio("Color Map By:", ["Avg Lead Time (days)", "Efficiency Score", "Total Shipments"],
                          horizontal=True)

    if map_metric == "Avg Lead Time (days)":
        color_col, color_scale, label = 'Avg_Lead_Time', 'RdYlGn_r', 'Avg Lead Time'
    elif map_metric == "Efficiency Score":
        color_col, color_scale, label = 'Avg_Efficiency', 'RdYlGn', 'Efficiency Score'
    else:
        color_col, color_scale, label = 'Total_Shipments', 'Blues', 'Shipments'

    fig_map = px.choropleth(
        state_stats,
        locations='State Abbrev',
        locationmode='USA-states',
        color=color_col,
        scope='usa',
        color_continuous_scale=color_scale,
        hover_name='State/Province',
        hover_data={'State Abbrev': False, 'Avg_Lead_Time': True, 'Total_Shipments': True, 'Avg_Efficiency': True},
        labels={color_col: label},
        title=f'US States — {map_metric}'
    )
    fig_map.update_layout(
        geo=dict(bgcolor='#1e2130', lakecolor='#1e2130', landcolor='#2a2f45'),
        paper_bgcolor='#1e2130', font_color='white', height=520,
        title_font=dict(size=18, color='white')
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Factory locations overlay
    st.markdown("<div class='section-header'>Factory Locations & Regional Performance</div>", unsafe_allow_html=True)

    col_map2, col_reg = st.columns([3, 2])

    with col_map2:
        factory_df = pd.DataFrame([
            {"Factory": k, "Lat": v["lat"], "Lon": v["lon"], "State": v["state"]}
            for k, v in FACTORY_COORDS.items()
        ])
        factory_orders = df.groupby('Factory').agg(
            Orders=('Row ID','count'), Avg_LT=('Lead Time','mean')).reset_index()
        factory_df = factory_df.merge(factory_orders, on='Factory', how='left')

        fig_fac = px.scatter_geo(factory_df, lat='Lat', lon='Lon',
                                 scope='usa', text='Factory',
                                 size='Orders', color='Avg_LT',
                                 color_continuous_scale='RdYlGn_r',
                                 hover_name='Factory',
                                 hover_data={'Lat': False, 'Lon': False, 'Avg_LT': ':.1f'},
                                 title='Factory Locations (bubble = order volume)')
        fig_fac.update_traces(textposition='top center', textfont=dict(color='white', size=10))
        fig_fac.update_layout(
            geo=dict(bgcolor='#1e2130', lakecolor='#1e2130', landcolor='#2a2f45',
                     showland=True, showcountries=False, showlakes=True),
            paper_bgcolor='#1e2130', font_color='white', height=420
        )
        st.plotly_chart(fig_fac, use_container_width=True)

    with col_reg:
        st.markdown("#### Regional Summary")
        region_stats = df.groupby('Region').agg(
            Orders=('Row ID','count'),
            Avg_LT=('Lead Time','mean'),
            Avg_Eff=('Efficiency Score','mean'),
        ).reset_index().sort_values('Avg_LT')
        region_stats['Avg_LT'] = region_stats['Avg_LT'].round(1)
        region_stats['Avg_Eff'] = region_stats['Avg_Eff'].round(1)

        fig_reg = px.bar(region_stats, x='Region', y='Avg_LT',
                         color='Avg_Eff', color_continuous_scale='RdYlGn',
                         text='Avg_LT',
                         labels={'Avg_LT': 'Avg Lead Time (days)', 'Avg_Eff': 'Efficiency'})
        fig_reg.update_traces(texttemplate='%{text:.0f}d', textposition='outside')
        fig_reg.update_layout(plot_bgcolor='#1e2130', paper_bgcolor='#1e2130',
                               font_color='white', height=300)
        st.plotly_chart(fig_reg, use_container_width=True)

        st.dataframe(region_stats.rename(columns={
            'Orders':'Shipments','Avg_LT':'Avg Lead Time','Avg_Eff':'Efficiency Score'
        }), use_container_width=True)

    # Bottleneck detection
    st.markdown("<div class='section-header'>⚠️ Geographic Bottleneck Detection</div>", unsafe_allow_html=True)
    bottleneck = state_stats[state_stats['Total_Shipments'] >= 50].sort_values('Avg_Lead_Time', ascending=False).head(10)
    fig_bot = px.scatter(bottleneck, x='Total_Shipments', y='Avg_Lead_Time',
                         size='Total_Shipments', color='Avg_Lead_Time',
                         text='State/Province',
                         color_continuous_scale='RdYlGn_r',
                         labels={'Total_Shipments':'Shipments','Avg_Lead_Time':'Avg Lead Time (days)'},
                         title='High-Volume States with Poor Performance (Bottlenecks)')
    fig_bot.update_traces(textposition='top center')
    fig_bot.update_layout(plot_bgcolor='#1e2130', paper_bgcolor='#1e2130',
                           font_color='white', height=400)
    st.plotly_chart(fig_bot, use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 3 — SHIP MODE ANALYSIS
# ════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-header'>Ship Mode Performance Comparison</div>", unsafe_allow_html=True)

    mode_stats = df.groupby('Ship Mode').agg(
        Avg_LT=('Lead Time','mean'),
        Median_LT=('Lead Time','median'),
        Std_LT=('Lead Time','std'),
        Orders=('Row ID','count'),
        Avg_Sales=('Sales','mean'),
        Total_Sales=('Sales','sum'),
        Avg_Cost=('Cost','mean'),
        Avg_Profit=('Gross Profit','mean'),
        Avg_Eff=('Efficiency Score','mean'),
        Delay_Count=('Lead Time', lambda x: (x > lt_threshold).sum()),
    ).reset_index()
    mode_stats['Delay Rate %'] = (mode_stats['Delay_Count'] / mode_stats['Orders'] * 100).round(1)

    c1, c2, c3 = st.columns(3)

    with c1:
        fig_mode1 = px.bar(mode_stats.sort_values('Avg_LT'), x='Ship Mode', y='Avg_LT',
                           color='Ship Mode', text='Avg_LT',
                           color_discrete_sequence=px.colors.qualitative.Bold,
                           title='Average Lead Time by Ship Mode')
        fig_mode1.update_traces(texttemplate='%{text:.0f}d', textposition='outside')
        fig_mode1.update_layout(plot_bgcolor='#1e2130', paper_bgcolor='#1e2130',
                                font_color='white', showlegend=False, height=350)
        st.plotly_chart(fig_mode1, use_container_width=True)

    with c2:
        fig_mode2 = px.pie(mode_stats, values='Orders', names='Ship Mode',
                           color_discrete_sequence=px.colors.qualitative.Bold,
                           title='Order Volume Distribution')
        fig_mode2.update_layout(paper_bgcolor='#1e2130', font_color='white', height=350)
        st.plotly_chart(fig_mode2, use_container_width=True)

    with c3:
        fig_mode3 = px.bar(mode_stats.sort_values('Delay Rate %', ascending=False),
                           x='Ship Mode', y='Delay Rate %',
                           color='Ship Mode', text='Delay Rate %',
                           color_discrete_sequence=px.colors.qualitative.Bold,
                           title=f'Delay Rate % (threshold: {lt_threshold} days)')
        fig_mode3.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_mode3.update_layout(plot_bgcolor='#1e2130', paper_bgcolor='#1e2130',
                                font_color='white', showlegend=False, height=350)
        st.plotly_chart(fig_mode3, use_container_width=True)

    st.markdown("<div class='section-header'>Lead Time Distribution — Violin Chart</div>", unsafe_allow_html=True)
    fig_vio = px.violin(df, x='Ship Mode', y='Lead Time', color='Ship Mode',
                        box=True, points='outliers',
                        color_discrete_sequence=px.colors.qualitative.Bold)
    fig_vio.update_layout(plot_bgcolor='#1e2130', paper_bgcolor='#1e2130',
                           font_color='white', height=420, showlegend=False)
    st.plotly_chart(fig_vio, use_container_width=True)

    st.markdown("<div class='section-header'>Cost vs Lead Time Tradeoff</div>", unsafe_allow_html=True)
    fig_cost = px.scatter(df.sample(min(2000, len(df))), x='Lead Time', y='Cost',
                          color='Ship Mode', size='Sales',
                          opacity=0.6,
                          color_discrete_sequence=px.colors.qualitative.Bold,
                          labels={'Lead Time':'Lead Time (days)','Cost':'Order Cost ($)'},
                          title='Cost vs Lead Time by Ship Mode (sample of 2000 orders)')
    fig_cost.update_layout(plot_bgcolor='#1e2130', paper_bgcolor='#1e2130',
                            font_color='white', height=420)
    st.plotly_chart(fig_cost, use_container_width=True)

    st.markdown("<div class='section-header'>Ship Mode Summary Table</div>", unsafe_allow_html=True)
    display_mode = mode_stats[['Ship Mode','Orders','Avg_LT','Median_LT','Std_LT','Avg_Profit','Delay Rate %','Avg_Eff']].copy()
    display_mode.columns = ['Ship Mode','Orders','Avg Lead Time','Median Lead Time','Std Dev','Avg Profit ($)','Delay Rate %','Efficiency Score']
    display_mode = display_mode.round(2)
    st.dataframe(display_mode, use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# TAB 4 — ROUTE DRILL-DOWN
# ════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("<div class='section-header'>State-Level Performance Insights</div>", unsafe_allow_html=True)

    selected_state = st.selectbox("Select a State to Drill Down:", sorted(df['State/Province'].unique()))
    state_df = df[df['State/Province'] == selected_state].copy()

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Orders", f"{len(state_df):,}")
    s2.metric("Avg Lead Time", f"{state_df['Lead Time'].mean():.0f} days")
    s3.metric("Efficiency Score", f"{state_df['Efficiency Score'].mean():.1f}/100")
    s4.metric("Delay Rate", f"{(state_df['Lead Time'] > lt_threshold).mean()*100:.1f}%")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.markdown(f"#### Factory Performance → {selected_state}")
        state_factory = state_df.groupby('Factory').agg(
            Orders=('Row ID','count'),
            Avg_LT=('Lead Time','mean'),
            Avg_Eff=('Efficiency Score','mean'),
        ).reset_index().sort_values('Avg_LT')
        fig_sf = px.bar(state_factory, x='Factory', y='Avg_LT',
                        color='Avg_Eff', color_continuous_scale='RdYlGn',
                        text='Avg_LT',
                        labels={'Avg_LT':'Avg Lead Time (days)','Avg_Eff':'Efficiency'})
        fig_sf.update_traces(texttemplate='%{text:.0f}d', textposition='outside')
        fig_sf.update_layout(plot_bgcolor='#1e2130', paper_bgcolor='#1e2130',
                              font_color='white', height=350, xaxis_tickangle=-20)
        st.plotly_chart(fig_sf, use_container_width=True)

    with col_d2:
        st.markdown(f"#### Ship Mode Split → {selected_state}")
        state_mode = state_df.groupby('Ship Mode').agg(
            Orders=('Row ID','count'),
            Avg_LT=('Lead Time','mean'),
        ).reset_index()
        fig_sm = px.pie(state_mode, values='Orders', names='Ship Mode',
                        color_discrete_sequence=px.colors.qualitative.Bold,
                        title='Orders by Ship Mode')
        fig_sm.update_layout(paper_bgcolor='#1e2130', font_color='white', height=350)
        st.plotly_chart(fig_sm, use_container_width=True)

    st.markdown(f"#### 📅 Monthly Shipment Timeline — {selected_state}")
    state_df['Month'] = state_df['Order Date'].dt.to_period('M').astype(str)
    monthly = state_df.groupby('Month').agg(
        Orders=('Row ID','count'),
        Avg_LT=('Lead Time','mean'),
    ).reset_index()
    fig_time = make_subplots(specs=[[{"secondary_y": True}]])
    fig_time.add_trace(go.Bar(x=monthly['Month'], y=monthly['Orders'],
                               name='Orders', marker_color='#7209b7'), secondary_y=False)
    fig_time.add_trace(go.Scatter(x=monthly['Month'], y=monthly['Avg_LT'],
                                   name='Avg Lead Time', line=dict(color='#f72585', width=2),
                                   mode='lines+markers'), secondary_y=True)
    fig_time.update_layout(plot_bgcolor='#1e2130', paper_bgcolor='#1e2130',
                            font_color='white', height=380,
                            legend=dict(bgcolor='#1e2130'))
    fig_time.update_yaxes(title_text='Orders', secondary_y=False, gridcolor='#2a2f45')
    fig_time.update_yaxes(title_text='Avg Lead Time (days)', secondary_y=True)
    fig_time.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_time, use_container_width=True)

    st.markdown("#### 📋 Order-Level Shipment Details")
    order_display = state_df[['Order ID','Order Date','Ship Date','Lead Time',
                               'Ship Mode','Factory','Product Name','Sales','Efficiency Score']].copy()
    order_display['Order Date'] = order_display['Order Date'].dt.strftime('%d-%m-%Y')
    order_display['Ship Date']  = order_display['Ship Date'].dt.strftime('%d-%m-%Y')
    order_display['Efficiency Score'] = order_display['Efficiency Score'].round(1)
    order_display = order_display.sort_values('Lead Time')
    st.dataframe(order_display, use_container_width=True, height=300)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#606080; font-size:0.85rem; padding: 10px;'>
    🍬 Nassau Candy Distributor — Shipping Route Efficiency Dashboard &nbsp;|&nbsp;
    Built with Streamlit & Plotly &nbsp;|&nbsp; Unified Mentor Internship Project
</div>
""", unsafe_allow_html=True)

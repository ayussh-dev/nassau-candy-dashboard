import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="Nassau Candy — Route Intelligence",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap');

*, html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

/* ── ANIMATED BACKGROUND ── */
.stApp {
    background: #07040a;
    overflow-x: hidden;
}

/* ── MOVING CANDY DOTS BACKGROUND ── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image:
        radial-gradient(circle 2px at 10% 20%, rgba(255,180,0,0.15) 0%, transparent 100%),
        radial-gradient(circle 2px at 90% 10%, rgba(255,80,40,0.12) 0%, transparent 100%),
        radial-gradient(circle 2px at 50% 80%, rgba(255,180,0,0.1) 0%, transparent 100%),
        radial-gradient(circle 2px at 70% 50%, rgba(255,100,0,0.08) 0%, transparent 100%),
        linear-gradient(135deg, rgba(255,180,0,0.02) 0%, transparent 50%, rgba(255,80,40,0.02) 100%);
    animation: bgShift 15s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes bgShift {
    0%   { transform: scale(1) rotate(0deg);   opacity: 0.8; }
    50%  { transform: scale(1.05) rotate(1deg); opacity: 1; }
    100% { transform: scale(1) rotate(-1deg);  opacity: 0.8; }
}

/* ── GOLDEN GLOW ORB ── */
.stApp::after {
    content: '';
    position: fixed;
    bottom: -300px; right: -300px;
    width: 700px; height: 700px;
    background: radial-gradient(circle, rgba(255,180,0,0.08) 0%, transparent 70%);
    animation: orbFloat 10s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
    border-radius: 50%;
}

@keyframes orbFloat {
    0%   { transform: translate(0,0) scale(1); }
    50%  { transform: translate(-150px,-100px) scale(1.3); }
    100% { transform: translate(-50px,-200px) scale(0.9); }
}

/* ── SIDEBAR ── */
div[data-testid="stSidebarContent"] {
    background: rgba(7,4,10,0.97) !important;
    border-right: 1px solid rgba(255,180,0,0.15) !important;
    backdrop-filter: blur(20px);
}

#MainMenu, footer, header { visibility: hidden; }

/* ── KPI CARDS ── */
.kpi-wrap {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,180,0,0.18);
    border-radius: 20px;
    padding: 24px 20px 20px;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    animation: cardIn 0.7s ease backwards;
}

.kpi-wrap:hover {
    transform: translateY(-10px) scale(1.03);
    border-color: rgba(255,180,0,0.7);
    box-shadow:
        0 25px 60px rgba(255,140,0,0.25),
        0 0 40px rgba(255,180,0,0.15),
        inset 0 0 30px rgba(255,180,0,0.04);
}

.kpi-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,180,0,0.08), transparent);
    transition: left 0.7s ease;
}
.kpi-wrap:hover::before { left: 100%; }

.kpi-wrap::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #ffb400, #ff5028, #ffb400);
    background-size: 200% 100%;
    animation: shimmer 2s linear infinite;
}

@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
@keyframes cardIn { from{opacity:0;transform:translateY(40px)} to{opacity:1;transform:translateY(0)} }

.kpi-icon {
    font-size: 1.6rem; margin-bottom: 10px; display: block;
    animation: iconBounce 2.5s ease-in-out infinite;
}
@keyframes iconBounce { 0%,100%{transform:translateY(0) rotate(0deg)} 50%{transform:translateY(-6px) rotate(5deg)} }

.kpi-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(135deg, #ffb400, #ff7a00);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1; letter-spacing: -1px;
}
.kpi-label {
    font-size: 0.72rem; color: rgba(255,255,255,0.28);
    text-transform: uppercase; letter-spacing: 2px; margin-top: 8px;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,180,0,0.12);
    border-radius: 16px; padding: 5px; gap: 3px;
    backdrop-filter: blur(10px);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important; font-size: 0.83rem !important;
    color: rgba(255,255,255,0.3) !important;
    border-radius: 12px !important; padding: 10px 22px !important;
    border: none !important; background: transparent !important;
    transition: all 0.3s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: rgba(255,255,255,0.7) !important;
    background: rgba(255,180,0,0.08) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #ffb400, #ff7a00) !important;
    color: #07040a !important;
    box-shadow: 0 4px 20px rgba(255,140,0,0.5), 0 0 40px rgba(255,180,0,0.2) !important;
    transform: scale(1.02) !important;
}

/* ── DIVIDER ── */
.fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,180,0,0.4), rgba(255,80,40,0.4), transparent);
    margin: 28px 0; position: relative;
}
.fancy-divider::after {
    content: '🍬';
    position: absolute; left: 50%; top: 50%;
    transform: translate(-50%,-50%);
    font-size: 0.9rem; background: #07040a; padding: 0 8px;
    animation: candySpin 4s linear infinite;
}
@keyframes candySpin { from{transform:translate(-50%,-50%) rotate(0deg)} to{transform:translate(-50%,-50%) rotate(360deg)} }

/* ── SECTION HEADERS ── */
.sec-label {
    font-family: 'Outfit', sans-serif; font-size: 0.65rem; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase; color: #ffb400;
    background: rgba(255,180,0,0.08); border: 1px solid rgba(255,180,0,0.2);
    border-radius: 100px; padding: 4px 16px; display: inline-block; margin-bottom: 10px;
    animation: tagGlow 3s ease-in-out infinite;
}
@keyframes tagGlow { 0%,100%{box-shadow:0 0 0 0 rgba(255,180,0,0)} 50%{box-shadow:0 0 20px rgba(255,180,0,0.4)} }

.sec-title {
    font-size: 1.6rem; font-weight: 800; color: #ffffff;
    margin-bottom: 22px; letter-spacing: -0.5px; line-height: 1.2;
}

/* ── SIDEBAR BRAND ── */
.sidebar-brand {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem; color: #ffb400; letter-spacing: 3px;
    text-shadow: 0 0 20px rgba(255,180,0,0.6);
    animation: brandGlow 2s ease-in-out infinite alternate;
}
@keyframes brandGlow {
    from { text-shadow: 0 0 20px rgba(255,180,0,0.4); }
    to   { text-shadow: 0 0 40px rgba(255,180,0,1), 0 0 80px rgba(255,140,0,0.4); }
}
.sidebar-sub { font-size: 0.68rem; color: rgba(255,255,255,0.2); letter-spacing: 3px; text-transform: uppercase; margin-bottom: 22px; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #07040a; }
::-webkit-scrollbar-thumb { background: linear-gradient(#ffb400, #ff5028); border-radius: 10px; }

/* ── SLIDER ── */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: linear-gradient(135deg, #ffb400, #ff7a00) !important;
    box-shadow: 0 0 15px rgba(255,180,0,0.6) !important;
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:fixed;top:0;left:0;pointer-events:none;z-index:99999;width:100%;height:100%;';
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    window.addEventListener('resize', () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; });

    let particles = [];

    document.addEventListener('mousemove', (e) => {
        for(let i = 0; i < 2; i++) {
            particles.push({
                x: e.clientX, y: e.clientY,
                vx: (Math.random()-0.5)*4, vy: (Math.random()-0.5)*4 - 1,
                life: 1, size: Math.random()*5+1,
                color: Math.random() > 0.5 ? '255,180,0' : '255,80,40',
                shape: Math.random() > 0.7 ? 'star' : 'circle'
            });
        }
    });

    document.addEventListener('click', (e) => {
        const emojis = ['🍬','🍭','⭐','✨','💛','🧡'];
        for(let i = 0; i < 25; i++) {
            const angle = (Math.PI*2/25)*i;
            particles.push({
                x: e.clientX, y: e.clientY,
                vx: Math.cos(angle)*8, vy: Math.sin(angle)*8,
                life: 1, size: Math.random()*7+3,
                color: Math.random() > 0.5 ? '255,180,0' : '255,100,20',
                shape: 'circle'
            });
        }
    });

    function animate() {
        ctx.clearRect(0,0,canvas.width,canvas.height);
        particles = particles.filter(p => p.life > 0);
        particles.forEach(p => {
            p.x += p.vx; p.y += p.vy;
            p.vx *= 0.94; p.vy *= 0.94;
            p.vy += 0.05;
            p.life -= 0.022;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI*2);
            ctx.fillStyle = `rgba(${p.color},${p.life})`;
            ctx.shadowBlur = 15;
            ctx.shadowColor = `rgba(${p.color},0.9)`;
            ctx.fill();
        });
        requestAnimationFrame(animate);
    }
    animate();
});
</script>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
FACTORY_COORDS = {
    "Lot's O' Nuts":     {"lat": 32.881893, "lon": -111.768036},
    "Wicked Choccy's":   {"lat": 32.076176, "lon": -81.088371},
    "Sugar Shack":       {"lat": 48.11914,  "lon": -96.18115},
    "Secret Factory":    {"lat": 41.446333, "lon": -90.565487},
    "The Other Factory": {"lat": 35.1175,   "lon": -89.971107},
}

PRODUCT_FACTORY = {
    'Wonka Bar - Nutty Crunch Surprise':  "Lot's O' Nuts",
    'Wonka Bar - Fudge Mallows':          "Lot's O' Nuts",
    'Wonka Bar -Scrumdiddlyumptious':     "Lot's O' Nuts",
    'Wonka Bar - Milk Chocolate':         "Wicked Choccy's",
    'Wonka Bar - Triple Dazzle Caramel':  "Wicked Choccy's",
    'Laffy Taffy':          'Sugar Shack',
    'SweeTARTS':            'Sugar Shack',
    'Nerds':                'Sugar Shack',
    'Fun Dip':              'Sugar Shack',
    'Fizzy Lifting Drinks': 'Sugar Shack',
    'Everlasting Gobstopper':'Secret Factory',
    'Hair Toffee':          'The Other Factory',
    'Lickable Wallpaper':   'Secret Factory',
    'Wonka Gum':            'Secret Factory',
    'Kazookles':            'The Other Factory',
}

STATE_ABBREV = {
    'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
    'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
    'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS',
    'Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA',
    'Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT',
    'Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM',
    'New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK',
    'Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC',
    'South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT',
    'Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY',
    'District of Columbia':'DC',
}

GOLD   = "#ffb400"
ORANGE = "#ff7a00"
RED    = "#ff3a3a"
SEQ    = [GOLD, ORANGE, "#ff5028", "#ffd166", "#e76f51", "#e9c46a"]
CHART  = dict(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(7,4,10,0.97)",
              font_color="#94a3b8", font_family="Outfit")

def cl(fig, h=400, **kw):
    fig.update_layout(**CHART, height=h, margin=dict(l=15,r=15,t=40,b=15),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748b")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.03)", zerolinecolor="rgba(255,255,255,0.03)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.03)", zerolinecolor="rgba(255,255,255,0.03)"), **kw)
    return fig

# ── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Nassau_Candy_Distributor.csv")
    df = pd.read_csv(csv_path)
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
    df['Ship Date']  = pd.to_datetime(df['Ship Date'],  dayfirst=True)
    df['Lead Time']  = (df['Ship Date'] - df['Order Date']).dt.days
    df = df[df['Lead Time'] >= 0].copy()
    df['Factory']      = df['Product Name'].map(PRODUCT_FACTORY)
    df['Route']        = df['Factory'] + ' to ' + df['State/Province']
    df['State Abbrev'] = df['State/Province'].map(STATE_ABBREV)
    mn, mx = df['Lead Time'].min(), df['Lead Time'].max()
    df['Efficiency Score'] = 100 - ((df['Lead Time'] - mn) / (mx - mn) * 100)
    return df

df_raw = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sidebar-brand'>🍬 NASSAU</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-sub'>Candy Route Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

    date_min = df_raw['Order Date'].min().date()
    date_max = df_raw['Order Date'].max().date()
    date_range = st.date_input("Date Range", value=(date_min, date_max), min_value=date_min, max_value=date_max)
    regions    = st.multiselect("Region",    options=sorted(df_raw['Region'].unique()),    default=sorted(df_raw['Region'].unique()))
    ship_modes = st.multiselect("Ship Mode", options=sorted(df_raw['Ship Mode'].unique()), default=sorted(df_raw['Ship Mode'].unique()))
    factories  = st.multiselect("Factory",   options=sorted(df_raw['Factory'].unique()),   default=sorted(df_raw['Factory'].unique()))
    lt_threshold = st.slider("Delay Threshold (days)",
                             min_value=int(df_raw['Lead Time'].min()),
                             max_value=int(df_raw['Lead Time'].max()),
                             value=int(df_raw['Lead Time'].quantile(0.75)))

if len(date_range) == 2:
    s_date, e_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    s_date, e_date = df_raw['Order Date'].min(), df_raw['Order Date'].max()

df = df_raw[
    (df_raw['Order Date'] >= s_date) & (df_raw['Order Date'] <= e_date) &
    (df_raw['Region'].isin(regions)) & (df_raw['Ship Mode'].isin(ship_modes)) &
    (df_raw['Factory'].isin(factories))
].copy()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:50px 0 36px;">
    <div style="font-size:0.68rem;font-weight:700;letter-spacing:5px;text-transform:uppercase;
                color:#ffb400;margin-bottom:14px;animation:fadeUp 0.6s ease backwards;">
        ◆ Nassau Candy Distributor · Logistics Intelligence ◆
    </div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:4rem;font-weight:400;
                color:#fff;line-height:0.95;letter-spacing:3px;
                animation:fadeUp 0.8s ease 0.1s backwards;">
        SHIPPING ROUTE
        <span style="background:linear-gradient(90deg,#ffb400,#ff7a00,#ff5028,#ffb400);
                     background-size:300% 100%;
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                     animation:gradFlow 3s linear infinite;">
            EFFICIENCY
        </span>
    </div>
    <div style="font-size:0.9rem;color:rgba(255,255,255,0.2);margin-top:16px;
                letter-spacing:1px;animation:fadeUp 1s ease 0.2s backwards;">
        5 Factories &nbsp;·&nbsp; 10,194 Shipments &nbsp;·&nbsp; 59 States &nbsp;·&nbsp; Real-Time Analytics
    </div>
</div>
<style>
@keyframes fadeUp { from{opacity:0;transform:translateY(25px)} to{opacity:1;transform:translateY(0)} }
@keyframes gradFlow { 0%{background-position:0% 50%} 100%{background-position:300% 50%} }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5 = st.columns(5)
for col,icon,val,lbl in [
    (k1,"📦",f"{len(df):,}","Total Orders"),
    (k2,"⏱",f"{df['Lead Time'].mean():.0f}d","Avg Lead Time"),
    (k3,"⚡",f"{df['Efficiency Score'].mean():.1f}","Avg Efficiency"),
    (k4,"🚨",f"{(df['Lead Time']>lt_threshold).mean()*100:.1f}%","Delay Rate"),
    (k5,"🛣️",f"{df['Route'].nunique()}","Active Routes"),
]:
    col.markdown(f"""<div class='kpi-wrap'>
        <div class='kpi-icon'>{icon}</div>
        <div class='kpi-val'>{val}</div>
        <div class='kpi-label'>{lbl}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4 = st.tabs([
    "  📊  Route Overview  ",
    "  🗺️  Geographic Map  ",
    "  🚚  Ship Mode  ",
    "  🔍  Drill-Down  ",
])

# ════════════════════════════════════
# TAB 1 — ROUTE OVERVIEW
# ════════════════════════════════════
with tab1:
    rs = df.groupby('Route').agg(
        Avg_Lead_Time=('Lead Time','mean'),
        Std_Lead_Time=('Lead Time','std'),
        Total_Shipments=('Row ID','count'),
        Avg_Efficiency=('Efficiency Score','mean'),
        Delay_Count=('Lead Time', lambda x:(x>lt_threshold).sum()),
    ).reset_index()
    rs['Delay Rate %'] = (rs['Delay_Count']/rs['Total_Shipments']*100).round(1)
    rs['Avg_Lead_Time'] = rs['Avg_Lead_Time'].round(1)
    rs['Avg_Efficiency'] = rs['Avg_Efficiency'].round(1)
    rs = rs.sort_values('Avg_Lead_Time')

    st.markdown("<div class='sec-label'>Performance Leaderboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>Best & Worst Delivery Routes</div>", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        fig = px.bar(rs.head(10), x='Avg_Lead_Time', y='Route', orientation='h',
                     color='Avg_Efficiency', color_continuous_scale=[[0,'#ff3a3a'],[0.5,'#ffb400'],[1,'#00e676']],
                     text='Avg_Lead_Time', title="🏆 Top 10 Fastest Routes")
        fig.update_traces(texttemplate='%{text:.0f}d', textposition='outside', marker_line_width=0)
        cl(fig,430); fig.update_layout(yaxis={'categoryorder':'total ascending'})
        fig.update_coloraxes(colorbar=dict(tickfont=dict(color='#a0a0b0'),title_font=dict(color='#a0a0b0')))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(rs.tail(10), x='Avg_Lead_Time', y='Route', orientation='h',
                      color='Avg_Efficiency', color_continuous_scale=[[0,'#ff3a3a'],[0.5,'#ffb400'],[1,'#00e676']],
                      text='Avg_Lead_Time', title="🐌 Bottom 10 Slowest Routes")
        fig2.update_traces(texttemplate='%{text:.0f}d', textposition='outside', marker_line_width=0)
        cl(fig2,430); fig2.update_layout(yaxis={'categoryorder':'total descending'})
        fig2.update_coloraxes(colorbar=dict(tickfont=dict(color='#a0a0b0'),title_font=dict(color='#a0a0b0')))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>Lead Time Distribution by Factory</div>", unsafe_allow_html=True)
    fig3 = px.violin(df, x='Factory', y='Lead Time', color='Factory', box=True, points='outliers', color_discrete_sequence=SEQ)
    fig3.update_layout(showlegend=False); cl(fig3,380)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>All Route Statistics</div>", unsafe_allow_html=True)
    disp = rs[['Route','Total_Shipments','Avg_Lead_Time','Std_Lead_Time','Avg_Efficiency','Delay Rate %']].copy()
    disp.columns = ['Route','Shipments','Avg Lead Time','Std Dev','Efficiency Score','Delay Rate %']
    disp['Std Dev'] = disp['Std Dev'].round(1)
    st.dataframe(disp, use_container_width=True, height=320)

# ════════════════════════════════════
# TAB 2 — GEOGRAPHIC MAP
# ════════════════════════════════════
with tab2:
    ss = df.groupby(['State/Province','State Abbrev']).agg(
        Avg_Lead_Time=('Lead Time','mean'),
        Total_Shipments=('Row ID','count'),
        Avg_Efficiency=('Efficiency Score','mean'),
    ).reset_index().dropna(subset=['State Abbrev']).round(1)

    st.markdown("<div class='sec-label'>Geographic Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>US Shipping Efficiency Map</div>", unsafe_allow_html=True)

    mc = st.radio("Color By:", ["Avg Lead Time","Efficiency Score","Total Shipments"], horizontal=True)
    cmap = {'Avg Lead Time':('Avg_Lead_Time','RdYlGn_r'),'Efficiency Score':('Avg_Efficiency','RdYlGn'),'Total Shipments':('Total_Shipments','YlOrRd')}
    cc, cs = cmap[mc]

    fig_map = px.choropleth(ss, locations='State Abbrev', locationmode='USA-states',
                            color=cc, scope='usa', color_continuous_scale=cs,
                            hover_name='State/Province',
                            hover_data={'State Abbrev':False,'Avg_Lead_Time':True,'Total_Shipments':True,'Avg_Efficiency':True})
    fig_map.update_layout(
        geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#07040a', landcolor='#1a1200', showland=True),
        paper_bgcolor='rgba(7,4,10,0.97)', font_color='#94a3b8', height=500,
        margin=dict(l=0,r=0,t=10,b=0),
        coloraxis_colorbar=dict(tickfont=dict(color='#a0a0b0'),title_font=dict(color='#a0a0b0'))
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
    cf, cr = st.columns([3,2])
    with cf:
        st.markdown("<div class='sec-title'>Factory Network Locations</div>", unsafe_allow_html=True)
        fdf = pd.DataFrame([{"Factory":k,"Lat":v["lat"],"Lon":v["lon"]} for k,v in FACTORY_COORDS.items()])
        fo = df.groupby('Factory').agg(Orders=('Row ID','count'),Avg_LT=('Lead Time','mean')).reset_index()
        fdf = fdf.merge(fo, on='Factory', how='left')
        ffig = px.scatter_geo(fdf, lat='Lat', lon='Lon', scope='usa', text='Factory',
                              size='Orders', color='Avg_LT', color_continuous_scale='YlOrRd',
                              hover_name='Factory', hover_data={'Lat':False,'Lon':False,'Avg_LT':':.1f'})
        ffig.update_traces(textposition='top center', textfont=dict(color='#ffb400', size=10))
        ffig.update_layout(
            geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#07040a', landcolor='#1a1200', showland=True),
            paper_bgcolor='rgba(7,4,10,0.97)', font_color='#94a3b8', height=400,
            margin=dict(l=0,r=0,t=10,b=0),
            coloraxis_colorbar=dict(tickfont=dict(color='#a0a0b0'),title_font=dict(color='#a0a0b0'))
        )
        st.plotly_chart(ffig, use_container_width=True)
    with cr:
        st.markdown("<div class='sec-title'>By Region</div>", unsafe_allow_html=True)
        reg = df.groupby('Region').agg(Orders=('Row ID','count'),Avg_LT=('Lead Time','mean'),Avg_Eff=('Efficiency Score','mean')).reset_index().sort_values('Avg_LT')
        rfig = px.bar(reg, x='Region', y='Avg_LT', color='Avg_Eff',
                      color_continuous_scale=[[0,'#ff3a3a'],[0.5,'#ffb400'],[1,'#00e676']], text='Avg_LT')
        rfig.update_traces(texttemplate='%{text:.0f}d', textposition='outside', marker_line_width=0)
        cl(rfig,280)
        rfig.update_coloraxes(colorbar=dict(tickfont=dict(color='#a0a0b0'),title_font=dict(color='#a0a0b0')))
        st.plotly_chart(rfig, use_container_width=True)
        st.dataframe(reg.rename(columns={'Orders':'Shipments','Avg_LT':'Avg Lead Time','Avg_Eff':'Efficiency'}).round(1), use_container_width=True)

    st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>High-Volume Problem States</div>", unsafe_allow_html=True)
    bn = ss[ss['Total_Shipments']>=50].sort_values('Avg_Lead_Time', ascending=False).head(10)
    bfig = px.scatter(bn, x='Total_Shipments', y='Avg_Lead_Time', size='Total_Shipments',
                      color='Avg_Lead_Time', text='State/Province', color_continuous_scale='YlOrRd',
                      labels={'Total_Shipments':'Shipments','Avg_Lead_Time':'Avg Lead Time (days)'})
    bfig.update_traces(textposition='top center', textfont=dict(color='#ffb400'))
    cl(bfig,400)
    bfig.update_coloraxes(colorbar=dict(tickfont=dict(color='#a0a0b0'),title_font=dict(color='#a0a0b0')))
    st.plotly_chart(bfig, use_container_width=True)

# ════════════════════════════════════
# TAB 3 — SHIP MODE
# ════════════════════════════════════
with tab3:
    ms = df.groupby('Ship Mode').agg(
        Avg_LT=('Lead Time','mean'), Median_LT=('Lead Time','median'),
        Std_LT=('Lead Time','std'), Orders=('Row ID','count'),
        Avg_Profit=('Gross Profit','mean'), Avg_Eff=('Efficiency Score','mean'),
        Delay_Count=('Lead Time', lambda x:(x>lt_threshold).sum()),
    ).reset_index()
    ms['Delay Rate %'] = (ms['Delay_Count']/ms['Orders']*100).round(1)

    st.markdown("<div class='sec-label'>Ship Mode Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>Performance by Shipping Method</div>", unsafe_allow_html=True)

    m1,m2,m3 = st.columns(3)
    with m1:
        mf1 = px.bar(ms.sort_values('Avg_LT'), x='Ship Mode', y='Avg_LT', color='Ship Mode',
                     text='Avg_LT', color_discrete_sequence=SEQ, title="Avg Lead Time")
        mf1.update_traces(texttemplate='%{text:.0f}d', textposition='outside', marker_line_width=0)
        cl(mf1,350,showlegend=False); st.plotly_chart(mf1, use_container_width=True)
    with m2:
        mf2 = px.pie(ms, values='Orders', names='Ship Mode', color_discrete_sequence=SEQ, title="Volume Split", hole=0.5)
        mf2.update_layout(paper_bgcolor='rgba(7,4,10,0.97)', font_color='#94a3b8', height=350, margin=dict(l=10,r=10,t=40,b=10), legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#64748b")))
        st.plotly_chart(mf2, use_container_width=True)
    with m3:
        mf3 = px.bar(ms.sort_values('Delay Rate %',ascending=False), x='Ship Mode', y='Delay Rate %',
                     color='Ship Mode', text='Delay Rate %', color_discrete_sequence=SEQ, title="Delay Rate %")
        mf3.update_traces(texttemplate='%{text:.1f}%', textposition='outside', marker_line_width=0)
        cl(mf3,350,showlegend=False); st.plotly_chart(mf3, use_container_width=True)

    st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>Lead Time Spread by Ship Mode</div>", unsafe_allow_html=True)
    vfig = px.violin(df, x='Ship Mode', y='Lead Time', color='Ship Mode', box=True, points='outliers', color_discrete_sequence=SEQ)
    vfig.update_layout(showlegend=False); cl(vfig,400)
    st.plotly_chart(vfig, use_container_width=True)

    st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>Cost vs Speed Tradeoff</div>", unsafe_allow_html=True)
    cfig = px.scatter(df.sample(min(2000,len(df))), x='Lead Time', y='Cost',
                      color='Ship Mode', size='Sales', opacity=0.55, color_discrete_sequence=SEQ)
    cl(cfig,400); st.plotly_chart(cfig, use_container_width=True)

    st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
    dm = ms[['Ship Mode','Orders','Avg_LT','Median_LT','Std_LT','Avg_Profit','Delay Rate %','Avg_Eff']].round(2)
    dm.columns = ['Ship Mode','Orders','Avg Lead Time','Median','Std Dev','Avg Profit ($)','Delay Rate %','Efficiency']
    st.dataframe(dm, use_container_width=True)

# ════════════════════════════════════
# TAB 4 — DRILL DOWN
# ════════════════════════════════════
with tab4:
    st.markdown("<div class='sec-label'>State-Level Deep Dive</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>Route Drill-Down</div>", unsafe_allow_html=True)

    sel = st.selectbox("Select a State:", sorted(df['State/Province'].unique()))
    sdf = df[df['State/Province']==sel].copy()

    d1,d2,d3,d4 = st.columns(4)
    for col,icon,val,lbl in [
        (d1,"📦",f"{len(sdf):,}","Orders"),
        (d2,"⏱",f"{sdf['Lead Time'].mean():.0f}d","Avg Lead Time"),
        (d3,"⚡",f"{sdf['Efficiency Score'].mean():.1f}","Efficiency"),
        (d4,"🚨",f"{(sdf['Lead Time']>lt_threshold).mean()*100:.1f}%","Delay Rate"),
    ]:
        col.markdown(f"""<div class='kpi-wrap'>
            <div class='kpi-icon'>{icon}</div>
            <div class='kpi-val'>{val}</div>
            <div class='kpi-label'>{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    dd1,dd2 = st.columns(2)
    with dd1:
        sf = sdf.groupby('Factory').agg(Orders=('Row ID','count'),Avg_LT=('Lead Time','mean'),Avg_Eff=('Efficiency Score','mean')).reset_index().sort_values('Avg_LT')
        sff = px.bar(sf, x='Factory', y='Avg_LT', color='Avg_Eff',
                     color_continuous_scale=[[0,'#ff3a3a'],[0.5,'#ffb400'],[1,'#00e676']],
                     text='Avg_LT', title=f"Factory Performance → {sel}")
        sff.update_traces(texttemplate='%{text:.0f}d', textposition='outside', marker_line_width=0)
        cl(sff,350); sff.update_layout(xaxis_tickangle=-20)
        sff.update_coloraxes(colorbar=dict(tickfont=dict(color='#a0a0b0'),title_font=dict(color='#a0a0b0')))
        st.plotly_chart(sff, use_container_width=True)
    with dd2:
        sm = sdf.groupby('Ship Mode').agg(Orders=('Row ID','count')).reset_index()
        smf = px.pie(sm, values='Orders', names='Ship Mode', color_discrete_sequence=SEQ,
                     title=f"Ship Mode → {sel}", hole=0.5)
        smf.update_layout(paper_bgcolor='rgba(7,4,10,0.97)', font_color='#94a3b8', height=350, margin=dict(l=10,r=10,t=40,b=10), legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#64748b")))
        st.plotly_chart(smf, use_container_width=True)

    st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sec-title'>Monthly Timeline — {sel}</div>", unsafe_allow_html=True)
    sdf['Month'] = sdf['Order Date'].dt.to_period('M').astype(str)
    mon = sdf.groupby('Month').agg(Orders=('Row ID','count'),Avg_LT=('Lead Time','mean')).reset_index()
    tfig = make_subplots(specs=[[{"secondary_y":True}]])
    tfig.add_trace(go.Bar(x=mon['Month'],y=mon['Orders'],name='Orders',marker_color=GOLD,opacity=0.7), secondary_y=False)
    tfig.add_trace(go.Scatter(x=mon['Month'],y=mon['Avg_LT'],name='Avg Lead Time',
                              line=dict(color=ORANGE,width=2.5),mode='lines+markers',
                              marker=dict(size=6,color=ORANGE)), secondary_y=True)
    tfig.update_layout(**CHART, height=380, margin=dict(l=20,r=20,t=20,b=40),
                       legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(color='#64748b')))
    tfig.update_xaxes(tickangle=-45, gridcolor='rgba(255,255,255,0.03)')
    tfig.update_yaxes(title_text='Orders', secondary_y=False, gridcolor='rgba(255,255,255,0.03)')
    tfig.update_yaxes(title_text='Lead Time (days)', secondary_y=True)
    st.plotly_chart(tfig, use_container_width=True)

    st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>Order-Level Details</div>", unsafe_allow_html=True)
    od = sdf[['Order ID','Order Date','Ship Date','Lead Time','Ship Mode','Factory','Product Name','Sales','Efficiency Score']].copy()
    od['Order Date'] = od['Order Date'].dt.strftime('%d-%m-%Y')
    od['Ship Date']  = od['Ship Date'].dt.strftime('%d-%m-%Y')
    od['Efficiency Score'] = od['Efficiency Score'].round(1)
    st.dataframe(od.sort_values('Lead Time'), use_container_width=True, height=280)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<div class='fancy-divider'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;padding:16px 0 30px;font-size:0.7rem;
            color:rgba(255,255,255,0.1);letter-spacing:2px;font-family:'Outfit',sans-serif;">
    🍬 NASSAU CANDY DISTRIBUTOR &nbsp;·&nbsp; ROUTE INTELLIGENCE &nbsp;·&nbsp; UNIFIED MENTOR &nbsp;·&nbsp; AYUSH PRAKASH G
</div>
""", unsafe_allow_html=True)

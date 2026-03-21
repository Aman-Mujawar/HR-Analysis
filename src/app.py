import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Diverse STEM Talent Finder",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #2d3250);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #4f8bf9;
        margin: 5px 0;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #4f8bf9; }
    .metric-label { font-size: 0.85rem; color: #a0aec0; margin-top: 4px; }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #e2e8f0;
        padding: 10px 0 5px 0;
        border-bottom: 2px solid #4f8bf9;
        margin-bottom: 20px;
    }
    .insight-box {
        background: linear-gradient(135deg, #1a2744, #1e3a5f);
        border-radius: 10px;
        padding: 15px 20px;
        border-left: 4px solid #63b3ed;
        margin: 10px 0;
        color: #bee3f8;
        font-size: 0.95rem;
    }
    div[data-testid="stSidebarContent"] {
        background: linear-gradient(180deg, #1a1f2e, #141824);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('../data/clean_eeo_data.csv')
    return df

df = load_data()

RACE_COLORS = {
    'Hispanic or Latino':               '#F6AD55',
    'Black or African American':        '#68D391',
    'Asian':                            '#63B3ED',
    'American Indian / Alaska Native':  '#FC8181',
    'Native Hawaiian / Pacific Islander':'#B794F4',
    'White':                            '#A0AEC0',
}

st.sidebar.image(
    "https://img.icons8.com/fluency/96/diversity.png", width=60
)
st.sidebar.title("🎛️ Control Panel")
st.sidebar.markdown("---")

# Occupation filter
st.sidebar.markdown("**📋 Occupation**")
all_occs = sorted(df['occupation'].unique().tolist())
selected_occs = st.sidebar.multiselect(
    "Select Occupations",
    options=all_occs,
    default=all_occs,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Race filter
st.sidebar.markdown("**👥 Demographic Groups**")
all_races = sorted(df['race'].unique().tolist())
selected_races = st.sidebar.multiselect(
    "Select Groups",
    options=all_races,
    default=[r for r in all_races if r != 'White'],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Threshold slider
st.sidebar.markdown("**📊 Min Representation %**")
min_pct = st.sidebar.slider(
    "Threshold", 0.0, 50.0, 5.0, 0.5,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Top N states
st.sidebar.markdown("**🏆 Top N States to Show**")
top_n = st.sidebar.slider(
    "Top N", 5, 30, 15, 1,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Deselect 'White' to focus on underrepresented groups only.")

df_f = df[
    (df['occupation'].isin(selected_occs)) &
    (df['race'].isin(selected_races)) &
    (df['percent'] >= min_pct)
].copy()


col_logo, col_title = st.columns([1, 11])
with col_title:
    st.markdown("# 🔬 Diverse STEM Talent Finder")
    st.markdown(
        "**Team 4 — Diversity & Inclusion Officers** | "
        "Identifying underutilized diverse professionals for satellite office placement"
    )

st.markdown("---")

k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, value, label, color="#4f8bf9"):
    col.markdown(f"""
    <div class="metric-card" style="border-left-color:{color}">
        <div class="metric-value" style="color:{color}">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

kpi(k1, df_f['state'].nunique(),      "📍 Areas Found",        "#4f8bf9")
kpi(k2, df_f['occupation'].nunique(), "💼 Occupations",        "#68D391")
kpi(k3, df_f['race'].nunique(),       "👥 Demographic Groups", "#F6AD55")
kpi(k4, len(df_f),                    "📊 Data Points",        "#B794F4")
kpi(k5, f"{df_f['percent'].mean():.1f}%", "📈 Avg Representation", "#FC8181")

st.markdown("<br>", unsafe_allow_html=True)

# ── Guard: empty filter ───────────────────────────────────────────────────────
if df_f.empty:
    st.warning("⚠️ No data matches your filters. Try lowering the minimum % or selecting more groups.")
    st.stop()

st.markdown('<div class="section-header">📊 Geographic Distribution of Diverse STEM Talent</div>', unsafe_allow_html=True)

col_bar, col_pie = st.columns([2, 1])

with col_bar:
    df_state = (
        df_f.groupby('state')['percent']
        .mean().reset_index()
        .sort_values('percent', ascending=False)
        .head(top_n)
    )

    fig_bar = px.bar(
        df_state.sort_values('percent', ascending=True),
        x='percent',
        y='state',
        orientation='h',
        color='percent',
        color_continuous_scale='Teal',
        labels={'percent': 'Avg Representation %', 'state': ''},
        title=f'Top {top_n} Areas by Avg Diverse Representation %'
    )
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e8f0',
        coloraxis_showscale=False,
        margin=dict(l=10, r=20, t=40, b=10),
        height=420
    )
    fig_bar.update_xaxes(gridcolor='#2d3250', zerolinecolor='#2d3250')
    fig_bar.update_yaxes(gridcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_pie:
    df_pie = df_f.groupby('race')['percent'].mean().reset_index()
    fig_pie = px.pie(
        df_pie,
        names='race',
        values='percent',
        color='race',
        color_discrete_map=RACE_COLORS,
        title='Avg Representation by Demographic Group',
        hole=0.45
    )
    fig_pie.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e8f0',
        legend=dict(orientation='v', font=dict(size=11)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=420
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

top_area = df_state.iloc[-1]['state'] if not df_state.empty else "N/A"
top_pct  = df_state.iloc[-1]['percent'] if not df_state.empty else 0
st.markdown(f"""
<div class="insight-box">
    💡 <strong>Key Insight:</strong> <strong>{top_area}</strong> leads with
    <strong>{top_pct:.1f}%</strong> average diverse STEM representation —
    making it a strong candidate for a satellite office placement.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-header">🧩 Demographic Breakdown by Area</div>', unsafe_allow_html=True)

top_states_list = df_state['state'].tolist()
df_breakdown = df_f[df_f['state'].isin(top_states_list)]

fig_group = px.bar(
    df_breakdown,
    x='state',
    y='percent',
    color='race',
    barmode='group',
    color_discrete_map=RACE_COLORS,
    labels={'percent': 'Representation %', 'state': 'Area', 'race': 'Demographic'},
    title=f'Demographic Breakdown — Top {top_n} Areas',
    hover_data={'occupation': True}
)
fig_group.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='#e2e8f0',
    xaxis_tickangle=-35,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    margin=dict(l=10, r=10, t=60, b=80),
    height=420
)
fig_group.update_xaxes(gridcolor='#2d3250')
fig_group.update_yaxes(gridcolor='#2d3250')
st.plotly_chart(fig_group, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-header">🌡️ Representation Heatmap — Area × Demographic</div>', unsafe_allow_html=True)

df_heat = (
    df_f[df_f['state'].isin(top_states_list)]
    .groupby(['state', 'race'])['percent']
    .mean().reset_index()
    .pivot(index='race', columns='state', values='percent')
    .fillna(0)
)

fig_heat = px.imshow(
    df_heat,
    color_continuous_scale='Teal',
    aspect='auto',
    labels=dict(x='Area', y='Demographic Group', color='Representation %'),
    title=f'Representation % Heatmap (Top {top_n} Areas)'
)
fig_heat.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='#e2e8f0',
    xaxis_tickangle=-35,
    margin=dict(l=10, r=10, t=40, b=80),
    height=380
)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-header">🎯 Opportunity Gap — Underutilized Talent by Area</div>', unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
    🎯 <strong>What is the Opportunity Gap?</strong>
    Areas where diverse groups have a presence but representation stays below 20%
    signal <strong>underutilized talent pools</strong> — ideal targets for satellite offices.
</div>
""", unsafe_allow_html=True)

df_gap = (
    df_f[df_f['percent'].between(min_pct, 20)]
    .groupby(['state', 'race'])['percent']
    .mean().reset_index()
    .sort_values('percent', ascending=False)
    .rename(columns={'state': 'Area', 'race': 'Demographic', 'percent': 'Representation %'})
    .reset_index(drop=True)
)
df_gap['Opportunity Score'] = (20 - df_gap['Representation %']).round(1)
df_gap['Representation %'] = df_gap['Representation %'].round(1)

st.dataframe(
    df_gap.head(30),
    use_container_width=True,
    height=380,
    column_config={
        'Representation %': st.column_config.ProgressColumn(
            'Representation %', min_value=0, max_value=20, format='%.1f%%'
        ),
        'Opportunity Score': st.column_config.ProgressColumn(
            'Opportunity Score ↑', min_value=0, max_value=20, format='%.1f'
        ),
    }
)

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("📋 View Full Filtered Dataset"):
    st.dataframe(
        df_f.sort_values('percent', ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=350
    )
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=df_f.to_csv(index=False),
        file_name='filtered_stem_diversity.csv',
        mime='text/csv'
    )

st.markdown("---")
st.markdown(
    "<center><small>Data: US Census ACS EEO 5-Year Estimates (2018) &nbsp;|&nbsp; "
    "Team 4 — Diversity & Inclusion Officers &nbsp;|&nbsp; HR Consultants for Tech Consortium</small></center>",
    unsafe_allow_html=True
)
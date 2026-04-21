import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os

from groq import Groq

st.set_page_config(
    page_title="Diverse STEM Talent Finder",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .main { background-color: #0f1117; }
  .metric-card {
    background: linear-gradient(135deg, #1e2130, #2d3250);
    border-radius: 12px; padding: 20px;
    border-left: 4px solid #4f8bf9; margin: 5px 0;
  }
  .metric-value { font-size: 2rem; font-weight: 700; color: #4f8bf9; }
  .metric-label { font-size: 0.85rem; color: #a0aec0; margin-top: 4px; }
  .section-header {
    font-size: 1.3rem; font-weight: 600; color: #e2e8f0;
    padding: 10px 0 5px 0; border-bottom: 2px solid #4f8bf9;
    margin-bottom: 20px;
  }
  .insight-box {
    background: linear-gradient(135deg, #1a2744, #1e3a5f);
    border-radius: 10px; padding: 15px 20px;
    border-left: 4px solid #63b3ed; margin: 10px 0;
    color: #bee3f8; font-size: 0.95rem; line-height: 1.6;
  }
  .stTabs [data-baseweb="tab-list"] {
    gap: 6px; background-color: #1a1f2e;
    border-radius: 12px; padding: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 8px; color: #a0aec0; font-weight: 500;
    font-size: 1rem; padding: 8px 20px;
  }
  .stTabs [aria-selected="true"] {
    background-color: #2d3250 !important; color: #4f8bf9 !important;
    font-weight: 700 !important;
  }
  div[data-testid="stSidebarContent"] {
    background: linear-gradient(180deg, #1a1f2e, #141824);
  }
  [data-testid="stChatMessage"] {
    background-color: #1e2130 !important;
    border-radius: 12px !important;
  }
  .suggest-btn button {
    background: linear-gradient(135deg, #1e2130, #2d3250) !important;
    border: 1px solid #4f8bf9 !important;
    border-radius: 10px !important;
    color: #bee3f8 !important;
    font-size: 0.88rem !important;
    padding: 12px !important;
    height: auto !important;
    white-space: normal !important;
    text-align: left !important;
    line-height: 1.4 !important;
  }
  .suggest-btn button:hover {
    background: linear-gradient(135deg, #2d3250, #3d4a7a) !important;
    border-color: #63b3ed !important;
    color: #fff !important;
  }
</style>
""", unsafe_allow_html=True)

RACE_COLORS = {
    'Hispanic or Latino':                '#F6AD55',
    'Black or African American':         '#68D391',
    'Asian':                             '#63B3ED',
    'American Indian / Alaska Native':   '#FC8181',
    'Native Hawaiian / Pacific Islander':'#B794F4',
    'White':                             '#A0AEC0',
}

@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, '..', 'Data', 'clean_eeo_data.csv')
    df = pd.read_csv(path)
    df = df[~df['state'].str.contains('Metro Area|Micro Area|Division|Region', na=False)]
    return df

df = load_data()

# Derive option lists from full unfiltered dataframe
ALL_OCCS  = sorted(df['occupation'].unique().tolist())
ALL_RACES = sorted(df['race'].unique().tolist())

US_STATES = {
    'Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut',
    'Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa',
    'Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan',
    'Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada',
    'New Hampshire','New Jersey','New Mexico','New York','North Carolina',
    'North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island',
    'South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont',
    'Virginia','Washington','West Virginia','Wisconsin','Wyoming',
    'District of Columbia','Puerto Rico',
}

@st.cache_data
def build_ai_context(df: pd.DataFrame) -> str:
    state_df = df[df['state'].isin(US_STATES)]
    agg = (
        state_df.groupby(['state', 'race'])['percent']
        .agg(avg='mean', hi='max').round(1).reset_index()
    )
    top_occ = (
        state_df.loc[state_df.groupby(['state', 'race'])['percent'].idxmax(),
                     ['state', 'race', 'occupation']]
        .reset_index(drop=True)
    )
    merged = agg.merge(top_occ, on=['state', 'race'], how='left')
    lines = ["state|demographic|avg_pct|max_pct|top_occupation"]
    for _, r in merged.iterrows():
        lines.append(f"{r['state']}|{r['race']}|{r['avg']}%|{r['hi']}%|{r['occupation']}")
    return "\n".join(lines)

AI_DATA_CONTEXT = build_ai_context(df)

SYSTEM_PROMPT = f"""You are an expert Diversity & Inclusion HR consultant AI specializing in STEM workforce analytics.

You have access to US Census ACS EEO 2018 data on diverse group representation across STEM occupations in all 50 US states and DC.

DATA (pipe-separated: state | demographic | avg_representation% | max_representation% | top_occupation):
{AI_DATA_CONTEXT}

RESPONSE RULES:
- Always cite specific states with exact % figures from the data above
- Rank top 3-5 recommendations with **bold state names**
- Briefly explain the business case per recommendation
- Add regional context and suggest major metros within that state to investigate
- Flag opportunity gaps: presence but below 15% avg representation means untapped talent pool
- Consider ALL demographic groups when answering, not just one
- If asked about cities, clarify data is state-level and suggest major metros
- Keep tone concise, data-driven, and executive-ready
- Format with clear headers and bullet points
"""

@st.cache_resource
def get_client():
    api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
    if not api_key:
        return None
    return Groq(api_key=api_key)

client = get_client()

st.sidebar.image("https://img.icons8.com/fluency/96/diversity.png", width=60)
st.sidebar.title("🎛️ Control Panel")
st.sidebar.markdown("---")

st.sidebar.markdown("**📋 Occupation**")
selected_occs = st.sidebar.multiselect(
    "Occupations",
    options=ALL_OCCS,
    default=ALL_OCCS,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**👥 Demographic Groups**")
selected_races = st.sidebar.multiselect(
    "Groups",
    options=ALL_RACES,
    default=ALL_RACES,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Min Representation %**")
min_pct = st.sidebar.slider(
    "Threshold", 0.0, 50.0, 0.0, 0.5,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**🏆 Top N States to Show**")
top_n = st.sidebar.slider(
    "Top N", 5, 30, 15, 1,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Use the filters above to refine all charts and exports.")

# Fall back to all if user clears a filter accidentally
occs_to_use  = selected_occs  if selected_occs  else ALL_OCCS
races_to_use = selected_races if selected_races else ALL_RACES

df_f = df[
    (df['occupation'].isin(occs_to_use)) &
    (df['race'].isin(races_to_use)) &
    (df['percent'] >= min_pct)
].copy()

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
    </div>""", unsafe_allow_html=True)

kpi(k1, df_f['state'].nunique(),           "📍 Areas Found",        "#4f8bf9")
kpi(k2, df_f['occupation'].nunique(),      "💼 Occupations",        "#68D391")
kpi(k3, df_f['race'].nunique(),            "👥 Demographic Groups", "#F6AD55")
kpi(k4, len(df_f),                         "📊 Data Points",        "#B794F4")
kpi(k5, f"{df_f['percent'].mean():.1f}%", "📈 Avg Representation", "#FC8181")

st.markdown("<br>", unsafe_allow_html=True)

if df_f.empty:
    st.warning("⚠️ No data matches your filters. Try lowering the minimum % or selecting more groups.")
    st.stop()

tab1, tab2, tab3 = st.tabs([
    "📊  Dashboard",
    "🤖  AI Location Advisor",
    "📥  Export Report",
])

#
with tab1:
    st.markdown('<div class="section-header">📊 Geographic Distribution of Diverse STEM Talent</div>', unsafe_allow_html=True)

    col_bar, col_pie = st.columns([2, 1])

    df_state = (
        df_f.groupby('state')['percent']
        .mean().reset_index()
        .sort_values('percent', ascending=False)
        .head(top_n)
    )

    with col_bar:
        fig_bar = px.bar(
            df_state.sort_values('percent', ascending=True),
            x='percent', y='state', orientation='h',
            color='percent', color_continuous_scale='Teal',
            labels={'percent': 'Avg Representation %', 'state': ''},
            title=f'Top {top_n} Areas by Avg Diverse Representation %'
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0', coloraxis_showscale=False,
            margin=dict(l=10, r=20, t=40, b=10), height=440
        )
        fig_bar.update_xaxes(gridcolor='#2d3250', zerolinecolor='#2d3250')
        fig_bar.update_yaxes(gridcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_pie:
        df_pie = df_f.groupby('race')['percent'].mean().reset_index()
        fig_pie = px.pie(
            df_pie, names='race', values='percent',
            color='race', color_discrete_map=RACE_COLORS,
            title='Avg Representation by Demographic Group', hole=0.45
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            legend=dict(orientation='v', font=dict(size=10)),
            margin=dict(l=10, r=10, t=40, b=10), height=440
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    top_area = df_state.iloc[0]['state'] if not df_state.empty else "N/A"
    top_pct  = df_state.iloc[0]['percent'] if not df_state.empty else 0
    st.markdown(f"""
    <div class="insight-box">
        💡 <strong>Key Insight:</strong> <strong>{top_area}</strong> leads with
        <strong>{top_pct:.1f}%</strong> average diverse STEM representation,
        making it a strong candidate for satellite office placement.
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">🧩 Demographic Breakdown by Area</div>', unsafe_allow_html=True)

    top_states_list = df_state['state'].tolist()
    df_breakdown = df_f[df_f['state'].isin(top_states_list)]

    fig_group = px.bar(
        df_breakdown, x='state', y='percent', color='race', barmode='group',
        color_discrete_map=RACE_COLORS,
        labels={'percent': 'Representation %', 'state': 'Area', 'race': 'Demographic'},
        title=f'Demographic Breakdown — Top {top_n} Areas',
        hover_data={'occupation': True}
    )
    fig_group.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e8f0', xaxis_tickangle=-35,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=10, r=10, t=60, b=80), height=440
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
        df_heat, color_continuous_scale='Teal', aspect='auto',
        labels=dict(x='Area', y='Demographic Group', color='Representation %'),
        title=f'Representation % Heatmap (Top {top_n} Areas)'
    )
    fig_heat.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e8f0', xaxis_tickangle=-35,
        margin=dict(l=10, r=10, t=40, b=80), height=400
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">🎯 Opportunity Gap — Underutilized Talent by Area</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
        🎯 <strong>What is the Opportunity Gap?</strong>
        Areas where diverse groups have a presence but representation stays below 20%
        signal <strong>underutilized talent pools</strong> — ideal targets for satellite offices.
    </div>""", unsafe_allow_html=True)

    df_gap = (
        df_f[df_f['percent'].between(min_pct, 20)]
        .groupby(['state', 'race'])['percent']
        .mean().reset_index()
        .sort_values('percent', ascending=False)
        .rename(columns={'state': 'Area', 'race': 'Demographic', 'percent': 'Representation %'})
        .reset_index(drop=True)
    )
    df_gap['Opportunity Score'] = (20 - df_gap['Representation %']).round(1)
    df_gap['Representation %']  = df_gap['Representation %'].round(1)

    st.dataframe(
        df_gap.head(30), use_container_width=True, height=380,
        column_config={
            'Representation %': st.column_config.ProgressColumn(
                'Representation %', min_value=0, max_value=20, format='%.1f%%'
            ),
            'Opportunity Score': st.column_config.ProgressColumn(
                'Opportunity Score ↑', min_value=0, max_value=20, format='%.1f'
            ),
        }
    )

    with st.expander("📋 View Full Filtered Dataset"):
        st.dataframe(
            df_f.sort_values('percent', ascending=False).reset_index(drop=True),
            use_container_width=True, height=350
        )
        st.download_button(
            label="⬇️ Download Filtered Data as CSV",
            data=df_f.to_csv(index=False),
            file_name='filtered_stem_diversity.csv',
            mime='text/csv'
        )


# TAB 2 — AI LOCATION ADVISOR

with tab2:
    st.markdown('<div class="section-header">🤖 AI Natural Language Location Advisor</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
        <strong>Ask anything about STEM diversity by location.</strong>
        The AI has full access to representation data for all 50 states across every
        demographic group and STEM occupation. Ask strategic questions, request comparisons,
        or get ranked satellite office recommendations.
    </div>
    """, unsafe_allow_html=True)

    if client is None:
        st.error(
            "Groq API key not found.\n\n"
            "1. Sign up free at https://console.groq.com\n"
            "2. Create an API key\n"
            "3. Add to `.streamlit/secrets.toml`:\n\n"
            "```toml\nGROQ_API_KEY = 'gsk_...'\n```"
        )
    else:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if not st.session_state.messages:
            st.markdown("### 💡 Suggested Queries — click any to ask instantly")

            suggestions = [
                ("🏢 Best satellite office location",
                 "Where should we open a satellite office to maximize overall workforce diversity across all demographic groups?"),
                ("📍 Underutilized talent pools",
                 "Which states have the highest opportunity gap — diverse talent present but underrepresented below 15% in STEM roles?"),
                ("⚖️ Most balanced diversity",
                 "Which 5 states have the most balanced representation across all demographic groups simultaneously in STEM?"),
                ("📈 High growth regions",
                 "Which states in the South or Midwest are emerging as strong diverse STEM talent markets worth investing in?"),
                ("🔬 Engineering talent",
                 "Which states have the strongest overall diverse talent pipeline specifically for engineering occupations?"),
                ("💰 Cost vs diversity",
                 "Which states offer a good combination of diverse STEM talent and lower cost of living for a new office?"),
            ]

            col1, col2, col3 = st.columns(3)
            cols = [col1, col2, col3]
            for i, (label, query) in enumerate(suggestions):
                with cols[i % 3]:
                    st.markdown('<div class="suggest-btn">', unsafe_allow_html=True)
                    if st.button(label, key=f"sug_{i}", use_container_width=True):
                        st.session_state._prefill = query
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        prefill = st.session_state.pop("_prefill", "")
        prompt  = st.chat_input("Ask the AI advisor anything about STEM diversity by location...") or prefill

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing talent data..."):
                    api_messages = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + api_messages,
                        max_tokens=1024,
                        temperature=0.3,
                    )
                    reply = response.choices[0].message.content
                    st.markdown(reply)

            st.session_state.messages.append({"role": "assistant", "content": reply})

        if st.session_state.messages:
            if st.button("🗑️ Clear conversation", key="clear_chat"):
                st.session_state.messages = []
                st.rerun()

# TAB 3 — EXPORT REPORT
#
with tab3:
    st.markdown('<div class="section-header">📥 Export Report</div>', unsafe_allow_html=True)

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.markdown("#### Summary Statistics")
        summary = df_f.groupby(['state', 'race'])['percent'].agg(
            ['mean', 'max', 'min', 'count']
        ).round(2).reset_index()
        summary.columns = ['State', 'Demographic', 'Avg %', 'Max %', 'Min %', 'Records']
        summary = summary.sort_values('Avg %', ascending=False)
        st.dataframe(summary.head(40), use_container_width=True, height=380)
        st.download_button(
            label="⬇️ Download Summary CSV",
            data=summary.to_csv(index=False),
            file_name=f'stem_diversity_summary_{datetime.date.today()}.csv',
            mime='text/csv',
            use_container_width=True
        )

    with col_e2:
        st.markdown("#### Top 10 Opportunity States")
        df_opp = (
            df_f[df_f['percent'].between(min_pct, 20)]
            .groupby(['state', 'race'])['percent']
            .mean().reset_index()
        )
        df_opp['opportunity_score'] = (20 - df_opp['percent']).round(1)
        df_opp = df_opp.sort_values('opportunity_score', ascending=False).head(10)
        df_opp.columns = ['State', 'Demographic', 'Avg %', 'Opportunity Score']
        st.dataframe(
            df_opp, use_container_width=True, height=380,
            column_config={
                'Avg %': st.column_config.ProgressColumn(min_value=0, max_value=20, format='%.1f%%'),
                'Opportunity Score': st.column_config.ProgressColumn(min_value=0, max_value=20, format='%.1f'),
            }
        )
        st.download_button(
            label="⬇️ Download Opportunity Report CSV",
            data=df_opp.to_csv(index=False),
            file_name=f'opportunity_report_{datetime.date.today()}.csv',
            mime='text/csv',
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("#### Full Filtered Dataset")
    st.download_button(
        label="⬇️ Download Full Filtered Data as CSV",
        data=df_f.to_csv(index=False),
        file_name=f'filtered_stem_diversity_{datetime.date.today()}.csv',
        mime='text/csv',
        use_container_width=True
    )

    st.markdown("#### Generate Executive Summary")
    if st.button("🖨️ Generate Text Report", use_container_width=True):
        top5      = df_f.groupby('state')['percent'].mean().sort_values(ascending=False).head(5)
        top5_race = df_f.groupby('race')['percent'].mean().sort_values(ascending=False)
        lines = [
            "DIVERSE STEM TALENT FINDER — EXECUTIVE SUMMARY",
            f"Generated : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "Data Source: US Census ACS EEO 2018 5-Year Estimates",
            "=" * 60,
            "",
            "FILTER SETTINGS",
            f"  Occupations selected : {len(occs_to_use)}",
            f"  Demographic groups   : {', '.join(races_to_use)}",
            f"  Min representation % : {min_pct}%",
            "",
            "KEY METRICS",
            f"  States found       : {df_f['state'].nunique()}",
            f"  Avg representation : {df_f['percent'].mean():.1f}%",
            f"  Total data points  : {len(df_f):,}",
            "",
            "TOP 5 STATES BY AVG DIVERSE REPRESENTATION",
        ]
        for i, (state, pct) in enumerate(top5.items(), 1):
            lines.append(f"  {i}. {state}: {pct:.1f}%")
        lines += ["", "REPRESENTATION BY DEMOGRAPHIC GROUP"]
        for race, pct in top5_race.items():
            lines.append(f"  {race}: {pct:.1f}%")
        lines += ["", "=" * 60, "Team 4 — Diversity & Inclusion Officers"]
        report_text = "\n".join(lines)
        st.text_area("Executive Summary", report_text, height=350)
        st.download_button(
            label="⬇️ Download Text Report",
            data=report_text,
            file_name=f'executive_summary_{datetime.date.today()}.txt',
            mime='text/plain',
            use_container_width=True
        )

st.markdown("---")
st.markdown(
    "<center><small>Data: US Census ACS EEO 5-Year Estimates (2018) &nbsp;|&nbsp; "
    "Team 4 — Diversity & Inclusion Officers &nbsp;|&nbsp; HR Consultants for Tech Consortium</small></center>",
    unsafe_allow_html=True
)
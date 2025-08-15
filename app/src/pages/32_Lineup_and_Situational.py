import os
import logging
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
import plotly.express as px
from modules import api_client

logger = logging.getLogger(__name__)

api_client.ensure_api_base()


def call_get_raw(endpoint: str, params: dict | None = None, timeout=5):
    return api_client.api_get(endpoint, params=params, timeout=timeout)


def get_teams(timeout=5):
    data = api_client.api_get('/basketball/teams', timeout=timeout)
    if isinstance(data, dict) and 'teams' in data:
        teams = data.get('teams', []) or []
    elif isinstance(data, list):
        teams = data or []
    else:
        teams = []

    # deduplicate by team_id
    seen = set()
    unique = []
    for t in teams:
        tid = t.get('team_id') or t.get('id')
        if tid is None:
            unique.append(t)
            continue
        try:
            key = int(tid)
        except Exception:
            key = str(tid)
        if key in seen:
            continue
        seen.add(key)
        unique.append(t)
    return unique


def get_lineup_configurations(endpoint_or_query: str):
    try:
        path, params = api_client._parse_endpoint_with_query(endpoint_or_query)
    except Exception:
        # fallback implementation
        import urllib.parse
        parsed = urllib.parse.urlparse(endpoint_or_query)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        params = {k: v[0] for k, v in qs.items()}
    return call_get_raw(path or '/analytics/lineup-configurations', params)


def get_situational_performance(endpoint_or_query: str):
    try:
        path, params = api_client._parse_endpoint_with_query(endpoint_or_query)
    except Exception:
        import urllib.parse
        parsed = urllib.parse.urlparse(endpoint_or_query)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        params = {k: v[0] for k, v in qs.items()}
    return call_get_raw(path or '/analytics/situational-performance', params)

st.set_page_config(page_title='Lineup & Situational - Head Coach', layout='wide')
SideBarLinks()
st.title('Lineup & Situational Analysis — Head Coach')
st.caption('Analyze lineup effectiveness and situational performance.')

def make_request(endpoint, method='GET', data=None):
    if endpoint.startswith('/basketball/teams') and method == 'GET':
        teams = get_teams() or []
        return {'teams': teams}
    if endpoint.startswith('/analytics/lineup-configurations'):
        return get_lineup_configurations(endpoint) or {}
    if endpoint.startswith('/analytics/situational-performance'):
        return get_situational_performance(endpoint) or {}
    return {}

# Tabs for Lineup Analysis and Situational Performance
tab1, tab2 = st.tabs(['Lineup Analysis', 'Situational Performance'])

with tab1:
    st.header('Lineup Analysis')
    teams = make_request('/basketball/teams') or {}
    if teams and 'teams' in teams:
        team_names = [t.get('name') for t in teams.get('teams', []) if t.get('name')]
        sel = st.selectbox('Select a team to analyze lineups:', team_names)
        if st.button('Get Lineup Analysis'):
            team_id = next((t.get('team_id') for t in teams.get('teams', []) if t.get('name') == sel), None)
            data = make_request(f'/analytics/lineup-configurations?team_id={team_id}') or {}
            if not data or 'lineup_effectiveness' not in data:
                st.error('No lineup data available')
            else:
                df = pd.DataFrame(data['lineup_effectiveness'])
                # Ensure dataframe is not empty
                if df.empty:
                    st.error('Lineup data returned empty for this team.')
                else:
                    # Ensure there is a numeric plus_minus column. If missing, create with NaN so sorting and plotting won't raise KeyError.
                    if 'plus_minus' in df.columns:
                        df['plus_minus'] = pd.to_numeric(df['plus_minus'], errors='coerce')
                    else:
                        # create a placeholder column so downstream logic can run; values will be NaN which are handled by plotting and selection
                        df['plus_minus'] = pd.NA

                    # If all values are NaN, coerce to 0 for display purposes but keep track to warn user
                    if df['plus_minus'].isna().all():
                        st.warning('No plus/minus values available for these lineups. Showing available lineup labels instead.')
                        df['plus_minus'] = 0

                    # Now safe to sort by the column
                    df = df.sort_values(by='plus_minus', ascending=True)

                    fig = px.bar(df, x='plus_minus', y='lineup', orientation='h', color='plus_minus', color_continuous_scale=px.colors.sequential.RdBu)
                    st.plotly_chart(fig, use_container_width=True)

                    try:
                        top3 = df.nlargest(3, 'plus_minus')
                        st.subheader('Top Rotation Suggestions')
                        for idx, row in top3.iterrows():
                            if row['plus_minus'] >= 5:
                                st.success(f"Keep: {row['lineup']} (+{row['plus_minus']:.1f})")
                            elif row['plus_minus'] >= 2:
                                st.info(f"Consider: {row['lineup']} (+{row['plus_minus']:.1f})")
                            else:
                                st.warning(f"Review: {row['lineup']} ({row['plus_minus']:.1f})")

                        st.markdown('''
                            <div style="padding:10px;border-radius:8px;border:1px solid #eee;background:#f9fafb">
                            Suggested rotation change: focus on starting lineup minutes for players in the top rotation during 4th quarter close moments.
                            </div>
                        ''', unsafe_allow_html=True)
                    except Exception:
                        pass

                    with st.expander('View Raw Data'):
                        st.table(df)

with tab2:
    st.header('Situational Performance')
    teams = make_request('/basketball/teams') or {}
    if teams and 'teams' in teams:
        team_names = [t.get('name') for t in teams.get('teams', []) if t.get('name')]
        sel = st.selectbox('Select team:', team_names, key='situ_team')
        team_id = next((t.get('team_id') for t in teams.get('teams', []) if t.get('name') == sel), None)

        if st.button('Load Situational Data'):
            data = make_request(f'/analytics/situational-performance?team_id={team_id}') or {}
            if data and 'situational' in data:
                situ = data['situational']
                if situ.get('clutch'):
                    st.subheader('Clutch Performance')
                    st.metric('Off Rating', situ['clutch']['off_rating'])
                    st.metric('Def Rating', situ['clutch']['def_rating'])
                    st.metric('Net Rating', situ['clutch']['net_rating'])
                    st.write(f"Games in sample: {situ['clutch']['games']}")

                if situ.get('by_quarter'):
                    st.subheader('Quarter-by-Quarter')
                    dfq = pd.DataFrame(situ['by_quarter'])
                    fig = px.bar(dfq, x='quarter', y=['avg_points_for','avg_points_against'], barmode='group', title='Avg Points by Quarter')
                    st.plotly_chart(fig, use_container_width=True)

                if situ.get('close_games'):
                    st.subheader('Close Games')
                    st.table(pd.DataFrame(situ['close_games']))

                # Suggestions
                st.subheader('Practice Focus Recommendations')
                recs = []
                if situ.get('clutch') and situ['clutch']['net_rating'] < 0:
                    recs.append('Work on late-game execution and ball security in close scenarios.')
                if situ.get('by_quarter'):
                    dfq = pd.DataFrame(situ['by_quarter'])
                    try:
                        worst_q = dfq.loc[dfq['avg_points_for'].astype(float).idxmin()]['quarter']
                        recs.append(f'Improve offense in Q{int(worst_q)}')
                    except Exception:
                        pass

                if recs:
                    for r in recs:
                        st.info(r)
                else:
                    st.write('No practice focus recommendations available for selected team.')

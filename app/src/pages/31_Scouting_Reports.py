import os
import logging
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
import plotly.graph_objects as go
from modules import api_client
import urllib.parse
from typing import Any, Dict

logger = logging.getLogger(__name__)

api_client.ensure_api_base()

def call_get_raw(endpoint: str, params: dict | None = None, timeout=5):
    return api_client.api_get(endpoint, params=params, timeout=timeout)


def call_post_raw(endpoint: str, data: dict | None = None, timeout=5):
    return api_client.api_post(endpoint, data=data, timeout=timeout)


def call_put_raw(endpoint: str, data: dict | None = None, timeout=5):
    return api_client.api_put(endpoint, data=data, timeout=timeout)


def get_teams(timeout=5):
    data = api_client.api_get('/basketball/teams', timeout=timeout)
    if isinstance(data, dict) and 'teams' in data:
        return data.get('teams', [])
    if isinstance(data, list):
        return data
    return []

def get_opponent_report(endpoint_or_query: str):
    try:
        path, params = api_client._parse_endpoint_with_query(endpoint_or_query)
    except Exception:
        parsed = urllib.parse.urlparse(endpoint_or_query)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        params = {k: v[0] for k, v in qs.items()}
    return call_get_raw(path or '/analytics/opponent-reports', params)


def create_game_plan(data: Dict[str, Any]):
    return call_post_raw('/strategy/game-plans', data)


def get_game_plans_from_query(endpoint_or_query: str):
    try:
        path, params = api_client._parse_endpoint_with_query(endpoint_or_query)
    except Exception:
        parsed = urllib.parse.urlparse(endpoint_or_query)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        params = {k: v[0] for k, v in qs.items()}
    return call_get_raw(path or '/strategy/game-plans', params)


def update_game_plan(plan_id: Any, data: Dict[str, Any]):
    return call_put_raw(f'/strategy/game-plans/{plan_id}', data)

st.set_page_config(page_title='Scouting & Game Planner - Head Coach', layout='wide')
SideBarLinks()
st.title('Scouting & Game Planning — Head Coach')
st.caption('Create opponent scouting reports and manage game plans.')

def make_request(endpoint, method='GET', data=None):
    # Minimal wrapper to keep existing call sites working; delegates to api_client
    if endpoint.startswith('/basketball/teams') and method == 'GET':
        return {'teams': get_teams()}
    if endpoint.startswith('/analytics/opponent-reports') and method == 'GET':
        # expected query params in endpoint string
        # delegate to analytics route via api_client
        # parse params naively
        return get_opponent_report(endpoint)
    if endpoint.startswith('/strategy/game-plans'):
        if method == 'POST':
            return create_game_plan(data)
        if method == 'GET':
            return get_game_plans_from_query(endpoint)
        if method == 'PUT':
            # expects endpoint like /strategy/game-plans/{id}
            parts = endpoint.rstrip('/').split('/')
            plan_id = parts[-1]
            return update_game_plan(plan_id, data)
    return None


# Load teams once and reuse for both tabs
teams_data = make_request('/basketball/teams') or {}
team_names = []
team_map = {}
if isinstance(teams_data, dict) and 'teams' in teams_data and teams_data['teams']:
    team_names = [t.get('name') for t in teams_data.get('teams', []) if t.get('name')]
    team_map = {t.get('name'): t.get('team_id') for t in teams_data.get('teams', [])}
else:
    st.error('Teams data unavailable from API. Some features will be limited.')


# Restore tabs layout (user preferred) and visible team selectors
tab1, tab2 = st.tabs(['Scouting Report', 'Game Planner'])

with tab1:
    st.header('Opponent Scouting')

    if not team_names:
        st.warning('Teams list unavailable — cannot run scouting.')
    else:
        # If logged-in user with team in session, use that as focal team and don't show selector
        focal_team = None
        try:
            role = st.session_state.get('role')
            team_name_session = st.session_state.get('team_name')
            if role in ('head_coach', 'general_manager') and team_name_session:
                focal_team = team_name_session
                # intentionally do not display the team on this page (shown on Head Coach Home page)
            else:
                focal_team = None
                st.warning('Team context not set. Please set your team on the Head Coach Home page to enable scouting.')
        except Exception:
            focal_team = None
            st.warning('Team context not set. Please set your team on the Head Coach Home page to enable scouting.')

        # Only allow selecting an opponent if a focal team is available
        if focal_team:
            opponent_options = [n for n in team_names if n != focal_team]
            if opponent_options:
                opponent = st.selectbox('Opponent to scout', opponent_options)
            else:
                opponent = None

            if st.button('Get Scouting Report'):
                if not focal_team or not opponent:
                    st.error('Please ensure your team context is set and an opponent is selected.')
                else:
                    your_id = team_map.get(focal_team)
                    opp_id = team_map.get(opponent)
                    if your_id is None or opp_id is None:
                        st.error('Failed to resolve team ids')
                    else:
                        report = make_request(f'/analytics/opponent-reports?team_id={your_id}&opponent_id={opp_id}') or {}

                        if report:
                            st.subheader(f"Scouting Report — {opponent}")

                            perf = report.get('recent_performance') or {}
                            avg_scored = perf.get('avg_points_scored', 0)
                            avg_allowed = perf.get('avg_points_allowed', 0)

                            c1, c2 = st.columns(2)
                            c1.metric('Avg. Points Scored', f"{float(avg_scored):.1f}")
                            c2.metric('Avg. Points Allowed', f"{float(avg_allowed):.1f}")

                            # Key players
                            if report.get('key_players'):
                                st.subheader('Key Players')
                                players_df = pd.DataFrame(report['key_players'])
                                cols = st.columns(min(len(players_df), 4))
                                for i, p in players_df.iterrows():
                                    with cols[i % len(cols)]:
                                        st.info(f"**{p['first_name']} {p['last_name']}** ({p.get('position','')})")
                                        try:
                                            st.metric('PPG', f"{float(p.get('avg_points',0)):.1f}")
                                        except Exception:
                                            pass

                            # Tactical Snapshot
                            shooting = report.get('shooting_patterns')
                            weaknesses = report.get('defensive_weaknesses')
                            recs = report.get('tactical_recommendations') or []

                            if shooting or weaknesses or recs:
                                st.subheader('Tactical Snapshot')
                                sc1, sc2, sc3 = st.columns([1,1,2])
                                with sc1:
                                    if shooting:
                                        st.metric('FG %', f"{shooting.get('fg_pct',0)*100:.1f}%")
                                        st.metric('3P %', f"{shooting.get('three_pt_pct',0)*100:.1f}%")
                                    else:
                                        st.write('Shooting patterns: N/A')
                                with sc2:
                                    if shooting:
                                        st.metric('2P %', f"{shooting.get('two_pt_pct',0)*100:.1f}%")
                                        st.metric('FT %', f"{shooting.get('ft_pct',0)*100:.1f}%")
                                with sc3:
                                    if weaknesses:
                                        st.markdown('**Defensive Weaknesses**')
                                        for w in weaknesses:
                                            st.warning(w)
                                    else:
                                        st.write('No clear defensive weaknesses from available data.')

                                if recs:
                                    st.markdown('**Top Tactical Recommendations**')
                                    for r in recs:
                                        st.success(r)
                                        
                                # REMOVED: "Mark recommendations for practice" button and functionality
                                # This feature has been removed as requested

                        with st.expander('View Raw Report'):
                            st.json(report)

with tab2:
    st.header('Game Planner (Create & Manage)')

    st.write('Create game plans using team names instead of numeric ids.')

    if not team_names:
        st.warning('Teams list unavailable — Game Planner disabled.')
    else:
        # If logged-in coach/GM with session team, use that and show as text instead of selectbox
        try:
            role = st.session_state.get('role')
            team_name_session = st.session_state.get('team_name')
            if role in ('head_coach', 'general_manager') and team_name_session:
                gp_team = team_name_session
                # intentionally do not display the team on this page (shown on Head Coach Home page)
            else:
                gp_team = None
                st.warning('Team context not set. Please set your team on the Head Coach Home page to create game plans.')
        except Exception:
            gp_team = None
            st.warning('Team context not set. Please set your team on the Head Coach Home page to create game plans.')

        # Only render game planner inputs if team context exists
        if gp_team:
            # Opponent must be selected for game plans (no '(none)' option)
            gp_opp_options = [n for n in team_names if n != gp_team]
            gp_opp = st.selectbox('Select Opponent', gp_opp_options)

            plan_name = st.text_input('Plan Name')
            off_strategy = st.text_area('Offensive Strategy')
            def_strategy = st.text_area('Defensive Strategy')
            key_matchups = st.text_area('Key Matchups')
            special_instructions = st.text_area('Special Instructions')

            if st.button('Create Game Plan'):
                if not plan_name:
                    st.error('Please provide a plan name')
                elif not gp_opp:
                    st.error('Please select an opponent (required)')
                else:
                    payload = {
                        'team_id': int(team_map.get(gp_team)),
                        'opponent_id': int(team_map.get(gp_opp)),
                        'plan_name': plan_name,
                        'offensive_strategy': off_strategy,
                        'defensive_strategy': def_strategy,
                        'key_matchups': key_matchups,
                        'special_instructions': special_instructions,
                        'status': 'draft'
                    }
                    res = make_request('/strategy/game-plans', method='POST', data=payload)
                    if res:
                        st.success(f"Created Game Plan: {res.get('plan_name')}")

            if st.button('Load Plans for Team'):
                team_id = team_map.get(gp_team)
                if not team_id:
                    st.error('Could not resolve selected team to an id')
                else:
                    plans = make_request(f'/strategy/game-plans?team_id={team_id}')
                    # If backend returned None or failed, surface raw response for debugging
                    if not plans:
                        try:
                            import requests as _req
                            base = api_client.ensure_api_base()
                            raw = _req.get(f"{base}/strategy/game-plans?team_id={team_id}")
                            
                            st.error(f"Failed to load plans — status {raw.status_code}")
                            with st.expander('Raw server response'):
                                st.text(raw.text)
                        except Exception as e:
                            st.error(f'Failed to fetch plans and could not retrieve raw response: {e}')
                    else:
                        if 'game_plans' in plans:
                            for gp in plans['game_plans']:
                                st.subheader(gp.get('plan_name'))
                                st.write('Status:', gp.get('status'))
                                st.write('Offense:', gp.get('offensive_strategy'))
                                st.write('Defense:', gp.get('defensive_strategy'))
                                st.write('Key matchups:', gp.get('key_matchups'))
                                if st.button(f"Activate {gp.get('plan_id')}", key=f"activate_{gp.get('plan_id')}"):
                                    gp_payload = {'status': 'active'}
                                    upd = make_request(f"/strategy/game-plans/{gp.get('plan_id')}", method='PUT', data=gp_payload)
                                    if upd:
                                        st.success('Plan activated')
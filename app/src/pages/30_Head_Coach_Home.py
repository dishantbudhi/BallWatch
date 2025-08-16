import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
import os

def _default_api_base():
    import os
    for key in ("API_BASE_URL", "API_BASE"):
        v = os.getenv(key)
        if v:
            return v
    if os.path.exists('/.dockerenv'):
        return 'http://api:4000'
    return 'http://localhost:4000'

API_BASE = _default_api_base()


def login(username, timeout=5):
    """Perform demo login by username; returns user object or None."""
    try:
        resp = requests.post(f"{API_BASE}/auth/login", json={'username': username}, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('user') if isinstance(data, dict) else None
        else:
            logger.warning('login returned status %s for username %s (%s)', resp.status_code, username, getattr(resp, 'text', None))
    except Exception as e:
        logger.exception('Exception in login(%s): %s', username, e)
    return None


def get_teams(timeout=5):
    """Return list of teams from the backend API."""
    try:
        resp = requests.get(f"{API_BASE}/basketball/teams", timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('teams', []) if isinstance(data, dict) else []
        else:
            logger.warning('get_teams returned status %s (%s)', resp.status_code, getattr(resp, 'text', None))
    except Exception as e:
        logger.exception('Exception in get_teams: %s', e)
    return []

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome Head Coach, {st.session_state.get('first_name', 'Guest')}.")

# If this user is a head coach, fetch their user row and show the assigned team (if any)
try:
    uid = st.session_state.get('user_id')
    role_raw = st.session_state.get('role') or ''
    role = str(role_raw).lower()
    # permissive head coach detection
    norm_role = role.replace('-', '_').replace(' ', '_')
    is_head_coach = ('head' in norm_role and 'coach' in norm_role) or norm_role in ('head_coach', 'head coach', 'coach')

    if is_head_coach and uid:
        # Minimal route calls: get user, then get team name if team_id present
        try:
            user = login(st.session_state.get('username'))
            if user and isinstance(user, dict):
                # normalize team_id to int when possible
                team_val = user.get('team_id')
                try:
                    st.session_state['team_id'] = int(team_val) if team_val is not None else None
                except Exception:
                    st.session_state['team_id'] = team_val
        except Exception:
            st.session_state['team_id'] = st.session_state.get('team_id')

        # Resolve team name via single team endpoint if team_id exists
        team_id = st.session_state.get('team_id')
        if team_id:
            try:
                teams = get_teams()
                id_to_name = {}
                for t in teams:
                    tid = t.get('team_id')
                    name = t.get('name')
                    if tid is None:
                        continue
                    try:
                        id_to_name[int(tid)] = name
                    except Exception:
                        id_to_name[tid] = name
                    id_to_name[str(tid)] = name

                st.session_state['team_name'] = id_to_name.get(team_id) or id_to_name.get(str(team_id))
            except Exception:
                pass

    # Always show team info for head coach below welcome
    # Only show team info when the current session is authenticated as a head coach
    if is_head_coach and st.session_state.get('authenticated', False):
        team_name = st.session_state.get('team_name')
        if team_name:
            st.markdown(f"**Team: {team_name}**")
        else:
            st.markdown('**Team: Not assigned**')
except Exception:
    pass

st.write('')
st.write('### What would you like to do today?')

st.markdown('''
<style>
.card {
  border: 1px solid #E6E6E6;
  border-radius: 12px;
  padding: 16px;
  background: linear-gradient(180deg, #ffffff 0%, #fffaf0 100%);
  box-shadow: 0 6px 18px rgba(16,24,40,0.06);
  min-height: 150px;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
}
.card-header { display:flex; align-items:center; gap:8px; }
.card-title { font-weight:700; font-size:18px; margin:0; }
.card-desc { color:#475569; margin-top:8px; margin-bottom:12px; }
</style>
''', unsafe_allow_html=True)

cards = [
    {'title': 'Scouting & Game Planning', 'desc': 'Opponent scouting, tactical recommendations, and game plan creation.', 'page': 'pages/31_Scouting_Reports.py', 'emoji': '📝', 'color': '#0369A1'},
    {'title': 'Lineup & Situational', 'desc': 'Lineup effectiveness, quarter-by-quarter and clutch performance insights.', 'page': 'pages/32_Lineup_and_Situational.py', 'emoji': '🧩', 'color': '#7C3AED'},
    {'title': 'Player Matchup', 'desc': 'Head-to-head player comparisons, advantage indicators and tactical assignments.', 'page': 'pages/33_Player_Matchup.py', 'emoji': '⚔️', 'color': '#F97316'}
]

cols = st.columns(len(cards))
for i, card in enumerate(cards):
    with cols[i]:
        st.markdown(f"""
        <div class='card' style='border-top:4px solid {card['color']}'>
          <div class='card-header'>
            <div class='card-emoji'>{card['emoji']}</div>
            <div>
              <div class='card-title'>{card['title']}</div>
              <div class='card-desc'>{card['desc']}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        # spacer between card and button
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if st.button(f"Open {card['title']}", key=f"hc_open_{i}"):
            st.switch_page(card['page'])

"""Head Coach landing page with quick access to coaching tools."""

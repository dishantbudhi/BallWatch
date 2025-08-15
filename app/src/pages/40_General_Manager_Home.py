import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
import os

# Resolve API base in the same way as the main Home module so the app
# works both inside Docker (service DNS) and locally.
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

st.title(f"Welcome General Manager, {st.session_state.get('first_name', 'Guest')}.")
st.write('')

# Replicate Head Coach behavior minimally: resolve and show team name for GM if available
try:
    uid = st.session_state.get('user_id')
    role_raw = st.session_state.get('role') or ''
    role = str(role_raw).lower()
    is_gm = 'general' in role or 'manager' in role or role in ('general_manager', 'gm')

    if is_gm and uid:
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

    # Only show team info when the current session is authenticated as a GM
    if is_gm and st.session_state.get('authenticated', False):
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
  background: linear-gradient(180deg, #ffffff 0%, #fbfbff 100%);
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
    {'title': 'Player Progress', 'desc': 'Track development and performance trajectories for players.', 'page': 'pages/41_Player_Progress.py', 'emoji': '📈', 'color': '#7C3AED'},
    {'title': 'Draft Rankings', 'desc': 'View and adjust draft rankings and prospect analyses.', 'page': 'pages/42_Draft_Rankings.py', 'emoji': '🧾', 'color': '#F97316'},
    {'title': 'Contract Efficiency', 'desc': 'Model contract decisions and roster salary impacts.', 'page': 'pages/43_Contract_Efficiency.py', 'emoji': '💼', 'color': '#059669'}
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
        if st.button(f"Open {card['title']}", key=f"gm_open_{i}"):
            st.switch_page(card['page'])
##################################################
# This is the main/entry-point file for the 
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks
import time
import requests
import os
import urllib.parse
from typing import Optional, Dict, Any, Tuple
from modules.api_client import get_users, get_teams as api_get_teams, assign_team as api_assign_team


# Inline API base and minimal helpers (ported from modules/api_client.py)
def _default_api_base():
    """Determine a sensible default API base URL.

    Priority:
      1) Respect environment variables API_BASE_URL or API_BASE
      2) If running inside a container (/.dockerenv) prefer the compose service hostname 'api:4000'
      3) Fall back to localhost for local development
    """
    env = os.getenv('API_BASE_URL') or os.getenv('API_BASE')
    if env:
        return env

    try:
        # In Docker there's often a /.dockerenv file; prefer the service DNS name
        if os.path.exists('/.dockerenv'):
            return 'http://api:4000'
    except Exception:
        pass

    # default for non-container/local dev
    return 'http://localhost:4000'

API_BASE = _default_api_base()
logger.info('Using API_BASE=%s', API_BASE)


def _parse_endpoint_with_query(endpoint: str) -> Tuple[str, Dict[str, Any]]:
    """Split an endpoint that may include a query string into path and params dict."""
    if not endpoint:
        return endpoint, {}
    parsed = urllib.parse.urlparse(endpoint)
    path = parsed.path
    qs = urllib.parse.parse_qs(parsed.query)
    # flatten values (take first)
    params = {k: v[0] for k, v in qs.items()}
    return path, params


def call_get_raw(endpoint: str, params: Optional[Dict[str, Any]] = None, timeout=5):
    """Generic GET wrapper returning parsed JSON or None."""
    try:
        path, p = _parse_endpoint_with_query(endpoint)
        merged = {**(p or {}), **(params or {})}
        resp = requests.get(f"{API_BASE}{path}", params=merged or None, timeout=timeout)
        if resp.status_code in (200, 201):
            return resp.json()
        logger.info('GET %s returned %s', path, resp.status_code)
    except Exception as e:
        logger.exception('Exception in call_get_raw(%s): %s', endpoint, e)
    return None


def get_users_for_role(role, timeout=5):
    """Return a list of users for the given role by calling the backend API.

    Uses centralized api_client.get_users to ensure consistent request behavior.
    """
    try:
        alias_map = {
            'superfan': 'fan',
            'data_engineer': 'admin',
            'head_coach': 'coach',
            'general_manager': 'gm',
        }

        def _extract_users_from_json(data):
            if not data:
                return None
            # if data is a dict wrapper like {'users': [...]}
            if isinstance(data, dict):
                # try common keys
                for key in ('users', 'results', 'items', 'records', 'data'):
                    val = None
                    # case-insensitive access
                    for k, v in data.items():
                        if k.lower() == key:
                            val = v
                            break
                    if val is not None:
                        if isinstance(val, list) and all(isinstance(i, dict) for i in val):
                            return val
                        if isinstance(val, dict):
                            # nested dict might contain the list
                            for nk, nv in val.items():
                                if nk.lower() in ('users', 'results', 'items') and isinstance(nv, list) and all(isinstance(i, dict) for i in nv):
                                    return nv
                # scan values
                for v in data.values():
                    if isinstance(v, list) and all(isinstance(i, dict) for i in v):
                        return v
                    if isinstance(v, dict):
                        for vv in v.values():
                            if isinstance(vv, list) and all(isinstance(i, dict) for i in vv):
                                return vv
                # id->user map
                dict_vals = [v for v in data.values() if isinstance(v, dict)]
                if dict_vals and all(('username' in v or 'user_id' in v or 'id' in v) for v in dict_vals):
                    return dict_vals
                return None
            elif isinstance(data, list):
                if all(isinstance(i, dict) for i in data):
                    return data
            return None

        candidates = [role]
        if role in alias_map:
            candidates.append(alias_map[role])
        if '_' in role:
            candidates.append(role.replace('_', ' '))

        tried = set()
        for c in candidates:
            if not c or c in tried:
                continue
            tried.add(c)
            try:
                data = get_users(role=c, timeout=timeout)
                if data is None:
                    logger.debug('api_client.get_users returned None for role=%s', c)
                    continue
                users = _extract_users_from_json(data)
                if users:
                    return users
                else:
                    logger.debug('get_users_for_role: unexpected JSON shape for role=%s; raw=%s', c, type(data))
            except Exception:
                logger.exception('Exception while fetching users for role %s', c)

        # Final fallback: fetch all users and filter client-side
        try:
            data = get_users(timeout=timeout)
            if not data:
                return []
            users = _extract_users_from_json(data) or []
            if users:
                acceptable = {role}
                if role in alias_map:
                    acceptable.add(alias_map[role])
                acceptable = {v.lower() for v in acceptable if v}
                filtered = [u for u in users if (u.get('role') or '').lower() in acceptable]
                return filtered
        except Exception:
            logger.exception('Exception while fetching all users for fallback')

    except Exception as e:
        logger.exception('Exception in get_users_for_role(%s): %s', role, e)
    logger.info('get_users_for_role returned no users for role %s', role)
    return []


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


def assign_team(user_id, team_id, timeout=5):
    """Assign a team to a user via the auth API; returns the updated user object on success or None."""
    try:
        resp = requests.put(f"{API_BASE}/auth/users/{user_id}/assign-team", json={'team_id': team_id}, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('user') if isinstance(data, dict) else None
        else:
            logger.warning('assign_team returned status %s: %s', resp.status_code, getattr(resp, 'text', None))
    except Exception as e:
        logger.exception('Exception in assign_team: %s', e)
    return None


def _safe_rerun():
    """Rerun the Streamlit app in a way that's compatible across Streamlit versions.

    Strategy:
    1. Prefer st.experimental_rerun() when available (immediate rerun).
    2. Then try assigning to st.query_params (public API) which triggers a rerun.
    3. As a last resort, mutate session_state and call st.stop() to end this run; the state change will persist.
    """
    # 1) immediate preferred API
    try:
        if hasattr(st, 'experimental_rerun'):
            return st.experimental_rerun()
    except Exception:
        pass

    # 2) try updating query params (public API) - this normally triggers a rerun
    try:
        st.query_params = {"_refresh": int(time.time())}
        return
    except Exception:
        pass

    # 3) fallback: mutate session_state and stop (ensures state is set; user can refresh)
    try:
        st.session_state['_refresh'] = int(time.time())
        try:
            # stop this run so Streamlit can begin a new one
            st.stop()
        except Exception:
            pass
        return
    except Exception:
        # nothing left we can do
        try:
            st.stop()
        except Exception:
            pass

# streamlit supports reguarl and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout = 'wide')

# If a user is at this page, we assume they are not 
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false. 
# Only set the default if the key is missing so we don't clobber a login.
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Enable debug_mode by default to help surface raw API responses when troubleshooting
# (change to False in production or remove once debugging is complete)
if 'debug_mode' not in st.session_state:
    st.session_state['debug_mode'] = True

# show a small debug banner when enabled so the page renders and it's obvious
try:
    if st.session_state.get('debug_mode'):
        st.info('Debug mode: ON — API responses will be shown for troubleshooting')
except Exception:
    pass

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel. 
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# Page title
st.title('BallWatch: Basketball Analytics')

# ***************************************************
#    The major content of this page
# ***************************************************

# Add minimal CSS for the home page to style persona cards
st.markdown('''
<style>
.home-grid { display:flex; gap:20px; flex-wrap:wrap; }
.persona-card {
  flex: 1 1 calc(50% - 20px);
  min-width: 280px;
  border-radius: 12px;
  border: 1px solid #E6E6E6;
  padding: 16px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfbff 100%);
  box-shadow: 0 8px 26px rgba(16,24,40,0.06);
  display:flex;
  flex-direction:column;
  justify-content:space-between;
}
.persona-header { display:flex; align-items:center; gap:12px; }
.persona-emoji { font-size:28px; }
.persona-title { font-size:20px; font-weight:700; margin:0; }
.persona-bio { color:#475569; margin-top:8px; margin-bottom:12px; }
.persona-footer { display:flex; gap:10px, align-items:center; }
.persona-select { flex:1; }
.login-btn { }
@media (max-width:800px) {
  .persona-card { flex: 1 1 100%; }
}
</style>
''', unsafe_allow_html=True)

# Small mapping for persona visual accents
_persona_accents = {
    'Superfan': {'emoji': '🏀', 'color': '#7C3AED'},
    'Data Engineer': {'emoji': '🛠️', 'color': '#059669'},
    'Head Coach': {'emoji': '🎯', 'color': '#0369A1'},
    'General Manager': {'emoji': '🏢', 'color': '#F97316'},
}

# Create persona definitions (IDs added, no hard-coded user names)
user_options = {
    "Superfan": {
        "persona_id": "p_superfan",
        "role": "superfan",
        "page": "pages/10_Superfan_Home.py",
        "bio": "A passionate basketball enthusiast who craves deeper insights beyond mainstream sports media. Frustrated by surface-level analysis and generic commentary, this user seeks advanced metrics and data-driven perspectives to truly understand player performance and team dynamics. As someone who enjoys sports betting, they constantly struggle to find reliable analytical edges that go beyond basic stats and gut feelings."
    },
    "Data Engineer": {
        "persona_id": "p_data_engineer",
        "role": "data_engineer",
        "page": "pages/20_Data_Engineer_Home.py",
        "bio": "An experienced data professional specializing in real-time sports analytics infrastructure. Daily challenges include maintaining data accuracy across multiple live feeds, managing pipeline failures during critical game moments, and scaling systems to handle increasing data volumes. Often pressured to deliver clean, reliable datasets while troubleshooting complex ingestion issues and optimizing query performance for time-sensitive analytics requests."
    },
    "Head Coach": {
        "persona_id": "p_head_coach",
        "role": "head_coach",
        "page": "pages/30_Head_Coach_Home.py",
        "bio": "A team leader who needs actionable insights to make strategic decisions quickly. Overwhelmed by dense statistical reports and complex spreadsheets that are difficult to interpret during game preparation and halftime adjustments. Struggles to translate analytical findings into clear, confident communication with players while making split-second tactical decisions backed by reliable data rather than intuition alone."
    },
    "General Manager": {
        "persona_id": "p_general_manager",
        "role": "general_manager",
        "page": "pages/40_General_Manager_Home.py",
        "bio": "A front office executive tasked with rebuilding a struggling franchise through data-driven decision making. Faces pressure to identify undervalued talent, optimize roster construction, and justify expensive trades or signings to ownership. Challenged by fragmented analytics tools, inconsistent reporting formats, and the need to balance advanced metrics with traditional scouting insights when making high-stakes personnel decisions."
    }
}


# Helper: format a display label for a user
def _format_user_label(u):
    uid = u.get('user_id') or u.get('id')
    username = (u.get('username') or '').strip()
    first = (u.get('first_name') or '').strip()
    last = (u.get('last_name') or '').strip()

    if first and last:
        display_name = f"{first.title()} {last.title()}"
    elif first:
        display_name = first.title()
    else:
        display_name = username.replace('_', ' ').replace('.', ' ').title()

    return f"{display_name} — {username} (id:{uid})"


# Helper: set session state and navigate after a successful login
def _complete_login(chosen, selected_label, opts):
    try:
        st.session_state['authenticated'] = True
        st.session_state['role'] = opts['role']
        st.session_state['user_id'] = chosen.get('user_id') or chosen.get('id')
        st.session_state['username'] = chosen.get('username')
        st.session_state['first_name'] = chosen.get('first_name') or (selected_label.split(' — ')[0] if selected_label else '')
        # set team_id in session if present on user object
        try:
            team_val = chosen.get('team_id')
            if team_val is None:
                st.session_state['team_id'] = None
            else:
                try:
                    st.session_state['team_id'] = int(team_val)
                except Exception:
                    st.session_state['team_id'] = team_val
        except Exception:
            st.session_state['team_id'] = None

        # If a team_id is present, try to resolve and store team_name in session
        try:
            team_id = st.session_state.get('team_id')
            if team_id:
                teams = get_teams()
                id_to_name = {}
                for t in teams:
                    tid = t.get('team_id') or t.get('id')
                    name = t.get('name')
                    if tid is None:
                        continue
                    try:
                        id_to_name[int(tid)] = name
                    except Exception:
                        id_to_name[tid] = name
                    try:
                        id_to_name[str(tid)] = name
                    except Exception:
                        pass

                st.session_state['team_name'] = id_to_name.get(team_id) or id_to_name.get(str(team_id))
            else:
                st.session_state['team_name'] = None
        except Exception:
            st.session_state['team_name'] = None

        # If head coach or general manager and no team assigned, prompt to save team
        try:
            user_team = st.session_state.get('team_id')
            if opts['role'] in ('head_coach', 'general_manager') and not user_team:
                try:
                    teams = get_teams()
                    team_map = {t['name']: t['team_id'] for t in teams if 'name' in t and 'team_id' in t}
                    team_names = [t['name'] for t in teams if 'name' in t]
                except Exception:
                    teams = []
                    team_map = {}
                    team_names = []

                if teams:
                    st.info('Please select your primary team for this account (you can change it later).')
                    chosen_team = st.selectbox('Select your team', team_names, key=f'choose_team_{opts["role"]}')
                    if st.button('Save team assignment', key=f'save_team_{opts["role"]}'):
                        sel_id = team_map.get(chosen_team)
                        try:
                            user_id = st.session_state.get('user_id')
                            updated = assign_team(user_id, sel_id)
                            if updated:
                                st.success('Team assigned successfully. Continuing to your dashboard...')
                                try:
                                    st.session_state['team_id'] = int(sel_id) if sel_id is not None else None
                                except Exception:
                                    st.session_state['team_id'] = sel_id
                                st.session_state['team_name'] = chosen_team
                            else:
                                st.error('Failed to assign team')
                        except Exception as e:
                            st.error(f'Failed to assign team: {e}')
        except Exception:
            pass

        try:
            if hasattr(st, 'switch_page'):
                st.switch_page(opts.get('page'))
        except Exception:
            _safe_rerun()
        else:
            _safe_rerun()

    except Exception as e:
        logger.exception('Exception in _complete_login: %s', e)

# Helper: try to fetch users for a role from backend; do NOT use any fallback demo data
def fetch_users_for_role(role):
    """Fetch users for a role and provide extra debug logging when no users are returned.

    This wraps get_users_for_role so we can log the raw API response (via api_client.get_users)
    when the normalized result is empty. If Streamlit session_state contains 'debug_mode'
    the raw response will also be shown in the UI to aid troubleshooting.
    """
    users = get_users_for_role(role)
    if users:
        return users

    # no users found — capture more information from the underlying API for debugging
    try:
        logger.info('No users returned for role=%s from get_users_for_role; fetching raw api response...', role)
        raw = get_users(role=role, timeout=5)
        logger.info('Raw get_users response for role=%s: %s', role, raw)
        # If developer enabled debug_mode in session_state, surface the raw response in the UI
        if st.session_state.get('debug_mode'):
            try:
                st.error(f"Debug: get_users raw response for role={role}: {raw}")
            except Exception:
                # avoid raising during UI rendering
                pass
    except Exception as e:
        logger.exception('Exception while fetching raw users for role %s: %s', role, e)

    return []

# Consolidated persona renderer
def _render_persona(title, opts):
    accent = _persona_accents.get(title, {'emoji': '👤', 'color': '#6B7280'})

    # Header and bio
    st.markdown(f"### {accent['emoji']}  {title}")
    st.write(opts['bio'])

    # Fetch role-specific users
    role_users = fetch_users_for_role(opts['role'])

    if role_users:
        user_map = {}
        labels = []
        for u in role_users:
            # use the centralized label formatter (no team text)
            label = _format_user_label(u)
            user_map[label] = u
            labels.append(label)

        sel_key = f"sel_{opts['role']}"
        btn_key = f"btn_login_{opts['role']}"

        cols_footer = st.columns([3,1])
        with cols_footer[0]:
            selected_label = st.selectbox('', options=labels, key=sel_key, label_visibility='collapsed')

        with cols_footer[1]:
            if st.button('Login', key=btn_key):
                chosen = user_map.get(st.session_state.get(sel_key)) or user_map.get(selected_label)
                if chosen:
                    _complete_login(chosen, selected_label, opts)
                else:
                    st.error('Please select a user before logging in')
    else:
        # show a friendly fallback so the persona card still renders and is usable
        st.warning('No users found for this role. You can enter a username to continue (debug mode)')
        cols = st.columns([3,1])
        with cols[0]:
            manual_key = f"manual_{opts['role']}"
            manual = st.text_input('Enter a username to continue', key=manual_key, value='')
        with cols[1]:
            cont_key = f"continue_{opts['role']}"
            if st.button('Continue', key=cont_key):
                if manual and manual.strip():
                    _complete_login_from_input(opts['role'], manual, opts)
                else:
                    st.error('Please enter a username to continue')

    # small spacing between personas
    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

def _complete_login_from_input(role, input_name, opts):
    """Minimal login path when no user objects are available from the API.

    This sets minimal session_state and navigates to the persona page so the
    UI remains usable when the backend returns no users. Intended for debugging.
    """
    try:
        st.session_state['authenticated'] = True
        st.session_state['role'] = role
        st.session_state['user_id'] = None
        st.session_state['username'] = (input_name or '').strip()
        st.session_state['first_name'] = st.session_state['username'].split()[0] if st.session_state['username'] else ''
        st.session_state['team_id'] = None
        st.session_state['team_name'] = None
    except Exception:
        pass

    try:
        if hasattr(st, 'switch_page'):
            st.switch_page(opts.get('page'))
    except Exception:
        _safe_rerun()
    else:
        _safe_rerun()

# Check if user is already authenticated and redirect
if st.session_state.get('authenticated', False):
    role = (st.session_state.get('role') or '').lower()
    # Map role to appropriate page
    try:
        if role in ('superfan', 'fan'):
            st.switch_page('pages/10_Superfan_Home.py')
        elif role in ('data_engineer', 'admin'):
            st.switch_page('pages/20_Data_Engineer_Home.py')
        elif role in ('head_coach', 'coach'):
            st.switch_page('pages/30_Head_Coach_Home.py')
        elif role in ('general_manager', 'gm'):
            st.switch_page('pages/40_General_Manager_Home.py')
        else:
            # Invalid role, reset authentication
            st.session_state['authenticated'] = False
    except Exception:
        # If switch_page not available or fails, attempt a safe rerun
        try:
            if hasattr(st, 'switch_page'):
                st.switch_page('pages/10_Superfan_Home.py')
        except Exception:
            _safe_rerun()

# If not authenticated, show persona login cards
if not st.session_state.get('authenticated', False):
    st.markdown("## Choose your role to access BallWatch:")
    st.markdown('<div class="home-grid">', unsafe_allow_html=True)
    
    # Create columns for persona cards (2x2 grid)
    col1, col2 = st.columns(2)
    personas = list(user_options.keys())
    
    # Render first two personas in first row
    with col1:
        if len(personas) > 0:
            _render_persona(personas[0], user_options[personas[0]])
    with col2:
        if len(personas) > 1:
            _render_persona(personas[1], user_options[personas[1]])
    
    # Render remaining personas in second row  
    col3, col4 = st.columns(2)
    with col3:
        if len(personas) > 2:
            _render_persona(personas[2], user_options[personas[2]])
    with col4:
        if len(personas) > 3:
            _render_persona(personas[3], user_options[personas[3]])
    
    st.markdown('</div>', unsafe_allow_html=True)
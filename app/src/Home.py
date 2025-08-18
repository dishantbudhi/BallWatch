##################################################
# This is the main/entry-point file for the 
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import time
import requests
import os
import urllib.parse
from typing import Optional, Dict, Any, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create a session with retry strategy
def create_robust_session():
    """Create a requests Session with retries and pooling."""
    session = requests.Session()
    retry_strategy = Retry(
        total=2,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "PUT", "POST", "DELETE", "OPTIONS", "TRACE"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Global session for connection pooling
api_session = create_robust_session()

# Enhanced API base URL detection with correct Docker service names
def _default_api_base():
    """Determine API base URL with fallback logic."""
    # 1. Check environment variables first
    env = os.getenv('API_BASE_URL') or os.getenv('API_BASE')
    if env:
        logger.info(f"Using API_BASE from environment: {env}")
        return env
    
    # 2. Check if we're running in Docker
    is_docker = os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER', False)
    
    if is_docker:
        # Try common Docker service names used in docker-compose
        docker_urls = [
            'http://web-api:4000',  # Most likely based on your container names
            'http://api:4000',
            'http://flask-api:4000',
            'http://backend:4000'
        ]
        
        for url in docker_urls:
            try:
                logger.info(f"Trying Docker service: {url}")
                resp = api_session.get(f'{url}/system/health', timeout=2)
                if resp.status_code in [200, 404]:
                    logger.info(f"✅ Docker API found at: {url}")
                    return url
            except Exception as e:
                logger.debug(f"Failed to connect to {url}: {e}")
                continue
    
    # 3. Try localhost variants (for local development)
    localhost_urls = [
        'http://localhost:4000',
        'http://127.0.0.1:4000',
        'http://0.0.0.0:4000'
    ]
    
    for url in localhost_urls:
        try:
            logger.info(f"Trying localhost: {url}")
            resp = api_session.get(f'{url}/system/health', timeout=2)
            if resp.status_code in [200, 404]:
                logger.info(f"✅ Local API found at: {url}")
                return url
        except Exception as e:
            logger.debug(f"Failed to connect to {url}: {e}")
            continue
    
    # 4. Default fallback
    default = 'http://web-api:4000' if is_docker else 'http://localhost:4000'
    logger.warning(f"No API connection found, defaulting to {default}")
    return default

# Initialize API base with retry logic
def initialize_api_base():
    """Try multiple times to detect a working API base URL."""
    max_retries = 10
    retry_delay = 2
    
    for attempt in range(max_retries):
        api_base = _default_api_base()
        
        # Test the connection
        try:
            test_endpoints = ['/system/health', '/basketball/teams', '/auth/users']
            for endpoint in test_endpoints:
                try:
                    resp = api_session.get(f"{api_base}{endpoint}", timeout=2)
                    if resp.status_code in [200, 201, 404]:
                        logger.info(f"✅ API connection established at {api_base}")
                        return api_base
                except:
                    continue
        except:
            pass
        
        if attempt < max_retries - 1:
            logger.info(f"API not ready, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_delay)
    
    # Final fallback
    return api_base

# Initialize API base
API_BASE = initialize_api_base()
logger.info('Using API_BASE=%s', API_BASE)

# Store in session state
if 'api_base_url' not in st.session_state:
    st.session_state['api_base_url'] = API_BASE

if 'api_connection_status' not in st.session_state:
    st.session_state['api_connection_status'] = 'unknown'

# Test API connection
def test_api_connection():
    """Check connectivity against multiple API endpoints and set session state."""
    try:
        # Try multiple endpoints in case health check doesn't exist
        test_endpoints = ['/system/health', '/basketball/teams', '/auth/users']
        
        for endpoint in test_endpoints:
            try:
                resp = api_session.get(f"{API_BASE}{endpoint}", timeout=3)
                if resp.status_code in [200, 201, 404]:
                    st.session_state['api_connection_status'] = 'connected'
                    return True
            except Exception as e:
                logger.debug(f"Test connection failed for {endpoint}: {e}")
                continue
        
        st.session_state['api_connection_status'] = 'disconnected'
        return False
        
    except Exception as e:
        logger.error(f"API connection test failed: {e}")
        st.session_state['api_connection_status'] = 'disconnected'
        return False

# Enhanced GET request with connection fallback
def call_get_raw(endpoint: str, params: Optional[Dict[str, Any]] = None, timeout=5):
    """Wrapper for GET requests that respects session state and API_BASE."""
    # If disconnected, try to reconnect with new base
    if st.session_state.get('api_connection_status') == 'disconnected':
        new_base = _default_api_base()
        if new_base != API_BASE:
            st.session_state['api_base_url'] = new_base
            globals()['API_BASE'] = new_base
            logger.info(f"Switched API_BASE to: {new_base}")
    
    try:
        if endpoint.startswith('http'):
            url = endpoint
        else:
            url = f"{API_BASE}{endpoint}"
        
        resp = api_session.get(url, params=params, timeout=timeout)
        
        if resp.status_code in (200, 201):
            st.session_state['api_connection_status'] = 'connected'
            return resp.json()
        elif resp.status_code == 404:
            logger.warning(f'Endpoint not found: {endpoint}')
            return None
        else:
            logger.warning(f'GET {endpoint} returned {resp.status_code}')
            return None
            
    except requests.exceptions.ConnectionError:
        st.session_state['api_connection_status'] = 'disconnected'
        logger.error(f'Connection error for {endpoint}')
        return None
        
    except requests.exceptions.Timeout:
        logger.error(f'Timeout error for {endpoint}')
        return None
        
    except Exception as e:
        logger.error(f'Unexpected error in call_get_raw: {e}')
        return None

# Import or define API client functions
try:
    from modules.api_client import get_users, get_teams as api_get_teams, assign_team as api_assign_team
except ImportError:
    logger.warning("Could not import from modules.api_client, using local implementations")
    
    def get_users(role=None, timeout=5):
        params = {'role': role} if role else None
        return call_get_raw('/auth/users', params=params, timeout=timeout)
    
    def api_get_teams(timeout=5):
        return call_get_raw('/basketball/teams', timeout=timeout)
    
    def api_assign_team(user_id, team_id, timeout=5):
        try:
            resp = api_session.put(
                f"{API_BASE}/auth/users/{user_id}/assign-team",
                json={'team_id': team_id},
                timeout=timeout
            )
            if resp.status_code == 200:
                return resp.json().get('user') if resp.json() else None
        except:
            return None

def get_users_for_role(role, timeout=5):
    """Return a list of users for the given role with enhanced error handling."""
    
    # Check API connection status first
    if st.session_state.get('api_connection_status') == 'disconnected':
        if not test_api_connection():
            logger.warning(f"API disconnected, cannot fetch users for role: {role}")
            return []
    
    try:
        # Role aliases for flexibility
        alias_map = {
            'superfan': 'fan',
            'data_engineer': 'admin',
            'head_coach': 'coach',
            'general_manager': 'gm',
        }
        
        # Try primary role first
        candidates = [role]
        if role in alias_map:
            candidates.append(alias_map[role])
        
        for candidate in candidates:
            try:
                data = call_get_raw('/auth/users', {'role': candidate}, timeout)
                
                if data:
                    users = []
                    if isinstance(data, dict):
                        users = data.get('users', [])
                    elif isinstance(data, list):
                        users = data
                    
                    # Filter and normalize users
                    normalized_users = []
                    for user in users:
                        if isinstance(user, dict):
                            if not user.get('username'):
                                continue
                            
                            user_role = (user.get('role') or '').lower()
                            if user_role in [role.lower(), alias_map.get(role, '').lower()]:
                                normalized_users.append(user)
                    
                    if normalized_users:
                        return normalized_users
                        
            except Exception as e:
                logger.error(f"Error fetching users for role {candidate}: {e}")
                continue
        
        # Try getting all users as fallback
        all_users_data = call_get_raw('/auth/users', timeout=timeout)
        if all_users_data:
            all_users = []
            if isinstance(all_users_data, dict):
                all_users = all_users_data.get('users', [])
            elif isinstance(all_users_data, list):
                all_users = all_users_data
            
            filtered = []
            for user in all_users:
                if isinstance(user, dict):
                    user_role = (user.get('role') or '').lower()
                    if user_role in [role.lower(), alias_map.get(role, '').lower()]:
                        filtered.append(user)
            
            return filtered
            
    except Exception as e:
        logger.exception(f'Critical error in get_users_for_role: {e}')
    
    return []

def get_teams(timeout=5):
    """Return teams list from backend API."""
    try:
        data = call_get_raw('/basketball/teams', timeout=timeout)
        if isinstance(data, dict) and 'teams' in data:
            return data.get('teams', [])
        elif isinstance(data, list):
            return data
    except Exception as e:
        logger.error(f'Error fetching teams: {e}')
    return []

def assign_team(user_id, team_id, timeout=5):
    """Assign a team to a user via the auth API."""
    try:
        resp = api_session.put(
            f"{API_BASE}/auth/users/{user_id}/assign-team", 
            json={'team_id': team_id}, 
            timeout=timeout
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get('user') if isinstance(data, dict) else None
    except Exception as e:
        logger.error(f'Error assigning team: {e}')
    return None

def _safe_rerun():
    """Rerun Streamlit app safely across versions."""
    try:
        if hasattr(st, 'rerun'):
            st.rerun()
        elif hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
        else:
            st.session_state['_refresh'] = int(time.time())
            st.stop()
    except:
        st.stop()

# Page configuration
st.set_page_config(layout='wide', page_title='BallWatch Basketball Analytics')

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'debug_mode' not in st.session_state:
    st.session_state['debug_mode'] = False

# Sidebar navigation
SideBarLinks(show_home=True)

# Page title with connection status
col1, col2 = st.columns([4, 1])
with col1:
    st.title('BallWatch')
with col2:
    if st.session_state.get('api_connection_status') == 'connected':
        st.success('🟢 Connected')
    elif st.session_state.get('api_connection_status') == 'disconnected':
        st.error('🔴 Disconnected')
        if st.button('Retry'):
            if test_api_connection():
                _safe_rerun()
    else:
        st.info('⚪ Checking...')
        test_api_connection()

# Add CSS for persona cards
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

# Persona visual accents
_persona_accents = {
    'Superfan': {'emoji': '🏀', 'color': '#7C3AED'},
    'Data Engineer': {'emoji': '🛠️', 'color': '#059669'},
    'Head Coach': {'emoji': '🎯', 'color': '#0369A1'},
    'General Manager': {'emoji': '🏢', 'color': '#F97316'},
}

# User options definition
user_options = {
    "Superfan": {
        "persona_id": "p_superfan",
        "role": "superfan",
        "page": "pages/10_Superfan_Home.py",
        "bio": "A passionate basketball enthusiast who craves deeper insights beyond mainstream sports media. Frustrated by surface-level analysis and generic commentary, this user seeks advanced metrics and data-driven perspectives to truly understand player performance and team dynamics."
    },
    "Data Engineer": {
        "persona_id": "p_data_engineer",
        "role": "data_engineer",
        "page": "pages/20_Data_Engineer_Home.py",
        "bio": "An experienced data professional specializing in real-time sports analytics infrastructure. Daily challenges include maintaining data accuracy across multiple live feeds, managing pipeline failures during critical game moments, and scaling systems to handle increasing data volumes."
    },
    "Head Coach": {
        "persona_id": "p_head_coach",
        "role": "head_coach",
        "page": "pages/30_Head_Coach_Home.py",
        "bio": "A team leader who needs actionable insights to make strategic decisions quickly. Overwhelmed by dense statistical reports and complex spreadsheets that are difficult to interpret during game preparation and halftime adjustments."
    },
    "General Manager": {
        "persona_id": "p_general_manager",
        "role": "general_manager",
        "page": "pages/40_General_Manager_Home.py",
        "bio": "A front office executive tasked with rebuilding a struggling franchise through data-driven decision making. Faces pressure to identify undervalued talent, optimize roster construction, and justify expensive trades or signings to ownership."
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

# Helper: set session state and navigate after successful login
def _complete_login(chosen, selected_label, opts):
    try:
        st.session_state['authenticated'] = True
        st.session_state['role'] = opts['role']
        st.session_state['user_id'] = chosen.get('user_id') or chosen.get('id')
        st.session_state['username'] = chosen.get('username')
        st.session_state['first_name'] = chosen.get('first_name') or (selected_label.split(' — ')[0] if selected_label else '')
        
        # Set team_id in session if present
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

        # If a team_id is present, try to resolve and store team_name
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

        # Navigate to appropriate page
        try:
            if hasattr(st, 'switch_page'):
                st.switch_page(opts.get('page'))
        except Exception:
            _safe_rerun()
        else:
            _safe_rerun()

    except Exception as e:
        logger.exception('Exception in _complete_login: %s', e)

# Helper: fetch users for a role from backend
def fetch_users_for_role(role):
    """Fetch users for a role with extra debug logging when no users are returned."""
    users = get_users_for_role(role)
    if users:
        return users

    # No users found - provide diagnostics
    raw = None
    try:
        logger.info('No users returned for role=%s from get_users_for_role', role)
        
        # Show error with expandable diagnostics
        st.error('No users available for this role. Please contact your system administrator.')
        
        with st.expander('Diagnostics (click to view)', expanded=False):
            st.markdown(f"**API Base:** `{st.session_state.get('api_base_url')}`")
            st.markdown(f"**Connection Status:** {st.session_state.get('api_connection_status')}")
            st.markdown(f"**Role Requested:** {role}")
            
            retry_key = f"diag_retry_{role}"
            if st.button('Retry fetch', key=retry_key):
                _safe_rerun()
    except Exception:
        logger.exception('Failed to render diagnostics UI for role %s', role)

    return []

# Persona renderer
def _render_persona(title, opts):
    accent = _persona_accents.get(title, {'emoji': '👤', 'color': '#6B7280'})

    # Header and bio
    st.markdown(f"### {accent['emoji']}  {title}")
    st.write(opts['bio'])

    # Check connection before attempting to fetch users
    if st.session_state.get('api_connection_status') == 'disconnected':
        st.warning('⚠️ API connection unavailable. Please check your backend service.')
        if st.button(f'Retry Connection ({title})', key=f'retry_{opts["role"]}'):
            if test_api_connection():
                _safe_rerun()
        return

    # Fetch role-specific users
    with st.spinner('Loading users...'):
        role_users = fetch_users_for_role(opts['role'])

    if role_users:
        user_map = {}
        labels = []
        for u in role_users:
            label = _format_user_label(u)
            user_map[label] = u
            labels.append(label)

        sel_key = f"sel_{opts['role']}"
        btn_key = f"btn_login_{opts['role']}"

        cols_footer = st.columns([3,1])
        with cols_footer[0]:
            selected_label = st.selectbox('Select User', options=labels, key=sel_key, label_visibility='collapsed')

        with cols_footer[1]:
            if st.button('Login', key=btn_key):
                chosen = user_map.get(st.session_state.get(sel_key)) or user_map.get(selected_label)
                if chosen:
                    _complete_login(chosen, selected_label, opts)
                else:
                    st.error('Please select a user before logging in')
    else:
        # No users returned from API
        if st.session_state.get('debug_mode', False):
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
        else:
            st.info('No users available for this role. Please ensure the backend service is running and properly configured.')
            retry_key = f"retry_{opts['role']}"
            if st.button('Retry', key=retry_key):
                _safe_rerun()

    # Small spacing between personas
    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

def _complete_login_from_input(role, input_name, opts):
    """Minimal login path when no user objects are available from the API."""
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
    # Test connection on page load
    if 'connection_tested' not in st.session_state:
        with st.spinner('Connecting to backend service...'):
            test_api_connection()
        st.session_state['connection_tested'] = True
    
    st.markdown("## Choose your role:")
    
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
import os
import logging
import urllib.parse
import requests
import streamlit as st

logger = logging.getLogger(__name__)


def _default_api_base():
    env = os.getenv('API_BASE_URL') or os.getenv('API_BASE')
    if env:
        return env
    try:
        # If running inside a container prefer common docker-compose service hostnames
        if os.path.exists('/.dockerenv'):
            # Some setups name the API service 'api' while others use 'web-api' as the hostname
            # Prefer 'api' first for backward-compatibility, then 'web-api'.
            return 'http://api:4000'
    except Exception:
        pass

    # Local development fallbacks (including container service names for convenience)
    localhost_candidates = [
        'http://localhost:4000',
        'http://127.0.0.1:4000',
        'http://0.0.0.0:4000',
        'http://api:4000',
        'http://web-api:4000'
    ]
    # Prefer first candidate by default
    return localhost_candidates[0]


def ensure_api_base():
    """Return and cache a responsive API base URL.

    Probe a short list of common base URLs (env override, docker service
    hostnames, localhost) and pick the first one that responds to
    a lightweight GET to /basketball/teams.
    """
    if 'api_base_url' in st.session_state:
        return st.session_state['api_base_url']

    env = os.getenv('API_BASE_URL') or os.getenv('API_BASE')
    candidates = []
    if env:
        candidates.append(env.rstrip('/'))
    try:
        if os.path.exists('/.dockerenv'):
            # containerized: prefer service hostnames
            candidates.extend(['http://api:4000', 'http://web-api:4000'])
    except Exception:
        pass

    # local fallbacks
    candidates.extend(['http://localhost:4000', 'http://127.0.0.1:4000', 'http://0.0.0.0:4000'])

    # dedupe while preserving order
    seen = set()
    uniq = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    candidates = uniq

    chosen = None
    # quick probe to find a responsive API base
    for base in candidates:
        try:
            probe_url = f"{base.rstrip('/')}/basketball/teams"
            resp = requests.get(probe_url, timeout=1.5)
            if resp.status_code in (200, 201):
                chosen = base
                break
        except Exception:
            continue

    # fallback to first candidate if none responded
    if not chosen and candidates:
        chosen = candidates[0]

    st.session_state['api_base_url'] = chosen
    # store a simple connection flag for UI pages to surface
    st.session_state['api_connection_status'] = True if chosen else False
    return st.session_state['api_base_url']


def _parse_endpoint_with_query(endpoint: str):
    # Parse an endpoint URL into path and params
    if not endpoint:
        return endpoint, {}
    parsed = urllib.parse.urlparse(endpoint)
    path = parsed.path
    qs = urllib.parse.parse_qs(parsed.query)
    params = {k: v[0] for k, v in qs.items()}
    return path, params


def _request(method: str, endpoint: str, data=None, params=None, timeout=10):
    # Perform an HTTP request against the chosen API base and return JSON or None
    try:
        base = ensure_api_base()
        path, p = _parse_endpoint_with_query(endpoint)
        merged = {**(p or {}), **(params or {})}
        full = f"{base}{path}"
        resp = requests.request(method, full, json=data if method in ('POST','PUT','PATCH') else None, params=merged or None, timeout=timeout)
        if resp.status_code in (200, 201):
            try:
                return resp.json()
            except Exception:
                logger.warning('Non-JSON response from %s', full)
                return None
        logger.warning('%s %s returned %s', method, full, resp.status_code)
        if st.session_state.get('debug_mode', False):
            try:
                st.error(f"{method} {full} returned {resp.status_code}: {resp.text}")
            except Exception:
                pass
    except requests.exceptions.ConnectionError:
        logger.error('Connection error for %s %s', method, endpoint)
        if st.session_state.get('debug_mode', False):
            try:
                st.error(f"Connection error: {method} {endpoint} against {st.session_state.get('api_base_url')}")
            except Exception:
                pass
    except Exception as e:
        logger.exception('Error requesting %s %s: %s', method, endpoint, e)
    return None


def api_get(endpoint: str, params=None, timeout=10):
    return _request('GET', endpoint, data=None, params=params, timeout=timeout)


def api_post(endpoint: str, data=None, timeout=10):
    return _request('POST', endpoint, data=data, params=None, timeout=timeout)


def api_put(endpoint: str, data=None, timeout=10):
    return _request('PUT', endpoint, data=data, params=None, timeout=timeout)


def api_delete(endpoint: str, params=None, timeout=10):
    """DELETE request helper returning parsed JSON or None."""
    return _request('DELETE', endpoint, data=None, params=params, timeout=timeout)


def get_users(role=None, timeout=10):
    """GET /auth/users helper (optional role query)."""
    params = {'role': role} if role else None
    return api_get('/auth/users', params=params, timeout=timeout)


def get_teams(timeout=10):
    """GET /basketball/teams helper."""
    return api_get('/basketball/teams', params=None, timeout=timeout)


def assign_team(user_id, team_id, timeout=10):
    """Call PUT /auth/users/{user_id}/assign-team with JSON payload {team_id}.

    Returns parsed JSON body on success or None.
    """
    return api_put(f'/auth/users/{user_id}/assign-team', data={'team_id': team_id}, timeout=timeout)


def dedupe_by_id(items, id_keys=('player_id', 'id')):
    """Remove duplicate dict items by id key while preserving order."""
    if not items:
        return []
    seen = set()
    out = []
    for it in items:
        if not isinstance(it, dict):
            out.append(it)
            continue
        pid = None
        for k in id_keys:
            if k in it and it.get(k) is not None:
                pid = it.get(k)
                break
        if pid is None:
            out.append(it)
            continue
        try:
            key = int(pid)
        except Exception:
            key = str(pid)
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def get_players(params=None, timeout=10):
    """Fetch players from the API and return a deduplicated list.

    This is a convenience wrapper that normalizes the various response shapes
    (list or dict with 'players') and removes duplicates by player_id or id.
    """
    data = api_get('/basketball/players', params=params, timeout=timeout)
    if isinstance(data, dict) and 'players' in data:
        players = data.get('players', []) or []
    elif isinstance(data, list):
        players = data or []
    else:
        players = []

    return dedupe_by_id(players, id_keys=('player_id', 'id'))

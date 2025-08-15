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
        if os.path.exists('/.dockerenv'):
            return 'http://api:4000'
    except Exception:
        pass
    return 'http://localhost:4000'


def ensure_api_base():
    """Ensure st.session_state['api_base_url'] exists and return it."""
    if 'api_base_url' not in st.session_state:
        st.session_state['api_base_url'] = _default_api_base()
    return st.session_state['api_base_url']


def _parse_endpoint_with_query(endpoint: str):
    if not endpoint:
        return endpoint, {}
    parsed = urllib.parse.urlparse(endpoint)
    path = parsed.path
    qs = urllib.parse.parse_qs(parsed.query)
    params = {k: v[0] for k, v in qs.items()}
    return path, params


def _request(method: str, endpoint: str, data=None, params=None, timeout=10):
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
    """Perform a DELETE request against the API and return parsed JSON or None."""
    return _request('DELETE', endpoint, data=None, params=params, timeout=timeout)


def get_users(role=None, timeout=10):
    """Return parsed JSON from GET /auth/users. If role is provided it is sent as a query param."""
    params = {'role': role} if role else None
    return api_get('/auth/users', params=params, timeout=timeout)


def get_teams(timeout=10):
    """Return parsed JSON from GET /basketball/teams (or None)."""
    return api_get('/basketball/teams', params=None, timeout=timeout)


def assign_team(user_id, team_id, timeout=10):
    """Call PUT /auth/users/{user_id}/assign-team with JSON payload {team_id}.

    Returns parsed JSON body on success or None.
    """
    return api_put(f'/auth/users/{user_id}/assign-team', data={'team_id': team_id}, timeout=timeout)


def dedupe_by_id(items, id_keys=('player_id', 'id')):
    """Return a new list with duplicates removed based on one of the provided id_keys.

    Preserves original order. Items that are not dicts are returned unchanged.
    If an item has none of the id_keys set, it will be included (can't dedupe).
    """
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

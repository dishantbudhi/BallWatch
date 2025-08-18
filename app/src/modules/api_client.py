import os
import logging
import requests
from urllib.parse import urljoin, parse_qs
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Module-level API base and session
API_BASE = None
_session = None


def _default_api_base():
    """Resolve API base from environment with sensible fallbacks.
    Prioritize Docker service discovery when running in a container.
    """
    env = os.getenv('API_BASE_URL') or os.getenv('API_BASE')
    if env:
        logger.debug('Using API base from env: %s', env)
        return env.rstrip('/')

    # Detect Docker container context
    is_docker = os.path.exists('/.dockerenv') or bool(os.getenv('DOCKER_CONTAINER'))
    if is_docker:
        # In Compose, the API service is named 'web-api'
        return 'http://web-api:4000'

    # Local development default
    return 'http://localhost:4000'


def _ensure_session():
    """Create a requests Session with a retry strategy for idempotent calls."""
    global _session
    if _session is not None:
        return _session

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(500, 502, 503, 504))
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    _session = session
    return _session


def ensure_api_base():
    """Ensure API_BASE is initialized and return it."""
    global API_BASE
    if API_BASE:
        return API_BASE
    API_BASE = _default_api_base()
    logger.info('API_BASE resolved to %s', API_BASE)
    return API_BASE


def _parse_endpoint_with_query(endpoint: str):
    """Return (path, params_dict) given endpoint which may include querystring."""
    if not endpoint:
        return ('', {})
    if '?' not in endpoint:
        return (endpoint, {})
    path, qs = endpoint.split('?', 1)
    params = {k: v[0] if isinstance(v, list) else v for k, v in parse_qs(qs).items()}
    return (path, params)


def _request(method: str, endpoint: str, data=None, params=None, timeout=10):
    """Generic request helper that joins the API base and handles errors.
    Returns JSON dict or None on failure.
    """
    base = ensure_api_base()
    path, implicit_params = _parse_endpoint_with_query(endpoint)
    url = urljoin(base + '/', path.lstrip('/'))
    merged_params = {}
    if implicit_params:
        merged_params.update(implicit_params)
    if params:
        merged_params.update(params)

    session = _ensure_session()
    try:
        resp = session.request(method, url, json=data, params=merged_params or None, timeout=timeout)
        resp.raise_for_status()
        # Defensive: some endpoints return empty body
        if resp.text:
            return resp.json()
        return {}
    except requests.HTTPError as he:
        logger.warning('HTTP %s %s failed: %s - %s', method, url, resp.status_code if 'resp' in locals() else '', str(he))
    except Exception as e:
        logger.exception('Request error %s %s: %s', method, url, e)
    return None


def api_get(endpoint: str, params=None, timeout=10):
    return _request('GET', endpoint, data=None, params=params, timeout=timeout)


def api_post(endpoint: str, data=None, timeout=10):
    return _request('POST', endpoint, data=data, params=None, timeout=timeout)


def api_put(endpoint: str, data=None, timeout=10):
    return _request('PUT', endpoint, data=data, params=None, timeout=timeout)


def api_delete(endpoint: str, params=None, timeout=10):
    return _request('DELETE', endpoint, data=None, params=params, timeout=timeout)


# Convenience methods used by pages
def get_users(role=None, timeout=10):
    params = {'role': role} if role else None
    return api_get('/auth/users', params=params, timeout=timeout)


def get_teams(timeout=10):
    return api_get('/basketball/teams', timeout=timeout)


def assign_team(user_id, team_id, timeout=10):
    return api_put(f'/auth/users/{user_id}/assign-team', data={'team_id': team_id}, timeout=timeout)


def dedupe_by_id(items, id_keys=('player_id', 'id')):
    seen = set()
    out = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        _id = None
        for k in id_keys:
            if k in it:
                _id = it.get(k)
                break
        if _id is None:
            out.append(it)
            continue
        if _id in seen:
            continue
        seen.add(_id)
        out.append(it)
    return out


def get_players(params=None, timeout=10):
    """Return a list of player dicts, deduplicated by player_id.
    Normalizes backend responses that may wrap results under 'players'.
    """
    resp = api_get('/basketball/players', params=params, timeout=timeout)
    rows = []
    if isinstance(resp, dict) and 'players' in resp:
        rows = resp.get('players') or []
    elif isinstance(resp, list):
        rows = resp
    else:
        rows = []

    # Deduplicate by player id-like keys
    seen = set()
    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        pid = r.get('player_id') or r.get('id')
        key = pid if pid is not None else id(r)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out

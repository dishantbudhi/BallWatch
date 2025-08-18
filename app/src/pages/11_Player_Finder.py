# pages/Player_Finder.py

"""Player Finder page: search and filter players."""

import logging
import pandas as pd
import streamlit as st
import plotly.express as px
from modules.nav import SideBarLinks
from modules import api_client

# ensure session api base is initialized
api_client.ensure_api_base()

# Replace local URL helpers with centralized client

def call_get_raw(endpoint: str, params: dict | None = None, timeout=20):
    return api_client.api_get(endpoint, params=params, timeout=timeout) or {}


def call_post_raw(endpoint: str, data: dict | None = None, timeout=20):
    return api_client.api_post(endpoint, data=data, timeout=timeout) or {}


def call_put_raw(endpoint: str, data: dict | None = None, timeout=20):
    return api_client.api_put(endpoint, data=data, timeout=timeout) or {}


def _default_api_base():
    # retained for compatibility but session-managed by api_client
    return api_client.ensure_api_base()

BASE_URL = api_client.ensure_api_base()


def get_teams(timeout=5):
    data = api_client.api_get('/basketball/teams', timeout=timeout)
    if isinstance(data, dict) and 'teams' in data:
        return data.get('teams', [])
    if isinstance(data, list):
        return data
    return []


def get_players(params: dict | None = None):
    """Use centralized api_client.get_players (deduplicated) to avoid duplicate implementations."""
    try:
        return api_client.get_players(params=params)
    except Exception:
        # fallback to original behavior if api_client helper is unavailable
        data = api_client.api_get('/basketball/players', params=params)
        if isinstance(data, dict) and 'players' in data:
            return data.get('players', [])
        if isinstance(data, list):
            return data
        return []


def get_player_stats(player_id: int):
    data = api_client.api_get(f'/basketball/players/{player_id}/stats')
    if not data:
        return {}
    return data.get('stats') or data.get('player_stats') or data

logger = logging.getLogger(__name__)
st.set_page_config(page_title="Player Finder - Superfan", layout="wide")

# Render shared sidebar/nav
SideBarLinks()

st.title("Player Finder — Superfan")

# ---------------- Session Defaults (to keep results sticky across reruns) -------------
if "search_active" not in st.session_state:
    st.session_state.search_active = False
if "last_filters_pf" not in st.session_state:
    st.session_state.last_filters_pf = {}

# ---------- Utilities ----------
@st.cache_data(ttl=180)
def resolve_team_ids_by_name(name_query: str) -> list[int]:
    """
    Look up team(s) by name using /basketball/teams and return their team_id values.
    Case-insensitive 'contains' match; returns possibly multiple IDs.
    """
    if not name_query:
        return []
    teams = get_teams()
    if not teams:
        return []
    # teams is expected to be a list of dicts (get_teams returns list)
    df = pd.DataFrame(teams)
    if "name" not in df.columns or "team_id" not in df.columns:
        return []
    mask = df["name"].str.contains(name_query, case=False, na=False)
    return df.loc[mask, "team_id"].dropna().astype(int).tolist()

def _safe_players_df(rows):
    try:
        if isinstance(rows, list):
            return pd.DataFrame(rows)
        if isinstance(rows, dict):
            if 'players' in rows and isinstance(rows['players'], list):
                return pd.DataFrame(rows['players'])
            return pd.DataFrame([rows])
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=120)
def load_players(position=None, team_name=None, min_age=None, max_age=None, min_salary=None, max_salary=None):
    """
    Option A:
      - If team_name provided, resolve to team_id(s) then query /basketball/players per team_id
      - Union & de-duplicate results client-side.
    """
    base_params = {}
    if position: base_params["position"] = position
    if min_age is not None: base_params["min_age"] = min_age
    if max_age is not None: base_params["max_age"] = max_age
    if min_salary is not None: base_params["min_salary"] = min_salary
    if max_salary is not None: base_params["max_salary"] = max_salary

    rows: list[dict] = []

    if team_name:
        team_ids = resolve_team_ids_by_name(team_name)
        if not team_ids:
            return pd.DataFrame()  # no such team(s)
        for tid in team_ids:
            params = {**base_params, "team_id": tid}
            # call backend via local get_players helper
            part = get_players(params)
            rows.extend(part)
        # De-dup by player_id (keep last occurrence)
        if rows:
            rows = list({r.get("player_id"): r for r in rows if r.get("player_id") is not None}.values())
    else:
        rows = get_players(base_params)

    return _safe_players_df(rows)

@st.cache_data(ttl=120)
def fetch_player_stats(player_id: int):
    """
    Fetch per-player stats WITHOUT season/game type filters.
    Supports both {player_stats: {...}} and {stats: {...}} response shapes.
    """
    resp = get_player_stats(player_id)
    return resp or {}

def enrich_with_stats(df_players: pd.DataFrame, max_players: int = 50):
    """For performance, cap the number of stat fetches."""
    if df_players.empty:
        return df_players

    rows = []
    limit = min(len(df_players), max_players)
    for _, row in df_players.head(limit).iterrows():
        stats = fetch_player_stats(int(row["player_id"]))
        merged = {**row.to_dict(), **(stats or {})}
        rows.append(merged)
    # If there are more players than max_players, keep the remaining without stats.
    if len(df_players) > limit:
        remainder = df_players.iloc[limit:].copy()
        rows += [r for _, r in remainder.iterrows()]
    return pd.DataFrame(rows)

# ---------- Filters (TOP, not sidebar) ----------
st.header("Filters")

col1, col2, col3, col4 = st.columns(4)
with col1:
    position = st.selectbox(
        "Position",
        options=["", "PG", "SG", "SF", "PF", "C"],
        index=0,
        help="Filter by the player's listed position.",
        key="pf_position"
    )
with col2:
    team_name = st.text_input("Team Name (optional)", value="", help="Type a team name (partial match allowed).", key="pf_teamname")
with col3:
    min_age = st.number_input("Min Age", min_value=0, max_value=60, value=0, step=1, key="pf_minage")
with col4:
    max_age = st.number_input("Max Age", min_value=0, max_value=60, value=60, step=1, key="pf_maxage")

col5, col6, col7 = st.columns([1, 1, 2])
with col5:
    min_salary = st.number_input("Min Salary", min_value=0, value=0, step=100_000, key="pf_minsal")
with col6:
    max_salary = st.number_input("Max Salary", min_value=0, value=0, step=100_000, help="0 means no max", key="pf_maxsal")
with col7:
    include_stats = st.checkbox("Include Season Averages", value=True, key="pf_includestats")

col8, col9, col10 = st.columns([1, 1, 2])
with col8:
    max_stats = st.slider("Max Players for Stats", 10, 200, 50, 10, key="pf_maxstats")
with col9:
    stat_display_to_key = {
        "Points per game": "avg_points",
        "Rebounds per game": "avg_rebounds",
        "Assists per game": "avg_assists",
        "Steals per game": "avg_steals",
        "Blocks per game": "avg_blocks",
        "Turnovers per game": "avg_turnovers",
        "Plus/Minus": "avg_plus_minus",
        "Minutes per game": "avg_minutes",
        "Shooting %": "avg_shooting_pct",
    }
    stat_display = st.selectbox(
        "Stat to Sort/Chart",
        options=list(stat_display_to_key.keys()),
        index=0,
        key="pf_stat_display"
    )
    stat_to_sort = stat_display_to_key[stat_display]
with col10:
    # Make the Search button sticky: set a session flag we can rely on across reruns
    if st.button("Search Players", type="primary", key="pf_search_btn"):
        st.session_state.search_active = True

# Optional "New Search" to clear results
with st.container():
    st.markdown("")
    if st.session_state.search_active:
        if st.button("🔄 New Search (clear results)", key="pf_reset_btn"):
            st.session_state.search_active = False

st.markdown("---")

# Track filters (not strictly required—useful if you later want to auto-clear on big changes)
current_filters = {
    "position": position or None,
    "team_name": (team_name or "").strip() or None,
    "min_age": min_age if min_age > 0 else None,
    "max_age": max_age if max_age < 60 else None,
    "min_salary": min_salary if min_salary > 0 else None,
    "max_salary": (None if max_salary == 0 else max_salary),
}
st.session_state.last_filters_pf = current_filters

# ---------- Main area ----------
if st.session_state.search_active:
    # Treat 0 as “unset” for max_salary to avoid filtering out everyone
    max_salary_param = None if max_salary == 0 else max_salary

    df = load_players(
        position=(position or None),
        team_name=team_name.strip() or None,
        min_age=min_age if min_age > 0 else None,
        max_age=max_age if max_age < 60 else None,
        min_salary=min_salary if min_salary > 0 else None,
        max_salary=max_salary_param
    )

    if df.empty:
        st.warning("No players found for these filters.")
        # keep search_active True so user can tweak sliders without losing the section
        st.stop()

    st.subheader("Players (Basic Info)")
    st.dataframe(df, use_container_width=True, hide_index=True)

    if include_stats:
        df_stats = enrich_with_stats(df, max_players=max_stats)
    else:
        df_stats = df.copy()

    # Ensure the selected stat column exists
    if stat_to_sort not in df_stats.columns:
        df_stats[stat_to_sort] = 0

    # Friendly display name
    df_stats["player_name"] = (
        df_stats.get("first_name", "").astype(str) + " " + df_stats.get("last_name", "").astype(str)
    ).str.strip()

    # Ensure numeric sorting for selected stat (desc)
    if stat_to_sort in df_stats.columns:
        df_stats[stat_to_sort] = pd.to_numeric(df_stats[stat_to_sort], errors="coerce")
    df_sorted = df_stats.sort_values(by=stat_to_sort, ascending=False, na_position="last")

    st.subheader(f"Top Players by {stat_display}")
    top_n = st.slider("Show Top N", 5, 50, 15, 5, key="pf_topn")

    # Chart
    chart_cols = ["player_name", stat_to_sort, "position", "current_salary", "expected_salary"]
    for c in chart_cols:
        if c not in df_sorted.columns:
            df_sorted[c] = None
    chart_df = df_sorted.head(top_n)[chart_cols].copy()

    fig = px.bar(
        chart_df,
        x=stat_to_sort,
        y="player_name",
        color="position" if "position" in chart_df.columns else None,
        orientation="h",
        title=f"Top {min(top_n, len(chart_df))} by {stat_display}"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed table
    cols_to_show = [
        "player_id", "player_name", "position", "age", "years_exp",
        "current_team", "current_salary", "expected_salary",
        "avg_points", "avg_rebounds", "avg_assists", "avg_steals", "avg_blocks",
        "avg_turnovers", "avg_plus_minus", "avg_minutes", "avg_shooting_pct"
    ]
    present_cols = [c for c in cols_to_show if c in df_sorted.columns]
    st.subheader("Results Table")
    st.dataframe(df_sorted[present_cols], use_container_width=True, hide_index=True)
else:
    st.info("Set filters above and click **Search Players**.")

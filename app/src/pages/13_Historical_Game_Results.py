"""Historical games page: view past results and stats."""

# pages/Game_Search.py
import os
import logging
from datetime import date
import pandas as pd
import streamlit as st
import plotly.express as px
from modules.nav import SideBarLinks
import requests
import urllib.parse
from typing import Optional, Dict, Any, Tuple
from modules import api_client

api_client.ensure_api_base()
API_BASE = api_client.ensure_api_base()

# -------------------------------------------------------------------
# Page setup + Nav
# -------------------------------------------------------------------
logger = logging.getLogger(__name__)
st.set_page_config(page_title="Game Search & Box Scores", layout="wide")
SideBarLinks()  # shared sidebar/nav
st.title("📅 Game Search & Box Scores")
st.caption("Search games by date, team, season, and view full box scores.")

# ---------------- Session Defaults (keep results sticky) ----------------
if "gs_search_active" not in st.session_state:
    st.session_state.gs_search_active = False
if "gs_selected_game_id" not in st.session_state:
    st.session_state.gs_selected_game_id = None
if "gs_last_filters" not in st.session_state:
    st.session_state.gs_last_filters = {}

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def _parse_endpoint_with_query(endpoint: str) -> Tuple[str, Dict[str, Any]]:
    if not endpoint:
        return endpoint, {}
    parsed = urllib.parse.urlparse(endpoint)
    path = parsed.path
    qs = urllib.parse.parse_qs(parsed.query)
    params = {k: v[0] for k, v in qs.items()}
    return path, params

def call_get_raw(endpoint: str, params: Optional[Dict[str, Any]] = None, timeout=5):
    return api_client.api_get(endpoint, params=params, timeout=timeout)

def get_teams(timeout=5):
    data = api_client.api_get('/basketball/teams', timeout=timeout)
    if isinstance(data, dict) and 'teams' in data:
        return data
    return data


def search_games(params: dict | None = None):
    return api_client.api_get('/basketball/games', params=params)


def get_game_details(game_id: int):
    return api_client.api_get(f'/basketball/games/{int(game_id)}')

@st.cache_data(ttl=300)
def load_teams() -> pd.DataFrame:
    """Fetch teams for name-based selection."""
    data = get_teams()
    rows = data["teams"] if isinstance(data, dict) and "teams" in data else (data or [])
    df = pd.DataFrame(rows)
    # Expected columns: team_id, name, abrv, city ...
    if not df.empty:
        df["display"] = df.apply(
            lambda x: f"{x.get('name','')}" + (f" ({x.get('abrv','')})" if pd.notna(x.get('abrv')) else ""),
            axis=1
        )
    return df

@st.cache_data(ttl=180)
def search_games_wrapper(start_date: str | None, end_date: str | None,
                 season: str | None, game_type: str | None, status: str | None) -> dict | None:
    """We do NOT pass team_id here; we'll filter by team name client-side."""
    params = {}
    if start_date: params["start_date"] = start_date
    if end_date: params["end_date"] = end_date
    if season: params["season"] = season
    if game_type: params["game_type"] = game_type
    if status: params["status"] = status
    return search_games(params)

@st.cache_data(ttl=180)
def get_game_details_wrapper(game_id: int) -> dict | None:
    return get_game_details(game_id)

def fmt_game_row(g: dict) -> str:
    gd = g.get("game_date") or g.get("date") or ""
    gt = g.get("game_time") or ""
    home = g.get("home_team_name") or str(g.get("home_team_id"))
    away = g.get("away_team_name") or str(g.get("away_team_id"))
    score = f"{g.get('away_score','?')} - {g.get('home_score','?')}"
    return f"[{g.get('game_id')}] {gd} {gt} — {away} @ {home}  ({score})"

def safe_df(rows) -> pd.DataFrame:
    try:
        return pd.DataFrame(rows or [])
    except Exception:
        return pd.DataFrame()

def filter_games_by_team_names(games: list[dict], names: list[str]) -> list[dict]:
    """Filter games where selected team names participate.
       If one name selected: include games where home OR away matches.
       If two+ names selected: include games where ALL selected appear (typically 2)."""
    if not names:
        return games
    wanted = {n.strip().lower() for n in names if n and n.strip()}
    out = []
    for g in games:
        home = (g.get("home_team_name") or "").strip().lower()
        away = (g.get("away_team_name") or "").strip().lower()
        teams_in_game = {home, away}
        if (len(wanted) == 1 and wanted & teams_in_game) or (len(wanted) >= 2 and wanted.issubset(teams_in_game)):
            out.append(g)
    return out

# -------------------------------------------------------------------
# Filters (top)
# -------------------------------------------------------------------
st.header("Search Filters")

teams_df = load_teams()
team_options = teams_df["name"].dropna().sort_values().unique().tolist() if not teams_df.empty else []

f1, f2, f3 = st.columns([2, 1, 1])
with f1:
    team_names = st.multiselect(
        "Team Name(s)",
        options=team_options,
        help="Pick one team to see all its games, or two teams to see only head-to-head games.",
        key="gs_teams"
    )
with f2:
    sd = st.date_input("Start Date", value=None, min_value=date(2000,1,1), help="YYYY-MM-DD (inclusive)", key="gs_start")
with f3:
    ed = st.date_input("End Date", value=None, min_value=date(2000,1,1), help="YYYY-MM-DD (inclusive)", key="gs_end")

f4, f5, f6 = st.columns(3)
with f4:
    season = st.text_input("Season (optional)", value="", help="e.g., 2024-25 or 2025", key="gs_season").strip() or None
with f5:
    game_type = st.selectbox("Game Type", ["", "regular", "playoff"], index=0, key="gs_type") or None
with f6:
    status = st.selectbox("Status", ["", "scheduled", "in_progress", "completed"], index=0, key="gs_status") or None

col_btns = st.columns([1, 1, 6])
with col_btns[0]:
    if st.button("Search Games", type="primary", key="gs_search_btn"):
        st.session_state.gs_search_active = True
with col_btns[1]:
    if st.session_state.gs_search_active and st.button("🔄 New Search", key="gs_reset_btn"):
        st.session_state.gs_search_active = False
        st.session_state.gs_selected_game_id = None

st.markdown("---")

# -------------------------------------------------------------------
# Results + selection
# -------------------------------------------------------------------
games_df = pd.DataFrame()

if st.session_state.gs_search_active:
    start_date = sd.isoformat() if isinstance(sd, date) else None
    end_date = ed.isoformat() if isinstance(ed, date) else None

    # Save filters (optional, for debugging/telemetry)
    st.session_state.gs_last_filters = dict(
        teams=team_names,
        start_date=start_date,
        end_date=end_date,
        season=season,
        game_type=game_type,
        status=status,
    )

    payload = search_games_wrapper(
        start_date=start_date,
        end_date=end_date,
        season=season,
        game_type=game_type,
        status=status
    )

    if not payload or "games" not in payload:
        st.warning("No games returned. Adjust filters and try again.")
    else:
        games = payload["games"] or []
        # Filter by chosen team names
        games = filter_games_by_team_names(games, team_names)

        games_df = safe_df(games)

        # Quick summary (recomputed after team-name filtering)
        total = len(games)
        completed = len([g for g in games if g.get("status") == "completed"])
        scheduled = len([g for g in games if g.get("status") == "scheduled"])
        in_prog = len([g for g in games if g.get("status") == "in_progress"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", total)
        c2.metric("Completed", completed)
        c3.metric("Scheduled", scheduled)
        c4.metric("In Progress", in_prog)

        if games_df.empty:
            st.info("No games match these filters.")
        else:
            # Build selectbox options
            options = [fmt_game_row(g) for g in games]

            # Try to preserve previously selected game across reruns
            def option_for_game_id(gid: int | None) -> str | None:
                if gid is None:
                    return None
                for g in games:
                    if int(g.get("game_id")) == int(gid):
                        return fmt_game_row(g)
                return None

            preserved_opt = option_for_game_id(st.session_state.gs_selected_game_id)
            default_index = 0
            if preserved_opt in options:
                default_index = options.index(preserved_opt)

            st.subheader("Matching Games")
            sel = st.selectbox("Choose a game", options=options, index=default_index, key="gs_game_select")

            # Update selected game id from current selection
            if sel:
                try:
                    st.session_state.gs_selected_game_id = int(sel.split("]")[0].strip("["))
                except Exception:
                    st.session_state.gs_selected_game_id = int(games[0]["game_id"])

            # Display list
            show_cols = [
                "game_id", "game_date", "game_time",
                "home_team_name", "away_team_name",
                "home_score", "away_score",
                "season", "game_type", "status", "venue"
            ]
            present = [c for c in show_cols if c in games_df.columns]
            st.dataframe(games_df[present], use_container_width=True, hide_index=True)

st.markdown("---")

# -------------------------------------------------------------------
# Game details + player box scores
# -------------------------------------------------------------------
selected_game_id = st.session_state.gs_selected_game_id
if st.session_state.gs_search_active and selected_game_id:
    details = get_game_details_wrapper(selected_game_id)
    if not details or "game_details" not in details:
        st.error("Failed to load game details.")
    else:
        g = details["game_details"]
        home_team = g.get("home_team_name") or str(g.get("home_team_id"))
        away_team = g.get("away_team_name") or str(g.get("away_team_id"))
        st.header(f"Game #{g.get('game_id')} — {away_team} @ {home_team}")

        # Top summary
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Date", g.get("game_date", ""))
        s2.metric("Time", g.get("game_time", ""))
        s3.metric("Score", f"{g.get('away_score','?')} - {g.get('home_score','?')}")
        s4.metric("Status", g.get("status",""))

        # Player stats DataFrames
        def norm_df(rows):
            df = safe_df(rows)
            for col in ["points", "rebounds", "assists", "steals", "blocks", "turnovers", "minutes_played"]:
                if col not in df.columns: df[col] = None
            if "first_name" in df.columns and "last_name" in df.columns and "player_name" not in df.columns:
                df["player_name"] = (df["first_name"].astype(str) + " " + df["last_name"].astype(str)).str.strip()
            return df

        # Backend may return different shapes; support several common keys and fallback grouping
        raw_home = details.get("home_team_stats")
        raw_away = details.get("away_team_stats")
        # collect any generic player-stats list present
        candidate_stats = None
        for key in ("player_stats", "player_game_stats", "players", "stats"):
            if key in details and details.get(key):
                candidate_stats = details.get(key)
                break

        # If home/away lists are missing but a flat player-stats list exists, group by team
        if (not raw_home or not raw_away) and candidate_stats:
            try:
                all_stats = candidate_stats or []
                # coerce ids and names
                try:
                    home_id = int(g.get('home_team_id')) if g.get('home_team_id') is not None else None
                except Exception:
                    home_id = None
                try:
                    away_id = int(g.get('away_team_id')) if g.get('away_team_id') is not None else None
                except Exception:
                    away_id = None

                home_name = (g.get('home_team_name') or "").strip().lower()
                away_name = (g.get('away_team_name') or "").strip().lower()

                grouped_home = []
                grouped_away = []
                for s in all_stats:
                    # team id match preferred
                    try:
                        tid = s.get('team_id')
                        if tid is not None:
                            if home_id is not None and int(tid) == home_id:
                                grouped_home.append(s); continue
                            if away_id is not None and int(tid) == away_id:
                                grouped_away.append(s); continue
                    except Exception:
                        pass
                    # fallback to team_name match
                    tname = (s.get('team_name') or s.get('team') or "").strip().lower()
                    if tname and home_name and tname == home_name:
                        grouped_home.append(s)
                    elif tname and away_name and tname == away_name:
                        grouped_away.append(s)

                # Use grouped lists if we found any
                if grouped_home and not raw_home:
                    raw_home = grouped_home
                if grouped_away and not raw_away:
                    raw_away = grouped_away
            except Exception:
                # if grouping fails, fall back to empty lists
                raw_home = raw_home or []
                raw_away = raw_away or []

        home_df = norm_df(raw_home)
        away_df = norm_df(raw_away)

        # If the backend returned a flat player-stats list but not separated home/away lists,
        # present a combined table so the UI is not empty.
        if (home_df.empty or away_df.empty):
            flat_candidates = details.get('player_stats') or details.get('player_game_stats') or details.get('players') or details.get('stats')
            if flat_candidates:
                try:
                    combined = norm_df(flat_candidates)
                    if not combined.empty:
                        st.warning('Team-specific box scores not available; showing all player stats returned by the API for this game.')
                        display_cols = [c for c in ["player_name", "team_name", "position", "points", "rebounds", "assists", "steals", "blocks", "turnovers", "minutes_played"] if c in combined.columns]
                        st.dataframe(combined[display_cols], use_container_width=True, hide_index=True)
                        # keep normal home/away as empty DataFrames for downstream charts
                except Exception:
                    pass

        st.subheader("Player Box Scores")
        c_home, c_away = st.columns(2)
        with c_home:
            st.markdown(f"**{home_team} — Players**")
            hcols = ["player_name", "position", "points", "rebounds", "assists", "steals", "blocks", "turnovers", "minutes_played"]
            hpresent = [c for c in hcols if c in home_df.columns]
            st.dataframe(home_df[hpresent], use_container_width=True, hide_index=True)
        with c_away:
            st.markdown(f"**{away_team} — Players**")
            acols = ["player_name", "position", "points", "rebounds", "assists", "steals", "blocks", "turnovers", "minutes_played"]
            apresent = [c for c in acols if c in away_df.columns]
            st.dataframe(away_df[apresent], use_container_width=True, hide_index=True)

        # Quick charts: Top scorers
        st.subheader("Top Scorers")
        top_n = st.slider("Top N", 3, 15, 8, key="gs_topn")
        if not home_df.empty and "points" in home_df.columns:
            hchart = home_df.nlargest(top_n, "points")[["player_name", "points"]].copy()
            hfig = px.bar(hchart, x="points", y="player_name", orientation="h", title=f"{home_team} — Top {min(top_n, len(hchart))} by Points")
            st.plotly_chart(hfig, use_container_width=True)
        if not away_df.empty and "points" in away_df.columns:
            achart = away_df.nlargest(top_n, "points")[["player_name", "points"]].copy()
            afig = px.bar(achart, x="points", y="player_name", orientation="h", title=f"{away_team} — Top {min(top_n, len(achart))} by Points")
            st.plotly_chart(afig, use_container_width=True)
else:
    st.info("Pick one or two Team Names and set any date/season filters, then press **Search Games**. Select a game to view full box scores.")

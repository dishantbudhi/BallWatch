# pages/Player_Comparison.py
import logging
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from modules.nav import SideBarLinks
from modules import api_client
import os

logger = logging.getLogger(__name__)
st.set_page_config(page_title="Player Comparison - Superfan", layout="wide")

# Shared sidebar/nav
SideBarLinks()

st.title("🆚 Player Comparison — Superfan")
st.caption("Compare two players side-by-side, view recent games, and visualize trends.")

# ------------------------------------------------------------------------------------
# Session defaults
# ------------------------------------------------------------------------------------
if "compare" not in st.session_state:
    st.session_state.compare = False  # sticky compare mode
if "last_filters" not in st.session_state:
    st.session_state.last_filters = {}

api_client.ensure_api_base()

# Use api_client for raw calls
def call_get_raw(endpoint: str, params: dict | None = None, timeout=5):
    return api_client.api_get(endpoint, params=params, timeout=timeout)


def get_teams(timeout=5):
    data = api_client.api_get('/basketball/teams', timeout=timeout)
    if isinstance(data, dict) and 'teams' in data:
        return data.get('teams', [])
    if isinstance(data, list):
        return data
    return []


def get_players(params: dict | None = None):
    data = api_client.api_get('/basketball/players', params=params)
    if isinstance(data, dict) and 'players' in data:
        return data.get('players', [])
    if isinstance(data, list):
        return data
    return []


def get_player_stats(player_id: int):
    return api_client.api_get(f'/basketball/players/{player_id}/stats')

# compatibility wrapper used by page code
def api_get(path: str, params: dict | None = None):
    if path.startswith('/basketball/players'):
        return {'players': get_players(params)}
    if path == '/basketball/teams':
        return {'teams': get_teams()}
    return call_get_raw(path, params)

@st.cache_data(ttl=300)
def fetch_teams_df() -> pd.DataFrame:
    resp = api_get("/basketball/teams")
    teams = resp.get("teams", []) if isinstance(resp, dict) else (resp or [])
    df = pd.DataFrame(teams)
    for col in ["team_id", "name", "city", "conference", "division"]:
        if col not in df.columns:
            df[col] = None
    return df

@st.cache_data(ttl=300)
def resolve_team_ids_by_name(name_query: str) -> list[int]:
    if not name_query:
        return []
    df = fetch_teams_df()
    if df.empty:
        return []
    exact = df[df["name"].str.lower() == name_query.strip().lower()]
    if not exact.empty:
        return exact["team_id"].dropna().astype(int).tolist()
    contains = df[df["name"].str.contains(name_query, case=False, na=False)]
    return contains["team_id"].dropna().astype(int).tolist()

@st.cache_data(ttl=180)
def load_all_players(position: str | None = None, team_name: str | None = None) -> pd.DataFrame:
    base_params = {}
    if position:
        base_params["position"] = position

    rows: list[dict] = []

    if team_name:
        team_ids = resolve_team_ids_by_name(team_name)
        if team_ids:
            for tid in team_ids:
                params = {**base_params, "team_id": tid}
                data = api_get("/basketball/players", params)
                part = data.get("players", []) if isinstance(data, dict) else (data or [])
                rows.extend(part)
            if rows:
                rows = list({r.get("player_id"): r for r in rows if r.get("player_id") is not None}.values())
                df = pd.DataFrame(rows)
            else:
                df = pd.DataFrame()
        else:
            data = api_get("/basketball/players", base_params)
            rows = data.get("players", []) if isinstance(data, dict) else (data or [])
            df = pd.DataFrame(rows)
            if not df.empty and "current_team" in df.columns:
                mask = df["current_team"].fillna("").str.contains(team_name, case=False, na=False)
                df = df[mask].reset_index(drop=True)
    else:
        data = api_get("/basketball/players", base_params)
        rows = data.get("players", []) if isinstance(data, dict) else (data or [])
        df = pd.DataFrame(rows)

    if not df.empty:
        if "position" not in df.columns:
            df["position"] = ""
        df["display"] = (
            df.get("first_name", "").astype(str) + " " +
            df.get("last_name", "").astype(str) +
            df.apply(lambda x: f" · {x['position']}" if pd.notna(x.get("position")) else "", axis=1)
        )
    return df

@st.cache_data(ttl=180)
def fetch_player_stats(player_id: int):
    resp = get_player_stats(player_id)
    if not resp:
        return {}, pd.DataFrame()
    stats = resp.get("stats") or resp.get("player_stats") or resp.get('player_stats') or {}
    recent = pd.DataFrame(resp.get("recent_games", []) or [])
    if "game_date" not in recent.columns and "date" in recent.columns:
        recent = recent.rename(columns={"date": "game_date"})
    return stats, recent

# ------------------------------------------------------------------------------------
# Filters (no season or game_type)
# ------------------------------------------------------------------------------------
st.header("Filters")

fcol1, fcol2 = st.columns([1.5, 1.5])
with fcol1:
    position_filter = st.selectbox(
        "Position Filter (optional)",
        ["", "Guard", "Forward", "Center"],
        index=0,
        key="pos_filter"
    ) or None
with fcol2:
    team_name_filter = st.text_input("Team Name Filter (optional)", value="", key="team_filter")

st.markdown("")

# Detect filter changes to optionally reset comparison (keeps UX sane)
current_filters = {"position": position_filter, "team": (team_name_filter or "").strip()}
if current_filters != st.session_state.last_filters:
    st.session_state.last_filters = current_filters
    # Optional: uncomment to clear comparison when the universe of players changes
    # st.session_state.compare = False

players_df = load_all_players(position=position_filter, team_name=team_name_filter.strip() or None)
if players_df.empty:
    st.warning("No players available. Adjust filters or load data.")
    st.stop()

# ------------------------------------------------------------------------------------
# Player pickers
# ------------------------------------------------------------------------------------
scol1, scol2 = st.columns(2)
with scol1:
    search1 = st.text_input("Search Player 1 by name", value="", key="search_p1")
    df1 = players_df.copy()
    if search1.strip():
        df1 = df1[df1["display"].str.contains(search1.strip(), case=False, na=False)]
    player1 = st.selectbox("Select Player 1", options=df1["display"].tolist(),
                           index=0 if not df1.empty else None, key="select_p1")
with scol2:
    search2 = st.text_input("Search Player 2 by name", value="", key="search_p2")
    df2 = players_df.copy()
    if search2.strip():
        df2 = df2[df2["display"].str.contains(search2.strip(), case=False, na=False)]
    default_idx = 1 if len(df2) > 1 else 0
    player2 = st.selectbox("Select Player 2", options=df2["display"].tolist(),
                           index=default_idx if not df2.empty else None, key="select_p2")

def pick_id(df, display):
    if df.empty or not display:
        return None
    row = df[df["display"] == display].head(1)
    return int(row["player_id"].iloc[0]) if not row.empty else None

p1_id = pick_id(players_df, player1)
p2_id = pick_id(players_df, player2)

# Make the compare button sticky across reruns
if st.button("Compare Players", type="primary", key="compare_btn"):
    st.session_state.compare = True

st.markdown("---")

# ------------------------------------------------------------------------------------
# Comparison
# ------------------------------------------------------------------------------------
if st.session_state.compare and p1_id and p2_id:
    p1_stats, p1_recent = fetch_player_stats(p1_id)
    p2_stats, p2_recent = fetch_player_stats(p2_id)

    c1, c2 = st.columns(2)

    def name_for(pid):
        row = players_df[players_df["player_id"] == pid]
        if row.empty:
            return "Unknown"
        fn = row["first_name"].iloc[0] if "first_name" in row.columns else ""
        ln = row["last_name"].iloc[0] if "last_name" in row.columns else ""
        pos = row.get("position", pd.Series([""])).iloc[0]
        team = row.get("current_team", pd.Series([""])).iloc[0]
        return f"{fn} {ln} ({pos}) · {team}"

    with c1:
        st.subheader("Player 1")
        st.info(name_for(p1_id))
        for label, key in [
            ("Games Played", "games_played"),
            ("Avg Points", "avg_points"),
            ("Avg Rebounds", "avg_rebounds"),
            ("Avg Assists", "avg_assists"),
            ("Avg Plus/Minus", "avg_plus_minus"),
            ("Avg Minutes", "avg_minutes"),
        ]:
            if key in p1_stats and p1_stats[key] is not None:
                st.metric(label, p1_stats[key])

    with c2:
        st.subheader("Player 2")
        st.info(name_for(p2_id))
        for label, key in [
            ("Games Played", "games_played"),
            ("Avg Points", "avg_points"),
            ("Avg Rebounds", "avg_rebounds"),
            ("Avg Assists", "avg_assists"),
            ("Avg Plus/Minus", "avg_plus_minus"),
            ("Avg Minutes", "avg_minutes"),
        ]:
            if key in p2_stats and p2_stats[key] is not None:
                st.metric(label, p2_stats[key])

    st.markdown("---")

    radar_cols = [
        "avg_points", "avg_rebounds", "avg_assists",
        "avg_steals", "avg_blocks", "avg_turnovers",
        "avg_plus_minus", "avg_minutes", "avg_shooting_pct"
    ]
    p1_vals = [float(p1_stats.get(k, 0) or 0) for k in radar_cols]
    p2_vals = [float(p2_stats.get(k, 0) or 0) for k in radar_cols]
    display_names = [name_for(p1_id), name_for(p2_id)]

    rfig = go.Figure()
    rfig.add_trace(go.Scatterpolar(r=p1_vals, theta=radar_cols, fill='toself', name=display_names[0]))
    rfig.add_trace(go.Scatterpolar(r=p2_vals, theta=radar_cols, fill='toself', name=display_names[1]))
    rfig.update_layout(polar=dict(radialaxis=dict(visible=True)), title="Averages Radar")
    st.plotly_chart(rfig, use_container_width=True)

    st.subheader("Recent Box Scores (Historical Games)")
    # This slider caused reruns that hid results before—now compare state is sticky
    ng = st.slider("Number of Recent Games to Show", 5, 25, 10, 5, key="recent_games_n")

    for df_recent in (p1_recent, p2_recent):
        if not df_recent.empty:
            if "points" not in df_recent.columns and "PTS" in df_recent.columns:
                df_recent.rename(columns={"PTS": "points"}, inplace=True)
            if "rebounds" not in df_recent.columns and "REB" in df_recent.columns:
                df_recent.rename(columns={"REB": "rebounds"}, inplace=True)
            if "assists" not in df_recent.columns and "AST" in df_recent.columns:
                df_recent.rename(columns={"AST": "assists"}, inplace=True)

    if not p1_recent.empty or not p2_recent.empty:
        lp1 = p1_recent.head(ng).copy()
        lp2 = p2_recent.head(ng).copy()
        lp1["player"] = display_names[0]
        lp2["player"] = display_names[1]
        chart_parts = []
        if not lp1.empty: chart_parts.append(lp1)
        if not lp2.empty: chart_parts.append(lp2)
        if chart_parts:
            combined = pd.concat(chart_parts, ignore_index=True)
            if "game_date" in combined.columns:
                combined["game_date"] = pd.to_datetime(combined["game_date"], errors="coerce")
                x = "game_date"
            else:
                combined["n"] = combined.groupby("player").cumcount() + 1
                x = "n"
            if "points" in combined.columns:
                lfig = px.line(combined, x=x, y="points", color="player", markers=True, title="Points in Recent Games")
                st.plotly_chart(lfig, use_container_width=True)

    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"**{display_names[0]} — Recent Games (Top {ng})**")
        st.dataframe(p1_recent.head(ng), use_container_width=True, hide_index=True)
    with t2:
        st.markdown(f"**{display_names[1]} — Recent Games (Top {ng})**")
        st.dataframe(p2_recent.head(ng), use_container_width=True, hide_index=True)

else:
    st.info("Choose two players above and press **Compare Players** to view stats, trends, and box scores.")

# Debug
with st.expander("Debug Info"):
    st.write({
        "players_path": "/basketball/players",
        "stats_path": "/basketball/players/<id>/stats",
        "team_name_entered": team_name_filter,
        "search_active": st.session_state.compare,
        "filters": st.session_state.last_filters,
    })

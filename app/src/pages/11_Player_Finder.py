# pages/Player_Finder.py
import os
import logging
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(page_title="Player Finder", layout="wide")

# Render your app's sidebar nav (logo, links, auth redirect, etc.)
SideBarLinks()

st.title("🔎 Player Finder (Superfan)")

# If your Streamlit app runs in Docker alongside the API, keep http://api:4000
# If you run Streamlit on your host, set API_BASE_URL=http://localhost:4000
BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")

# ---------- Utilities ----------
def api_get(path: str, params: dict | None = None):
    try:
        url = f"{BASE_URL}{path}"
        r = requests.get(url, params=params, timeout=20)
        if r.status_code in (200, 201):
            return r.json()
        st.error(f"API {r.status_code}: {r.text}")
    except Exception as e:
        st.error(f"Connection error: {e}")
    return None

@st.cache_data(ttl=120)
def load_players(position=None, team_id=None, min_age=None, max_age=None, min_salary=None, max_salary=None):
    params = {}
    if position: params["position"] = position
    if team_id: params["team_id"] = team_id
    if min_age is not None: params["min_age"] = min_age
    if max_age is not None: params["max_age"] = max_age
    if min_salary is not None: params["min_salary"] = min_salary
    if max_salary is not None: params["max_salary"] = max_salary

    # ✅ Prefixed path
    data = api_get("/basketball/players", params)

    # Your /players handler currently returns a list (not wrapped in {"players": ...})
    if isinstance(data, dict) and "players" in data:
        rows = data["players"]
    else:
        rows = data or []
    return pd.DataFrame(rows)

@st.cache_data(ttl=120)
def fetch_player_season_stat(player_id: int, season: str | None):
    params = {}
    if season:
        params["season"] = season
    # NOTE: Your /players/<id>/stats returns a dict {stats: {...}, recent_games: [...]}
    # ✅ Prefixed path
    resp = api_get(f"/basketball/players/{player_id}/stats", params)
    if not resp or "stats" not in resp or resp["stats"] is None:
        return {}
    return resp["stats"]

def enrich_with_stats(df_players: pd.DataFrame, season: str | None, max_players: int = 50):
    """For performance, cap the number of stat fetches."""
    if df_players.empty:
        return df_players

    rows = []
    limit = min(len(df_players), max_players)
    for _, row in df_players.head(limit).iterrows():
        stats = fetch_player_season_stat(int(row["player_id"]), season)
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
        options=["", "PG", "SG", "SF", "PF", "C", "Guard", "Forward", "Center"],
        index=0,
        help="Filter by the player's listed position."
    )
with col2:
    team_id_input = st.text_input("Team ID (optional)", value="", help="Enter a numeric team_id.")
    team_id = int(team_id_input) if team_id_input.strip().isdigit() else None
with col3:
    min_age = st.number_input("Min Age", min_value=0, max_value=60, value=0, step=1)
with col4:
    max_age = st.number_input("Max Age", min_value=0, max_value=60, value=60, step=1)

col5, col6, col7, col8 = st.columns(4)
with col5:
    min_salary = st.number_input("Min Salary", min_value=0, value=0, step=100_000)
with col6:
    max_salary = st.number_input("Max Salary", min_value=0, value=0, step=100_000, help="0 means no max")
with col7:
    season = st.text_input("Season (optional)", value="", help="e.g., 2024-25 or 2025. Leave blank for all seasons.")
with col8:
    include_stats = st.checkbox("Include Season Averages (/basketball/players/<id>/stats)", value=True)

col9, col10, col11 = st.columns([1, 1, 2])
with col9:
    max_stats = st.slider("Max Players for Stats", 10, 200, 50, 10)
with col10:
    stat_to_sort = st.selectbox(
        "Stat to Sort/Chart",
        options=[
            "avg_points", "avg_rebounds", "avg_assists",
            "avg_steals", "avg_blocks", "avg_turnovers",
            "avg_plus_minus", "avg_minutes", "avg_shooting_pct",
        ],
        index=0
    )
with col11:
    run_btn = st.button("Search Players", type="primary")

st.markdown("---")

# ---------- Main area ----------
if run_btn:
    # Treat 0 as “unset” for max_salary to avoid filtering out everyone
    max_salary_param = None if max_salary == 0 else max_salary

    df = load_players(
        position=(position or None),
        team_id=team_id,
        min_age=min_age if min_age > 0 else None,
        max_age=max_age if max_age < 60 else None,
        min_salary=min_salary if min_salary > 0 else None,
        max_salary=max_salary_param
    )

    if df.empty:
        st.warning("No players found for these filters.")
        st.stop()

    st.subheader("Players (Basic Info)")
    st.dataframe(df, use_container_width=True, hide_index=True)

    if include_stats:
        st.info("Fetching season averages… this may take a moment for many players.")
        df_stats = enrich_with_stats(df, season if season.strip() else None, max_players=max_stats)
    else:
        df_stats = df.copy()

    # Ensure the selected stat column exists
    if stat_to_sort not in df_stats.columns:
        df_stats[stat_to_sort] = 0

    # Friendly display name
    df_stats["player_name"] = (
        df_stats.get("first_name", "").astype(str) + " " + df_stats.get("last_name", "").astype(str)
    ).str.strip()

    # Sort by selected stat (desc)
    df_sorted = df_stats.sort_values(by=stat_to_sort, ascending=False, na_position="last")

    st.subheader(f"Top Players by **{stat_to_sort}**")
    top_n = st.slider("Show Top N", 5, 50, 15, 5)

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
        title=f"Top {min(top_n, len(chart_df))} by {stat_to_sort}"
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

# Optional: debug footer
with st.expander("Debug Info"):
    st.write({
        "BASE_URL": BASE_URL,
        "players_path": "/basketball/players",
        "stats_path": "/basketball/players/<id>/stats"
    })

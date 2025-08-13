# pages/Game_Search.py
import os
import logging
from datetime import date
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from modules.nav import SideBarLinks

# -------------------------------------------------------------------
# Page setup + Nav
# -------------------------------------------------------------------
logger = logging.getLogger(__name__)
st.set_page_config(page_title="Game Search & Box Scores", layout="wide")
SideBarLinks()  # your shared sidebar nav/logo/auth
st.title("📅 Game Search & Box Scores")

# If Streamlit runs in Docker next to the API use http://api:4000
# If running on your host, set API_BASE_URL=http://localhost:4000
BASE_URL = os.getenv("API_BASE_URL", "http://api:4000")

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def api_get(path: str, params: dict | None = None):
    try:
        url = f"{BASE_URL}{path}"
        r = requests.get(url, params=params, timeout=25)
        if r.status_code in (200, 201):
            return r.json()
        st.error(f"API {r.status_code}: {r.text}")
    except Exception as e:
        st.error(f"Connection error: {e}")
    return None

@st.cache_data(ttl=300)
def load_teams() -> pd.DataFrame:
    """Fetch teams for name-based selection."""
    data = api_get("/basketball/teams", None)
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
def search_games(start_date: str | None, end_date: str | None,
                 season: str | None, game_type: str | None, status: str | None) -> dict | None:
    """We do NOT pass team_id here; we'll filter by team name client-side."""
    params = {}
    if start_date: params["start_date"] = start_date
    if end_date: params["end_date"] = end_date
    if season: params["season"] = season
    if game_type: params["game_type"] = game_type
    if status: params["status"] = status
    return api_get("/basketball/games", params)

@st.cache_data(ttl=180)
def get_game_details(game_id: int) -> dict | None:
    return api_get(f"/basketball/games/{game_id}")

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
        # If only one name: match either side; if 2+, require all selected present.
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
        help="Pick one team to see all its games, or two teams to see only head-to-head games."
    )
with f2:
    sd = st.date_input("Start Date", value=None, min_value=date(2000,1,1), help="YYYY-MM-DD (inclusive)")
with f3:
    ed = st.date_input("End Date", value=None, min_value=date(2000,1,1), help="YYYY-MM-DD (inclusive)")

f4, f5, f6 = st.columns(3)
with f4:
    season = st.text_input("Season (optional)", value="", help="e.g., 2024-25 or 2025")
    season = season.strip() or None
with f5:
    game_type = st.selectbox("Game Type", ["", "regular", "playoff"], index=0)
    game_type = game_type or None
with f6:
    status = st.selectbox("Status", ["", "scheduled", "in_progress", "completed"], index=0)
    status = status or None

go = st.button("Search Games", type="primary")
st.markdown("---")

# -------------------------------------------------------------------
# Results + selection
# -------------------------------------------------------------------
games_df = pd.DataFrame()
selected_game_id = None

if go:
    start_date = sd.isoformat() if isinstance(sd, date) else None
    end_date = ed.isoformat() if isinstance(ed, date) else None

    payload = search_games(
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

        # Quick summary
        s = payload.get("summary", {})
        # Recompute totals after filtering by names
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
            options = [fmt_game_row(g) for g in games]
            st.subheader("Matching Games")
            sel = st.selectbox("Choose a game", options=options, index=0)

            if sel:
                try:
                    selected_game_id = int(sel.split("]")[0].strip("["))
                except Exception:
                    selected_game_id = int(games[0]["game_id"])

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
if selected_game_id:
    details = get_game_details(selected_game_id)
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

        home_df = norm_df(details.get("home_team_stats"))
        away_df = norm_df(details.get("away_team_stats"))

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
        top_n = st.slider("Top N", 3, 15, 8)
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

# Debug footer
with st.expander("Debug Info"):
    st.write({
        "BASE_URL": BASE_URL,
        "teams_path": "/basketball/teams",
        "games_path": "/basketball/games",
        "game_details_path": "/basketball/games/<id>"
    })

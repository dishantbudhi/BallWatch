# BallWatch — CS3200 Project Template (Spring 2025)

This template provides a small basketball analytics platform with a Streamlit UI, a Flask REST API, and a MySQL database initialized from SQL files. Use it to explore full‑stack analytics patterns.

## Repository layout

- `app/` — Streamlit frontend
  - `src/` — Python source for the Streamlit app
    - `Home.py` — app entry point
    - `pages/` — Streamlit pages (personas and analytic pages such as `32_Lineup_and_Situational.py`)
    - `modules/` — shared client and navigation helpers (e.g. `api_client.py`, `nav.py`)
  - `Dockerfile` — image used by `docker-compose`

- `api/` — Flask REST API
  - `backend/` — Flask blueprints and DB connection (e.g. `basketball`, `analytics`, `auth`, `admin`, `strategy`)
  - `backend_app.py` — app entry point
  - `Dockerfile` — image used by `docker-compose`
  - `.env.template` — environment variables for DB connection

- `database-files/` — SQL schema and insert scripts that initialize the MySQL container

- `docker-compose.yaml` — orchestrates app, api, and db containers for local development

## Quickstart (Docker)

1. Copy the API env template and update secrets:

   cp api/.env.template api/.env
   # Edit api/.env and set MYSQL_ROOT_PASSWORD and any other values you need

2. Start all services with Docker Compose (from repository root):

   docker compose up -d

   Services:
   - `app` (Streamlit UI) → http://localhost:8501
   - `api` (Flask REST) → http://localhost:4000
   - `db` (MySQL) → host port 3200

   DB note: the container runs SQL from `database-files/` on first start. If you change SQL, re‑create the DB container/volume.

3. View the Streamlit app in your browser:

   http://localhost:8501

4. If the app can’t reach the API, verify the `api` container and see `app/src/modules/api_client.py` for base URL resolution.

## Functional overview

BallWatch is an end‑to‑end sample basketball analytics platform with distinct personas and workflows. The Streamlit UI talks to a Flask API that serves analytics and strategy endpoints backed by a MySQL schema.

### Personas and pages

- Superfan
  - Player Finder: filter players by position, team, age, and salary; optionally enrich with season averages; sort/chart by key stats.
  - Player Comparison: pick two players and compare per‑game averages, radar chart, and recent box scores.
  - Game Analysis: search historical games by team/date/season/type and view game details and box scores.

- Data Engineer
  - Data Pipelines: view data loads history, statuses, and metrics; retry a load; mark failed loads as resolved.
  - System Health: system status, DB health, metrics, and recent error logs with severity breakdown.
  - Data Cleanup: review data validation errors and mark items as resolved; schedule cleanups.

- Head Coach
  - Scouting & Game Planning: generate opponent reports (key players, performance snapshot, tactical notes) and create/activate game plans.
  - Lineup & Situational: analyze lineup plus/minus and ratings; see situational analytics (clutch, trends, splits) with recommendations.
  - Player Matchup: head‑to‑head player matchup analysis with advantage indicator and tactical recommendation.

- General Manager
  - Player Progress: development metrics and growth potential for players using draft evaluation data.
  - Draft Rankings: load and update player evaluations (ratings, notes, projected round).
  - Contract Efficiency: value vs. estimated salary analysis and signing strategy helpers.

### Core API flows

- Teams: `GET /basketball/teams` powers selectors across pages.
- Players: `GET /basketball/players` with optional filters (position, team_id, age, salary).
- Player stats: `GET /basketball/players/{id}/stats` for season averages and recent games.
- Games: `GET /basketball/games` + `GET /basketball/games/{id}` for search and box scores.
- Analytics:
  - Lineups: `GET /analytics/lineup-configurations?team_id=...&min_games=...` returns lineup plus/minus and ratings.
  - Situational: `GET /analytics/situational-performance?team_id=...&last_n_games=...` returns clutch, splits, trends, close games, performers.
  - Player Matchup: `GET /analytics/player-matchups?player1_id=...&player2_id=...` returns H2H summary and games.
  - Opponent report: `GET /analytics/opponent-reports?team_id=...&opponent_id=...` for scouting snapshot and recommendations.
- Strategy:
  - Game plans: `POST /strategy/game-plans`, `GET /strategy/game-plans?team_id=...`, `PUT /strategy/game-plans/{id}` to activate/update.
- Ops:
  - Data loads: `GET /system/data-loads?days=...`, `POST /system/data-loads` (retry), `PUT /system/data-loads/{id}` (resolve/update).
  - Error logs: `GET /system/error-logs?days=...`, `PUT /system/error-logs/{log_id}` (mark resolved).
  - Data errors: `GET /system/data-errors?days=...` for validation issues.
  - Cleanup scheduler: `GET/POST /system/data-cleanup` to list/schedule housekeeping.

### What you can do

- Explore teams/players/games and visualize comparisons and trends.
- Inspect lineup effectiveness (plus/minus, offense/defense ratings) and get rotation tips.
- Generate opponent scouting with key players and tactical guidance.
- Create and activate game plans for a team.
- Operate the data tier: check health, review errors, retry/resolve loads, and schedule cleanup jobs.

### Extending the project

- Add new analytics endpoints under `api/backend/analytics/` and wire them to a new Streamlit page in `app/src/pages/`.
- Expand the schema in `database-files/*.sql` (tables like Players, Game, PlayerGameStats, Teams, DraftEvaluations are already present) and expose new fields via the API.
- Keep response shapes consistent with existing pages (e.g., wrap collections: `{ "teams": [...] }`).

## Run locally without Docker

- Start a MySQL instance and create a database matching `api/.env` values.
- Run the Flask API:
  - cd `api/`
  - pip install -r requirements.txt
  - python backend_app.py
- Run the Streamlit app:
  - cd `app/src/`
  - pip install -r requirements.txt
  - streamlit run Home.py --server.port=8501 --server.address=0.0.0.0

## Important files

- `app/src/modules/api_client.py` — centralizes HTTP requests from the Streamlit UI to the Flask API. If you get "Unable to load teams data", check this file and ensure API_BASE is resolved and the API is running.
- `api/backend/analytics/analytics_routes.py` — contains routes for analytics endpoints such as `/analytics/lineup-configurations` and `/analytics/situational-performance` used by the UI.
- `database-files/` — SQL executed by MySQL on container startup. If the database is empty, the API will return empty datasets.

## Troubleshooting

- "⚠️ Unable to load teams data. Please check your API connection." — typically means the Streamlit app could not reach the Flask API or the API returned empty/invalid data. Steps:
  1. Ensure the `api` container is running: `docker compose ps` or `docker ps`.
  2. Check API logs: `docker compose logs api --tail 200`.
  3. Test the endpoint directly: `curl http://localhost:4000/basketball/teams`.
  4. Verify `api/.env` is set and DB is initialized. Check MySQL container logs for errors during startup.

- "No lineup configurations matched the filters." — the frontend filters by `min_games` before showing lineups. Verify the API returns lineup data for the team by querying `/analytics/lineup-configurations?team_id=<id>&min_games=<n>` directly.

- If you modify SQL in `database-files/`, remove the `mysql_db` container and its volumes before restarting to ensure initialization runs again:

  docker compose down
  docker compose up --build db

## Developer notes

- The app uses Streamlit caching (`@st.cache_data`) to reduce repeated API calls. Use the "Refresh Data" button (present on some pages) or clear the cache when debugging data updates.
- Several modules include defensive parsing of API responses; if endpoints return strings instead of JSON objects, the client may try to json.loads the payload. Keep API responses consistent (prefer JSON objects with expected keys).
- Many route implementations in `api/backend/*` are placeholders for course exercises. When adding real logic, update the route to return consistent JSON shapes the frontend expects (e.g. `{'teams': [...]}', `{'lineup_effectiveness': [...]}`, `{'situational': {...}}`).

## Contributing

- Follow the existing structure: UI under `app/src/`, backend blueprints under `api/backend/`.
- Add unit tests and manual API checks for endpoint shapes when changing backend output.

If you want, tell me which README section to expand or any wording change you prefer.

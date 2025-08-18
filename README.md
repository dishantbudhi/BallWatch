# HMS Sports Project Repository

This repo contains our semester project for CS3200: Intro to Databases. It includes our infrastructure setup (containers), project databases, and UI pages.

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

## Description
An all-in-one database for a high school sports team that streamlines activity for its users. Because the app focuses on specific user stories and personas, some views are intentionally scoped and may be “hard coded” to highlight relevant results for those roles.

## Features
This project supports role-based access with archetypical users. Each persona has tailored tools:

- Coach (Head Coach) Features
  - Scouting & Game Planning: opponent reports (key players, performance snapshot, tactical notes), create/activate game plans
  - Lineup & Situational: lineup plus/minus and ratings; situational analytics (clutch, trends, splits)
  - Player Matchup: head‑to‑head advantage indicators with tactical recommendations

- Superfan Features
  - Player Finder: filter by position/team/age/salary; add season averages; rank/chart by stat
  - Player Comparison: side‑by‑side metrics, radar chart, recent box scores
  - Game Analysis: search historical games and view box scores

- Data Engineer Tools
  - Data Pipelines: view load history and metrics; retry loads; mark failures as resolved
  - System Health: overall/DB status, platform metrics, recent error logs
  - Data Cleanup: review data validation errors and mark items as resolved; schedule cleanup tasks

- General Manager Tools
  - Player Progress: growth potential and development insights using evaluation data
  - Draft Rankings: load and update player evaluations (ratings, notes)
  - Contract Efficiency: value vs. estimated salary analysis and signing strategy helpers

- App Features
  - Clear entry points to tools and a navigation sidebar for quick access and logout

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

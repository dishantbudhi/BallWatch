# BallWatch — CS3200 Project Template (Spring 2025)

This repository contains the BallWatch sample analytics platform used for the CS3200 project. It includes a Streamlit frontend app, a Flask REST API backend, and a MySQL database initialized from SQL files. The README below documents how this specific codebase is organized and how to run it locally using Docker.

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

## Quickstart (Docker, recommended)

1. Copy the API env template and update secrets:

   cp api/.env.template api/.env
   # Edit api/.env and set MYSQL_ROOT_PASSWORD and any other values you need

2. Start all services with Docker Compose (from repository root):

   docker compose up -d

   This will build and run three services defined in `docker-compose.yaml`:
   - `app` (Streamlit UI) mapped to http://localhost:8501
   - `api` (Flask REST) mapped to http://localhost:4000
   - `db` (MySQL) mapped to host port 3200 in this compose

   The MySQL container executes SQL files from `database-files/` to create the sample schema and inserts. If you change SQL files, re-create the db container.

3. View the Streamlit app in your browser:

   http://localhost:8501

4. If the API is unreachable from the app, make sure the `api` container is healthy and reachable at http://localhost:4000. The Streamlit app uses `app/src/modules/api_client.py` to discover the API base URL.

## Running locally without Docker

- Start a MySQL instance and create a database matching `api/.env` values.
- Run the Flask API:
  - cd `api/`
  - pip install -r requirements.txt
  - python backend_app.py
- Run the Streamlit app:
  - cd `app/src/`
  - pip install -r requirements.txt
  - streamlit run Home.py --server.port=8501 --server.address=0.0.0.0

## Important files and behavior

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

## Notes for developers

- The app uses Streamlit caching (`@st.cache_data`) to reduce repeated API calls. Use the "Refresh Data" button (present on some pages) or clear the cache when debugging data updates.
- Several modules include defensive parsing of API responses; if endpoints return strings instead of JSON objects, the client may try to json.loads the payload. Keep API responses consistent (prefer JSON objects with expected keys).
- Many route implementations in `api/backend/*` are placeholders for course exercises. When adding real logic, update the route to return consistent JSON shapes the frontend expects (e.g. `{'teams': [...]}', `{'lineup_effectiveness': [...]}`, `{'situational': {...}}`).

## Contributing

- Follow the existing structure: UI under `app/src/`, backend blueprints under `api/backend/`.
- Add unit tests and manual API checks for endpoint shapes when changing backend output.

If you want, tell me which README section to expand or any wording change you prefer.

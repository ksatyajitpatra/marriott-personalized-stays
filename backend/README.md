# Backend — Marriott Bonvoy Enhanced Experience API

FastAPI service powering the additive Bonvoy experience: hotel search, eco
scoring, mock auth, reservations, local partner map, and the personalized
pre-stay Arrival Brief.

> All data is mocked. No real Marriott APIs, databases, or networks are touched.

## Quick start (local)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # tweak as needed
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs for the interactive OpenAPI UI.

## Endpoints (high-level)

| Method | Path                                  | Notes                         |
| ------ | ------------------------------------- | ----------------------------- |
| GET    | `/health`                             | liveness                      |
| POST   | `/auth/login`                         | persona login (alex/jordan/sam) |
| POST   | `/auth/logout`                        |                               |
| GET    | `/auth/me`                            | current session               |
| GET    | `/auth/profile`                       | full guest profile (auth req) |
| PATCH  | `/auth/profile/preferences`           | update pet service radius, etc. |
| GET    | `/guests` / `/guests/{id}`            | persona browsing              |
| GET    | `/hotels`                             | filter: `city`, `pet_friendly`, `min_eco` |
| GET    | `/hotels/{id}`                        | detail + LLM marketing copy   |
| GET    | `/hotels/{id}/eco-score`              | full eco breakdown            |
| GET    | `/partners/nearby?hotel_id=…`         | local partner map data        |
| GET    | `/reservations`                       | my trips (auth req)           |
| POST   | `/reservations`                       | book a stay                   |
| POST   | `/reservations/{id}/payment`          | mock payment                  |
| POST   | `/reservations/{id}/pet-services`     | book a pet service (date + time) |
| DELETE | `/reservations/{id}/pet-services/{bid}` | cancel a pet service booking   |
| GET    | `/arrival-brief/{stay_id}`            | pre-stay personalized brief   |

## Env

See [`.env.example`](./.env.example). The app boots with no keys configured —
LLM and weather both have deterministic mock paths.

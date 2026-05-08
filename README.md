# Chat with PDF

This project has two deployable services:
- `frontend` (Next.js)
- `backend` (FastAPI)

## Deploy to Railway

Create one Railway project with 3 services:
1. Postgres database
2. Backend service from `chat-with-pdf/backend`
3. Frontend service from `chat-with-pdf/frontend`

### 1) Create Postgres
- In Railway, add a `PostgreSQL` service.
- Keep its `DATABASE_URL` variable; backend will use it as `PGVECTOR_DSN` fallback.

### 2) Deploy Backend
- New service -> `Deploy from GitHub repo` -> set root directory to `chat-with-pdf/backend`.
- Railway will build from `backend/Dockerfile`.
- Add env vars:
  - `GEMINI_API_KEY=...`
  - `PGVECTOR_DSN=${{Postgres.DATABASE_URL}}` (or leave unset to use `DATABASE_URL`)
  - Optional: `CORS_ORIGINS=https://<your-frontend-domain>`
- Deploy.
- Copy backend public URL, e.g. `https://your-backend.up.railway.app`.

### 3) Deploy Frontend
- New service -> `Deploy from GitHub repo` -> set root directory to `chat-with-pdf/frontend`.
- Railway will build from `frontend/Dockerfile`.
- Add env var:
  - `NEXT_PUBLIC_API_URL=https://<your-backend-domain>/api`
- Deploy.

### 4) Final Wiring
- Set backend `CORS_ORIGINS` to your frontend URL, for example:
  - `CORS_ORIGINS=https://your-frontend.up.railway.app`
- Redeploy backend once after setting CORS.

## Notes
- Backend auto-creates `vector` extension/table/index at runtime.
- If your DB rejects `CREATE EXTENSION vector`, use a Postgres instance where `pgvector` is available.

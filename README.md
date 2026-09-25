# QueryMind — Chat with Your Data

[![CI](https://github.com/CodeWithMunnaX/QueryMind/actions/workflows/ci.yml/badge.svg)](https://github.com/CodeWithMunnaX/QueryMind/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Ask plain-English questions about a sales dataset and get a real answer: the exact SQL that produced
it, the result data, and an auto-generated chart — computed live against PostgreSQL. Every AI-generated
query is validated (read-only, schema-checked, row/time-capped) before it ever touches the database.

## Features

- **Landing page + email/password auth** — register/login gates the app; each user's history is isolated.
- **NL → SQL → execution → insight → chart** for any question about the sales data.
- **SQL safety validation** (SQLGlot) — blocks writes, DDL, multi-statements, unknown tables/columns.
- **Hallucination & ambiguity guardrails** — refuses to guess on fields that don't exist or vague questions.
- **Conversational follow-ups** — "what about only 2025?" uses the previous question's context.
- **Auto chart selection**, validated against the actual result columns.
- **Live dashboard** and **query history** — both computed from real data, nothing hardcoded.

## Tech stack

- **Frontend:** Next.js 15 · TypeScript · Tailwind CSS · Recharts · TanStack Query
- **Backend:** FastAPI · SQLAlchemy · Pandas · LangChain · OpenAI API · SQLGlot
- **Database:** PostgreSQL (tested on [Neon](https://neon.tech))
- **Infra:** Docker Compose

## Quick start

```bash
git clone <this-repo> && cd "Project 01"
cp .env.example .env        # fill in OPENAI_API_KEY, DATABASE_URL, JWT_SECRET_KEY
```

**Backend**

```bash
cd backend
python -m venv .venv && .venv/Scripts/activate   # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python data/generate_dataset.py     # generates the sample dataset
python -m app.database.seed         # creates tables + loads data
uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev   # http://localhost:3000
```

Open the app, click **Get started free**, register (any email + 8-char password), and you're in.

**Docker:** `cp .env.example .env` (fill in the values) then `docker compose up --build`.

## Environment variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI key. Never exposed to the frontend. |
| `DATABASE_URL` | PostgreSQL connection string. |
| `JWT_SECRET_KEY` | Signs auth tokens — generate with `python -c "import secrets; print(secrets.token_hex(32))"`. |
| `CORS_ORIGINS` | Origins allowed to call the API (default `http://localhost:3000`). |
| `NEXT_PUBLIC_API_URL` | Where the frontend finds the backend (default `http://localhost:8000`). |

Full list with defaults in `backend/.env.example` and `frontend/.env.example`.

## Example questions

- Which category generated the highest revenue in 2025?
- Show me the top 5 products by revenue in 2025.
- What are total sales by region?
- Compare sales and profit by category.
- Show me the best products. *(too vague → asks a clarifying question)*
- Show revenue by department. *(not a real column → hallucination guardrail)*

## API

Docs at **`/docs`** once the backend is running. All endpoints except `/api/auth/register`,
`/api/auth/login`, and `/api/health` require `Authorization: Bearer <token>`.

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/register` / `/api/auth/login` | Get a JWT. |
| `POST` | `/api/chat` | question → SQL → execution → summary → chart |
| `POST` | `/api/query` | Re-run a known, validated SQL string |
| `GET` | `/api/dashboard` / `/api/history` / `/api/schema` | Live metrics, your query history, live schema |

## Security highlights

- Passwords hashed with `bcrypt`; sessions are signed JWTs. Every user's data is isolated by `user_id`.
- The LLM only ever produces a SQL *string* — it's parsed, schema-checked, and restricted to
  read-only `SELECT`/`WITH` (SQLGlot) before execution, inside a read-only, time-limited transaction.
- Charts can't reference invented columns; row counts and query time are always capped.
- Secrets (`OPENAI_API_KEY`, `DATABASE_URL`, `JWT_SECRET_KEY`) stay server-side — never commit `.env`.

## Data & ML pipeline (optional, standalone)

The dataset is versioned with [DVC](https://dvc.org), and `ml/` holds a separate pipeline that
trains a small local text-to-SQL model from it (`dvc repro`). **Not used by the running app** — see
[`ml/README.md`](ml/README.md).

## Future improvements

- Streaming chat responses
- A dedicated read-only DB role (defense in depth alongside app-level validation)
- Multi-dataset support
- Password reset / email verification
- OAuth login (Google/GitHub)

## License

MIT — see [LICENSE](LICENSE).

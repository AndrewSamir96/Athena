# Chat With Your Notes — React + Python Build Guide

A single-user RAG app: upload your own notes/PDFs, ask questions, get answers grounded in them (with citations). Built to teach you **React** (your first frontend) and a **Python/FastAPI RAG backend** — nothing more, nothing less. No teams, no roles, no multi-user chat. Do the phases in order; each depends on the last.

## Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.11+ + FastAPI |
| Frontend | React + Vite |
| Database | PostgreSQL + `pgvector` extension |
| Auth | JWT (kept simple — one user type, no roles) |
| LLM + embeddings | Anthropic API (or OpenAI — either works) |
| Real-time answer streaming | Server-Sent Events (SSE) — simpler than WebSockets, and it's what most production LLM apps actually use |

---

## Phase 0 — Environment & scaffolding

### 0.1 Install
- Python 3.11+, Node.js 20+, Docker Desktop (for Postgres), a code editor (VS Code is fine).
- Check versions:
```bash
python3 --version
node -v
npm -v
docker --version
```

### 0.2 Backend scaffold
```bash
mkdir notes-rag && cd notes-rag
mkdir backend frontend
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary alembic \
  pydantic-settings python-jose[cryptography] "passlib[bcrypt]" python-multipart
pip freeze > requirements.txt
```
Target structure:
```
backend/
  app/
    main.py            # FastAPI app entrypoint
    config.py          # settings from .env
    database.py         # SQLAlchemy engine/session
    models/             # ORM models (one file per table)
    schemas/             # Pydantic request/response shapes
    routers/             # one file per resource (auth, notes, chat)
    services/             # business logic: chunking, embeddings, retrieval, llm
    core/                 # security.py (JWT/hashing), deps.py (get_current_user)
  alembic/
  requirements.txt
  .env                   # never commit this
```

### 0.3 Frontend scaffold
```bash
cd ../frontend
npm create vite@latest . -- --template react
npm install
npm install react-router-dom axios
```
Target structure:
```
frontend/
  src/
    api/            # axios client + auth header injection
    auth/           # AuthContext, LoginPage, RegisterPage
    notes/          # UploadPage, NotesList
    chat/           # ChatPage, useChatStream hook
    App.jsx
    main.jsx
```

### Checkpoint
`uvicorn app.main:app --reload` serves on `localhost:8000` (with a `/health` route returning 200); `npm run dev` serves on `localhost:5173`. Both start with no errors.

---

## Phase 1 — Postgres + pgvector, by hand first

### 1.1 Run Postgres with pgvector via Docker (no local install needed)
At the repo root, `docker-compose.yml`:
```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    restart: always
    environment:
      POSTGRES_USER: notesrag
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: notesrag
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```
```bash
docker compose up -d
docker exec -it $(docker compose ps -q db) psql -U notesrag -d notesrag -c "SELECT 1;"
```

### 1.2 Enable the extension
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 1.3 Learn the mechanism by hand, before any app code
```sql
CREATE TABLE playground (id serial PRIMARY KEY, embedding vector(3));
INSERT INTO playground (embedding) VALUES ('[1,2,3]'), ('[4,5,6]'), ('[1,2,4]');
SELECT id, embedding <=> '[1,2,3]' AS distance FROM playground ORDER BY distance LIMIT 2;
```
`<=>` is cosine distance — smaller means more similar. This one query *is* the retrieval mechanism you'll build the rest of the app around.

### Checkpoint
You can explain, in one sentence, why "nearest vector" search finds relevant text — and you've watched it return the right nearest row above.

---

## Phase 2 — Database schema (design once, use everywhere)

```sql
CREATE TABLE users (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email         varchar(255) UNIQUE NOT NULL,
  hashed_password varchar(255) NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE notes (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title       varchar(255) NOT NULL,
  status      varchar(20) NOT NULL,          -- 'pending' | 'processing' | 'ready' | 'failed'
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE note_chunks (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  note_id     uuid NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  chunk_index int NOT NULL,
  content     text NOT NULL,
  embedding   vector(1536) NOT NULL          -- must match your embedding model's dimension exactly
);
CREATE INDEX ON note_chunks USING hnsw (embedding vector_cosine_ops);

CREATE TABLE chat_messages (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role        varchar(20) NOT NULL,          -- 'user' | 'assistant'
  content     text NOT NULL,
  citations   jsonb,                          -- [{note_id, chunk_id, title}] — nullable
  created_at  timestamptz NOT NULL DEFAULT now()
);
```

Mirror this with SQLAlchemy models in `app/models/` — one file each: `user.py`, `note.py`, `chunk.py`, `message.py`. Use `pgvector.sqlalchemy.Vector` (`pip install pgvector`) for the embedding column type.

Then set up Alembic:
```bash
alembic init alembic
# edit alembic/env.py to import your Base and read DATABASE_URL from settings
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```
**Why migrations instead of just letting SQLAlchemy create tables:** you get a versioned, repeatable history of schema changes — essential once there's real data you can't just drop.

### Checkpoint
You can draw how a `note` relates to its `note_chunks`, and how `chat_messages` references `users` — before writing a single route.

---

## Phase 3 — Plain REST API (no auth, no AI yet)

### 3.1 The shape every feature follows
**Router** (HTTP in/out) → **Service** (logic) → **SQLAlchemy model** (data). Keep routers thin.

### 3.2 Build first (unauthenticated for now)
| Method | Path | Purpose |
|---|---|---|
| POST | `/notes` | Create a note record (metadata only) |
| GET | `/notes` | List all notes |
| GET | `/notes/{id}` | Get one note |
| DELETE | `/notes/{id}` | Delete a note |

Run with `uvicorn app.main:app --reload` and use FastAPI's free auto-generated docs at `localhost:8000/docs` to test every endpoint — this is your Postman replacement for the whole project.

### Checkpoint
Via `/docs`, you create, list, and delete a note, and see the row appear/disappear in `psql`.

---

## Phase 4 — Auth (JWT, kept simple)

### 4.1 Concepts
- Passwords are hashed, never stored plain — `passlib`'s bcrypt.
- A JWT is a signed token containing the user's id and an expiry; the server verifies the signature, it never looks up a session.
- "Stateless" = no server-side session store; every request proves identity via the `Authorization: Bearer <token>` header.

### 4.2 Build
- `app/core/security.py`: `hash_password`, `verify_password`, `create_access_token`, `decode_token`.
- `app/routers/auth.py`: `POST /auth/register`, `POST /auth/login` (returns a JWT).
- `app/core/deps.py`: `get_current_user` — a FastAPI dependency that decodes the token, loads the user, raises `401` if invalid.
- Scope every notes/chat query by `get_current_user`'s id — never trust a user-supplied id in the request body.

### Checkpoint
`GET /notes` without a token → `401`. With a valid token from `/auth/login` → `200` and only your notes.

---

## Phase 5 — Frontend basics (React)

This is your first frontend — keep it to plain building blocks, no state-management library yet.

### 5.1 Build
- `src/api/client.js` — an axios instance with a request interceptor that attaches the JWT from React state/localStorage.
- `src/auth/AuthContext.jsx` — React Context holding `{ user, token, login(), logout() }`. This is *why* Context exists: any component can read auth state without passing props down manually ("prop drilling").
- `src/auth/LoginPage.jsx`, `RegisterPage.jsx` — forms posting to your auth endpoints.
- `src/notes/NotesListPage.jsx`, `UploadPage.jsx`.
- `react-router-dom` with a `ProtectedRoute` wrapper that redirects to `/login` if there's no token.

### Checkpoint
You register, log in, and see an empty notes list — entirely through the browser, no `/docs` involved. Refreshing the page doesn't log you out.

---

## Phase 6 — Ingestion pipeline (the "R" in RAG)

### 6.1 Concepts
- **Chunking:** split each document into ~500–800 token chunks with ~10–15% overlap, ideally on paragraph boundaries, so context isn't cut mid-thought and retrieval returns focused passages instead of whole files.
- **Embeddings:** a call to an embeddings API turns each chunk into a vector. The *same* model must be used for storing and querying, and the `vector(N)` column dimension must match its output size exactly.

### 6.2 Build
```bash
pip install pypdf langchain-text-splitters
```
- `services/ingestion_service.py`:
  1. Extract text (`pypdf` for PDFs, plain read for `.txt`/`.md`).
  2. Chunk with `RecursiveCharacterTextSplitter`.
  3. Embed each chunk (batch 50–100 per API call, not one call per chunk).
  4. Insert `note_chunks` rows; mark the note `status = 'ready'`.
- `POST /notes/upload` (multipart) — save the note as `pending`, run ingestion. Start **synchronously in the request** (simplest); note as a known limitation you could later fix with `BackgroundTasks`.
- Frontend: an upload form with a status indicator (poll `GET /notes/{id}` every couple seconds, or just refetch after upload).

### Checkpoint
After uploading a PDF, `SELECT count(*) FROM note_chunks WHERE note_id = '...'` shows multiple rows, each with a non-null `embedding`.

---

## Phase 7 — Retrieval + generation, with citations (the "AG" in RAG)

### 7.1 The loop, precisely
1. Embed the user's question (same embedding model as ingestion).
2. `SELECT content, note_id, chunk_index FROM note_chunks WHERE note_id IN (your notes) ORDER BY embedding <=> :question_vector LIMIT 5`.
3. Build a prompt with **explicit source tags**, e.g.:
   ```
   [Source 1: "onboarding.pdf", chunk 3]
   <chunk text>

   [Source 2: "handbook.pdf", chunk 7]
   <chunk text>

   Answer the question using only the sources above. Cite the source number after each claim.
   If the sources don't contain the answer, say so explicitly.
   ```
4. Call the LLM, return both the answer text and a structured `citations` list (`{note_id, chunk_id, title}`) so the frontend can render them as clickable references.
- `services/retrieval_service.py`, `services/llm_service.py` (a thin wrapper around the Anthropic/OpenAI SDK).
- `POST /chat/ask` (plain, non-streaming first) — wire the full loop, test it in `/docs` before touching the frontend.

### Checkpoint
A question about content only in your notes returns a correct, grounded answer with a citation pointing at the right chunk. A question outside your notes' content gets an honest "I don't know" rather than a hallucination.

---

## Phase 8 — Streaming answers (optional but a great resume line)

### 8.1 Concepts
- Streaming tokens as they're generated (instead of waiting for the full answer) is what makes an LLM app feel responsive.
- SSE (Server-Sent Events) is a one-directional HTTP stream — simpler than WebSockets, and exactly the right tool here since you only need server → client.

### 8.2 Build
- Switch your LLM call to streaming mode (`stream=True` in the Anthropic/OpenAI SDK).
- `GET /chat/ask/stream` returning `text/event-stream`, yielding each token as an SSE event, then a final event with the citations.
- Frontend: `EventSource` (or a small `useChatStream` hook) that appends each token to the in-progress answer bubble as it arrives.
- Persist the full user question + assistant answer to `chat_messages` once the stream completes.

### Checkpoint
Asking a question shows the answer appearing progressively, word by word — not all at once.

---

## Phase 9 — Polish & stretch goals (pick 1–2, don't do all)
- `docker-compose.yml` extended to also run the backend and frontend, so the whole app starts with one command.
- Deploy: Neon/Supabase (free Postgres + pgvector) → Render/Railway (backend) → Vercel/Netlify (frontend static build).
- A basic README: what it does, a short GIF of the citation flow, how to run it locally, and a "trade-offs" paragraph (e.g. *"chose pgvector over a dedicated vector store to avoid extra infra at this scale"*) — this is what makes a portfolio project read as intentional rather than tutorial-copied.
- Conversation memory: include the last few `chat_messages` in the prompt so follow-up questions work.

---

## What to do next
Start Phase 0 for real: get Python, Node, and Docker verified, scaffold both projects, and get `localhost:8000` and `localhost:5173` running side by side before writing any real logic.

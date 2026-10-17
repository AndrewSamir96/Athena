# Athena

Athena is a small, private notes assistant. Users can create an account, upload
PDF or text notes, and ask questions whose answers are generated from the
uploaded notes with source citations.

The project is intentionally simple: it has one user type, a single frontend
and backend, and no teams, roles, or collaborative features.

## Features

### Authentication

- Register with an email address and password.
- Log in and receive a JWT bearer token.
- Passwords are hashed with bcrypt.
- Protected note and chat routes are scoped to the authenticated user.
- Log out from the application shell.

### Notes

- List the signed-in user's notes.
- Upload one PDF, TXT, or Markdown file at a time.
- Drag and drop a file or select it through the file picker.
- Extract text from PDFs with `pypdf`.
- Read UTF-8 text files.
- Split extracted text into overlapping chunks.
- Generate embeddings for chunks with the local Ollama
  `embeddinggemma` model.
- Store chunks and 768-dimensional embeddings in PostgreSQL with pgvector.
- Show note processing status: `pending`, `processing`, `ready`, or `failed`.
- Delete a note and its chunks.

### Chat and retrieval

- Ask a question about the authenticated user's uploaded notes.
- Retrieve the five closest ready chunks using cosine distance.
- Generate an answer with the local Ollama `qwen3.5:0.8b` model.
- Return source citations containing the note and chunk identifiers.
- Display answers and citation chips in a chat interface.
- Show a loading state while an answer is being generated.

### User interface

- React single-page application with protected routes.
- Login and registration screens.
- Notes list and upload screens.
- Chat screen.
- Sidebar navigation.
- Light and dark themes with persisted theme selection.
- Persisted login token and display email in browser local storage.
- Empty, loading, error, and upload-processing states.

### Backend API

| Method | Endpoint | Purpose | Auth |
| --- | --- | --- | --- |
| `GET` | `/health` | Check that the API is running | No |
| `POST` | `/auth/register` | Create an account and return a token | No |
| `POST` | `/auth/login` | Authenticate and return a token | No |
| `GET` | `/notes` | List the current user's notes | Bearer token |
| `GET` | `/notes/{note_id}` | Get one note belonging to the current user | Bearer token |
| `POST` | `/notes/upload` | Upload and ingest a note | Bearer token |
| `DELETE` | `/notes/{note_id}` | Delete a note | Bearer token |
| `POST` | `/chat/ask` | Retrieve note context and generate an answer | Bearer token |

Interactive API documentation is available at
`http://localhost:8000/docs` when the backend is running.

## Architecture

```text
React + Vite
    |
    | HTTP / JWT
    v
FastAPI
    |
    +-- Authentication and authorization
    +-- Note upload and text extraction
    +-- Chunking and embedding generation
    +-- Vector retrieval and answer generation
    |
    +--> PostgreSQL + pgvector
    +--> Ollama (local embeddings and chat models)
```

The backend follows a small router/service/model structure:

- `backend/app/routers/` contains HTTP endpoints for auth, notes, and chat.
- `backend/app/services/` contains ingestion, retrieval, and LLM logic.
- `backend/app/models/` contains SQLAlchemy models.
- `backend/app/schemas/` contains Pydantic request and response models.
- `backend/alembic/` contains database migrations.

## Prerequisites

- Python 3.14 or newer
- Node.js and npm
- Docker Desktop
- Ollama
- The Ollama models used by the application:

```powershell
ollama pull embeddinggemma
ollama pull qwen3.5:0.8b
```

## Local setup

### 1. Start PostgreSQL and pgAdmin

From the repository root:

```powershell
docker compose up -d
```

The compose file exposes:

- PostgreSQL at `localhost:5433`
- pgAdmin at `http://localhost:5050`

The development database is named `athena`. The credentials in
`docker-compose.yml` are for local development only.

### 2. Configure the backend

Create `backend/.env` and set values similar to:

```dotenv
database_url=postgresql+psycopg2://athena:devpassword@127.0.0.1:5433/athena
jwt_secret_key=replace-with-a-long-random-development-secret
jwt_algorithm=HS256
jwt_expire_minutes=60
llm_api_key=unused-by-the-current-ollama-provider
```

The current implementation uses Ollama locally. `llm_api_key` remains required
by the settings model because an alternative OpenAI-based service exists in the
source tree, but that service is not currently selected by the chat router.

Install the backend dependencies and apply migrations:

```powershell
cd backend
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

If `uv` is not installed, install it using the official uv installation
instructions, then repeat the commands above.

### 3. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally
`http://localhost:5173`.

The frontend currently calls the API at `http://localhost:8000`. If the API is
hosted elsewhere, update the Axios base URL in
`frontend/src/api/client.js`.

## Database

The migrations create:

- `users` for accounts.
- `notes` for uploaded note metadata and processing status.
- `note_chunks` for chunk text and vector embeddings.
Chat responses are intentionally not persisted. The active chat route returns
answers and citations only.

## Design review

For a deliberately small personal project, the current design is coherent:
the main user journey is clear (`register/login -> upload -> wait for ready ->
ask questions`), the router/service/model split is understandable, and the
warm paper/ink visual system is consistent with the notes concept. A major
redesign is not necessary.

The following are the design improvements worth making, in priority order:

1. **Make the LLM provider choice explicit.** The project contains an
   OpenAI/Anthropic-oriented service alongside the active Ollama service, while
   the router imports Ollama directly. Remove the unused provider or introduce a
   configuration-based provider interface so deployment behavior is unambiguous.
2. **Move ingestion out of the request thread.** PDF parsing and embedding calls
   happen synchronously during upload. A background job would keep the API
   responsive and make retries possible. The existing status field provides a
   good foundation for this.
3. **Strengthen configuration for non-development use.** Replace wildcard CORS,
   development credentials, and default-style secrets with environment-specific
   values. Add explicit upload size/type limits and validate empty or
   unextractable files.
4. **Improve operational feedback.** Replace `print` statements with structured
   logging, return a useful ingestion failure reason, and expose readiness
   information for the database and Ollama dependencies.
5. **Add a small test baseline.** Cover auth isolation, note upload/status
   transitions, retrieval ownership filtering, and the main frontend flows.
6. **Polish responsive and accessible behavior.** Add a mobile layout for the
   fixed sidebar, ensure focus-visible states and semantic labels for all
   controls, and provide a more descriptive citation interaction than
   non-clickable title chips.

These are mostly production-readiness improvements, not reasons to complicate
the current simple architecture.

## Current limitations

- Chat answers are generated synchronously and are not streamed.
- Only one file is uploaded per request.
- Supported ingestion is PDF and UTF-8 text; scanned PDFs need OCR, which is
  not included.
- Chat responses are not persisted between sessions.
- The frontend uses a fixed local API URL rather than a build-time environment
  variable.
- There are no automated backend or frontend tests in the repository.

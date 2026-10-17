# Athena

Athena is a small, private notes assistant. Users can create an account, upload
PDF or text notes, and ask questions whose answers are generated from the
uploaded notes with source citations.

The project is intentionally simple: it has one user type, a single frontend
and backend, and no teams, roles, or collaborative features.

## Technologies used

### Frontend

- React 18
- Vite
- JavaScript (ES modules)
- React Router
- Axios
- CSS

### Backend

- Python 3.14+
- FastAPI and Uvicorn
- SQLAlchemy
- Pydantic Settings
- Alembic
- PostgreSQL client via `psycopg2`
- JWT authentication with `python-jose`
- Password hashing with `bcrypt`
- Multipart file uploads with `python-multipart`
- PDF extraction with `pypdf`
- Text chunking with LangChain Text Splitters

### AI and retrieval

- Ollama for local language-model and embedding inference
- `embeddinggemma` for embeddings
- `qwen3.5:0.8b` for answer generation
- PostgreSQL with the `pgvector` extension for vector similarity search

### Development and infrastructure

- Docker Compose
- PostgreSQL 16 and pgAdmin
- `uv` for Python dependency and environment management
- npm for frontend dependency management

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

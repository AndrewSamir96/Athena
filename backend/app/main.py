from app.config import settings
from app.routers import auth, chat, notes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Athena Notes RAG API",
    version="0.1.0",
)

# --- 2. Middleware -------------------------------------------------------
# CORS lives here because it's transport-level (which *origins* are allowed
# to call this API at all), not request-level auth (which *user* is calling).
# That's why it's configured on the app object in main.py, not in core/security.py
# or core/deps.py — those two only ever run per-request, after CORS has
# already decided whether the browser is even allowed to send the request.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,   # from .env — no hardcoded URLs here
    allow_credentials=True,                 # required if you ever send cookies, harmless otherwise
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Routers ------------------------------------------------------------
# Each router owns one resource and its own url prefix (set inside the
# router file itself, e.g. APIRouter(prefix="/auth")) — main.py just mounts them.
app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(chat.router)

# --- 4. Top-level routes that don't belong to any one resource -------------
@app.get("/health", tags=["meta"])
def health():
    """Liveness check — hit this to confirm the server + config loaded correctly."""
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Hello World"}
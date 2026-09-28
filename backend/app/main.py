from app.config import settings
from app.routers import auth, chat, notes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Athena Notes RAG API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(chat.router)


@app.get("/health", tags=["meta"])
def health():
    """Liveness check — hit this to confirm the server + config loaded correctly."""
    print("[health] status check")
    return {"status": "ok"}


@app.get("/")
async def root():
    print("[root] request received")
    return {"message": "Hello World"}

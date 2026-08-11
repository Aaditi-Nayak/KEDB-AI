from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models.user import User
from app.models.known_error import KnownError
from app.models.category import Category

from app.routers import auth, known_error, category, dashboard, ai

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KEDB API",
    version="1.0.0",
    description="Known Error Database Backend"
)

# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Welcome to KEDB API"
    }

app.include_router(auth.router)
app.include_router(known_error.router)
app.include_router(category.router)
app.include_router(dashboard.router)
app.include_router(ai.router)
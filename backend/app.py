from fastapi import FastAPI
from backend.routes import quiz_routes
from backend.routes import upload_routes
from backend.routes import process_routes

# Database imports
from backend.database.connection import engine
from backend.models.db_models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Quiz Generator API")

# Attach the quiz routes (so it becomes /quiz/generate)
app.include_router(quiz_routes.router, prefix="/quiz", tags=["Quiz"])

app.include_router(
    upload_routes.router,
    prefix="/api",
    tags=["Upload"]
)

app.include_router(
    process_routes.router,
    prefix="/api",
    tags=["Process"]
)

@app.get("/")
def home():
    return {"message": "AI Quiz Generator Backend is running!"}
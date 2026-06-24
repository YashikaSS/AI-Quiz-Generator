from fastapi import FastAPI
from backend.routes import quiz_routes

app = FastAPI(title="AI Quiz Generator API")

# Attach the quiz routes (so it becomes /quiz/generate)
app.include_router(quiz_routes.router, prefix="/quiz", tags=["Quiz"])

@app.get("/")
def home():
    return {"message": "AI Quiz Generator Backend is running!"}
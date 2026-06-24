from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.quiz_service import generate_quiz
from backend.models.schemas import QuizGenerationResponse

# Create the router for the FastAPI app
router = APIRouter()

# Define what the frontend needs to send to this API
class QuizRequest(BaseModel):
    text: str
    num_questions: int = 5

@router.post("/generate", response_model=QuizGenerationResponse)
async def create_quiz_endpoint(request: QuizRequest):
    """
    API Endpoint: Receives text from the frontend, runs Member 5's AI quiz generator, 
    and returns the structured JSON quiz.
    """
    print("Received request to generate quiz...")
    
    # Call Member 5's completed service function
    quiz_data = generate_quiz(content_text=request.text, num_questions=request.num_questions)
    
    if not quiz_data:
        # If the AI fails or returns bad JSON, send a 500 error to the frontend
        raise HTTPException(status_code=500, detail="AI Model failed to generate a valid quiz.")
    
    # (Optional) Member 6 will later add code here to save quiz_data to the MySQL Database
    
    return quiz_data
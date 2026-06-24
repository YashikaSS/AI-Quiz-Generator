from pydantic import BaseModel, Field
from typing import List

class MCQItem(BaseModel):
    question_num: int = Field(..., description="Question number")
    question: str = Field(..., description="The MCQ question text")
    options: List[str] = Field(..., description="Exactly 4 options")
    correct_answer: str = Field(..., description="The correct option string")
    explanation: str = Field(..., description="Why this answer is correct")

class QuizGenerationResponse(BaseModel):
    quiz_title: str = Field(..., description="Generated title for the quiz")
    questions: List[MCQItem] = Field(..., description="List of MCQ items")
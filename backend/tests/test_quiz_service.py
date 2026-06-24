import pytest
from unittest.mock import patch
from backend.services.quiz_service import generate_quiz
from backend.models.schemas import QuizGenerationResponse

# We use @patch to intercept the call to 'generate_text' inside your quiz_service
@patch("backend.services.quiz_service.generate_text")
def test_generate_quiz_success(mock_generate_text):
    """Tests if the service correctly parses a valid JSON response from the AI."""
    
    # 1. Simulate a perfect JSON response from the AI
    mock_generate_text.return_value = """
    ```json
    {
      "quiz_title": "Biology Basics",
      "questions": [
        {
          "question_num": 1,
          "question": "What is the powerhouse of the cell?",
          "options": ["Nucleus", "Mitochondria", "Ribosome", "Membrane"],
          "correct_answer": "Mitochondria",
          "explanation": "Mitochondria generate most of the cell's supply of adenosine triphosphate (ATP)."
        }
      ]
    }
    ```
    """

    # 2. Run your actual function
    sample_text = "Mitochondria are often referred to as the powerhouse of the cell."
    result = generate_quiz(content_text=sample_text, num_questions=1)

    # 3. Assertions to prove Member 5's code works perfectly
    assert result is not None
    assert isinstance(result, QuizGenerationResponse)
    assert result.quiz_title == "Biology Basics"
    assert len(result.questions) == 1
    assert result.questions[0].correct_answer == "Mitochondria"
    assert len(result.questions[0].options) == 4

@patch("backend.services.quiz_service.generate_text")
def test_generate_quiz_invalid_json(mock_generate_text):
    """Tests if the service safely handles a bad AI response that isn't JSON."""
    
    # 1. Simulate the AI going rogue and returning conversational text instead of JSON
    mock_generate_text.return_value = "Sure! Here is your quiz. Question 1: What is biology? A) Science B) Math..."

    # 2. Run your function
    sample_text = "Some random text about science."
    result = generate_quiz(content_text=sample_text, num_questions=1)

    # 3. The service should catch the JSONDecodeError and return None safely, not crash
    assert result is None
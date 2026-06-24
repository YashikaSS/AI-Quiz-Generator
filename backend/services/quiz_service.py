import json
import logging
from typing import Optional
from backend.models.schemas import QuizGenerationResponse
# Import the exact function from the shared llm_service
from backend.services.llm_service import generate_text 

logger = logging.getLogger(__name__)

def generate_quiz(content_text: str, num_questions: int = 5) -> Optional[QuizGenerationResponse]:
    """Generates MCQs with explanations from raw text using the shared LLM service."""
    
    # Combine instructions and content into a single prompt for generate_text()
    full_prompt = (
        "You are an expert quiz generator. Your task is to analyze the provided text "
        "and output a JSON quiz. Respond ONLY with raw JSON. Do not include markdown formatting like ```json.\n\n"
        "REQUIRED JSON SCHEMA:\n"
        "{\n"
        '  "quiz_title": "string",\n'
        '  "questions": [\n'
        "    {\n"
        '      "question_num": int,\n'
        '      "question": "string",\n'
        '      "options": ["A", "B", "C", "D"],\n'
        '      "correct_answer": "exact string match of correct option",\n'
        '      "explanation": "why it is correct"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        f"Generate a {num_questions}-question quiz based on this text:\n"
        "--- START TEXT ---\n"
        f"{content_text}\n"
        "--- END TEXT ---"
    )

    try:
        # Call the shared function. Give it plenty of tokens to output a full JSON string.
        raw_output = generate_text(full_prompt, max_new_tokens=1024)
        
        # Clean potential markdown formatting from the AI response
        clean_json = raw_output.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
            
        parsed_data = json.loads(clean_json.strip())
        return QuizGenerationResponse(**parsed_data)

    except RuntimeError as e:
        # This catches the error if USE_REAL_LLM is set to false
        logger.error(f"LLM Service Error: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI output as JSON: {e}\nRaw Output: {raw_output}")
        return None
    except Exception as e:
        # Import traceback to show us the exact line that crashed
        import traceback
        print("\n--- DETAILED ERROR TRACE ---")
        traceback.print_exc()
        print("----------------------------\n")
        
        logger.error(f"Quiz generation failed: {e}")
        return None
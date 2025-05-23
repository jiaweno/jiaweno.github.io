# backend/app/core/openai_utils.py
import openai
import json
import logging
from app.core.config import settings
from app.models.learning_models import GeneratedQuestion, QuestionType, QuestionOption # For type hinting if needed
from typing import List, Optional # Added List and Optional

logger = logging.getLogger(__name__)

# Ensure OpenAI API key is set (already done in previous steps for embeddings)
# openai.api_key = settings.OPENAI_API_KEY # This is typically done when the client is initialized

async def generate_questions_with_gpt(content: str, num_mcq: int = 2, num_short_answer: int = 1, context_title: str = "the provided content") -> Optional[List[GeneratedQuestion]]:
    if not settings.OPENAI_API_KEY:
        logger.error("OpenAI API key not configured. Cannot generate questions.")
        return None

    prompt = f"""
    Based on the following content titled "{context_title}":
    ---
    {content[:4000]}  # Limit context length to manage token usage for the prompt itself
    ---
    
    Please generate a quiz with the following questions:
    - {num_mcq} multiple-choice questions. Each multiple-choice question should have 4 options, with one clearly correct answer.
    - {num_short_answer} short-answer questions that require a brief textual response.

    Format the output as a JSON list of objects. Each object should represent a single question and have the following structure:
    {{
        "question_text": "The question text...",
        "question_type": "multiple_choice" | "short_answer",
        "options": [ {{ "text": "Option A text", "is_correct": false/true }}, ... ],  // (Only for multiple_choice)
        // "correct_answer_text": "The concise correct answer for short_answer or true_false types" // (Optional, especially if answer is in options for MCQ)
    }}

    Ensure the JSON is well-formed. Provide only the JSON list, no other text or explanations.
    Example for a multiple-choice question option: {{"text": "Option text", "is_correct": true}}
    Example for a short-answer question: {{"question_text": "What is X?", "question_type": "short_answer"}}
    """

    try:
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY) # Use Async client for FastAPI
        chat_completion = await client.chat.completions.create(
            model="gpt-4-turbo-preview", # Or "gpt-3.5-turbo" for faster/cheaper, or specific GPT-4 model
            # response_format={ "type": "json_object" }, # For newer models that support JSON mode reliably
            messages=[
                {"role": "system", "content": "You are an AI assistant that generates educational quiz questions based on provided content. Output ONLY the JSON as requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5, # Adjust for creativity vs. determinism
            max_tokens=1500 # Adjust based on expected output size
        )
        
        response_content = chat_completion.choices[0].message.content
        if not response_content:
            logger.error("GPT-4 returned empty content for quiz generation.")
            return None

        logger.debug(f"Raw GPT response for quiz gen: {response_content}")
        
        # Try to parse the JSON from the response. GPT might sometimes include markdown ```json ... ```
        json_response_cleaned = response_content.strip()
        if json_response_cleaned.startswith("```json"):
            json_response_cleaned = json_response_cleaned[7:]
        if json_response_cleaned.endswith("```"):
            json_response_cleaned = json_response_cleaned[:-3]
        
        questions_data = json.loads(json_response_cleaned)
        
        # Validate and parse into Pydantic models (basic validation example)
        parsed_questions = []
        for q_data in questions_data:
            # Basic validation, can be more robust with Pydantic parsing directly if format is strict
            if not all(k in q_data for k in ['question_text', 'question_type']):
                logger.warning(f"Skipping question due to missing fields: {q_data}")
                continue
            
            # Map question_type string to Enum
            try:
                q_type = QuestionType(q_data["question_type"])
            except ValueError:
                logger.warning(f"Skipping question due to invalid question_type: {q_data.get('question_type')}")
                continue

            options_list = None
            if q_type == QuestionType.MULTIPLE_CHOICE:
                if not q_data.get("options") or not isinstance(q_data["options"], list):
                    logger.warning(f"Skipping MCQ due to missing/invalid options: {q_data}")
                    continue
                options_list = [QuestionOption(**opt) for opt in q_data["options"]]
                # Ensure at least one option is correct for MCQs
                if not any(opt.is_correct for opt in options_list):
                    logger.warning(f"Skipping MCQ as no correct option was marked: {q_data}")
                    continue

            parsed_questions.append(
                GeneratedQuestion(
                    question_text=q_data["question_text"],
                    question_type=q_type,
                    options=options_list
                    # correct_answer_text=q_data.get("correct_answer_text")
                )
            )
        return parsed_questions

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response from GPT-4 for quiz generation: {e}. Response was: {response_content if 'response_content' in locals() else 'response_content not available'}")
        return None
    except Exception as e:
        logger.error(f"Error generating questions with GPT-4: {e}")
        return None

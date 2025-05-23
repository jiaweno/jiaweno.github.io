# backend/app/api/v1/endpoints/quiz_attempts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from typing import List, Any # Added Any

from app.db.session import get_db
from app.models.user_models import User as PydanticUser
from app.models.learning_models import (
    QuizAttemptResponse, QuizAttemptResultResponse, QuizSubmissionPayload, 
    QuestionForAttemptResponse, AttemptedQuestionAnswerResponse, QuestionOption, QuestionType, # Added QuestionType
    UserAnswerData # For type hint if needed
)
from app.services import quiz_attempt_service
from app.core.dependencies import get_current_active_user
from app.db.models_sqlalchemy import QuizAttempt as QuizAttemptModel

router = APIRouter()

def map_attempt_to_start_response(attempt_model: QuizAttemptModel) -> QuizAttemptResponse:
    questions_for_display: List[QuestionForAttemptResponse] = []
    # Ensure questions are sorted by their creation order or an explicit sequence if available
    # For now, assuming the order from the database relationship is stable (usually by PK or insertion order)
    # If an explicit order is needed, the AQA_Model should have a sequence field.
    sorted_attempted_questions = sorted(attempt_model.attempted_questions, key=lambda x: x.id)


    for aqa in sorted_attempted_questions:
        options_for_display = None
        if aqa.options and aqa.question_type == QuestionType.MULTIPLE_CHOICE: # Use QuestionType enum
            # Strip 'is_correct' from options for the user
            options_for_display = [{"text": opt['text']} for opt in aqa.options]
        
        questions_for_display.append(
            QuestionForAttemptResponse(
                attempted_question_answer_id=aqa.id, # This is crucial for submission
                question_text=aqa.question_text,
                question_type=aqa.question_type,
                options=options_for_display
            )
        )
    
    return QuizAttemptResponse(
        id=attempt_model.id,
        user_id=attempt_model.user_id,
        source_learning_path_id=attempt_model.source_learning_path_id,
        source_knowledge_point_id=attempt_model.source_knowledge_point_id,
        status=attempt_model.status,
        score=attempt_model.score,
        attempted_at=attempt_model.attempted_at,
        questions_for_attempt=questions_for_display
    )
        
def map_attempt_to_result_response(attempt_model: QuizAttemptModel) -> QuizAttemptResultResponse:
    # Sort questions if there's a specific order, e.g., by ID or a sequence number if added
    sorted_attempted_questions = sorted(attempt_model.attempted_questions, key=lambda x: x.id)
    
    return QuizAttemptResultResponse(
        id=attempt_model.id,
        user_id=attempt_model.user_id,
        source_learning_path_id=attempt_model.source_learning_path_id,
        source_knowledge_point_id=attempt_model.source_knowledge_point_id,
        status=attempt_model.status,
        score=attempt_model.score,
        attempted_at=attempt_model.attempted_at,
        questions_with_answers=[AttemptedQuestionAnswerResponse.model_validate(aqa) for aqa in sorted_attempted_questions]
    )


@router.post("/start/kp/{kp_id}", response_model=QuizAttemptResponse)
async def start_attempt_for_kp(
    kp_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
) -> Any: # Changed to Any
    attempt = await quiz_attempt_service.start_quiz_attempt(db, user_id=current_user.id, source_id=kp_id, source_type="kp")
    if not attempt:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not start quiz attempt for Knowledge Point.")
    return map_attempt_to_start_response(attempt)


@router.post("/start/lp/{lp_id}", response_model=QuizAttemptResponse)
async def start_attempt_for_lp(
    lp_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
) -> Any: # Changed to Any
    attempt = await quiz_attempt_service.start_quiz_attempt(db, user_id=current_user.id, source_id=lp_id, source_type="lp")
    if not attempt:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not start quiz attempt for Learning Path.")
    return map_attempt_to_start_response(attempt)


@router.post("/{attempt_id}/submit", response_model=QuizAttemptResultResponse)
async def submit_attempt_answers( # Changed to async to align with potential async service calls in future
    attempt_id: uuid.UUID,
    payload: QuizSubmissionPayload,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
) -> Any: # Changed to Any
    result = quiz_attempt_service.submit_quiz_answers(db, attempt_id=attempt_id, user_id=current_user.id, submitted_answers=payload.answers)
    if not result:
        # Consider more specific error codes (e.g., 403 if already submitted and not allowed to re-submit)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz attempt not found or already submitted.")
    return map_attempt_to_result_response(result)


@router.get("/{attempt_id}/result", response_model=QuizAttemptResultResponse)
async def get_attempt_result( # Changed to async
    attempt_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
) -> Any: # Changed to Any
    result = quiz_attempt_service.get_quiz_attempt_results(db, attempt_id=attempt_id, user_id=current_user.id)
    if not result : # Check if result exists
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz attempt result not found.")
    if result.status != QuizAttemptStatus.COMPLETED: # Check if attempt is completed
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz attempt not yet completed.")
    return map_attempt_to_result_response(result)

@router.get("/", response_model=List[QuizAttemptResultResponse]) # Or a simpler list item response
async def list_my_attempts( # Changed to async
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 10
) -> Any: # Changed to Any
    attempts = quiz_attempt_service.list_user_quiz_attempts(db, user_id=current_user.id, skip=skip, limit=limit)
    return [map_attempt_to_result_response(att) for att in attempts]

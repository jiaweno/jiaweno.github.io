# backend/app/api/v1/endpoints/quizzes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.db.session import get_db
from app.models.user_models import User as PydanticUser # For auth dependency
from app.models.learning_models import GeneratedQuizResponse
from app.services import quiz_service 
from app.core.dependencies import get_current_active_user # Auth

router = APIRouter()

@router.post("/generate/kp/{kp_id}", response_model=GeneratedQuizResponse)
async def generate_quiz_from_kp(
    kp_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user) # Ensure user is authenticated
):
    # Optional: Add logic here to check if current_user has access to this kp_id
    # (e.g., if KPs are tied to user-owned documents)
    # For now, any authenticated user can attempt to generate a quiz for any KP.
    
    quiz_data = await quiz_service.generate_quiz_for_knowledge_point(db, kp_id=kp_id)
    if not quiz_data:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate quiz for Knowledge Point.")
    return quiz_data

@router.post("/generate/lp/{lp_id}", response_model=GeneratedQuizResponse)
async def generate_quiz_from_lp(
    lp_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
):
    # Optional: Add logic here to check if current_user owns or has access to this lp_id
    # This can be done within the quiz_service or learning_path_service when fetching the LP.
    # For now, the learning_path_service's get_learning_path_by_id does not enforce ownership
    # if user_id is not passed, but for quiz generation, it's a good check to have.
    # However, the current quiz_service.generate_quiz_for_learning_path doesn't pass user_id.
    # This means any authenticated user can generate a quiz for any LP ID.
    # If Learning Paths are user-specific, this should be tightened.
    # (The learning_path_service.get_learning_path_by_id in the LP CRUD ops does check user_id)

    quiz_data = await quiz_service.generate_quiz_for_learning_path(db, lp_id=lp_id)
    if not quiz_data:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate quiz for Learning Path.")
    return quiz_data

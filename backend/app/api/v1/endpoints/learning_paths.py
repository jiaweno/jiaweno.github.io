# backend/app/api/v1/endpoints/learning_paths.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any # Ensure List, Any are imported
import uuid # Ensure uuid is imported

from app.db.session import get_db
from app.models.user_models import User as PydanticUser
from app.models.learning_models import LearningPathCreate, LearningPathUpdate, LearningPathResponse, KnowledgePointForPath
from app.services import learning_path_service
from app.core.dependencies import get_current_active_user
from app.db.models_sqlalchemy import LearningPath as LPModel # For type hinting service returns

router = APIRouter()

def map_lp_model_to_response(lp_model: LPModel) -> LearningPathResponse:
    # Helper to map SQLAlchemy model to Pydantic response, especially for nested KPs
    kps_for_response = []
    # Ensure associations are loaded and sorted; the relationship already sorts by sequence_order
    for assoc in lp_model.knowledge_point_associations: 
        if assoc.knowledge_point: # Ensure KP is loaded (due to joinedload in service)
            kps_for_response.append(
                KnowledgePointForPath(
                    id=assoc.knowledge_point.id,
                    title=assoc.knowledge_point.title,
                    sequence_order=assoc.sequence_order
                )
            )
    
    return LearningPathResponse(
        id=lp_model.id,
        user_id=lp_model.user_id,
        title=lp_model.title,
        description=lp_model.description,
        created_at=lp_model.created_at,
        updated_at=lp_model.updated_at,
        knowledge_points=kps_for_response
    )

@router.post("/", response_model=LearningPathResponse, status_code=status.HTTP_201_CREATED)
def create_new_learning_path(
    path_in: LearningPathCreate,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
) -> Any:
    try:
        created_lp_model = learning_path_service.create_learning_path(db, path_in=path_in, user_id=current_user.id)
        # Re-fetch to ensure all relationships are loaded for the response model
        populated_lp = learning_path_service.get_learning_path_by_id(db, path_id=created_lp_model.id, user_id=current_user.id)
        if not populated_lp: 
            # This should ideally not happen if creation was successful
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve created learning path for response.")
        return map_lp_model_to_response(populated_lp)
    except ValueError as ve: # Catch specific errors like KP not found from service
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.get("/", response_model=List[LearningPathResponse])
def list_user_learning_paths(
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 10 # Changed default to 10
) -> Any:
    lp_models = learning_path_service.get_learning_paths_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return [map_lp_model_to_response(lp) for lp in lp_models]


@router.get("/{path_id}", response_model=LearningPathResponse)
def get_single_learning_path(
    path_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user) 
) -> Any:
    lp_model = learning_path_service.get_learning_path_by_id(db, path_id=path_id, user_id=current_user.id)
    if not lp_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning Path not found or not owned by user.")
    return map_lp_model_to_response(lp_model)

@router.put("/{path_id}", response_model=LearningPathResponse)
def update_existing_learning_path(
    path_id: uuid.UUID,
    path_update_data: LearningPathUpdate,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
) -> Any:
    try:
        updated_lp_model = learning_path_service.update_learning_path(db, path_id=path_id, path_update_data=path_update_data, user_id=current_user.id)
        if not updated_lp_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning Path not found or failed to update.")
        # The service's update_learning_path now re-fetches with relationships
        return map_lp_model_to_response(updated_lp_model)
    except ValueError as ve: # Catch specific errors like KP not found from service
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_learning_path(
    path_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
):
    success = learning_path_service.delete_learning_path(db, path_id=path_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning Path not found or not owned by user.")
    return None

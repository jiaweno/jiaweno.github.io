# backend/app/services/learning_path_service.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import delete # For deleting associations

from app.db.models_sqlalchemy import LearningPath as LPModel, LearningPathKnowledgePoint as LPKPModel, KnowledgePoint as KPModel
from app.models.learning_models import LearningPathCreate, LearningPathUpdate # LearningPathKPDetail is used within these
import uuid

def create_learning_path(db: Session, path_in: LearningPathCreate, user_id: uuid.UUID) -> LPModel:
    db_lp = LPModel(
        user_id=user_id,
        title=path_in.title,
        description=path_in.description
    )
    db.add(db_lp)
    db.flush() # Flush to get db_lp.id for associations

    associations = []
    if path_in.knowledge_points: # Check if there are any KPs to add
        for kp_detail in path_in.knowledge_points:
            # Optional: Check if KP exists
            kp_exists = db.query(KPModel).filter(KPModel.id == kp_detail.knowledge_point_id).first()
            if not kp_exists:
                # Handle error: KP not found. This might involve rolling back the transaction
                # or collecting errors to return. For now, raise an exception.
                # This should ideally be part of validation before this service function.
                raise ValueError(f"KnowledgePoint with ID {kp_detail.knowledge_point_id} not found.")
            
            assoc = LPKPModel(
                learning_path_id=db_lp.id,
                knowledge_point_id=kp_detail.knowledge_point_id,
                sequence_order=kp_detail.sequence_order
            )
            associations.append(assoc)
        db.add_all(associations)
       
    db.commit()
    db.refresh(db_lp)
    # To ensure relationships are loaded for the returned object, especially if mapped later
    # It's often better to re-fetch or rely on the ORM's configured lazy/eager loading.
    # For now, the refreshed db_lp will have its direct attributes.
    # The relationships will be loaded when accessed (lazy) or if configured for eager load.
    return db_lp

def get_learning_path_by_id(db: Session, path_id: uuid.UUID, user_id: Optional[uuid.UUID] = None) -> Optional[LPModel]:
    query = db.query(LPModel).options(
        joinedload(LPModel.knowledge_point_associations).joinedload(LPKPModel.knowledge_point)
    ).filter(LPModel.id == path_id)
    if user_id: # If user_id is provided, filter by owner
        query = query.filter(LPModel.user_id == user_id)
    return query.first()

def get_learning_paths_by_user(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[LPModel]:
    # For list view, we might not always need full details.
    # The current response model (LearningPathResponse) expects knowledge_points.
    # If a simpler list view is desired later, this query might not need joinedload.
    return db.query(LPModel).filter(LPModel.user_id == user_id)\
        .options(joinedload(LPModel.knowledge_point_associations).joinedload(LPKPModel.knowledge_point))\
        .order_by(LPModel.created_at.desc()).offset(skip).limit(limit).all()

def update_learning_path(db: Session, path_id: uuid.UUID, path_update_data: LearningPathUpdate, user_id: uuid.UUID) -> Optional[LPModel]:
    # Fetch existing path, ensuring user ownership
    db_lp = db.query(LPModel).filter(LPModel.id == path_id, LPModel.user_id == user_id).first()
    if not db_lp:
        return None

    if path_update_data.title is not None:
        db_lp.title = path_update_data.title
    if path_update_data.description is not None:
        db_lp.description = path_update_data.description

    if path_update_data.knowledge_points is not None:
        # Clear existing associations for this learning path
        # Using ORM cascade delete for LearningPath.knowledge_point_associations
        # is an alternative, but explicit delete gives more control or can be safer.
        # The current model uses cascade="all, delete-orphan" on the relationship,
        # so assigning a new list to db_lp.knowledge_point_associations *might* work
        # if the ORM handles the diff correctly. Explicit delete is safer.
        
        # Delete existing associations first
        db.query(LPKPModel).filter(LPKPModel.learning_path_id == path_id).delete(synchronize_session=False)
        # db.flush() # Ensure deletes are processed before adding new ones if needed

        new_associations = []
        for kp_detail in path_update_data.knowledge_points:
            # Optional: Check if KP exists
            kp_exists = db.query(KPModel).filter(KPModel.id == kp_detail.knowledge_point_id).first()
            if not kp_exists:
                raise ValueError(f"KnowledgePoint with ID {kp_detail.knowledge_point_id} not found during update.")

            assoc = LPKPModel(
                learning_path_id=path_id, # Use path_id directly
                knowledge_point_id=kp_detail.knowledge_point_id,
                sequence_order=kp_detail.sequence_order
            )
            new_associations.append(assoc)
        db.add_all(new_associations)
       
    db.commit()
    db.refresh(db_lp)
    # Re-fetch with relationships to ensure the returned object is fully populated for the response model
    return get_learning_path_by_id(db, path_id=path_id, user_id=user_id)


def delete_learning_path(db: Session, path_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    db_lp = db.query(LPModel).filter(LPModel.id == path_id, LPModel.user_id == user_id).first()
    if db_lp:
        db.delete(db_lp) # Cascade="all, delete-orphan" on knowledge_point_associations will handle LPKPModel records
        db.commit()
        return True
    return False

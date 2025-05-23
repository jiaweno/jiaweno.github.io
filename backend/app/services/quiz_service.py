# backend/app/services/quiz_service.py
import logging
from typing import List, Optional # Ensure List, Optional are imported
from sqlalchemy.orm import Session
import uuid

from app.db.models_sqlalchemy import KnowledgePoint as KPModel # LearningPath as LPModel is not directly used here but could be
from app.models.learning_models import GeneratedQuestion, GeneratedQuizResponse # Ensure GeneratedQuestion is imported
from app.core.openai_utils import generate_questions_with_gpt 
# To avoid circular dependency, we might need to import the specific service function
# or ensure services are structured to prevent this (e.g. using a central service registry or dependency injection)
# For now, direct import for learning_path_service.get_learning_path_by_id if quiz_service is imported by learning_path_service
# from app.services.learning_path_service import get_learning_path_by_id as get_lp_by_id_from_lp_service

logger = logging.getLogger(__name__)

async def generate_quiz_for_knowledge_point(db: Session, kp_id: uuid.UUID) -> Optional[GeneratedQuizResponse]:
    kp = db.query(KPModel).filter(KPModel.id == kp_id).first()
    if not kp:
        logger.warning(f"Knowledge Point {kp_id} not found for quiz generation.")
        return None

    # Assuming kp.document relationship is available if needed for context_title
    # For now, just using KP title.
    context_title = f"Knowledge Point: {kp.title or 'Untitled'}"
    
    questions = await generate_questions_with_gpt(content=kp.content_chunk, context_title=context_title)
    if not questions:
        return None
    
    return GeneratedQuizResponse(
        title=f"Quiz for: {kp.title or 'Knowledge Point'}",
        knowledge_point_id=kp_id,
        questions=questions
    )

async def generate_quiz_for_learning_path(db: Session, lp_id: uuid.UUID) -> Optional[GeneratedQuizResponse]:
    # This import is placed here to minimize potential circular import issues at module load time.
    # A better solution might be DI or restructuring services.
    from app.services.learning_path_service import get_learning_path_by_id as get_lp_by_id_from_lp_service
    
    lp_with_kps = get_lp_by_id_from_lp_service(db, path_id=lp_id) 

    if not lp_with_kps or not lp_with_kps.knowledge_point_associations:
        logger.warning(f"Learning Path {lp_id} not found or has no knowledge points.")
        return None

    combined_content = ""
    # KPs are ordered by sequence_order due to relationship definition in LearningPath model
    for i, assoc in enumerate(lp_with_kps.knowledge_point_associations):
        if i >= 3: # Limit to first 3 KPs for content combination
            logger.info(f"Limiting combined content to first 3 KPs for Learning Path {lp_id}.")
            break 
        # Ensure knowledge_point is loaded (it should be due to joinedload in get_learning_path_by_id)
        if assoc.knowledge_point:
            kp_content = assoc.knowledge_point.content_chunk
            combined_content += f"Content from '{assoc.knowledge_point.title or f'Chunk {i+1}'}':\n{kp_content}\n\n---\n\n"
        else:
            logger.warning(f"Knowledge point not loaded for association in LP {lp_id}, sequence {assoc.sequence_order}")
       
    if not combined_content.strip():
        logger.warning(f"No content could be combined from KPs for Learning Path {lp_id}.")
        return None

    questions = await generate_questions_with_gpt(
        content=combined_content, 
        context_title=f"Learning Path: {lp_with_kps.title}", 
        num_mcq=5, # Example: more MCQs for a longer path quiz
        num_short_answer=2
    )
    if not questions:
        return None

    return GeneratedQuizResponse(
        title=f"Quiz for Learning Path: {lp_with_kps.title}",
        learning_path_id=lp_id,
        questions=questions
    )

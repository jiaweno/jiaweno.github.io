# backend/app/services/quiz_attempt_service.py
import logging
from typing import List, Optional, Tuple # Ensure Tuple is imported if used
import uuid
from sqlalchemy.orm import Session, selectinload 

from app.db.models_sqlalchemy import QuizAttempt as QuizAttemptModel, AttemptedQuestionAnswer as AQA_Model
# KPModel and LPModel are not directly used here unless for validation not covered by quiz_service
# from app.db.models_sqlalchemy import KnowledgePoint as KPModel, LearningPath as LPModel
from app.models.learning_models import (
    QuizAttemptStatus, GeneratedQuestion, UserAnswerData, UserSubmittedAnswer, QuestionType, QuestionOption
)
from app.services import quiz_service # To get generated questions

logger = logging.getLogger(__name__)

async def start_quiz_attempt(
    db: Session, user_id: uuid.UUID, 
    source_id: uuid.UUID, 
    source_type: str # "kp" or "lp"
) -> Optional[QuizAttemptModel]:
    
    generated_quiz_response = None
    source_kp_id = None
    source_lp_id = None

    if source_type == "kp":
        generated_quiz_response = await quiz_service.generate_quiz_for_knowledge_point(db, kp_id=source_id)
        source_kp_id = source_id
    elif source_type == "lp":
        generated_quiz_response = await quiz_service.generate_quiz_for_learning_path(db, lp_id=source_id)
        source_lp_id = source_id
    else:
        logger.error(f"Invalid source_type for starting quiz: {source_type}")
        return None

    if not generated_quiz_response or not generated_quiz_response.questions:
        logger.error(f"Failed to generate questions for {source_type} ID {source_id}.")
        return None

    # Create QuizAttempt
    db_quiz_attempt = QuizAttemptModel(
        user_id=user_id,
        source_knowledge_point_id=source_kp_id,
        source_learning_path_id=source_lp_id,
        status=QuizAttemptStatus.IN_PROGRESS
    )
    db.add(db_quiz_attempt)
    db.flush() # To get db_quiz_attempt.id

    # Create AttemptedQuestionAnswer entries
    attempted_questions_list = []
    for q_gen in generated_quiz_response.questions:
        options_dict_list = None
        if q_gen.options:
            options_dict_list = [opt.model_dump() for opt in q_gen.options]

        aqa = AQA_Model(
            quiz_attempt_id=db_quiz_attempt.id,
            question_text=q_gen.question_text,
            question_type=q_gen.question_type,
            options=options_dict_list 
        )
        attempted_questions_list.append(aqa)
    
    db.add_all(attempted_questions_list)
    db.commit()
    db.refresh(db_quiz_attempt)
    # Eager load attempted_questions for the response
    # This can be done here or when fetching for response mapping
    db_quiz_attempt = db.query(QuizAttemptModel).options(
        selectinload(QuizAttemptModel.attempted_questions)
    ).filter(QuizAttemptModel.id == db_quiz_attempt.id).first()
    
    return db_quiz_attempt


def submit_quiz_answers(
    db: Session, attempt_id: uuid.UUID, user_id: uuid.UUID, submitted_answers: List[UserSubmittedAnswer]
) -> Optional[QuizAttemptModel]:
    
    db_quiz_attempt = db.query(QuizAttemptModel).options(
        selectinload(QuizAttemptModel.attempted_questions)
    ).filter(QuizAttemptModel.id == attempt_id, QuizAttemptModel.user_id == user_id).first()

    if not db_quiz_attempt:
        logger.warning(f"Quiz attempt {attempt_id} not found for user {user_id}.")
        return None
    if db_quiz_attempt.status == QuizAttemptStatus.COMPLETED:
        logger.warning(f"Quiz attempt {attempt_id} has already been completed.")
        return db_quiz_attempt 

    total_score = 0.0
    # max_possible_score = 0.0 # Not strictly needed for this implementation, but good for percentage

    for submitted_ans in submitted_answers:
        attempted_q = next((q for q in db_quiz_attempt.attempted_questions if q.id == submitted_ans.attempted_question_answer_id), None)
        if not attempted_q:
            logger.warning(f"AttemptedQuestionAnswer ID {submitted_ans.attempted_question_answer_id} not found in attempt {attempt_id}. Skipping.")
            continue

        attempted_q.submitted_answer_data = submitted_ans.submitted_answer_data.model_dump() 
        
        is_q_correct = False
        q_score = 0.0
        question_points = 10.0 # Default points
        # max_possible_score += question_points

        if attempted_q.question_type == QuestionType.MULTIPLE_CHOICE:
            correct_option_index = -1
            original_options = [QuestionOption(**opt_dict) for opt_dict in attempted_q.options] if attempted_q.options else []

            for i, opt in enumerate(original_options):
                if opt.is_correct:
                    correct_option_index = i
                    break
            
            if submitted_ans.submitted_answer_data.selected_option_index is not None and \
               submitted_ans.submitted_answer_data.selected_option_index == correct_option_index:
                is_q_correct = True
                q_score = question_points
        
        # TODO: Add scoring for SHORT_ANSWER and TRUE_FALSE
        # Example for TRUE_FALSE (assuming answer_text is "true" or "false")
        elif attempted_q.question_type == QuestionType.TRUE_FALSE:
            # Assuming options list for TRUE_FALSE stores the correct boolean answer text in the first option marked is_correct
            correct_answer_str = ""
            original_options = [QuestionOption(**opt_dict) for opt_dict in attempted_q.options] if attempted_q.options else []
            for opt in original_options:
                if opt.is_correct:
                    correct_answer_str = opt.text.lower() # e.g. "true" or "false"
                    break
            if submitted_ans.submitted_answer_data.answer_text and \
               submitted_ans.submitted_answer_data.answer_text.lower() == correct_answer_str:
                is_q_correct = True
                q_score = question_points


        attempted_q.is_correct = is_q_correct
        attempted_q.score = q_score
        total_score += q_score
    
    db_quiz_attempt.score = total_score 
    db_quiz_attempt.status = QuizAttemptStatus.COMPLETED
    db.commit()
    db.refresh(db_quiz_attempt)
    # Eager load for response
    db_quiz_attempt = db.query(QuizAttemptModel).options(
        selectinload(QuizAttemptModel.attempted_questions)
    ).filter(QuizAttemptModel.id == db_quiz_attempt.id).first()
    return db_quiz_attempt

def get_quiz_attempt_results(db: Session, attempt_id: uuid.UUID, user_id: uuid.UUID) -> Optional[QuizAttemptModel]:
    return db.query(QuizAttemptModel).options(
        selectinload(QuizAttemptModel.attempted_questions)
    ).filter(QuizAttemptModel.id == attempt_id, QuizAttemptModel.user_id == user_id).first()

def list_user_quiz_attempts(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 10) -> List[QuizAttemptModel]:
    return db.query(QuizAttemptModel).options(
        selectinload(QuizAttemptModel.attempted_questions) # Eager load for list view if details are needed
    ).filter(QuizAttemptModel.user_id == user_id).order_by(QuizAttemptModel.attempted_at.desc()).offset(skip).limit(limit).all()

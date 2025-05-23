from pydantic import BaseModel
from typing import Optional, List, Dict, Any # Ensure List, Optional are imported
import uuid # Ensure uuid is imported
from datetime import datetime # Ensure datetime is imported
from enum import Enum # Added for QuestionType

# --- KnowledgePoint Models (ensure they are suitable for nesting) ---
class KnowledgePointBasePydantic(BaseModel): 
    document_id: uuid.UUID
    content_chunk: str 
    title: Optional[str] = None 
    sequence_in_document: Optional[int] = None

class KnowledgePointCreatePydantic(KnowledgePointBasePydantic): 
    pass

class KnowledgePointInDBBasePydantic(KnowledgePointBasePydantic):
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True 

class KnowledgePointPydantic(KnowledgePointInDBBasePydantic): 
    pass

# --- LearningPath Pydantic Models ---
class LearningPathKPDetail(BaseModel): 
    knowledge_point_id: uuid.UUID
    sequence_order: int

class LearningPathBase(BaseModel):
    title: str
    description: Optional[str] = None

class LearningPathCreate(LearningPathBase):
    knowledge_points: List[LearningPathKPDetail] = [] 

class LearningPathUpdate(BaseModel): 
    title: Optional[str] = None
    description: Optional[str] = None
    knowledge_points: Optional[List[LearningPathKPDetail]] = None

class KnowledgePointForPath(BaseModel): 
    id: uuid.UUID
    title: Optional[str] = None
    sequence_order: int 

    class Config:
        from_attributes = True

class LearningPathResponse(LearningPathBase):
    id: uuid.UUID
    user_id: uuid.UUID 
    created_at: datetime
    updated_at: datetime
    knowledge_points: List[KnowledgePointForPath] = []

    class Config:
        from_attributes = True

# --- QuizAttempt Models (remain unchanged for this subtask) ---
class QuizAttemptBase(BaseModel):
    user_id: uuid.UUID
    learning_path_id: Optional[uuid.UUID] = None 
    knowledge_point_id: Optional[uuid.UUID] = None 
    score: Optional[float] = None
    
class QuizAttemptCreate(QuizAttemptBase):
    questions_answers_payload: List[Dict[str, Any]]

class QuizAttemptInDBBase(QuizAttemptBase):
    id: uuid.UUID
    attempted_at: datetime

    class Config:
        from_attributes = True

class QuizAttempt(QuizAttemptInDBBase):
    pass

# --- New Quiz Generation Pydantic Models ---
class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"
    # ESSAY = "essay" # For later

class QuestionOption(BaseModel): # For MCQs
    text: str
    is_correct: bool # Clearly mark the correct option(s)

class GeneratedQuestion(BaseModel):
    question_text: str
    question_type: QuestionType
    options: Optional[List[QuestionOption]] = None # For MCQ
    # correct_answer_text: Optional[str] = None # For short answer/true-false
    # points: int = 10 

class GeneratedQuizResponse(BaseModel):
    title: str 
    knowledge_point_id: Optional[uuid.UUID] = None
    learning_path_id: Optional[uuid.UUID] = None
    questions: List[GeneratedQuestion]
    # quiz_settings: Optional[Dict[str, Any]] = None

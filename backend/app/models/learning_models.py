from pydantic import BaseModel, Field # Ensure Field is imported
from typing import Optional, List, Dict, Any, Union # Ensure Union is imported
import uuid # Ensure uuid is imported
from datetime import datetime # Ensure datetime is imported
from enum import Enum 

# --- KnowledgePoint Models ---
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

# --- Quiz Generation Pydantic Models ---
class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"

class QuestionOption(BaseModel): 
    text: str
    is_correct: bool 

class GeneratedQuestion(BaseModel):
    question_text: str
    question_type: QuestionType
    options: Optional[List[QuestionOption]] = None 
    # The prompt for this subtask doesn't include attempted_question_answer_id here,
    # but it's mentioned in the API endpoint mapping.
    # Let's add it here for clarity in what QuizAttemptResponse.questions_for_attempt should contain.
    attempted_question_answer_id: Optional[uuid.UUID] = None # ID of the AQA_Model instance

class GeneratedQuizResponse(BaseModel):
    title: str 
    knowledge_point_id: Optional[uuid.UUID] = None
    learning_path_id: Optional[uuid.UUID] = None
    questions: List[GeneratedQuestion]


# --- New Quiz Attempt & Scoring Pydantic Models ---
class UserAnswerData(BaseModel): 
    selected_option_id: Optional[uuid.UUID] = None # Not used if options don't have own IDs
    selected_option_index: Optional[int] = None # For MCQ
    answer_text: Optional[str] = None # For short_answer, true_false

class AttemptedQuestionAnswerBase(BaseModel):
    quiz_attempt_id: uuid.UUID
    # question_id: Optional[uuid.UUID] = None # If linking to a persisted QuestionBank Question ID
    
    question_text: str
    question_type: QuestionType 
    options: Optional[List[QuestionOption]] = None # Denormalized options from GeneratedQuestion

    submitted_answer_data: Optional[UserAnswerData] = None
    is_correct: Optional[bool] = None
    score: Optional[float] = 0.0

class AttemptedQuestionAnswerCreate(AttemptedQuestionAnswerBase):
    pass 

class AttemptedQuestionAnswerResponse(AttemptedQuestionAnswerBase):
    id: uuid.UUID
    class Config:
        from_attributes = True

class QuizAttemptStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class QuizAttemptBase(BaseModel):
    user_id: uuid.UUID
    source_learning_path_id: Optional[uuid.UUID] = None
    source_knowledge_point_id: Optional[uuid.UUID] = None
    status: QuizAttemptStatus = QuizAttemptStatus.IN_PROGRESS
    score: Optional[float] = None

class QuizAttemptCreate(QuizAttemptBase): # Used by service layer
    pass

# For responding when an attempt is first started
class QuestionForAttemptResponse(BaseModel): # Strips correct answer info for MCQs
    attempted_question_answer_id: uuid.UUID # ID of the AQA_Model instance
    question_text: str
    question_type: QuestionType
    options: Optional[List[Dict[str, Any]]] = None # Strips 'is_correct' from QuestionOption

    class Config:
        from_attributes = True


class QuizAttemptResponse(QuizAttemptBase): # For starting an attempt
    id: uuid.UUID
    attempted_at: datetime 
    questions_for_attempt: List[QuestionForAttemptResponse] = [] 
    
    class Config:
        from_attributes = True

class QuizAttemptResultResponse(QuizAttemptBase): # For showing results after completion
    id: uuid.UUID
    attempted_at: datetime
    questions_with_answers: List[AttemptedQuestionAnswerResponse] = []

    class Config:
        from_attributes = True

class UserSubmittedAnswer(BaseModel):
    attempted_question_answer_id: uuid.UUID 
    submitted_answer_data: UserAnswerData

class QuizSubmissionPayload(BaseModel):
    answers: List[UserSubmittedAnswer]

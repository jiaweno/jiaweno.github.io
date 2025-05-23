from sqlalchemy import Column, String, Boolean, DateTime, func, Text, ForeignKey, Enum as SAEnum, Integer, Float # Added Float
from sqlalchemy.dialects.postgresql import UUID, JSONB # Added JSONB
from sqlalchemy.orm import relationship 
import uuid
from .base_class import Base 
from app.models.document_models import DocumentStatus 
from app.models.learning_models import QuizAttemptStatus, QuestionType # Added QuizAttemptStatus, QuestionType

class User(Base):
    __tablename__ = "users" 

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Document(Base):
    __tablename__ = "documents" 

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    s3_url = Column(String(1024), nullable=False)
    status = Column(SAEnum(DocumentStatus, name="document_status_enum", create_type=False), nullable=False, default=DocumentStatus.PENDING)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    extracted_text_s3_url = Column(String(1024), nullable=True) 
    processing_error = Column(Text, nullable=True) 

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    title = Column(String(255), nullable=True) 
    content_chunk = Column(Text, nullable=False)
    sequence_in_document = Column(Integer, nullable=True) 

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False) 
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    knowledge_point_associations = relationship(
        "LearningPathKnowledgePoint", 
        back_populates="learning_path", 
        order_by="LearningPathKnowledgePoint.sequence_order", 
        cascade="all, delete-orphan" 
    )

class LearningPathKnowledgePoint(Base):
    __tablename__ = "learning_path_knowledge_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    learning_path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False)
    knowledge_point_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_points.id"), nullable=False)
    sequence_order = Column(Integer, nullable=False) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    learning_path = relationship("LearningPath", back_populates="knowledge_point_associations")
    knowledge_point = relationship("KnowledgePoint") 

# --- New Quiz Attempt SQLAlchemy Models ---
class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    source_learning_path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=True)
    source_knowledge_point_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_points.id"), nullable=True)

    status = Column(SAEnum(QuizAttemptStatus, name="quiz_attempt_status_enum", create_type=False), nullable=False, default=QuizAttemptStatus.IN_PROGRESS)
    score = Column(Float, nullable=True)
    
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    attempted_questions = relationship(
        "AttemptedQuestionAnswer", 
        back_populates="quiz_attempt",
        cascade="all, delete-orphan"
    )

class AttemptedQuestionAnswer(Base):
    __tablename__ = "attempted_question_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_attempt_id = Column(UUID(as_uuid=True), ForeignKey("quiz_attempts.id"), nullable=False)
    
    question_text = Column(Text, nullable=False)
    question_type = Column(SAEnum(QuestionType, name="question_type_enum", create_type=False), nullable=False)
    options = Column(JSONB, nullable=True) # Stores List[QuestionOption]

    submitted_answer_data = Column(JSONB, nullable=True) # Stores UserAnswerData
    is_correct = Column(Boolean, nullable=True)
    score = Column(Float, default=0.0)

    quiz_attempt = relationship("QuizAttempt", back_populates="attempted_questions")

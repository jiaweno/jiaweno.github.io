# This file makes 'db' a Python package
# It will also export Base and ORM models

from .base_class import Base
# Import your SQLAlchemy models here so they are registered with Base
from .models_sqlalchemy import (
    User, 
    Document, 
    KnowledgePoint, 
    LearningPath, 
    LearningPathKnowledgePoint,
    QuizAttempt,                 # Added
    AttemptedQuestionAnswer      # Added
)

# You might also want to define a function to initialize tables for dev/testing
# def init_db(engine):
#     Base.metadata.create_all(bind=engine)

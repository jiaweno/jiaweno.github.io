from fastapi import APIRouter
from .endpoints import users, documents, learning_paths, quizzes, quiz_attempts # Added quiz_attempts

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(learning_paths.router, prefix="/learning-paths", tags=["learning-paths"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"]) 
api_router.include_router(quiz_attempts.router, prefix="/quiz-attempts", tags=["quiz-attempts"]) # Added quiz_attempts router

# Add more routers here as they are created

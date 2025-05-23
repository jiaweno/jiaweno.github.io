from fastapi import APIRouter
from .endpoints import users, documents, learning_paths, quizzes # Added quizzes

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(learning_paths.router, prefix="/learning-paths", tags=["learning-paths"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"]) # Added quizzes router

# Add more routers here as they are created
# e.g., other quiz-related endpoints like attempts.

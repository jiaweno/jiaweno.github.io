from fastapi import FastAPI
from .api.v1.api import api_router as api_v1_router # Will create this file next
from .core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# Placeholder for startup/shutdown events (e.g., DB connections)
@app.on_event("startup")
async def startup_event():
    # For example, connect to database
    # await connect_to_db()
    print("Application startup")

@app.on_event("shutdown")
async def shutdown_event():
    # For example, disconnect from database
    # await disconnect_from_db()
    print("Application shutdown")

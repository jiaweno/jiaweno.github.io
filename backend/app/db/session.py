from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings # Assuming app is in PYTHONPATH

# For local development, you might not need to configure SSL
# For production, ensure you configure SSL appropriately if your DB requires it
engine_kwargs = {}
# if "rds.amazonaws.com" in settings.SQLALCHEMY_DATABASE_URI: # Example for AWS RDS
#     engine_kwargs["connect_args"] = {"sslmode": "require"}


engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Placeholder for initial data or base model for ORM
# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()

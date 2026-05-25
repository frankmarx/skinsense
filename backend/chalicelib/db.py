import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from dotenv import load_dotenv

# Load .env to ensure DATABASE_URL is available for the engine
load_dotenv(override=True)

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# SessionLocal will be used to create a new session for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models to inherit from
Base = declarative_base()

@contextmanager
def get_db():
    """
    Context manager that provides a transactional scope around a series of operations.
    Usage:
        with get_db() as db:
            db.query(Model).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initializes the database by creating all tables defined in the Base metadata.
    """
    # Import models here to ensure they are registered with Base before create_all
    from chalicelib.models import Price
    Base.metadata.create_all(bind=engine)

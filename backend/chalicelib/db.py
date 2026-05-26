import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from dotenv import load_dotenv

# Define Base (does not need DB access)
Base = declarative_base()

# Robustly find .env in the backend/ directory
# Assuming this file is in backend/chalicelib/db.py
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError(f"DATABASE_URL environment variable is not set. Looked in: {env_path}")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# SessionLocal will be used to create a new session for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from functools import wraps

def db_transaction(func):
    """
    Decorator to wrap a function in a database transaction session.
    Automatically commits on success and rolls back on failure.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with get_db() as db:
            try:
                # Inject 'db' session into the decorated function if not already passed
                if 'db' not in kwargs:
                    kwargs['db'] = db
                result = func(*args, **kwargs)
                db.commit()
                return result
            except Exception as e:
                db.rollback()
                raise e
    return wrapper

def init_db():
    """
    Initializes the database by creating all tables defined in the Base metadata.
    """
    Base.metadata.create_all(bind=engine)

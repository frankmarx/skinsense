from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from chalicelib.utils.config import get_db_url

# Define Base (does not need DB access)
Base = declarative_base()

DB_URL = get_db_url()

if not DB_URL:
    raise ValueError("DB_URL is not set.")

# Create SQLAlchemy engine
engine = create_engine(DB_URL)

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

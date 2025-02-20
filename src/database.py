from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the DATABASE_URL from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL is None:
    raise ValueError("""
    DATABASE_URL environment variable is not set. 
    Please check your .env file exists and contains:
    DATABASE_URL=postgresql://username:password@localhost:5432/dbname
    """)

# Modified engine creation with connection pooling settings
engine = create_engine(
    DATABASE_URL,
    pool_size=5,  # Maximum number of connections to keep
    max_overflow=2,  # Maximum number of connections that can be created beyond pool_size
    pool_timeout=30,  # Timeout for getting a connection from the pool
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Enable connection health checks
    poolclass=QueuePool  # Use QueuePool for better connection management
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Kitty(Base):
    __tablename__ = "kitties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    link = Column(String, unique=True)
    found_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    try:
        logging.info("Attempting to connect to database...")
        # Test the connection first
        with engine.connect() as conn:
            logging.info("Database connection successful")
        # Create tables
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables initialized successfully")
    except Exception as e:
        logging.error(f"Database connection/initialization error: {str(e)}")
        raise  # Re-raise the exception to handle it in the calling code

def get_db():
    db = None
    try:
        db = SessionLocal()
        # Test the connection with proper text() wrapper
        db.execute(text("SELECT 1"))
        return db
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        if db:
            db.close()
        # Wait and retry once
        import time
        time.sleep(1)
        try:
            db = SessionLocal()
            return db
        except Exception as retry_error:
            logging.error(f"Retry failed: {str(retry_error)}")
            raise

def add_kitty(name, age, gender, link):
    db = get_db()
    try:
        # Check if kitty already exists
        existing_kitty = db.query(Kitty).filter(Kitty.link == link).first()
        if existing_kitty:
            logging.info(f'Kitty {name} already exists in database')
            return False

        new_kitty = Kitty(
            name=name,
            age=age,
            gender=gender,
            link=link
        )
        db.add(new_kitty)
        db.commit()
        logging.info(f'Added new kitty: {name}')
        return True
    except Exception as e:
        db.rollback()
        logging.error(f"Error adding kitty to database: {str(e)}")
        return False
    finally:
        db.close()

def get_all_kitties():
    db = get_db()
    try:
        return db.query(Kitty).all()
    finally:
        db.close()

def get_recent_kitties(days=7):
    db = get_db()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return db.query(Kitty).filter(Kitty.found_at >= cutoff_date).all()
    finally:
        db.close()

def cat_exists(link):
    db = get_db()
    try:
        exists = db.query(Kitty).filter(Kitty.link == link).first() is not None
        return exists
    except Exception as e:
        logging.error(f"Error checking if cat exists: {str(e)}")
        return False
    finally:
        db.close() 
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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
    DATABASE_URL=postgresql://yasminesalamelama@localhost:5432/kitty_db
    """)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
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
    try:
        db = SessionLocal()
        return db
    except Exception as e:
        logging.error(f"Error getting database session: {str(e)}")
        raise  # Re-raise the exception to handle it in the calling code

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
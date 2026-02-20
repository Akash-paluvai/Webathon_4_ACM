import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Normalize PostgreSQL URLs to use psycopg2 driver
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif DATABASE_URL.startswith("postgresql://") and "+psycopg" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    elif "psycopg://" in DATABASE_URL and "psycopg2://" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("psycopg://", "psycopg2://", 1)

    # Remove channel_binding param (psycopg2 doesn't support it)
    DATABASE_URL = re.sub(r'[&?]channel_binding=[^&]*', '', DATABASE_URL)

    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        # Quick connection test
        with engine.connect() as conn:
            pass
        print(f"✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"⚠️  PostgreSQL connection failed: {e}")
        print("⚠️  Falling back to SQLite")
        DATABASE_URL = "sqlite:///./film_os.db"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    print("⚠️  No DATABASE_URL set, using SQLite")
    DATABASE_URL = "sqlite:///./film_os.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

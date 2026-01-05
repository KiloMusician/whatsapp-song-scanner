"""Database connection configuration."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import DATABASE_CONFIG


# CREATE DATABASE ENGINE

def get_database_url():
    """Build MariaDB connection URL."""
    config = DATABASE_CONFIG['mariadb']
    return (
        f"mysql+pymysql://{config['username']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['database']}"
        f"?charset={config['charset']}"
    )


engine = create_engine(
    get_database_url(),
    pool_size=DATABASE_CONFIG['mariadb']['pool_size'],
    max_overflow=DATABASE_CONFIG['mariadb']['max_overflow'],
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Set to True for SQL query logging
)


# CREATE SESSION FACTORY

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# CREATE BASE CLASS FOR MODELS

Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

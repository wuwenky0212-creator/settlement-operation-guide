"""Pytest configuration and fixtures"""
import pytest
import os


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine using SQLite in-memory database"""
    try:
        from sqlalchemy import create_engine
        from app.database import Base
        
        # Use SQLite in-memory database for testing
        # This doesn't require PostgreSQL to be installed or running
        test_db_url = "sqlite:///:memory:"
        
        # SQLite specific settings for better compatibility
        engine = create_engine(
            test_db_url,
            echo=False,
            connect_args={"check_same_thread": False}  # Allow multi-threaded access
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        yield engine
        
        # Drop all tables after tests
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
    except ImportError:
        pytest.skip("Database dependencies not installed")


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create a new database session for each test"""
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    
    # Clear all tables before each test to ensure isolation
    Base.metadata.drop_all(bind=test_db_engine)
    Base.metadata.create_all(bind=test_db_engine)
    
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )
    session = TestingSessionLocal()
    
    yield session
    
    # Rollback any changes after each test
    session.rollback()
    session.close()

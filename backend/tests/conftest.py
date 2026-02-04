"""Shared fixtures for RAG system tests."""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

# Add backend to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vector_store import VectorStore, SearchResults
from models import Course, Lesson, CourseChunk
from session_manager import SessionManager


# =============================================================================
# Vector Store Fixtures
# =============================================================================

@pytest.fixture
def tmp_vector_store(tmp_path):
    """Create a VectorStore backed by a temporary directory with max_results=5."""
    store = VectorStore(
        chroma_path=str(tmp_path / "chroma"),
        embedding_model="all-MiniLM-L6-v2",
        max_results=5,
    )
    return store


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_course():
    """A minimal Course object for testing."""
    return Course(
        title="Test Course",
        course_link="https://example.com/test-course",
        instructor="Test Instructor",
        lessons=[
            Lesson(lesson_number=1, title="Intro", lesson_link="https://example.com/l1"),
            Lesson(lesson_number=2, title="Basics", lesson_link="https://example.com/l2"),
        ],
    )


@pytest.fixture
def sample_chunks():
    """Content chunks belonging to the sample course."""
    return [
        CourseChunk(content="This lesson introduces prompt engineering techniques.", course_title="Test Course", lesson_number=1, chunk_index=0),
        CourseChunk(content="Chain of thought prompting improves reasoning accuracy.", course_title="Test Course", lesson_number=1, chunk_index=1),
        CourseChunk(content="The basics of API usage and authentication tokens.", course_title="Test Course", lesson_number=2, chunk_index=2),
    ]


@pytest.fixture
def populated_store(tmp_vector_store, sample_course, sample_chunks):
    """A VectorStore that already contains the sample course and chunks."""
    tmp_vector_store.add_course_metadata(sample_course)
    tmp_vector_store.add_course_content(sample_chunks)
    return tmp_vector_store


# =============================================================================
# Mock Fixtures for API Testing
# =============================================================================

@pytest.fixture
def mock_rag_system():
    """Create a mock RAG system for API tests."""
    mock = MagicMock()
    mock.session_manager = SessionManager(max_history=2)

    # Default mock behavior for query
    mock.query.return_value = (
        "This is a test response about the course.",
        [{"title": "Test Course", "lesson": "Intro", "content": "Sample content"}]
    )

    # Default mock behavior for analytics
    mock.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Test Course", "Another Course"]
    }

    return mock


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    @dataclass
    class MockConfig:
        ANTHROPIC_API_KEY: str = "test-api-key"
        ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
        EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
        CHUNK_SIZE: int = 800
        CHUNK_OVERLAP: int = 100
        MAX_RESULTS: int = 5
        MAX_HISTORY: int = 2
        CHROMA_PATH: str = "./test_chroma_db"

    return MockConfig()


# =============================================================================
# API Test Client Fixtures
# =============================================================================

@pytest.fixture
def test_app(mock_rag_system):
    """Create a test FastAPI app with mocked dependencies.

    This creates a minimal FastAPI app with the same endpoints as the main app,
    but without static file mounting (which requires the frontend directory).
    """
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from typing import List, Optional

    app = FastAPI(title="Test Course Materials RAG System")

    # Pydantic models (same as main app)
    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[dict]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    # Store mock in app state for access in endpoints
    app.state.rag_system = mock_rag_system

    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            rag = app.state.rag_system
            session_id = request.session_id
            if not session_id:
                session_id = rag.session_manager.create_session()

            answer, sources = rag.query(request.query, session_id)

            return QueryResponse(
                answer=answer,
                sources=sources,
                session_id=session_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            rag = app.state.rag_system
            analytics = rag.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/")
    async def root():
        return {"message": "Course Materials RAG System API"}

    return app


@pytest.fixture
def client(test_app):
    """Create a test client for API testing."""
    from fastapi.testclient import TestClient
    return TestClient(test_app)

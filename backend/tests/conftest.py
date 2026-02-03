"""Shared fixtures for RAG system tests."""
import sys
import os
import pytest

# Add backend to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vector_store import VectorStore, SearchResults
from models import Course, Lesson, CourseChunk


@pytest.fixture
def tmp_vector_store(tmp_path):
    """Create a VectorStore backed by a temporary directory with max_results=5."""
    store = VectorStore(
        chroma_path=str(tmp_path / "chroma"),
        embedding_model="all-MiniLM-L6-v2",
        max_results=5,
    )
    return store


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

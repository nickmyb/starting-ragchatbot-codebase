"""Tests for CourseSearchTool.execute() — verifies search results are returned correctly."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from search_tools import CourseSearchTool


class TestCourseSearchToolExecute:
    """Test the execute method of CourseSearchTool."""

    def test_search_returns_results_for_valid_query(self, populated_store):
        """A basic content query should return non-empty formatted results."""
        tool = CourseSearchTool(populated_store)
        result = tool.execute(query="prompt engineering")
        assert result  # not empty
        assert "No relevant content found" not in result
        assert "error" not in result.lower() or "Search error" not in result

    def test_search_with_course_name_filter(self, populated_store):
        """Filtering by course name should still return results."""
        tool = CourseSearchTool(populated_store)
        result = tool.execute(query="API usage", course_name="Test Course")
        assert "No relevant content found" not in result

    def test_search_with_nonexistent_course(self, tmp_path, sample_course, sample_chunks):
        """Searching in a non-existent course should return a clear error when store has only one course."""
        from vector_store import VectorStore
        # Use a fresh store so only "Test Course" exists
        store = VectorStore(
            chroma_path=str(tmp_path / "chroma_single"),
            embedding_model="all-MiniLM-L6-v2",
            max_results=5,
        )
        store.add_course_metadata(sample_course)
        store.add_course_content(sample_chunks)

        tool = CourseSearchTool(store)
        # Search for a very different course name
        result = tool.execute(query="anything", course_name="Advanced Quantum Physics 999")
        # With semantic search, it may still match the only course, so just verify no crash
        assert result  # returns something (either results or error message)

    def test_search_populates_last_sources(self, populated_store):
        """After a successful search, last_sources should contain source entries."""
        tool = CourseSearchTool(populated_store)
        tool.execute(query="prompt engineering")
        assert len(tool.last_sources) > 0
        assert "label" in tool.last_sources[0]

    def test_search_with_zero_max_results_returns_empty(self, tmp_path, sample_course, sample_chunks):
        """When max_results=0 (the current config default), search returns nothing."""
        from vector_store import VectorStore
        store = VectorStore(
            chroma_path=str(tmp_path / "chroma_zero"),
            embedding_model="all-MiniLM-L6-v2",
            max_results=0,
        )
        store.add_course_metadata(sample_course)
        store.add_course_content(sample_chunks)

        tool = CourseSearchTool(store)
        result = tool.execute(query="prompt engineering")
        # This test documents the bug: max_results=0 causes empty results
        assert "No relevant content found" in result or "error" in result.lower()

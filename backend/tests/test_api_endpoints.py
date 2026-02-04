"""Tests for FastAPI endpoints in the RAG system."""
import pytest
from unittest.mock import MagicMock


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_returns_message(self, client):
        """Root endpoint should return a welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()


class TestQueryEndpoint:
    """Tests for the /api/query endpoint."""

    def test_query_with_valid_request(self, client, mock_rag_system):
        """Query endpoint should return answer and sources."""
        response = client.post(
            "/api/query",
            json={"query": "What is prompt engineering?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["answer"] == "This is a test response about the course."

    def test_query_creates_session_when_not_provided(self, client, mock_rag_system):
        """Query should create a new session if none provided."""
        response = client.post(
            "/api/query",
            json={"query": "Test question"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"].startswith("session_")

    def test_query_uses_provided_session_id(self, client, mock_rag_system):
        """Query should use the provided session ID."""
        session_id = "existing_session_123"
        mock_rag_system.session_manager.sessions[session_id] = []

        response = client.post(
            "/api/query",
            json={"query": "Follow-up question", "session_id": session_id}
        )

        assert response.status_code == 200
        mock_rag_system.query.assert_called_once()
        call_args = mock_rag_system.query.call_args
        assert call_args[0][1] == session_id

    def test_query_returns_sources(self, client, mock_rag_system):
        """Query should return sources from RAG system."""
        expected_sources = [
            {"title": "Course A", "lesson": "Lesson 1", "content": "Content A"},
            {"title": "Course B", "lesson": "Lesson 2", "content": "Content B"},
        ]
        mock_rag_system.query.return_value = ("Answer", expected_sources)

        response = client.post(
            "/api/query",
            json={"query": "Test question"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["sources"]) == 2
        assert data["sources"][0]["title"] == "Course A"

    def test_query_empty_query_string(self, client):
        """Query with empty string should still be processed."""
        response = client.post(
            "/api/query",
            json={"query": ""}
        )

        # Empty query is valid input, endpoint should process it
        assert response.status_code == 200

    def test_query_missing_query_field(self, client):
        """Query without query field should return 422 validation error."""
        response = client.post(
            "/api/query",
            json={}
        )

        assert response.status_code == 422

    def test_query_handles_rag_system_error(self, client, mock_rag_system):
        """Query should return 500 when RAG system raises an error."""
        mock_rag_system.query.side_effect = Exception("Database connection failed")

        response = client.post(
            "/api/query",
            json={"query": "Test question"}
        )

        assert response.status_code == 500
        assert "Database connection failed" in response.json()["detail"]


class TestCoursesEndpoint:
    """Tests for the /api/courses endpoint."""

    def test_get_courses_returns_stats(self, client, mock_rag_system):
        """Courses endpoint should return course statistics."""
        response = client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()
        assert "total_courses" in data
        assert "course_titles" in data
        assert data["total_courses"] == 2
        assert len(data["course_titles"]) == 2

    def test_get_courses_empty_catalog(self, client, mock_rag_system):
        """Courses endpoint should handle empty course catalog."""
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": []
        }

        response = client.get("/api/courses")

        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    def test_get_courses_handles_error(self, client, mock_rag_system):
        """Courses endpoint should return 500 on error."""
        mock_rag_system.get_course_analytics.side_effect = Exception("Vector store error")

        response = client.get("/api/courses")

        assert response.status_code == 500
        assert "Vector store error" in response.json()["detail"]


class TestAPIIntegration:
    """Integration tests for API workflows."""

    def test_query_then_get_courses(self, client, mock_rag_system):
        """Test a typical workflow: query then check courses."""
        # First, make a query
        query_response = client.post(
            "/api/query",
            json={"query": "What courses are available?"}
        )
        assert query_response.status_code == 200

        # Then, get course stats
        courses_response = client.get("/api/courses")
        assert courses_response.status_code == 200

    def test_multiple_queries_same_session(self, client, mock_rag_system):
        """Test multiple queries within the same session."""
        # First query creates session
        response1 = client.post(
            "/api/query",
            json={"query": "First question"}
        )
        session_id = response1.json()["session_id"]

        # Second query uses same session
        response2 = client.post(
            "/api/query",
            json={"query": "Second question", "session_id": session_id}
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        # Both queries should use the same session
        assert response2.json()["session_id"] == session_id

    def test_concurrent_sessions(self, client, mock_rag_system):
        """Test that different sessions are handled independently."""
        # Create first session
        response1 = client.post(
            "/api/query",
            json={"query": "Question for session 1"}
        )
        session1 = response1.json()["session_id"]

        # Create second session
        response2 = client.post(
            "/api/query",
            json={"query": "Question for session 2"}
        )
        session2 = response2.json()["session_id"]

        # Sessions should be different
        assert session1 != session2

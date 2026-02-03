"""Tests for RAGSystem — end-to-end query handling."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, MagicMock
from dataclasses import dataclass


class TestRAGSystemConfig:
    """Test that the production config values are sane."""

    def test_max_results_is_positive(self):
        """MAX_RESULTS must be > 0 or ChromaDB returns no results."""
        from config import Config
        cfg = Config()
        assert cfg.MAX_RESULTS > 0, (
            f"MAX_RESULTS={cfg.MAX_RESULTS} — this causes ChromaDB to return 0 results. "
            "Set it to a positive integer (e.g. 5)."
        )


class TestRAGSystemQuery:
    """Test the full query pipeline with mocked AI."""

    @pytest.fixture
    def rag_system(self, tmp_path, sample_course, sample_chunks):
        """Build a RAGSystem with a temp vector store and mocked AI."""
        @dataclass
        class TestConfig:
            ANTHROPIC_API_KEY: str = "fake-key"
            ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
            EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
            CHUNK_SIZE: int = 800
            CHUNK_OVERLAP: int = 100
            MAX_RESULTS: int = 5
            MAX_HISTORY: int = 2
            CHROMA_PATH: str = str(tmp_path / "chroma")

        # Patch Anthropic client to avoid proxy issues
        with patch("anthropic.Anthropic") as MockClient:
            MockClient.return_value = MagicMock()
            from rag_system import RAGSystem
            system = RAGSystem(TestConfig())
            system.vector_store.add_course_metadata(sample_course)
            system.vector_store.add_course_content(sample_chunks)
            return system

    def test_query_returns_response_and_sources(self, rag_system):
        """A content query through the full pipeline should return a response string and sources list."""

        # We need to mock the Anthropic API but let the tool execution run for real.
        class FakeBlock:
            def __init__(self, block_type, **kw):
                self.type = block_type
                for k, v in kw.items():
                    setattr(self, k, v)

        tool_use_block = FakeBlock(
            "tool_use",
            id="t1",
            name="search_course_content",
            input={"query": "prompt engineering"},
        )

        first_resp = MagicMock()
        first_resp.stop_reason = "tool_use"
        first_resp.content = [tool_use_block]

        second_resp = MagicMock()
        second_resp.stop_reason = "end_turn"
        second_resp.content = [FakeBlock("text", text="Prompt engineering is...")]

        with patch("anthropic.Anthropic") as MockClient:
            instance = MockClient.return_value
            instance.messages.create.side_effect = [first_resp, second_resp]

            # Re-init generator with mocked client
            rag_system.ai_generator.client = instance

            answer, sources = rag_system.query("What is prompt engineering?")

        assert "Prompt engineering" in answer
        assert isinstance(sources, list)

    def test_tool_manager_has_both_tools(self, rag_system):
        """ToolManager should have both search and outline tools registered."""
        tool_names = list(rag_system.tool_manager.tools.keys())
        assert "search_course_content" in tool_names
        assert "get_course_outline" in tool_names

    def test_search_tool_gets_results_with_correct_max_results(self, rag_system):
        """The search tool should return actual results (not empty) with max_results=5."""
        result = rag_system.search_tool.execute(query="prompt engineering")
        assert "No relevant content found" not in result
        assert result  # not empty string

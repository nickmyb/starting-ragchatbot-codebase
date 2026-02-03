"""Tests for AIGenerator — verifies it correctly invokes tools when appropriate."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import MagicMock, patch
from search_tools import ToolManager, CourseSearchTool


class FakeContentBlock:
    def __init__(self, block_type, **kwargs):
        self.type = block_type
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestAIGeneratorToolCalling:
    """Test that AIGenerator triggers tool use for course-content queries."""

    @pytest.fixture
    def generator(self):
        # Patch Anthropic client to avoid proxy issues in test environment
        with patch("anthropic.Anthropic") as MockClient:
            MockClient.return_value = MagicMock()
            from ai_generator import AIGenerator
            gen = AIGenerator(api_key="fake-key", model="claude-sonnet-4-20250514")
            return gen

    def test_tool_definitions_passed_to_api(self, generator, populated_store):
        """When tools are provided, they should appear in the API call params."""
        tool_mgr = ToolManager()
        tool_mgr.register_tool(CourseSearchTool(populated_store))
        tool_defs = tool_mgr.get_tool_definitions()

        with patch.object(generator.client.messages, "create") as mock_create:
            # Simulate a direct text response (no tool use)
            mock_response = MagicMock()
            mock_response.stop_reason = "end_turn"
            mock_response.content = [FakeContentBlock("text", text="Hello")]
            mock_create.return_value = mock_response

            generator.generate_response(
                query="What is prompt engineering?",
                tools=tool_defs,
                tool_manager=tool_mgr,
            )

            call_kwargs = mock_create.call_args[1]
            assert "tools" in call_kwargs
            assert call_kwargs["tools"] == tool_defs
            assert call_kwargs["tool_choice"] == {"type": "auto"}

    def test_tool_execution_on_tool_use_response(self, generator, populated_store):
        """When Claude responds with tool_use, the generator should execute the tool and make a follow-up call."""
        tool_mgr = ToolManager()
        search_tool = CourseSearchTool(populated_store)
        tool_mgr.register_tool(search_tool)
        tool_defs = tool_mgr.get_tool_definitions()

        tool_use_block = FakeContentBlock(
            "tool_use",
            id="tool_123",
            name="search_course_content",
            input={"query": "prompt engineering"},
        )

        with patch.object(generator.client.messages, "create") as mock_create:
            # First call: Claude wants to use a tool
            first_response = MagicMock()
            first_response.stop_reason = "tool_use"
            first_response.content = [tool_use_block]

            # Second call: Claude gives final answer
            second_response = MagicMock()
            second_response.stop_reason = "end_turn"
            second_response.content = [FakeContentBlock("text", text="Here is the answer.")]

            mock_create.side_effect = [first_response, second_response]

            result = generator.generate_response(
                query="Tell me about prompt engineering",
                tools=tool_defs,
                tool_manager=tool_mgr,
            )

            assert result == "Here is the answer."
            assert mock_create.call_count == 2

            # Verify the second call includes tool_result
            second_call_kwargs = mock_create.call_args_list[1][1]
            messages = second_call_kwargs["messages"]
            tool_result_msg = messages[-1]
            assert tool_result_msg["role"] == "user"
            assert tool_result_msg["content"][0]["type"] == "tool_result"
            assert tool_result_msg["content"][0]["tool_use_id"] == "tool_123"

    def test_system_prompt_mentions_outline_tool(self, generator):
        """System prompt should instruct Claude about the outline tool."""
        assert "get_course_outline" in generator.SYSTEM_PROMPT

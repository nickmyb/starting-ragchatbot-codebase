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

    def test_two_sequential_tool_calls(self, generator, populated_store):
        """When Claude needs 2 tool calls, both should execute sequentially."""
        tool_mgr = ToolManager()
        tool_mgr.register_tool(CourseSearchTool(populated_store))
        tool_defs = tool_mgr.get_tool_definitions()

        # First response: tool call 1
        first_tool_use = FakeContentBlock(
            "tool_use", id="t1", name="search_course_content", input={"query": "q1"}
        )
        first_response = MagicMock(stop_reason="tool_use", content=[first_tool_use])

        # Second response: tool call 2 (after seeing first result)
        second_tool_use = FakeContentBlock(
            "tool_use", id="t2", name="search_course_content", input={"query": "q2"}
        )
        second_response = MagicMock(stop_reason="tool_use", content=[second_tool_use])

        # Third response: final text
        final_response = MagicMock(
            stop_reason="end_turn",
            content=[FakeContentBlock("text", text="Answer from two searches")]
        )

        with patch.object(generator.client.messages, "create") as mock_create:
            mock_create.side_effect = [first_response, second_response, final_response]

            result = generator.generate_response(
                query="Complex query needing two searches",
                tools=tool_defs,
                tool_manager=tool_mgr,
            )

            assert result == "Answer from two searches"
            assert mock_create.call_count == 3  # Initial + 2 tool rounds

    def test_max_two_rounds_enforced(self, generator, populated_store):
        """Should stop after 2 tool rounds even if Claude wants more."""
        tool_mgr = ToolManager()
        tool_mgr.register_tool(CourseSearchTool(populated_store))
        tool_defs = tool_mgr.get_tool_definitions()

        # Setup mock to always return tool_use
        tool_use_block = FakeContentBlock(
            "tool_use", id="t", name="search_course_content", input={"query": "q"}
        )
        tool_response = MagicMock(stop_reason="tool_use", content=[tool_use_block])

        # After 2 rounds, even if Claude wants more tools, we return the response
        # The third response still has tool_use but also includes text
        final_with_text = MagicMock(
            stop_reason="tool_use",
            content=[
                tool_use_block,
                FakeContentBlock("text", text="Partial answer after max rounds")
            ]
        )

        with patch.object(generator.client.messages, "create") as mock_create:
            mock_create.side_effect = [tool_response, tool_response, final_with_text]

            result = generator.generate_response(
                query="Query that keeps triggering tools",
                tools=tool_defs,
                tool_manager=tool_mgr,
            )

            # Should have made exactly 3 API calls (initial + 2 rounds max)
            assert mock_create.call_count == 3
            assert result == "Partial answer after max rounds"

    def test_tool_error_handled_gracefully(self, generator, populated_store):
        """Tool execution errors should be passed to Claude as error results."""
        tool_mgr = ToolManager()
        tool_mgr.register_tool(CourseSearchTool(populated_store))
        tool_defs = tool_mgr.get_tool_definitions()

        tool_use_block = FakeContentBlock(
            "tool_use",
            id="tool_err",
            name="search_course_content",
            input={"query": "test"},
        )

        with patch.object(generator.client.messages, "create") as mock_create:
            # First call: Claude wants to use a tool
            first_response = MagicMock(stop_reason="tool_use", content=[tool_use_block])

            # Second call: Claude gives final answer after seeing error
            second_response = MagicMock(
                stop_reason="end_turn",
                content=[FakeContentBlock("text", text="I encountered an error.")]
            )

            mock_create.side_effect = [first_response, second_response]

            # Patch the tool execution to raise an error
            with patch.object(tool_mgr, "execute_tool", side_effect=Exception("Tool failed")):
                result = generator.generate_response(
                    query="Query that causes tool error",
                    tools=tool_defs,
                    tool_manager=tool_mgr,
                )

            assert result == "I encountered an error."
            assert mock_create.call_count == 2

            # Verify error was passed to Claude with is_error flag
            second_call_kwargs = mock_create.call_args_list[1][1]
            messages = second_call_kwargs["messages"]
            tool_result_msg = messages[-1]
            assert tool_result_msg["role"] == "user"
            assert tool_result_msg["content"][0]["type"] == "tool_result"
            assert tool_result_msg["content"][0]["is_error"] is True
            assert "Tool failed" in tool_result_msg["content"][0]["content"]

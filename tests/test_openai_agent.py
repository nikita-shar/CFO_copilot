"""
Tests for OpenAI Agent - requires API key.
These tests verify that the AI agent can properly interact with OpenAI's API.
"""

import pytest
import os
from openai_cfo_agent import OpenAICFOAgent


class TestAgentInitialization:
    """Tests for agent setup and configuration."""
    
    @pytest.fixture
    def api_key(self):
        """Get API key from environment."""
        key = os.getenv('OPENAI_API_KEY')
        if not key:
            pytest.skip("OPENAI_API_KEY not set")
        return key
    
    def test_agent_can_initialize(self, api_key):
        """Test that agent initializes without errors."""
        agent = OpenAICFOAgent(api_key)
        
        assert agent is not None
        assert agent.client is not None
    
    def test_agent_has_correct_date_info(self, api_key):
        """Test that agent knows current date information."""
        agent = OpenAICFOAgent(api_key)
        
        assert agent.current_year >= 2025
        assert 1 <= agent.current_month <= 12
    
    def test_agent_has_tools_registered(self, api_key):
        """Test that all financial functions are registered as tools."""
        agent = OpenAICFOAgent(api_key)
        
        assert len(agent.tools) == 6
        
        tool_names = [tool['function']['name'] for tool in agent.tools]
        expected_tools = [
            'get_revenue_vs_budget',
            'calculate_gross_margin',
            'calculate_gross_margin_aggregate',
            'opex_by_category',
            'calculate_cash_runway',
            'calculate_ebitda'
        ]
        
        for expected in expected_tools:
            assert expected in tool_names
    
    def test_conversation_history_starts_empty(self, api_key):
        """Test that conversation history starts empty."""
        agent = OpenAICFOAgent(api_key)
        
        assert agent.conversation_history == []
    
    def test_reset_conversation_clears_history(self, api_key):
        """Test that reset clears conversation history."""
        agent = OpenAICFOAgent(api_key)
        
        # Add something to history
        agent.conversation_history.append({"role": "user", "content": "test"})
        
        # Reset
        agent.reset_conversation()
        
        assert agent.conversation_history == []


#@pytest.mark.integration
class TestAgentQueries:
    """Integration tests that make real API calls."""
    
    @pytest.fixture
    def agent(self):
        """Create an agent for testing."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")
        return OpenAICFOAgent(api_key)
    
    def test_simple_revenue_query(self, agent):
        """Test a simple revenue query (costs ~$0.01)."""
        response = agent.ask("What was our revenue in January 2025?")
        
        assert 'answer' in response
        assert 'data' in response
        assert 'chart_config' in response
        
        assert isinstance(response['answer'], str)
        assert len(response['answer']) > 0
        
        # Should have called get_revenue_vs_budget or similar
        assert len(response['data']) > 0
    
    def test_response_contains_function_data(self, agent):
        """Test that response includes data from function calls."""
        response = agent.ask("What was our revenue vs budget for Q1 2025?")
        
        assert isinstance(response['data'], dict)
        
        # Should have called at least one function
        assert len(response['data']) > 0
        
        # Check that function data has expected structure
        for func_name, data in response['data'].items():
            assert isinstance(data, dict)
    
    def test_chart_config_generated(self, agent):
        """Test that chart configuration is generated when appropriate."""
        response = agent.ask("Show me revenue vs budget for January 2025")
        
        if response['chart_config']:
            assert 'chart_type' in response['chart_config']
            assert 'title' in response['chart_config']
            assert 'data' in response['chart_config']
    
    def test_conversation_history_updates(self, agent):
        """Test that conversation history is maintained."""
        initial_len = len(agent.conversation_history)
        
        agent.ask("What was our revenue in January 2025?")
        
        # Should have added 2 messages (user + assistant)
        assert len(agent.conversation_history) == initial_len + 2
    
    def test_multiple_queries_in_sequence(self, agent):
        """Test that agent can handle multiple queries."""
        response1 = agent.ask("What was our revenue in January 2025?")
        response2 = agent.ask("What about February?")
        
        assert response1['answer'] != response2['answer']
        assert len(agent.conversation_history) >= 4  # At least 2 exchanges
    
    def test_complex_query_with_multiple_functions(self, agent):
        """Test query that might require multiple function calls."""
        response = agent.ask("Compare our Q1 revenue vs budget and show gross margin")
        
        assert 'answer' in response
        assert len(response['answer']) > 50  # Should be a substantial answer
        
        # Might call multiple functions
        assert len(response['data']) >= 1


#@pytest.mark.slow
class TestAgentEdgeCases:
    """Tests for edge cases and error handling."""
    
    @pytest.fixture
    def agent(self):
        """Create an agent for testing."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")
        return OpenAICFOAgent(api_key)
    
    def test_vague_query_gets_response(self, agent):
        """Test that vague queries still get a response."""
        response = agent.ask("Tell me about our finances")
        
        assert 'answer' in response
        assert len(response['answer']) > 0
    
    def test_invalid_date_handled_gracefully(self, agent):
        """Test that invalid dates are handled."""
        # Agent should either ask for clarification or use reasonable defaults
        response = agent.ask("What was revenue in month 13?")
        
        assert 'answer' in response
        # Should not crash
    
    def test_question_without_date_uses_defaults(self, agent):
        """Test that questions without dates use reasonable defaults."""
        response = agent.ask("What's our cash runway?")
        
        assert 'answer' in response
        assert 'data' in response


# Pytest configuration
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests that make real API calls"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests that take significant time"
    )
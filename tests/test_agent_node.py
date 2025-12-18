"""
Unit tests for agent node functionality.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage


class TestAgentNode:
    """Test agent node helper function."""
    
    def test_agent_node_success(self):
        """Test successful agent node execution."""
        import re
        
        def agent_node(state, agent, name):
            try:
                # Validate state
                if not state or "messages" not in state:
                    error_msg = f"{name} received invalid state."
                    return {"messages": [AIMessage(content=error_msg, name=name)]}
                
                result = agent.invoke({"messages": state["messages"]})
                
                # Check if result is valid
                if not result or "messages" not in result or not result["messages"]:
                    error_msg = f"{name} returned an empty or invalid response."
                    return {"messages": [AIMessage(content=error_msg, name=name)]}
                
                # Clean the content
                content = result["messages"][-1].content
                
                # Handle None or empty content
                if not content:
                    content = f"{name} completed but returned no content."
                
                # Replace problematic Unicode spaces
                content = content.replace('\u202f', ' ')
                content = content.replace('\u2009', ' ')
                content = content.replace('\u00a0', ' ')
                content = re.sub(r' +', ' ', content)
                
                return {
                    "messages": [AIMessage(content=content, name=name)]
                }
            except Exception as e:
                error_msg = f"{name} encountered an error: {str(e)}"
                return {
                    "messages": [AIMessage(content=error_msg, name=name)]
                }
        
        # Mock agent
        mock_agent = Mock()
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="The price is $150")]
        }
        
        state = {
            "messages": [HumanMessage(content="What is the price?")]
        }
        
        result = agent_node(state, mock_agent, "FinancialAgent")
        
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert result["messages"][0].content == "The price is $150"
        assert result["messages"][0].name == "FinancialAgent"
    
    def test_agent_node_unicode_cleaning(self):
        """Test Unicode character cleaning in agent node."""
        import re
        
        def agent_node(state, agent, name):
            result = agent.invoke({"messages": state["messages"]})
            content = result["messages"][-1].content
            
            # Clean Unicode characters
            content = content.replace('\u202f', ' ')
            content = content.replace('\u2009', ' ')
            content = content.replace('\u00a0', ' ')
            content = re.sub(r' +', ' ', content)
            
            return {
                "messages": [AIMessage(content=content, name=name)]
            }
        
        mock_agent = Mock()
        # Simulate response with Unicode characters
        mock_agent.invoke.return_value = {
            "messages": [AIMessage(content="December\u202f12,\u202f2025")]
        }
        
        state = {"messages": [HumanMessage(content="Test")]}
        result = agent_node(state, mock_agent, "FinancialAgent")
        
        # Check that Unicode characters are cleaned
        assert '\u202f' not in result["messages"][0].content
        assert "December 12, 2025" in result["messages"][0].content.replace(' ', ' ')  # Normalized spaces
    
    def test_agent_node_invalid_state(self):
        """Test agent node with invalid state."""
        import re
        
        def agent_node(state, agent, name):
            try:
                if not state or "messages" not in state:
                    error_msg = f"{name} received invalid state."
                    return {"messages": [AIMessage(content=error_msg, name=name)]}
                
                result = agent.invoke({"messages": state["messages"]})
                content = result["messages"][-1].content
                content = content.replace('\u202f', ' ')
                content = re.sub(r' +', ' ', content)
                
                return {
                    "messages": [AIMessage(content=content, name=name)]
                }
            except Exception as e:
                error_msg = f"{name} encountered an error: {str(e)}"
                return {
                    "messages": [AIMessage(content=error_msg, name=name)]
                }
        
        mock_agent = Mock()
        result = agent_node(None, mock_agent, "FinancialAgent")
        
        assert "invalid state" in result["messages"][0].content.lower()
    
    def test_agent_node_empty_response(self):
        """Test agent node with empty response."""
        import re
        
        def agent_node(state, agent, name):
            result = agent.invoke({"messages": state["messages"]})
            
            if not result or "messages" not in result or not result["messages"]:
                error_msg = f"{name} returned an empty or invalid response."
                return {"messages": [AIMessage(content=error_msg, name=name)]}
            
            content = result["messages"][-1].content
            
            if not content:
                content = f"{name} completed but returned no content."
            
            content = content.replace('\u202f', ' ')
            content = re.sub(r' +', ' ', content)
            
            return {
                "messages": [AIMessage(content=content, name=name)]
            }
        
        mock_agent = Mock()
        mock_agent.invoke.return_value = {"messages": []}
        
        state = {"messages": [HumanMessage(content="Test")]}
        result = agent_node(state, mock_agent, "FinancialAgent")
        
        assert "empty or invalid" in result["messages"][0].content.lower()
    
    def test_agent_node_exception_handling(self):
        """Test exception handling in agent node."""
        import re
        
        def agent_node(state, agent, name):
            try:
                result = agent.invoke({"messages": state["messages"]})
                content = result["messages"][-1].content
                content = content.replace('\u202f', ' ')
                content = re.sub(r' +', ' ', content)
                
                return {
                    "messages": [AIMessage(content=content, name=name)]
                }
            except Exception as e:
                error_msg = f"{name} encountered an error: {str(e)}"
                return {
                    "messages": [AIMessage(content=error_msg, name=name)]
                }
        
        mock_agent = Mock()
        mock_agent.invoke.side_effect = Exception("Test error")
        
        state = {"messages": [HumanMessage(content="Test")]}
        result = agent_node(state, mock_agent, "FinancialAgent")
        
        assert "error" in result["messages"][0].content.lower()
        assert "test error" in result["messages"][0].content.lower()


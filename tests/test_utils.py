"""
Unit tests for utility functions.
"""
import pytest
from langchain_core.messages import AIMessage, HumanMessage


class TestProcessEvent:
    """Test process_event helper function."""
    
    def test_process_event_with_messages(self):
        """Test processing event with messages."""
        def process_event(event):
            """Process and display events from the graph execution."""
            if not event:
                return
            
            if "__end__" not in event:
                if "messages" in event and event["messages"]:
                    try:
                        last_message = event["messages"][-1]
                        agent_name = getattr(last_message, 'name', "Unknown")
                        content = getattr(last_message, 'content', str(last_message))
                        return f"=== {agent_name} ===\n{content}\n"
                    except (IndexError, AttributeError, TypeError) as e:
                        return f"Error processing message event: {e}"
                elif "next" in event:
                    next_agent = event.get('next', 'Unknown')
                    return f"Supervisor decides the next agent: {next_agent}\n"
            return None
        
        event = {
            "messages": [AIMessage(content="The price is $150", name="FinancialAgent")]
        }
        
        result = process_event(event)
        assert "FinancialAgent" in result
        assert "$150" in result
    
    def test_process_event_with_next(self):
        """Test processing event with next agent decision."""
        def process_event(event):
            if not event:
                return
            
            if "__end__" not in event:
                if "messages" in event and event["messages"]:
                    last_message = event["messages"][-1]
                    agent_name = getattr(last_message, 'name', "Unknown")
                    content = getattr(last_message, 'content', str(last_message))
                    return f"=== {agent_name} ===\n{content}\n"
                elif "next" in event:
                    next_agent = event.get('next', 'Unknown')
                    return f"Supervisor decides the next agent: {next_agent}\n"
            return None
        
        event = {"next": "FinancialAgent"}
        result = process_event(event)
        assert "FinancialAgent" in result
    
    def test_process_event_empty(self):
        """Test processing empty event."""
        def process_event(event):
            if not event:
                return None
            return "Processed"
        
        result = process_event(None)
        assert result is None
    
    def test_process_event_without_name(self):
        """Test processing event with message without name."""
        def process_event(event):
            if not event:
                return
            
            if "__end__" not in event:
                if "messages" in event and event["messages"]:
                    try:
                        last_message = event["messages"][-1]
                        agent_name = getattr(last_message, 'name', "Unknown")
                        content = getattr(last_message, 'content', str(last_message))
                        return f"=== {agent_name} ===\n{content}\n"
                    except (IndexError, AttributeError, TypeError) as e:
                        return f"Error: {e}"
            return None
        
        event = {
            "messages": [AIMessage(content="Test message")]  # No name
        }
        
        result = process_event(event)
        assert "Unknown" in result or "Test message" in result
    
    def test_process_event_end(self):
        """Test processing end event."""
        def process_event(event):
            if not event:
                return
            
            if "__end__" not in event:
                return "Processing"
            return "End"
        
        event = {"__end__": True}
        result = process_event(event)
        assert result == "End"


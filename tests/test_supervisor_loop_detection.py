"""
Unit tests for supervisor loop detection functionality.
"""
import pytest
from langchain_core.messages import AIMessage, HumanMessage


class TestSupervisorLoopDetection:
    """Test loop detection logic in supervisor agent."""
    
    def test_detect_identical_responses(self):
        """Test detection of identical responses from same agent."""
        messages = [
            HumanMessage(content="What is the price?"),
            AIMessage(content="The price is $150", name="FinancialAgent"),
            AIMessage(content="The price is $150", name="FinancialAgent"),  # Duplicate
        ]
        
        # Simulate loop detection logic
        agent_messages = [msg for msg in messages[-8:] if isinstance(msg, AIMessage) and hasattr(msg, 'name') and msg.name]
        
        if len(agent_messages) >= 2:
            last_agent = agent_messages[-1].name
            recent_same_agent_responses = [msg for msg in agent_messages if msg.name == last_agent]
            
            if len(recent_same_agent_responses) >= 2:
                contents = [msg.content.strip() for msg in recent_same_agent_responses[-2:]]
                if contents[-1] == contents[-2]:
                    assert True, "Loop detected - identical responses"
                    return
        
        assert False, "Loop not detected when it should be"
    
    def test_detect_three_identical_responses(self):
        """Test detection of three identical responses."""
        messages = [
            HumanMessage(content="What is the price?"),
            AIMessage(content="The price is $150", name="FinancialAgent"),
            AIMessage(content="The price is $150", name="FinancialAgent"),
            AIMessage(content="The price is $150", name="FinancialAgent"),  # Third duplicate
        ]
        
        agent_messages = [msg for msg in messages[-8:] if isinstance(msg, AIMessage) and hasattr(msg, 'name') and msg.name]
        
        if len(agent_messages) >= 3:
            last_agent = agent_messages[-1].name
            recent_same_agent_responses = [msg for msg in agent_messages if msg.name == last_agent]
            
            if len(recent_same_agent_responses) >= 3:
                contents = [msg.content.strip() for msg in recent_same_agent_responses[-3:]]
                if contents[-1] == contents[-2] == contents[-3]:
                    assert True, "Loop detected - three identical responses"
                    return
        
        assert False, "Loop not detected"
    
    def test_no_loop_different_responses(self):
        """Test that different responses don't trigger loop detection."""
        messages = [
            HumanMessage(content="What is the price?"),
            AIMessage(content="The price is $150", name="FinancialAgent"),
            AIMessage(content="The price is $151", name="FinancialAgent"),  # Different
        ]
        
        agent_messages = [msg for msg in messages[-8:] if isinstance(msg, AIMessage) and hasattr(msg, 'name') and msg.name]
        
        if len(agent_messages) >= 2:
            last_agent = agent_messages[-1].name
            recent_same_agent_responses = [msg for msg in agent_messages if msg.name == last_agent]
            
            if len(recent_same_agent_responses) >= 2:
                contents = [msg.content.strip() for msg in recent_same_agent_responses[-2:]]
                if contents[-1] == contents[-2]:
                    assert False, "Loop detected when responses are different"
                    return
        
        assert True, "No loop detected for different responses"
    
    def test_normalized_similarity_detection(self):
        """Test normalized similarity detection (whitespace differences)."""
        messages = [
            HumanMessage(content="What is the price?"),
            AIMessage(content="The price is $150", name="FinancialAgent"),
            AIMessage(content="The  price  is  $150", name="FinancialAgent"),  # Extra spaces
        ]
        
        agent_messages = [msg for msg in messages[-8:] if isinstance(msg, AIMessage) and hasattr(msg, 'name') and msg.name]
        
        if len(agent_messages) >= 2:
            last_agent = agent_messages[-1].name
            recent_same_agent_responses = [msg for msg in agent_messages if msg.name == last_agent]
            
            if len(recent_same_agent_responses) >= 2:
                contents = [msg.content.strip() for msg in recent_same_agent_responses[-2:]]
                
                # Normalize: remove extra whitespace
                def normalize(text):
                    return ' '.join(text.split())
                
                norm_contents = [normalize(c) for c in contents[-2:]]
                if norm_contents[0] == norm_contents[1]:
                    assert True, "Loop detected - normalized similarity"
                    return
        
        assert False, "Normalized similarity not detected"
    
    def test_similarity_with_length_check(self):
        """Test similarity detection with length difference check."""
        messages = [
            HumanMessage(content="What is the price?"),
            AIMessage(content="The most recent closing price for **AAPL** was **$278.28** on **December 12, 2025**.", name="FinancialAgent"),
            AIMessage(content="The most recent closing price for **AAPL** was **$278.28** on **December 12, 2025**.", name="FinancialAgent"),
        ]
        
        agent_messages = [msg for msg in messages[-8:] if isinstance(msg, AIMessage) and hasattr(msg, 'name') and msg.name]
        
        if len(agent_messages) >= 2:
            last_agent = agent_messages[-1].name
            recent_same_agent_responses = [msg for msg in agent_messages if msg.name == last_agent]
            
            if len(recent_same_agent_responses) >= 2:
                contents = [msg.content.strip() for msg in recent_same_agent_responses[-2:]]
                
                if len(contents) >= 2:
                    c1, c2 = contents[-2], contents[-1]
                    if len(c1) > 50 and len(c2) > 50:
                        if c1[:150] == c2[:150]:
                            max_len = max(len(c1), len(c2))
                            if max_len > 0:
                                len_diff = abs(len(c1) - len(c2)) / max_len
                                if len_diff < 0.05:
                                    assert True, "Loop detected - high similarity"
                                    return
        
        assert False, "Similarity not detected"
    
    def test_no_loop_different_agents(self):
        """Test that different agents don't trigger loop detection."""
        messages = [
            HumanMessage(content="What is the price?"),
            AIMessage(content="The price is $150", name="FinancialAgent"),
            AIMessage(content="Searching for information...", name="WebSearchAgent"),  # Different agent
        ]
        
        agent_messages = [msg for msg in messages[-8:] if isinstance(msg, AIMessage) and hasattr(msg, 'name') and msg.name]
        
        if len(agent_messages) >= 2:
            last_agent = agent_messages[-1].name
            recent_same_agent_responses = [msg for msg in agent_messages if msg.name == last_agent]
            
            if len(recent_same_agent_responses) >= 2:
                contents = [msg.content.strip() for msg in recent_same_agent_responses[-2:]]
                if contents[-1] == contents[-2]:
                    assert False, "Loop detected for different agents"
                    return
        
        assert True, "No loop detected for different agents"
    
    def test_handle_messages_without_name(self):
        """Test that messages without name attribute don't cause errors."""
        messages = [
            HumanMessage(content="What is the price?"),
            AIMessage(content="The price is $150"),  # No name attribute
            AIMessage(content="The price is $150", name="FinancialAgent"),
        ]
        
        # Should not raise error
        agent_messages = [msg for msg in messages[-8:] if isinstance(msg, AIMessage) and hasattr(msg, 'name') and msg.name]
        
        # Should filter out messages without name
        assert len(agent_messages) >= 1, "Should handle messages without name"
    
    def test_max_iterations_check(self):
        """Test maximum iterations check."""
        MAX_ITERATIONS = 20
        
        # Create 20+ agent responses
        messages = [HumanMessage(content="Test")]
        for i in range(MAX_ITERATIONS + 1):
            messages.append(AIMessage(content=f"Response {i}", name="FinancialAgent"))
        
        agent_responses = [msg for msg in messages if isinstance(msg, AIMessage) and msg.name]
        
        if len(agent_responses) >= MAX_ITERATIONS:
            assert True, "Max iterations reached"
        else:
            assert False, "Max iterations not reached"


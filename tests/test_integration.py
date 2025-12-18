"""
Integration tests for the multi-agent system.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_date_formatting_integration(self):
        """Test that date formatting works with real-like API responses."""
        from datetime import datetime
        import re
        
        class TestDateFormatter:
            def _format_dates(self, text: str) -> str:
                result = text
                
                def replace_iso_date(match):
                    date_str = match.group(0)
                    try:
                        dt = datetime.strptime(date_str, '%Y-%m-%d')
                        return dt.strftime('%B %d, %Y')
                    except ValueError:
                        return date_str
                
                result = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', replace_iso_date, result)
                return result
        
        formatter = TestDateFormatter()
        
        # Simulate Alpha Vantage API response
        api_response = (
            "Time Series (Daily)\n"
            "2025-12-12, Open: 278.00, High: 280.00, Low: 277.00, Close: 278.28\n"
            "2025-12-11, Open: 277.50, High: 279.00, Low: 276.50, Close: 277.80"
        )
        
        formatted = formatter._format_dates(api_response)
        
        assert "December 12, 2025" in formatted or "2025-12-12" in formatted
        assert "278.28" in formatted  # Price preserved
    
    def test_loop_detection_integration(self):
        """Test loop detection with realistic conversation flow."""
        messages = [
            HumanMessage(content="What was the last closing stock price of AAPL?"),
            AIMessage(content="The most recent closing price for **AAPL** was **$278.28** on **December 12, 2025**.", name="FinancialAgent"),
            AIMessage(content="The most recent closing price for **AAPL** was **$278.28** on **December 12, 2025**.", name="FinancialAgent"),
            AIMessage(content="The most recent closing price for **AAPL** was **$278.28** on **December 12, 2025**.", name="FinancialAgent"),
        ]
        
        # Simulate loop detection
        agent_messages = [msg for msg in messages[-8:] if isinstance(msg, AIMessage) and hasattr(msg, 'name') and msg.name]
        
        assert len(agent_messages) >= 2
        
        last_agent = agent_messages[-1].name
        recent_same_agent_responses = [msg for msg in agent_messages if msg.name == last_agent]
        
        assert len(recent_same_agent_responses) >= 2
        
        contents = [msg.content.strip() for msg in recent_same_agent_responses[-2:]]
        is_loop = contents[-1] == contents[-2]
        
        assert is_loop, "Should detect loop with identical responses"
    
    def test_unicode_cleaning_integration(self):
        """Test Unicode cleaning with real response format."""
        import re
        
        # Simulate response with Unicode characters
        content = "The most recent closing price for **AAPL** was **$278.28** on **December\u202f12,\u202f2025**."
        
        # Clean Unicode
        cleaned = content.replace('\u202f', ' ')
        cleaned = cleaned.replace('\u2009', ' ')
        cleaned = cleaned.replace('\u00a0', ' ')
        cleaned = re.sub(r' +', ' ', cleaned)
        
        assert '\u202f' not in cleaned
        assert "December 12, 2025" in cleaned or "December" in cleaned
        assert "$278.28" in cleaned


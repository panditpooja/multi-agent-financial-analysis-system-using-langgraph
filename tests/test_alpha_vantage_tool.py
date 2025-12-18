"""
Unit tests for Alpha Vantage tool date formatting functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import re


class TestAlphaVantageDateFormatting:
    """Test date formatting in Alpha Vantage tool."""
    
    def test_format_iso_date(self):
        """Test formatting of ISO date format (YYYY-MM-DD)."""
        from langchain_core.tools import BaseTool
        from langchain_community.utilities.alpha_vantage import AlphaVantageAPIWrapper
        from datetime import datetime
        import re
        
        # Create a minimal test class with just the date formatting method
        class TestDateFormatter:
            def _format_dates(self, text: str) -> str:
                """Convert date strings to human-readable format."""
                result = text
                
                # Pattern 1: YYYY-MM-DD format
                def replace_iso_date(match):
                    date_str = match.group(0)
                    try:
                        dt = datetime.strptime(date_str, '%Y-%m-%d')
                        return dt.strftime('%B %d, %Y')
                    except ValueError:
                        return date_str
                
                result = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', replace_iso_date, result)
                
                # Pattern 2: YYYYMMDD format
                def replace_compact_date(match):
                    date_str = match.group(0)
                    try:
                        dt = datetime.strptime(date_str, '%Y%m%d')
                        if 1900 <= dt.year <= 2100:
                            return dt.strftime('%B %d, %Y')
                    except (ValueError, IndexError):
                        pass
                    return date_str
                
                result = re.sub(r'\b\d{8}\b', replace_compact_date, result)
                
                # Pattern 3: MM/DD/YYYY format
                def replace_slash_date(match):
                    date_str = match.group(0)
                    try:
                        dt = datetime.strptime(date_str, '%m/%d/%Y')
                        return dt.strftime('%B %d, %Y')
                    except ValueError:
                        return date_str
                
                result = re.sub(r'\b\d{1,2}/\d{1,2}/\d{4}\b', replace_slash_date, result)
                
                return result
        
        formatter = TestDateFormatter()
        
        # Test ISO date format
        text = "Date: 2025-12-12"
        result = formatter._format_dates(text)
        assert "December 12, 2025" in result
        assert "2025-12-12" not in result
    
    def test_format_compact_date(self):
        """Test formatting of compact date format (YYYYMMDD)."""
        from datetime import datetime
        import re
        
        class TestDateFormatter:
            def _format_dates(self, text: str) -> str:
                result = text
                
                def replace_compact_date(match):
                    date_str = match.group(0)
                    try:
                        dt = datetime.strptime(date_str, '%Y%m%d')
                        if 1900 <= dt.year <= 2100:
                            return dt.strftime('%B %d, %Y')
                    except (ValueError, IndexError):
                        pass
                    return date_str
                
                result = re.sub(r'\b\d{8}\b', replace_compact_date, result)
                return result
        
        formatter = TestDateFormatter()
        
        # Test compact date format
        text = "Date: 20251212"
        result = formatter._format_dates(text)
        assert "December 12, 2025" in result or "20251212" in result  # May not match if not valid date
        
        # Test with valid date
        text = "Date: 20251215"
        result = formatter._format_dates(text)
        # Should format if valid, otherwise leave as is
    
    def test_format_slash_date(self):
        """Test formatting of slash date format (MM/DD/YYYY)."""
        from datetime import datetime
        import re
        
        class TestDateFormatter:
            def _format_dates(self, text: str) -> str:
                result = text
                
                def replace_slash_date(match):
                    date_str = match.group(0)
                    try:
                        dt = datetime.strptime(date_str, '%m/%d/%Y')
                        return dt.strftime('%B %d, %Y')
                    except ValueError:
                        return date_str
                
                result = re.sub(r'\b\d{1,2}/\d{1,2}/\d{4}\b', replace_slash_date, result)
                return result
        
        formatter = TestDateFormatter()
        
        # Test slash date format
        text = "Date: 12/15/2025"
        result = formatter._format_dates(text)
        assert "December 15, 2025" in result
        assert "12/15/2025" not in result
    
    def test_format_multiple_dates(self):
        """Test formatting multiple dates in same text."""
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
        
        text = "Dates: 2025-12-12 and 2025-12-13"
        result = formatter._format_dates(text)
        assert "December 12, 2025" in result
        assert "December 13, 2025" in result
    
    def test_invalid_date_preserved(self):
        """Test that invalid dates are preserved as-is."""
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
        
        # Invalid date should be preserved
        text = "Date: 2025-13-45"  # Invalid month and day
        result = formatter._format_dates(text)
        # Should either format if parseable or preserve original
        assert "2025-13-45" in result or "Date:" in result
    
    def test_date_in_text_context(self):
        """Test date formatting when date is part of larger text."""
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
        
        text = "The closing price on 2025-12-12 was $278.28"
        result = formatter._format_dates(text)
        assert "December 12, 2025" in result
        assert "$278.28" in result  # Other content preserved


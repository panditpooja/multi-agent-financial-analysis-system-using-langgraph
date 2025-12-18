"""
Pytest configuration and fixtures for Multi-Agent Financial Analysis System tests.
"""
import pytest
import os
from unittest.mock import Mock, MagicMock
from langchain_core.messages import AIMessage, HumanMessage
from datetime import datetime


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    mock = MagicMock()
    mock.invoke.return_value = AIMessage(content="Test response")
    return mock


@pytest.fixture
def sample_messages():
    """Sample messages for testing."""
    return [
        HumanMessage(content="What is the price of AAPL?"),
        AIMessage(content="The price is $150.00", name="FinancialAgent"),
    ]


@pytest.fixture
def sample_state():
    """Sample state for testing."""
    return {
        "messages": [
            HumanMessage(content="What is the price of AAPL?"),
            AIMessage(content="The price is $150.00", name="FinancialAgent"),
        ],
        "next": "FINISH"
    }


@pytest.fixture
def mock_alpha_vantage_wrapper():
    """Mock Alpha Vantage API wrapper."""
    mock = MagicMock()
    mock._get_time_series_daily.return_value = (
        "Time Series (Daily)\n"
        "2025-12-12, Open: 278.00, High: 280.00, Low: 277.00, Close: 278.28\n"
        "2025-12-11, Open: 277.50, High: 279.00, Low: 276.50, Close: 277.80"
    )
    return mock


@pytest.fixture
def set_env_vars(monkeypatch):
    """Set environment variables for testing."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_openrouter_key")
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "test_alpha_vantage_key")
    monkeypatch.setenv("TAVILY_API_KEY", "test_tavily_key")


@pytest.fixture
def unset_env_vars(monkeypatch):
    """Unset environment variables for testing."""
    monkeypatch.delenv("ALPHA_VANTAGE_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)


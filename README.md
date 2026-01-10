# Multi-Agent Financial Analysis System using LangGraph

A sophisticated multi-agent financial analysis system built with LangGraph that utilizes a supervisor pattern to orchestrate specialized agents for complex financial queries. The system can fetch stock prices, search financial news, and generate visualizations.

## 🎯 Features

- **Multi-Agent Architecture**: Supervisor pattern with specialized agents
- **Django Web Interface**: Modern, responsive chat interface for easy interaction
- **Financial Data**: Real-time stock market data via Alpha Vantage API
- **Web Search**: Financial news and information via Tavily search (max 2 results per query)
- **Data Visualization**: Python REPL for generating charts and plots (saved to `static/plots/plot.png`)
- **Intelligent Routing**: Supervisor agent intelligently routes tasks to appropriate agents
- **Loop Detection**: Built-in infinite loop prevention with MAX_ITERATIONS=40
- **Message Truncation**: Automatically keeps only last 5 message pairs (10 messages) to prevent token limit errors
- **Date Formatting**: Automatic human-readable date conversion
- **Unicode Cleaning**: Automatic cleaning of problematic Unicode characters
- **Event Processing**: Proper handling of LangGraph event structure for displaying agent outputs
- **Metrics Dashboard**: Prometheus metrics integration for monitoring system performance
- **Response Length Control**: Agents are prompted to keep responses concise (1-2 paragraphs, max 1000 words)
- **Cache-Busting**: Automatic cache-busting for plot images to ensure fresh visualizations

## 🏗️ Architecture

The system consists of:

1. **Supervisor Agent**: Orchestrates the workflow and routes tasks to appropriate agents
2. **Financial Agent**: Fetches stock market data using Alpha Vantage API
3. **Web Search Agent**: Searches the web for financial news and information
4. **Code Agent**: Generates Python code for data visualization

## 📋 Prerequisites

- Python 3.8 or higher
- API Keys:
  - Groq API key (for LLM access via `openai/gpt-oss-120b`) OR OpenRouter API key (alternative)
  - Alpha Vantage API key (for stock data)
  - Tavily API key (optional, for web search)

## 🚀 Quick Start

### Option 1: Django Web Interface (Recommended)

1. **Clone or download the repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # On Linux/Mac:
   cp .env.example .env
   
   # On Windows:
   copy .env.example .env
   ```
   Then edit `.env` and add your API keys (see [Configuration](#-configuration) section below).

4. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start the Django server**:
   ```bash
   python manage.py runserver
   ```
   Or use the helper script:
   ```bash
   python run_django_server.py
   ```

6. **Open in browser**: Navigate to `http://127.0.0.1:8000/`

7. **Access metrics dashboard**: Navigate to `http://127.0.0.1:8000/metrics/`

### Option 2: Jupyter Notebook

1. **Follow steps 1-3 from Option 1**

2. **Start Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```

3. **Open and run** `research/multi_agent_system_financial_analysis.ipynb`

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step-by-Step Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install test dependencies** (optional, for running tests):
   ```bash
   pip install -r requirements-test.txt
   ```

3. **Set up environment variables** (see [Configuration](#-configuration) section)

## ⚙️ Configuration

### Environment Variables Setup

1. **Copy the example file**:
   ```bash
   # Linux/Mac:
   cp .env.example .env
   
   # Windows:
   copy .env.example .env
   ```

2. **Edit `.env` file** and add your actual API keys:

```env
# For Groq (currently used):
GROQ_API_KEY=your_groq_api_key_here

# OR for OpenRouter (alternative):
# OPENROUTER_API_KEY=your_openrouter_api_key_here

ALPHAVANTAGE_API_KEY=your_alpha_vantage_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional
```

### Getting API Keys

- **Groq**: Sign up at [Groq.com](https://console.groq.com/) and get your API key (currently using `openai/gpt-oss-120b` model)
- **OpenRouter**: Sign up at [OpenRouter.ai](https://openrouter.ai/) and get your API key (alternative LLM provider)
- **Alpha Vantage**: Get a free API key at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
- **Tavily**: Sign up at [Tavily](https://tavily.com/) for web search API (optional)

## 📖 Usage

### Using the Django Web Interface

1. **Start the server** (see [Quick Start](#-quick-start))

2. **Open** `http://127.0.0.1:8000/` in your browser

3. **Ask questions** in the chat interface, for example:
   - "What was the last closing stock price of AAPL?"
   - "Summarize the latest news about Tesla's stock performance."
   - "Draw a plot of the closing stock prices of WMT over the last week."
   - "Get me the stock information for NVDA"

4. **View metrics**: Navigate to `http://127.0.0.1:8000/metrics/` to see system performance metrics

### Running the Notebook

1. **Start Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```

2. **Open** `research/multi_agent_system_financial_analysis.ipynb`

3. **Run all cells** to initialize the system

4. **Example Queries**:

   ```python
   # Example 1: Get stock price
   config = {"configurable": {"thread_id": "1"}}
   events = graph.stream(
       {"messages": [HumanMessage(content="What was the last closing stock price of AAPL?")]},
       config=config
   )
   
   for event in events:
       process_event(event)
   ```

   ```python
   # Example 2: Search financial news
   config = {"configurable": {"thread_id": "2"}}
   events = graph.stream(
       {"messages": [HumanMessage(content="Summarize the latest news about Tesla's stock performance.")]},
       config=config
   )
   
   for event in events:
       process_event(event)
   ```

   ```python
   # Example 3: Generate visualization
   config = {"configurable": {"thread_id": "3"}}
   events = graph.stream(
       {"messages": [HumanMessage(content="Draw a plot of the closing stock prices of AAPL over the last week.")]},
       config=config
   )
   
   for event in events:
       process_event(event)
   ```

## 🧪 Testing

The project includes a comprehensive test suite:

1. **Install test dependencies**:
   ```bash
   pip install -r requirements-test.txt
   ```

2. **Run all tests**:
   ```bash
   pytest tests/
   ```
   Or use the test runner:
   ```bash
   python run_tests.py
   ```

3. **Run with coverage**:
   ```bash
   pytest tests/ --cov=tests --cov-report=html
   ```

See [tests/README.md](tests/README.md) for more testing information.

## 📁 Project Structure

```
.
├── agentic_ai_multi_gent_financial_analysis.py   # Main Python file (used by Django)
├── financial_ai/                                  # Django app
│   ├── views.py                                   # Django views (chat interface, metrics)
│   ├── urls.py                                    # URL routing
│   ├── settings.py                                # Django settings
│   └── ...
├── templates/financial_ai/                        # Django templates
│   ├── index.html                                 # Main chat interface
│   ├── metrics.html                               # Metrics dashboard
│   └── history.html                              # Query history (placeholder)
├── static/plots/                                  # Generated plot images
│   └── plot.png                                   # Latest generated plot
├── research/
│   └── multi_agent_system_financial_analysis.ipynb # Jupyter notebook
├── metrics_collector.py                           # Metrics collection module
├── metrics_integration.py                         # Metrics integration helpers
├── requirements.txt                               # Main dependencies
├── requirements-test.txt                          # Test dependencies
├── manage.py                                      # Django management script
├── run_django_server.py                           # Django server helper
├── .env.example                                   # Environment variables template
├── .gitignore                                     # Git ignore file
├── pytest.ini                                     # Pytest configuration
├── run_tests.py                                   # Test runner script
├── README.md                                      # This file
└── tests/                                         # Test suite
    ├── __init__.py
    ├── conftest.py                                # Pytest fixtures
    ├── test_alpha_vantage_tool.py                 # Date formatting tests
    ├── test_supervisor_loop_detection.py          # Loop detection tests
    ├── test_agent_node.py                          # Agent node tests
    ├── test_utils.py                               # Utility function tests
    ├── test_integration.py                         # Integration tests
    └── README.md                                   # Test documentation
```

## 🔧 Key Components

### Agents

- **Financial Agent**: Uses Alpha Vantage API to fetch stock market data
  - Automatically extracts ticker symbols from company names (e.g., "Microsoft" → "MSFT")
  - Never asks for clarification - always uses the tool
  - Automatically formats dates to human-readable format
  - Handles errors gracefully with informative messages
  - Provides data in structured format for visualization requests

- **Web Search Agent**: Uses Tavily to search for financial information
  - Returns comprehensive search results (max 2 results per query)
  - Synthesizes information from multiple sources
  - Keeps responses concise (1-2 paragraphs)

- **Code Agent**: Uses Python REPL for data visualization
  - Extracts data from conversation history
  - Generates plots and saves to `static/plots/plot.png`
  - Uses matplotlib with 'Agg' backend for web compatibility
  - Keeps responses brief (1-2 sentences)

- **Supervisor Agent**: Routes tasks and manages workflow
  - Detects task completion intelligently
  - Prevents infinite loops (MAX_ITERATIONS=40)
  - Manages agent transitions
  - Special handling for visualization requests (FinancialAgent → CodeAgent → FINISH)

### Features

- **Message Truncation**: Automatically keeps only last 5 message pairs (10 messages) to prevent token limit errors
- **Loop Detection**: Automatically detects and prevents infinite loops with multiple detection strategies
- **Date Formatting**: Converts dates from various formats to human-readable format
- **Unicode Cleaning**: Removes problematic Unicode characters from responses
- **Error Handling**: Comprehensive error handling throughout the system
- **State Management**: Uses LangGraph's checkpointing for state persistence
- **Plot Generation**: Saves plots to `static/plots/plot.png` with cache-busting timestamps
- **Metrics Collection**: Prometheus metrics for monitoring latency, reliability, and performance
- **Response Length Control**: All agents are prompted to keep responses concise

## 🛠️ Customization

### Changing the LLM Model

Edit the `get_llm()` function in `agentic_ai_multi_gent_financial_analysis.py`:

**For Groq (current)**:
```python
def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    return ChatOpenAI(
        model="openai/gpt-oss-120b",  # Change this to your preferred Groq model
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
        temperature=0,
        max_tokens=2000,
    )
```

**For OpenRouter (alternative)**:
```python
def get_llm():
    api_key = os.getenv("OPENROUTER_API_KEY")
    return ChatOpenAI(
        model="openai/gpt-4o-mini",  # Change this to your preferred model
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        temperature=0,
        max_tokens=2000
    )
```

**Note**: The current model is `openai/gpt-oss-120b` via Groq. Popular alternatives include:
- Groq: `llama-3.1-70b-versatile`, `mixtral-8x7b-32768`
- OpenRouter: `openai/gpt-4o-mini`, `openai/gpt-3.5-turbo`, `anthropic/claude-3-haiku`

### Adding New Agents

1. Create the agent in the notebook
2. Add it to the `members` dictionary in the supervisor configuration
3. Add the corresponding node to the graph
4. Update the `RouteResponse` schema

### Modifying Agent Prompts

Edit the `system_prompt` for each agent in the notebook:
- Web Search Agent
- Financial Agent  
- Code Agent
- Supervisor Agent

The exact cell numbers may vary, but you can search for "system_prompt" in the notebook to find each agent's configuration.

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure all API keys are set in `.env` file
   - Check that the `.env` file is in the root directory
   - Verify API keys are valid and have sufficient credits

2. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+)

3. **Infinite Loops**
   - The system has built-in loop detection (MAX_ITERATIONS=40), but if issues persist:
     - Check the supervisor prompt
     - Verify MAX_ITERATIONS is set to 40 in `agentic_ai_multi_gent_financial_analysis.py`
     - Review agent responses for identical content
     - Check logs for loop detection messages

4. **Token Limit Errors (Error code: 413)**
   - The system automatically truncates messages to last 10 messages (5 pairs)
   - If you still see token errors:
     - Verify `truncate_messages` reducer is being used in `AgentState`
     - Check that conversation history is being properly truncated
     - Consider reducing MAX_MESSAGES in `truncate_messages` function if needed

5. **Plot Not Displaying**
   - Check that `static/plots/plot.png` exists and was recently modified
   - Verify cache-busting timestamp is included in plot URL
   - Check browser console for image loading errors
   - Ensure matplotlib backend is set to 'Agg' (non-interactive)

4. **Date Formatting Issues**
   - Dates should automatically format, but if issues occur:
     - Check the date format in API responses
     - Verify the regex patterns in `_format_dates` method

## 📝 License

This project is provided as-is for educational and research purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)
- [Tavily API](https://docs.tavily.com/)
- [OpenRouter](https://openrouter.ai/)

## 🔮 Recent Improvements

- ✅ **Message Truncation**: Automatic conversation history management (last 10 messages)
- ✅ **Django Web Interface**: Modern chat interface with real-time responses
- ✅ **Metrics Dashboard**: Prometheus integration for performance monitoring
- ✅ **Improved Prompts**: Response length guidelines and better routing instructions
- ✅ **Plot Generation**: Saves plots to file with cache-busting for web display
- ✅ **Loop Prevention**: Enhanced supervisor logic with multiple detection strategies
- ✅ **Error Handling**: Comprehensive error handling and fallback mechanisms
- ✅ **Performance**: Using `time.perf_counter()` for accurate latency measurements

## 🔮 Future Enhancements

- [ ] Add more financial data sources (Yahoo Finance, Reuters)
- [ ] Implement reflection steps for quality improvement
- [ ] Add support for multiple stock tickers in single query
- [ ] Enhanced visualization capabilities (multiple chart types)
- [ ] Implement rate limiting per user/IP
- [ ] Add conversation export functionality
- [ ] Support for more LLM providers (Anthropic, Google, etc.)
- [ ] Add authentication and user management
- [ ] Implement query history persistence in database

## 📧 Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Note**: This system uses external APIs that may have rate limits and usage costs. Please review the terms of service for each API provider.


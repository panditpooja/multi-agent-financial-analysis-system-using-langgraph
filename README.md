# Multi-Agent Financial Analysis System using LangGraph

A sophisticated multi-agent financial analysis system built with LangGraph that utilizes a supervisor pattern to orchestrate specialized agents for complex financial queries. The system can fetch stock prices, search financial news, and generate visualizations.

## 🎯 Features

- **Multi-Agent Architecture**: Supervisor pattern with specialized agents
- **Financial Data**: Real-time stock market data via Alpha Vantage API
- **Web Search**: Financial news and information via Tavily search
- **Data Visualization**: Python REPL for generating charts and plots
- **Intelligent Routing**: Supervisor agent intelligently routes tasks to appropriate agents
- **Loop Detection**: Built-in infinite loop prevention
- **Date Formatting**: Automatic human-readable date conversion
- **Unicode Cleaning**: Automatic cleaning of problematic Unicode characters
- **Event Processing**: Proper handling of LangGraph event structure for displaying agent outputs

## 🏗️ Architecture

The system consists of:

1. **Supervisor Agent**: Orchestrates the workflow and routes tasks to appropriate agents
2. **Financial Agent**: Fetches stock market data using Alpha Vantage API
3. **Web Search Agent**: Searches the web for financial news and information
4. **Code Agent**: Generates Python code for data visualization

## 📋 Prerequisites

- Python 3.8 or higher
- API Keys:
  - OpenRouter API key (for LLM access)
  - Alpha Vantage API key (for stock data)
  - Tavily API key (optional, for web search)

## 🚀 Quick Start

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

4. **Start Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```

5. **Open and run** `multi_agent_system_financial_analysis.ipynb`

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
OPENROUTER_API_KEY=your_openrouter_api_key_here
ALPHAVANTAGE_API_KEY=your_alpha_vantage_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional
```

### Getting API Keys

- **OpenRouter**: Sign up at [OpenRouter.ai](https://openrouter.ai/) and get your API key
- **Alpha Vantage**: Get a free API key at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
- **Tavily**: Sign up at [Tavily](https://tavily.com/) for web search API (optional)

## 📖 Usage

### Running the Notebook

1. **Start Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```

2. **Open** `multi_agent_system_financial_analysis.ipynb`

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
├── multi_agent_system_financial_analysis.ipynb  # Main notebook
├── requirements.txt                               # Main dependencies
├── requirements-test.txt                         # Test dependencies
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
  - Automatically formats dates to human-readable format
  - Handles errors gracefully with informative messages

- **Web Search Agent**: Uses Tavily to search for financial information
  - Returns comprehensive search results

- **Code Agent**: Uses Python REPL for data visualization
  - Generates code for plots and charts

- **Supervisor Agent**: Routes tasks and manages workflow
  - Detects task completion
  - Prevents infinite loops
  - Manages agent transitions

### Features

- **Loop Detection**: Automatically detects and prevents infinite loops
- **Date Formatting**: Converts dates from various formats to human-readable format
- **Unicode Cleaning**: Removes problematic Unicode characters from responses
- **Error Handling**: Comprehensive error handling throughout the system
- **State Management**: Uses LangGraph's checkpointing for state persistence

## 🛠️ Customization

### Changing the LLM Model

Edit the model in the notebook (around Cell 3):
```python
llm = ChatOpenAI(
    model="nvidia/nemotron-nano-9b-v2:free",  # Change this to your preferred model
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    temperature=0,
    max_tokens=1000
)
```

**Note**: The current model is `nvidia/nemotron-nano-9b-v2:free`. You can use any model supported by OpenRouter. Popular alternatives include:
- `openai/gpt-4o-mini`
- `openai/gpt-3.5-turbo`
- `anthropic/claude-3-haiku`
- `google/gemini-pro`

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
   - The system has built-in loop detection, but if issues persist:
     - Check the supervisor prompt
     - Verify MAX_ITERATIONS is set appropriately
     - Review agent responses for identical content

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

## 🔮 Future Enhancements

- [ ] Add more financial data sources (Yahoo Finance, Reuters)
- [ ] Implement reflection steps for quality improvement
- [ ] Add support for multiple stock tickers
- [ ] Enhanced visualization capabilities
- [ ] Add conversation history management
- [ ] Implement rate limiting
- [ ] Add logging system
- [ ] Support for more LLM providers

## 📧 Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Note**: This system uses external APIs that may have rate limits and usage costs. Please review the terms of service for each API provider.


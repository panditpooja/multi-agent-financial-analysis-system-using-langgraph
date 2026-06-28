# Multi-Agent Financial Analysis System — LangGraph

A production-grade **multi-agent financial Q&A system** built with LangGraph, featuring a supervisor agent that dynamically routes queries across three domain-specialized AI agents with full Prometheus observability.

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-agentic-green)](https://langchain-ai.github.io/langgraph/)
[![Prometheus](https://img.shields.io/badge/Prometheus-observability-orange?logo=prometheus)](https://prometheus.io)
[![Django](https://img.shields.io/badge/Django-web_interface-092E20?logo=django)](https://djangoproject.com)

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│           Supervisor Agent          │  ← Intent classification + routing
│       (LangGraph StateGraph)        │  ← Loop prevention (MAX_ITERATIONS=40)
└──────┬──────────────┬───────────────┘
       │              │               │
       ▼              ▼               ▼
  ┌──────────┐  ┌───────────┐  ┌───────────┐
  │Financial │  │Web Search │  │   Code    │
  │  Agent   │  │   Agent   │  │   Agent   │
  │(Alpha    │  │ (Tavily)  │  │  (Python  │
  │Vantage)  │  │           │  │   REPL)   │
  └──────────┘  └───────────┘  └───────────┘
       │              │               │
       └──────────────┴───────────────┘
                      │
                      ▼
              Prometheus Metrics
         (latency · routing · errors)
                      │
                      ▼
           Django Web Interface
           + Jupyter Notebook
```

### Key Design Decisions

- **Supervisor routing** — Classifies intent and selects the appropriate domain agent rather than broadcasting to all agents, reducing token usage and improving response coherence.
- **Context engineering** — Shared `AgentState` maintains conversation history and tool outputs across agent hops, preventing redundant retrieval and enabling multi-turn reasoning.
- **Loop prevention** — `MAX_ITERATIONS=40` cycle detection guards against infinite supervisor ↔ agent loops on ambiguous queries. Message history is automatically truncated to the last 10 messages (5 pairs) to prevent token limit errors.
- **Prometheus observability** — Every routing decision, agent invocation, and response latency is instrumented with custom metrics, accessible via a built-in Django metrics dashboard.
- **Graceful degradation** — Automatic Unicode cleaning, date formatting, and error handling throughout all agent nodes.

---

## Features

- Natural language financial Q&A with domain-aware supervisor routing
- Real-time stock market data via Alpha Vantage API (auto-extracts ticker symbols from company names)
- Financial news search via Tavily (max 2 results per query)
- Python REPL for data visualization — plots saved to `static/plots/plot.png` with cache-busting
- Multi-turn conversational memory via LangGraph state management
- Django web interface with chat UI + Prometheus metrics dashboard
- Jupyter notebook for interactive exploration
- Comprehensive test suite (pytest)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph (StateGraph, conditional edges) |
| LLM integration | LangChain + Groq / OpenRouter |
| Financial data | Alpha Vantage API |
| Web search | Tavily API |
| Observability | Prometheus + custom metric exporters |
| Web interface | Django |
| Visualization | matplotlib (Agg backend) |
| Language | Python 3.8+ |
| Testing | pytest |

---

## Quick Start

### Option 1: Django Web Interface (Recommended)

```bash
git clone https://github.com/panditpooja/multi-agent-financial-analysis-system-using-langgraph.git
cd multi-agent-financial-analysis-system-using-langgraph
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env    # Linux/Mac
copy .env.example .env  # Windows
# Edit .env and add your API keys (see Configuration below)

python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the chat interface.  
Open `http://127.0.0.1:8000/metrics/` for the Prometheus dashboard.

### Option 2: Jupyter Notebook

```bash
# Follow steps above through pip install + .env setup, then:
jupyter notebook
# Open research/multi_agent_system_financial_analysis.ipynb
```

---

## Configuration

Edit `.env` with your API keys:

```env
# LLM Provider (choose one)
GROQ_API_KEY=your_groq_api_key_here
# OPENROUTER_API_KEY=your_openrouter_api_key_here  # alternative

# Financial data
ALPHAVANTAGE_API_KEY=your_alpha_vantage_api_key_here

# Web search (optional)
TAVILY_API_KEY=your_tavily_api_key_here
```

**Getting API keys:**
- **Groq**: [console.groq.com](https://console.groq.com/)
- **OpenRouter**: [openrouter.ai](https://openrouter.ai/)
- **Alpha Vantage**: [alphavantage.co](https://www.alphavantage.co/support/#api-key) (free tier available)
- **Tavily**: [tavily.com](https://tavily.com/) (optional, for web search)

---

## Usage Examples

**Django chat interface** — ask questions like:
- `"What was the last closing stock price of AAPL?"`
- `"Summarize the latest news about Tesla's stock performance."`
- `"Draw a plot of the closing stock prices of WMT over the last week."`

**Notebook:**
```python
config = {"configurable": {"thread_id": "1"}}
events = graph.stream(
    {"messages": [HumanMessage(content="What was the last closing stock price of AAPL?")]},
    config=config
)
for event in events:
    process_event(event)
```

---

## Testing

```bash
pip install -r requirements-test.txt
pytest tests/
pytest tests/ --cov=tests --cov-report=html   # with coverage
```

See [tests/README.md](tests/README.md) for full test documentation.

---

## Project Structure

```
├── agentic_ai_multi_gent_financial_analysis.py   # Main agent system
├── financial_ai/                                  # Django app
│   ├── views.py                                   # Chat interface + metrics views
│   ├── urls.py                                    # URL routing
│   └── settings.py                                # Django settings
├── templates/financial_ai/
│   ├── index.html                                 # Chat interface
│   └── metrics.html                               # Metrics dashboard
├── static/plots/                                  # Generated visualizations
├── research/
│   └── multi_agent_system_financial_analysis.ipynb
├── metrics_collector.py                           # Prometheus metrics
├── metrics_integration.py
├── requirements.txt
├── requirements-test.txt
├── .env.example
└── tests/
    ├── conftest.py
    ├── test_alpha_vantage_tool.py
    ├── test_supervisor_loop_detection.py
    ├── test_agent_node.py
    ├── test_utils.py
    └── test_integration.py
```

---

## Key Components

**Financial Agent** — Fetches stock data via Alpha Vantage. Auto-extracts ticker symbols (e.g., "Microsoft" → "MSFT"), formats dates to human-readable format, never asks for clarification.

**Web Search Agent** — Searches financial news via Tavily. Returns max 2 results per query, synthesizes into concise 1–2 paragraph summaries.

**Code Agent** — Python REPL for visualization. Extracts data from conversation history, generates plots with matplotlib (Agg backend), saves to `static/plots/plot.png`.

**Supervisor Agent** — Routes tasks, manages workflow, detects completion, prevents loops. Special handling for visualization requests: FinancialAgent → CodeAgent → FINISH.

---

## What I Learned

Building this system surfaced real challenges in production agentic design:

- **Loop detection is non-trivial** — simple cycle guards break multi-hop queries that legitimately revisit the supervisor. Solution: track routing history per turn, not globally. Added `MAX_ITERATIONS=40` as a hard fallback.
- **Context accumulation overhead** — passing full state on every edge is expensive. Used message truncation (last 10 messages) to prevent token limit errors at scale.
- **Routing confidence** — hard classification misroutes edge-case queries. Supervisor prompt engineering and completion detection logic were the biggest tuning areas.
- **Web interface integration** — wiring LangGraph's streaming event structure to a Django chat UI required careful event processing to extract and display agent outputs correctly.

---

## Recent Improvements

- ✅ **Message Truncation** — automatic conversation history management (last 10 messages)
- ✅ **Django Web Interface** — modern chat UI with real-time streaming responses
- ✅ **Metrics Dashboard** — Prometheus integration for routing + latency monitoring
- ✅ **Loop Prevention** — enhanced supervisor logic with multiple detection strategies
- ✅ **Plot Generation** — cache-busting timestamps for always-fresh visualizations
- ✅ **Error Handling** — comprehensive fallback mechanisms across all agent nodes

---

## Future Enhancements

- [ ] Additional financial data sources (Yahoo Finance, Reuters)
- [ ] Reflection steps for response quality improvement
- [ ] Multi-ticker batch queries
- [ ] Enhanced visualization (multiple chart types)
- [ ] Rate limiting per user/IP
- [ ] Conversation export + history persistence
- [ ] Authentication and user management

---

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)
- [Tavily API](https://docs.tavily.com/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)

---

## Contributing

Contributions welcome — please open an issue or submit a pull request.

## License

Provided as-is for educational and research purposes.

---

## Author

**Pooja Diwakar Pandit**  
M.S. Information Science (Machine Learning), University of Arizona — GPA 4.0 | IEEE First Author  
[LinkedIn](https://www.linkedin.com/in/pooja-pandit-177978135/) · [Portfolio](https://poojapandit.pythonanywhere.com) · [GitHub](https://github.com/panditpooja)

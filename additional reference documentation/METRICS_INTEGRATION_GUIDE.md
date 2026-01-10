# Metrics Integration Guide

This guide explains how to integrate comprehensive metrics tracking into your multi-agent financial analysis system.

## Overview

The metrics system provides:

1. **Latency & Performance Metrics**
   - End-to-end response time (p50, p95)
   - Tool call latency per tool (Alpha Vantage, Tavily, Python REPL)
   - Agent transition counts
   - Tool call counts and latency per tool

2. **Reliability & Robustness Metrics**
   - Success rate (% of queries completed without failure)
   - Error rate (API failures, timeouts, invalid inputs)
   - Recovery rate (% of failed tool calls that succeed after retry)
   - Tool-specific success rates

3. **Loop Prevention Metrics**
   - Number of loops detected/prevented
   - Percentage of conversations needing supervisor intervention

4. **Prometheus Metrics Endpoint**
   - HTTP endpoint at `/metrics` for Prometheus scraping
   - All metrics exposed as Prometheus-compatible format

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

This will install `prometheus-client` which is required for the Prometheus endpoint.

## Quick Start

### Option 1: Minimal Integration (Recommended)

Add these lines to your notebook **after** creating all tools and agents, but **before** compiling the graph:

```python
# Import metrics integration
from metrics_integration import (
    setup_metrics,
    instrument_all_tools,
    instrument_all_agents,
    instrument_graph
)

# Initialize metrics (starts Prometheus server on port 8000)
metrics = setup_metrics(enable_prometheus=True, prometheus_port=8000)

# Instrument all tools
alpha_vantage_tool, tavily_tool, python_repl_tool = instrument_all_tools(
    alpha_vantage_tool,
    tavily_tool,
    python_repl_tool,
    get_current_date_tool=get_current_date
)

# Instrument all agent nodes
web_search_node, financial_node, code_node, supervisor_agent = instrument_all_agents(
    web_search_node,
    financial_node,
    code_node,
    supervisor_agent
)

# Recreate the graph with instrumented nodes
workflow = StateGraph(AgentState)
workflow.add_node("WebSearchAgent", web_search_node)
workflow.add_node("FinancialAgent", financial_node)
workflow.add_node("CodeAgent", code_node)
workflow.add_node("Supervisor", supervisor_agent)

# ... rest of graph setup ...

# Compile graph
graph = workflow.compile(checkpointer=memory)

# Instrument the graph stream method
graph = instrument_graph(graph)
```

### Option 2: Manual Integration

If you prefer more control, you can instrument components individually:

```python
from metrics_collector import get_metrics_collector
from instrumentation import instrument_tool, instrument_agent_node, instrument_supervisor

# Initialize metrics
metrics = get_metrics_collector(enable_prometheus=True, prometheus_port=8000)

# Instrument individual tools
instrument_tool(alpha_vantage_tool, "alpha_vantage")
instrument_tool(tavily_tool, "tavily")
instrument_tool(python_repl_tool, "python_repl")

# Instrument agent nodes
web_search_node = instrument_agent_node(web_search_node, "WebSearchAgent")
financial_node = instrument_agent_node(financial_node, "FinancialAgent")
code_node = instrument_agent_node(code_node, "CodeAgent")
supervisor_agent = instrument_supervisor(supervisor_agent)
```

## Viewing Metrics

### In Python/Notebook

```python
from metrics_integration import print_metrics_summary, get_metrics_json

# Print formatted summary
print_metrics_summary()

# Get metrics as dictionary
metrics_dict = get_metrics_json()
```

### Via Command Line

```bash
# Print formatted summary
python view_metrics.py

# Output as JSON
python view_metrics.py --json

# Show Prometheus endpoint info
python view_metrics.py --prometheus
```

### Via Prometheus Endpoint

Once the metrics system is initialized, you can access metrics at:

```
http://localhost:8000/metrics
```

You can:
- View in browser
- Scrape with Prometheus server
- Use with Grafana for visualization

## Metrics Details

### Latency Metrics

- `agent_query_latency_seconds`: Histogram of end-to-end query latencies
- `agent_tool_latency_seconds{tool_type="..."}`: Histogram of tool call latencies per tool

### Count Metrics

- `agent_transitions_total{from_agent="...", to_agent="..."}`: Counter of agent transitions
- `agent_tool_calls_total{tool_type="...", status="success|failure"}`: Counter of tool calls
- `agent_queries_total{status="success|failure"}`: Counter of queries

### Error Metrics

- `agent_errors_total{error_type="...", tool_type="..."}`: Counter of errors by type and tool
- `agent_tool_recoveries_total{tool_type="..."}`: Counter of successful recoveries

### Loop Prevention Metrics

- `agent_loops_detected_total`: Counter of loops detected
- `agent_supervisor_interventions_total`: Counter of supervisor interventions

### Gauge Metrics

- `agent_active_queries`: Current number of active queries
- `agent_tool_call_count{tool_type="..."}`: Total tool calls per tool

## Example Usage in Notebook

```python
# After running some queries, view metrics
from metrics_integration import print_metrics_summary

# Run a query
config = {"configurable": {"thread_id": "test_1"}}
events = graph.stream(
    {"messages": [HumanMessage(content="What was the last closing stock price of AAPL?")]},
    config=config
)

for event in events:
    process_event(event)

# View metrics
print_metrics_summary()
```

## Advanced Configuration

### Custom Prometheus Port

```python
metrics = setup_metrics(enable_prometheus=True, prometheus_port=9090)
```

### Disable Prometheus (use in-memory metrics only)

```python
metrics = setup_metrics(enable_prometheus=False)
```

### Access Metrics Programmatically

```python
from metrics_collector import get_metrics_collector

metrics = get_metrics_collector()

# Get specific metrics
p50, p95 = metrics.get_query_latency_percentiles()
success_rate = metrics.get_success_rate()
tool_latency = metrics.get_tool_latency_percentiles("alpha_vantage")
```

## Troubleshooting

### Prometheus Server Won't Start

If you see an error about the port being in use:
1. Change the port: `setup_metrics(prometheus_port=8001)`
2. Or stop the existing server using that port

### Metrics Not Appearing

1. Make sure you've instrumented all tools and agents
2. Make sure you're calling `graph.stream()` (not `graph.invoke()`)
3. Check that thread_id is being passed in config

### Import Errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Integration with Monitoring Tools

### Prometheus + Grafana

1. Configure Prometheus to scrape `http://localhost:8000/metrics`
2. Create Grafana dashboards using the metrics
3. Set up alerts based on metrics thresholds

### Example Prometheus Config

```yaml
scrape_configs:
  - job_name: 'multi-agent-system'
    static_configs:
      - targets: ['localhost:8000']
```

## Notes

- Metrics are stored in-memory and will reset when the Python process restarts
- For persistent metrics, consider using Prometheus with persistent storage
- The metrics collector is thread-safe and can handle concurrent queries
- Tool call tracking requires the tool to be instrumented before use


"""
Integration helper for adding metrics to the multi-agent system.

This module provides helper functions to easily instrument the existing
multi-agent system with comprehensive metrics collection.
"""

from metrics_collector import get_metrics_collector, ToolType
from instrumentation import (
    instrument_tool,
    instrument_agent_node,
    instrument_supervisor,
    instrument_graph_stream
)


def setup_metrics(enable_prometheus: bool = True, prometheus_port: int = 8000):
    """Initialize the metrics collector.
    
    Args:
        enable_prometheus: Whether to enable Prometheus metrics
        prometheus_port: Port for Prometheus HTTP server
    """
    return get_metrics_collector(
        enable_prometheus=enable_prometheus,
        prometheus_port=prometheus_port
    )


def instrument_all_tools(
    alpha_vantage_tool,
    tavily_tool,
    python_repl_tool,
    get_current_date_tool=None
):
    """Instrument all tools with metrics tracking.
    
    Args:
        alpha_vantage_tool: Alpha Vantage tool instance
        tavily_tool: Tavily search tool instance
        python_repl_tool: Python REPL tool instance
        get_current_date_tool: Optional current date tool instance
        
    Returns:
        Tuple of instrumented tools
    """
    # Instrument Alpha Vantage
    instrument_tool(alpha_vantage_tool, ToolType.ALPHA_VANTAGE.value)
    
    # Instrument Tavily
    instrument_tool(tavily_tool, ToolType.TAVILY.value)
    
    # Instrument Python REPL
    instrument_tool(python_repl_tool, ToolType.PYTHON_REPL.value)
    
    # Instrument get_current_date if provided
    if get_current_date_tool:
        instrument_tool(get_current_date_tool, ToolType.GET_CURRENT_DATE.value)
    
    return alpha_vantage_tool, tavily_tool, python_repl_tool


def instrument_all_agents(
    web_search_node,
    financial_node,
    code_node,
    supervisor_agent
):
    """Instrument all agent nodes with metrics tracking.
    
    Args:
        web_search_node: Web search agent node function
        financial_node: Financial agent node function
        code_node: Code agent node function
        supervisor_agent: Supervisor agent function
        
    Returns:
        Tuple of instrumented agent nodes
    """
    # Instrument agent nodes
    web_search_node = instrument_agent_node(web_search_node, "WebSearchAgent")
    financial_node = instrument_agent_node(financial_node, "FinancialAgent")
    code_node = instrument_agent_node(code_node, "CodeAgent")
    supervisor_agent = instrument_supervisor(supervisor_agent)
    
    return web_search_node, financial_node, code_node, supervisor_agent


def instrument_graph(graph):
    """Instrument a compiled graph with metrics tracking.
    
    Args:
        graph: The compiled LangGraph graph
        
    Returns:
        Instrumented graph
    """
    # Wrap the stream method
    original_stream = graph.stream
    graph.stream = instrument_graph_stream(original_stream)
    
    return graph


def print_metrics_summary():
    """Print a formatted summary of current metrics."""
    metrics = get_metrics_collector()
    summary = metrics.get_summary()
    
    print("\n" + "="*80)
    print("METRICS SUMMARY")
    print("="*80)
    
    # Latency & Performance
    print("\n📊 LATENCY & PERFORMANCE")
    print("-" * 80)
    latency = summary['latency_performance']['end_to_end_response_time']
    print(f"  End-to-End Response Time:")
    print(f"    P50: {latency['p50_seconds']:.3f} seconds")
    print(f"    P95: {latency['p95_seconds']:.3f} seconds")
    
    print(f"\n  Tool Call Latency:")
    for tool, latencies in summary['latency_performance']['tool_calls_latency_per_tool'].items():
        print(f"    {tool}:")
        print(f"      P50: {latencies['p50']:.3f} seconds")
        print(f"      P95: {latencies['p95']:.3f} seconds")
    
    print(f"\n  Agent Transitions: {summary['latency_performance']['agent_transitions_count']}")
    print(f"  Tool Calls Count: {summary['latency_performance']['tool_calls_count']}")
    
    # Reliability & Robustness
    print("\n🛡️  RELIABILITY & ROBUSTNESS")
    print("-" * 80)
    print(f"  Success Rate: {summary['reliability_robustness']['success_rate_percent']:.2f}%")
    
    error_rate = summary['reliability_robustness']['error_rate']
    print(f"\n  Error Rate:")
    print(f"    Total Errors: {error_rate['total_errors']}")
    print(f"    API Failures: {error_rate['api_failures']}")
    print(f"    Timeouts: {error_rate['timeouts']}")
    print(f"    Invalid Inputs: {error_rate['invalid_inputs']}")
    print(f"    Errors by Tool: {error_rate['errors_by_tool']}")
    
    print(f"\n  Recovery Rate: {summary['reliability_robustness']['recovery_rate_percent']:.2f}%")
    
    print(f"\n  Tool Success Rates:")
    for tool, rate in summary['reliability_robustness']['tool_success_rates'].items():
        print(f"    {tool}: {rate:.2f}%")
    
    # Loop Prevention
    print("\n🔄 LOOP PREVENTION")
    print("-" * 80)
    loop_prevention = summary['loop_prevention']
    print(f"  Loops Detected: {loop_prevention['loops_detected']}")
    print(f"  Queries with Loops: {loop_prevention['queries_with_loops']}")
    print(f"  Percentage Queries with Loops: {loop_prevention['percentage_queries_with_loops']:.2f}%")
    
    # Supervisor Interventions
    print("\n👮 SUPERVISOR INTERVENTIONS")
    print("-" * 80)
    interventions = summary['supervisor_interventions']
    print(f"  Total Interventions: {interventions['total']}")
    print(f"  Percentage Queries Needing Intervention: {interventions['percentage_queries_needing_intervention']:.2f}%")
    
    # Totals
    print("\n📈 TOTALS")
    print("-" * 80)
    totals = summary['totals']
    print(f"  Total Queries: {totals['total_queries']}")
    print(f"  Successful Queries: {totals['successful_queries']}")
    print(f"  Failed Queries: {totals['failed_queries']}")
    print(f"  Total Tool Calls: {totals['total_tool_calls']}")
    print(f"  Recovered Tool Calls: {totals['recovered_tool_calls']}")
    
    print("\n" + "="*80)
    
    # Prometheus info
    metrics_collector = get_metrics_collector()
    if metrics_collector.prometheus_enabled:
        print(f"\n📊 Prometheus metrics available at: http://localhost:{metrics_collector.prometheus_port}/metrics")
    
    print("\n")


def get_metrics_json():
    """Get metrics as JSON-serializable dictionary.
    
    Returns:
        Dictionary with all metrics
    """
    metrics = get_metrics_collector()
    return metrics.get_summary()


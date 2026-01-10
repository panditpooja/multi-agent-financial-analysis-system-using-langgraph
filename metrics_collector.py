"""
Metrics collection module for the Multi-Agent Financial Analysis System.

This module provides comprehensive metrics tracking including:
- Latency and performance metrics (p50, p95)
- Tool call latency per tool
- Agent transitions
- Success/error rates
- Recovery rates
- Loop prevention effectiveness
"""

import time
import threading
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import statistics

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("Warning: prometheus_client not installed. Prometheus metrics will be disabled.")


class ToolType(Enum):
    """Enumeration of tool types."""
    ALPHA_VANTAGE = "alpha_vantage"
    TAVILY = "tavily"
    PYTHON_REPL = "python_repl"
    GET_CURRENT_DATE = "get_current_date"


class AgentType(Enum):
    """Enumeration of agent types."""
    SUPERVISOR = "Supervisor"
    WEB_SEARCH = "WebSearchAgent"
    FINANCIAL = "FinancialAgent"
    CODE = "CodeAgent"


@dataclass
class ToolCallMetrics:
    """Metrics for a single tool call."""
    tool_type: str
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    @property
    def latency(self) -> Optional[float]:
        """Calculate latency in seconds."""
        if self.end_time is not None:
            return self.end_time - self.start_time
        return None


@dataclass
class QueryMetrics:
    """Metrics for a complete query execution."""
    query_id: str
    thread_id: str
    start_time: float
    end_time: Optional[float] = None
    agent_transitions: List[str] = field(default_factory=list)
    tool_calls: List[ToolCallMetrics] = field(default_factory=list)
    loops_detected: int = 0
    supervisor_interventions: int = 0
    completed: bool = False
    error: Optional[str] = None
    
    @property
    def end_to_end_latency(self) -> Optional[float]:
        """Calculate end-to-end latency in seconds."""
        if self.end_time is not None:
            return self.end_time - self.start_time
        return None
    
    @property
    def agent_transition_count(self) -> int:
        """Get the number of agent transitions."""
        return len(self.agent_transitions)
    
    @property
    def tool_call_count(self) -> int:
        """Get the number of tool calls."""
        return len(self.tool_calls)
    
    @property
    def success(self) -> bool:
        """Check if query completed successfully."""
        return self.completed and self.error is None


class MetricsCollector:
    """Central metrics collector for the multi-agent system."""
    
    def __init__(self, enable_prometheus: bool = True, prometheus_port: int = 8000):
        """Initialize the metrics collector.
        
        Args:
            enable_prometheus: Whether to enable Prometheus metrics
            prometheus_port: Port for Prometheus HTTP server
        """
        self._lock = threading.Lock()
        self._queries: Dict[str, QueryMetrics] = {}
        self._active_queries: Dict[str, str] = {}  # thread_id -> query_id mapping
        
        # In-memory metrics storage
        self._tool_latencies: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._query_latencies: deque = deque(maxlen=1000)
        self._tool_call_counts: Dict[str, int] = defaultdict(int)
        self._tool_error_counts: Dict[str, int] = defaultdict(int)
        self._tool_success_counts: Dict[str, int] = defaultdict(int)
        self._agent_transition_counts: Dict[str, int] = defaultdict(int)
        self._loop_detections: int = 0
        self._supervisor_interventions: int = 0
        self._total_queries: int = 0
        self._successful_queries: int = 0
        self._failed_queries: int = 0
        self._recovered_tool_calls: int = 0
        self._failed_tool_calls: int = 0
        
        # Prometheus metrics
        self.prometheus_enabled = enable_prometheus and PROMETHEUS_AVAILABLE
        self.prometheus_port = prometheus_port
        
        if self.prometheus_enabled:
            self._init_prometheus_metrics()
            try:
                start_http_server(self.prometheus_port)
                print(f"✅ Prometheus metrics server started on port {self.prometheus_port}")
            except Exception as e:
                print(f"⚠️  Failed to start Prometheus server: {e}")
                self.prometheus_enabled = False
        else:
            print("ℹ️  Prometheus metrics disabled")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        # End-to-end query latency (p50, p95)
        self.prom_query_latency = Histogram(
            'agent_query_latency_seconds',
            'End-to-end query latency in seconds',
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        )
        
        # Tool call latency per tool
        self.prom_tool_latency = Histogram(
            'agent_tool_latency_seconds',
            'Tool call latency in seconds',
            ['tool_type'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        # Agent transitions
        self.prom_agent_transitions = Counter(
            'agent_transitions_total',
            'Total number of agent transitions',
            ['from_agent', 'to_agent']
        )
        
        # Tool calls count
        self.prom_tool_calls = Counter(
            'agent_tool_calls_total',
            'Total number of tool calls',
            ['tool_type', 'status']
        )
        
        # Query success/failure
        self.prom_query_success = Counter(
            'agent_queries_total',
            'Total number of queries',
            ['status']
        )
        
        # Error rates
        self.prom_errors = Counter(
            'agent_errors_total',
            'Total number of errors',
            ['error_type', 'tool_type']
        )
        
        # Recovery rate
        self.prom_recoveries = Counter(
            'agent_tool_recoveries_total',
            'Total number of successful tool call recoveries',
            ['tool_type']
        )
        
        # Loop detection
        self.prom_loops_detected = Counter(
            'agent_loops_detected_total',
            'Total number of loops detected'
        )
        
        # Supervisor interventions
        self.prom_supervisor_interventions = Counter(
            'agent_supervisor_interventions_total',
            'Total number of supervisor interventions'
        )
        
        # Active queries gauge
        self.prom_active_queries = Gauge(
            'agent_active_queries',
            'Number of currently active queries'
        )
        
        # Tool call counts per tool
        self.prom_tool_call_count = Gauge(
            'agent_tool_call_count',
            'Total number of tool calls per tool',
            ['tool_type']
        )
    
    def start_query(self, thread_id: str, query_id: Optional[str] = None) -> str:
        """Start tracking a new query.
        
        Args:
            thread_id: Thread ID for the query
            query_id: Optional query ID (generated if not provided)
            
        Returns:
            Query ID
        """
        if query_id is None:
            query_id = f"{thread_id}_{int(time.time() * 1000)}"
        
        with self._lock:
            query_metrics = QueryMetrics(
                query_id=query_id,
                thread_id=thread_id,
                start_time=time.perf_counter()
            )
            self._queries[query_id] = query_metrics
            self._active_queries[thread_id] = query_id
            self._total_queries += 1
            
            if self.prometheus_enabled:
                self.prom_active_queries.inc()
        
        return query_id
    
    def end_query(self, thread_id: str, success: bool = True, error: Optional[str] = None):
        """End tracking a query.
        
        Args:
            thread_id: Thread ID for the query
            success: Whether the query completed successfully
            error: Error message if query failed
        """
        with self._lock:
            query_id = self._active_queries.get(thread_id)
            if query_id is None:
                return
            
            query_metrics = self._queries.get(query_id)
            if query_metrics is None:
                return
            
            query_metrics.end_time = time.perf_counter()
            query_metrics.completed = True
            query_metrics.error = error
            
            # Update aggregated metrics
            latency = query_metrics.end_to_end_latency
            if latency is not None:
                self._query_latencies.append(latency)
                if self.prometheus_enabled:
                    self.prom_query_latency.observe(latency)
            
            if success:
                self._successful_queries += 1
                if self.prometheus_enabled:
                    self.prom_query_success.labels(status='success').inc()
            else:
                self._failed_queries += 1
                if self.prometheus_enabled:
                    self.prom_query_success.labels(status='failure').inc()
            
            # Remove from active queries
            if thread_id in self._active_queries:
                del self._active_queries[thread_id]
            
            if self.prometheus_enabled:
                self.prom_active_queries.dec()
    
    def record_agent_transition(self, thread_id: str, from_agent: str, to_agent: str):
        """Record an agent transition.
        
        Args:
            thread_id: Thread ID for the query
            from_agent: Source agent name
            to_agent: Target agent name
        """
        with self._lock:
            query_id = self._active_queries.get(thread_id)
            if query_id:
                query_metrics = self._queries.get(query_id)
                if query_metrics:
                    query_metrics.agent_transitions.append(f"{from_agent} -> {to_agent}")
            
            self._agent_transition_counts[to_agent] += 1
            
            if self.prometheus_enabled:
                self.prom_agent_transitions.labels(
                    from_agent=from_agent,
                    to_agent=to_agent
                ).inc()
    
    def start_tool_call(self, thread_id: str, tool_type: str) -> str:
        """Start tracking a tool call.
        
        Args:
            thread_id: Thread ID for the query
            tool_type: Type of tool being called
            
        Returns:
            Tool call ID
        """
        tool_call_id = f"{tool_type}_{int(time.time() * 1000000)}"
        
        with self._lock:
            query_id = self._active_queries.get(thread_id)
            if query_id:
                query_metrics = self._queries.get(query_id)
                if query_metrics:
                    tool_metrics = ToolCallMetrics(
                        tool_type=tool_type,
                        start_time=time.perf_counter()
                    )
                    query_metrics.tool_calls.append(tool_metrics)
                    return tool_call_id
        
        return tool_call_id
    
    def end_tool_call(
        self,
        thread_id: str,
        tool_type: str,
        success: bool = True,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
        retry_count: int = 0
    ):
        """End tracking a tool call.
        
        Args:
            thread_id: Thread ID for the query
            tool_type: Type of tool that was called
            success: Whether the tool call succeeded
            error_type: Type of error if failed
            error_message: Error message if failed
            retry_count: Number of retries attempted
        """
        with self._lock:
            query_id = self._active_queries.get(thread_id)
            if query_id:
                query_metrics = self._queries.get(query_id)
                if query_metrics and query_metrics.tool_calls:
                    # Update the last tool call of this type
                    for tool_metrics in reversed(query_metrics.tool_calls):
                        if tool_metrics.tool_type == tool_type and tool_metrics.end_time is None:
                            tool_metrics.end_time = time.perf_counter()
                            tool_metrics.success = success
                            tool_metrics.error_type = error_type
                            tool_metrics.error_message = error_message
                            tool_metrics.retry_count = retry_count
                            
                            # Update aggregated metrics
                            latency = tool_metrics.latency
                            if latency is not None:
                                self._tool_latencies[tool_type].append(latency)
                                if self.prometheus_enabled:
                                    self.prom_tool_latency.labels(tool_type=tool_type).observe(latency)
                            
                            break
            
            # Update counters
            self._tool_call_counts[tool_type] += 1
            if success:
                self._tool_success_counts[tool_type] += 1
                if retry_count > 0:
                    self._recovered_tool_calls += 1
                    if self.prometheus_enabled:
                        self.prom_recoveries.labels(tool_type=tool_type).inc(retry_count)
            else:
                self._tool_error_counts[tool_type] += 1
                self._failed_tool_calls += 1
            
            # Update Prometheus metrics
            if self.prometheus_enabled:
                status = 'success' if success else 'failure'
                self.prom_tool_calls.labels(tool_type=tool_type, status=status).inc()
                
                if error_type:
                    self.prom_errors.labels(
                        error_type=error_type,
                        tool_type=tool_type
                    ).inc()
                
                self.prom_tool_call_count.labels(tool_type=tool_type).inc()
    
    def record_loop_detection(self, thread_id: str):
        """Record a loop detection event.
        
        Args:
            thread_id: Thread ID for the query
        """
        with self._lock:
            query_id = self._active_queries.get(thread_id)
            if query_id:
                query_metrics = self._queries.get(query_id)
                if query_metrics:
                    query_metrics.loops_detected += 1
            
            self._loop_detections += 1
            
            if self.prometheus_enabled:
                self.prom_loops_detected.inc()
    
    def record_supervisor_intervention(self, thread_id: str):
        """Record a supervisor intervention.
        
        Args:
            thread_id: Thread ID for the query
        """
        with self._lock:
            query_id = self._active_queries.get(thread_id)
            if query_id:
                query_metrics = self._queries.get(query_id)
                if query_metrics:
                    query_metrics.supervisor_interventions += 1
            
            self._supervisor_interventions += 1
            
            if self.prometheus_enabled:
                self.prom_supervisor_interventions.inc()
    
    # Statistics methods
    def get_query_latency_percentiles(self) -> Dict[str, float]:
        """Get p50 and p95 latency percentiles for queries.
        
        Returns:
            Dictionary with 'p50' and 'p95' keys
        """
        with self._lock:
            if len(self._query_latencies) == 0:
                return {'p50': 0.0, 'p95': 0.0}
            
            latencies = sorted(self._query_latencies)
            p50_idx = int(len(latencies) * 0.5)
            p95_idx = int(len(latencies) * 0.95)
            
            return {
                'p50': latencies[p50_idx] if p50_idx < len(latencies) else 0.0,
                'p95': latencies[p95_idx] if p95_idx < len(latencies) else 0.0
            }
    
    def get_tool_latency_percentiles(self, tool_type: str) -> Dict[str, float]:
        """Get p50 and p95 latency percentiles for a specific tool.
        
        Args:
            tool_type: Type of tool
            
        Returns:
            Dictionary with 'p50' and 'p95' keys
        """
        with self._lock:
            latencies = self._tool_latencies.get(tool_type, deque())
            if len(latencies) == 0:
                return {'p50': 0.0, 'p95': 0.0}
            
            sorted_latencies = sorted(latencies)
            p50_idx = int(len(sorted_latencies) * 0.5)
            p95_idx = int(len(sorted_latencies) * 0.95)
            
            return {
                'p50': sorted_latencies[p50_idx] if p50_idx < len(sorted_latencies) else 0.0,
                'p95': sorted_latencies[p95_idx] if p95_idx < len(sorted_latencies) else 0.0
            }
    
    def get_success_rate(self) -> float:
        """Get overall query success rate.
        
        Returns:
            Success rate as a percentage (0-100)
        """
        with self._lock:
            total = self._total_queries
            if total == 0:
                return 0.0
            return (self._successful_queries / total) * 100.0
    
    def get_tool_success_rate(self, tool_type: str) -> float:
        """Get success rate for a specific tool.
        
        Args:
            tool_type: Type of tool
            
        Returns:
            Success rate as a percentage (0-100)
        """
        with self._lock:
            total = self._tool_call_counts.get(tool_type, 0)
            if total == 0:
                return 0.0
            success = self._tool_success_counts.get(tool_type, 0)
            return (success / total) * 100.0
    
    def get_recovery_rate(self) -> float:
        """Get recovery rate for failed tool calls.
        
        Returns:
            Recovery rate as a percentage (0-100)
        """
        with self._lock:
            total_failed = self._failed_tool_calls
            if total_failed == 0:
                return 0.0
            return (self._recovered_tool_calls / total_failed) * 100.0
    
    def get_loop_prevention_effectiveness(self) -> Dict[str, Any]:
        """Get loop prevention effectiveness metrics.
        
        Returns:
            Dictionary with loop detection statistics
        """
        with self._lock:
            total_queries = self._total_queries
            if total_queries == 0:
                return {
                    'loops_detected': 0,
                    'queries_with_loops': 0,
                    'percentage_queries_with_loops': 0.0
                }
            
            queries_with_loops = sum(
                1 for q in self._queries.values()
                if q.loops_detected > 0
            )
            
            return {
                'loops_detected': self._loop_detections,
                'queries_with_loops': queries_with_loops,
                'percentage_queries_with_loops': (queries_with_loops / total_queries) * 100.0
            }
    
    def get_supervisor_intervention_rate(self) -> float:
        """Get percentage of queries that needed supervisor intervention.
        
        Returns:
            Intervention rate as a percentage (0-100)
        """
        with self._lock:
            total_queries = self._total_queries
            if total_queries == 0:
                return 0.0
            
            queries_with_intervention = sum(
                1 for q in self._queries.values()
                if q.supervisor_interventions > 0
            )
            
            return (queries_with_intervention / total_queries) * 100.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all metrics.
        
        Returns:
            Dictionary with all metrics
        """
        # Note: We don't acquire the lock here because all helper methods
        # (get_query_latency_percentiles, get_tool_latency_percentiles, etc.)
        # already acquire the lock themselves. Acquiring it here would cause a deadlock.
        
        query_latency = self.get_query_latency_percentiles()
        
        tool_latencies = {}
        for tool_type in ['alpha_vantage', 'tavily', 'python_repl']:
            tool_latencies[tool_type] = self.get_tool_latency_percentiles(tool_type)
        
        # Get tool_calls_count safely
        with self._lock:
            tool_calls_count_dict = dict(self._tool_call_counts)
            agent_transitions_count = sum(self._agent_transition_counts.values())
            total_errors = sum(self._tool_error_counts.values())
            errors_by_tool = dict(self._tool_error_counts)
            total_queries = self._total_queries
            successful_queries = self._successful_queries
            failed_queries = self._failed_queries
            total_tool_calls = sum(self._tool_call_counts.values())
            recovered_tool_calls = self._recovered_tool_calls
            supervisor_interventions_total = self._supervisor_interventions
        
        return {
            'latency_performance': {
                'end_to_end_response_time': {
                    'p50_seconds': query_latency['p50'],
                    'p95_seconds': query_latency['p95']
                },
                'tool_call_latency': tool_latencies,
                'agent_transitions_count': agent_transitions_count,
                'tool_calls_count': tool_calls_count_dict,
                'tool_calls_latency_per_tool': {
                    tool: self.get_tool_latency_percentiles(tool)
                    for tool in tool_calls_count_dict.keys()
                }
            },
            'reliability_robustness': {
                'success_rate_percent': self.get_success_rate(),
                'error_rate': {
                    'total_errors': total_errors,
                    'errors_by_tool': errors_by_tool,
                    'api_failures': errors_by_tool.get('alpha_vantage', 0) + 
                                  errors_by_tool.get('tavily', 0),
                    'timeouts': errors_by_tool.get('timeout', 0),
                    'invalid_inputs': errors_by_tool.get('invalid_ticker', 0)
                },
                'recovery_rate_percent': self.get_recovery_rate(),
                'tool_success_rates': {
                    tool: self.get_tool_success_rate(tool)
                    for tool in tool_calls_count_dict.keys()
                }
            },
            'loop_prevention': self.get_loop_prevention_effectiveness(),
            'supervisor_interventions': {
                'total': supervisor_interventions_total,
                'percentage_queries_needing_intervention': self.get_supervisor_intervention_rate()
            },
            'totals': {
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'failed_queries': failed_queries,
                'total_tool_calls': total_tool_calls,
                'recovered_tool_calls': recovered_tool_calls
            }
        }


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector(
    enable_prometheus: bool = True,
    prometheus_port: int = 8000
) -> MetricsCollector:
    """Get or create the global metrics collector instance.
    
    Args:
        enable_prometheus: Whether to enable Prometheus metrics
        prometheus_port: Port for Prometheus HTTP server
        
    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(
            enable_prometheus=enable_prometheus,
            prometheus_port=prometheus_port
        )
    return _metrics_collector


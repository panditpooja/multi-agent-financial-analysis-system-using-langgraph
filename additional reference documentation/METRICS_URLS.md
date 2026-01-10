# Metrics URLs and Endpoints

The Django application now includes comprehensive metrics endpoints!

## 📊 Available Metrics URLs

### 1. Metrics Dashboard (HTML)
**URL:** `/metrics/`

A beautiful, interactive dashboard showing all metrics:
- Latency & Performance metrics
- Reliability & Robustness metrics
- Loop Prevention statistics
- Supervisor Interventions
- Total statistics

**Access:** Open in browser at `http://127.0.0.1:8000/metrics/`

### 2. Metrics JSON API
**URL:** `/metrics/json/`

Returns all metrics as JSON for programmatic access.

**Example:**
```bash
curl http://127.0.0.1:8000/metrics/json/
```

**Response Format:**
```json
{
  "latency_performance": {
    "end_to_end_response_time": {
      "p50_seconds": 2.345,
      "p95_seconds": 5.678
    },
    "tool_call_latency": {...},
    "agent_transitions_count": 15,
    ...
  },
  "reliability_robustness": {...},
  "loop_prevention": {...},
  ...
}
```

### 3. Prometheus Metrics Endpoint
**URL:** `/metrics/prometheus/`

Returns metrics in Prometheus-compatible format for scraping.

**Example:**
```bash
curl http://127.0.0.1:8000/metrics/prometheus/
```

**Response Format:**
```
# HELP agent_query_latency_seconds End-to-end query latency in seconds
# TYPE agent_query_latency_seconds histogram
agent_query_latency_seconds_bucket{le="0.1"} 5.0
agent_query_latency_seconds_bucket{le="0.5"} 12.0
...
```

### 4. Direct Prometheus Server
**URL:** `http://localhost:9090/metrics`

The Prometheus server runs on port 9090 (separate from Django on 8000) to avoid conflicts.

**Access:** Direct Prometheus server endpoint (bypasses Django)

## 🔗 Quick Links

When the Django server is running:

- **Main Chat Interface:** `http://127.0.0.1:8000/`
- **Metrics Dashboard:** `http://127.0.0.1:8000/metrics/`
- **Metrics JSON:** `http://127.0.0.1:8000/metrics/json/`
- **Prometheus (via Django):** `http://127.0.0.1:8000/metrics/prometheus/`
- **Prometheus (direct):** `http://localhost:9090/metrics`

## 📈 Metrics Tracked

### Latency & Performance
- End-to-end response time (p50, p95)
- Tool call latency per tool (Alpha Vantage, Tavily, Python REPL)
- Agent transitions count
- Tool calls count per tool

### Reliability & Robustness
- Success rate (% of queries completed without failure)
- Error rate (API failures, timeouts, invalid inputs)
- Recovery rate (% of failed tool calls that succeed after retry)
- Tool-specific success rates

### Loop Prevention
- Number of loops detected/prevented
- Percentage of queries needing supervisor intervention

## 🚀 Usage

### View Metrics in Browser

1. Start Django server: `python manage.py runserver`
2. Navigate to: `http://127.0.0.1:8000/metrics/`
3. View real-time metrics dashboard

### Access Metrics Programmatically

```python
import requests

# Get metrics as JSON
response = requests.get('http://127.0.0.1:8000/metrics/json/')
metrics = response.json()

print(f"Success Rate: {metrics['reliability_robustness']['success_rate_percent']}%")
print(f"P95 Latency: {metrics['latency_performance']['end_to_end_response_time']['p95_seconds']}s")
```

### Scrape with Prometheus

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'financial-ai-system'
    static_configs:
      - targets: ['localhost:9090']  # Direct Prometheus server
        # OR
      - targets: ['localhost:8000']  # Via Django proxy
        metrics_path: '/metrics/prometheus/'
```

## 🔧 Integration

Metrics are automatically tracked when:
1. Django views process queries
2. The multi-agent system executes
3. Tools are called (if instrumented)

To enable full metrics tracking, make sure:
- `prometheus-client` is installed: `pip install prometheus-client`
- Metrics are initialized (happens automatically in `views.py`)

## 📝 Notes

- Prometheus server runs on port **9090** (separate from Django on 8000)
- Metrics are stored in-memory and reset when the server restarts
- For persistent metrics, use Prometheus with persistent storage
- The metrics dashboard updates when you refresh the page


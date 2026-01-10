"""
Django views for the Financial AI Multi-Agent System.
"""
import json
import uuid
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

# Import the multi-agent system
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentic_ai_multi_gent_financial_analysis import process_query as process_financial_query, build_graph

# Import metrics
try:
    from metrics_collector import get_metrics_collector
    from metrics_integration import print_metrics_summary, get_metrics_json, setup_metrics
    METRICS_AVAILABLE = True
    print("✅ Metrics modules imported successfully")
except ImportError as e:
    METRICS_AVAILABLE = False
    print(f"⚠️ Warning: Metrics not available. Error: {e}")
    print("Install prometheus-client for metrics support.")

# Initialize metrics on module load
if METRICS_AVAILABLE:
    try:
        # Use a different port for Prometheus to avoid conflict with Django (8000)
        metrics = setup_metrics(enable_prometheus=True, prometheus_port=9090)
        print(f"✅ Metrics initialized successfully. Prometheus port: 9090")
    except Exception as e:
        import traceback
        print(f"❌ Warning: Could not initialize metrics: {e}")
        traceback.print_exc()
        metrics = None
else:
    metrics = None

# Build graph once at module load (not on every request!)
try:
    _graph_instance = build_graph()
    print("✅ Graph built successfully at startup")
except Exception as e:
    print(f"❌ Error building graph at startup: {e}")
    _graph_instance = None


@ensure_csrf_cookie
def index(request):
    """Render the main chat interface."""
    # Get or create session thread_id
    if 'thread_id' not in request.session:
        request.session['thread_id'] = str(uuid.uuid4())
    
    return render(request, 'financial_ai/index.html', {
        'thread_id': request.session['thread_id']
    })


@require_http_methods(["POST"])
def process_query(request):
    """Process a financial query via AJAX."""
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({
                'success': False,
                'error': 'Query cannot be empty'
            }, status=400)
        
        # Check if graph is available
        if _graph_instance is None:
            return JsonResponse({
                'success': False,
                'error': 'System not initialized. Please restart the server.'
            }, status=503)
        
        # Get thread_id from session or request
        thread_id = data.get('thread_id') or request.session.get('thread_id')
        if not thread_id:
            thread_id = str(uuid.uuid4())
            request.session['thread_id'] = thread_id
        
        # Start metrics tracking if available (with error handling)
        if METRICS_AVAILABLE and metrics:
            try:
                metrics.start_query(thread_id)
            except Exception as e:
                print(f"Warning: Metrics start_query failed: {e}")
        
        # Process the query (pass the pre-built graph)
        result = process_financial_query(query, thread_id=thread_id, graph_instance=_graph_instance)
        
        # End metrics tracking if available (with error handling)
        if METRICS_AVAILABLE and metrics:
            try:
                metrics.end_query(thread_id, success=result.get('success', False), error=result.get('error'))
            except Exception as e:
                print(f"Warning: Metrics end_query failed: {e}")
        
        # Format response for frontend
        if result.get('success'):
            response_data = {
                'success': True,
                'response': result.get('response', ''),
                'thread_id': result.get('thread_id', thread_id)
            }
            # Include plot path if available
            if 'plot_path' in result:
                response_data['plot_path'] = result['plot_path']
            print(f"Sending successful response to frontend. Response length: {len(response_data.get('response', ''))}, Has plot: {'plot_path' in response_data}")
            return JsonResponse(response_data)
        else:
            error_msg = result.get('error', 'Unknown error occurred')
            print(f"Query processing error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request'
        }, status=400)
    except Exception as e:
        error_msg = f'Server error: {str(e)}'
        print(f"Unexpected error in process_query: {error_msg}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': error_msg
        }, status=500)


def query_history(request):
    """Display query history (placeholder for future implementation)."""
    return render(request, 'financial_ai/history.html', {
        'queries': []  # TODO: Implement query history storage
    })


def metrics_dashboard(request):
    """Display metrics dashboard."""
    print(f"📊 Metrics dashboard accessed. METRICS_AVAILABLE={METRICS_AVAILABLE}, metrics={metrics is not None}")
    if not METRICS_AVAILABLE or not metrics:
        error_msg = 'Metrics system not available. Install prometheus-client for metrics support.'
        if not METRICS_AVAILABLE:
            error_msg += ' (Metrics modules not imported)'
        elif not metrics:
            error_msg += ' (Metrics not initialized)'
        return render(request, 'financial_ai/metrics.html', {
            'metrics_available': False,
            'error': error_msg
        })
    
    try:
        print("📊 Calling metrics.get_summary()...")
        import time
        import signal
        
        start_time = time.perf_counter()
        
        # Get summary with timeout protection
        try:
            summary = metrics.get_summary()
            elapsed = time.perf_counter() - start_time
            print(f"📊 get_summary() completed in {elapsed:.3f}s. Summary type: {type(summary)}")
        except Exception as get_summary_error:
            print(f"❌ Error in get_summary(): {get_summary_error}")
            import traceback
            traceback.print_exc()
            return render(request, 'financial_ai/metrics.html', {
                'metrics_available': False,
                'error': f'Error getting metrics summary: {str(get_summary_error)}. Check the Django console for details.'
            })
        
        # Check if summary is valid
        if not summary or not isinstance(summary, dict):
            print("📊 Summary is invalid or empty")
            return render(request, 'financial_ai/metrics.html', {
                'metrics_available': False,
                'error': 'Metrics data is invalid or empty. Make some queries first to collect metrics.'
            })
        
        print(f"📊 Summary keys: {list(summary.keys())}")
        
        # Safely extract nested data with defaults
        latency_perf = summary.get('latency_performance', {})
        print(f"📊 Latency performance keys: {list(latency_perf.keys()) if isinstance(latency_perf, dict) else 'N/A'}")
        
        # Convert tool_calls_count dict to a format easier for templates
        tool_calls_count = latency_perf.get('tool_calls_count', {})
        print(f"📊 Tool calls count: {tool_calls_count}")
        
        # Get prometheus port safely
        prometheus_port = None
        if hasattr(metrics, 'prometheus_enabled') and metrics.prometheus_enabled:
            prometheus_port = getattr(metrics, 'prometheus_port', None)
        
        print(f"📊 Rendering template with metrics data...")
        render_start = time.perf_counter()
        response = render(request, 'financial_ai/metrics.html', {
            'metrics_available': True,
            'summary': summary,
            'tool_calls_count': tool_calls_count,
            'prometheus_port': prometheus_port
        })
        render_elapsed = time.perf_counter() - render_start
        print(f"📊 Template rendered in {render_elapsed:.3f}s. Response length: {len(response.content)} bytes")
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        error_msg = str(e)
        print(f"❌ ERROR in metrics_dashboard: {error_msg}")
        return render(request, 'financial_ai/metrics.html', {
            'metrics_available': False,
            'error': f'Error loading metrics: {error_msg}. Check the Django console for details.'
        })


def metrics_json(request):
    """Get metrics as JSON."""
    if not METRICS_AVAILABLE or not metrics:
        return JsonResponse({
            'error': 'Metrics system not available'
        }, status=503)
    
    try:
        summary = metrics.get_summary()
        return JsonResponse(summary, json_dumps_params={'indent': 2})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': f'Error loading metrics: {str(e)}'
        }, status=500)


def metrics_prometheus(request):
    """Proxy to Prometheus metrics endpoint."""
    if not METRICS_AVAILABLE or not metrics or not metrics.prometheus_enabled:
        return HttpResponse('Prometheus metrics not available', status=503)
    
    try:
        import urllib.request
        prometheus_url = f'http://localhost:{metrics.prometheus_port}/metrics'
        with urllib.request.urlopen(prometheus_url) as response:
            content = response.read().decode('utf-8')
            return HttpResponse(content, content_type='text/plain')
    except Exception as e:
        return HttpResponse(f'Error fetching Prometheus metrics: {str(e)}', status=500)


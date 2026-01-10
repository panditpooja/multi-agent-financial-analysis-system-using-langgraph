#!/usr/bin/env python3
"""
Standalone script to view metrics from the multi-agent system.

Usage:
    python view_metrics.py              # Print metrics summary
    python view_metrics.py --json       # Output metrics as JSON
    python view_metrics.py --prometheus # Show Prometheus endpoint info
"""

import argparse
import json
import sys
from metrics_collector import get_metrics_collector
from metrics_integration import print_metrics_summary, get_metrics_json


def main():
    parser = argparse.ArgumentParser(
        description='View metrics from the multi-agent financial analysis system'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output metrics as JSON'
    )
    parser.add_argument(
        '--prometheus',
        action='store_true',
        help='Show Prometheus endpoint information'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Prometheus server port (default: 8000)'
    )
    
    args = parser.parse_args()
    
    # Initialize metrics collector (will use existing instance if already initialized)
    try:
        metrics = get_metrics_collector(enable_prometheus=True, prometheus_port=args.port)
    except Exception as e:
        print(f"Warning: Could not initialize metrics collector: {e}")
        print("Metrics may not be available if the system hasn't been run yet.")
        sys.exit(1)
    
    if args.json:
        # Output as JSON
        summary = get_metrics_json()
        print(json.dumps(summary, indent=2))
    elif args.prometheus:
        # Show Prometheus info
        if metrics.prometheus_enabled:
            print(f"✅ Prometheus metrics server is running")
            print(f"📊 Metrics endpoint: http://localhost:{metrics.prometheus_port}/metrics")
            print(f"\nYou can:")
            print(f"  1. View metrics in browser: http://localhost:{metrics.prometheus_port}/metrics")
            print(f"  2. Scrape with Prometheus: http://localhost:{metrics.prometheus_port}/metrics")
            print(f"  3. Use Grafana to visualize the metrics")
        else:
            print("❌ Prometheus metrics are not enabled")
            print("   Make sure prometheus-client is installed: pip install prometheus-client")
    else:
        # Print formatted summary
        print_metrics_summary()


if __name__ == '__main__':
    main()


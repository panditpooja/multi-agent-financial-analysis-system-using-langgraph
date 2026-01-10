"""
Instrumentation module for wrapping tools and agents with metrics collection.

This module provides decorators and wrappers to automatically track:
- Tool call latency
- Agent transitions
- Errors and retries
- Loop detection
"""

import time
import functools
import threading
from typing import Any, Callable, Optional
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage

from metrics_collector import (
    get_metrics_collector,
    ToolType,
    AgentType
)

# Thread-local storage for thread_id
_thread_local = threading.local()


def set_thread_id(thread_id: str):
    """Set the thread_id for the current thread.
    
    Args:
        thread_id: Thread ID to set
    """
    _thread_local.thread_id = thread_id


def get_thread_id() -> str:
    """Get the thread_id for the current thread.
    
    Returns:
        Thread ID or 'unknown' if not set
    """
    return getattr(_thread_local, 'thread_id', 'unknown')


def instrument_tool(tool: BaseTool, tool_type: str):
    """Instrument a tool to track metrics.
    
    Args:
        tool: The tool to instrument
        tool_type: Type identifier for the tool
        
    Returns:
        Wrapped tool with metrics tracking
    """
    original_run = tool._run
    
    @functools.wraps(original_run)
    def wrapped_run(*args, **kwargs):
        # Get thread_id from thread-local storage
        thread_id = get_thread_id()
        
        metrics = get_metrics_collector()
        tool_call_id = metrics.start_tool_call(thread_id, tool_type)
        
        success = False
        error_type = None
        error_message = None
        retry_count = 0
        
        try:
            result = original_run(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            
            # Classify error types
            if 'timeout' in str(e).lower() or 'timed out' in str(e).lower():
                error_type = 'timeout'
            elif 'rate limit' in str(e).lower() or '429' in str(e):
                error_type = 'rate_limit'
            elif 'invalid' in str(e).lower() or 'not found' in str(e).lower():
                if tool_type == 'alpha_vantage':
                    error_type = 'invalid_ticker'
                else:
                    error_type = 'invalid_input'
            elif 'api' in str(e).lower():
                error_type = 'api_failure'
            
            raise
        finally:
            metrics.end_tool_call(
                thread_id=thread_id,
                tool_type=tool_type,
                success=success,
                error_type=error_type,
                error_message=error_message,
                retry_count=retry_count
            )
    
    tool._run = wrapped_run
    return tool


def instrument_agent_node(agent_func: Callable, agent_name: str):
    """Instrument an agent node to track transitions and metrics.
    
    Args:
        agent_func: The agent node function
        agent_name: Name of the agent
        
    Returns:
        Wrapped agent function with metrics tracking
    """
    @functools.wraps(agent_func)
    def wrapped_agent_node(state: dict):
        metrics = get_metrics_collector()
        
        # Get thread_id from thread-local storage
        thread_id = get_thread_id()
        
        # Record transition to this agent
        # Try to determine previous agent from state
        previous_agent = 'Supervisor'  # Default, as supervisor routes to agents
        if 'messages' in state:
            messages = state['messages']
            agent_messages = [msg for msg in messages if isinstance(msg, AIMessage) and hasattr(msg, 'name') and msg.name]
            if agent_messages:
                previous_agent = agent_messages[-1].name or 'Supervisor'
        
        metrics.record_agent_transition(thread_id, previous_agent, agent_name)
        
        # Execute the agent
        try:
            result = agent_func(state)
            return result
        except Exception as e:
            # Record error
            error_type = type(e).__name__
            metrics.end_tool_call(
                thread_id=thread_id,
                tool_type=agent_name,
                success=False,
                error_type=error_type,
                error_message=str(e)
            )
            raise
    
    return wrapped_agent_node


def instrument_supervisor(supervisor_func: Callable):
    """Instrument the supervisor to track interventions and loop detection.
    
    Args:
        supervisor_func: The supervisor function
        
    Returns:
        Wrapped supervisor function with metrics tracking
    """
    @functools.wraps(supervisor_func)
    def wrapped_supervisor(state: dict):
        metrics = get_metrics_collector()
        
        # Get thread_id from thread-local storage
        thread_id = get_thread_id()
        
        # Check for loops before supervisor decision
        if 'messages' in state:
            messages = state['messages']
            agent_messages = [msg for msg in messages if isinstance(msg, AIMessage) and hasattr(msg, 'name') and msg.name]
            
            if len(agent_messages) >= 2:
                # Check for identical consecutive responses (loop detection logic from supervisor)
                last_agent = agent_messages[-1].name
                recent_same_agent_responses = [msg for msg in agent_messages if msg.name == last_agent]
                
                if len(recent_same_agent_responses) >= 2:
                    contents = [msg.content.strip() for msg in recent_same_agent_responses[-2:]]
                    if contents[-1] == contents[-2]:
                        metrics.record_loop_detection(thread_id)
        
        # Execute supervisor
        result = supervisor_func(state)
        
        # Record supervisor intervention if it made a decision
        if isinstance(result, dict) and 'next' in result:
            if result['next'] != 'FINISH':
                metrics.record_supervisor_intervention(thread_id)
        
        return result
    
    return wrapped_supervisor


def instrument_graph_stream(graph_stream_func: Callable):
    """Instrument graph.stream to track query start/end.
    
    Args:
        graph_stream_func: The graph.stream function
        
    Returns:
        Wrapped stream function with metrics tracking
    """
    @functools.wraps(graph_stream_func)
    def wrapped_stream(inputs: dict, config: Optional[dict] = None, **kwargs):
        metrics = get_metrics_collector()
        
        # Extract thread_id
        thread_id = 'unknown'
        if config and 'configurable' in config:
            thread_id = config['configurable'].get('thread_id', 'unknown')
        
        # Set thread_id in thread-local storage
        set_thread_id(thread_id)
        
        # Start query tracking
        query_id = metrics.start_query(thread_id)
        
        try:
            # Stream events
            finished = False
            for event in graph_stream_func(inputs, config=config, **kwargs):
                yield event
                
                # Check if query completed (END event)
                if isinstance(event, dict) and '__end__' in event:
                    if not finished:
                        metrics.end_query(thread_id, success=True)
                        finished = True
                elif isinstance(event, dict):
                    # Check for FINISH decision
                    for node_name, node_state in event.items():
                        if isinstance(node_state, dict) and node_state.get('next') == 'FINISH':
                            if not finished:
                                metrics.end_query(thread_id, success=True)
                                finished = True
                            break
            
            # If we didn't detect a finish, end the query when stream completes
            if not finished:
                metrics.end_query(thread_id, success=True)
        except Exception as e:
            # Query failed
            metrics.end_query(thread_id, success=False, error=str(e))
            raise
        finally:
            # Clear thread-local storage
            if hasattr(_thread_local, 'thread_id'):
                delattr(_thread_local, 'thread_id')
    
    return wrapped_stream


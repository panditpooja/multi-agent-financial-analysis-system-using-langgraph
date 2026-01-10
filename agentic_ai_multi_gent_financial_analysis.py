"""
Multi-Agent Financial Analysis System using LangGraph

This module provides a sophisticated multi-agent financial analysis system
that utilizes a supervisor pattern to orchestrate specialized agents for
complex financial queries.
"""

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_community.utilities.alpha_vantage import AlphaVantageAPIWrapper
from langchain_experimental.tools import PythonREPLTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
import os
import re
import json
import uuid
from typing import Annotated, Literal, Sequence
from typing_extensions import TypedDict
from pydantic import BaseModel
import operator
import functools
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def check_env_vars(reload=False):
    """Check if required environment variables are set."""
    if reload:
        load_dotenv(override=True)
        print("✅ Environment variables reloaded!")
    
    required_vars = {
        "OPENROUTER_API_KEY": "OpenRouter API key for LLM access",
        "ALPHAVANTAGE_API_KEY": "Alpha Vantage API key for stock data",
        "TAVILY_API_KEY": "Tavily API key for web search (optional)"
    }
    
    print("📋 Environment Variables Status:\n")
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            # Show first and last 4 characters for security
            masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            print(f"✅ {var_name}: {masked} ({description})")
        else:
            print(f"❌ {var_name}: NOT SET ({description})")
    
    print("\n💡 Tip: If you just added variables to .env, run: check_env_vars(reload=True)")


# Define the LLM
# For OPEN_ROUTER_API_KEY use
# def get_llm():
#     """Initialize and return the LLM."""
#     api_key = os.getenv("OPENROUTER_API_KEY")
#     if not api_key:
#         raise ValueError("OPENROUTER_API_KEY environment variable is not set. Please set it in your .env file.")
    
#     return ChatOpenAI(
#         model="openai/gpt-oss-120b:free",
#         base_url="https://openrouter.ai/api/v1",
#         api_key=api_key,
#         temperature=0,
#         max_tokens=2000
#     )

# For GROQ_ROUTER_API_KEY use
def get_llm():
    """Initialize and return the LLM (Groq via OpenAI-compatible endpoint)."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")
    
    return ChatOpenAI(
        model="openai/gpt-oss-120b",  # Groq model id
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
        temperature=0,  # Groq converts 0 -> 1e-8 internally; OK
        max_tokens=2000,
    )

# Tools
from langchain_core.tools import tool

@tool
def get_current_date():
    """Returns the current date and time. Use this tool first for any time-based queries."""
    return f"The current date is: {datetime.now().strftime('%d %B %Y')}"


# Define custom tool for alpha vantage
from langchain_core.tools import BaseTool

class AlphaVantageQueryRun(BaseTool):
    """Tool that queries the Alpha Vantage API."""

    name: str = "alpha_vantage"
    description: str = (
        "A wrapper around Alpha Vantage API. "
        "Useful for getting financial information about stocks, "
        "forex, cryptocurrencies, and economic indicators. "
        "Input should be the name of the stock ticker."
    )
    api_wrapper: AlphaVantageAPIWrapper = AlphaVantageAPIWrapper()

    def _run(self, ticker: str) -> str:
        """Use the tool."""
        return self.api_wrapper._get_time_series_daily(ticker)


# Initialize tools
def initialize_tools():
    """Initialize all tools."""
    import matplotlib
    # Set matplotlib to use non-interactive backend for web environments
    # This prevents plt.show() from hanging when CodeAgent generates plots
    matplotlib.use('Agg')  # Use non-interactive backend
    
    # Create plots directory if it doesn't exist
    plots_dir = os.path.join(os.path.dirname(__file__), 'static', 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    tavily_tool = TavilySearch(max_results=2)
    alpha_vantage_tool = AlphaVantageQueryRun()
    python_repl_tool = PythonREPLTool()
    
    return {
        'tavily_tool': tavily_tool,
        'alpha_vantage_tool': alpha_vantage_tool,
        'python_repl_tool': python_repl_tool,
        'get_current_date': get_current_date
    }


# Create agents
def create_agents(llm, tools):
    """Create all agents."""
    # Web Search Agent
    web_search_system_prompt = (
        "You are a web search agent specializing in financial information. "
        "Your role is to use web search tools to find current information and return comprehensive, well-structured answers. "
        "\n\nIMPORTANT:"
        "\n1. Search for the most recent and relevant information"
        "\n2. Synthesize information from multiple sources when available"
        "\n3. Provide clear, concise summaries with key points"
        "\n4. Cite sources or mention where information came from when relevant"
        "\n5. Focus on financial news, market trends, company performance, and related topics"
        "\n\nRESPONSE LENGTH:"
        "\n- Keep responses concise: 1-2 paragraphs is usually enough"
        "\n- Maximum 1000 words only if absolutely necessary for complex topics"
        "\n- Prioritize clarity and brevity over verbosity"
        "\n\nFormat your responses clearly with:"
        "- Main points or summary at the top"
        "- Supporting details below"
        "- Any relevant dates, numbers, or statistics"
    )
    web_search_agent = create_agent(
        llm, 
        tools=[tools['tavily_tool'], tools['get_current_date']], 
        system_prompt=web_search_system_prompt
    )
    
    # Financial Analysis Agent
    financial_system_prompt = (
        "You are a financial analysis agent. Your role is to use the Alpha Vantage tool to gather financial data and provide concise, informative answers. "
        "\n\nCRITICAL - ALWAYS USE THE TOOL:"
        "\n1. You MUST use the alpha_vantage tool for EVERY query - never ask for clarification"
        "\n2 If you see a ticker symbol (e.g., MSFT, AAPL), use it directly"
        "\n3. If the user says 'Microsoft', 'Apple', 'Tesla', etc., automatically convert to ticker and use the tool"
        "\n4. NEVER ask 'Could you let me know...' or 'What ticker...' - just extract and use the tool"
        "\n\nDATA PRESENTATION:"
        "\n1. Present data clearly in a structured format (tables, lists, or well-formatted text)"
        "\n2. Always format dates in human-readable format (e.g., 'December 12, 2025' instead of '2025-12-12')"
        "\n3. If asked about plots/charts/visualizations, provide the data clearly and state: 'I cannot create plots, but here is the data:'"
        "\n4. For visualization requests, include all necessary data (dates, prices, closing values) in a format that can be easily parsed"
        "\n\nRESPONSE LENGTH:"
        "\n- Keep responses concise: 1-2 paragraphs is usually enough"
        "\n- Maximum 1000 words only if absolutely necessary for complex data analysis"
        "\n- Focus on presenting data clearly, not lengthy explanations"
        "\n\nDo NOT:"
        "- Generate charts, plots, or visualizations (CodeAgent handles that)"
        "- Use vague or incomplete data"
        "- Skip important information like dates or prices"
        "- Be overly verbose - get to the point quickly"
    )
    financial_agent = create_agent(
        llm, 
        tools=[tools['alpha_vantage_tool'], tools['get_current_date']], 
        system_prompt=financial_system_prompt
    )
    
    # Code Agent
    code_system_prompt = (
        "You are a visualization agent. Your role is to create visual representations of data using Python. "
        "Use the Python REPL tool provided to generate plots, charts, or other visualizations. "
        "\n\nIMPORTANT INSTRUCTIONS:"
        "\n1. Extract data from the conversation history - look for stock prices, dates, and financial data provided by FinancialAgent."
        "\n2. Parse the data (it may be in JSON, table, or text format) and convert it to Python data structures (lists, dictionaries, pandas DataFrames)."
        "\n3. Create appropriate visualizations using matplotlib (e.g., line plots for time series, bar charts for comparisons)."
        "\n4. Always include proper labels: title, x-axis label, y-axis label."
        "\n5. Format dates on x-axis if the data contains dates."
        "\n6. CRITICAL: Save the plot to a file instead of using plt.show(). "
        "\n   First create directory if needed: import os; os.makedirs('static/plots', exist_ok=True)"
        "\n   Then save: plt.savefig('static/plots/plot.png', dpi=150, bbox_inches='tight')"
        "\n   Finally close: plt.close()"
        "\n7. After saving, confirm completion with: 'Plot saved successfully. The visualization has been created.'"
        "\n\nRESPONSE LENGTH:"
        "\n- Keep text responses very brief: 1-2 sentences is usually enough"
        "\n- Maximum 1000 words only if absolutely necessary to explain complex visualization code"
        "\n- The visualization itself is the main output, not lengthy explanations"
        "\n\nDo NOT:"
        "- Perform data analysis or gather new information"
        "- Call APIs or fetch data (FinancialAgent already provided the data)"
        "- Generate multiple plots unless explicitly requested"
        "- Return without executing the visualization code"
        "- Write lengthy explanations - be concise"
    )
    code_agent = create_agent(
        llm, 
        tools=[tools['python_repl_tool']], 
        system_prompt=code_system_prompt
    )
    
    return {
        'web_search_agent': web_search_agent,
        'financial_agent': financial_agent,
        'code_agent': code_agent
    }


# Supervisor Agent
def create_supervisor(llm):
    """Create the supervisor agent."""
    # Define team members
    members = {
        "WebSearchAgent": "An agent that performs web searches to gather information",
        "FinancialAgent": "An agent that analyzes financial data using Alpha Vantage API to acquire stock market information.",
        "CodeAgent": "An agent that executes Python code and performs computations. Use this to generate plots and tables."
    }
    
    # Supervisor Prompt Template
    system_prompt = (
        "You are a highly efficient supervisor managing a collaborative conversation between specialized agents:"
        "\n{members_description}"
        "\n\n=== YOUR ROLE ==="
        "\n1. Analyze the user's request and the ongoing conversation."
        "\n2. Determine which agent is best suited to handle the next task."
        "\n3. Ensure a logical flow and prevent unnecessary agent calls."
        "\n4. Detect task completion and respond with 'FINISH' when done."
        "\n\n=== DECISION RULES ==="
        "\n\n**VISUALIZATION REQUESTS (plot, chart, graph, visualize, draw):**"
        "\n1. Route to FinancialAgent FIRST to gather data"
        "\n2. After FinancialAgent provides data (look for: prices, dates, tables, or 'cannot create plots'), route to CodeAgent"
        "\n3. CRITICAL: After CodeAgent responds (even if it's just 'Plot generated' or similar), respond with FINISH immediately"
        "\n4. DO NOT route back to FinancialAgent if it already provided data"
        "\n5. DO NOT route to CodeAgent multiple times - one visualization per request"
        "\n\n**SIMPLE DATA QUERIES (price, stock value, closing price):**"
        "\n1. Route to FinancialAgent"
        "\n2. After FinancialAgent provides the answer, respond with FINISH immediately"
        "\n\n**NEWS/INFORMATION QUERIES (news, summary, latest information):**"
        "\n1. Route to WebSearchAgent"
        "\n2. After WebSearchAgent provides comprehensive answer, respond with FINISH"
        "\n\n**COMBINED QUERIES (news about stock performance):**"
        "\n1. Route to FinancialAgent for stock data (optional, if needed)"
        "\n2. Route to WebSearchAgent for news"
        "\n3. After WebSearchAgent responds, respond with FINISH"
        "\n\n=== COMPLETION DETECTION (When to FINISH) ==="
        "\nRespond with 'FINISH' when:"
        "\n✓ CodeAgent has been called and responded (even once) - visualization is complete"
        "\n✓ FinancialAgent provided a direct answer to a simple question (e.g., 'AAPL is $150')"
        "\n✓ WebSearchAgent provided comprehensive information"
        "\n✓ The same agent was called twice with similar responses (loop detected)"
        "\n✓ All user objectives are met"
        "\n\n=== ANTI-PATTERNS (What NOT to do) ==="
        "\n✗ DO NOT call CodeAgent multiple times for the same visualization request"
        "\n✗ DO NOT route back to FinancialAgent after it already provided data for a visualization"
        "\n✗ DO NOT continue routing if an agent already answered the question completely"
        "\n✗ DO NOT ignore completion signals (e.g., 'Plot generated', 'Visualization created')"
        "\n\n=== EXAMPLES ==="
        "\nUser: 'What was AAPL price?' → FinancialAgent → FINISH"
        "\nUser: 'Draw a plot of AAPL prices' → FinancialAgent → CodeAgent → FINISH"
        "\nUser: 'Latest news about Tesla' → WebSearchAgent → FINISH"
        "\nUser: 'Plot AAPL prices' → FinancialAgent → CodeAgent → FINISH (after CodeAgent responds)"
    )
    
    members_description = "\n".join([f"- {k}: {v}" for k, v in members.items()])
    system_prompt = system_prompt.format(members_description=members_description)
    
    # Possible options for the supervisor
    options = ["FINISH"] + list(members.keys())
    
    # Define the supervisor's output schema
    class RouteResponse(BaseModel):
        """The supervisor's response to the user's request."""
        next: Literal["FINISH", "WebSearchAgent", "FinancialAgent", "CodeAgent"]
    
    # Supervisor Prompt
    supervisor_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Based on the conversation, who should act next? Choose one of: {options}",
            ),
        ]
    ).partial(options=str(options), members=", ".join([f"{k}: {v}" for k, v in members.items()]))
    
    # Maximum iterations to prevent infinite loops (safety limit)
    # This is per conversation thread - allows ~10-15 questions in a single conversation
    # Loop detection handles most infinite loops before this limit is reached
    MAX_ITERATIONS = 40
    
    # Supervisor Agent Function
    def supervisor_agent(state):
        import logging
        logger = logging.getLogger(__name__)
        
        messages = state.get("messages", [])
        logger.info(f"Supervisor called with {len(messages)} total messages in state")
        
        # Find the most recent user message (current query)
        last_user_message_idx = None
        for i, msg in enumerate(messages):
            if isinstance(msg, HumanMessage):
                last_user_message_idx = i
                logger.info(f"Found user message at index {i}: {msg.content[:50]}...")
        
        # Only check messages from the current query (after last user message)
        # If no user message found, check all messages (first query)
        if last_user_message_idx is not None:
            current_query_messages = messages[last_user_message_idx:]
        else:
            current_query_messages = messages
        
        # Check for maximum iterations (safety limit) - only count current query
        agent_responses = [msg for msg in current_query_messages if isinstance(msg, AIMessage) and msg.name]
        if len(agent_responses) >= MAX_ITERATIONS:
            logger.warning(f"MAX_ITERATIONS ({MAX_ITERATIONS}) reached for current query - finishing")
            return {"next": "FINISH"}
        
        # IMPORTANT: If this is a new query (no agent responses yet in current query), we MUST route to an agent
        # Don't finish if no agent has responded to the current query yet
        if len(agent_responses) == 0:
            logger.info("No agent responses yet for current query - supervisor will route to an agent")
            # Don't return here - let the supervisor logic below decide which agent to route to
        
        # Check for infinite loops - only check current query messages
        if len(current_query_messages) >= 4:
            # Only look at last 8 messages from current query
            query_agent_messages = [msg for msg in current_query_messages[-8:] if isinstance(msg, AIMessage) and hasattr(msg, 'name') and msg.name]
            
            if len(query_agent_messages) >= 2:
                last_agent = query_agent_messages[-1].name
                recent_same_agent_responses = [msg for msg in query_agent_messages if msg.name == last_agent]
                
                # Special handling for CodeAgent - if it's been called twice in current query, likely generating duplicate plots
                if last_agent == "CodeAgent" and len(recent_same_agent_responses) >= 2:
                    # CodeAgent has been called multiple times in current query, likely generating same plot
                    return {"next": "FINISH"}
                
                if len(recent_same_agent_responses) >= 2:
                    contents = [msg.content.strip() for msg in recent_same_agent_responses[-3:]]
                    
                    if len(contents) >= 2:
                        if contents[-1] == contents[-2]:
                            return {"next": "FINISH"}
                        
                        if len(contents) >= 3 and contents[-1] == contents[-2] == contents[-3]:
                            return {"next": "FINISH"}
                        
                        def normalize(text):
                            return ' '.join(text.split())
                        
                        norm_contents = [normalize(c) for c in contents[-2:]]
                        if norm_contents[0] == norm_contents[1]:
                            return {"next": "FINISH"}
                        
                        if len(contents) >= 2:
                            c1, c2 = contents[-2], contents[-1]
                            if len(c1) > 50 and len(c2) > 50:
                                if c1[:150] == c2[:150]:
                                    max_len = max(len(c1), len(c2))
                                    if max_len > 0:
                                        len_diff = abs(len(c1) - len(c2)) / max_len
                                        if len_diff < 0.05:
                                            return {"next": "FINISH"}
        
        # Check for visualization requests
        # IMPORTANT: Only check messages AFTER the most recent user message (current query)
        if len(messages) >= 2:
            # Get the most recent user message (current query)
            user_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
            if user_messages:
                last_user_message_idx = None
                for i, msg in enumerate(messages):
                    if isinstance(msg, HumanMessage):
                        last_user_message_idx = i
                
                if last_user_message_idx is not None:
                    # Only check messages AFTER the last user message (current query context)
                    current_query_messages = messages[last_user_message_idx:]
                    user_request = user_messages[-1].content.lower()
                    viz_keywords = ['plot', 'chart', 'graph', 'visualize', 'visualization', 'draw', 'show me a graph', 'create a plot']
                    is_viz_request = any(keyword in user_request for keyword in viz_keywords)
                    
                    if is_viz_request:
                        # Only check agent messages in the current query context (after last user message)
                        agent_messages = [msg for msg in current_query_messages if isinstance(msg, AIMessage) and hasattr(msg, 'name') and msg.name]
                        financial_agent_called = any(msg.name == "FinancialAgent" for msg in agent_messages)
                        code_agent_called = any(msg.name == "CodeAgent" for msg in agent_messages)
                        
                        # If CodeAgent has already been called in THIS query, check if it completed successfully
                        if code_agent_called:
                            # Get the last CodeAgent message from current query
                            code_agent_messages = [msg for msg in agent_messages if msg.name == "CodeAgent"]
                            if code_agent_messages:
                                last_code_response = code_agent_messages[-1].content.lower()
                                # Check if CodeAgent successfully generated a visualization
                                success_indicators = [
                                    'plot', 'chart', 'graph', 'figure', 'visualization',
                                    'matplotlib', 'plt.show()', 'display', 'created',
                                    'generated', 'executed successfully', 'saved successfully'
                                ]
                                error_indicators = [
                                    'error', 'failed', 'exception', 'traceback',
                                    'cannot', "can't", 'unable'
                                ]
                                
                                # If CodeAgent response contains success indicators and no errors, FINISH
                                has_success = any(indicator in last_code_response for indicator in success_indicators)
                                has_error = any(indicator in last_code_response for indicator in error_indicators)
                                
                                if has_success and not has_error:
                                    # CodeAgent has successfully generated visualization in THIS query, FINISH
                                    return {"next": "FINISH"}
                                # If there's an error, don't route back to CodeAgent (prevent infinite loop)
                                elif has_error:
                                    return {"next": "FINISH"}
                        
                        # Route to CodeAgent only if FinancialAgent has provided data in THIS query and CodeAgent hasn't been called yet
                        if financial_agent_called and not code_agent_called:
                            if agent_messages and agent_messages[-1].name == "FinancialAgent":
                                last_content = agent_messages[-1].content.lower()
                                if any(indicator in last_content for indicator in ['price', 'date', 'closing', 'table', 'data', 'cannot create plots', "can't create"]):
                                    return {"next": "CodeAgent"}
        
        try:
            supervisor_chain = supervisor_prompt | llm.with_structured_output(RouteResponse)
            result = supervisor_chain.invoke(state)
            # Log supervisor decision for debugging
            print(f"Supervisor decision: {result.get('next', 'UNKNOWN')}")
            return result
        except Exception as e:
            try:
                regular_chain = supervisor_prompt | llm
                response = regular_chain.invoke(state)
                
                if hasattr(response, 'content'):
                    content = response.content.strip()
                else:
                    content = str(response).strip()
                
                valid_options = ["FINISH", "WebSearchAgent", "FinancialAgent", "CodeAgent"]
                
                for option in valid_options:
                    if option.lower() in content.lower() or content == option:
                        return {"next": option}
                
                json_match = re.search(r'\{[^}]*"next"[^}]*\}', content)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group())
                        if "next" in parsed and parsed["next"] in valid_options:
                            return {"next": parsed["next"]}
                    except:
                        pass
                
                print(f"Supervisor: Could not parse response '{content}', defaulting to FINISH")
                return {"next": "FINISH"}
                
            except Exception as e2:
                print(f"Supervisor error: {e}")
                print(f"Fallback parsing also failed: {e2}")
                return {"next": "FINISH"}
    
    return supervisor_agent, members


# Message truncation reducer - keeps only last 5 pairs (10 messages total)
def truncate_messages(left: Sequence[BaseMessage], right: Sequence[BaseMessage]) -> Sequence[BaseMessage]:
    """
    Reducer function that keeps only the last 5 message pairs (10 messages total).
    This prevents conversation history from growing too large and hitting token limits.
    """
    from langchain_core.messages import HumanMessage
    
    # Combine messages
    combined = list(left) + list(right)
    
    # Maximum messages to keep: 5 pairs = 10 messages
    MAX_MESSAGES = 10
    
    if len(combined) <= MAX_MESSAGES:
        return combined
    
    # Keep only the last MAX_MESSAGES messages
    # This ensures we always have the most recent conversation context
    truncated = combined[-MAX_MESSAGES:]
    
    # Log truncation for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Truncated messages from {len(combined)} to {len(truncated)} (keeping last {MAX_MESSAGES} messages)")
    
    return truncated


# Define the state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], truncate_messages]
    next: str


# Helper Function for Agent Nodes
def agent_node(state, agent, name):
    """Helper function for agent nodes."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"agent_node called for {name}")
    
    try:
        if not state or "messages" not in state:
            error_msg = f"{name} received invalid state."
            logger.warning(f"{name}: Invalid state received")
            return {"messages": [AIMessage(content=error_msg, name=name)]}
        
        logger.info(f"{name}: Invoking agent with {len(state['messages'])} messages")
        
        # Invoke the agent
        result = agent.invoke({"messages": state["messages"]})
        
        logger.info(f"{name}: Agent invoke completed, result type: {type(result)}")
        
        if not result or "messages" not in result or not result["messages"]:
            error_msg = f"{name} returned an empty or invalid response."
            logger.warning(f"{name}: Empty or invalid response")
            return {"messages": [AIMessage(content=error_msg, name=name)]}
        
        logger.info(f"{name}: Got {len(result['messages'])} messages in response")
        content = result["messages"][-1].content
        
        if not content:
            content = f"{name} completed but returned no content."
            logger.warning(f"{name}: No content in response")
        
        logger.info(f"{name}: Response content length: {len(content)} chars")
        
        # Clean Unicode characters
        content = content.replace('\u202f', ' ')
        content = content.replace('\u2009', ' ')
        content = content.replace('\u00a0', ' ')
        content = re.sub(r' +', ' ', content)
        
        return {
            "messages": [AIMessage(content=content, name=name)]
        }
    except Exception as e:
        error_msg = f"{name} encountered an error: {str(e)}"
        print(f"Error in {name}: {e}")
        return {
            "messages": [AIMessage(content=error_msg, name=name)]
        }


# Build the graph
def build_graph():
    """Build and compile the LangGraph workflow."""
    # Initialize components
    llm = get_llm()
    tools = initialize_tools()
    agents = create_agents(llm, tools)
    supervisor_agent, members = create_supervisor(llm)
    
    # Create agent nodes
    web_search_node = functools.partial(agent_node, agent=agents['web_search_agent'], name="WebSearchAgent")
    financial_node = functools.partial(agent_node, agent=agents['financial_agent'], name="FinancialAgent")
    code_node = functools.partial(agent_node, agent=agents['code_agent'], name="CodeAgent")
    
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("WebSearchAgent", web_search_node)
    workflow.add_node("FinancialAgent", financial_node)
    workflow.add_node("CodeAgent", code_node)
    workflow.add_node("Supervisor", supervisor_agent)
    
    # Define edges
    for member in members:
        workflow.add_edge(member, "Supervisor")
    
    # Supervisor decides the next agent or to finish
    conditional_map = {member: member for member in members}
    conditional_map["FINISH"] = END
    workflow.add_conditional_edges("Supervisor", lambda x: x["next"], conditional_map)
    
    # Entry point
    workflow.add_edge(START, "Supervisor")
    
    # Compile the graph with memory checkpointing
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)
    
    return graph


# Process query
def process_query(query: str, thread_id: str = None, graph_instance=None):
    """
    Process a financial query using the multi-agent system.
    
    Args:
        query: The user's financial query
        thread_id: Optional thread ID for conversation continuity
        graph_instance: Optional pre-built graph instance (for performance)
        
    Returns:
        Dictionary with response and metadata
    """
    import time
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    
    # Use provided graph instance or build new one (for backward compatibility)
    if graph_instance is None:
        logger.info("Building new graph instance...")
        graph = build_graph()
    else:
        graph = graph_instance
    
    config = {"configurable": {"thread_id": thread_id}}
    
    events = []
    response_parts = []
    start_time = time.perf_counter()
    
    try:
        logger.info(f"Starting query processing for thread {thread_id}: {query[:50]}...")
        
        event_count = 0
        last_event_time = start_time
        
        try:
            for event in graph.stream(
                {"messages": [HumanMessage(content=query)]},
                config=config
            ):
                event_count += 1
                elapsed = time.perf_counter() - start_time
                time_since_last = time.perf_counter() - last_event_time
                last_event_time = time.perf_counter()
                logger.info(f"Event {event_count} received after {elapsed:.2f}s (gap: {time_since_last:.2f}s)")
                logger.info(f"Event {event_count} keys: {list(event.keys())}")
                
                events.append(event)
                
                # Check if we've been waiting too long (potential hang)
                if time_since_last > 60:
                    logger.warning(f"Long gap detected: {time_since_last:.2f}s since last event")
                
                # Process event to extract response
                # Only process agent nodes (skip Supervisor which only has 'next' key)
                for node_name, node_state in event.items():
                    if node_name == "__end__":
                        logger.info("Received END event - query finished")
                        continue
                    
                    # Skip Supervisor node - it doesn't have agent messages
                    if node_name == "Supervisor":
                        logger.info(f"Skipping Supervisor node (only has routing info)")
                        continue
                    
                    logger.info(f"Processing node: {node_name}")
                    
                    if isinstance(node_state, dict):
                        logger.info(f"Node {node_name} state keys: {list(node_state.keys())}")
                        
                        if "messages" in node_state and node_state["messages"]:
                            logger.info(f"Node {node_name} has {len(node_state['messages'])} messages")
                            # Get the last AIMessage from this agent
                            for message in reversed(node_state["messages"]):
                                if isinstance(message, AIMessage):
                                    agent_name = getattr(message, 'name', node_name)
                                    content = getattr(message, 'content', str(message))
                                    content_preview = content[:100] + "..." if len(content) > 100 else content
                                    logger.info(f"Agent {agent_name} responded (length: {len(content)} chars): {content_preview}")
                                    response_parts.append({
                                        'agent': agent_name,
                                        'content': content
                                    })
                                    break  # Only take the last AIMessage
                            else:
                                logger.info(f"Node {node_name} has no AIMessage in messages")
                        else:
                            logger.info(f"Node {node_name} has no messages in state")
                    else:
                        logger.info(f"Node {node_name} state is not a dict: {type(node_state)}")
        except StopIteration:
            logger.info("Stream ended normally (StopIteration)")
        except Exception as stream_error:
            logger.error(f"Error in stream: {str(stream_error)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        total_time = time.perf_counter() - start_time
        logger.info(f"Query completed in {total_time:.2f}s with {event_count} events")
        logger.info(f"Response parts collected: {len(response_parts)}")
        for i, part in enumerate(response_parts):
            logger.info(f"  Part {i+1}: {part['agent']} ({len(part['content'])} chars)")
        
        # Combine all responses
        if response_parts:
            full_response = "\n\n".join([f"**{part['agent']}:**\n{part['content']}" for part in response_parts])
        else:
            # If no response parts were collected, try to extract the most recent agent response from the conversation
            logger.warning("No response parts collected - attempting to extract from conversation history")
            
            # Get the final state to check for any agent messages
            try:
                final_state = graph.get_state(config)
                if final_state and "values" in final_state:
                    state_messages = final_state["values"].get("messages", [])
                    # Look for the most recent AIMessage with a name (agent response)
                    for message in reversed(state_messages):
                        if isinstance(message, AIMessage) and hasattr(message, 'name') and message.name:
                            agent_name = message.name
                            content = getattr(message, 'content', str(message))
                            logger.info(f"Found recent agent response from {agent_name} in conversation history")
                            full_response = f"**{agent_name}:**\n{content}"
                            response_parts.append({
                                'agent': agent_name,
                                'content': content
                            })
                            break
            except Exception as e:
                logger.error(f"Error extracting response from conversation history: {e}")
            
            # If still no response, return error message
            if not response_parts:
                logger.error("No agent responses found in conversation history either")
                full_response = "Query processed but no agent responses were captured. The supervisor may have finished without routing to an agent. Please check server logs or try rephrasing your question."
        
        # Check if CodeAgent generated a plot in this query
        # Only return plot if CodeAgent was actually called in this query
        plot_path = None
        code_agent_called = any(part['agent'] == 'CodeAgent' for part in response_parts)
        
        if code_agent_called:
            # Check in multiple possible locations
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if os.path.dirname(__file__) else os.getcwd()
            possible_plot_paths = [
                os.path.join(base_dir, 'static', 'plots', 'plot.png'),
                os.path.join(os.getcwd(), 'static', 'plots', 'plot.png'),
                os.path.join(os.path.dirname(__file__), 'static', 'plots', 'plot.png'),
                'static/plots/plot.png',
                'plot.png'
            ]
            
            for plot_file in possible_plot_paths:
                if os.path.exists(plot_file):
                    # Check if plot was recently modified (within last 30 seconds)
                    plot_mtime = os.path.getmtime(plot_file)
                    time_since_modified = time.time() - plot_mtime
                    if time_since_modified < 30:  # Plot was modified in last 30 seconds
                        # Add timestamp to prevent browser caching
                        plot_path = f'/static/plots/plot.png?t={int(plot_mtime)}'
                        logger.info(f"Plot found at: {plot_file}, modified {time_since_modified:.1f}s ago, serving as: {plot_path}")
                        break
                    else:
                        logger.info(f"Plot found but too old ({time_since_modified:.1f}s), not including in response")
        else:
            logger.info("CodeAgent was not called, not checking for plot")
        
        logger.info(f"Returning response (length: {len(full_response)} chars)")
        
        result = {
            'success': True,
            'response': full_response,
            'thread_id': thread_id,
            'events': events
        }
        
        if plot_path:
            result['plot_path'] = plot_path
        
        return result
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        logger.error(f"Error after {elapsed:.2f}s: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': f'Error processing query: {str(e)}',
            'thread_id': thread_id
        }


# Main execution (for testing)
if __name__ == "__main__":
    # Check environment variables
    check_env_vars()

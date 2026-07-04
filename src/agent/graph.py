# src/agent/graph.py

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI

# Import calibration loader
from src.agent.memory.calibration import load_user_calibration

# Define your agent state
class AgentState(dict):
    pass

# Create the agent graph
def create_ultimate_agent_graph():
    graph = StateGraph(AgentState)

    # Example: add a tool node
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tool_node = ToolNode(llm)
    graph.add_node("llm", tool_node)

    # Add checkpoint saver
    saver = SqliteSaver.from_conn_string(":memory:")
    graph.set_checkpoint(saver)

    # Add edges (example: start → llm)
    graph.add_edge("START", "llm")
    graph.add_edge("llm", "END")

    return graph

# Run the agent
def run_ultimate_agent(input_text: str):
    graph = create_ultimate_agent_graph()

    # Load calibration data
    calibration = load_user_calibration()

    # Example: pass calibration into agent state
    initial_state = AgentState({
        "input": input_text,
        "calibration": calibration
    })

    result = graph.run(initial_state)
    return result

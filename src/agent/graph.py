# src/agent/graph.py
from src.agent.memory.memory import HybridMemoryManager
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from pathlib import Path

class AgentState(dict):
    pass

def create_ultimate_agent_graph():
    graph = StateGraph(AgentState)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tool_node = ToolNode(llm)
    graph.add_node("llm", tool_node)

    saver = SqliteSaver.from_conn_string(":memory:")
    graph.set_checkpoint(saver)

    graph.add_edge("START", "llm")
    graph.add_edge("llm", "END")

    return graph

def run_ultimate_agent(input_text: str):
    graph = create_ultimate_agent_graph()

    # Initialize memory manager
    memory_manager = HybridMemoryManager()

    # Seed calibration from JSON file
    seed_file = Path("src/config/user_calibration_seed.json")
    calibration = memory_manager.seed_from_json(seed_file)

    # Inject calibration into agent state
    initial_state = AgentState({
        "input": input_text,
        "calibration": calibration
    })

    result = graph.run(initial_state)
    return result

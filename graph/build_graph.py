from langgraph.graph import StateGraph
from graph.nodes import context_agent, preference_agent, risk_agent, loyalty_agent
from graph.nodes import device_optimizer_agent, analytics_logger_agent, fallback_agent, ux_personalizer_agent
from utils.helpers import MCPMessage
from pydantic import BaseModel
from typing import Any, Dict

class OrchestratorState(BaseModel):
    mcp_message: Dict[str, Any]

def node_adapter(agent_func):
    def wrapper(state):
        mcp = MCPMessage(**state.mcp_message)
        updated_mcp = agent_func(mcp)
        return {"mcp_message": updated_mcp.dict()}
    return wrapper

def build_payment_graph():
    g = StateGraph(OrchestratorState)
    g.add_node("context", node_adapter(context_agent.run))
    g.add_node("preference", node_adapter(preference_agent.run))
    g.add_node("risk", node_adapter(risk_agent.run))
    g.add_node("loyalty", node_adapter(loyalty_agent.run))
    g.add_node("device_optimizer", node_adapter(device_optimizer_agent.run))
    g.add_node("analytics_logger", node_adapter(analytics_logger_agent.run))
    g.add_node("fallback", node_adapter(fallback_agent.run))
    g.add_node("ux_personalizer", node_adapter(ux_personalizer_agent.run))
    # Define entrypoint
    g.add_edge("__start__", "context")
    # Define sequential flow
    g.add_edge("context", "preference")
    g.add_edge("preference", "risk")
    g.add_edge("risk", "loyalty")
    g.add_edge("loyalty", "device_optimizer")
    g.add_edge("device_optimizer", "analytics_logger")
    g.add_edge("analytics_logger", "fallback")
    g.add_edge("fallback", "ux_personalizer")
    return g.compile()

# Example function to run the graph (for testing)
def run_orchestrator(input_msg: MCPMessage) -> MCPMessage:
    graph_app = build_payment_graph()
    state = {"mcp_message": input_msg.dict()}
    result = graph_app.invoke(state)
    return MCPMessage(**result["mcp_message"])

from utils.helpers import MCPMessage

def run(input_msg: MCPMessage) -> MCPMessage:
    # Enrich context with dummy values if missing
    context = input_msg.context.copy()
    context.setdefault("device", "iPhone 13")
    context.setdefault("location", "UK")
    context.setdefault("loyalty_status", "Gold")
    # Return updated MCPMessage
    return MCPMessage(
        role="context_agent",
        intent="enrich_context",
        context=context,
        requested_action="return_context"
    )

from utils.helpers import MCPMessage

def run(input_msg: MCPMessage) -> MCPMessage:
    context = input_msg.context.copy()
    risk = context.get("risk_score", 0.0)
    if risk > 0.4:
        fallback = "Offer phone support or wallet switch"
    else:
        fallback = "No fallback needed"
    context["fallback_action"] = fallback
    return MCPMessage(
        role="fallback_agent",
        intent="handle_fallback",
        context=context,
        requested_action="return_fallback"
    ) 
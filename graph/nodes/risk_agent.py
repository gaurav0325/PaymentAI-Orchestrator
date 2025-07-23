from utils.helpers import MCPMessage

def run(input_msg: MCPMessage) -> MCPMessage:
    context = input_msg.context.copy()
    # Dummy risk logic
    if context.get("loyalty_status") == "Gold":
        risk_score = 0.1
    else:
        risk_score = 0.5
    context["risk_score"] = risk_score
    return MCPMessage(
        role="risk_agent",
        intent="evaluate_risk",
        context=context,
        requested_action="return_risk"
    )

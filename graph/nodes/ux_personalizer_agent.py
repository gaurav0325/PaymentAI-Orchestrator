from utils.helpers import MCPMessage

def run(input_msg: MCPMessage) -> MCPMessage:
    context = input_msg.context.copy()
    loyalty = context.get("loyalty_status", "None")
    if loyalty == "Gold":
        message = "Welcome, valued Gold member! Enjoy your exclusive offers."
    else:
        message = "Welcome! Choose your preferred payment method."
    context["ux_message"] = message
    return MCPMessage(
        role="ux_personalizer_agent",
        intent="personalize_ux",
        context=context,
        requested_action="return_ux_message"
    ) 
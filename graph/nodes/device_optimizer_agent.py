from utils.helpers import MCPMessage

def run(input_msg: MCPMessage) -> MCPMessage:
    context = input_msg.context.copy()
    device = context.get("device", "Unknown")
    if "iPhone" in device:
        recommendation = "Use Apple Pay with Face ID"
    elif "Android" in device:
        recommendation = "Use Google Pay with biometric fallback"
    else:
        recommendation = "Use 3DS Redirect"
    context["device_recommendation"] = recommendation
    return MCPMessage(
        role="device_optimizer_agent",
        intent="optimize_device_payment",
        context=context,
        requested_action="return_device_recommendation"
    ) 
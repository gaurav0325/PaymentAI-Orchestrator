from utils.helpers import MCPMessage

def run(input_msg: MCPMessage) -> MCPMessage:
    context = input_msg.context.copy()
    # Dummy loyalty logic
    offers = []
    if context.get("loyalty_status") == "Gold":
        offers.append("10% off next flight")
        offers.append("Free lounge access")
    context["loyalty_offers"] = offers
    return MCPMessage(
        role="loyalty_agent",
        intent="check_loyalty_offers",
        context=context,
        requested_action="return_offers"
    ) 
from utils.helpers import MCPMessage, load_business_rules

def run(input_msg: MCPMessage) -> MCPMessage:
    context = input_msg.context.copy()
    flight = context.get("flight", {})
    rules = load_business_rules()
    # Check for block_payment rules
    for rule in rules:
        if rule.get("type") == "block_payment":
            cond = rule.get("condition", {})
            # Check if flight_from_country matches
            if cond.get("flight_from_country") and \
               (flight.get("from", "").lower().find(cond["flight_from_country"].lower()) != -1 or context.get("location", "").lower() == cond["flight_from_country"].lower()):
                action = rule.get("action", {})
                if action.get("block"):
                    context["payment_methods"] = []
                    context["payment_block_reason"] = action.get("message", "Payment blocked by business rule.")
                    return MCPMessage(
                        role="preference_agent",
                        intent="personalize_methods",
                        context=context,
                        requested_action="return_methods"
                    )
    # Dummy logic: personalize payment methods
    if context.get("device") == "iPhone 13":
        methods = ["Apple Pay", "Credit Card", "PayPal"]
    else:
        methods = ["Google Pay", "Credit Card", "PayPal"]
    if context.get("loyalty_status") == "Gold":
        methods.append("Miles + Pay")
    context["payment_methods"] = methods
    return MCPMessage(
        role="preference_agent",
        intent="personalize_methods",
        context=context,
        requested_action="return_methods"
    )

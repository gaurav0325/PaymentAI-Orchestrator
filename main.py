import sys
import os
import subprocess
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'utils')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'graph')))

import streamlit as st
import json
from utils.helpers import MCPMessage, load_business_rules
from graph.build_graph import run_orchestrator

# For Mermaid diagram rendering
from streamlit.components.v1 import html

data_dir = os.path.join(os.path.dirname(__file__), 'data')

# Load sample users
def load_users():
    with open(os.path.join(data_dir, 'sample_users.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

# Remove sidebar_tab and Project Summary logic from main.py
# Only keep business rules admin and customer journey UI

st.set_page_config(page_title="PaymentAI-Orchestrator Demo", layout="wide")
st.title("PaymentAI-Orchestrator: User Journey Demo")

# --- Sidebar: Business Rules Admin ---
st.sidebar.header("Business Rules Admin")
business_rules = load_business_rules()
for rule in business_rules:
    st.sidebar.markdown(f"**{rule['id']}**: {rule['description']}")
    st.sidebar.caption(f"Type: {rule['type']} | Condition: {rule['condition']} | Action: {rule['action']}")
ADMIN_PORT = 8508
if st.sidebar.button(f"Open Full Admin UI (port {ADMIN_PORT})"):
    admin_path = os.path.join("frontend", "admin_rules.py")
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", admin_path, f"--server.port={ADMIN_PORT}"])
    st.sidebar.markdown(f"[Click here to open Admin UI](http://localhost:{ADMIN_PORT})")
else:
    st.sidebar.markdown(f"[Click here to open Admin UI](http://localhost:{ADMIN_PORT})")

# --- Main: User selection and workflow ---
users = load_users()
user_options = {f"{u['user_id']} ({u.get('location', 'Unknown')})": u for u in users}
user_key = st.selectbox("Select a user", list(user_options.keys()))
user = user_options[user_key]

st.subheader("User Context")
st.json(user)

# --- Workflow Diagram ---
def render_mermaid(user):
    user_id = user.get('user_id', 'N/A')
    device = user.get('device', 'N/A')
    location = user.get('location', 'N/A')
    loyalty = user.get('loyalty_status', 'N/A')
    mermaid = f'''
graph TD
    A["User: {user_id}\nDevice: {device}\nLocation: {location}\nLoyalty: {loyalty}"] --> B["Orchestrator"]
    B --> C["Context Agent"]
    C --> D["Preference Agent"]
    D --> E["Risk Agent"]
    E --> F["Loyalty Agent"]
    F --> G["Device Optimizer"]
    G --> H["Analytics Logger"]
    H --> I["Fallback Agent"]
    I --> J["UX Personalizer"]
    B -.-> K["Business Rules"]
    B -.-> L["Sample Data"]
    B -.-> M["Memory/State"]
    style K fill:#f9f,stroke:#333,stroke-width:2px
    style L fill:#bbf,stroke:#333,stroke-width:2px
    style M fill:#bfb,stroke:#333,stroke-width:2px
    style B fill:#ffd,stroke:#333,stroke-width:2px
    style A fill:#fff,stroke:#333,stroke-width:2px
    style J fill:#efe,stroke:#333,stroke-width:2px
    style C fill:#efe,stroke:#333,stroke-width:2px
    style D fill:#efe,stroke:#333,stroke-width:2px
    style E fill:#efe,stroke:#333,stroke-width:2px
    style F fill:#efe,stroke:#333,stroke-width:2px
    style G fill:#efe,stroke:#333,stroke-width:2px
    style H fill:#efe,stroke:#333,stroke-width:2px
    style I fill:#efe,stroke:#333,stroke-width:2px
'''
    html(f'<div class="mermaid">{mermaid}</div>'
         '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>'
         '<script>mermaid.initialize({startOnLoad:true});</script>',
         height=600)

render_mermaid(user)

# --- Sequence Diagram ---
def render_sequence_diagram(steps):
    mermaid = "sequenceDiagram\n"
    mermaid += "    participant U as User\n"
    mermaid += "    participant O as Orchestrator\n"
    mermaid += "    participant C as Context\n"
    mermaid += "    participant P as Preference\n"
    mermaid += "    participant R as Risk\n"
    mermaid += "    participant L as Loyalty\n"
    mermaid += "    participant D as Device\n"
    mermaid += "    participant A as Analytics\n"
    mermaid += "    participant F as Fallback\n"
    mermaid += "    participant X as UX\n"
    mermaid += "    U->>O: Select user and start payment\n"
    for step in steps:
        agent = step.get('agent', '?')
        data = step.get('data', {})
        # Only show a summary of key fields, avoid multiline/long text
        summary = ', '.join(f'{k}: {str(v)[:20]}' for k, v in data.items() if k in [
            'payment_methods', 'risk_score', 'loyalty_offers', 'device_recommendation',
            'fallback_action', 'ux_message', 'payment_block_reason'
        ])
        if not summary:
            summary = ', '.join(f'{k}' for k in data.keys())
        mermaid += f"    O->>{agent}: Call {agent} Agent\n"
        mermaid += f"    {agent}-->>O: {summary}\n"
    html(f'<div class="mermaid">{mermaid}</div>'
         '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>'
         '<script>mermaid.initialize({startOnLoad:true});</script>',
         height=600)

def run_orchestrator_with_steps(mcp):
    from graph.nodes import context_agent, preference_agent, risk_agent, loyalty_agent
    from graph.nodes import device_optimizer_agent, analytics_logger_agent, fallback_agent, ux_personalizer_agent
    steps = []
    agents = [
        ("C", context_agent.run),
        ("P", preference_agent.run),
        ("R", risk_agent.run),
        ("L", loyalty_agent.run),
        ("D", device_optimizer_agent.run),
        ("A", analytics_logger_agent.run),
        ("F", fallback_agent.run),
        ("X", ux_personalizer_agent.run),
    ]
    current = mcp
    for agent_code, agent_func in agents:
        current = agent_func(current)
        steps.append({"agent": agent_code, "data": current.context})
    return current, steps

if st.button("Run Orchestrator"):
    context = {k: v for k, v in user.items() if k != 'user_id'}
    mcp = MCPMessage(
        role="orchestrator",
        intent="optimize_payment",
        context=context,
        requested_action="invoke:ContextAgent"
    )
    result, steps = run_orchestrator_with_steps(mcp)
    st.subheader("Orchestrator Output")
    st.json(result.context)
    if result.context.get("payment_block_reason"):
        st.error(f"Payment Blocked: {result.context['payment_block_reason']}")
    else:
        st.success("Payment methods available:")
        st.write(result.context.get("payment_methods", []))
    if result.context.get("loyalty_offers"):
        st.info(f"Loyalty Offers: {result.context['loyalty_offers']}" )
    if result.context.get("risk_score") is not None:
        st.warning(f"Risk Score: {result.context['risk_score']}")
    if result.context.get("device_recommendation"):
        st.info(f"Device Recommendation: {result.context['device_recommendation']}")
    if result.context.get("fallback_action"):
        st.info(f"Fallback Action: {result.context['fallback_action']}")
    if result.context.get("ux_message"):
        st.info(f"UX Message: {result.context['ux_message']}")
    st.subheader("Agent Sequence Diagram")
    render_sequence_diagram(steps) 
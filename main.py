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
from streamlit.components.v1 import html

data_dir = os.path.join(os.path.dirname(__file__), 'data')

# Load sample users
def load_users():
    with open(os.path.join(data_dir, 'sample_users.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

# Logging function for Application Log page
def log_event(message):
    try:
        with open("app_log.txt", "a") as f:
            f.write(message + "\n")
    except Exception as e:
        pass  # On Streamlit Cloud, file writes are ephemeral

st.set_page_config(page_title="PaymentAI-Orchestrator Demo", layout="wide")

# --- Sidebar Navigation ---
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Project Summary", "Application Log", "Admin UI (Business Rules)"]
)

# Use a placeholder admin subdomain for the admin UI
ADMIN_UI_URL = "https://multi-ai-agent-paymentmethods-admin-ga.streamlit.app/"

if page == "Home":
    st.title("PaymentAI-Orchestrator: User Journey Demo")
    users = load_users()
    user_options = {f"{u['user_id']} ({u.get('location', 'Unknown')})": u for u in users}
    user_key = st.selectbox("Select a user", list(user_options.keys()))
    user = user_options[user_key]
    st.subheader("User Context")
    st.json(user)
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
        log_event(f"User ran orchestrator for user_id: {user['user_id']}")
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
elif page == "Project Summary":
    st.title("Project Summary")
    st.markdown('''
**PaymentAI-Orchestrator**

- **Objective:** Enable real-time personalization of payment journeys for airline customers using a multi-agent AI system.
- **Orchestrator:** LLM-based agent (LangGraph) that routes, aggregates, and manages agent workflows.
- **Agents:**
    - Context Agent: Gathers user/session context
    - Preference Agent: Personalizes payment methods
    - Risk Agent: Assesses risk
    - Loyalty Agent: Checks loyalty offers
    - Device Optimizer: Suggests device-based payment options
    - Analytics Logger: Logs decisions
    - Fallback Agent: Handles fallback/alternative flows
    - UX Personalizer: Customizes frontend messaging
- **Business Rules:** Dynamic, admin-editable rules for compliance and custom logic
- **Frontend:** Streamlit UI for both user journey and admin management
- **Data:** Sample users, offers, risk flags, devices, business rules, etc.
- **Workflow:**
    1. User lands on payment page
    2. Orchestrator collects context, routes to agents
    3. Agents enrich context and personalize journey
    4. Business rules are applied dynamically
    5. Final decision and options are shown to the user
- **Tech Stack:** Python, LangChain, LangGraph, Streamlit, Pydantic, JSON
    ''')
elif page == "Application Log":
    st.title("Application Log")
    log_file = "app_log.txt"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = f.read()
        st.text_area("Application Log", logs, height=400)
    else:
        st.info("No log file found. On Streamlit Cloud, logs are available via the cloud dashboard.")
elif page == "Admin UI (Business Rules)":
    st.title("Business Rules Admin UI")
    st.write("Manage business rules below. All changes are logged.")
    rules = load_business_rules()
    # Display rules in a table with edit/delete buttons
    for idx, rule in enumerate(rules):
        with st.expander(f"{rule['id']}: {rule['description']}"):
            st.json(rule)
            col1, col2, col3 = st.columns([1,1,2])
            with col1:
                if st.button(f"Edit", key=f"edit_{idx}"):
                    st.session_state['edit_rule'] = idx
            with col2:
                if st.button(f"Delete", key=f"delete_{idx}"):
                    rules.pop(idx)
                    from utils.helpers import save_business_rules
                    save_business_rules(rules)
                    log_event(f"Deleted business rule: {rule['id']}")
                    st.success(f"Deleted rule {rule['id']}")
                    st.experimental_rerun()
    # Add or edit rule form
    st.subheader("Add / Edit Business Rule")
    def rule_form(default=None):
        with st.form(key="rule_form"):
            rule_id = st.text_input("Rule ID", value=default.get('id', '') if default else '')
            description = st.text_input("Description", value=default.get('description', '') if default else '')
            rule_type = st.selectbox("Type", ["block_payment"], index=0 if not default or default.get('type') == 'block_payment' else 0)
            flight_from_country = st.text_input("Flight From Country", value=default.get('condition', {}).get('flight_from_country', '') if default else '')
            block = st.checkbox("Block Payment?", value=default.get('action', {}).get('block', False) if default else False)
            message = st.text_input("Block Message", value=default.get('action', {}).get('message', '') if default else '')
            submitted = st.form_submit_button("Save Rule")
            if submitted:
                new_rule = {
                    "id": rule_id,
                    "description": description,
                    "type": rule_type,
                    "condition": {"flight_from_country": flight_from_country},
                    "action": {"block": block, "message": message}
                }
                from utils.helpers import save_business_rules
                if default:
                    rules[st.session_state['edit_rule']] = new_rule
                    log_event(f"Edited business rule: {rule_id}")
                else:
                    rules.append(new_rule)
                    log_event(f"Added business rule: {rule_id}")
                save_business_rules(rules)
                st.success(f"Saved rule {rule_id}")
                if 'edit_rule' in st.session_state:
                    del st.session_state['edit_rule']
                st.experimental_rerun()
    # Edit mode
    if 'edit_rule' in st.session_state:
        rule_to_edit = rules[st.session_state['edit_rule']]
        st.subheader(f"Edit Rule: {rule_to_edit['id']}")
        rule_form(default=rule_to_edit)
        if st.button("Cancel Edit"):
            del st.session_state['edit_rule']
            st.experimental_rerun()
    else:
        st.subheader("Add New Rule")
        rule_form() 
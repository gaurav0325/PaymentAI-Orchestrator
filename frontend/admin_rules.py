import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import json
from utils.helpers import load_business_rules, save_business_rules, add_business_rule, edit_business_rule, delete_business_rule

# Set Streamlit port if running directly
#if __name__ == "__main__":
  #  import subprocess
  #  subprocess.run([sys.executable, "-m", "streamlit", "run", __file__, "--server.port=8505"])
  #  sys.exit(0)

st.set_page_config(page_title="Business Rules Admin", layout="wide")
st.title("Business Rules Administration")

# Load rules
rules = load_business_rules()

# Display all rules
st.header("Current Business Rules")
for rule in rules:
    with st.expander(f"{rule['id']}: {rule['description']}"):
        st.json(rule)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Edit {rule['id']}"):
                st.session_state['edit_rule'] = rule['id']
        with col2:
            if st.button(f"Delete {rule['id']}"):
                delete_business_rule(rule['id'])
                st.success(f"Deleted rule {rule['id']}")
                st.experimental_rerun()

# Add or edit rule
st.header("Add / Edit Business Rule")
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
            if default:
                edit_business_rule(rule_id, new_rule)
                st.success(f"Edited rule {rule_id}")
            else:
                add_business_rule(new_rule)
                st.success(f"Added rule {rule_id}")
            st.experimental_rerun()

# Edit mode
edit_id = st.session_state.get('edit_rule')
if edit_id:
    rule_to_edit = next((r for r in rules if r['id'] == edit_id), None)
    st.subheader(f"Edit Rule: {edit_id}")
    rule_form(default=rule_to_edit)
    if st.button("Cancel Edit"):
        st.session_state['edit_rule'] = None
        st.experimental_rerun()
else:
    st.subheader("Add New Rule")
    rule_form() 
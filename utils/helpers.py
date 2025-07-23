from typing import Dict, Any, List
from pydantic import BaseModel
import json
import os

class MCPMessage(BaseModel):
    role: str
    intent: str
    context: Dict[str, Any]
    requested_action: str

BUSINESS_RULES_PATH = os.path.join(os.path.dirname(__file__), '../data/business_rules.json')

def load_business_rules() -> List[Dict[str, Any]]:
    with open(BUSINESS_RULES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_business_rules(rules: List[Dict[str, Any]]):
    with open(BUSINESS_RULES_PATH, 'w', encoding='utf-8') as f:
        json.dump(rules, f, indent=2)

def add_business_rule(rule: Dict[str, Any]):
    rules = load_business_rules()
    rules.append(rule)
    save_business_rules(rules)

def edit_business_rule(rule_id: str, updated_rule: Dict[str, Any]):
    rules = load_business_rules()
    for i, rule in enumerate(rules):
        if rule.get('id') == rule_id:
            rules[i] = updated_rule
            break
    save_business_rules(rules)

def delete_business_rule(rule_id: str):
    rules = load_business_rules()
    rules = [rule for rule in rules if rule.get('id') != rule_id]
    save_business_rules(rules)

import json
from typing import List
from engine import Rule

def load_rules(path: str) -> List[Rule]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    rules = []
    for i, r in enumerate(raw, start=1):
        rules.append(Rule(
            antecedents=r.get("if", []),
            consequent=r["then"],
            priority=r.get("priority", 0),
            name=r.get("name", f"Rule #{i}")
        ))
    return rules

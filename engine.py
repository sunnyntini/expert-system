from dataclasses import dataclass
from typing import List, Set, Dict, Any


@dataclass
class Rule:
    antecedents: List[str]
    consequent: str
    priority: int = 0
    name: str = ""


class ForwardChainingEngine:
    """ forward-chaining inference logic.

    A rule fires when every antecedent is in working memory and its consequent is not yet known.
    Firing adds the consequent as a new fact, which may enable further rules
    """

    def __init__(self, rules: List[Rule]):
        self.rules = rules
        self.facts: Set[str] = set()
        self.initial_facts: Set[str] = set()
        self.trace: List[Dict[str, Any]] = []

    def assert_facts(self, initial: List[str]) -> None:
        """Store initial facts into the working memory."""
        self.facts.update(initial)
        self.initial_facts.update(initial)

    def can_fire(self, rule: Rule) -> bool:
        """Return True if all antecedents are true and consequent not yet known"""
        if rule.consequent in self.facts:
            return False
        return all(a in self.facts for a in rule.antecedents)

    def run(self) -> None:
        """Forward chaining loop: fire rules until none can fire.

        Conflict resolution: highest priority first; ties are broken by
        position in the rule file (earlier rule wins).
        """
        while True:
            candidates = [(i, r) for i, r in enumerate(self.rules) if self.can_fire(r)]
            if not candidates:
                break
            _, rule = min(candidates, key=lambda c: (-c[1].priority, c[0]))
            self.facts.add(rule.consequent)
            self.trace.append({
                "step": len(self.trace) + 1,
                "rule": rule.name,
                "because": list(rule.antecedents),
                "derived": rule.consequent,
            })

    def conclusions(self) -> Dict[str, List[str]]:
        """Return separated results (recommendations, specs, other facts).
        Only facts that were derived are reported.
        """
        derived = self.facts - self.initial_facts
        result: Dict[str, List[str]] = {"recommendations": [], "specs": [], "other": []}
        for fact in sorted(derived):
            if fact.startswith("recommend:"):
                result["recommendations"].append(fact.split(":", 1)[1])
            elif fact.startswith("spec:"):
                result["specs"].append(fact.split(":", 1)[1])
            else:
                result["other"].append(fact)
        return result

    def explain(self, fact: str) -> str:
        """Rule and fact explanation"""
        for step in self.trace:
            if step["derived"] == fact:
                return f"derived from rule '{step['rule']}' because {', '.join(step['because'])}"
        if fact in self.initial_facts:
            return "given by the user"
        return "not derived"

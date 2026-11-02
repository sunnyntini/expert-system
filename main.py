from kb_loader import load_rules
from engine import ForwardChainingEngine

KB_PATH = "kb/laptop_rules.json"


def ask_yes_no(question: str) -> bool:
    return input(f"{question} (y/n): ").strip().lower().startswith("y")


def ask_choice(question: str, options):
    """Ask the user to pick one option; returns the chosen string."""
    while True:
        answer = input(f"{question} ({'/'.join(options)}): ").strip().lower()
        if answer in options:
            return answer
        print(f"  Please type one of: {', '.join(options)}")


def collect_initial_facts():
    facts = []
    budget = ask_choice("What is your budget?", ["low", "medium", "high"])
    facts.append(f"budget_{budget}")

    yes_no_questions = [
        ("Is portability important?", "portable"),
        ("Do you need long battery life?", "long_battery"),
        ("Will you use it for gaming?", "gaming"),
        ("Will you do creative work (video, design, music)?", "creative_work"),
        ("Is it only for office / light tasks?", "office_only"),
        ("Do you need AI acceleration (e.g. ML workloads)?", "needs_ai_accel"),
        ("Do you want a large screen?", "large_screen"),
        ("Do you travel often?", "travel_often"),
    ]
    for question, fact in yes_no_questions:
        if ask_yes_no(question):
            facts.append(fact)

    os_pref = ask_choice("Preferred OS?", ["windows", "macos", "linux", "none"])
    if os_pref != "none":
        facts.append(f"pref_os_{os_pref}")
    return facts


def main():
    rules = load_rules(KB_PATH)
    engine = ForwardChainingEngine(rules)
    engine.assert_facts(collect_initial_facts())
    engine.run()
    result = engine.conclusions()

    print()
    if not result["recommendations"]:
        print("> No specific laptop recommendation for these answers.")
    for rec in result["recommendations"]:
        print(f"> Recommendation: {rec}")
        print(f"> Explanation: {engine.explain('recommend:' + rec)}")
    for spec in result["specs"]:
        print(f"> Suggested spec: {spec}")
        print(f">   Explanation: {engine.explain('spec:' + spec)}")
    for fact in result["other"]:
        print(f"> Derived fact: {fact}")

    print("\nRules fired (in order):")
    if not engine.trace:
        print("  (none)")
    for step in engine.trace:
        print(f"  {step['step']}. {step['rule']}: IF {' AND '.join(step['because'])} "
              f"THEN {step['derived']}")


if __name__ == "__main__":
    main()

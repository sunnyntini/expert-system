import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine import ForwardChainingEngine, Rule
from kb_loader import load_rules

KB = os.path.join(os.path.dirname(__file__), "..", "kb", "laptop_rules.json")


def infer(facts, rules=None):
    engine = ForwardChainingEngine(rules or load_rules(KB))
    engine.assert_facts(facts)
    engine.run()
    return engine


class TestKnowledgeBase(unittest.TestCase):
    # (input facts, expected derived facts)
    CASES = [
        (["budget_high", "portable", "long_battery"], {"recommend:premium_ultrabook"}),
        (["budget_low", "office_only", "portable"], {"recommend:budget_ultrabook"}),
        (["gaming", "budget_medium"], {"recommend:midrange_gaming_laptop"}),
        (["gaming", "budget_high"], {"recommend:high_end_gaming_laptop"}),
        (["creative_work", "portable"], {"spec:ram_16_plus"}),
        (["creative_work", "large_screen"], {"spec:display_15_plus_color_accurate"}),
        (["travel_often", "long_battery"], {"spec:battery_60wh_plus"}),
        (["pref_os_macos"], {"spec:macos_required"}),
        (["needs_ai_accel"], {"spec:gpu_with_tensor_cores"}),
        (["pref_os_linux", "office_only"], {"spec:linux_friendly_hw"}),
        # several rules at once
        (["budget_high", "portable", "long_battery", "creative_work", "travel_often"],
         {"recommend:premium_ultrabook", "spec:ram_16_plus", "spec:battery_60wh_plus"}),
        # nothing should fire
        (["budget_low"], set()),
        ([], set()),
        # partial match must NOT fire
        (["budget_high", "portable"], set()),
    ]

    def test_cases(self):
        for facts, expected in self.CASES:
            with self.subTest(facts=facts):
                e = infer(facts)
                self.assertEqual(e.facts - set(facts), expected)

    def test_at_least_ten_rules(self):
        self.assertGreaterEqual(len(load_rules(KB)), 10)


class TestEngine(unittest.TestCase):
    def test_chaining(self):
        rules = [Rule(["b"], "c", name="r2"), Rule(["a"], "b", name="r1")]
        e = infer(["a"], rules)
        self.assertIn("c", e.facts)
        self.assertEqual([s["rule"] for s in e.trace], ["r1", "r2"])

    def test_priority_order(self):
        rules = [Rule(["a"], "low", priority=1, name="low"),
                 Rule(["a"], "high", priority=9, name="high")]
        e = infer(["a"], rules)
        self.assertEqual(e.trace[0]["rule"], "high")

    def test_terminates_on_cycle(self):
        rules = [Rule(["a"], "b"), Rule(["b"], "a")]
        e = infer(["a"], rules)
        self.assertEqual(e.facts, {"a", "b"})

    def test_does_not_refire(self):
        e = infer(["a"], [Rule(["a"], "b")])
        self.assertEqual(len(e.trace), 1)

    def test_conclusions_split(self):
        rules = [Rule(["a"], "recommend:x"), Rule(["a"], "spec:y"), Rule(["a"], "z")]
        c = infer(["a"], rules).conclusions()
        self.assertEqual(c, {"recommendations": ["x"], "specs": ["y"], "other": ["z"]})

    def test_explain(self):
        e = infer(["a"], [Rule(["a"], "b", name="R")])
        self.assertIn("'R'", e.explain("b"))


if __name__ == "__main__":
    unittest.main()

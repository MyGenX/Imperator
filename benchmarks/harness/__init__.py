"""Imperator real-world benchmark harness.

Runs Claude Code headless on a suite of realistic tasks under A/B conditions
(with vs. without the compiled Imperator ruleset) and compares what actually
happened: tokens spent, files/lines touched, tool calls, correctness, latency,
and rule-adherence quality (LLM-as-judge).
"""

"""
AAIS Engine Core v2.2 — Deterministic, Replayable, Cryptographically Checkpointed
=================================================================================
Event-sourced, pure-rule workflow engine with snapshot hashing and replay mode.
"""

from __future__ import annotations
import json
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


# ─────────────────────────────────────────────
# Event Model
# ─────────────────────────────────────────────

@dataclass
class Event:
    type: str
    payload: Dict[str, Any]
    seq: int = 0


# ─────────────────────────────────────────────
# Deterministic State
# ─────────────────────────────────────────────

class DeterministicState:
    def __init__(self) -> None:
        self.data: Dict[str, Any] = {}
        self.events: List[Event] = []
        self.seq_counter = 0

    def apply(self, event: Event) -> None:
        """Apply event deterministically and update state."""
        event.seq = self.seq_counter
        self.seq_counter += 1

        self.events.append(event)

        for k, v in event.payload.items():
            self.data[k] = v

    def snapshot(self) -> Dict[str, Any]:
        return dict(self.data)


# ─────────────────────────────────────────────
# Rule Model
# ─────────────────────────────────────────────

class Rule:
    def __init__(self, name: str, evaluator):
        self.name = name
        self.evaluator = evaluator

    def evaluate(self, state: DeterministicState) -> Tuple[bool, List[Event]]:
        return self.evaluator(state)


# ─────────────────────────────────────────────
# Workflow Model
# ─────────────────────────────────────────────

class Step:
    def __init__(self, name: str, rules: List[Rule]):
        self.name = name
        self.rules = rules


class Workflow:
    def __init__(self, steps: List[Step]):
        self.steps = steps
        self.current = 0

    def current_step(self) -> Step | None:
        if self.current < len(self.steps):
            return self.steps[self.current]
        return None

    def advance(self) -> None:
        self.current += 1


# ─────────────────────────────────────────────
# Deterministic Engine
# ─────────────────────────────────────────────

class DeterministicEngine:
    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        self.state = DeterministicState()
        self.trace: List[Dict] = []

    # Snapshot hashing for determinism proof
    def _hash_state(self) -> str:
        return hashlib.sha256(
            json.dumps(self.state.snapshot(), sort_keys=True).encode()
        ).hexdigest()

    def run(self, inputs: List[Dict[str, Any]]) -> List[Dict]:
        """Load all inputs first, then execute workflow deterministically."""
        for inp in inputs:
            self.state.apply(Event("input", inp))

        while self.workflow.current_step():
            self._cycle()

        return self.trace

    def _cycle(self) -> None:
        step = self.workflow.current_step()
        if not step:
            return

        step_trace = {"step": step.name, "rules": []}

        for rule in step.rules:
            fired, events = rule.evaluate(self.state)

            for e in events:
                self.state.apply(e)

            step_trace["rules"].append({
                "rule": rule.name,
                "fired": fired,
                "events": [
                    {"type": e.type, "payload": e.payload, "seq": e.seq}
                    for e in events
                ],
                "state": self.state.snapshot(),
                "state_hash": self._hash_state()
            })

        self.trace.append(step_trace)
        self.workflow.advance()

    # Replay mode — deterministic reconstruction
    def replay(self, events: List[Event]) -> Dict[str, Any]:
        self.state = DeterministicState()
        for e in events:
            self.state.apply(e)
        return self.state.snapshot()


# ─────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────

if __name__ == "__main__":
    def needs_approval(state: DeterministicState):
        amount = state.data.get("amount", 0)
        if amount > 1000:
            return True, [Event("approved", {"approved": True})]
        return False, []

    def finalize(state: DeterministicState):
        return True, [Event("status", {"status": "completed"})]

    rule_check = Rule("CheckAmount", needs_approval)
    rule_finalize = Rule("Finalize", finalize)

    step1 = Step("Validation", [rule_check])
    step2 = Step("Completion", [rule_finalize])
    workflow = Workflow([step1, step2])

    engine = DeterministicEngine(workflow)
    trace = engine.run([{"amount": 1500}])

    print(json.dumps(trace, indent=2))

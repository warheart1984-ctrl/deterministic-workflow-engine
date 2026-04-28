# engine_core.py
# Prototype: Deterministic Logic + State + Workflow Engine


class State:

    def __init__(self, initial=None):
        self.data = initial or {}
        self.history = []

    def update(self, key, value):
        self.data[key] = value
        self.history.append((key, value))

    def snapshot(self):
        return dict(self.data)


class Rule:

    def __init__(self, name, condition, action):
        self.name = name
        self.condition = condition  # function(state) -> bool
        self.action = action        # function(state) -> None

    def apply(self, state):
        if self.condition(state):
            self.action(state)
            return True
        return False


class Step:

    def __init__(self, name, rules):
        self.name = name
        self.rules = rules  # list of Rule objects


class Workflow:

    def __init__(self, steps):
        self.steps = steps
        self.current = 0

    def next_step(self):
        if self.current < len(self.steps):
            step = self.steps[self.current]
            self.current += 1
            return step
        return None


class Engine:

    def __init__(self, state, workflow):
        self.state = state
        self.workflow = workflow
        self.trace = []

    def run(self):
        while True:
            step = self.workflow.next_step()
            if not step:
                break

            step_trace = {"step": step.name, "rules": []}

            for rule in step.rules:
                fired = rule.apply(self.state)
                step_trace["rules"].append({
                    "rule": rule.name,
                    "fired": fired,
                    "state": self.state.snapshot()
                })

            self.trace.append(step_trace)

        return self.trace


# -------------------------
# Demo / Example Usage
# -------------------------
if __name__ == "__main__":

    # --- Define rules ---
    def needs_approval(state):
        return state.data.get("amount", 0) > 1000

    def approve(state):
        state.update("approved", True)

    def finalize(state):
        state.update("status", "completed")

    rule_check = Rule("CheckAmount", needs_approval, approve)
    rule_finalize = Rule("Finalize", lambda s: True, finalize)

    # --- Define workflow ---
    step1 = Step("Validation", [rule_check])
    step2 = Step("Completion", [rule_finalize])
    workflow = Workflow([step1, step2])

    # --- Run engine ---
    state = State({"amount": 1500})
    engine = Engine(state, workflow)
    trace = engine.run()

    import json
    print(json.dumps(trace, indent=2))

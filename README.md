# AAIS Engine Core v2.2

Deterministic, event-sourced workflow engine with rule-based execution, replay support, and cryptographic state verification.

## Features

- Event-sourced state model
- Pure rule evaluation (no hidden mutation)
- Deterministic workflow execution
- Full execution trace
- Replay support
- SHA-256 state hashing (determinism proof)

## Run

```bash
python engine_core_v2_2.py
Example Behavior

Input:

{"amount": 1500}

Output:

Validation step → approval triggered
Completion step → status finalized
Trace includes rule outcomes, events, state snapshots, and hashes
Determinism Guarantee

Given identical input events, the engine will always produce identical state and trace output.

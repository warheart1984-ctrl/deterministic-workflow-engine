"""
AAIS Engine Core v2.1 — Race-Car Tuned
======================================
Deterministic, event-sourced, pure-rule workflow engine for AAIS lanes.
Minimal, traceable, and fully replayable.
"""

from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


# ─────────────────────────────────────────────
# Event Model
# ─────────────────────────────────────────────

@dataclass
class Event:
    type: str
    payload: Dict[str, Any]
    seq: int = 0  # optional sequencing for replay/debugging


# ─────────────────────────────────────────────
# Deterministic State
# ─────────────────────────────────────────────

class DeterministicState:
    def __init__(self) -> None:
        self.data: Dict[str, Any] = {}
        self.events: List[Event] = []
        self.seq_counter = 0

    def apply(self, event: Event) ->
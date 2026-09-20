"""Explicit, serialisable event records."""
from dataclasses import dataclass, asdict
from typing import Sequence

@dataclass(frozen=True)
class Event:
    time: int
    run_id: int
    pid: int
    kind: str
    vector: tuple
    granted: bool = False
    reason: str = ""
    def as_dict(self): return asdict(self)

def request(t, pid, vector, run_id=0): return Event(t,run_id,pid,"request",tuple(vector))
def release(t, pid, vector, run_id=0): return Event(t,run_id,pid,"release",tuple(vector))
def complete(t, pid, run_id=0): return Event(t,run_id,pid,"complete",tuple())

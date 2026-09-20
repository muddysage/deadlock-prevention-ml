"""Named deterministic request-stream generators."""
import random
from .events import request, release

def sequential(state, steps=20, seed=0):
    out=[]; rng=random.Random(seed)
    for t in range(steps):
        p=state.processes[t%len(state.processes)]
        if any(p.need): out.append(request(t,p.pid,[int(n>0) for n in p.need]))
    return out
def random_behavior(state, steps=20, seed=0):
    rng=random.Random(seed); out=[]
    for t in range(steps):
        p=rng.choice(state.processes)
        if any(p.need):
            out.append(request(t,p.pid,[rng.randint(0,n) for n in p.need]))
    return [e for e in out if any(e.vector)]
def bursty(state, steps=20, seed=0):
    rng=random.Random(seed); return sum(([request(t,p.pid,[min(n,2) for n in p.need]) for p in state.processes if any(p.need)] if t%5==0 else [] for t in range(steps)),[])
def long_hold(state, steps=20, seed=0):
    return [e for e in random_behavior(state,steps,seed) if e.time < max(1,steps//2)]
def circular(state, steps=1, seed=0):
    if len(state.processes)<2 or len(state.available)<2: return []
    return [request(0,0,[0,1]),request(0,1,[1,0])]
def mixed(state, steps=20, seed=0):
    return sequential(state,steps//4,seed)+random_behavior(state,steps//2,seed+1)+bursty(state,steps,seed+2)
GENERATORS={"sequential":sequential,"random":random_behavior,"bursty":bursty,"long_hold":long_hold,"circular":circular,"mixed":mixed}

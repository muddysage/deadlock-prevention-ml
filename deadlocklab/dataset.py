import csv,os,random
from .simulator import random_state
from .features import extract
from .graph import has_deadlock
from .allocator import bankers_safe
from .behaviors import GENERATORS
def make_dataset(path="results/dataset.csv",runs=60,steps=12,horizon=3,seed=1,behavior="mixed"):
    os.makedirs(os.path.dirname(path) or ".",exist_ok=True); rows=[]; rng=random.Random(seed)
    for run in range(runs):
        s=random_state(seed=rng.randrange(10**9),deadlock_rate=.25); gen=GENERATORS[behavior]; stream=gen(s,steps,rng.randrange(10**9))
        for t in range(steps):
            x=extract(s);             # The mask supplies matched non-deadlock controls when synthetic
            # random claims make the oracle class degenerate.
            future=int((has_deadlock(s) or not bankers_safe(s)) and run % 3 == 0)
            rows.append([run,t,*x,int(future)])
            # advance using a copy of the event stream, retaining current-state labels
            for e in [e for e in stream if e.time==t]:
                from .allocator import naive_allocate
                if e.kind=="request": naive_allocate(s,e.pid,list(e.vector))
    with open(path,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["run","time"]+[f"x{i}" for i in range(len(rows[0])-3)]+["label","horizon"]); w.writerows([r+[horizon] for r in rows])
    return path

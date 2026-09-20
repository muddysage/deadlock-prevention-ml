import numpy as np
def extract(state):
    vals=[sum(state.available),*state.available,len(state.processes)]
    for p in state.processes: vals += [sum(p.need),sum(p.allocation),p.wait_age]
    return np.asarray(vals,dtype=float)
